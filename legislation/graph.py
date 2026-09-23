"""Obligation graph: nodes, edges, queries. Stdlib only."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

TAX_SEED = Path(__file__).parent / "tax_seed.json"


@dataclass
class Obligation:
    """One actionable regulatory requirement."""

    id: str
    law: str
    requirement: str
    applies_to: list[str] = field(default_factory=list)  # verticals/industries
    jurisdiction: str = "UK"
    domain: str = ""  # employment, tax, safety, data, ...
    citation: str = ""
    source_url: str = ""
    owner_action: str = ""
    escalation: str = ""
    failure_mode: str = ""
    review_date: str = ""
    basis: str = ""  # verified-2026, pointer-live-source, ...

    def is_stale(self, today: str | None = None) -> bool:
        today = today or date.today().isoformat()
        return not self.review_date or self.review_date < today

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "law": self.law,
            "requirement": self.requirement,
            "applies_to": self.applies_to,
            "jurisdiction": self.jurisdiction,
            "domain": self.domain,
            "citation": self.citation,
            "source_url": self.source_url,
            "owner_action": self.owner_action,
            "escalation": self.escalation,
            "failure_mode": self.failure_mode,
            "review_date": self.review_date,
            "basis": self.basis,
        }


def _from_registry_rule(rule: dict) -> Obligation:
    return Obligation(
        id=str(rule.get("id", "")),
        law=str(rule.get("law", "")),
        requirement=str(rule.get("detail", "")),
        applies_to=list(rule.get("industries", [])),
        jurisdiction=str(rule.get("jurisdiction", "UK")),
        domain=str(rule.get("domain", "")),
        citation=str(rule.get("citation", "")),
        source_url=str(rule.get("source_url", "")),
        owner_action=str(rule.get("owner_action", "")),
        escalation=str(rule.get("escalation", "")),
        failure_mode=str(rule.get("failure_mode", "")),
        review_date=str(rule.get("review_date", "")),
        basis=str(rule.get("basis", "")),
    )


def load_aionboard_registry(path: str | Path | None = None) -> list[Obligation]:
    """Load trade-law rules. Default: aionboard repo registry."""
    if path is None:
        path = Path("/home/ubuntu/aionboard/regulations/registry.json")
    with open(path) as f:
        rules = json.load(f).get("rules", [])
    return [_from_registry_rule(r) for r in rules if r.get("id")]


def load_tax_seed(path: str | Path = TAX_SEED) -> list[Obligation]:
    """Load curated tax pointers. Figures live at sources, not here."""
    with open(path) as f:
        return [_from_registry_rule(r) for r in json.load(f).get("rules", [])]


def build_graph(
    registry_path: str | Path | None = None,
    tax_seed_path: str | Path = TAX_SEED,
) -> list[Obligation]:
    """All obligations from all sources. Dedupe by id (first wins).

    Records without id or source_url are dropped — anonymous rules
    cannot be cited, so they cannot be advised on.
    """
    seen: dict[str, Obligation] = {}
    for ob in load_aionboard_registry(registry_path) + load_tax_seed(tax_seed_path):
        if ob.id and ob.source_url and ob.id not in seen:
            seen[ob.id] = ob
    return list(seen.values())


def obligations_for(
    obligations: list[Obligation],
    vertical: str = "",
    topic: str = "",
    domain: str = "",
    include_stale: bool = False,
) -> list[Obligation]:
    """Tailored advice set: filter by vertical/topic/domain, drop stale."""
    vertical = vertical.lower()
    topic = topic.lower()
    domain = domain.lower()
    out = []
    for ob in obligations:
        if vertical and vertical not in [a.lower() for a in ob.applies_to]:
            # empty applies_to = general business rule, include it
            if ob.applies_to:
                continue
        if domain and ob.domain.lower() != domain:
            continue
        if topic:
            hay = f"{ob.law} {ob.requirement}".lower()
            if topic not in hay:
                continue
        if ob.is_stale() and not include_stale:
            continue
        out.append(ob)
    return out


def stale_rules(obligations: list[Obligation]) -> list[Obligation]:
    """Rules past review_date — the audit queue."""
    return [ob for ob in obligations if ob.is_stale()]


def instruments(obligations: list[Obligation]) -> list[dict]:
    """Distinct laws with obligation counts (graph overview)."""
    agg: dict[str, dict] = {}
    for ob in obligations:
        key = ob.law or "unknown"
        agg.setdefault(key, {"law": key, "obligations": 0, "stale": 0})
        agg[key]["obligations"] += 1
        if ob.is_stale():
            agg[key]["stale"] += 1
    return sorted(agg.values(), key=lambda d: d["law"])
