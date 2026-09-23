"""Self-hashing certificates for reports, approvals, and decisions.

Adapted from proofdesk foxit/src/audit (MIT). A certificate includes
its own content hash: anyone can recompute it and detect alteration.
Used for paid security reports and approval grants — the "peace of
mind" artifact with teeth.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any


def _hash_object(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"),
                   default=str).encode()).hexdigest()


@dataclass
class Certificate:
    """Tamper-evident certificate. Hash covers everything but itself."""

    cert_type: str  # approval | report | resolution | extraction
    subject: str
    evidence: list[dict] = field(default_factory=list)  # hash refs
    issuer: str = "aocsec"
    metadata: dict = field(default_factory=dict)
    issued_at: float = field(default_factory=time.time)
    certificate_hash: str = ""

    def compute_hash(self) -> str:
        data = {
            "cert_type": self.cert_type,
            "subject": self.subject,
            "evidence": self.evidence,
            "issuer": self.issuer,
            "metadata": self.metadata,
            "issued_at": self.issued_at,
        }
        return _hash_object(data)

    def seal(self) -> "Certificate":
        """Compute and attach the hash. Returns self for chaining."""
        self.certificate_hash = self.compute_hash()
        return self

    def verify(self) -> bool:
        """True when content matches the attached hash."""
        return bool(self.certificate_hash) and \
            self.certificate_hash == self.compute_hash()

    def to_dict(self) -> dict:
        return {
            "cert_type": self.cert_type,
            "subject": self.subject,
            "evidence": self.evidence,
            "issuer": self.issuer,
            "metadata": self.metadata,
            "issued_at": self.issued_at,
            "certificate_hash": self.certificate_hash,
        }
