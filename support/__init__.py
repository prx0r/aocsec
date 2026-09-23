"""Support backend — tickets, handoff, knowledge, manuals.

Boring by design. Tickets track human follow-ups (the desk itself can
be osTicket/GoHelpDesk/ITFlow — see docs/support-backend.md). What lives
here: the handoff protocol (bot→human with full context, never repeat),
SLA timers, a shared knowledge base both bot and humans answer from,
and the per-business e-manual generator.
"""

from .handoff import (
    HANDOFF_TRIGGERS,
    build_context_package,
    should_escalate,
)
from .kb import add_article, init_kb_tables, promote_resolution, record_use, search_articles
from .manual import build_systems_graph, generate_emanual
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
    "assign_ticket",
    "build_context_package",
    "build_systems_graph",
    "generate_emanual",
    "get_ticket",
    "init_kb_tables",
    "init_support_tables",
    "list_overdue",
    "open_ticket",
    "promote_resolution",
    "record_use",
    "resolve_ticket",
    "search_articles",
    "set_status",
    "should_escalate",
]
