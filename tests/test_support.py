"""Tests for support backend: tickets, handoff, KB, e-manual."""

import sqlite3
import unittest

from support import (
    HANDOFF_TRIGGERS,
    SLA_TARGETS,
    add_article,
    assign_ticket,
    build_context_package,
    build_systems_graph,
    generate_emanual,
    get_ticket,
    init_kb_tables,
    init_support_tables,
    list_overdue,
    open_ticket,
    promote_resolution,
    record_use,
    resolve_ticket,
    search_articles,
    set_status,
    should_escalate,
)


def _db():
    conn = sqlite3.connect(":memory:")
    init_support_tables(conn)
    init_kb_tables(conn)
    return conn


class TestTickets(unittest.TestCase):
    def test_lifecycle(self):
        conn = _db()
        t = open_ticket(conn, business_id="b1", subject="Quote stuck",
                        priority="high")
        self.assertEqual(t["status"], "new")
        t = assign_ticket(conn, t["id"], "tech-amy")
        self.assertEqual(t["status"], "open")
        t = set_status(conn, t["id"], "pending")
        self.assertEqual(t["status"], "pending")
        t = resolve_ticket(conn, t["id"], "Reset the price book cache.")
        self.assertEqual(t["status"], "resolved")
        self.assertIn("[resolution]", t["detail"])
        conn.close()

    def test_bad_priority_rejected(self):
        with self.assertRaises(ValueError):
            open_ticket(_db(), business_id="b", subject="x", priority="urgent!")

    def test_empty_subject_rejected(self):
        with self.assertRaises(ValueError):
            open_ticket(_db(), business_id="b", subject="  ")

    def test_empty_resolution_rejected(self):
        conn = _db()
        t = open_ticket(conn, business_id="b", subject="x")
        with self.assertRaises(ValueError):
            resolve_ticket(conn, t["id"], "  ")
        conn.close()

    def test_overdue(self):
        conn = _db()
        t = open_ticket(conn, business_id="b", subject="x", priority="low")
        # far future: nothing overdue
        self.assertEqual(list_overdue(conn, at="2020-01-01T00:00:00+00:00"), [])
        # far past due date: overdue
        overdue = list_overdue(conn, at="2099-01-01T00:00:00+00:00")
        self.assertEqual(len(overdue), 1)
        conn.close()


class TestHandoff(unittest.TestCase):
    def test_explicit(self):
        r = should_escalate("please talk to a human about this")
        self.assertTrue(r["escalate"])

    def test_urgency(self):
        r = should_escalate("this is ridiculous, third time asking")
        self.assertTrue(r["escalate"])

    def test_policy(self):
        r = should_escalate("can you handle it?", topics=["payment"])
        self.assertTrue(r["escalate"])
        self.assertIn("policy", r["reason"])

    def test_loops(self):
        r = should_escalate("same question again", repeats=2)
        self.assertTrue(r["escalate"])

    def test_in_scope(self):
        r = should_escalate("what are your opening hours?")
        self.assertFalse(r["escalate"])

    def test_context_package(self):
        pkg = build_context_package(
            customer_wants="Fix the tap", tried=["asked for photos"],
            unresolved="need visit slot", business_id="b1",
            business_name="Demo", transcript_tail=["hi", "tap leaks"])
        self.assertIn("repeat", pkg["instruction"].lower())
        self.assertEqual(pkg["business_id"], "b1")


class TestKB(unittest.TestCase):
    def test_add_search_promote(self):
        conn = _db()
        aid = add_article(conn, title="Reset price cache",
                          body="Settings > cache > reset.", vertical="electrician")
        record_use(conn, aid)
        res = search_articles(conn, "price cache reset")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["id"], aid)
        t = open_ticket(conn, business_id="b", subject="Cache broke")
        t = resolve_ticket(conn, t["id"], "Reset the price book cache.")
        pid = promote_resolution(conn, t, vertical="electrician")
        self.assertIsNotNone(pid)
        self.assertEqual(len(search_articles(conn, "price book cache")), 2)
        conn.close()

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            add_article(_db(), title=" ", body="x")

    def test_no_match(self):
        conn = _db()
        add_article(conn, title="Boilers", body="Annual service.")
        self.assertEqual(search_articles(conn, "quantum toasters"), [])
        conn.close()


class TestEmanual(unittest.TestCase):
    def test_graph_shape(self):
        g = build_systems_graph(
            business={"business_id": "b1", "business_name": "Demo Sparks",
                      "vertical": "electrician", "postcode": "M14"},
            systems=[{"name": "Gmail", "kind": "email", "owner": "customer"}],
            contacts=[{"role": "owner", "channel": "phone", "detail": "071"}],
            qualifications=["NICEIC"])
        self.assertEqual(g["business"]["id"], "b1")
        self.assertEqual(len(g["systems"]), 1)
        self.assertEqual(g["qualifications"], ["NICEIC"])

    def test_manual_sections(self):
        doc = generate_emanual(
            business_name="Demo Sparks", vertical="electrician",
            systems=[{"name": "Gmail", "kind": "email"}],
            obligations=[{"law": "CIS", "requirement": "Verify subs.",
                          "source_url": "https://x.test",
                          "owner_action": "Register."}],
            support_channel="support@test.example",
            assistant_name="Sparky")
        for section in ["Your systems", "Sparky", "Rules that apply",
                        "goes wrong", "support@test.example"]:
            self.assertIn(section, doc)

    def test_empty_manual(self):
        doc = generate_emanual(business_name="X", vertical="cleaner",
                               systems=[], obligations=[])
        self.assertIn("No systems recorded", doc)


if __name__ == "__main__":
    unittest.main()
