"""Backup manifest checks + restore drill records."""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from pathlib import Path

# What must survive, where it lives, max acceptable age (hours).
# Paths may not exist on every host — missing sources are reported,
# not errors, so the same manifest runs everywhere.
DEFAULT_MANIFEST: list[dict] = [
    {"id": "powops-state", "path": os.path.expanduser("~/.powops"),
     "max_age_hours": 24,
     "why": "history, incidents, events, alert state — operational memory"},
    {"id": "powops-dashboard-token", "path": os.path.expanduser("~/.powops/dashboard_token"),
     "max_age_hours": 24, "why": "dashboard access (600 perms)"},
    {"id": "aocsec-gateway-audit", "path": os.path.expanduser("~/.aocsec/gateway-audit.jsonl"),
     "max_age_hours": 168, "why": "gateway audit chain"},
    {"id": "aocsec-audit-log", "path": os.path.expanduser("~/.aocsec/audit.jsonl"),
     "max_age_hours": 168,
     "why": "central audit sink — onboarding, attestations, maintenance, messages, gates"},
]


def _newest_mtime(path: Path) -> float | None:
    if not path.exists():
        return None
    if path.is_file():
        return path.stat().st_mtime
    newest = None
    for root, _, files in os.walk(path):
        for f in files:
            try:
                mt = os.stat(os.path.join(root, f)).st_mtime
            except OSError:
                continue
            if newest is None or mt > newest:
                newest = mt
    return newest


def check_freshness(manifest: list[dict] | None = None,
                    now: float | None = None) -> dict:
    """Check each manifest entry. Returns per-id status + summary."""
    manifest = manifest if manifest is not None else DEFAULT_MANIFEST
    now = now if now is not None else time.time()
    results = []
    for entry in manifest:
        newest = _newest_mtime(Path(os.path.expanduser(entry["path"])))
        if newest is None:
            results.append({"id": entry["id"], "status": "missing",
                            "detail": "path absent on this host",
                            "why": entry.get("why", "")})
            continue
        age_h = (now - newest) / 3600
        if age_h <= entry["max_age_hours"]:
            results.append({"id": entry["id"], "status": "fresh",
                            "age_hours": round(age_h, 1),
                            "why": entry.get("why", "")})
        else:
            results.append({"id": entry["id"], "status": "stale",
                            "age_hours": round(age_h, 1),
                            "max_age_hours": entry["max_age_hours"],
                            "why": entry.get("why", "")})
    bad = [r for r in results if r["status"] != "fresh"]
    return {"results": results,
            "fresh": len(results) - len(bad), "total": len(results),
            "ok": not bad,
            "checked_at": datetime.now(timezone.utc).isoformat()}


def restore_drill(label: str, steps: list[dict]) -> dict:
    """Record a restore drill. Each step: {step, passed: bool, evidence}.

    A drill passes only when every step passes with evidence text.
    Returns the drill record (caller persists it wherever drills live).
    """
    cleaned = []
    for s in steps:
        passed = bool(s.get("passed")) and bool(str(s.get("evidence", "")).strip())
        cleaned.append({"step": s.get("step", "?"), "passed": passed,
                        "evidence": str(s.get("evidence", ""))[:300]})
    return {"label": label,
            "at": datetime.now(timezone.utc).isoformat(),
            "passed": all(s["passed"] for s in cleaned) and bool(cleaned),
            "steps": cleaned}
