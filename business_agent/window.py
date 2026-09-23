"""24-hour messaging window logic.

WhatsApp platform rule: free-form messages only within 24h of the
user's last message. After that, approved templates only. Support
flows MUST branch on this — a "helpful" free-form reply outside the
window silently fails (or worse, violates policy).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

WINDOW_HOURS = 24


def _parse(ts: str) -> datetime:
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def in_freeform_window(last_user_message_at: str,
                       now: str | None = None) -> bool:
    """True when a free-form reply is allowed right now."""
    try:
        last = _parse(last_user_message_at)
    except (ValueError, TypeError):
        return False
    current = _parse(now) if now else datetime.now(timezone.utc)
    return timedelta(0) <= (current - last) <= timedelta(hours=WINDOW_HOURS)


def window_status(last_user_message_at: str,
                  now: str | None = None) -> dict:
    """Window state + what the agent may send."""
    if in_freeform_window(last_user_message_at, now):
        return {"window": "open", "may_send": "free-form",
                "note": "Reply normally."}
    try:
        _parse(last_user_message_at)
    except (ValueError, TypeError):
        return {"window": "unknown", "may_send": "nothing",
                "note": "No valid timestamp — treat as closed."}
    return {"window": "closed", "may_send": "approved templates only",
            "note": "Free-form replies will fail. Use a template or "
                    "wait for the user to message first."}
