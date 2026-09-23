"""Attestation records — who verified what, when, from which register.

Attestations record OUTCOMES (verified/unverified + registration
number), never document contents. Registration numbers are business
credentials shown to customers — safe to store. Personal data from
documents is never stored, by design (no field exists for it).
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone


def init_verify_tables(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS verify_attestations (
            business_id TEXT NOT NULL,
            qualification TEXT NOT NULL,
            verdict TEXT NOT NULL,
            reference TEXT NOT NULL DEFAULT '',
            verified_by TEXT NOT NULL DEFAULT '',
            verified_at TEXT NOT NULL,
            PRIMARY KEY (business_id, qualification)
        );
        """
    )
    connection.commit()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_attestation(connection: sqlite3.Connection, *,
                       business_id: str, qualification: str,
                       verdict: str, reference: str = "",
                       verified_by: str = "") -> dict:
    """Record a verification outcome. Verdicts: verified, unverified,
    expired, not_applicable. Reference = registration number or
    register URL — never document contents."""
    if verdict not in ("verified", "unverified", "expired",
                       "not_applicable"):
        raise ValueError(f"unknown verdict: {verdict}")
    if not business_id.strip() or not qualification.strip():
        raise ValueError("business_id and qualification are required")
    if not verified_by.strip():
        raise ValueError("verified_by is required (named human, not 'system')")
    connection.execute(
        "INSERT OR REPLACE INTO verify_attestations (business_id, "
        "qualification, verdict, reference, verified_by, verified_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (business_id.strip(), qualification.strip(), verdict,
         reference.strip()[:120], verified_by.strip(), _now()))
    connection.commit()
    return {"business_id": business_id.strip(),
            "qualification": qualification.strip(), "verdict": verdict}


def list_attestations(connection: sqlite3.Connection,
                      business_id: str) -> list[dict]:
    """All attestations for a business."""
    rows = connection.execute(
        "SELECT qualification, verdict, reference, verified_by, verified_at "
        "FROM verify_attestations WHERE business_id=? ORDER BY qualification",
        (business_id,)).fetchall()
    return [{"qualification": r[0], "verdict": r[1], "reference": r[2],
             "verified_by": r[3], "verified_at": r[4]} for r in rows]
