"""Verification without seeing sensitive documents.

Principle: check public registers, record attestations, never collect
the document. For every qualification there is an order of preference:

1. Public register lookup (no document changes hands at all).
2. Customer attestation + registration number (numbers are business
   credentials shown to customers, not secrets — safe to record).
3. Redacted document review (customer redacts first, guided).
4. Never: full unredacted IDs, certificates with personal data,
   bank statements, or anything a register could have answered.

Gas Safe's bot protection (403 to scripts) proves the point: some
registers REQUIRE human eyes. The module records outcomes; humans
perform lookups. That division is structural, not temporary.
"""

from .methods import (
    VERIFICATION_METHODS,
    method_for,
)
from .attest import (
    init_verify_tables,
    list_attestations,
    record_attestation,
)

__all__ = [
    "VERIFICATION_METHODS",
    "init_verify_tables",
    "list_attestations",
    "method_for",
    "record_attestation",
]
