# Payments hardening guide

> Rule: no payment credential ever touches our servers, Muse, or the
> agent loop. Verified options only — no custom checkout code.

## 1. The stack (use these, build nothing)

| Need | Use | Why |
|------|-----|-----|
| One-off setup fees (£499/£999) | **Stripe Payment Links** | No-code hosted page, SAQ A (~22 questions, ~1hr/year), 1.5% + 20p UK cards, 40+ methods, SCA/3DS2 handled by Stripe |
| Repeat/maintenance payments | **GoCardless** Direct Debit / Instant Bank Pay | 0.5% + 20p capped £4 — a £500 job costs £4.00 vs £7.70 on cards. Bank accounts don't expire (fewer failures). Recurring Pay by Bank scheme live June 2026 (UKPI). |
| Subscriptions (£79/mo advisory) | Stripe Billing **or** GoCardless | Cards for convenience, Direct Debit for margin — offer both |
| In-person (if ever) | Stripe Terminal via Lloyds Accept | Note: Terminal needs SAQ C, not A. Avoid unless required. |

Both providers FCA-regulated (Stripe UK 900461, GoCardless 597190).

## 2. Fee math that matters (verified 2026 pricing)

- £499 setup on UK card via Stripe: ~£7.69 fee.
- £500 job deposit via GoCardless DD: £2.70 capped math → £4.00 cap applies above ~£760; at £500 ≈ £2.70. Either way roughly half of cards.
- Failed-card admin (expiry, lost cards) disappears on bank payments — this is the hidden saving for repeat trade customers.

## 3. What we never build

- Custom card forms (would push us to SAQ A-EP: 200+ controls).
- Card number storage, bank credential storage, payment initiation.
- Anything that touches PAN. If card data reaches our server, the
  architecture has failed — treat as an incident, not a feature request.

## 4. Muse + money posture

- Connector manifest declares zero payment capabilities.
- Stripe is Muse's own payment facilitation layer (Link) — customer-side,
  on Stripe-hosted surfaces, never through our tools.
- If Meta ships transactional connectors: new submission, new review,
  new threat model. Until then, quotes are drafts and payments happen
  on provider-hosted pages the customer opens themselves.

## 5. Per-install checklist

- [ ] Business has Stripe OR GoCardless account (their account, their KYC)
- [ ] Payment Links created by the owner in their dashboard (we guide, we don't click)
- [ ] No card/bank fields in any form we built (grep the site)
- [ ] Reminders are text drafts, never auto-charge
- [ ] Refund path documented (dashboard refunds, owner-only)
