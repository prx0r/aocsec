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
    gate_install,
    record_tos_acceptance,
)
from .payment_scope import SCOPES, record_payment_scope, widen_scope
from .window import in_freeform_window, window_status

__all__ = [
    "EXCLUDED_VERTICALS",
    "eligibility_checklist",
    "gate_install",
    "in_freeform_window",
    "record_payment_scope",
    "record_tos_acceptance",
    "window_status",
]
