# What happens when they say yes — backend runbook

> The "yes" is the start, not the sale. This is the exact backend
> sequence per business, per vertical. Code: `onboarding/` package.

## The six gates (in order, each blocks the next)

```
contacted → interested → consent_recorded → eligible → isolated
→ installed → verified → maintenance
```

1. **Consent** — basis recorded (call, email reply, form, referral).
   Nothing install-shaped happens before this row exists.
2. **Eligibility** — Business Agent gate (vertical allowed, number
   eligible, Cloud API, good standing, single agent) + ToS acceptance
   recorded. Fail = stop, do not sell.
3. **Isolation** — 7 steps (dedicated mailbox, capped spending, no
   overdraft, txn notifications, work calendar, min CRM role,
   revocation drilled). All 7 or stop.
4. **Install** — vertical runbook: 5 universal baseline steps + trade
   extras (e.g. electrician: Part P check; cleaners: access-data rule;
   weddings: deposit workflow). Missing step = stop with the list.
5. **Verify** — red-team green + audit clean, as evidence, not claims.
6. **Maintenance** — plan selected (care/care_plus). First quarterly
   review scheduled.

`run_yes_flow()` executes this with human-supplied evidence and stops
at the first gap, naming it. Re-running after filling the gap resumes.

## Per vertical (runbook highlights)

| Vertical | Extra steps beyond baseline |
|----------|----------------------------|
| electrician | Part P registration check |
| beauty/hair/lashes/nails | Health-data rule (nothing clinical in prompts) |
| cleaners | Access-data rule (keys/codes), COSHH check |
| gardeners-window-cleaners | Waste carrier check |
| dog-groomers | Incident consent process |
| car-detailers | Before/after custody photos standard |
| driving-instructors | ADI check, safeguarding note |
| weddings | Deposit workflow (highest fraud exposure) |

Legislation topics + security focus per vertical ride along from the
same runbook (drives which obligations and red-team classes apply).

## After yes: follow-ups

- **14-day fixes window** from install date. Issues log against the
  install; afterwards they become support tickets.
- **Quarterly reviews**: red-team re-run, domain re-checks, stale-rule
  refresh. Overdue reviews surface, never nag automatically.
