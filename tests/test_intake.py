"""Tests for intake/ — structured capture, no LLM, no network."""

import sqlite3
import unittest

from intake import (
    expire_sessions,
    open_sessions,
    owner_alert,
    record_inbound,
)


def _db():
    return sqlite3.connect(":memory:")


class TestCapture(unittest.TestCase):
    def test_three_messages_complete_electrician(self):
        conn = _db()
        r1 = record_inbound(conn, "biz1", "+447700900100",
                            "my fuse box keeps tripping",
                            vertical="electrician")
        self.assertEqual(r1["status"], "open")
        self.assertIn("postcode", r1["next_question"].lower())
        r2 = record_inbound(conn, "biz1", "+447700900100", "M1 1AA",
                            vertical="electrician")
        self.assertEqual(r2["status"], "open")
        r3 = record_inbound(conn, "biz1", "+447700900100",
                            "tomorrow morning if poss",
                            vertical="electrician")
        self.assertEqual(r3["status"], "complete")
        self.assertTrue(r3["just_completed"])
        self.assertIsNone(r3["next_question"])
        self.assertIn("M1", r3["slots"]["location"])

    def test_just_completed_fires_once(self):
        conn = _db()
        record_inbound(conn, "biz1", "+447700900100", "socket",
                       vertical="electrician")
        record_inbound(conn, "biz1", "+447700900100", "M1 1AA",
                       vertical="electrician")
        r = record_inbound(conn, "biz1", "+447700900100", "today",
                           vertical="electrician")
        self.assertTrue(r["just_completed"])
        r2 = record_inbound(conn, "biz1", "+447700900100", "thanks",
                            vertical="electrician")
        self.assertFalse(r2["just_completed"])

    def test_contacts_hashed_not_stored(self):
        conn = _db()
        record_inbound(conn, "biz1", "+447700900100", "socket",
                       vertical="electrician")
        rows = conn.execute(
            "SELECT contact_hash FROM intake_sessions").fetchall()
        self.assertNotIn("+447700900100", rows[0][0])
        self.assertEqual(len(rows[0][0]), 64)

    def test_owner_alert_is_draft_never_sendable(self):
        alert = owner_alert("biz1", {"job": "socket", "location": "M1 1AA",
                                     "timing": "today"})
        self.assertFalse(alert.get("sendable"))
        self.assertIn("socket", alert["text"])

    def test_expiry(self):
        conn = _db()
        record_inbound(conn, "biz1", "+447700900100", "socket",
                       vertical="electrician")
        conn.execute("UPDATE intake_sessions SET updated_at = '2000-01-01'")
        conn.commit()
        self.assertEqual(expire_sessions(conn), 1)
        self.assertEqual(open_sessions(conn, "biz1"), [])

    def test_open_sessions_for_owner_followup(self):
        conn = _db()
        record_inbound(conn, "biz1", "+447700900100", "socket",
                       vertical="electrician")
        opened = open_sessions(conn, "biz1")
        self.assertEqual(len(opened), 1)
        self.assertIn("socket", opened[0]["slots"]["job"])


if __name__ == "__main__":
    unittest.main()
