"""Jev triage — cheap judgments with confidence-gated escalation.

Jev (TypeSafe) is System One: triage, classify, first-pass. It never
decides anything consequential. Every judgment carries a confidence;
below threshold the item goes to human review, never to auto-action.

The `judge` callable is injected: production passes a JevMCP-backed
caller, tests pass stubs. No fake intelligence, no hardcoded verdicts.

Requires TYPESAFE_API_KEY (or OpenRouter key) at runtime for live calls.
Without it, every function raises — it will not guess.
"""

from .client import JevMCP, JevError, jev_available
from .triage import (
    CONFIDENCE_FLOOR,
    classify_alerts,
    gate_completion,
    verify_claims,
)

__all__ = [
    "CONFIDENCE_FLOOR",
    "JevMCP",
    "JevError",
    "classify_alerts",
    "gate_completion",
    "jev_available",
    "verify_claims",
]
