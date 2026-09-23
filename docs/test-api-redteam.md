# Agent Test API as red-team target

> Meta's Test API runs messages through the full agent pipeline
> synchronously with no WhatsApp user involved and unbilled tokens.
> That makes it the ideal red-team surface: attack staging free,
> production untouched.

## Protocol

1. Configure the staging agent exactly like production (same knowledge,
   same skills, same audience rules).
2. Run every redteam/ attack class through Test API calls.
3. Grade with the same keyword evidence + human review of borderlines.
4. Ship to production ONLY on full hold. Any breach → fix → re-run.
5. Re-run on: skill changes, knowledge updates, Meta platform updates,
   quarterly at minimum.

## Why this beats testing in production

- Zero customer exposure during testing.
- Zero token billing for test traffic.
- No WhatsApp user needed on the other end.
- Deterministic replay: same message set every run, diffable results.

## Evidence chain

Each run: attack set version + timestamp + per-attack verdicts +
digests, stored alongside other red-team evidence. Production
enablement requires the latest green run on record — "tested last
month" is not current.
