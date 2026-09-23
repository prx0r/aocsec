# Agent-managed tech support

> The agent runs the queue; humans own outcomes. Every round produces
> proposals, drafts, and flags — nothing is sent, resolved, or
> reprioritized without a human grant.

## The loop (`support/agent.py`)

Per business, per round (`run_support_round`):

1. **Triage new tickets** — Jev classify when available (0.75 floor),
   keyword tiers otherwise. Output: priority proposal + KB draft hints.
2. **Draft first responses** — from shared KB articles, never composed
   from scratch. Drafts, not sends.
3. **SLA watch** — overdue tickets get draft nudges (marked DRAFT).
4. **Escalation check** — policy topics, loops, explicit asks compile a
   handoff package with the business graph attached (systems +
   qualifications travel with the ticket).

Idempotent: re-running with no changes produces no new actions.

## The business graph (one record per customer)

`support/business.py` persists profile + systems + contacts +
qualifications per business_id. Tickets, handoff, KB scoping, manual,
and maintenance all join here — the "whole company on our graph"
substrate. E-manuals render straight from it (`manual_for_business`).

## What the agent cannot do (structural)

- Send replies, quotes, or nudges (no send methods exist).
- Resolve tickets (requires human + written resolution).
- Change priorities (proposals only).
- File, pay, or touch credentials (no code paths, per structure scan).

## Human surface

- Morning queue: `run_support_round` output per business.
- Overdue: `sla_watch` at any time.
- Handoff: context package with transcript tail + business graph.
- Evidence: every ticket transition lands in the chained audit log.
