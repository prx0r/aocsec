# Agent harness evaluation: unreal-agent vs pi

> Cloned and reviewed 2026-09-23 (unreallabsai/unreal-agent, MIT, 1.6k
> stars, active). Verdict: don't replace pi. Steal four patterns.

## What it is

Async-first Go harness for durable agent runs: session-scoped
idempotent inbox, append-only session store with forks, tool
translators (sync validation, no I/O on the loop), actor operation
manager, serializable versioned operations, Harbor benchmarks.
Well-designed infrastructure code.

## Why not instead of pi

Different jobs. Pi (opencode + our MCP servers) is an interactive
ops/coding agent that reads dashboards, queries data, and proposes
actions. Unreal-agent is a library for *building* durable agent
runtimes — it has no monitoring data, no domain tools, no approval
model, no chatbot, no customer context. Replacing pi with it means
rebuilding everything pi already does, in Go, to gain durability we
only need in one place (long workflows).

Also: no native MCP client found (only incidental mentions). Our 30+
MCP tools would need a bridge written from scratch.

## What to steal (in priority order)

1. **Idempotent inbox** — duplicate webhook/timer deliveries deduped by
   caller-supplied ID. Our scheduler + gateway have no dedup; a retried
   delivery double-fires today. Small to add, real robustness win.
2. **Serializable operations** — durable, recoverable long runs. Needed
   exactly once: multi-day procurement/manufacturing workflows
   (goldmoat). Everywhere else YAGNI.
3. **Session forks** — branch a conversation to explore without losing
   the trunk. Maps to handoff investigation paths (try a resolution
   privately, keep the customer thread clean).
4. **Harbor-style evals** — benchmark harness for agent runs. Our
   redteam suite covers adversarial behavior; Harbor-style task
   benchmarks would cover competence. Adopt the pattern when the
   assistant fleet grows past hand-checking.

## Decision

Track the repo (it's active and good). Steal idempotency first — it's
a day's work with immediate payoff for scheduler + gateway reliability.
Revisit the rest when a long-running workflow actually exists.
