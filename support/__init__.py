"""Support backend — tickets, handoff, knowledge, manuals.

Boring by design. Tickets track human follow-ups (the desk itself can
be osTicket/GoHelpDesk/ITFlow — see docs/support-backend.md). What lives
here: the handoff protocol (bot→human with full context, never repeat),
SLA timers, a shared knowledge base both bot and humans answer from,
and the per-business e-manual generator.
"""

from .agent import run_support_round, sla_watch, triage_ticket
from .business import (
    add_contact,
    add_qualification,
    add_system,
    get_business,
    init_business_tables,
    list_businesses,
    upsert_business,
)
from .handoff import (
    HANDOFF_TRIGGERS,
    build_context_package,
    should_escalate,
)
from .kb import add_article, init_kb_tables, promote_resolution, record_use, search_articles
from .manual import build_systems_graph, generate_emanual, manual_for_business
from .tickets import (
    SLA_TARGETS,
    assign_ticket,
    get_ticket,
    init_support_tables,
    list_overdue,
    open_ticket,
    resolve_ticket,
    set_status,
)

__all__ = [
    "HANDOFF_TRIGGERS",
    "SLA_TARGETS",
    "add_article",
    "add_contact",
    "add_qualification",
    "add_system",
    "assign_ticket",
    "build_context_package",
    "build_systems_graph",
    "generate_emanual",
    "get_business",
    "get_ticket",
    "init_business_tables",
    "init_kb_tables",
    "init_support_tables",
    "list_businesses",
    "list_overdue",
    "manual_for_business",
    "open_ticket",
    "promote_resolution",
    "record_use",
    "resolve_ticket",
    "run_support_round",
    "search_articles",
    "set_status",
    "should_escalate",
    "sla_watch",
    "triage_ticket",
    "upsert_business",
]
