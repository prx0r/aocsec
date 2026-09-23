# Extended dev plan — aocsec + estate

> Where this goes from here. Phases in order; each has an exit
> condition. Nothing starts without the previous phase's evidence.

## Phase 1 — First ten customers (now → +8 weeks)

Goal: real installs producing real outcome data. Everything built so
far is pre-customer; value starts at first paid onboarding.

- Run yes-flow per business (onboarding/). Target: 10 across ≥3 verticals.
- Each install fills: business graph, isolation checklist, e-manual,
  attestations, first maintenance run.
- Rulebook entries accumulate from real mistakes (other agent's surface).
- Exit: 10 verified installs, 10 e-manuals vaulted, first outcome data.

## Phase 2 — Harden from reality (+8 → +16 weeks)

Goal: replace assumptions with evidence from Phase 1.

- Red-team suite vs live Business Agent Test API per install.
- First real incident → run the response playbook → file findings.
- Review false-positive rates (invoice workflow friction, alert noise).
- Tune Jev floor (0.75) and triage keywords from actual outcomes.
- Exit: red-team green on live configs, incident report published,
  tuned thresholds committed.

## Phase 3 — Unblock keys and remotes (parallel, needs human)

Goal: activate dormant systems. Each needs a human decision, then
agent-executable work. Order by ROI:

1. Webhook URL → alerts notify someone (1 hour, unlocks monitoring).
2. Cloudflare Access → origins protected (30 min setup each).
3. Gateway deploy + tunnel → remote/Muse access real.
4. OpenRouter key handoff → Jev live triage at cents per call.
5. 5 powrobots API keys → supply-side data flows.
6. ONS URLs → only if a customer asks (low ROI, skip otherwise).
7. Muse directory submission → when 3+ installs verified.

## Phase 4 — Scale multi-client (+16 → +28 weeks)

Goal: marginal cost per customer approaches data entry.

- BISU credential model live (one partner credential, per-business scopes).
- Scheduler timers live (daily/weekly/monthly/quarterly jobs firing).
- Compliance calendar fed by live legislation + cert dates.
- Maintenance engine running unattended with human review of outputs.
- Calibration ladder replaces flat Jev floor (needs Phase 1–2 data).
- Exit: 50 businesses, same headcount, no missed SLAs.

## Phase 5 — POW convergence (when procurement is real)

Goal: connect trades demand to robot parts supply (goldmoat loop).

- Repair outcomes feed parts compatibility graph.
- Kit sales generate the transaction outcomes both sides need.
- Opportunity engine consumes powuk signals per trade area.
- Only starts when Phase 1 proves the install motion — not before.

## Non-goals (explicit)

- No custom checkout, card handling, or filing automation. Ever.
- No ONS archaeology without a paying customer asking.
- No second dashboard framework. Static HTML + JSON endpoints.
- No rewriting gardens. File findings in owning repos.

## How to track

- Threads: per-phase open items live here (findings/ for filed work).
- Proof: runs/ style timestamped logs for every phase exit claim.
- Review this plan quarterly. Delete what proved wrong.

---

## Addendum 2026-09-23 — promise review gate (amends Phase 1)

Sales promises now exist per vertical (PROMISES.md) and two of them
contradict the security architecture: auto-sent key/access instructions
and auto-send bookings vs draft-never-send. New rule: **no install
proceeds while its vertical's promises contradict the posture.**
The promises review (findings/2026-09-23-aionboard-promises-review.md)
is now a Phase 1 entry gate alongside eligibility. Either the promises
get reworded or the architecture gains explicitly scoped pre-approvals
— decided per item, on record, before customers.

## Addendum 2026-09-23 — WhatsApp-native operations (new Phase 2b)

Runs after Phase 1 starts producing installs, before scale:

- Per-install WhatsApp wiring: opt-in recorded, templates selected,
  24h-window behavior verified against staging, Business Agent scope
  set (eligibility + ToS + payment-scope record).
- Red-team via Agent Test API per install (free, unbilled, no users).
- First real incident exercises the response playbook end to end.
- Exit: 3 installs fully on WhatsApp rails with green staging runs.

## Addendum 2026-09-23 — maintenance goes live (amends Phase 4)

The maintenance engine (plans, runner, certified reports) is built and
tested. Activation sequence per business: subscription record →
scheduler timers → first monthly run → report vaulted → certificate
issued. Billing state tracks plan/current; charging stays with
Stripe/GoCardless. No new code expected — this is operations, not build.

## Addendum 2026-09-23 — findings backlog (all filed, owners pending)

- pow-site.service token (needs owner restart with fix).
- Webhook URL, 5 API keys, ONS URLs, Cloudflare Access, Jev key.
- aionboard promise contradictions (2 high, 3 medium — their call).
- Each item names its owner and unblock condition in findings/.
  Nothing here is "later" without a name and a trigger.
