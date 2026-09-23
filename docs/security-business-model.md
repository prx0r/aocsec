# Security business model — bundled baseline, paid depth

> Answer: bundle the baseline into every onboarding (non-optional),
> sell depth as a service. Rationale, module mapping, and prices below.
> aionboard-side pricing updates are the product owner's call — this doc
> specifies what maps where.

## The split

**Bundled in every install (structure, not a service):**
Security presented as optional signals it's optional — it isn't. The
baseline rides along with work already being done:

| Module | Cost to deliver | Why bundled |
|--------|----------------|-------------|
| device + backup checklists | ~15 min during training | worthless without the install context |
| password + 2FA package | ~20 min, same session | highest ROI, must be universal |
| email auth checks (SPF/DKIM/DMARC) | minutes, scripted | proves the domain is really theirs |
| presence ownership review | ~10 min | hijack defense before it matters |
| approval gates + red-team first pass | automated | every install leaves tested, not just configured |
| isolation checklist | ~10 min | dedicated mailbox/card/calendar set up anyway |

Total marginal cost: roughly 45–60 minutes inside a 4–6 hour install.
That buys "every customer more secure than we found them" as a selling
point for onboarding itself — and it means our red-team and audit data
grow with every install (flywheel fuel).

**Paid service (depth, recurring):**

| Product | Price proposal | What |
|---------|---------------|------|
| Security report | £49 one-off | Digest-pinned findings + fixes + certificate. The peace-of-mind artifact. |
| Security care | £19–29/mo | Quarterly red-team re-run + domain re-checks + rulebook currency review. Alongside cloudflare_care. |
| Standalone audit | £149 one-off | Full suite for non-onboarded businesses (also a lead funnel into onboarding). |
| Incident response | quoted | Breach support. Rare, high-value, human-led. |

Prices are proposals to test, not validated willingness-to-pay. Anchor
against Cyber Essentials (£300+VAT cert) — we prepare evidence they'd
need, we don't compete with it.

## Liability bounding (why the split protects us)

- Bundled baseline has a written scope: what was checked, what wasn't.
  The report states both. Scope in writing bounds liability.
- Paid depth is explicitly point-in-time ("checked 2026-09-23"), never
  a guarantee. The report disclaimers already say this.
- We never warrant third parties (Google, Meta, banks, HMRC). Our
  warranty covers our work: gates configured, checks run, evidence kept.
- Customer's own actions after handover (new staff, disabled 2FA,
  approved-against-advice) are logged against their business record,
  not ours.

## Funnel logic

```
standalone audit (£149) → finds gaps → onboarding (£499/£20) → baseline free
                                                              → security care (£19-29/mo)
```

The audit is the cheapest trust-building sale: dated evidence, fixed
scope, no subscription. It converts to onboarding (fix what we found)
and to care (keep it fixed). Each stage funds the next.
