"""Tests for quotes/ — chase tracker, drafts never sends."""

import sqlite3
import unittest

from quotes import (
    due_chases,
    mark_chased,
    pipeline_value,
    record_quote,
    resolve_quote,
)


def _db():
    return sqlite3.connect(":memory:")


def _old(conn, qid, days_ago=5, value=450.0):
    record_quote(conn, qid, "biz1", "hash-cust-1", "consumer unit", value)
    conn.execute(
        "UPDATE quotes SET sent_at = datetime('now', ?) WHERE quote_id = ?",
        (f"-{days_ago} days", qid))
    conn.commit()


class TestChase(unittest.TestCase):
    def test_fresh_quote_not_due(self):
        conn = _db()
        record_quote(conn, "q1", "biz1", "h1", "socket", 95.0)
        self.assertEqual(due_chases(conn, "biz1"), [])

    def test_old_quote_due_highest_value_first(self):
        conn = _db()
        _old(conn, "q-small", value=95.0)
        _old(conn, "q-big", value=900.0)
        due = due_chases(conn, "biz1")
        self.assertEqual([d["quote_id"] for d in due], ["q-big", "q-small"])
        self.assertIn("Following up", due[0]["draft"])

    def test_won_quote_leaves_pipeline(self):
        conn = _db()
        _old(conn, "q1")
        self.assertTrue(resolve_quote(conn, "q1", "won"))
        self.assertEqual(due_chases(conn, "biz1"), [])
        self.assertEqual(pipeline_value(conn, "biz1")["open_quotes"], 0)

    def test_bad_outcome_rejected(self):
        conn = _db()
        _old(conn, "q1")
        self.assertFalse(resolve_quote(conn, "q1", "maybe"))
        self.assertEqual(len(due_chases(conn, "biz1")), 1)

    def test_max_chases_parks_quote(self):
        conn = _db()
        _old(conn, "q1")
        for _ in range(3):
            self.assertTrue(mark_chased(conn, "q1"))
        # last_chase_at is now; force it old again to test the cap
        conn.execute("UPDATE quotes SET last_chase_at = '2000-01-01'"
                     " WHERE quote_id = 'q1'")
        conn.commit()
        self.assertEqual(due_chases(conn, "biz1"), [])

    def test_pipeline_totals(self):
        conn = _db()
        _old(conn, "q1", value=100.0)
        _old(conn, "q2", value=200.0)
        pipe = pipeline_value(conn, "biz1")
        self.assertEqual(pipe["open_quotes"], 2)
        self.assertEqual(pipe["open_value_gbp"], 300.0)


if __name__ == "__main__":
    unittest.main()
