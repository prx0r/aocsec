"""Read client for FreeAgent Company API. Reads + draft prep only.

Exposed as methods (not MCP tools yet — tools get added at the gateway
with approval tiers). Filing endpoints (VAT returns, Self Assessment
submit, MTD submit) are deliberately absent: there is no method for
them, so no tool can ever wrap them.
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request

BASE = "https://api.freeagent.com/v2"


class FreeAgentError(Exception):
    pass


class FreeAgentClient:
    """Authenticated read client. Token supplied by caller (600 store)."""

    def __init__(self, access_token: str, timeout: int = 30):
        if not access_token:
            raise ValueError("access_token is required")
        self._token = access_token
        self._timeout = timeout

    def _get(self, path: str, params: dict | None = None) -> dict:
        url = BASE + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(
            url, method="GET",
            headers={"Authorization": f"Bearer {self._token}",
                     "Accept": "application/json",
                     "User-Agent": "aocsec-freeagent/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            raise FreeAgentError(f"GET {path}: HTTP {e.code}") from e
        except urllib.error.URLError as e:
            raise FreeAgentError(f"GET {path}: {e.reason}") from e

    def invoices(self, **params) -> list[dict]:
        """Sales invoices (read). Key fields: dated_on, total_value, status."""
        return self._get("/invoices", params or None).get("invoices", [])

    def expenses(self, **params) -> list[dict]:
        """Expense claims (read)."""
        return self._get("/expenses", params or None).get("expenses", [])

    def bank_transactions(self, bank_account_id: str, **params) -> list[dict]:
        """Bank transactions for one account (read)."""
        return self._get(f"/bank_accounts/{bank_account_id}/bank_transactions",
                         params or None).get("bank_transactions", [])

    def draft_invoice_payload(self, *, contact: str, items: list[dict],
                              dated_on: str, reference: str = "") -> dict:
        """Build (not send) an invoice payload for owner review.

        Returns the payload + an approval receipt shape. Sending happens
        in FreeAgent's UI by the owner, never here — there is no send
        method on this client.
        """
        if not items:
            raise ValueError("invoice needs at least one item")
        total = round(sum(float(i.get("price", 0)) * int(i.get("quantity", 1))
                          for i in items), 2)
        return {
            "payload": {"invoice": {
                "contact": contact, "dated_on": dated_on,
                "reference": reference, "invoice_items": items}},
            "total": total,
            "approval": {"required": True, "sent": False,
                         "note": "Owner sends in FreeAgent. Never auto-send."},
        }
