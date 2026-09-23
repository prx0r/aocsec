"""Tests for aocsec safe tax organizer. No network, no filing, no payments."""

import json
import tempfile
import unittest
from pathlib import Path

from tax import (
    RECORD_TYPES,
    add_month,
    load_ledger,
    mtd_checklist,
    records_gap,
    rolling_12m,
    save_ledger,
    threshold_status,
)


class TestTurnover(unittest.TestCase):
    def test_add_and_roll(self):
        led = {}
        for i, m in enumerate(["2025-10", "2025-11", "2025-12", "2026-01"], 1):
            led = add_month(led, m, 1000.0 * i)
        self.assertEqual(rolling_12m(led), 10000.0)
        self.assertEqual(rolling_12m(led, through="2025-11"), 3000.0)
        self.assertEqual(rolling_12m({}), 0.0)

    def test_bad_month_rejected(self):
        with self.assertRaises(ValueError):
            add_month({}, "Oct 2025", 100)
        with self.assertRaises(ValueError):
            add_month({}, "2025-10", -5)

    def test_bands(self):
        self.assertEqual(threshold_status(500, 1000)["band"], "comfortable")
        self.assertEqual(threshold_status(850, 1000)["band"], "watch")
        self.assertEqual(threshold_status(950, 1000)["band"], "act_now")
        self.assertEqual(threshold_status(1000, 1000)["band"], "likely_over")
        self.assertEqual(threshold_status(500, None)["band"], "unknown")
        self.assertIn("gov.uk", threshold_status(500, None)["action"])
        with self.assertRaises(ValueError):
            threshold_status(500, 0)

    def test_ledger_roundtrip_600(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "ledger.json"
            save_ledger(p, {"2026-01": 1234.5})
            self.assertEqual(oct(p.stat().st_mode & 0o777), "0o600")
            self.assertEqual(load_ledger(p), {"2026-01": 1234.5})
            self.assertEqual(load_ledger(Path(tmp) / "missing.json"), {})


class TestMTD(unittest.TestCase):
    def test_no_scope(self):
        steps = mtd_checklist()
        self.assertEqual(len(steps), 1)
        self.assertIn("confirm", steps[0]["step"])

    def test_full_checklist(self):
        steps = mtd_checklist(self_employed=True)
        self.assertEqual(len(steps), 4)
        self.assertTrue(all("done" in s and "detail" in s for s in steps))
        self.assertIn("never this tool",
                      [s["detail"] for s in steps][-1])


class TestRecords(unittest.TestCase):
    def test_gap(self):
        r = records_gap("sole_trader", ["sales_invoices"])
        self.assertFalse(r["complete"])
        self.assertIn("cis_deduction_statements", r["missing"])

    def test_complete(self):
        r = records_gap("sole_trader", RECORD_TYPES["sole_trader"])
        self.assertTrue(r["complete"])

    def test_unknown_structure(self):
        self.assertIn("error", records_gap("partnership_x", []))


if __name__ == "__main__":
    unittest.main()
