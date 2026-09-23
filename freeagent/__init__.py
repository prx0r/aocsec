"""FreeAgent integration — OAuth + read client + turnover bridge.

Customer authorizes in THEIR FreeAgent (their login, consent screen).
We hold scoped tokens, never passwords. Reads are free; invoice drafts
are gated (see approvals pattern); filing endpoints are never exposed.

Endpoint reference: dev.freeagent.com. Verify paths before first live use.
"""

from .client import FreeAgentClient, FreeAgentError
from .oauth import authorize_url, exchange_code
from .turnover import invoices_to_monthly

__all__ = [
    "FreeAgentClient",
    "FreeAgentError",
    "authorize_url",
    "exchange_code",
    "invoices_to_monthly",
]
