"""Quote chase tracker. Quotes sent and never followed up are dead money.

A quote is recorded at send time with value + customer. It becomes
due for chase after CHASE_DAYS. Each chase is a draft for the owner —
the system never sends to the customer itself. Outcomes: won, lost,
or keep chasing (max MAX_CHASES, then park it so owners aren't nagged
forever).
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS quotes (
    quote_id TEXT PRIMARY KEY,
    business_id TEXT NOT NULL,
    customer_hash TEXT NOT NULL,
    summary TEXT NOT NULL DEFAULT '',
    value_gbp REAL NOT NULL DEFAULT 0,
    sent_at TEXT NOT NULL,
    last_chase_at TEXT NOT NULL DEFAULT '',
    chases INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'sent'
)
"""

CHASE_DAYS = 3
MAX_CHASES = 3


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_quote(connection: sqlite3.Connection, quote_id: str,
                 business_id: str, customer_hash: str, summary: str,
                 value_gbp: float = 0.0) -> None:
    """Record a sent quote. Customer identified by hash, never raw PII."""
    connection.execute(SCHEMA)
    connection.execute(
        "INSERT OR REPLACE INTO quotes (quote_id, business_id,"
        " customer_hash, summary, value_gbp, sent_at, status) VALUES"
        " (?, ?, ?, ?, ?, ?, 'sent')",
        (quote_id, business_id, customer_hash, summary[:300],
         value_gbp, _now()))
    connection.commit()


def resolve_quote(connection: sqlite3.Connection, quote_id: str,
                  outcome: str) -> bool:
    """Mark won or lost. Returns False for unknown ids/outcomes."""
    if outcome not in ("won", "lost"):
        return False
    connection.execute(SCHEMA)
    cur = connection.execute(
        "UPDATE quotes SET status = ? WHERE quote_id = ? AND status = 'sent'",
        (outcome, quote_id))
    connection.commit()
    return cur.rowcount == 1


def due_chases(connection: sqlite3.Connection,
               business_id: str) -> list[dict]:
    """Quotes owed a follow-up, highest value first. Drafts, not sends."""
    connection.execute(SCHEMA)
    cutoff = (datetime.now(timezone.utc)
              - timedelta(days=CHASE_DAYS)).isoformat()
    rows = connection.execute(
        "SELECT quote_id, summary, value_gbp, chases, sent_at FROM quotes"
        " WHERE business_id = ? AND status = 'sent' AND chases < ? AND"
        " COALESCE(NULLIF(last_chase_at, ''), sent_at) < ?"
        " ORDER BY value_gbp DESC",
        (business_id, MAX_CHASES, cutoff)).fetchall()
    return [{"quote_id": r[0], "summary": r[1], "value_gbp": r[2],
             "chases": r[3],
             "draft": f"Following up on your quote ({r[1][:80]}). "
                      f"Still interested? Reply YES and we'll book it in."}
            for r in rows]


def mark_chased(connection: sqlite3.Connection, quote_id: str) -> bool:
    """Record that the owner sent a chase. Returns False if unknown."""
    connection.execute(SCHEMA)
    cur = connection.execute(
        "UPDATE quotes SET chases = chases + 1, last_chase_at = ? WHERE"
        " quote_id = ? AND status = 'sent'", (_now(), quote_id))
    connection.commit()
    return cur.rowcount == 1


def pipeline_value(connection: sqlite3.Connection,
                   business_id: str) -> dict:
    """Open pipeline totals — the number that makes owners act."""
    connection.execute(SCHEMA)
    row = connection.execute(
        "SELECT COUNT(*), COALESCE(SUM(value_gbp), 0) FROM quotes WHERE"
        " business_id = ? AND status = 'sent'",
        (business_id,)).fetchone()
    return {"open_quotes": row[0], "open_value_gbp": row[1]}
