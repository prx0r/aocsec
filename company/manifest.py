"""Capability manifests — every capability declares its contract.

Stolen from agentcom company_graph processor packs: requires, provides,
cost, authority, prohibitions, failure modes. A capability that can't
state its prohibitions doesn't ship.
"""

from __future__ import annotations

CAPABILITIES: dict[str, dict] = {
    "company.lookup": {
        "requires": ["query.company_number"],
        "provides": ["company.profile"],
        "cost": {"money": 0, "tokens": 0, "wall_seconds": 5,
                 "external_calls": 1, "human_seconds": 0},
        "authority_required": False,
        "prohibitions": ["bulk_download", "officer_pii_export",
                         "self_validate"],
        "failure_modes": ["NOT_FOUND", "RATE_LIMITED", "NO_KEY"],
    },
    "company.search": {
        "requires": ["query.company_name"],
        "provides": ["company.candidates"],
        "cost": {"money": 0, "tokens": 0, "wall_seconds": 5,
                 "external_calls": 1, "human_seconds": 0},
        "authority_required": False,
        "prohibitions": ["bulk_download", "self_validate"],
        "failure_modes": ["NO_RESULT", "RATE_LIMITED", "NO_KEY"],
    },
}


def get_capability(name: str) -> dict:
    """Capability contract. Unknown names rejected (no silent default)."""
    if name not in CAPABILITIES:
        raise ValueError(f"unknown capability: {name}. "
                         f"Known: {sorted(CAPABILITIES)}")
    return {"name": name, **CAPABILITIES[name]}
