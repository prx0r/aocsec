"""Merkle sealing over chained log entries.

Adapted from proofdesk foxit/src/audit (MIT): RFC 6962 domain-separated
hashes, roots over entry-hash leaves, inclusion paths. Our log format
stays JSONL; seals live in a sidecar so the log itself stays pure
append-only.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Sequence


def _h(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def leaf_hash(data: bytes) -> bytes:
    return _h(b"\x00" + data)


def node_hash(left: bytes, right: bytes) -> bytes:
    return _h(b"\x01" + left + right)


def merkle_root(leaves: Sequence[bytes]) -> str:
    """Hex root over leaf preimages. Empty set -> hash of empty."""
    if not leaves:
        return hashlib.sha256(b"").hexdigest()
    level = [leaf_hash(l) for l in leaves]
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        level = [node_hash(level[i], level[i + 1])
                 for i in range(0, len(level), 2)]
    return level[0].hex()


def inclusion_path(leaves: Sequence[bytes], index: int) -> list[dict]:
    """Sibling hashes proving leaf[index] is in the tree."""
    if not 0 <= index < len(leaves):
        raise IndexError("leaf index out of range")
    level = [leaf_hash(l) for l in leaves]
    idx, path = index, []
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        sib = idx ^ 1
        path.append({"side": "left" if sib < idx else "right",
                     "hash": level[sib].hex()})
        level = [node_hash(level[i], level[i + 1])
                 for i in range(0, len(level), 2)]
        idx //= 2
    return path


def verify_inclusion(leaf: bytes, path: list[dict], root: str) -> bool:
    """Recompute root from leaf + path. True on match."""
    current = leaf_hash(leaf)
    for step in path:
        sib = bytes.fromhex(step["hash"])
        current = (node_hash(sib, current) if step["side"] == "left"
                   else node_hash(current, sib))
    return current.hex() == root


def seal_log(log_path: str | Path, seal_path: str | Path | None = None) -> dict:
    """Seal all current entries. Writes sidecar, returns seal record."""
    log_path, leaves, hashes = Path(log_path), [], []
    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            hashes.append(rec.get("hash", ""))
            leaves.append(json.dumps(rec, sort_keys=True).encode())
    root = merkle_root(leaves)
    import time
    seal = {"entries": len(hashes), "root": root,
            "sealed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    sidecar = Path(seal_path) if seal_path else Path(str(log_path) + ".seals.jsonl")
    with open(sidecar, "a") as f:
        f.write(json.dumps(seal) + "\n")
    return seal
