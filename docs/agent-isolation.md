# Agent isolation — give Muse its own everything

> Core rule: the agent operates under a dedicated identity with bounded
> resources. A compromised or confused agent loses the sandbox, never
> the business. Status: pattern + checklists + red-team cover shipped.

## The principle

Never connect an agent to your personal accounts. Provision per-agent
identities instead:

| Resource | Yours (never connected) | Agent's (connected, bounded) |
|----------|------------------------|------------------------------|
| Email | personal inbox, 10 years of history | dedicated mailbox or alias (e.g. assistant@), sees only job mail |
| Wallet | main bank, real cards | prepaid/virtual card, low cap, no overdraft; per-transaction limits |
| Calendar | full diary, personal events | separate sub-calendar, work slots only |
| Contacts | full address book | job-scoped contacts only |
| CRM/software | owner login | scoped OAuth role, minimum permissions |

Maximum loss from a rogue, hijacked, or confused agent = whatever is
inside the sandbox. Size the sandbox so that number never hurts:
tens of pounds on the card, no personal data in the mailbox, no
standing permissions beyond the job at hand.

## Why this beats permission lists alone

Permissions say what the agent *should* touch. Isolation bounds what
it *can* lose. A prompt injection that escapes the approval flow still
hits: an empty-ish inbox, a capped card, a work-only calendar. Defense
in depth means the last layer is arithmetic (the cap), not language
(the prompt).

## Spending caps that make "don't risk spending" real

- Prepaid or single-use virtual card for anything agent-adjacent.
  Cap sized to one bad day, not one good month.
- No overdraft, no credit line, no linked savings on the agent instrument.
- Per-transaction notification to the owner (bank app alerts are free).
- Reconciliation weekly: every agent-touched pound accounted for in
  the books (feeds the FreeAgent flow, not a separate system).
- Refill manually, never automatically. Auto-top-up converts a bounded
  loss into an unbounded one.

## Email isolation specifics

- Dedicated mailbox or alias for agent-handled mail
  (e.g. jobs@ or assistant@). Owner's personal mail never in scope.
- Forwarding rules move job mail in; nothing personal flows out.
- If the mailbox is compromised: rotate its credentials, revoke its
  OAuth grants, check the cap card. Personal inbox untouched.
- Muse connector scoped to the agent mailbox only — never "all mail".

## Calendar isolation specifics

- Separate sub-calendar for agent-managed slots. Owner merges by eye.
- No visibility into personal/family events (the agent can't leak
  what it can't see, and injection can't exfiltrate it either).

## Onboarding checklist (per install)

- [ ] Dedicated agent mailbox created, owner inbox out of scope
- [ ] Capped spending instrument issued, limits verified in banking app
- [ ] No overdraft/credit on the agent instrument
- [ ] Transaction notifications on, owner phone confirmed receiving
- [ ] Work-only calendar created and shared (not the full diary)
- [ ] CRM role is minimum-permission, not owner/admin
- [ ] Revocation drill done once: owner can cut every access in <5 min
- [ ] Red-team identity-confusion suite green against this config

## Revocation (the other half of isolation)

Isolation only counts if you can sever it. Quarterly drill: revoke the
agent mailbox grant, freeze the spending card, remove the CRM role,
disconnect the Muse connector — then confirm the business still runs.
Record the drill date; stale drills are findings.
