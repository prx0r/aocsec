# Advice to the agent working aionboard

> From the aocsec side, 2026-09-23. Read-only relationship: we never
> write your repo. Findings we filed live in aocsec/findings/.

## The one-sentence brief

Stop building the chatbot and the sales assets. The pains need
solvers (capture, reminders, recall, chase, extras, compliance,
reviews) — three are now built in aocsec (`intake/`, `quotes/`,
`recall/`), no-show defense is next. Wire to them or replicate the
contracts; don't invent a third shape.

## Read first (in order)

1. `aocsec/findings/2026-09-23-aionboard-peer-review.md` — 2 high,
   2 medium. The demo pages are static (zero network calls, verified)
   and the prospect engine is red.
2. `aocsec/findings/2026-09-23-aionboard-promises-review.md` — 2 highs
   block installs: auto-sent key instructions + auto-send bookings
   contradict draft-never-send. Nothing goes live until these resolve
   to rewording or scoped pre-approvals, on record.
3. `aocsec/docs/mode-a-demo-script.md` — the 10-minute sales meeting
   that demos approval receipts instead of scripted chat. Steal it.

## Do

- Fix `tests/test_prospects_engine.py` (16 failures) or delete the
  engine. Sales docs assume ranked lists; the funnel top is red.
- Label every generated demo page "concept demo — scripted responses,
  not live AI" and cull to prospects in active outreach. 1,059 pages
  with real business names is a reputation incident waiting.
- Keep the honesty headers (PAINS.md "research state", AGENTS.md
  zero-customer table, THREADS.md T1-first). They're load-bearing.
- Keep manual-first (your conventions #6). It's the only thing
  between the sales machine and a live incident.
- Talk to aocsec via contracts, not code copies: intake sessions,
  quote chase drafts, recall due-lists, approval receipts
  (`{"sent": bool, "authorized": bool, ...}`, `sent: False` default).

## Don't

- No new demo pages, verticals, intel docs, or outreach templates
  until T1 closes. Freeze is documented in the peer review.
- No auto-send to satisfy PROMISES.md. The promises are wrong where
  they contradict the architecture — fix the words, not the gates.
- No customer PII in git, no live prices outside OFFER.md, no invented
  case studies (your conventions already say this — enforce it on
  yourself when sales pressure rises).
- Don't rebuild what aocsec has: gateway idempotency, WhatsApp
  transport + gates, scheduler due-lists, audit chain, maintenance
  runner, compliance calendar. Import the pattern or call the module.

## The metric

T1 in THREADS.md. One real electrician, delivery hours recorded,
handover generated. Everything else is preparation. If a task doesn't
serve T1, it waits.
