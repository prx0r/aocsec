"""Opt-in/opt-out per recipient. No consent record = no messages.

WhatsApp requires opt-in for business-initiated conversations. STOP
always works. Every send path checks this first.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone


def init_consent_tables(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS wa_consent (
            recipient TEXT PRIMARY KEY,
            opted_in INTEGER NOT NULL DEFAULT 0,
            source TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL
        );
        """
    )
    connection.commit()


def record_consent(connection: sqlite3.Connection, recipient: str,
                   source: str = "") -> dict:
    """Record opt-in. Recipient = phone in E.164 (+447...)."""
    recipient = recipient.strip()
    if not recipient:
        raise ValueError("recipient is required")
    now = datetime.now(timezone.utc).isoformat()
    connection.execute(
        "INSERT INTO wa_consent (recipient, opted_in, source, updated_at) "
        "VALUES (?, 1, ?, ?) ON CONFLICT(recipient) DO UPDATE SET "
        "opted_in=1, source=excluded.source, updated_at=excluded.updated_at",
        (recipient, source, now))
    connection.commit()
    return {"recipient": recipient, "opted_in": True}


def record_optout(connection: sqlite3.Connection, recipient: str) -> dict:
    """STOP. Immediate, unconditional, no confirmation step needed."""
    recipient = recipient.strip()
    now = datetime.now(timezone.utc).isoformat()
    connection.execute(
        "INSERT INTO wa_consent (recipient, opted_in, source, updated_at) "
        "VALUES (?, 0, 'stop', ?) ON CONFLICT(recipient) DO UPDATE SET "
        "opted_in=0, source='stop', updated_at=excluded.updated_at",
        (recipient, now))
    connection.commit()
    return {"recipient": recipient, "opted_in": False}


def is_opted_in(connection: sqlite3.Connection, recipient: str) -> bool:
    """Gate every send path on this. Unknown = not opted in."""
    row = connection.execute(
        "SELECT opted_in FROM wa_consent WHERE recipient=?",
        (recipient.strip(),)).fetchone()
    return bool(row and row[0])
