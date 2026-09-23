# Vertical capability matrix — what we can do per trade today

> Generated from live code, not claims. Legislation counts from
> `coverage_report()`; finances and security are universal modules
> applied per vertical. Opportunities depend on aionboard+powuk
> (external — noted, not duplicated).

## Answer first

**Finances: yes, all 11.** Turnover tracking, threshold bands, MTD
readiness, and records gaps are structure-based (sole trader / ltd /
landlord), not trade-based. A cleaner and an electrician use the same
code paths with different figures.

**Security: yes, all 11.** 12 red-team classes + domain checks + paid
reports are trade-agnostic; per-vertical threat notes
(docs/vertical-security.md) tune which classes matter most.

**Legislation: varies.** 0–7 specific rules + 3 general rules each:

| Vertical | Specific | General | Finance | Security | Notes |
|----------|----------|---------|---------|----------|-------|
| electrician | 7 | 3 | full | full | best covered; EV/solar overlap |
| beauty | 4 | 3 | full | full + health-data rules | patch-test sensitivity |
| hair | 3 | 3 | full | full + health-data rules | via beauty/barber aliases |
| lashes | 3 | 3 | full | full + health-data rules | via beauty aliases |
| nails | 3 | 3 | full | full + health-data rules | via beauty aliases |
| cleaners | 2 | 3 | full | full + access-data rules | key/alarm-code hygiene |
| gardeners-window-cleaners | 4 | 3 | full | full | + waste-carrier seed |
| dog-groomers | 4 | 3 | full | full | petcare/vet rules |
| car-detailers | 1 | 3 | full | full | COSHH seed only |
| driving-instructors | 1 | 3 | full | full | ADI seed only |
| weddings | 0 | 3 | full | full | honest gap; fraud notes instead |

## What "full finances" means per vertical

1. Turnover ledger (600-perm) + rolling 12m vs owner-supplied threshold.
2. MTD readiness checklist (self-employed/landlord paths).
3. Records gap report (sole/ltd/landlord structures).
4. FreeAgent bridge when they connect their account (OAuth, reads only).
5. CIS specifics for construction-adjacent trades (electrician, plumber
   pattern) via LEG-UK-CIS-SUB.

## What "full security" means per vertical

1. Red-team suite (12 classes) runnable against their assistant config.
2. Free domain checks + paid digest-pinned reports.
3. Approval receipts on every consequential action.
4. Vertical threat notes applied (health-data vs access-data hygiene).

## External dependencies (not ours, noted)

- Opportunities feed: aionboard matcher + powuk signals. Works live
  (verified: 5 planning matches for M14 electrician). We consume
  nothing; aionboard reads powuk files directly.
- Filing/submission: FreeAgent UI by owner; HMRC by owner/accountant.
- Payments: Stripe Links / GoCardless, owner accounts.

## Scope proof (2026-09-23)

`git status` across all other repos: only pre-existing local outputs
(powstock/powrobots/repair untracked data dirs from their own
collectors). One exception: uncommitted powproducts fixes
(BaseCollector init, hashlib import) from before the scope rule —
left in place, pending owner review/commit. No writes outside aocsec
since the rule took effect.
