"""Tests for onboarding pipeline, runbooks, yes-flow, follow-ups."""

import sqlite3
import unittest

from onboarding import (
    STAGES,
    advance,
    fixes_due,
    followups_for,
    pipeline_status,
    record_consent,
    record_evidence,
    register_prospect,
    review_due,
    run_yes_flow,
    runbook_for,
)


def _db():
    from onboarding.pipeline import init_onboarding_tables
    conn = sqlite3.connect(":memory:")
    init_onboarding_tables(conn)
    return conn


def _to_interested(conn, bid="b1"):
    register_prospect(conn, business_id=bid, name="Demo",
                      vertical="electrician", postcode="M14")
    record_evidence(conn, bid, "interested", "positive_response", "call")
    return advance(conn, bid)


class TestPipeline(unittest.TestCase):
    def test_stages_order(self):
        self.assertEqual(STAGES[0], "contacted")
        self.assertEqual(STAGES[-1], "maintenance")

    def test_register_starts_contacted(self):
        conn = _db()
        st = register_prospect(conn, business_id="b1")
        self.assertEqual(st["stage"], "contacted")
        conn.close()

    def test_advance_blocked_without_evidence(self):
        conn = _db()
        register_prospect(conn, business_id="b1")
        st = advance(conn, "b1")
        self.assertEqual(st["stage"], "contacted")
        self.assertIn("blocked", st)
        conn.close()

    def test_consent_flow(self):
        conn = _db()
        _to_interested(conn)
        st = record_consent(conn, "b1", basis="phone call")
        self.assertEqual(st["stage"], "consent_recorded")
        conn.close()

    def test_consent_needs_basis(self):
        conn = _db()
        _to_interested(conn)
        with self.assertRaises(ValueError):
            record_consent(conn, "b1", basis="  ")
        conn.close()

    def test_unknown_business(self):
        conn = _db()
        with self.assertRaises(LookupError):
            pipeline_status(conn, "nope")
        conn.close()


class TestRunbooks(unittest.TestCase):
    def test_eleven_covered(self):
        for v in ["electrician", "beauty", "hair", "lashes", "nails",
                  "cleaners", "gardeners-window-cleaners", "dog-groomers",
                  "car-detailers", "driving-instructors", "weddings"]:
            rb = runbook_for(v)
            self.assertTrue(rb["known"], v)
            self.assertGreaterEqual(len(rb["steps"]), 5)

    def test_unknown_gets_baseline(self):
        rb = runbook_for("blacksmith")
        self.assertFalse(rb["known"])
        self.assertEqual(len(rb["steps"]), 5)

    def test_electrician_extras(self):
        rb = runbook_for("electrician")
        ids = [s["id"] for s in rb["steps"]]
        self.assertIn("part_p_check", ids)
        self.assertIn("quote_fraud", rb["security_focus"])


class TestYesFlow(unittest.TestCase):
    def _ready(self, conn, bid="b1"):
        _to_interested(conn, bid)
        return {
            "consent_basis": "phone call",
            "eligibility": {"go": True},
            "isolation_done": ["dedicated_mailbox", "capped_spending",
                               "no_overdraft", "txn_notifications",
                               "work_calendar", "min_crm_role",
                               "revocation_drilled"],
            "install_done": [s["id"] for s in
                             runbook_for("electrician")["steps"]],
            "verify_evidence": {"redteam_green": "14/14",
                                "audit_clean": "scan clean"},
            "plan_id": "care",
        }

    def test_full_run(self):
        conn = _db()
        register_prospect(conn, business_id="b1", name="D",
                          vertical="electrician", postcode="M14")
        _to_interested(conn)
        out = run_yes_flow(conn, "b1", **self._ready(conn))
        self.assertTrue(out["complete"])
        self.assertEqual(out["stage"], "maintenance")
        self.assertEqual(
            [s for s, _ in out["log"]],
            ["consent", "eligibility", "isolation", "install", "verify",
             "maintenance"])
        conn.close()

    def test_stops_at_eligibility(self):
        conn = _db()
        register_prospect(conn, business_id="b1", vertical="electrician")
        _to_interested(conn)
        kw = self._ready(conn)
        kw["eligibility"] = {"go": False}
        out = run_yes_flow(conn, "b1", **kw)
        self.assertFalse(out.get("complete", False))
        self.assertEqual(out["stopped_at"], "consent_recorded")
        conn.close()

    def test_stops_at_isolation(self):
        conn = _db()
        register_prospect(conn, business_id="b1", vertical="electrician")
        _to_interested(conn)
        kw = self._ready(conn)
        kw["isolation_done"] = ["dedicated_mailbox"]
        out = run_yes_flow(conn, "b1", **kw)
        self.assertEqual(out["stopped_at"], "eligible")
        self.assertIn("capped_spending", out["detail"])
        conn.close()

    def test_bad_isolation_step(self):
        conn = _db()
        register_prospect(conn, business_id="b1", vertical="electrician")
        _to_interested(conn)
        kw = self._ready(conn)
        kw["isolation_done"] = ["nope"]
        out = run_yes_flow(conn, "b1", **kw)
        self.assertIn("unknown isolation step", out["reason"])
        conn.close()


class TestFollowups(unittest.TestCase):
    def test_fixes_window(self):
        r = fixes_due("2026-09-20T00:00:00+00:00",
                      now="2026-09-23T00:00:00+00:00")
        self.assertEqual(r["window"], "open")
        r = fixes_due("2026-09-01T00:00:00+00:00",
                      now="2026-09-23T00:00:00+00:00")
        self.assertEqual(r["window"], "closed")

    def test_review_due(self):
        r = review_due("2026-01-01T00:00:00+00:00",
                       now="2026-09-23T00:00:00+00:00")
        self.assertTrue(r["due"])
        r = review_due("2026-09-20T00:00:00+00:00",
                       now="2026-09-23T00:00:00+00:00")
        self.assertFalse(r["due"])

    def test_combined(self):
        r = followups_for("b1", installed_at="2026-09-20T00:00:00+00:00",
                          last_review_at="2026-01-01T00:00:00+00:00",
                          now="2026-09-23T00:00:00+00:00")
        self.assertTrue(r["attention"])
        self.assertEqual(len(r["items"]), 2)


if __name__ == "__main__":
    unittest.main()
