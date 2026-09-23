"""Follow-up scheduler — 14-day fixes window + quarterly reviews.

Dates in, due-lists out. No notifications sent (the human or a
scheduled job decides delivery). Overdue items surface, never nag
automatically.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


def _parse(ts: str) -> datetime:
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def fixes_due(installed_at: str, now: str | None = None) -> dict:
    """14-day fixes window status for one install."""
    start = _parse(installed_at)
    current = _parse(now) if now else datetime.now(timezone.utc)
    end = start + timedelta(days=14)
    remaining = (end - current).days
    if remaining < 0:
        return {"window": "closed", "days_left": 0,
                "action": "Fixes window ended. New issues go through "
                          "support tickets, not the install."}
    return {"window": "open", "days_left": remaining,
            "action": f"{remaining} days of fixes remaining. Log issues "
                      f"against the install, not as new tickets."}


def review_due(last_review_at: str, now: str | None = None,
               period_days: int = 90) -> dict:
    """Quarterly review status (maintenance, red-team, rules currency)."""
    last = _parse(last_review_at)
    current = _parse(now) if now else datetime.now(timezone.utc)
    due = last + timedelta(days=period_days)
    if current >= due:
        overdue = (current - due).days
        return {"due": True, "overdue_days": overdue,
                "action": "Quarterly review overdue: re-run redteam, "
                          "re-check domains, refresh stale rules."}
    return {"due": False,
            "days_left": (due - current).days,
            "action": "On schedule."}


def followups_for(business_id: str, *, installed_at: str,
                  last_review_at: str,
                  now: str | None = None) -> dict:
    """Combined follow-up state for one business."""
    fixes = fixes_due(installed_at, now)
    review = review_due(last_review_at, now)
    items = []
    if fixes["window"] == "open":
        items.append({"kind": "fixes_window", **fixes})
    if review["due"]:
        items.append({"kind": "quarterly_review", **review})
    return {"business_id": business_id, "items": items,
            "attention": bool(items)}
