# Review: aionboard PROMISES.md vs security posture — 2026-09-23

> Read-only review of aionboard promises/demos/outreach. No edits made
> there. Each item: the promise, the conflict, the fix. Severity from
> a customer-harm perspective.

## High

### 1. "Key access instructions sent automatically" (cleaners promise)
Sending alarm codes / key locations without a human in the loop means
one misrouted message hands building access to a stranger. Our
access-data rule (keys/codes never in prompts/tickets) must extend to
automated sends: access instructions require explicit per-message
owner approval, verified recipient, and an audit entry. Recommend
removing "automatically" or scoping to owner-composed templates only.

### 2. Auto-send booking confirmations / waitlist fills / cancellations
Several verticals promise confirmations, rebooking, and reminders
"sent automatically". Our architecture says drafts + human grants.
Either the promises overstate (fix wording to "drafted for your
approval") or the architecture needs per-template pre-approvals with
logged scope. Decide explicitly — silent auto-send is the one outcome
both docs must agree to forbid.

## Medium

### 3. Deposit collection via Stripe link (nails + tech notes)
Mechanism aligns (provider-hosted page, SAQ A). Gaps: who creates the
link (must be owner in Stripe dashboard), what happens on failed
payment (dunning path?), and refund handling (human-in-Stripe only).
Promise wording "deposits collected" implies agency — reword to
"deposit links sent for your approval" or document the approved flow.

### 4. Invoice reminders at fixed schedules
Text reminders are safe; the <7-day payment metric implies follow-
through the agent can't guarantee. Keep reminders as drafts + owner
send, and measure honestly (response rate, not payment time).

### 5. 1,059 generated demos with real business data
Demos use real names/services/prices. Verify: no phone numbers, emails,
or non-public data in generated demo content; demo links unguessable;
demo data retention policy stated. (Not audited — flagged for review.)

## Aligned (no action)

- Free trial framing (no payment, walk away) matches low-pressure ethics.
- Outcome promises with before/after measurement match our evidence rules.
- Meta Business Agent as live channel matches our posture docs.
- Outreach templates + TPS screening match contact rules.
- Dashboard spec: cross-check against our gateway scopes when built.
