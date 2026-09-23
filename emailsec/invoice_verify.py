"""Supplier bank-detail verification workflow.

The money-losing attack in UK construction: "new bank details for your
invoice" from a compromised supplier inbox. Rule: NEVER act on emailed
bank details. Verify by phone on a previously known number, then record
the verification. No verification record = no payment change. Ever.
"""

from __future__ import annotations

from datetime import datetime, timezone


def verification_checklist(*, supplier: str, amount_gbp: float,
                           requested_channel: str) -> list[dict]:
    """Steps to clear before changing where money goes."""
    return [
        {"step": "ignore_email_details",
         "done": False,
         "detail": f"Do not use any bank details in the message about "
                   f"{supplier} (£{amount_gbp:,.2f} via {requested_channel}). "
                   f"Treat the message as hostile until verified."},
        {"step": "call_known_number",
         "done": False,
         "detail": "Call the supplier on a number you already hold "
                   "(saved contact, previous invoice, website typed by hand "
                   "— never a number from the suspicious message)."},
        {"step": "confirm_two_facts",
         "done": False,
         "detail": "Confirm TWO facts on the call: the new details AND a "
                   "recent genuine invoice number or job reference."},
        {"step": "record_verification",
         "done": False,
         "detail": "Record who confirmed, when, and on which number. "
                   "No record = no payment change."},
    ]


def assess_payment_change(*, verified_by_call: bool,
                          two_facts_confirmed: bool,
                          recorded: bool) -> dict:
    """Verdict on a proposed payment-detail change. Default: BLOCKED."""
    missing = []
    if not verified_by_call:
        missing.append("phone verification on known number")
    if not two_facts_confirmed:
        missing.append("two-fact confirmation")
    if not recorded:
        missing.append("written verification record")
    if missing:
        return {"decision": "BLOCKED",
                "checked_at": datetime.now(timezone.utc).isoformat(),
                "missing": missing,
                "action": "Do not pay to the new details. Complete: "
                          + "; ".join(missing) + "."}
    return {"decision": "CLEARED",
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "missing": [],
            "action": "Proceed. Keep the verification record 6 years "
                      "with the invoice."}
