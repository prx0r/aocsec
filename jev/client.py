"""Jev MCP client — stdio JSON-RPC to the jev-mcp server.

Server: `npx -y @jkudish/jev-mcp` (needs TYPESAFE_API_KEY in env,
or OpenRouter key per jev-mcp docs). One persistent process per
client; call tools by name with arguments dicts.
"""

from __future__ import annotations

import json
import os
import subprocess


class JevError(Exception):
    pass


def jev_available() -> bool:
    """True when a key is present to actually call Jev."""
    return bool(os.environ.get("TYPESAFE_API_KEY")
                or os.environ.get("OPENROUTER_API_KEY"))


class JevMCP:
    """Thin caller over the jev-mcp stdio server."""

    def __init__(self, timeout: int = 60):
        if not jev_available():
            raise JevError(
                "no TypeSafe/OpenRouter key. Set TYPESAFE_API_KEY. "
                "This client refuses to guess without the model.")
        self._timeout = timeout
        self._proc: subprocess.Popen | None = None
        self._msg_id = 0

    def _ensure(self):
        if self._proc is None or self._proc.poll() is not None:
            env = dict(os.environ)
            self._proc = subprocess.Popen(
                ["npx", "-y", "@jkudish/jev-mcp"],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, text=True, bufsize=1, env=env)
            self._hello()

    def _hello(self):
        assert self._proc and self._proc.stdin and self._proc.stdout
        self._msg_id += 1
        self._proc.stdin.write(json.dumps({
            "jsonrpc": "2.0", "id": self._msg_id, "method": "initialize",
            "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                       "clientInfo": {"name": "aocsec-jev", "version": "0.1"}}}) + "\n")
        self._proc.stdin.flush()
        line = self._proc.stdout.readline()
        resp = json.loads(line)
        if "error" in resp:
            raise JevError(f"initialize failed: {resp['error']}")

    def call(self, tool: str, arguments: dict) -> dict:
        """Call one jev-mcp tool. Returns the parsed result payload."""
        self._ensure()
        assert self._proc and self._proc.stdin and self._proc.stdout
        self._msg_id += 1
        self._proc.stdin.write(json.dumps({
            "jsonrpc": "2.0", "id": self._msg_id, "method": "tools/call",
            "params": {"name": tool, "arguments": arguments}}) + "\n")
        self._proc.stdin.flush()
        line = self._proc.stdout.readline()
        if not line:
            raise JevError(f"empty response from jev-mcp on {tool}")
        resp = json.loads(line)
        if "error" in resp:
            raise JevError(f"{tool} failed: {resp['error']}")
        return resp.get("result", {})

    def close(self):
        if self._proc is not None:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=5)
            except Exception:
                try:
                    self._proc.kill()
                except Exception:
                    pass
            self._proc = None

    def __enter__(self):
        self._ensure()
        return self

    def __exit__(self, *a):
        self.close()
