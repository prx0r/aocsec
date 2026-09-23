# Business Agent in the UK — what it can actually do today

> Researched September 2026 from Meta/WhatsApp official pages,
> TechCrunch, and developer docs. Things Meta announces move fast —
> re-verify before building on any single capability.

## Live now (global, incl. UK)

- AI answers customer questions in brand voice, 24/7, on WhatsApp
  (+ Messenger/Instagram). Free to start; paid tiers rolling out.
- Product recommendations from uploaded catalogs; lead qualification;
  appointment booking; sales closing (with per-install scope decisions).
- Human handoff built in — verify it's configured per install, not assumed.
- Learns from Facebook Page, past chats, website, uploaded catalogs.
- WhatsApp Business Discovery — customers can find agent-powered
  businesses by name inside WhatsApp.
- Developer platform: system-user + BISU tokens, Skills endpoint
  (X-API-Version 2.0.0), Eligibility endpoint, Agent Test API
  (free, unbilled), handoff events, WhatsApp Business Tools MCP
  (setup automation, beta).

## What this means per install

1. Eligibility check first (our gate) — never sell to an ineligible number.
2. Decide the payment scope in writing (handoff-only default).
3. Curate training sources (page + site + catalog only — no inboxes,
   no bank statements, no customer PII dumps).
4. Configure handoff + test it with something the agent can't do.
5. Invoice verification applies to anything it presents (bank details
   in chat get the same call-known-number treatment as email).
6. Track token/billing exposure once paid tiers land.

## What it doesn't do (yet)

- No evidence it files taxes, manages payroll, or handles compliance —
  our tax organizer + FreeAgent bridge cover that side.
- No public multi-tenant management beyond BISU — our per-business
  scoping model stands.
- Migration risk if Meta changes pricing/terms — our stack keeps all
  state (tickets, KB, manuals, audit) locally, so leaving is possible.
