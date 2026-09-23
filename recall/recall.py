"""Lapsed-client win-back. The biggest revenue line in every vertical.

Dogs need grooming every 6 weeks, nails need infills every 3,
boilers need servicing every 12 months. When the interval passes
with no visit, that's not churn — it's a scheduling failure worth
a reminder. Recall lists are drafts for the owner; consent is
checked per contact before anything is sendable.

Intervals are starting defaults per vertical, tunable per business
once real data exists (Phase 1 will prove most of these wrong).
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS recall_clients (
    customer_hash TEXT NOT NULL,
    business_id TEXT NOT NULL,
    vertical TEXT NOT NULL DEFAULT '',
    service TEXT NOT NULL DEFAULT '',
    last_visit_at TEXT NOT NULL,
    interval_days INTEGER NOT NULL DEFAULT 0,
    last_recalled_at TEXT NOT NULL DEFAULT '',
    recalls INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (customer_hash, business_id)
)
"""

# starting defaults (days); per-business override wins
DEFAULT_INTERVALS = {
    "nails": 21,
    "lashes": 21,
    "hair": 42,
    "beauty": 42,
    "dog-groomers": 42,
    "cleaners": 14,
    "gardeners-window-cleaners": 28,
    "driving-instructors": 7,
    "electrician": 365,
    "car-detailers": 90,
    "weddings": 0,  # one-off by nature; no interval recall
}

MAX_RECALLS = 2


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_visit(connection: sqlite3.Connection, customer_hash: str,
                 business_id: str, vertical: str = "",
                 service: str = "", interval_days: int = 0,
                 visited_at: str = "") -> None:
    """Log a visit. Resets the recall clock for this client."""
    connection.execute(SCHEMA)
    interval = interval_days or DEFAULT_INTERVALS.get(vertical, 0)
    connection.execute(
        "INSERT INTO recall_clients (customer_hash, business_id, vertical,"
        " service, last_visit_at, interval_days) VALUES (?, ?, ?, ?, ?, ?)"
        " ON CONFLICT (customer_hash, business_id) DO UPDATE SET"
        " service = excluded.service, last_visit_at = excluded.last_visit_at,"
        " interval_days = excluded.interval_days, recalls = 0,"
        " last_recalled_at = ''",
        (customer_hash, business_id, vertical, service[:120],
         visited_at or _now(), interval))
    connection.commit()


def due_recalls(connection: sqlite3.Connection,
                business_id: str) -> list[dict]:
    """Clients past their interval, longest-overdue first.

    Returns drafts with consent still to check upstream (whatsapp
    build_message refuses non-opted-in contacts — the gate holds).
    """
    connection.execute(SCHEMA)
    now = datetime.now(timezone.utc)
    rows = connection.execute(
        "SELECT customer_hash, vertical, service, last_visit_at,"
        " interval_days, recalls FROM recall_clients WHERE business_id = ?"
        " AND interval_days > 0 AND recalls < ?",
        (business_id, MAX_RECALLS)).fetchall()
    due = []
    for h, vert, svc, last, interval, recalls in rows:
        try:
            last_dt = datetime.fromisoformat(last)
        except ValueError:
            continue
        overdue = (now - last_dt).days - interval
        if overdue > 0:
            due.append({"customer_hash": h, "vertical": vert,
                        "service": svc, "days_overdue": overdue,
                        "draft": f"Hi — it's been a while since your last"
                                 f" {svc or 'visit'}. Want to book back in?"
                                 f" Reply YES and we'll find a time."})
    due.sort(key=lambda d: -d["days_overdue"])
    return due


def mark_recalled(connection: sqlite3.Connection, customer_hash: str,
                  business_id: str) -> bool:
    """Record that the owner sent a recall. Returns False if unknown."""
    connection.execute(SCHEMA)
    cur = connection.execute(
        "UPDATE recall_clients SET recalls = recalls + 1,"
        " last_recalled_at = ? WHERE customer_hash = ? AND business_id = ?",
        (_now(), customer_hash, business_id))
    connection.commit()
    return cur.rowcount == 1


def recall_value(connection: sqlite3.Connection,
                 business_id: str) -> dict:
    """How many clients are drifting, and how far."""
    due = due_recalls(connection, business_id)
    return {"drifting_clients": len(due),
            "total_overdue_days": sum(d["days_overdue"] for d in due)}
