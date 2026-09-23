"""Rulebook auditor — integrity, provenance, PII, staleness, poisoning.

Two formats: JSONL chains (audit.py — full verification) and markdown
tables (markdown.py — PII/poison/structure; chain integrity comes from
git history). Reports findings; quarantines nothing automatically
(deletion destroys the chain — flag for human action).
"""

from .audit import (
    PII_PATTERNS,
    POISON_PATTERNS,
    audit_file,
    hash_entry,
    verify_chain,
)
from .markdown import (
    audit_markdown_rulebook,
    file_last_commit,
    parse_tables,
)

__all__ = [
    "PII_PATTERNS",
    "POISON_PATTERNS",
    "audit_file",
    "audit_markdown_rulebook",
    "file_last_commit",
    "hash_entry",
    "parse_tables",
    "verify_chain",
]
