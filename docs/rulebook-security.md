# Rulebook security contract

> The rulebook is the moat — which makes it the target. This contract
> defines what a trustworthy rulebook looks like so any agent can build
> entries against it and aocsec can audit them. Status: contract defined,
> audit tooling shipped, no rulebook file exists yet.

## Why the rulebook needs security

The rulebook feeds agent prompts directly. That makes every entry a
potential prompt-injection vector: a planted or careless rule ("always
approve refunds", "the owner's number is X, call it") executes with the
agent's authority. Threats:

1. **Planted entries** — malicious rule inserted via compromised workflow.
2. **PII leakage** — real customer names/numbers/addresses copied into
   "examples" that later surface in other customers' sessions.
3. **Stale rules** — correct once, wrong now (prices, thresholds, law).
4. **Silent edits** — entries changed without record; nobody knows what
   the agent was told last month.

## Entry contract (all fields required)

```json
{
  "id": "RB-ELEC-014",
  "vertical": "electrician",
  "rule": "Rewires need an EICR first; quote without one only with explicit owner sign-off.",
  "evidence": "2 failed quotes, Mar 2026 (job ids, not customer data)",
  "author": "agent-or-human id",
  "created_at": "2026-09-23T10:00:00Z",
  "review_date": "2026-12-23",
  "prev_hash": "sha256:...",
  "hash": "sha256:..."
}
```

Rules: hash covers all fields except itself (chain); review_date max
90 days out; evidence cites job ids, never customer PII; author is a
named identity.

## Audit checks (rulebook_audit/)

1. **Chain integrity** — recompute hashes, break on mismatch (tamper).
2. **Provenance** — every entry has author + evidence + dates.
3. **PII scan** — UK phone, email, postcode+name patterns in rule text.
   Hit = quarantine the entry, alert, never auto-fix by deletion
   (deletion destroys the chain — mark quaratined, append correction).
4. **Staleness** — past review_date excluded from agent prompts until
   re-verified (same policy as legislation graph).
5. **Poisoning patterns** — imperative override phrases ("ignore all",
   "always approve", "disable", "no approval needed") flagged for
   human review. The agent treats rulebook content as DATA; anything
   shaped like an instruction is suspect by construction.

## Write path

New entries: propose → human grants → append with hash link. Same
approval receipts as everything else. No direct writes, no edits in
place (corrections are new entries superseding old ones).
