"""Tests for whatsapp, scheduler, vault, billing."""

import sqlite3
import unittest

from billing import (
    cancel_subscription,
    set_plan,
    subscription_status,
)
from billing.billing import init_billing_tables
from scheduler import compliance_calendar, due_items, due_jobs, job_ids
from vault import get_document, list_documents, store_document
from vault.vault import init_vault_tables
from whatsapp import (
    TEMPLATES,
    build_message,
    get_template,
    is_opted_in,
    record_consent,
    record_optout,
)


def _db():
    from whatsapp.optout import init_consent_tables
    conn = sqlite3.connect(":memory:")
    init_consent_tables(conn)
    init_vault_tables(conn)
    init_billing_tables(conn)
    return conn


class TestTemplates(unittest.TestCase):
    def test_known_templates(self):
        for name in ["review_due", "cert_expiring", "appointment_reminder",
                     "sla_breach_owner", "maintenance_done",
                     "opportunity_digest", "auth_code"]:
            self.assertIn(name, TEMPLATES)

    def test_unknown_rejected(self):
        from whatsapp.templates import render_template
        with self.assertRaises(ValueError):
            render_template("nope", {})

    def test_missing_variable_rejected(self):
        from whatsapp.templates import render_template
        with self.assertRaises(ValueError):
            render_template("review_due", {"name": "x"})

    def test_get_template(self):
        self.assertEqual(get_template("auth_code")["category"],
                         "authentication")


class TestConsent(unittest.TestCase):
    def test_opt_in_out(self):
        conn = _db()
        self.assertFalse(is_opted_in(conn, "+447700900001"))
        record_consent(conn, "+447700900001", source="onboarding")
        self.assertTrue(is_opted_in(conn, "+447700900001"))
        record_optout(conn, "+447700900001")
        self.assertFalse(is_opted_in(conn, "+447700900001"))
        conn.close()

    def test_empty_recipient(self):
        with self.assertRaises(ValueError):
            record_consent(_db(), "  ")


class TestBuildMessage(unittest.TestCase):
    def _consented(self):
        conn = _db()
        record_consent(conn, "+447700900001")
        return conn

    def test_template_sendable(self):
        m = build_message(self._consented(), to="+447700900001",
                          template="review_due",
                          variables={"name": "Amy", "link": "https://x.test"})
        self.assertTrue(m["sendable"])
        self.assertEqual(m["kind"], "template")

    def test_no_consent_refused(self):
        m = build_message(_db(), to="+447700900001",
                          template="review_due",
                          variables={"name": "Amy", "link": "x"})
        self.assertFalse(m["sendable"])
        self.assertIn("opted", m["reason"])

    def test_freeform_in_window(self):
        from datetime import datetime, timedelta, timezone
        recent = (datetime.now(timezone.utc)
                  - timedelta(hours=1)).isoformat()
        m = build_message(
            self._consented(), to="+447700900001", body="Hi, quick update",
            last_user_message_at=recent)
        self.assertTrue(m["sendable"])
        self.assertEqual(m["kind"], "freeform")

    def test_freeform_closed_window(self):
        m = build_message(
            self._consented(), to="+447700900001", body="Hi",
            last_user_message_at="2020-01-01T00:00:00+00:00")
        self.assertFalse(m["sendable"])
        self.assertTrue(m.get("suggest_template", False))

    def test_freeform_no_timestamp(self):
        m = build_message(self._consented(), to="+447700900001",
                          body="Hi")
        self.assertFalse(m["sendable"])


class TestScheduler(unittest.TestCase):
    def test_job_ids(self):
        ids = job_ids()
        for j in ["sla_watch", "review_due", "cert_expiry",
                  "maintenance_run", "opportunity_digest", "backup_check"]:
            self.assertIn(j, ids)

    def test_due_jobs(self):
        daily = [j["id"] for j in due_jobs("daily")]
        self.assertIn("sla_watch", daily)
        self.assertNotIn("review_due", daily)

    def test_calendar_ordering(self):
        cal = compliance_calendar(
            obligations=[{"law": "CIS", "review_date": "2026-12-31"}],
            certificates=[{"name": "NICEIC", "expires": "2020-01-01"}],
            maintenance_due="2026-12-01T00:00:00+00:00",
            tax_deadlines=[{"title": "VAT", "date": "2026-10-31"}],
            now="2026-09-23T00:00:00+00:00")
        self.assertEqual(cal[0]["kind"], "certificate_expiry")
        self.assertTrue(cal[0]["overdue"])

    def test_due_items(self):
        cal = compliance_calendar(
            certificates=[{"name": "X", "expires": "2020-01-01"}],
            now="2026-09-23T00:00:00+00:00")
        self.assertEqual(len(due_items(cal)), 0 + 1)


class TestVault(unittest.TestCase):
    def test_store_get_list(self):
        conn = _db()
        r = store_document(conn, business_id="b1", kind="report",
                           title="Sept", content="findings here")
        self.assertEqual(len(r["sha256"]), 64)
        got = get_document(conn, r["sha256"])
        self.assertEqual(got["content"], "findings here")
        self.assertEqual(len(list_documents(conn, "b1")), 1)
        self.assertIsNone(get_document(conn, "0" * 64))
        conn.close()

    def test_dedupe(self):
        conn = _db()
        a = store_document(conn, business_id="b1", kind="r",
                           title="t", content="same")
        b = store_document(conn, business_id="b2", kind="r",
                           title="t", content="same")
        self.assertEqual(a["sha256"], b["sha256"])
        conn.close()

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            store_document(_db(), business_id="b1", kind="r",
                           title="t", content="  ")


class TestBilling(unittest.TestCase):
    def test_lifecycle(self):
        conn = _db()
        self.assertEqual(
            subscription_status(conn, "b1")["status"], "none")
        s = set_plan(conn, "b1", "care_plus")
        self.assertEqual(s["plan"], "care_plus")
        self.assertEqual(s["status"], "active")
        c = cancel_subscription(conn, "b1", reason="moved away")
        self.assertEqual(c["status"], "cancelled")
        # history kept: plan row still there
        self.assertEqual(
            subscription_status(conn, "b1")["plan"], "care_plus")
        conn.close()

    def test_unknown_plan(self):
        with self.assertRaises(ValueError):
            set_plan(_db(), "b1", "enterprise-ultra")


if __name__ == "__main__":
    unittest.main()
