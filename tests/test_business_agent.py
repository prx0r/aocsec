"""Tests for business_agent onboarding gates + 24h window."""

import unittest

from business_agent import (
    EXCLUDED_VERTICALS,
    eligibility_checklist,
    in_freeform_window,
    record_tos_acceptance,
    window_status,
)


class TestEligibility(unittest.TestCase):
    def _ok(self, **kw):
        base = {"vertical": "electrician", "country_eligible": True,
                "cloud_api": True, "good_standing": True,
                "single_agent": True}
        base.update(kw)
        return eligibility_checklist(**base)

    def test_all_pass(self):
        r = self._ok()
        self.assertTrue(r["eligible"])
        self.assertEqual(r["failed"], [])

    def test_excluded_vertical(self):
        for v in ("health", "finance", "gambling"):
            r = self._ok(vertical=v)
            self.assertFalse(r["eligible"])
            self.assertIn("STOP", r["action"])

    def test_trades_allowed(self):
        for v in ("electrician", "plumber", "cleaner"):
            self.assertTrue(self._ok(vertical=v)["eligible"])

    def test_each_gate_blocks(self):
        for kw in ({"country_eligible": False}, {"cloud_api": False},
                   {"good_standing": False}, {"single_agent": False}):
            self.assertFalse(self._ok(**kw)["eligible"])

    def test_payment_scope(self):
        from business_agent import (
            SCOPES, record_payment_scope, widen_scope)
        self.assertEqual(list(SCOPES),
                         ["handoff_only", "quotes", "bookings", "payments"])
        r = record_payment_scope(business_id="b1", scope="handoff_only",
                                 decided_by="owner")
        self.assertIn("review_by", r)
        w = widen_scope(r, to_scope="quotes", decided_by="owner")
        self.assertEqual(w["scope"], "quotes")
        n = widen_scope(w, to_scope="handoff_only", decided_by="owner")
        self.assertEqual(n["scope"], "handoff_only")
        with self.assertRaises(ValueError):
            record_payment_scope(business_id="b1", scope="everything",
                                 decided_by="owner")

    def test_handoff_window_constraint(self):
        from support import build_context_package
        pkg = build_context_package(
            customer_wants="Fix tap", tried=[], unresolved="slot?",
            business_id="b1", channel="whatsapp",
            last_user_message_at="2020-01-01T00:00:00+00:00")
        self.assertIn("channel_constraint", pkg)
        self.assertIn("template", pkg["channel_constraint"])

    def test_tos_record(self):
        r = record_tos_acceptance(business_id="b1", accepted_by="owner")
        self.assertIn("at", r)
        with self.assertRaises(ValueError):
            record_tos_acceptance(business_id=" ", accepted_by="x")


class TestWindow(unittest.TestCase):
    def test_open(self):
        self.assertTrue(in_freeform_window(
            "2026-09-23T10:00:00+00:00", now="2026-09-23T12:00:00+00:00"))

    def test_closed(self):
        self.assertFalse(in_freeform_window(
            "2026-09-20T10:00:00+00:00", now="2026-09-23T12:00:00+00:00"))
        r = window_status("2026-09-20T10:00:00+00:00",
                          now="2026-09-23T12:00:00+00:00")
        self.assertEqual(r["window"], "closed")
        self.assertIn("template", r["may_send"])

    def test_boundary(self):
        self.assertTrue(in_freeform_window(
            "2026-09-22T12:00:00+00:00", now="2026-09-23T12:00:00+00:00"))
        self.assertFalse(in_freeform_window(
            "2026-09-22T11:59:00+00:00", now="2026-09-23T12:00:00+00:00"))

    def test_future_timestamp(self):
        self.assertFalse(in_freeform_window(
            "2026-09-24T10:00:00+00:00", now="2026-09-23T12:00:00+00:00"))

    def test_gate_blocks_and_passes(self):
        from business_agent import gate_install
        blocked = gate_install(
            business_id="b1", vertical="electrician",
            country_eligible=False, cloud_api=True, good_standing=True,
            single_agent=True)
        self.assertFalse(blocked["go"])
        self.assertIsNone(blocked["tos"])
        gated = gate_install(
            business_id="b1", vertical="electrician",
            country_eligible=True, cloud_api=True, good_standing=True,
            single_agent=True, tos_accepted_by="owner")
        self.assertTrue(gated["go"])
        self.assertIsNotNone(gated["tos"])

    def test_garbage(self):
        self.assertFalse(in_freeform_window("not-a-date"))
        self.assertEqual(window_status("not-a-date")["window"], "unknown")


if __name__ == "__main__":
    unittest.main()
