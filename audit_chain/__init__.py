"""Hash-chained append-only audit log.

Every record links to the previous hash. Tampering, deletion, or
reorder breaks the chain — verifiable without trusting the writer.
Same pattern as powops history and rulebook entries, one shared shape:

    {"ts", "actor", "action", "detail", "prev", "hash"}

Values never enter the log: callers pass shapes/hashes/counts, and
the module redacts anything looking like a secret anyway.
"""

from .certificates import Certificate
from .chain import append, create_log, verify
from .merkle import (
    inclusion_path,
    leaf_hash,
    merkle_root,
    node_hash,
    seal_log,
    verify_inclusion,
)

__all__ = [
    "Certificate",
    "append",
    "create_log",
    "inclusion_path",
    "leaf_hash",
    "merkle_root",
    "node_hash",
    "seal_log",
    "verify",
    "verify_inclusion",
]
