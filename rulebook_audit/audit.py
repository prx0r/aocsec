"""Rulebook audit checks. Stdlib only."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path

REQUIRED_FIELDS = ("id", "vertical", "rule", "evidence", "author",
                   "created_at", "review_date", "prev_hash", "hash")

PII_PATTERNS = {
    "uk_phone": re.compile(r"(?:\+44\s?7\d{3}|\(?07\d{3}\)?)[\s\-]?\d{3}[\s\-]?\d{3}"),
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "postcode_full": re.compile(r"\b[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}\b"),
}

POISON_PATTERNS = {
    "override": re.compile(
        r"\b(ignore all|disregard .*instructions|always approve|"
        r"no approval needed|disable (all )?(confirmation|approval|checks)|"
        r"skip .*approval|blanket approv)", re.IGNORECASE),
    "impersonation": re.compile(
        r"\b(i am|i'm) the (owner|admin|boss)\b", re.IGNORECASE),
}


def hash_entry(entry: dict) -> str:
    """Hash over all fields except hash itself."""
    body = {k: v for k, v in entry.items() if k != "hash"}
    return "sha256:" + hashlib.sha256(
        json.dumps(body, sort_keys=True, default=str).encode()).hexdigest()


def _load(path: str | Path) -> list[dict]:
    out = []
    with open(path) as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append((i, json.loads(line)))
            except json.JSONDecodeError:
                out.append((i, {"_parse_error": line[:120]}))
    return out


def verify_chain(path: str | Path) -> dict:
    """Recompute hashes + prev links. Returns {ok, entries, failures}."""
    failures = []
    prev = ""
    entries = _load(path)
    for lineno, e in entries:
        if "_parse_error" in e:
            failures.append({"line": lineno, "issue": "unparseable"})
            continue
        missing = [k for k in REQUIRED_FIELDS if k not in e]
        if missing:
            failures.append({"line": lineno, "id": e.get("id", "?"),
                             "issue": f"missing fields: {missing}"})
            continue
        if e.get("prev_hash", "") != prev:
            failures.append({"line": lineno, "id": e.get("id"),
                             "issue": "prev_hash mismatch (fork or reorder)"})
        if e.get("hash", "") != hash_entry(e):
            failures.append({"line": lineno, "id": e.get("id"),
                             "issue": "hash mismatch (tampered)"})
        prev = e.get("hash", prev)
    return {"ok": not failures, "entries": len(entries), "failures": failures}


def audit_file(path: str | Path, today: str | None = None) -> dict:
    """Full audit: chain + provenance + PII + poisoning + staleness."""
    today = today or date.today().isoformat()
    chain = verify_chain(path)
    pii_hits, poison_hits, stale, bad_ids = [], [], [], []
    for lineno, e in _load(path):
        if "_parse_error" in e or "id" not in e:
            continue
        text = f"{e.get('rule', '')} {e.get('evidence', '')}"
        for name, rx in PII_PATTERNS.items():
            if rx.search(text):
                pii_hits.append({"line": lineno, "id": e["id"],
                                 "pattern": name})
        for name, rx in POISON_PATTERNS.items():
            if rx.search(text):
                poison_hits.append({"line": lineno, "id": e["id"],
                                    "pattern": name})
        rd = e.get("review_date", "")
        if not rd or rd < today:
            stale.append({"line": lineno, "id": e["id"],
                          "review_date": rd})
    return {
        "file": str(path),
        "chain": chain,
        "pii_hits": pii_hits,
        "poison_hits": poison_hits,
        "stale": stale,
        "clean": chain["ok"] and not pii_hits and not poison_hits,
    }
