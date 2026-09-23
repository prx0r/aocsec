# Per-vertical security profiles

> What each trade needs secured beyond the generic baseline. Legislation
> coverage comes from the graph (`legislation/coverage_report`); this doc
> adds the threat notes no statute states plainly.

## electrician
- Best-covered vertical (5 specific rules + general). Part P, EV, solar.
- Threat notes: high-value jobs (£1k+) make quote fraud lucrative;
  EV-charger installs involve DNO notifications (paperwork to verify).
- Red-team focus: quote_fraud, approval_bypass.

## beauty / hair / lashes / nails
- Covered via beauty/barber rules (patch tests, chemicals). No
  hair/lash/nail-specific rules — noted as acceptable (shared regime).
- Threat notes: allergy/patch-test records are HEALTH DATA — highest
  PII sensitivity in the estate. Before/after photos need explicit
  consent per image, not blanket. Colour chemical incidents are the
  liability event.
- Red-team focus: pii_leakage (health records, photos).

## cleaners
- Thin coverage (1 rule). Real sensitivity is operational: keys, alarm
  codes, access routines to empty properties.
- Threat notes: alarm codes and key logs must never enter prompts,
  tickets, or audit logs (shapes only). Staff turnover = access review.
- Red-team focus: pii_leakage (access details), cross_session.

## gardeners-window-cleaners
- Window work partially covered; gardening via waste-carrier seed.
- Pesticide use flagged as gap (no rule asserted — needs research).
- Threat notes: equipment theft from vans/yards (operational, not ours
  to solve); green-waste paperwork for commercial clearances.

## dog-groomers
- Covered (petcare/vet rules). Animal welfare handling standards.
- Threat notes: pet injury incidents are the liability event; consent
  forms for handling + photo use.

## car-detailers
- Registry gap. COSHH seed covers chemicals/solvents.
- Threat notes: high-value vehicles in custody (key control, damage
  documentation before/after). Water runoff/environmental awareness.

## driving-instructors
- Registry gap. ADI seed covers licensing.
- Threat notes: lone working with 17-year-olds — safeguarding awareness,
  dashcam/consent considerations. Dual-control safety.

## weddings
- Low-regulation vertical, stated honestly. No law asserted.
- Threat notes: large deposits = payment-fraud target (fake supplier
  invoices, deposit scams). Supplier verification matters more than
  any statute here. GoCardless/Stripe guidance applies doubly.

## Cross-vertical rules for onboarding agents
1. Never assert a rule the graph doesn't return with a citation.
2. Gaps are stated ("no specific rules found for X"), not filled.
3. Health-data verticals (beauty/hair/lashes/nails) get the strictest
   prompt hygiene: no names, no photos, no conditions in prompts.
4. Key/alarm-code verticals (cleaners) get access-data hygiene: codes
   live in the customer's lockbox, never in tickets or prompts.
