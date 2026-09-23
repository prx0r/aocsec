"""Backup verification — manifest, freshness, restore drills.

Backups nobody tests are wishes. This module declares what must survive
(state, credentials inventory, customer records locations), checks
freshness, and structures restore drills with pass/fail evidence.

It does not perform backups itself (rsync/R2/timers belong to deploy).
It proves they happened and that restore works.
"""

from .backups import (
    DEFAULT_MANIFEST,
    check_freshness,
    restore_drill,
)

__all__ = [
    "DEFAULT_MANIFEST",
    "check_freshness",
    "restore_drill",
]
