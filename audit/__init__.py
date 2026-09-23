"""Central audit sink — one chained log for every state change.

All modules report here: onboarding transitions, attestations,
maintenance runs, message builds, gate decisions. Controlled by env:

  AOCSEC_AUDIT=off     disable entirely (tests, dry runs)
  AOCSEC_AUDIT_LOG     override path (tests use temp files)

Failures never propagate — a broken audit trail must not break the
operation it observes (but it does get reported to stderr).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

DEFAULT_LOG = Path.home() / ".aocsec" / "audit.jsonl"


def _log_path() -> Path | None:
    if os.environ.get("AOCSEC_AUDIT", "").lower() == "off":
        return None
    return Path(os.environ.get("AOCSEC_AUDIT_LOG", str(DEFAULT_LOG)))


def audit(*, actor: str, action: str, business_id: str = "",
          detail: dict | None = None) -> dict | None:
    """Append one audit record. Returns record or None when disabled."""
    path = _log_path()
    if path is None:
        return None
    try:
        from audit_chain import append
        body = dict(detail or {})
        if business_id:
            body = {"business_id": business_id, **body}
        return append(path, actor=actor, action=action, detail=body)
    except Exception as e:
        print(f"audit write failed: {e}", file=sys.stderr)
        return None


from .export import export_business_audit

__all__ = ["audit", "export_business_audit"]
