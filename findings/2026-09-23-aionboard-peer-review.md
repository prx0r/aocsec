# Peer review: aionboard (read-only, 2026-09-23)

> Scope: full-tree review from aocsec. No aionboard files touched.
> Evidence commands cited inline; reproduce from `/home/ubuntu/aionboard`.

## Verdict

Strong trust architecture, honest internal docs, real unit-tested
libraries — wrapped in a sales apparatus that currently sells things
that do not exist. The single most valuable asset (the approval-gated
assistant design) has never served a real user; the single most
numerous asset (1,059 demo pages) demonstrates nothing that runs.

## What's real (credit where due)

- **Security architecture** (`SECURITY_ARCHITECTURE.md`, `security.py`,
  `assistant/approvals.py`): money never touches the system, scoped
  one-time mandates, human grants every consequential action. Genuinely
  good design, unit-tested.
- **Internal honesty**: `AGENTS.md` "State of the world" table admits
  zero paying customers, no live integrations, hypothetical economics.
  `THREADS.md` puts T1 (first real install) on the critical path. The
  repo knows what's unproven. Don't lose this as sales pressure grows.
- **Working libraries**: CRM, installs state machine, onboarding
  registry, handover generator (rejects secrets), encrypted backups
  with restore verify, booking-link verifier — tested with fixtures.

## Finding 1 (high): 1,059 demo pages demonstrate nothing live

- Evidence: `find demos/generated -name "*.html" | wc -l` → 1059;
  `grep -c -i -E "fetch|websocket|api\." <any page>` → 0. Every page
  answers via `generateResponse()` keyword-matching an embedded blob.
- A prospect clicking their own business name sees a chatbot that
  cannot fail because it cannot do anything. The moment they ask an
  unscripted question ("can you move my Thursday booking?"), the
  illusion breaks — in front of the customer, during the sales meeting.
- Worse: pages carry real business names. If a prospect Googles
  themselves and finds our demo page ranking or circulating, that's a
  reputation incident wearing our branding.
- Recommendation: cap the generated set to prospects actually in
  outreach (dozens, not thousands); label every page "concept demo —
  scripted responses, not live AI" in the footer; delete the rest.
  The engine's `sample_questions` + keyword responses are a liability
  at scale, not an asset.

## Finding 2 (high): lead generation is failing, not untested

- Evidence: `python3 -m pytest tests/ -q` → 16 failed, all in
  `tests/test_prospects_engine.py` (loading, scoring, density,
  export, summary). The funnel top is red while `SALES_PLAYBOOK.md`
  and outreach templates assume ranked prospect lists exist.
- Recommendation: fix or delete. A broken engine that sales docs
  depend on will produce either manual workarounds nobody records or
  fabricated lists. Either poisons the CRM data T1 needs to be clean.

## Finding 3 (medium): designed-but-absent infrastructure is presented as roadmap, not gap

- Evidence (their own table): MCP contracts "designed, no server
  running"; Muse connector "draft, not submitted"; every pipeline
  step `manual`; gateway library "not deployed as a gateway".
- The docs are honest internally, but PROMISES.md + outreach
  templates sell outcomes (auto-send bookings, key instructions —
  see promises review 2026-09-23) that require exactly this missing
  infrastructure. The gap between promise and mechanism is where
  incidents will live.
- Recommendation: tag every sales claim with its required
  infrastructure state; block outreach using claims whose mechanism
  is `manual` or absent.

## Finding 4 (medium): T1 still OPEN is the only metric

- Everything economic — pricing, automation priority, support
  staffing, the £20 thesis — depends on delivery hours from one real
  install. `THREADS.md` says this plainly. No amount of demo pages,
  intel docs, or TikTok scripts substitutes for it.
- Recommendation: freeze new sales-asset generation until T1 closes.
  Every hour spent on demos past the current set is an hour not
  spent calling Manchester.

## What to keep doing

- Findings-style honesty in AGENTS.md/THREADS.md. Extend it to the
  demo footers and the promises doc.
- Manual-first discipline (`conventions` #6). It's the only thing
  standing between the sales apparatus and a live incident.
- Approval-receipt contracts (`sent: False` default). The core
  differentiator — demo THAT, not a scripted chat.

## Repro

```bash
cd /home/ubuntu/aionboard
find demos/generated -name "*.html" | wc -l
grep -c -i -E "fetch|websocket|api\." demos/generated/electrician/*.html | head -3
python3 -m pytest tests/ -q 2>&1 | tail -2
```
