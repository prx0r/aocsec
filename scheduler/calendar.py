"""Compliance calendar per business — every dated obligation in one timeline.

Aggregates: legislation review dates, qualification/certificate expiries
(from the business graph), maintenance review dates, tax deadlines the
owner entered. Sorted by urgency. The "never miss" view.
"""

from __future__ import annotations

from datetime import datetime, timezone


def _parse(ts: str):
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError, AttributeError):
        return None


def compliance_calendar(*, obligations: list[dict] | None = None,
                        certificates: list[dict] | None = None,
                        maintenance_due: str = "",
                        tax_deadlines: list[dict] | None = None,
                        now: str | None = None) -> list[dict]:
    """Merge all dated items into one sorted timeline.

    Each item: {date, kind, title, detail}. Past-due sorts first.
    """
    current = _parse(now) if now else datetime.now(timezone.utc)
    items = []

    for o in obligations or []:
        rd = o.get("review_date", "")
        dt = _parse(rd) if rd else None
        if dt is None:
            continue
        items.append({"date": rd, "kind": "legislation_review",
                      "title": o.get("law", o.get("id", "?")),
                      "detail": "Rule needs re-verification.",
                      "overdue": dt < current})

    for c in certificates or []:
        exp = c.get("expires", "")
        dt = _parse(exp) if exp else None
        if dt is None:
            continue
        items.append({"date": exp, "kind": "certificate_expiry",
                      "title": c.get("name", "?"),
                      "detail": "Renew before expiry.",
                      "overdue": dt < current})

    if maintenance_due:
        dt = _parse(maintenance_due)
        if dt is not None:
            items.append({"date": maintenance_due, "kind": "maintenance",
                          "title": "Quarterly review",
                          "detail": "Red-team + domain + rules refresh.",
                          "overdue": dt < current})

    for t in tax_deadlines or []:
        if t.get("date"):
            dt = _parse(t["date"])
            items.append({"date": t["date"], "kind": "tax",
                          "title": t.get("title", "?"),
                          "detail": t.get("detail", ""),
                          "overdue": bool(dt and dt < current)})

    items.sort(key=lambda i: (not i["overdue"], i["date"]))
    return items


def due_items(calendar: list[dict], within_days: int = 30) -> list[dict]:
    """Overdue + upcoming-within-N-days items. The morning queue."""
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    out = []
    for item in calendar:
        dt = _parse(item["date"])
        if dt is None:
            continue
        if dt < now or dt - now <= timedelta(days=within_days):
            out.append(item)
    return out
