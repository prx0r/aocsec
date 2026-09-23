"""Maintenance plans. Prices proposed, not validated."""

from __future__ import annotations

PLANS: dict[str, dict] = {
    "care": {
        "name": "Security care",
        "price": "£19/mo",
        "checks": ["domain", "email_auth", "legislation_stale"],
        "report": True,
        "redteam": False,
        "support_note": "Findings reported; fixes quoted separately.",
    },
    "care_plus": {
        "name": "Security care plus",
        "price": "£39/mo",
        "checks": ["domain", "email_auth", "legislation_stale",
                   "redteam", "backups"],
        "report": True,
        "redteam": True,
        "support_note": "Includes 30 min engineer review of findings monthly.",
    },
}


def plan_for(plan_id: str) -> dict:
    """Plan definition. Unknown IDs rejected (no silent default tier)."""
    if plan_id not in PLANS:
        raise ValueError(f"unknown plan: {plan_id}. Known: {sorted(PLANS)}")
    return {"id": plan_id, **PLANS[plan_id]}
