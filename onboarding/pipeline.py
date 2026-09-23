"""Pipeline state machine: prospect to maintained customer.

Stages advance only forward, each gated on the previous stage's
evidence. Consent is the load-bearing transition: nothing install-ish
happens before it (matches aionboard contact rules + our scope).
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

STAGES = (
    "contacted",
    "interested",
    "consent_recorded",
    "eligible",
    "isolated",
    "installed",
    "verified",
    "maintenance",
)

# stage -> evidence required to ENTER it
_GATES = {
    "contacted": ["first_touch"],
    "interested": ["positive_response"],
    "consent_recorded": ["consent_basis"],
    "eligible": ["eligibility_pass"],
    "isolated": ["isolation_complete"],
    "installed": ["install_checklist"],
    "verified": ["verification_evidence"],
    "maintenance": ["plan_id"],
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_onboarding_tables(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS ob_prospects (
            business_id TEXT PRIMARY KEY,
            name TEXT NOT NULL DEFAULT '',
            vertical TEXT NOT NULL DEFAULT '',
            postcode TEXT NOT NULL DEFAULT '',
            stage TEXT NOT NULL DEFAULT 'contacted',
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS ob_evidence (
            business_id TEXT NOT NULL,
            stage TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL DEFAULT '',
            recorded_at TEXT NOT NULL,
            PRIMARY KEY (business_id, stage, key)
        );
        """
    )
    connection.commit()


def register_prospect(connection: sqlite3.Connection, *,
                      business_id: str, name: str = "",
                      vertical: str = "", postcode: str = "") -> dict:
    """First touch. Starts at contacted."""
    if not business_id.strip():
        raise ValueError("business_id is required")
    connection.execute(
        "INSERT OR IGNORE INTO ob_prospects (business_id, name, vertical, "
        "postcode, stage, updated_at) VALUES (?, ?, ?, ?, 'contacted', ?)",
        (business_id.strip(), name, vertical, postcode, _now()))
    connection.execute(
        "INSERT OR IGNORE INTO ob_evidence (business_id, stage, key, "
        "value, recorded_at) VALUES (?, 'contacted', 'first_touch', "
        "'registered', ?)",
        (business_id.strip(), _now()))
    connection.commit()
    return pipeline_status(connection, business_id)


def record_evidence(connection: sqlite3.Connection, business_id: str,
                    stage: str, key: str, value: str = "yes") -> dict:
    """Attach evidence for a stage gate."""
    if _stage(connection, business_id) is None:
        raise LookupError(f"unknown business: {business_id}")
    connection.execute(
        "INSERT OR REPLACE INTO ob_evidence (business_id, stage, key, "
        "value, recorded_at) VALUES (?, ?, ?, ?, ?)",
        (business_id, stage, key, value, _now()))
    connection.commit()
    return {"business_id": business_id, "stage": stage, "key": key}


def record_consent(connection: sqlite3.Connection, business_id: str, *,
                   basis: str) -> dict:
    """The yes. Records consent basis (call, email reply, form, referral).

    Consent advances interested -> consent_recorded ONLY. Everything
    downstream keys off this row existing.
    """
    if not basis.strip():
        raise ValueError("consent basis is required")
    if _stage(connection, business_id) is None:
        raise LookupError(f"unknown business: {business_id}")
    record_evidence(connection, business_id, "consent_recorded",
                    "consent_basis", basis.strip())
    return advance(connection, business_id)


def _stage(connection: sqlite3.Connection, business_id: str) -> str | None:
    row = connection.execute(
        "SELECT stage FROM ob_prospects WHERE business_id=?",
        (business_id,)).fetchone()
    return row[0] if row else None


def _has_evidence(connection: sqlite3.Connection, business_id: str,
                  stage: str) -> bool:
    required = _GATES.get(stage, [])
    if not required:
        return True
    have = {r[0] for r in connection.execute(
        "SELECT key FROM ob_evidence WHERE business_id=? AND stage=?",
        (business_id, stage)).fetchall()}
    return all(k in have for k in required)


def advance(connection: sqlite3.Connection, business_id: str) -> dict:
    """Advance one stage if its gate evidence exists. Never skips."""
    current = _stage(connection, business_id)
    if current is None:
        raise LookupError(f"unknown business: {business_id}")
    idx = STAGES.index(current)
    if idx >= len(STAGES) - 1:
        return pipeline_status(connection, business_id)
    nxt = STAGES[idx + 1]
    if not _has_evidence(connection, business_id, nxt):
        return {**pipeline_status(connection, business_id),
                "blocked": f"missing evidence for {nxt}: "
                           f"{_GATES.get(nxt, [])}"}
    connection.execute(
        "UPDATE ob_prospects SET stage=?, updated_at=? WHERE business_id=?",
        (nxt, _now(), business_id))
    connection.commit()
    return pipeline_status(connection, business_id)


def pipeline_status(connection: sqlite3.Connection,
                    business_id: str) -> dict:
    """Current stage + what's needed next."""
    current = _stage(connection, business_id)
    if current is None:
        raise LookupError(f"unknown business: {business_id}")
    idx = STAGES.index(current)
    nxt = STAGES[idx + 1] if idx < len(STAGES) - 1 else None
    return {"business_id": business_id, "stage": current,
            "next": nxt,
            "needs": _GATES.get(nxt, []) if nxt else []}
