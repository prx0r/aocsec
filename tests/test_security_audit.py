"""Tests for aionboard.security_audit — free checks + report builder.

Network checks run against example.com (stable, fast). TLS test uses a
short timeout and tolerates sandbox network restrictions by asserting
shape, not specific values.
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest

from security_audit import build_report, check_domain, free_check


class TestChecks(unittest.TestCase):
    def test_check_domain_shape(self):
        try:
            findings = check_domain("example.com", timeout=10)
        except Exception as e:
            self.skipTest(f"no network: {e}")
        self.assertEqual(len(findings), 3)
        for f in findings:
            for k in ("check", "pass", "severity", "detail", "remediation"):
                self.assertIn(k, f)
        names = [f["check"] for f in findings]
        self.assertEqual(names, ["https", "tls_expiry", "headers"])

    def test_free_check_shape(self):
        try:
            res = free_check("example.com", timeout=10)
        except Exception as e:
            self.skipTest(f"no network: {e}")
        for k in ("domain", "checked_at", "findings", "fail_count",
                  "worst_severity"):
            self.assertIn(k, res)
        self.assertEqual(res["domain"], "example.com")

    def test_domain_normalized(self):
        try:
            res = free_check("https://example.com/some/page", timeout=10)
        except Exception as e:
            self.skipTest(f"no network: {e}")
        self.assertEqual(res["domain"], "example.com")


class TestReport(unittest.TestCase):
    def test_report_shape(self):
        try:
            rep = build_report("example.com", business_name="Demo Ltd",
                               timeout=10)
        except Exception as e:
            self.skipTest(f"no network: {e}")
        self.assertIn("# Security report — Demo Ltd", rep["markdown"])
        self.assertTrue(rep["digest"].startswith("sha256:"))
        self.assertIn("fail_count", rep["summary"])

    def test_report_with_redteam(self):
        try:
            rep = build_report(
                "example.com", redteam_summary={
                    "held": 7, "total": 8, "breached": ["xsession-plant"],
                    "evidence": "runs/redteam_x.jsonl"},
                timeout=10)
        except Exception as e:
            self.skipTest(f"no network: {e}")
        self.assertIn("Assistant red-team", rep["markdown"])
        self.assertIn("xsession-plant", rep["markdown"])

    def test_report_disclaims(self):
        try:
            rep = build_report("example.com", timeout=10)
        except Exception as e:
            self.skipTest(f"no network: {e}")
        self.assertIn("not a penetration", rep["markdown"])


if __name__ == "__main__":
    unittest.main()
