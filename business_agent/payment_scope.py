"""Payment-scope decisions per install.

Meta's agent CAN complete payments. Our connector declares none. The
gap between those facts is a per-install decision that must be written
down: what Meta's side may complete, who decided, when. Default scope
is handoff-only. Anything wider needs a named approver and a review
date — money movement without a recorded decision is a finding.
"""

from __future__ import annotations

from datetime import datetime, timezone

SCOPES = ("handoff_only", "quotes", "bookings", "payments")
_SCOPE_RANK = {name: i for i, name in enumerate(SCOPES)}


def record_payment_scope(*, business_id: str, scope: str,
                         decided_by: str,
                         review_days: int = 90) -> dict:
    """Record what Meta's side may complete for one install."""
    if scope not in SCOPES:
        raise ValueError(f"unknown scope: {scope}. Known: {list(SCOPES)}")
    if not business_id.strip() or not decided_by.strip():
        raise ValueError("business_id and decided_by are required")
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    return {
        "business_id": business_id.strip(),
        "scope": scope,
        "decided_by": decided_by.strip(),
        "decided_at": now.isoformat(),
        "review_by": (now + timedelta(days=review_days)).date().isoformat(),
        "note": ("Agent hands off all money movement."
                 if scope == "handoff_only" else
                 f"Agent may complete: {scope}. Invoice verification "
                 f"applies to everything it presents."),
    }


def widen_scope(record: dict, *, to_scope: str,
                decided_by: str) -> dict:
    """Widen scope. Narrowing is free; widening re-records fully."""
    if _SCOPE_RANK[to_scope] <= _SCOPE_RANK[record["scope"]]:
        return {**record, "scope": to_scope,
                "decided_by": decided_by.strip(),
                "decided_at": datetime.now(timezone.utc).isoformat()}
    return record_payment_scope(business_id=record["business_id"],
                                scope=to_scope, decided_by=decided_by)
