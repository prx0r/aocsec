"""MCP gateway server. Stdlib only.

Config file (JSON):
{
  "tokens": {"tok-id-1": {"secret": "bearer-secret", "scopes": ["legislation:read"]}},
  "backends": {"legislation": {"command": ["python3", "-m", "legislation.mcp_server"],
                               "cwd": "/home/ubuntu/aocsec",
                               "tools": {"legislation_lookup": "legislation:read"}}}
}

Request flow: Bearer auth -> scope check (token scopes must include the
tool's required scope) -> forward JSON-RPC to backend stdin -> return
stdout line. One persistent subprocess per backend, guarded by a lock.
Audit entries record shapes, never values.
"""

from __future__ import annotations

import json
import os
import secrets
import subprocess
import threading
import time
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

# Default rate limit: 60 calls / 60s per token. Configurable per token
# via "rate_limit": {"calls": N, "window_s": M} in gateway.json.
DEFAULT_RATE = {"calls": 60, "window_s": 60}


class RateLimiter:
    """Per-token sliding window. In-memory; restarts reset budgets."""

    def __init__(self):
        self._lock = threading.Lock()
        self._hits: dict[str, list[float]] = {}

    def check(self, token_id: str, calls: int = 60,
              window_s: int = 60) -> bool:
        """True when allowed (and recorded). False when over budget."""
        now = time.time()
        with self._lock:
            hits = [t for t in self._hits.get(token_id, [])
                    if now - t < window_s]
            if len(hits) >= calls:
                self._hits[token_id] = hits
                return False
            hits.append(now)
            self._hits[token_id] = hits
            return True


LIMITER = RateLimiter()


class IdempotencyStore:
    """Replay-safe tools/call. Same (token, key) returns the stored
    response instead of re-executing. TTL 24h, capped size."""

    def __init__(self, ttl_s: int = 86400, max_entries: int = 1000):
        self._lock = threading.Lock()
        self._ttl = ttl_s
        self._max = max_entries
        self._store: dict[tuple[str, str], tuple[float, dict]] = {}

    def check(self, token_id: str, key: str) -> dict | None:
        now = time.time()
        with self._lock:
            hit = self._store.get((token_id, key))
            if hit is None:
                return None
            ts, resp = hit
            if now - ts > self._ttl:
                del self._store[(token_id, key)]
                return None
            return resp

    def store(self, token_id: str, key: str, response: dict) -> None:
        with self._lock:
            now = time.time()
            old = [(k, ts) for k, (ts, _) in self._store.items()
                   if now - ts > self._ttl]
            for k, _ in old:
                del self._store[k]
            while len(self._store) >= self._max:
                oldest = min(self._store, key=lambda k: self._store[k][0])
                del self._store[oldest]
            self._store[(token_id, key)] = (now, response)


IDEMPOTENT = IdempotencyStore()


@dataclass
class Backend:
    name: str
    command: list[str]
    cwd: str
    tools: dict[str, str]  # tool name -> required scope
    proc: subprocess.Popen | None = None
    lock: threading.Lock = field(default_factory=threading.Lock)
    msg_id: int = 0


@dataclass
class GatewayConfig:
    tokens: dict[str, dict]  # token id -> {"secret": str, "scopes": [str]}
    backends: dict[str, Backend]
    audit_log: str = ""

    @classmethod
    def load(cls, path: str | Path) -> "GatewayConfig":
        with open(path) as f:
            data = json.load(f)
        backends = {
            name: Backend(name=name, command=b["command"], cwd=b.get("cwd", "."),
                          tools=b.get("tools", {}))
            for name, b in data.get("backends", {}).items()
        }
        return cls(tokens=data.get("tokens", {}), backends=backends,
                   audit_log=data.get("audit_log", ""))


def load_config(path: str | Path) -> GatewayConfig:
    return GatewayConfig.load(path)


def _audit(cfg: GatewayConfig, token_id: str, tool: str, ok: bool,
           detail: str = "") -> None:
    if not cfg.audit_log:
        return
    from audit_chain import append
    append(cfg.audit_log, actor=f"token:{token_id[:4]}...",
           action=tool,
           detail={"ok": ok, "detail": detail[:120]})


def _backend_call(backend: Backend, payload: dict, timeout: int = 60) -> dict:
    """Forward one JSON-RPC message to a backend stdio server."""
    with backend.lock:
        if backend.proc is None or backend.proc.poll() is not None:
            backend.proc = subprocess.Popen(
                backend.command, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                text=True, bufsize=1, cwd=backend.cwd)
            backend.msg_id = 0
            # initialize handshake
            backend.msg_id += 1
            backend.proc.stdin.write(json.dumps({
                "jsonrpc": "2.0", "id": backend.msg_id, "method": "initialize",
                "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                           "clientInfo": {"name": "aocsec-gateway",
                                          "version": "0.1"}}}) + "\n")
            backend.proc.stdin.flush()
            line = backend.proc.stdout.readline()
            resp = json.loads(line)
            if "error" in resp:
                raise RuntimeError(f"backend {backend.name} init: {resp['error']}")
        backend.msg_id += 1
        payload = {**payload, "id": backend.msg_id}
        assert backend.proc.stdin and backend.proc.stdout
        backend.proc.stdin.write(json.dumps(payload) + "\n")
        backend.proc.stdin.flush()
        line = backend.proc.stdout.readline()
        if not line:
            backend.proc = None
            raise RuntimeError(f"backend {backend.name}: empty response")
        return json.loads(line)


