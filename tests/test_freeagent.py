"""Tests for aocsec freeagent integration. Fully mocked — no network."""

import io
import json
import unittest
from unittest import mock

from freeagent import (
    FreeAgentClient,
    FreeAgentError,
    authorize_url,
    exchange_code,
    invoices_to_monthly,
)


def _resp(payload, status=200):
    m = mock.MagicMock()
    m.read.return_value = json.dumps(payload).encode()
    m.status = status
    return m


class TestOAuth(unittest.TestCase):
    def test_authorize_url(self):
        url = authorize_url("CID", "https://x.test/cb")
        self.assertIn("api.freeagent.com/v2/approve_app", url)
        self.assertIn("client_id=CID", url)
        self.assertNotIn("secret", url)

    def test_exchange_code(self):
        with mock.patch("urllib.request.urlopen") as uo:
            cm = mock.MagicMock()
            cm.__enter__.return_value = _resp({"access_token": "tok",
                                              "token_type": "bearer"})
            cm.__exit__.return_value = False
            uo.return_value = cm
            data = exchange_code("CID", "SEC", "CODE", "https://x.test/cb")
        self.assertEqual(data["access_token"], "tok")

    def test_exchange_failure(self):
        with mock.patch("urllib.request.urlopen") as uo:
            cm = mock.MagicMock()
            cm.__enter__.return_value = _resp({"error": "bad"})
            cm.__exit__.return_value = False
            uo.return_value = cm
            with self.assertRaises(ValueError):
                exchange_code("CID", "SEC", "CODE", "https://x.test/cb")


class TestClient(unittest.TestCase):
    def test_needs_token(self):
        with self.assertRaises(ValueError):
            FreeAgentClient("")

    def test_invoices(self):
        with mock.patch("urllib.request.urlopen") as uo:
            cm = mock.MagicMock()
            cm.__enter__.return_value = _resp(
                {"invoices": [{"dated_on": "2026-01-05",
                               "total_value": "500.00", "status": "paid"}]})
            cm.__exit__.return_value = False
            uo.return_value = cm
            invs = FreeAgentClient("tok").invoices()
        self.assertEqual(len(invs), 1)
        # auth header present, token not in URL
        sent_req = uo.call_args[0][0]
        self.assertIn("Bearer tok", sent_req.get_header("Authorization"))
        self.assertNotIn("tok", sent_req.full_url)

    def test_http_error_wrapped(self):
        import urllib.error
        with mock.patch("urllib.request.urlopen",
                        side_effect=urllib.error.HTTPError(
                            "u", 401, "x", {}, io.BytesIO(b""))):
            with self.assertRaises(FreeAgentError):
                FreeAgentClient("tok").invoices()

    def test_draft_never_sends(self):
        c = FreeAgentClient("tok")
        d = c.draft_invoice_payload(
            contact="Acme", dated_on="2026-02-01",
            items=[{"price": 100, "quantity": 2}])
        self.assertEqual(d["total"], 200.0)
        self.assertTrue(d["approval"]["required"])
        self.assertFalse(d["approval"]["sent"])
        self.assertFalse(hasattr(c, "send_invoice"))
        with self.assertRaises(ValueError):
            c.draft_invoice_payload(contact="x", dated_on="y", items=[])


class TestTurnoverBridge(unittest.TestCase):
    def test_sums_paid_only(self):
        invs = [
            {"dated_on": "2026-01-05", "total_value": "500.00", "status": "paid"},
            {"dated_on": "2026-01-20", "total_value": "250.00", "status": "sent"},
            {"dated_on": "2026-02-01", "total_value": "100.00", "status": "draft"},
            {"dated_on": "2026-02-02", "total_value": "50.00", "status": "void"},
            {"dated_on": "", "total_value": "999.00", "status": "paid"},
        ]
        self.assertEqual(invoices_to_monthly(invs),
                         {"2026-01": 750.0})

    def test_into_tax_ledger(self):
        from tax.turnover import rolling_12m, threshold_status
        monthly = invoices_to_monthly([
            {"dated_on": f"2026-{m:02d}-01", "total_value": "1000",
             "status": "paid"} for m in range(1, 7)])
        monthly.update({f"2026-{m:02d}-15": 500.0 for m in range(1, 6)})
        total = rolling_12m(monthly)
        self.assertEqual(total, 8500.0)
        self.assertEqual(threshold_status(total, 10000)["band"], "watch")


if __name__ == "__main__":
    unittest.main()
