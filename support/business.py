"""Business store — one graph per customer.

Profiles, systems, contacts, and qualifications persisted per
business_id. Everything downstream (tickets, handoff, KB scoping,
e-manual, maintenance) joins here. This is the "whole company on
our graph" substrate: the business exists once, every workflow
reads the same record.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone


def init_business_tables(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS support_businesses (
            business_id TEXT PRIMARY KEY,
            name TEXT NOT NULL DEFAULT '',
            vertical TEXT NOT NULL DEFAULT '',
            postcode TEXT NOT NULL DEFAULT '',
            team_size INTEGER NOT NULL DEFAULT 1,
            price_book_ref TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS support_systems (
            business_id TEXT NOT NULL,
            name TEXT NOT NULL,
            kind TEXT NOT NULL DEFAULT '',
            owner TEXT NOT NULL DEFAULT 'customer',
            access TEXT NOT NULL DEFAULT '',
            notes TEXT NOT NULL DEFAULT '',
            PRIMARY KEY (business_id, name)
        );
        CREATE TABLE IF NOT EXISTS support_contacts (
            business_id TEXT NOT NULL,
            role TEXT NOT NULL,
            channel TEXT NOT NULL DEFAULT '',
            detail TEXT NOT NULL DEFAULT '',
            PRIMARY KEY (business_id, role)
        );
        CREATE TABLE IF NOT EXISTS support_qualifications (
            business_id TEXT NOT NULL,
            qualification TEXT NOT NULL,
            PRIMARY KEY (business_id, qualification)
        );
        """
    )
    connection.commit()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def upsert_business(connection: sqlite3.Connection, *,
                    business_id: str, name: str = "",
                    vertical: str = "", postcode: str = "",
                    team_size: int = 1,
                    price_book_ref: str = "") -> dict:
    """Create or update a business profile. Empty id rejected."""
    if not business_id.strip():
        raise ValueError("business_id is required")
    connection.execute(
        "INSERT INTO support_businesses (business_id, name, vertical, "
        "postcode, team_size, price_book_ref, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?) "
        "ON CONFLICT(business_id) DO UPDATE SET name=excluded.name, "
        "vertical=excluded.vertical, postcode=excluded.postcode, "
        "team_size=excluded.team_size, "
        "price_book_ref=excluded.price_book_ref, "
        "updated_at=excluded.updated_at",
        (business_id.strip(), name, vertical, postcode, team_size,
         price_book_ref, _now()))
    connection.commit()
    return get_business(connection, business_id)


def get_business(connection: sqlite3.Connection,
                 business_id: str) -> dict | None:
    """Full business graph: profile + systems + contacts + qualifications."""
    row = connection.execute(
        "SELECT * FROM support_businesses WHERE business_id=?",
        (business_id,)).fetchone()
    if row is None:
        return None
    cols = [d[0] for d in connection.execute(
        "SELECT * FROM support_businesses LIMIT 0").description]
    profile = dict(zip(cols, row))
    profile["systems"] = [
        {"name": r[0], "kind": r[1], "owner": r[2], "access": r[3],
         "notes": r[4]}
        for r in connection.execute(
            "SELECT name, kind, owner, access, notes FROM support_systems "
            "WHERE business_id=? ORDER BY name", (business_id,)).fetchall()
    ]
    profile["contacts"] = [
        {"role": r[0], "channel": r[1], "detail": r[2]}
        for r in connection.execute(
            "SELECT role, channel, detail FROM support_contacts "
            "WHERE business_id=? ORDER BY role", (business_id,)).fetchall()
    ]
    profile["qualifications"] = [
        r[0] for r in connection.execute(
            "SELECT qualification FROM support_qualifications "
            "WHERE business_id=? ORDER BY qualification",
            (business_id,)).fetchall()
    ]
    return profile


def add_system(connection: sqlite3.Connection, business_id: str, *,
               name: str, kind: str = "", owner: str = "customer",
               access: str = "", notes: str = "") -> dict:
    """Record a system the business runs. Empty names rejected."""
    if not name.strip():
        raise ValueError("system name is required")
    if get_business(connection, business_id) is None:
        raise LookupError(f"unknown business: {business_id}")
    connection.execute(
        "INSERT INTO support_systems (business_id, name, kind, owner, "
        "access, notes) VALUES (?, ?, ?, ?, ?, ?) "
        "ON CONFLICT(business_id, name) DO UPDATE SET kind=excluded.kind, "
        "owner=excluded.owner, access=excluded.access, "
        "notes=excluded.notes",
        (business_id, name.strip(), kind, owner, access, notes))
    connection.commit()
    return {"business_id": business_id, "name": name.strip()}


def add_contact(connection: sqlite3.Connection, business_id: str, *,
                role: str, channel: str = "", detail: str = "") -> dict:
    """Record a contact channel. Contact VALUES stay minimal — roles
    and channels, never bulk PII dumps."""
    if not role.strip():
        raise ValueError("role is required")
    if get_business(connection, business_id) is None:
        raise LookupError(f"unknown business: {business_id}")
    connection.execute(
        "INSERT INTO support_contacts (business_id, role, channel, detail) "
        "VALUES (?, ?, ?, ?) ON CONFLICT(business_id, role) DO UPDATE SET "
        "channel=excluded.channel, detail=excluded.detail",
        (business_id, role.strip(), channel, detail))
    connection.commit()
    return {"business_id": business_id, "role": role.strip()}


def add_qualification(connection: sqlite3.Connection, business_id: str,
                      qualification: str) -> dict:
    if not qualification.strip():
        raise ValueError("qualification is required")
    if get_business(connection, business_id) is None:
        raise LookupError(f"unknown business: {business_id}")
    connection.execute(
        "INSERT OR IGNORE INTO support_qualifications (business_id, "
        "qualification) VALUES (?, ?)",
        (business_id, qualification.strip()))
    connection.commit()
    return {"business_id": business_id,
            "qualification": qualification.strip()}


def list_businesses(connection: sqlite3.Connection) -> list[dict]:
    """All business ids + names. The managed portfolio."""
    return [{"business_id": r[0], "name": r[1], "vertical": r[2]}
            for r in connection.execute(
                "SELECT business_id, name, vertical FROM support_businesses "
                "ORDER BY business_id").fetchall()]
