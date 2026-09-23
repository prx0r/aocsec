"""Hash-chained append-only audit log.

Every record links to the previous hash. Tampering, deletion, or
reorder breaks the chain — verifiable without trusting the writer.
Same pattern as powops history and rulebook entries, one shared shape:

    {"ts", "actor", "action", "detail", "prev", "hash"}

Values never enter the log: callers pass shapes/hashes/counts, and
the module redacts anything looking like a secret anyway.
"""

from .chain import append, create_log, verify

__all__ = ["append", "create_log", "verify"]
