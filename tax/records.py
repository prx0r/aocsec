"""Required record types per structure. Gap reports, not storage."""

from __future__ import annotations

RECORD_TYPES: dict[str, list[str]] = {
    "sole_trader": [
        "sales_invoices", "purchase_receipts", "bank_statements",
        "cis_deduction_statements", "mileage_log", "vat_records_if_registered",
    ],
    "limited_company": [
        "sales_invoices", "purchase_receipts", "bank_statements",
        "payroll_records", "dividend_vouchers", "board_minutes",
        "vat_records_if_registered", "corporation_tax_workings",
    ],
    "landlord": [
        "rental_income_log", "expense_receipts", "tenancy_agreements",
        "deposit_protection_refs", "safety_certificates",
    ],
}


def records_gap(structure: str, present: list[str]) -> dict:
    """Which required record types are missing for a structure."""
    required = RECORD_TYPES.get(structure)
    if required is None:
        return {"error": f"unknown structure: {structure}. "
                         f"Known: {sorted(RECORD_TYPES)}"}
    have = set(present)
    missing = [r for r in required if r not in have]
    return {"structure": structure, "required": required,
            "present": sorted(have), "missing": missing,
            "complete": not missing,
            "action": ("Records complete. Keep 6 years."
                       if not missing else
                       f"Missing {len(missing)} record types: "
                       f"{', '.join(missing)}. Gather before year-end.")}
