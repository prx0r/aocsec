"""Tests for maintenance plans, runner, and monthly report."""

import unittest
from unittest import mock

from maintenance import PLANS, build_monthly_report, plan_for, run_monthly


class TestPlans(unittest.TestCase):
    def test_two_tiers(self):
        self.assertEqual(set(PLANS), {"care", "care_plus"})
        self.assertIn("redteam", plan_for("care_plus")["checks"])
        self.assertNotIn("redteam", plan_for("care")["checks"])

    def test_unknown_rejected(self):
        with self.assertRaises(ValueError):
            plan_for("enterprise-ultra")


class TestRunner(unittest.TestCase):
    def test_care_no_domain(self):
        out = run_monthly(business_id="b1", plan_id="care")
        # legislation leg needs no domain (local graph); domain legs skip
        self.assertIn("legislation", out["checks"])
        self.assertNotIn("email_auth", out["checks"])

    def test_redteam_needs_responder(self):
        out = run_monthly(business_id="b1", plan_id="care_plus")
        self.assertIn("error", out["checks"]["redteam"])

    def test_redteam_runs(self):
        def responder(message, session_id):
            return "I cannot help with that."

        with mock.patch(
                "redteam.run_suite",
                return_value={"held": 14, "total": 14, "breached": [],
                              "errors": [], "evidence": "x"}):
            out = run_monthly(business_id="b1", plan_id="care_plus",
                              responder=responder)
        self.assertEqual(out["checks"]["redteam"]["held"], 14)

    def test_email_auth_mocked(self):
        with mock.patch("emailsec.spf_record",
                        return_value={"pass": True}), \
             mock.patch("emailsec.dmarc_record",
                        return_value={"pass": False}):
            out = run_monthly(business_id="b1", plan_id="care",
                              domain="example.com")
        self.assertEqual(out["checks"]["email_auth"],
                         {"spf": True, "dmarc": False})


class TestReport(unittest.TestCase):
    def test_combined_report(self):
        results = {"business_id": "b1", "plan": "care_plus",
                   "checks": {
                       "email_auth": {"spf": True, "dmarc": False},
                       "redteam": {"held": 14, "total": 14, "breached": []},
                   }}
        rep = build_monthly_report("Demo Ltd", results)
        self.assertIn("Demo Ltd", rep["markdown"])
        self.assertEqual(rep["problems"], 1)
        self.assertTrue(rep["digest"])
        # certificate verifies independently
        from audit_chain.certificates import Certificate as C
        cd = rep["certificate"]
        c2 = C(cert_type=cd["cert_type"], subject=cd["subject"],
               evidence=cd["evidence"], issuer=cd["issuer"],
               metadata=cd["metadata"], issued_at=cd["issued_at"],
               certificate_hash=cd["certificate_hash"])
        self.assertTrue(c2.verify())

    def test_empty_checks(self):
        rep = build_monthly_report("X", {"business_id": "b", "plan": "care",
                                         "checks": {}})
        self.assertEqual(rep["problems"], 0)


if __name__ == "__main__":
    unittest.main()
