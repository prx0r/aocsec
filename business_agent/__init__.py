"""Meta Business Agent onboarding helpers.

Pure logic around the documented Platform flow: eligibility gating,
ToS acceptance records, the 24-hour messaging window, and handoff
verification. No API calls here — credentials and HTTP live with the
integrator. These functions decide WHAT must be true, not how Meta's
API responds.
"""

from .onboarding import (
    EXCLUDED_VERTICALS,
    eligibility_checklist,
    record_tos_acceptance,
)
from .window import in_freeform_window, window_status

__all__ = [
    "EXCLUDED_VERTICALS",
    "eligibility_checklist",
    "in_freeform_window",
    "record_tos_acceptance",
    "window_status",
]
