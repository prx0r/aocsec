"""Legislation graph — structured regulatory data for chatbots and audits.

Unifies trade-law rules (aionboard regulations/registry.json) and a small
curated tax seed into obligation records with review dates, citations, and
owner actions. Powers tailored advice (match by vertical + topic), auditing
(stale-rule detection), and the MCP server for Muse.

Design rules:
- Every record carries source_url + review_date. No anonymous rules.
- Tax figures are pointers (check live source), never hardcoded rates.
  Rates change; the graph says WHERE to check and WHAT applies to whom.
- Past review_date = excluded from advice until re-verified.
"""

from .graph import (
    Obligation,
    build_graph,
    instruments,
    load_aionboard_registry,
    load_tax_seed,
    obligations_for,
    stale_rules,
)

__all__ = [
    "Obligation",
    "build_graph",
    "instruments",
    "load_aionboard_registry",
    "load_tax_seed",
    "obligations_for",
    "stale_rules",
]
