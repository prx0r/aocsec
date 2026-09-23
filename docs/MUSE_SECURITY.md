# Muse channel + payments security design

> Everything customer-facing runs through Muse's security posture.
> Everything money-shaped runs through tokenized, approval-bound flows.
> Status: design + building blocks. Muse UK availability unconfirmed.

## 1. Why Muse is the channel

Trades customers already live in WhatsApp. Muse operates there (US today),
with multistep tasks across authorized apps: email, calendar, shopping,
payments. For aionboard that means one interface for enquiries, quotes,
bookings, and reports — no new app to learn.

Constraints (do not design around them, design within them):
- UK launch date unconfirmed. The service works without Muse (web dashboard,
  email) and gets better with it.
- Amazon blocked Muse purchases over disputed access practices. Never rely
  on an agent browsing arbitrary sites to buy things. Use direct,
  authorized supplier integrations only.
- Connector review gates what businesses can publish. Submission is not
  approval; build to the review criteria (functional, security, legal).

## 2. What Muse can and cannot do here

| Can (with customer authorization) | Cannot (by design) |
|---|---|
| Read enquiry inbox, draft replies | Send anything without approval receipt |
| Draft quotes from the approved price book | Invent prices or discounts |
| Check diary, propose slots | Book/change/cancel without approval |
| Summarize regulations with citations | Give legal advice; always cite + escalate |
| Surface nearby opportunities | Contact anyone (needs approval + TPS check) |
| Report security-check findings | Run checks against domains not authorized |

Every row in the right column is enforced by code (approvals.py), not by
prompt wording. The redteam suite (`aionboard/redteam`) probes exactly
these boundaries: approval bypass, owner impersonation, PII fishing,
quote fraud, booking manipulation.

## 3. Payments: never touch money

The rule, stated as architecture:

1. **Tokenization, not storage (Stripe pattern).** Card entry happens in
   Stripe-hosted fields or payment links. The PAN travels customer →
   Stripe directly, never through our servers. We hold tokens, references,
   last-4, amounts, statuses. Token-only systems qualify for SAQ A, not
   SAQ D. A full breach yields nothing spendable.
2. **Scoped mandates, not permissions.** Every approval binds customer +
   exact action + payload hash + expiry (see assistant/approvals.py).
   Cannot be reused, retargeted, transferred, or replayed. This mirrors
   the industry direction (shared payment tokens, signed mandates).
3. **Audit that can't become a second breach.** security.py redact_args
   logs shapes + SHA-256, never values. Denials log louder than successes.
4. **Blast-radius controls.** RateLimiter per-client per-tool. Tiers:
   auto-approve reads → log queries → approve writes → block destructive.
5. **No code path from AI to payment.** The assistant proposes (draft +
   approval receipt). A human grants. A separate, narrow executor —
   outside the agent loop — redeems scoped mandates. The agent can never
   reach across that boundary no matter what the prompt says.

The pitch, honestly stated: our systems are built so there is no code
path from AI to your money, and no card data to steal. Verify it: the
red-team suite includes quote-fraud and approval-bypass attacks, and the
paid security report re-runs them against your installation.

## 4. What to build, in order

1. `assistant/` approvals on every write path (done — approvals.py).
2. Red-team suite green against the assistant responder (done — redteam/).
3. Free domain checks + paid reports (done — security_audit/).
4. Muse connector submission when UK-eligible (connector/ exists).
5. Shop Pay / Stripe tokenized checkout for kits/parts (needs POW
   procurement API — goldmoat2; not started).
6. Continuous re-testing: red-team runs on a schedule, evidence kept.

## 5. What we will not do

- Hold card numbers, bank credentials, or payment initiation capability.
- Auto-send quotes, bookings, or messages. Ever.
- Claim PCI certification we don't hold. SAQ A posture is documented,
  not certified, until assessed.
- Promise Muse features (checkout, placements) Meta hasn't shipped in the UK.
