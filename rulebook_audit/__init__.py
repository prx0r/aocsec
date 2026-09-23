"""Rulebook auditor — integrity, provenance, PII, staleness, poisoning.

Reads rulebook JSONL files (one entry per line, per the contract in
docs/rulebook-security.md). Reports findings; quarantines nothing
automatically (deletion destroys the chain — flag for human action).
"""

from .audit import (
    PII_PATTERNS,
    POISON_PATTERNS,
    audit_file,
    hash_entry,
    verify_chain,
)

__all__ = [
    "PII_PATTERNS",
    "POISON_PATTERNS",
    "audit_file",
    "hash_entry",
    "verify_chain",
]
