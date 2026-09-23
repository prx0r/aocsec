"""Monthly maintenance engine — one subscription, everything checked.

Plans bundle security reports, tech-support readiness evidence, and
custom-tooling inputs into a single monthly run per customer. Lead
generation and bespoke dev stay product-side (aionboard); this engine
produces the evidence those conversations run on.
"""

from .plans import PLANS, plan_for
from .report import build_monthly_report
from .runner import run_monthly

__all__ = ["PLANS", "build_monthly_report", "plan_for", "run_monthly"]
