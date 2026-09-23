"""MTD readiness + records checklists. Questions, not filings."""

from __future__ import annotations


def mtd_checklist(*, self_employed: bool = False, landlord: bool = False,
                  uses_compatible_software: bool = False,
                  income_band_known: bool = False) -> list[dict]:
    """Readiness steps. Every step is an owner action, nothing automatic."""
    if not (self_employed or landlord):
        return [{"step": "confirm_scope",
                 "done": False,
                 "detail": "MTD for Income Tax covers self-employment and "
                           "property income. Confirm which applies to you."}]
    steps = [
        {"step": "confirm_phase",
         "done": bool(income_band_known),
         "detail": "Confirm whether the current MTD phase covers your "
                   "income level (phases roll out by band — check "
                   "gov.uk for the current one)."},
        {"step": "compatible_software",
         "done": bool(uses_compatible_software),
         "detail": "Adopt HMRC-recognised compatible software before "
                   "your phase deadline."},
        {"step": "digital_records",
         "done": False,
         "detail": "Keep digital business records (income + expenses) "
                   "from the start of your first MTD period."},
        {"step": "quarterly_updates",
         "done": False,
         "detail": "File quarterly updates plus a final declaration. "
                   "Your software or accountant submits — never this tool."},
    ]
    return steps