def handle_request(cfg: GatewayConfig, auth_header: str, body: dict) -> tuple[int, dict]:
    """Authorize + scope-check + forward. Returns (http_code, response)."""
    token = ""
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
    matched_id, matched = None, None
    for tid, t in cfg.tokens.items():
        if secrets.compare_digest(token, t.get("secret", "")):
            matched_id, matched = tid, t
            break
    if matched is None:
        return 401, {"error": "bad token"}

    rl = matched.get("rate_limit", {})
    if not LIMITER.check(matched_id,
                         calls=int(rl.get("calls", DEFAULT_RATE["calls"])),
                         window_s=int(rl.get("window_s",
                                             DEFAULT_RATE["window_s"]))):
        _audit(cfg, matched_id, body.get("method", "unknown") or "unknown",
               False, "rate limited")
        return 429, {"jsonrpc": "2.0", "id": body.get("id"),
                     "error": {"code": -32004, "message": "rate limited"}}

    method = body.get("method", "")
    params = body.get("params", {}) or {}
    req_id = body.get("id")

    if method == "tools/list":
        tools = []
        for b in cfg.backends.values():
            tools.extend({"name": t, "backend": b.name}
                         for t in _visible_tools(b, matched))
        _audit(cfg, matched_id, "tools/list", True)
        return 200, {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools}}

    if method == "tools/call":
        name = params.get("name", "")
        backend = next((b for b in cfg.backends.values() if name in b.tools), None)
        if backend is None:
            _audit(cfg, matched_id, name, False, "unknown tool")
            return 404, {"jsonrpc": "2.0", "id": req_id,
                         "error": {"code": -32601, "message": f"unknown tool: {name}"}}
        required = backend.tools[name]
        if required not in matched.get("scopes", []):
            _audit(cfg, matched_id, name, False, "scope denied")
            return 403, {"jsonrpc": "2.0", "id": req_id,
                         "error": {"code": -32003, "message": "scope denied"}}
        idem_key = params.get("idempotency_key", "") or ""
        if idem_key:
            cached = IDEMPOTENT.check(matched_id, idem_key)
            if cached is not None:
                replay = {**cached, "id": req_id}
                _audit(cfg, matched_id, name, True, "idempotent replay")
                return 200, replay
        try:
            resp = _backend_call(backend, {"jsonrpc": "2.0",
                                           "method": "tools/call",
                                           "params": params})
        except Exception as e:
            _audit(cfg, matched_id, name, False, str(e)[:80])
            return 502, {"jsonrpc": "2.0", "id": req_id,
                         "error": {"code": -32603, "message": "backend error"}}
        # rewrite backend msg id back to caller id
        resp["id"] = req_id
        if idem_key and "error" not in resp:
            IDEMPOTENT.store(matched_id, idem_key, resp)
        _audit(cfg, matched_id, name, True)
        return 200, resp

    return 404, {"jsonrpc": "2.0", "id": req_id,
                 "error": {"code": -32601, "message": f"unknown method: {method}"}}


def _visible_tools(backend: Backend, token: dict) -> list[str]:
    scopes = set(token.get("scopes", []))
    return [t for t, s in backend.tools.items() if s in scopes]


def serve(cfg: GatewayConfig, host: str = "127.0.0.1", port: int = 8799):
    """Serve forever. Bind loopback; put Cloudflare Tunnel in front."""

    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, obj: dict):
            data = json.dumps(obj, default=str).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'none'")
            self.send_header("X-Frame-Options", "DENY")
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0) or 0)
            if length <= 0 or length > 1_000_000:
                return self._send(400, {"error": "bad body"})
            try:
                body = json.loads(self.rfile.read(length))
            except (json.JSONDecodeError, ValueError):
                return self._send(400, {"error": "bad json"})
            code, resp = handle_request(
                cfg, self.headers.get("Authorization", ""), body)
            self._send(code, resp)

        def do_GET(self):
            u = urlparse(self.path)
            if u.path == "/health":
                return self._send(200, {"ok": True})
            return self._send(404, {"error": "use POST"})

        def log_message(self, *a):
            pass

    print(f"aocsec gateway on {host}:{port}", flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    import sys
    cfg = load_config(sys.argv[1] if len(sys.argv) > 1 else "gateway.json")
    serve(cfg, port=int(os.environ.get("AOCSEC_GATEWAY_PORT", "8799")))
