# Meta Business Agent architecture (imported)

> Sources: developers.facebook.com (Platform overview, get-started,
> quickstart), whatsappbusiness.com (product pages), TechCrunch
> 2026-06-03, Parallel AI MCP notes. Verified September 2026.
> This is a research import, not Meta documentation — verify against
> the live docs before building on any endpoint.

## How it fits together

```
Customer WhatsApp user
        ↓ messages
Meta Business Agent (primary responder)
   ├── answers from business knowledge (FAQs, site, catalog, files)
   ├── acts via connected APIs + webhooks (booking, payment confirmation)
   ├── hands off to YOUR APP when needed (handoff events)
   └── your app still receives every user message + copies of agent replies
        ↓ standby participant
Your backend (our stack: approvals, audit, KB, tickets)
```

Key: enabling the agent does NOT disconnect your systems. Your app
stays in the loop receiving everything — which is where our audit
trail, approval gates, and red-team coverage attach.

## Auth model (what matters for multi-client management)

- Direct integrators: **system user token** (one business, own WABA).
- Partners managing clients: **BISU token** (Business Integration System
  User) — act on behalf of multiple client WABAs under one credential.
  This is the correct model for managing many trades businesses.
- Required permissions: `whatsapp_business_messaging` (+ `..._management`
  for setup). Missing either = 401.
- Every Platform API call needs `X-API-Version: 2.0.0` header (v1 lacks
  the Skills endpoint).

## The four controls (map 1:1 to our modules)

| Meta control | Our equivalent | Status |
|---|---|---|
| Knowledge (FAQs, site, catalog, files) | KB module + vertical packs | built |
| Personality (tone, voice) | AgentIdentity + TargetProfile fields | built |
| Audience (who it talks to) | Per-business scoping, outward-code matching | built |
| Handoff (to your app) | handoff.py triggers + context packages | built |

## Endpoints that matter to us

- **Eligibility** — check a number CAN run an agent before selling anything.
- **Onboarding + Settings** — enable agent, accept ToS (ToS acceptance is a real step, not a checkbox we skip).
- **Skills** — tone/priorities/voice (v2.0.0 header required).
- **Agent Test API** — full pipeline replies synchronously, NO WhatsApp user needed, tokens NOT billed. This is our red-team target: attack the staging agent free, ship only what holds.
- **Handoff events** — initiation + status; our app receives both.

## Constraints that shape our product

1. **24-hour rule**: free-form messages only within 24h of the user's last message. After that, approved templates only. Support flows must branch on window state (see business_agent/window.py).
2. **Vertical exclusions**: Finance, Government, Health, Alcohol, Gambling, OTC drugs, matrimony. NONE of our 11 trades verticals are excluded — verified against the list.
3. **One number, one agent**: a number can't run conflicting messaging products. Dedicate the business number.
4. **Paid tiers coming** (token-metered for large firms). Track per-install spend; flag runaway usage.
5. **WhatsApp Business Tools MCP** (Sept 2026): Meta's own MCP for setup automation. Review its scopes before any agent touches it — same supply-chain rules as any third-party MCP.

## What changes for us (net)

1. **Muse is no longer the near-term channel** — Business Agent is live globally NOW. Muse becomes the upgrade path (docs/MUSE_SECURITY.md stays valid, priority drops).
2. **BISU is the multi-client answer.** One partner credential, per-client WABAs, our per-business scoping on top. Design all multi-tenant tooling around this.
3. **Agent Test API = free red-team target.** Every attack class in redteam/ should run against staging via Test API before any install goes live. Unbilled, no users involved.
4. **Onboarding gains eligibility + ToS steps.** Check eligibility endpoint first (never sell to an ineligible number), record ToS acceptance with date.
5. **Payment completion lives in Meta's agent.** Our posture stands: our connector declares no payment capability; per-install scope decision documents what Meta's side may complete; invoice-verification applies regardless of presenter.
