"""Tests for recall/ — lapsed win-back, drafts never sends."""

import sqlite3
import unittest
from datetime import datetime, timedelta, timezone

from recall import (
    due_recalls,
    mark_recalled,
    recall_value,
    record_visit,
)


def _db():
    return sqlite3.connect(":memory:")


def _old_visit(conn, h, days_ago, vertical="nails", service="infill"):
    past = (datetime.now(timezone.utc)
            - timedelta(days=days_ago)).isoformat()
    record_visit(conn, h, "biz1", vertical=vertical, service=service,
                 visited_at=past)


class TestRecall(unittest.TestCase):
    def test_recent_visit_not_due(self):
        conn = _db()
        _old_visit(conn, "h1", 5)  # nails interval 21
        self.assertEqual(due_recalls(conn, "biz1"), [])

    def test_overdue_due_longest_first(self):
        conn = _db()
        _old_visit(conn, "h-near", 30)
        _old_visit(conn, "h-far", 60)
        due = due_recalls(conn, "biz1")
        self.assertEqual([d["customer_hash"] for d in due],
                         ["h-far", "h-near"])
        self.assertIn("book back in", due[0]["draft"])

    def test_revisit_resets_clock(self):
        conn = _db()
        _old_visit(conn, "h1", 60)
        self.assertEqual(len(due_recalls(conn, "biz1")), 1)
        record_visit(conn, "h1", "biz1", vertical="nails")
        self.assertEqual(due_recalls(conn, "biz1"), [])

    def test_max_recalls_parks_client(self):
        conn = _db()
        _old_visit(conn, "h1", 60)
        self.assertTrue(mark_recalled(conn, "h1", "biz1"))
        self.assertTrue(mark_recalled(conn, "h1", "biz1"))
        self.assertEqual(due_recalls(conn, "biz1"), [])

    def test_weddings_excluded(self):
        conn = _db()
        _old_visit(conn, "h1", 400, vertical="weddings")
        self.assertEqual(due_recalls(conn, "biz1"), [])

    def test_recall_value(self):
        conn = _db()
        _old_visit(conn, "h1", 30)  # 9 overdue (30-21)
        val = recall_value(conn, "biz1")
        self.assertEqual(val["drifting_clients"], 1)
        self.assertGreaterEqual(val["total_overdue_days"], 9)


if __name__ == "__main__":
    unittest.main()
