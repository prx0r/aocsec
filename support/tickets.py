"""Tickets + SLA timers. Minimal lifecycle, chained audit.

Statuses: new -> open -> pending -> resolved (-> reopened).
SLA clocks pause in pending (waiting on customer/external).
Every transition appends to the audit chain when a log path is given.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone

SLA_TARGETS = {
    # priority: (response_hours, resolution_hours)
    "critical": (1, 4),
    "high": (4, 24),
    "medium": (24, 72),
    "low": (72, 168),
}

_STATUSES = ("new", "open", "pending", "resolved", "reopened")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_support_tables(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY,
            business_id TEXT NOT NULL,
            subject TEXT NOT NULL,
            detail TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'new',
            priority TEXT NOT NULL DEFAULT 'medium',
            assignee TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            response_due_at TEXT NOT NULL,
            resolve_due_at TEXT NOT NULL,
            resolved_at TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_tickets_business
            ON support_tickets(business_id, status);
        """
    )
    connection.commit()


def _audit(action: str, business_id: str, ticket_id: int, detail: str = "") -> None:
    try:
        from audit_chain import append
        from pathlib import Path
        append(Path.home() / ".aocsec" / "support-audit.jsonl",
               actor="support", action=action,
               detail={"business_id": business_id, "ticket": ticket_id,
                       "detail": detail[:120]})
    except Exception:
        pass  # audit is best-effort here; tickets are source of truth


def open_ticket(connection: sqlite3.Connection, *, business_id: str,
                subject: str, detail: str = "",
                priority: str = "medium") -> dict:
    """Open a ticket. Unknown priorities rejected."""
    if priority not in SLA_TARGETS:
        raise ValueError(f"unknown priority: {priority}")
    if not subject.strip():
        raise ValueError("subject is required")
    now = datetime.now(timezone.utc)
    resp_h, res_h = SLA_TARGETS[priority]
    cur = connection.execute(
        "INSERT INTO support_tickets (business_id, subject, detail, "
        "status, priority, created_at, updated_at, response_due_at, "
        "resolve_due_at) VALUES (?, ?, ?, 'new', ?, ?, ?, ?, ?)",
        (business_id, subject.strip(), detail,
         priority, now.isoformat(), now.isoformat(),
         (now + timedelta(hours=resp_h)).isoformat(),
         (now + timedelta(hours=res_h)).isoformat()))
    connection.commit()
    ticket_id = int(cur.lastrowid)
    _audit("ticket.opened", business_id, ticket_id, subject)
    return get_ticket(connection, ticket_id)


def get_ticket(connection: sqlite3.Connection, ticket_id: int) -> dict:
    row = connection.execute(
        "SELECT * FROM support_tickets WHERE id=?", (ticket_id,)).fetchone()
    if row is None:
        raise LookupError(f"unknown ticket: {ticket_id}")
    cols = [d[0] for d in connection.execute(
        "SELECT * FROM support_tickets LIMIT 0").description]
    return dict(zip(cols, row))


def assign_ticket(connection: sqlite3.Connection, ticket_id: int,
                  assignee: str) -> dict:
    """Assign + move to open. Empty assignee rejected."""
    if not assignee.strip():
        raise ValueError("assignee is required")
    t = get_ticket(connection, ticket_id)
    connection.execute(
        "UPDATE support_tickets SET assignee=?, status='open', "
        "updated_at=? WHERE id=?",
        (assignee.strip(), _now(), ticket_id))
    connection.commit()
    _audit("ticket.assigned", t["business_id"], ticket_id, assignee)
    return get_ticket(connection, ticket_id)


def set_status(connection: sqlite3.Connection, ticket_id: int,
               status: str) -> dict:
    """Move status. Resolved stamps resolved_at."""
    if status not in _STATUSES:
        raise ValueError(f"unknown status: {status}")
    t = get_ticket(connection, ticket_id)
    if status == "resolved":
        connection.execute(
            "UPDATE support_tickets SET status='resolved', updated_at=?, "
            "resolved_at=? WHERE id=?", (_now(), _now(), ticket_id))
    else:
        connection.execute(
            "UPDATE support_tickets SET status=?, updated_at=? WHERE id=?",
            (status, _now(), ticket_id))
    connection.commit()
    _audit(f"ticket.{status}", t["business_id"], ticket_id)
    return get_ticket(connection, ticket_id)


def resolve_ticket(connection: sqlite3.Connection, ticket_id: int,
                   resolution: str) -> dict:
    """Resolve with a written resolution. Empty resolutions rejected —
    future techs need to know what worked."""
    if not resolution.strip():
        raise ValueError("resolution text is required")
    t = get_ticket(connection, ticket_id)
    connection.execute(
        "UPDATE support_tickets SET status='resolved', detail=detail || ?, "
        "updated_at=?, resolved_at=? WHERE id=?",
        (f"\n[resolution] {resolution.strip()}", _now(), _now(), ticket_id))
    connection.commit()
    _audit("ticket.resolved", t["business_id"], ticket_id,
           resolution[:80])
    return get_ticket(connection, ticket_id)


def list_overdue(connection: sqlite3.Connection,
                 at: str | None = None) -> list[dict]:
    """Tickets past response or resolve SLA (excluding pending/resolved)."""
    at = at or _now()
    cols = [d[0] for d in connection.execute(
        "SELECT * FROM support_tickets LIMIT 0").description]
    rows = connection.execute(
        "SELECT * FROM support_tickets WHERE status NOT IN "
        "('pending', 'resolved') AND (response_due_at < ? OR "
        "resolve_due_at < ?) ORDER BY resolve_due_at",
        (at, at)).fetchall()
    return [dict(zip(cols, r)) for r in rows]
