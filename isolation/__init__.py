"""Agent isolation checklists — dedicated identity per agent.

Verifies the sandbox exists before the agent gets authority: separate
mailbox, capped spending instrument, work-only calendar, minimum CRM
role, and a practiced revocation path. Mirrors the devicecheck/presence
state pattern.
"""

from .isolation import (
    STEPS,
    isolation_status,
    mark_done,
    max_loss_estimate,
    onboarding_checklist,
)

__all__ = [
    "STEPS",
    "isolation_status",
    "mark_done",
    "max_loss_estimate",
    "onboarding_checklist",
]
