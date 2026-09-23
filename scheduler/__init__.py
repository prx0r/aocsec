"""Scheduler — what runs when, per business.

Jobs are due-lists, not cron daemons: the timer (systemd) calls
`due_jobs()` and executes what returns. Every job maps to a WhatsApp
template where the customer is involved, or a silent backend run where
they aren't. Nothing sends without the message builder's gates.
"""

from .calendar import compliance_calendar, due_items
from .jobs import JOB_DEFS, due_jobs, job_ids

__all__ = [
    "JOB_DEFS",
    "compliance_calendar",
    "due_items",
    "due_jobs",
    "job_ids",
]
