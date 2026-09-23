"""Onboarding gates for Meta Business Agent installs.

Order matters: eligibility FIRST (never sell to an ineligible number),
then ToS acceptance (recorded with date), then configuration. Each gate
returns pass/fail with the exact next action.
"""

from __future__ import annotations

from datetime import datetime, timezone

# Per Meta docs: agent unavailable in these verticals.
EXCLUDED_VERTICALS = (
    "finance", "government", "health", "alcohol", "gambling",
    "otc_drugs", "matrimony",
)


def eligibility_checklist(*, vertical: str, country_eligible: bool,
                          cloud_api: bool, good_standing: bool,
                          single_agent: bool) -> dict:
    """Gate a number before selling anything. All five must pass.

    country_eligible, cloud_api, good_standing, single_agent come from
    the Meta Eligibility endpoint / WhatsApp Manager — this function
    judges the answers, it does not fetch them.
    """
    checks = [
        ("vertical_allowed",
         vertical.lower() not in EXCLUDED_VERTICALS,
         "Vertical excluded by Meta — do not proceed." if vertical.lower()
         in EXCLUDED_VERTICALS else ""),
        ("country_eligible", bool(country_eligible),
         "Business country not authorized — check Eligibility endpoint."),
        ("cloud_api", bool(cloud_api),
         "Number must use Cloud API (not the WhatsApp Business app)."),
        ("good_standing", bool(good_standing),
         "Account restricted or banned — resolve first."),
        ("single_agent", bool(single_agent),
         "Number already runs a conflicting messaging product."),
    ]
    failed = [{"check": name, "action": action}
              for name, ok, action in checks if not ok]
    return {"eligible": not failed, "failed": failed,
            "action": ("Proceed to ToS acceptance." if not failed else
                       "STOP. Resolve failures before selling anything.")}


def record_tos_acceptance(*, business_id: str, accepted_by: str,
                          at: str | None = None) -> dict:
    """Record ToS acceptance. The API requires it before any call."""
    if not business_id.strip() or not accepted_by.strip():
        raise ValueError("business_id and accepted_by are required")
    return {
        "business_id": business_id.strip(),
        "accepted_by": accepted_by.strip(),
        "at": at or datetime.now(timezone.utc).isoformat(),
        "note": "Meta Business Agent Terms accepted in WhatsApp Manager. "
                "API calls require this first.",
    }
