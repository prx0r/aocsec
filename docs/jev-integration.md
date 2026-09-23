# Jev integration — cheap judgments inside hard gates

> Jev (TypeSafe) is System One: triage, classify, first-pass. It never
> decides anything consequential. Status: module built + tested, live
> calls blocked on an API key (see setup).

## Setup (human, 5 min)

1. Key at console.typesafe.ai/settings/keys (or OpenRouter account).
2. `export TYPESAFE_API_KEY=...` (or `OPENROUTER_API_KEY=...`).
3. Flip the `jev` entry in opencode.jsonc to `"enabled": true`.
4. Never paste the key into chat. Never commit it.

opencode.jsonc entry (present but disabled until keyed):

```json
"jev": {
  "type": "local",
  "command": ["npx", "-y", "@jkudish/jev-mcp"],
  "enabled": false,
  "timeout": 30000
}
```

Requires Node 20+. Alternative: typesafe-mcp `evaluate` CLI
(`curl -fsSL .../install.sh | sh`, same key).

## Tool mapping (what we use it for)

| jev-mcp tool | Our use | Gate |
|---|---|---|
| `jev_classify` | Alert/incident triage (act_now/watch/noise) | confidence ≥ 0.75 or human review |
| `jev_verify` | Check report claims against cited evidence | low confidence → needs_human, never pass |
| `jev_gate` | Completion claims (diff + test evidence → ship/no-ship) | default no-ship; anything uncertain blocks |
| `jev_screen` | Screen fetched pages before context (supplier docs, ONS pages) | skip-on-doubt, never trust-on-doubt |
| `jev_review` | Score diffs pre-merge (multi-agent branches) | advisory; human merges |
| `jev_rerank` / `jev_find` | Order threads, findings, opportunities by relevance | presentation only |

## Confidence policy

- Floor 0.75 (`CONFIDENCE_FLOOR` in triage.py). Below → human.
- Judge errors → human. Missing confidence → 0.0 → human.
- Every accepted judgment recorded with its confidence (audit trail).
- These gates wrap Jev; they don't replace approval receipts,
  red-team, or chain verification for consequential actions.

## Cost logic

Jev at fractions of a cent per call means: judge everything cheap,
escalate what matters. Alert triage every 15 min, context sieving on
every monitoring run, review scoring on every diff — all affordable.
Frontier models and humans handle only what clears the floor upward
(i.e. consequential). Spending flows toward certainty, not volume.
