"""Append-only hash-chained log. Stdlib only."""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path

_SECRET_HINT = re.compile(
    r"(api[_-]?key|token|secret|password|passwd|bearer)",
    re.IGNORECASE)


def _redact(obj):
    """Recursively replace secret-shaped values with [redacted]."""
    if isinstance(obj, dict):
        return {k: ("[redacted]" if _SECRET_HINT.search(str(k)) else _redact(v))
                for k, v in obj.items()}
    if isinstance(obj, list):
        return [_redact(v) for v in obj]
    if isinstance(obj, str) and len(obj) > 32:
        # long opaque strings are probably tokens/keys
        return "[redacted]"
    return obj


def _hash(body: dict) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(body, sort_keys=True, default=str).encode()).hexdigest()


def create_log(path: str | Path) -> Path:
    """Create an empty chained log (genesis prev = all zeros)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text("")
    return p


def _last_hash(path: Path) -> str:
    if not path.exists():
        return "0" * 64
    last = ""
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                last = line
    if not last:
        return "0" * 64
    try:
        return json.loads(last).get("hash", "0" * 64)
    except json.JSONDecodeError:
        raise ValueError(f"corrupt log line in {path}")


def append(path: str | Path, *, actor: str, action: str,
           detail: dict | None = None) -> dict:
    """Append one record. Returns the record (with hash)."""
    p = create_log(path)
    body = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "actor": actor,
        "action": action,
        "detail": _redact(detail or {}),
        "prev": _last_hash(p),
    }
    record = {**body, "hash": _hash(body)}
    with open(p, "a") as f:
        f.write(json.dumps(record) + "\n")
    return record


def verify(path: str | Path) -> dict:
    """Verify chain integrity. Returns {ok, entries, failures}."""
    p = Path(path)
    failures = []
    prev = "0" * 64
    count = 0
    if not p.exists():
        return {"ok": True, "entries": 0, "failures": []}
    with open(p) as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            count += 1
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                failures.append({"line": i, "issue": "unparseable"})
                continue
            if rec.get("prev") != prev:
                failures.append({"line": i, "issue": "prev mismatch"})
            body = {k: v for k, v in rec.items() if k != "hash"}
            if rec.get("hash") != _hash(body):
                failures.append({"line": i, "issue": "hash mismatch"})
            prev = rec.get("hash", prev)
    return {"ok": not failures, "entries": count, "failures": failures}
