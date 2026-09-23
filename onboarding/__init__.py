"""Outreach-to-customer pipeline — what happens when they say yes.

Stages: contacted -> interested -> consent_recorded -> eligible ->
isolated -> installed -> verified -> maintenance. Each transition is
gated: missing prerequisites rejected, never skipped. The pipeline
itself never touches customer systems — it records that humans did.

Per-vertical runbooks (runbooks.py) derive install steps from what we
know: legislation obligations + security checklists for that trade.
"""

from .pipeline import (
    STAGES,
    advance,
    pipeline_status,
    record_consent,
    record_evidence,
    register_prospect,
)
from .followups import fixes_due, followups_for, review_due
from .runbooks import runbook_for
from .yesflow import run_yes_flow

__all__ = [
    "STAGES",
    "advance",
    "fixes_due",
    "followups_for",
    "pipeline_status",
    "record_consent",
    "record_evidence",
    "register_prospect",
    "review_due",
    "run_yes_flow",
    "runbook_for",
]
