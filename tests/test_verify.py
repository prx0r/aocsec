"""Tests for verify module (methods + attestations). No network."""

import sqlite3
import unittest

from verify import (
    VERIFICATION_METHODS,
    init_verify_tables,
    list_attestations,
    method_for,
    record_attestation,
)


def _db():
    conn = sqlite3.connect(":memory:")
    init_verify_tables(conn)
    return conn


class TestMethods(unittest.TestCase):
    def test_known_qualifications(self):
        for q in ["gas_safe", "niceic", "trustmark", "adi",
                  "companies_house", "waste_carrier", "insurance"]:
            m = method_for(q)
            self.assertIn(m["method"], ("human_lookup", "api", "attestation"))
            if m["method"] != "attestation":
                self.assertTrue(m["url"].startswith("https://"), q)

    def test_unknown_safe_default(self):
        m = method_for("underwater_basket_weaving")
        self.assertIn("No known public register", m["register"])
        self.assertNotIn("http", m["url"])

    def test_gas_safe_is_human(self):
        # bot-blocked registers must never be marked automated
        self.assertEqual(method_for("gas_safe")["method"], "human_lookup")


class TestAttestations(unittest.TestCase):
    def test_lifecycle(self):
        conn = _db()
        r = record_attestation(conn, business_id="b1",
                               qualification="gas_safe", verdict="verified",
                               reference="GS-123456", verified_by="amy")
        self.assertEqual(r["verdict"], "verified")
        rows = list_attestations(conn, "b1")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["reference"], "GS-123456")
        conn.close()

    def test_bad_verdict(self):
        with self.assertRaises(ValueError):
            record_attestation(_db(), business_id="b", qualification="q",
                               verdict="probably", verified_by="amy")

    def test_anonymous_verifier_rejected(self):
        with self.assertRaises(ValueError):
            record_attestation(_db(), business_id="b", qualification="q",
                               verdict="verified", verified_by="  ")

    def test_empty_business(self):
        with self.assertRaises(ValueError):
            record_attestation(_db(), business_id="  ", qualification="q",
                               verdict="verified", verified_by="amy")


if __name__ == "__main__":
    unittest.main()
