"""Vertical map — the 11 aionboard trades vs legislation coverage.

Each vertical lists the registry industries that cover it. Gaps (no
specific rules) are explicit, not hidden — they drive the seed file and
the audit queue.
"""

from __future__ import annotations

VERTICALS: dict[str, dict] = {
    "electrician": {
        "registry_industries": ["electrician"],
        "notes": "Best covered. Part P, EV, solar overlap with POW parts work.",
    },
    "beauty": {
        "registry_industries": ["beauty", "medspa"],
        "notes": "Patch-test and chemical rules; medspa overlap for advanced treatments.",
    },
    "hair": {
        "registry_industries": ["beauty", "barber"],
        "notes": "Covered via beauty/barber rules. No hair-specific rules in registry.",
    },
    "lashes": {
        "registry_industries": ["beauty"],
        "notes": "Covered via beauty rules (patch tests, adhesives). No lash-specific rules.",
    },
    "nails": {
        "registry_industries": ["beauty"],
        "notes": "Covered via beauty rules. No nail-specific rules.",
    },
    "cleaners": {
        "registry_industries": ["cleaning"],
        "notes": "Thin: 1 rule. Key-holding/alarm codes are the real sensitivity (see vertical-security).",
    },
    "gardeners-window-cleaners": {
        "registry_industries": ["window_cleaner", "tree_surgeon"],
        "notes": "Window work partially covered; gardening covered by waste-carrier seed. Pesticide use flagged as gap.",
    },
    "dog-groomers": {
        "registry_industries": ["petcare", "vet"],
        "notes": "Covered. Animal handling + welfare rules apply.",
    },
    "car-detailers": {
        "registry_industries": [],
        "notes": "Gap: no registry rules. Covered by COSHH seed (chemicals) only.",
    },
    "driving-instructors": {
        "registry_industries": [],
        "notes": "Gap: no registry rules. Covered by ADI seed. Young pupils (17+) raise safeguarding awareness (no DBS rule asserted).",
    },
    "weddings": {
        "registry_industries": [],
        "notes": "Gap: low-regulation vertical. Deposits/consumer contracts flagged as commercial sensitivity, not asserted as law.",
    },
}


def _alias_map() -> dict[str, list[str]]:
    """vertical -> equivalent registry industry names (lowercased)."""
    return {
        v: [i.lower() for i in meta["registry_industries"]]
        for v, meta in VERTICALS.items()
    }


def obligations_for_vertical(vertical: str, obligations: list,
                             **kwargs) -> list:
    """obligations_for with vertical alias expansion."""
    from .graph import obligations_for
    return obligations_for(obligations, vertical=vertical,
                           aliases=_alias_map(), **kwargs)


def coverage_report(obligations: list) -> dict:
    """Per-vertical counts from actual advice output.

    specific = obligations matched for the vertical (registry + seed);
    general = empty-applies_to rules applying to all businesses.
    gap = no native registry industries (structural flag — seed may
    still cover advice, see specific count).
    """
    from .graph import obligations_for

    report = {}
    for vertical, meta in VERTICALS.items():
        matched = obligations_for(obligations, vertical=vertical)
        specific = sum(1 for o in matched if o.applies_to)
        general = sum(1 for o in matched if not o.applies_to)
        report[vertical] = {
            "specific": specific,
            "general": general,
            "total": len(matched),
            "gap": not meta["registry_industries"],
        }
    return report
