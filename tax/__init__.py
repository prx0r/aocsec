"""Safe tax organizer — local arithmetic on user-entered figures.

Hard boundaries (non-negotiable):
- NO filing, NO payments, NO bank credentials, NO HMRC login.
- Thresholds are USER-SUPPLIED (checked at gov.uk by the owner).
  This module never hardcodes a rate or threshold.
- All data stays in local files the owner controls.
- Output is organization + warnings + next steps, never tax advice.
  Every result points at the relevant legislation record and says
  "ask an accountant" where judgment is required.

What it does:
- turnover: rolling 12-month taxable turnover from monthly figures the
  owner enters; distance-to-threshold bands against THEIR threshold.
- mtd: Making Tax Digital readiness checklist from business profile.
- records: required record types per structure, gap report.
"""

from .turnover import (
    add_month,
    load_ledger,
    rolling_12m,
    save_ledger,
    threshold_status,
)
from .mtd import mtd_checklist
from .records import RECORD_TYPES, records_gap

__all__ = [
    "add_month",
    "load_ledger",
    "rolling_12m",
    "save_ledger",
    "threshold_status",
    "mtd_checklist",
    "RECORD_TYPES",
    "records_gap",
]
