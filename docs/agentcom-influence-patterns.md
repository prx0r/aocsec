# agentcom + influence patterns worth stealing

> Reviewed agentcom v0.5–v0.7 family + influence repo. Verdict per
> pattern: stolen (built), tracked (noted), skipped (wrong domain).
> Nothing vendored — patterns reimplemented in our style, our tests.

## Stolen and built

**Capability manifests with cost + prohibitions** (agentcom company_graph
processor packs) → `company/manifest.py`. Every capability declares
requires/provides/cost/authority/prohibitions/failure-modes. Unknown
names rejected. A capability that can't state its prohibitions doesn't
ship — now enforced in code, not just docs.

**Company lookup with PII minimization** (company_graph lookup idea) →
`company/companies_house.py`. Verified live: GES Electrons Ltd, active,
SIC 43210, Manchester. Officer identities reduced to a boolean flag.
This is exactly the prospect verification aionboard's VISION.md calls
for ("verify its current trading status").

**Two-chain evidence** (influence: private raw + public commitments) →
already our posture (shapes-not-values logs + digest-pinned reports);
influence's formulation sharpened the docs. No code change needed.

**Actuality discipline** (influence: TRUE/FALSE/UNKNOWN, attempt
evidence never settles claims, nonce roundtrips) → already our redteam
and runs/ proof-log practice. Adopted vocabulary in reviews.

**Human-task-centered operations** (influence dashboard: task carries
class/consequence/options/recommendation/cost-of-wait) → matches our
support tickets + handoff packages. Validated direction, no change.

## Tracked, not built

**qp judge kernel** (tiny deterministic replay of claim+evidence) →
elegant, but our approval receipts + redteam cover the same ground
today. Revisit if disputes need formal replay.

**Calibration ladder** (Brier/ECE per decision family, shadow→auto) →
strictly better than our flat 0.75 Jev floor. Blocked on data: needs
months of judged outcomes first. The floor stands until then.

**Dependency-graph spine** (influence Project/passport/Reconcile) →
right shape for multi-garden orchestration, but that's powops/powk
territory, not aocsec. Noted for them.

## Skipped

**Full agentcom processor packs / module system** — heavyweight
ontology (processors, Seed0 lanes, Harbor export) for autonomous
economic discovery. Wrong domain for trade onboarding security.
Take the patterns (manifests, prohibitions, evidence discipline),
leave the framework.

**influence paraders/leaderboards** — reputation mechanics for
influencer runs. No mapping to our problem.
