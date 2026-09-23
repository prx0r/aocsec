"""Free + paid security checks for trade businesses.

Free tier: customer-authorized checks against their own domain — HTTPS,
TLS expiry, security headers, reachability. Stdlib only, no scanning of
third parties, nothing the customer didn't ask us to look at.

Paid tier (report): same checks plus assistant red-team run
(aionboard.redteam) and a written report with severity + remediation.
Report content is evidence + advice, never a guarantee.

Both tiers record what was checked, when, and what was found — the
"peace of mind" artifact is the dated, digest-pinned report.
"""

from .checks import check_domain, free_check
from .report import build_report

__all__ = ["check_domain", "free_check", "build_report"]
