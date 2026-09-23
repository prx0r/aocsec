"""Structured missed-inbound capture. Not a chatbot.

When the tradesperson can't answer, this takes the enquiry: it asks
for the missing slots (job, location, timing) one at a time, then
hands the owner a complete summary. Rules-based extraction, no LLM,
works offline. Builders return payloads; humans send.

Privacy: contacts stored as sha256 hashes, prefixes only in logs.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import datetime, timedelta, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS intake_sessions (
    contact_hash TEXT NOT NULL,
    business_id TEXT NOT NULL,
    vertical TEXT NOT NULL DEFAULT '',
    slots_json TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'open',
    started_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (contact_hash, business_id)
)
"""

SESSION_TTL_HOURS = 48

# slot order per vertical: first missing slot is asked next
SLOT_ORDER = {
    "electrician": ["job", "location", "timing"],
    "default": ["job", "location", "timing"],
}

QUESTIONS = {
    "job": "What needs doing? (e.g. socket, lights, fuse box, fault)",
    "location": "What's the postcode?",
    "timing": "When do you need it? (today, this week, or a day)",
}

ELECTRICIAN_JOBS = [
    "socket", "consumer unit", "fuse box", "fusebox", "light", "lighting",
    "fault", "tripp", "eicr", "certificate", "cert", "cooker", "shower",
    "rewir", "extra point", "ev charger", "smoke alarm", "fan",
]

POSTCODE_RE = re.compile(
    r"\b([A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2})\b", re.IGNORECASE)

TIMING_WORDS = ["today", "tomorrow", "asap", "urgent", "emergency",
                "weekend", "morning", "afternoon", "evening",
                "monday", "tuesday", "wednesday", "thursday", "friday",
                "saturday", "sunday", "next week", "this week"]


def _hash(contact: str) -> str:
    return hashlib.sha256(contact.strip().lower().encode()).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _extract(slots: dict, vertical: str, text: str) -> dict:
    low = text.lower()
    if vertical == "electrician":
        for job in ELECTRICIAN_JOBS:
            if job in low:
                slots["job"] = text.strip()[:200]
                break
    else:
        if len(text.strip()) > 3 and "job" not in slots:
            slots["job"] = text.strip()[:200]
    m = POSTCODE_RE.search(text.upper())
    if m:
        slots["location"] = m.group(1).upper()
    for word in TIMING_WORDS:
        if word in low:
            slots["timing"] = word
            break
    return slots


def record_inbound(connection: sqlite3.Connection, business_id: str,
                   contact: str, text: str,
                   vertical: str = "") -> dict:
    """Fold one inbound message into the contact's open session.

    Returns {"status": "open"|"complete", "next_question": str|None,
    "slots": dict}. Complete fires once, when the last slot fills.
    """
    connection.execute(SCHEMA)
    chash = _hash(contact)
    row = connection.execute(
        "SELECT slots_json, status FROM intake_sessions WHERE "
        "contact_hash = ? AND business_id = ?", (chash, business_id)).fetchone()
    slots = json.loads(row[0]) if row else {}
    was_complete = bool(row) and row[1] == "complete"
    slots = _extract(slots, vertical or "default", text)
    order = SLOT_ORDER.get(vertical, SLOT_ORDER["default"])
    missing = [s for s in order if s not in slots]
    status = "complete" if not missing else "open"
    connection.execute(
        "INSERT INTO intake_sessions (contact_hash, business_id, vertical,"
        " slots_json, status, started_at, updated_at) VALUES (?, ?, ?, ?,"
        " ?, ?, ?) ON CONFLICT (contact_hash, business_id) DO UPDATE SET"
        " slots_json = excluded.slots_json, status = excluded.status,"
        " updated_at = excluded.updated_at",
        (chash, business_id, vertical, json.dumps(slots), status,
         _now(), _now()))
    connection.commit()
    just_completed = status == "complete" and not was_complete
    return {"status": status,
            "next_question": QUESTIONS[missing[0]] if missing else None,
            "slots": slots,
            "just_completed": just_completed}


def owner_alert(business_id: str, slots: dict) -> dict:
    """Draft owner summary. Returned, never sent — human sends."""
    lines = [f"New enquiry ({business_id}):"]
    for key in ("job", "location", "timing"):
        lines.append(f"- {key}: {slots.get(key, '?')}")
    return {"sendable": False, "reason": "owner approval required",
            "text": "\n".join(lines)}


def expire_sessions(connection: sqlite3.Connection) -> int:
    """Mark sessions older than TTL as expired. Returns count."""
    connection.execute(SCHEMA)
    cutoff = (datetime.now(timezone.utc)
              - timedelta(hours=SESSION_TTL_HOURS)).isoformat()
    cur = connection.execute(
        "UPDATE intake_sessions SET status = 'expired' WHERE status = 'open'"
        " AND updated_at < ?", (cutoff,))
    connection.commit()
    return cur.rowcount


def open_sessions(connection: sqlite3.Connection,
                  business_id: str) -> list[dict]:
    """Open sessions for follow-up (owner works them, not the bot)."""
    connection.execute(SCHEMA)
    rows = connection.execute(
        "SELECT slots_json, started_at FROM intake_sessions WHERE "
        "business_id = ? AND status = 'open'", (business_id,)).fetchall()
    return [{"slots": json.loads(r[0]), "started_at": r[1]} for r in rows]
