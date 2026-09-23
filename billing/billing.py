"""Subscription state per business. No charging here — ever."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

PLANS = ("care", "care_plus")


def init_billing_tables(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS billing_subscriptions (
            business_id TEXT PRIMARY KEY,
            plan TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            started_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS billing_events (
            business_id TEXT NOT NULL,
            at TEXT NOT NULL,
            event TEXT NOT NULL,
            detail TEXT NOT NULL DEFAULT ''
        );
        """
    )
    connection.commit()


def _log(connection: sqlite3.Connection, business_id: str,
         event: str, detail: str = "") -> None:
    connection.execute(
        "INSERT INTO billing_events (business_id, at, event, detail) "
        "VALUES (?, ?, ?, ?)",
        (business_id, datetime.now(timezone.utc).isoformat(), event,
         detail))
    connection.commit()


def set_plan(connection: sqlite3.Connection, business_id: str,
             plan: str) -> dict:
    """Set or change plan. Unknown plans rejected. Recorded as event."""
    if plan not in PLANS:
        raise ValueError(f"unknown plan: {plan}. Known: {list(PLANS)}")
    if not business_id.strip():
        raise ValueError("business_id is required")
    now = datetime.now(timezone.utc).isoformat()
    connection.execute(
        "INSERT INTO billing_subscriptions (business_id, plan, status, "
        "started_at, updated_at) VALUES (?, ?, 'active', ?, ?) "
        "ON CONFLICT(business_id) DO UPDATE SET plan=excluded.plan, "
        "status='active', updated_at=excluded.updated_at",
        (business_id.strip(), plan, now, now))
    _log(connection, business_id.strip(), "plan_set", plan)
    connection.commit()
    return subscription_status(connection, business_id)


def cancel_subscription(connection: sqlite3.Connection, business_id: str,
                        reason: str = "") -> dict:
    """Cancel. History kept (events table); row marked, never deleted."""
    _log(connection, business_id, "cancelled", reason[:200])
    connection.execute(
        "UPDATE billing_subscriptions SET status='cancelled', "
        "updated_at=? WHERE business_id=?",
        (datetime.now(timezone.utc).isoformat(), business_id))
    connection.commit()
    return subscription_status(connection, business_id)


def subscription_status(connection: sqlite3.Connection,
                        business_id: str) -> dict:
    """Current subscription or explicit none (never implied)."""
    row = connection.execute(
        "SELECT plan, status, started_at, updated_at "
        "FROM billing_subscriptions WHERE business_id=?",
        (business_id,)).fetchone()
    if row is None:
        return {"business_id": business_id, "plan": None,
                "status": "none"}
    return {"business_id": business_id, "plan": row[0], "status": row[1],
            "started_at": row[2], "updated_at": row[3]}
