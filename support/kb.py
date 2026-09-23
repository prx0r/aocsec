"""Shared knowledge base — one answer source for bot and humans.

Both the assistant and the human tech answer from the same articles.
When a ticket resolves with new knowledge, it becomes an article, so
the next identical question never needs a human. SQLite FTS-free:
keyword scoring is honest about its limits.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone


def init_kb_tables(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS kb_articles (
            id INTEGER PRIMARY KEY,
            vertical TEXT NOT NULL DEFAULT '',
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT 'manual',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            use_count INTEGER NOT NULL DEFAULT 0
        );
        """
    )
    connection.commit()


def add_article(connection: sqlite3.Connection, *, title: str, body: str,
                vertical: str = "", source: str = "manual") -> int:
    """Add an article. Empty title/body rejected."""
    if not title.strip() or not body.strip():
        raise ValueError("title and body are required")
    now = datetime.now(timezone.utc).isoformat()
    cur = connection.execute(
        "INSERT INTO kb_articles (vertical, title, body, source, "
        "created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
        (vertical, title.strip(), body.strip(), source, now, now))
    connection.commit()
    return int(cur.lastrowid)


def record_use(connection: sqlite3.Connection, article_id: int) -> None:
    """Count an answer served from an article. Drives usefulness ranking."""
    connection.execute(
        "UPDATE kb_articles SET use_count = use_count + 1, "
        "updated_at = updated_at WHERE id = ?", (article_id,))
    connection.commit()


def search_articles(connection: sqlite3.Connection, query: str,
                    vertical: str = "", limit: int = 5) -> list[dict]:
    """Keyword search, vertical preferred. Returns most useful first."""
    words = [w.lower() for w in query.split() if len(w) > 2]
    if not words:
        return []
    rows = connection.execute(
        "SELECT id, vertical, title, body, source, use_count "
        "FROM kb_articles").fetchall()
    scored = []
    for rid, vert, title, body, source, uses in rows:
        if vertical and vert and vert != vertical:
            continue
        hay = f"{title} {body}".lower()
        score = sum(hay.count(w) for w in words)
        if score:
            scored.append({"id": rid, "vertical": vert, "title": title,
                           "body": body, "source": source,
                           "score": score, "use_count": uses})
    scored.sort(key=lambda a: (a["score"], a["use_count"]), reverse=True)
    return scored[:limit]


def promote_resolution(connection: sqlite3.Connection, ticket: dict,
                       vertical: str = "") -> int | None:
    """Turn a resolved ticket into a KB article. Returns article id or
    None when the ticket has no usable resolution text."""
    detail = ticket.get("detail", "")
    if "[resolution]" not in detail:
        return None
    subject = ticket.get("subject", "Resolved issue")
    return add_article(connection, title=f"Resolved: {subject}",
                       body=detail, vertical=vertical, source="ticket")
