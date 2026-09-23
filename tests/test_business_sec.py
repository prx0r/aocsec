"""Tests for emailsec, invoice verify, devicecheck, presence, ICO seed."""

import unittest
from unittest import mock

from devicecheck import checklist_status, backup_checklist, device_checklist, mark_done as dev_done
from emailsec import assess_payment_change, dmarc_record, spf_record, verification_checklist
from presence import checklist_status as pstatus, mark_done as pdone, presence_checklist


def _doh_factory(mapping):
    def fake(name, rrtype="TXT", timeout=15):
        return mapping.get(name, [])
    return fake


class TestEmailDNS(unittest.TestCase):
    def test_spf_present(self):
        with mock.patch("emailsec.dns._doh",
                        return_value=["v=spf1 include:_spf.google.com ~all"]):
            r = spf_record("example.com")
        self.assertTrue(r["pass"])
        self.assertIn("softfail", r["detail"])

    def test_spf_missing(self):
        with mock.patch("emailsec.dns._doh", return_value=[]):
            r = spf_record("example.com")
        self.assertFalse(r["pass"])
        self.assertEqual(r["severity"], "high")

    def test_dmarc_policy(self):
        with mock.patch("emailsec.dns._doh",
                        return_value=["v=DMARC1; p=reject;"]):
            r = dmarc_record("example.com")
        self.assertTrue(r["pass"])
        self.assertIsNone(r["remediation"])

    def test_dmarc_missing(self):
        with mock.patch("emailsec.dns._doh", return_value=[]):
            r = dmarc_record("example.com")
        self.assertFalse(r["pass"])

    def test_unreachable_degrades_gracefully(self):
        # _doh swallows transport errors -> empty -> missing-record path
        with mock.patch("emailsec.dns._doh", return_value=[]):
            r = spf_record("example.com")
            self.assertFalse(r["pass"])
            self.assertEqual(r["severity"], "high")


class TestInvoiceVerify(unittest.TestCase):
    def test_blocked_by_default(self):
        r = assess_payment_change(verified_by_call=False,
                                  two_facts_confirmed=False, recorded=False)
        self.assertEqual(r["decision"], "BLOCKED")
        self.assertEqual(len(r["missing"]), 3)

    def test_cleared(self):
        r = assess_payment_change(verified_by_call=True,
                                  two_facts_confirmed=True, recorded=True)
        self.assertEqual(r["decision"], "CLEARED")

    def test_partial(self):
        r = assess_payment_change(verified_by_call=True,
                                  two_facts_confirmed=False, recorded=False)
        self.assertEqual(r["decision"], "BLOCKED")
        self.assertEqual(len(r["missing"]), 2)

    def test_checklist_shape(self):
        steps = verification_checklist(supplier="Acme", amount_gbp=1850.0,
                                       requested_channel="email")
        self.assertEqual(len(steps), 4)
        self.assertIn("hostile", steps[0]["detail"])


class TestDeviceBackup(unittest.TestCase):
    def test_lifecycle(self):
        cl = device_checklist()
        self.assertEqual(len(cl), 5)
        cl = dev_done(cl, "screen_lock")
        st = checklist_status(cl)
        self.assertEqual(st["done"], 1)
        self.assertFalse(st["complete"])
        with self.assertRaises(ValueError):
            dev_done(cl, "nope")

    def test_backup_recovery_codes(self):
        steps = [s["step"] for s in backup_checklist()]
        self.assertIn("2fa_recovery", steps)


class TestPresence(unittest.TestCase):
    def test_lifecycle(self):
        cl = presence_checklist()
        self.assertEqual(len(cl), 6)
        for s in ["gbp_ownership", "social_admins", "domain_control"]:
            cl = pdone(cl, s)
        st = pstatus(cl)
        self.assertEqual(st["done"], 3)
        with self.assertRaises(ValueError):
            pdone(cl, "nope")


class TestICOSeed(unittest.TestCase):
    def test_ico_rule_loads(self):
        from legislation.graph import build_graph, obligations_for
        g = build_graph()
        res = [o for o in g if o.id == "LEG-UK-ICO-FEE"]
        self.assertEqual(len(res), 1)
        self.assertIn("ico.org.uk", res[0].source_url)


if __name__ == "__main__":
    unittest.main()
