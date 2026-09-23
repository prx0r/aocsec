"""Tests for business store, agent loop, and graph wiring."""

import sqlite3
import unittest

from support.agent import run_support_round, sla_watch, triage_ticket
from support.business import (
    add_contact,
    add_qualification,
    add_system,
    get_business,
    init_business_tables,
    list_businesses,
    upsert_business,
)
from support.kb import init_kb_tables
from support.manual import manual_for_business
from support.tickets import init_support_tables, open_ticket


def _db():
    conn = sqlite3.connect(":memory:")
    init_business_tables(conn)
    init_support_tables(conn)
    init_kb_tables(conn)
    return conn


def _biz(conn, bid="b1"):
    upsert_business(conn, business_id=bid, name="Demo Sparks",
                    vertical="electrician", postcode="M14")
    add_system(conn, bid, name="Gmail", kind="email")
    add_contact(conn, bid, role="owner", channel="phone")
    add_qualification(conn, bid, "NICEIC")
    return bid


class TestBusinessStore(unittest.TestCase):
    def test_full_graph(self):
        conn = _db()
        _biz(conn)
        g = get_business(conn, "b1")
        self.assertEqual(g["name"], "Demo Sparks")
        self.assertEqual(len(g["systems"]), 1)
        self.assertEqual(len(g["contacts"]), 1)
        self.assertEqual(g["qualifications"], ["NICEIC"])
        conn.close()

    def test_unknown_business(self):
        conn = _db()
        self.assertIsNone(get_business(conn, "nope"))
        with self.assertRaises(LookupError):
            add_system(conn, "nope", name="x")
        with self.assertRaises(ValueError):
            upsert_business(conn, business_id="  ")
        conn.close()

    def test_portfolio(self):
        conn = _db()
        _biz(conn, "b1")
        _biz(conn, "b2")
        self.assertEqual(len(list_businesses(conn)), 2)
        conn.close()


class TestAgentLoop(unittest.TestCase):
    def test_triage_keyword(self):
        conn = _db()
        _biz(conn)
        t = open_ticket(conn, business_id="b1",
                        subject="Invoice overdue, urgent", priority="medium")
        prop = triage_ticket(conn, t["id"])
        self.assertIn(prop["proposal"], ("critical", "high", "medium", "low"))
        self.assertIn("human approval", prop["note"])
        conn.close()

    def test_triage_judge(self):
        conn = _db()
        _biz(conn)
        t = open_ticket(conn, business_id="b1", subject="Routine query")
        prop = triage_ticket(
            conn, t["id"],
            judge=lambda tool, args: {"label": "low", "confidence": 0.9})
        self.assertEqual(prop["proposal"], "low")
        self.assertEqual(prop["source"], "jev")
        conn.close()

    def test_round_proposes_nothing_sent(self):
        conn = _db()
        _biz(conn)
        open_ticket(conn, business_id="b1", subject="Talk to a human please")
        out = run_support_round(conn)
        self.assertEqual(out["businesses_with_actions"], 1)
        kinds = [i["kind"] for i in out["actions"]["b1"]]
        self.assertIn("triage", kinds)
        self.assertIn("handoff_package", kinds)
        # handoff package carries the business graph
        pkg = [i for i in out["actions"]["b1"]
               if i["kind"] == "handoff_package"][0]["package"]
        self.assertEqual(len(pkg["systems"]), 1)
        self.assertEqual(pkg["qualifications"], ["NICEIC"])
        # nothing was sent or resolved by the round
        t = get_ticket_from(conn)
        self.assertEqual(t["status"], "new")
        conn.close()

    def test_sla_watch(self):
        conn = _db()
        _biz(conn)
        t = open_ticket(conn, business_id="b1", subject="x", priority="low")
        self.assertEqual(sla_watch(conn), [])
        # backdate past SLA: shows up with a draft nudge
        conn.execute("UPDATE support_tickets SET response_due_at=?, "
                     "resolve_due_at=? WHERE id=?",
                     ("2020-01-01T00:00:00+00:00", "2020-01-02T00:00:00+00:00",
                      t["id"]))
        conn.commit()
        nudges = sla_watch(conn)
        self.assertEqual(len(nudges), 1)
        self.assertIn("DRAFT", nudges[0]["draft_nudge"])
        conn.close()


def get_ticket_from(conn):
    from support.tickets import get_ticket
    rows = conn.execute("SELECT id FROM support_tickets").fetchall()
    return get_ticket(conn, rows[0][0])


class TestManualWiring(unittest.TestCase):
    def test_manual_from_graph(self):
        conn = _db()
        _biz(conn)
        doc = manual_for_business(
            conn, "b1",
            obligations=[{"law": "CIS", "requirement": "Verify subs.",
                          "source_url": "https://x.test",
                          "owner_action": "Register."}])
        self.assertIn("Demo Sparks", doc)
        self.assertIn("Gmail", doc)
        self.assertIn("CIS", doc)
        conn.close()

    def test_unknown_business(self):
        with self.assertRaises(LookupError):
            manual_for_business(_db(), "nope")


if __name__ == "__main__":
    unittest.main()
