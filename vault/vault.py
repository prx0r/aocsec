"""Content-addressed document store. Stdlib + sqlite3."""

from __future__ import annotations

import hashlib
import sqlite3
from datetime import datetime, timezone


def init_vault_tables(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS vault_docs (
            sha256 TEXT PRIMARY KEY,
            business_id TEXT NOT NULL,
            kind TEXT NOT NULL,
            title TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS vault_blobs (
            sha256 TEXT PRIMARY KEY,
            content TEXT NOT NULL
        );
        """
    )
    connection.commit()


def store_document(connection: sqlite3.Connection, *, business_id: str,
                   kind: str, title: str, content: str) -> dict:
    """Store a document. Returns {sha256, business_id, kind}.

    Blobs dedupe by hash; the doc row links business+kind to bytes.
    Empty content rejected.
    """
    if not content.strip():
        raise ValueError("content is required")
    if not business_id.strip():
        raise ValueError("business_id is required")
    sha = hashlib.sha256(content.encode()).hexdigest()
    now = datetime.now(timezone.utc).isoformat()
    connection.execute(
        "INSERT OR IGNORE INTO vault_blobs (sha256, content) VALUES (?, ?)",
        (sha, content))
    connection.execute(
        "INSERT OR REPLACE INTO vault_docs (sha256, business_id, kind, "
        "title, created_at) VALUES (?, ?, ?, ?, ?)",
        (sha, business_id.strip(), kind, title, now))
    connection.commit()
    return {"sha256": sha, "business_id": business_id.strip(), "kind": kind}


def get_document(connection: sqlite3.Connection, sha256: str) -> dict | None:
    """Retrieve by hash. None when absent."""
    row = connection.execute(
        "SELECT d.business_id, d.kind, d.title, d.created_at, b.content "
        "FROM vault_docs d JOIN vault_blobs b ON d.sha256 = b.sha256 "
        "WHERE d.sha256 = ?", (sha256,)).fetchone()
    if row is None:
        return None
    return {"sha256": sha256, "business_id": row[0], "kind": row[1],
            "title": row[2], "created_at": row[3], "content": row[4]}


def list_documents(connection: sqlite3.Connection,
                   business_id: str) -> list[dict]:
    """All documents for a business, newest first."""
    rows = connection.execute(
        "SELECT sha256, kind, title, created_at FROM vault_docs "
        "WHERE business_id=? ORDER BY created_at DESC",
        (business_id,)).fetchall()
    return [{"sha256": r[0], "kind": r[1], "title": r[2],
             "created_at": r[3]} for r in rows]
