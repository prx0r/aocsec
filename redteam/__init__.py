"""Adversarial testing for per-target assistants.

Pattern imported from aisec/worlds/voiceagent (attack → grade → digest-pinned
evidence JSONL). Adapted: the target is a trade-business assistant, so the
attack classes cover customer PII, quote fraud, owner impersonation, and
approval bypass — the threats that actually apply to aionboard installs.

The runner takes any `respond(message, session_id)` callable: a live model
backend, the OpenAI SDK path, or a test double. Grading is keyword evidence
(honest limits — catches regressions and gaping holes, not clever jailbreaks).
"""

from .attacks import ATTACKS, ATTACK_CLASSES
from .grade import digest, grade
from .runner import run_suite

__all__ = ["ATTACKS", "ATTACK_CLASSES", "digest", "grade", "run_suite"]
