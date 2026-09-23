"""Company lookup — verify a business exists and what it is.

Pattern stolen from agentcom company_graph processor: declared costs,
explicit prohibitions, no self-validation. Uses Companies House API
(key from env, never code). Read-only: profile + officers count only.
No filings, no charges detail, no bulk download.
"""

from .companies_house import (
    CompanyNotFound,
    lookup_company,
    search_companies,
)
from .manifest import CAPABILITIES

__all__ = [
    "CAPABILITIES",
    "CompanyNotFound",
    "lookup_company",
    "search_companies",
]
