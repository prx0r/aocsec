# Meta Business Agent posture — live globally since June 2026

> The channel changed under us: Muse is US-only and future; Business
> Agent is live globally NOW (1M+ businesses), free to start, in
> WhatsApp/Messenger/Instagram. This doc sets our posture toward it.
> Verified against Meta/WhatsApp announcements + TechCrunch, Sept 2026.

## What it does that changes our threat model

1. **It closes sales and processes payments** (Meta's words: "complete
   the payment, process the booking, place the order"). Money moves
   inside Meta's agent, not through our approval receipts. Our
   draft-never-send posture covers OUR tools only — a Business Agent
   sale happens outside our gates entirely.
2. **It learns from past chats, website, and catalog.** Training data
   ingestion with business-controlled scope; same memory-persistence
   dynamics as Muse (assume retained until proven otherwise).
3. **Native human handoff exists.** Good — aligns with our handoff
   protocol. Verify per install that handoff is configured, not assumed.
4. **Agent Platform for enterprise** with governance controls; plus a
   WhatsApp Business Tools MCP (Sept 2026) letting coding agents manage
   WhatsApp Business setup. Supply-chain surface: review what that MCP
   can touch before any agent uses it.
5. **Paid tiers coming** (token-metered for large businesses). Cost
   exposure is a new budget line to track per install.

## Posture per install

- [ ] Business Agent enabled deliberately, not by default. Record why.
- [ ] Payment/booking capabilities: confirm what the agent is allowed
      to complete vs hand off. Default: hand off money movement to the
      human (our invoice-verification workflow still applies to any
      bank-detail content, whoever presents it).
- [ ] Handoff configured and tested (ask it something it can't do,
      confirm a human gets full context).
- [ ] Training sources reviewed: past chats + site + catalog only.
      No personal inboxes, no bank statements, no customer PII dumps
      as training material.
- [ ] Memories/disconnect behavior demonstrated (same drill as Muse).
- [ ] Token/cost exposure checked (paid tiers, per-token billing).

## Relationship to our stack

| Layer | Owner |
|-------|-------|
| Agent behavior inside Meta's app | Meta (reviewed, their guardrails) |
| What the agent is allowed to touch | Us (this checklist, per install) |
| Money movement | Provider pages + human approval; Business Agent sales need explicit scope decision per install |
| Red-team cover | Our suite (email_indirect + invoice_fraud classes apply directly — the inbox IS WhatsApp here) |
| Audit trail | Our chained log for our actions; Meta-side history via their dashboard (note retention limits) |

## What we will not do

- Pretend our approval receipts govern Meta-native sales. They don't.
  Say so in every install where Business Agent handles money.
- Feed customer PII into training sources to "personalize" faster.
- Recommend the agent for payment collection without the invoice-
  verification workflow in place first.
