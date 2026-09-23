"""Tests for company lookup + capability manifests. Fully mocked."""

import unittest
from unittest import mock

from company import (
    CAPABILITIES,
    CompanyNotFound,
    lookup_company,
    search_companies,
)

import os as _os
_os.environ.setdefault("COMPANIES_HOUSE_API_KEY", "test-key")
from company.manifest import get_capability


def _urlopen_factory(payload):
    import io
    import json
    cm = mock.MagicMock()
    m = mock.MagicMock()
    m.read.return_value = json.dumps(payload).encode()
    cm.__enter__.return_value = m
    cm.__exit__.return_value = False
    return cm


class TestManifest(unittest.TestCase):
    def test_known(self):
        c = get_capability("company.lookup")
        self.assertIn("prohibitions", c)
        self.assertIn("self_validate", c["prohibitions"])
        self.assertIn("cost", c)

    def test_unknown_rejected(self):
        with self.assertRaises(ValueError):
            get_capability("company.delete-everything")


class TestLookup(unittest.TestCase):
    PROFILE = {
        "company_number": "16658292", "company_name": "GES ELECTRONS LTD",
        "company_status": "active", "type": "ltd",
        "date_of_creation": "2025-08-18", "sic_codes": ["43210"],
        "registered_office_address": {"locality": "Manchester"},
        "links": {"officers": "/company/16658292/officers"},
    }

    def test_profile_shape(self):
        with mock.patch("urllib.request.urlopen",
                        return_value=_urlopen_factory(self.PROFILE)):
            r = lookup_company("16658292")
        self.assertEqual(r["status"], "active")
        self.assertEqual(r["sic_codes"], ["43210"])
        self.assertTrue(r["has_officers"])
        # officer identities reduced to a flag, never names/URLs
        self.assertNotIn("/company/16658292/officers", str(r))

    def test_number_normalized(self):
        with mock.patch("urllib.request.urlopen",
                        return_value=_urlopen_factory(self.PROFILE)):
            r = lookup_company(" 16658-292 ")
        self.assertEqual(r["company_number"], "16658292")

    def test_empty_number(self):
        with self.assertRaises(ValueError):
            lookup_company("   ")

    def test_404_maps(self):
        import urllib.error
        with mock.patch("urllib.request.urlopen",
                        side_effect=urllib.error.HTTPError(
                            "u", 404, "x", {}, __import__("io").BytesIO(b""))):
            with self.assertRaises(CompanyNotFound):
                lookup_company("00000000")

    def test_no_key_refuses(self):
        with mock.patch.dict("os.environ", {}, clear=False):
            import os
            env = {k: v for k, v in os.environ.items()
                   if k != "COMPANIES_HOUSE_API_KEY"}
            with mock.patch("os.environ", env):
                with self.assertRaises(Exception):
                    lookup_company("16658292")

    def test_search(self):
        payload = {"items": [
            {"company_number": "1", "title": "A Ltd",
             "company_status": "active", "company_type": "ltd",
             "address": {"locality": "Leeds"}}]}
        with mock.patch("urllib.request.urlopen",
                        return_value=_urlopen_factory(payload)):
            res = search_companies("A Ltd")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["address"], "Leeds")

    def test_empty_query(self):
        with self.assertRaises(ValueError):
            search_companies("  ")


if __name__ == "__main__":
    unittest.main()
