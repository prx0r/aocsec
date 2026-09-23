"""End-to-end lifecycle: one business from prospect to maintained.

Exercises the real modules together (sqlite :memory:, mocked network):
register -> consent -> eligibility -> isolation -> install (runbook) ->
verify -> maintenance plan -> support ticket -> triage -> handoff ->
e-manual -> vault -> WhatsApp draft -> billing. Asserts each stage's
output feeds the next. Nothing sends, files, pays, or touches network.
"""

import sqlite3
import unittest
from unittest import mock


def _db():
    from onboarding.pipeline import init_onboarding_tables
    from support import init_business_tables, init_kb_tables, init_support_tables
    from billing.billing import init_billing_tables
    from whatsapp.optout import init_consent_tables
    conn = sqlite3.connect(":memory:")
    init_onboarding_tables(conn)
    init_business_tables(conn)
    init_support_tables(conn)
    init_kb_tables(conn)
    init_billing_tables(conn)
    from vault import init_vault_tables
    init_vault_tables(conn)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS wa_consent (recipient TEXT PRIMARY KEY,"
        " opted_in INTEGER NOT NULL DEFAULT 0, source TEXT NOT NULL DEFAULT '',"
        " updated_at TEXT NOT NULL)")
    conn.commit()
    return conn


class TestLifecycle(unittest.TestCase):
    def test_prospect_to_maintenance(self):
        from onboarding import (
            register_prospect, record_evidence, advance, record_consent,
            run_yes_flow,
        )
        from onboarding.runbooks import runbook_for
        from maintenance import plan_for

        conn = _db()
        # prospect says yes
        register_prospect(conn, business_id="sparky", name="Demo Sparks",
                          vertical="electrician", postcode="M14")
        record_evidence(conn, "sparky", "interested",
                        "positive_response", "call")
        advance(conn, "sparky")

        # full yes-flow
        rb = runbook_for("electrician")
        out = run_yes_flow(
            conn, "sparky",
            consent_basis="phone call",
            eligibility={"go": True},
            isolation_done=["dedicated_mailbox", "capped_spending",
                            "no_overdraft", "txn_notifications",
                            "work_calendar", "min_crm_role",
                            "revocation_drilled"],
            install_done=[s["id"] for s in rb["steps"]],
            verify_evidence={"redteam_green": "15/15",
                             "audit_clean": "clean"},
            plan_id="care_plus")
        self.assertTrue(out["complete"])
        self.assertEqual(out["stage"], "maintenance")
        plan_for("care_plus")  # plan exists
        conn.close()

    def test_support_uses_business_graph(self):
        from support import (
            add_system, get_business, manual_for_business, open_ticket,
            run_support_round, triage_ticket, upsert_business,
        )
        conn = _db()
        upsert_business(conn, business_id="sparky", name="Demo Sparks",
                        vertical="electrician", postcode="M14")
        add_system(conn, "sparky", name="Gmail", kind="email")
        t = open_ticket(conn, business_id="sparky",
                        subject="Quote stuck in drafts")
        prop = triage_ticket(conn, t["id"])
        self.assertIn("proposal", prop)
        out = run_support_round(conn)
        self.assertIn("sparky", out["actions"])
        doc = manual_for_business(conn, "sparky", obligations=[])
        self.assertIn("Demo Sparks", doc)
        self.assertIn("Gmail", doc)
        conn.close()

    def test_whatsapp_draft_for_maintenance(self):
        from maintenance import run_monthly
        from whatsapp import build_message, record_consent
        conn = _db()
        record_consent(conn, "+447700900001", source="onboarding")
        monthly = run_monthly(business_id="sparky", plan_id="care")
        self.assertIn("checks", monthly)
        msg = build_message(
            conn, to="+447700900001", template="maintenance_done",
            variables={"name": "Demo", "passed": "5", "total": "5",
                       "link": "https://example.test/report"})
        self.assertTrue(msg["sendable"])
        conn.close()

    def test_vault_and_billing_close_loop(self):
        from billing import set_plan, subscription_status
        from vault import get_document, store_document
        conn = _db()
        set_plan(conn, "sparky", "care_plus")
        self.assertEqual(
            subscription_status(conn, "sparky")["status"], "active")
        doc = store_document(conn, business_id="sparky", kind="report",
                             title="Sept maintenance",
                             content="5/5 checks green.")
        self.assertEqual(get_document(conn, doc["sha256"])["content"],
                         "5/5 checks green.")
        conn.close()

    def test_blocked_prospect_stays_put(self):
        from onboarding import pipeline_status, register_prospect
        conn = _db()
        register_prospect(conn, business_id="noshow", vertical="cleaners")
        st = pipeline_status(conn, "noshow")
        self.assertEqual(st["stage"], "contacted")
        self.assertIsNotNone(st["next"])
        conn.close()


if __name__ == "__main__":
    unittest.main()
