"""Structural scanner — prove dangerous capabilities are absent.

Detection asks "did anything bad happen". This asks "is the bad thing
even expressible". AST-level checks over agent-path code:

- eval / exec / compile — arbitrary code execution, no legitimate use.
- os.system / subprocess with shell=True — shell injection surface.
- pickle / yaml.load (unsafe loader) — deserialization attacks.
- socket / raw HTTP servers in agent modules — unexpected listeners.
- open() with write modes outside allowlisted paths — unbounded writes.

Each finding cites file:line. Clean output is evidence, not a vibe.
"""

from .scan import (
    BANNED_NODES,
    scan_file,
    scan_repo,
)

__all__ = [
    "BANNED_NODES",
    "scan_file",
    "scan_repo",
]
