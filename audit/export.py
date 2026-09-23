"""Per-business audit export — everything about one customer, one file.

Gathers chained-log records (filtered by business_id in detail),
support tickets, and attestations into a single exportable dict.
This is what "audit everything for them" concretely means: one query,
complete trail, no hunting across systems.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def export_business_audit(
    business_id: str,
    *,
    chain_logs: list[str | Path] | None = None,
    support_conn: sqlite3.Connection | None = None,
    attest_conn: sqlite3.Connection | None = None,
) -> dict:
    """Collect all audit evidence for a business.

    chain_logs: JSONL chained logs to filter by detail.business_id.
    support_conn: connection with support_tickets table.
    attest_conn: connection with verify_attestations table.
    """
    business_id = business_id.strip()
    if not business_id:
        raise ValueError("business_id is required")

    chain_records = []
    for log_path in chain_logs or []:
        p = Path(log_path)
        if not p.exists():
            continue
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                detail = rec.get("detail", {})
                if isinstance(detail, dict) and \
                        detail.get("business_id") == business_id:
                    chain_records.append(rec)

    tickets: list[dict] = []
    if support_conn is not None:
        try:
            cols = [d[0] for d in support_conn.execute(
                "SELECT * FROM support_tickets LIMIT 0").description]
            rows = support_conn.execute(
                "SELECT * FROM support_tickets WHERE business_id=? "
                "ORDER BY id", (business_id,)).fetchall()
            tickets = [dict(zip(cols, r)) for r in rows]
        except sqlite3.OperationalError:
            pass

    attestations: list[dict] = []
    if attest_conn is not None:
        try:
            from verify import list_attestations
            attestations = list_attestations(attest_conn, business_id)
        except Exception:
            pass

    return {
        "business_id": business_id,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "chain_records": chain_records,
        "tickets": tickets,
        "attestations": attestations,
        "counts": {"chain": len(chain_records), "tickets": len(tickets),
                   "attestations": len(attestations)},
    }
