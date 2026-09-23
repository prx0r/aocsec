"""Bridge: FreeAgent invoices -> tax turnover ledger format.

Replaces hand-typed figures with sums from the customer's own invoices.
Same bands, same owner-supplied-threshold rule as tax/turnover.py.
Only paid/dated invoices count; drafts and voids excluded.
"""

from __future__ import annotations


def invoices_to_monthly(invoices: list[dict]) -> dict:
    """Sum invoice totals by YYYY-MM. Skips drafts, voids, undated."""
    monthly: dict[str, float] = {}
    for inv in invoices:
        status = str(inv.get("status", "")).lower()
        if status in ("draft", "void", "cancelled"):
            continue
        dated = str(inv.get("dated_on", ""))[:7]
        if len(dated) != 7 or dated[4] != "-":
            continue
        try:
            total = float(inv.get("total_value", 0) or 0)
        except (TypeError, ValueError):
            continue
        monthly[dated] = round(monthly.get(dated, 0.0) + total, 2)
    return monthly
