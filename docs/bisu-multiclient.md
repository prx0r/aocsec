# BISU multi-client design

> One partner credential acting across client WABAs, with per-business
> scoping on our side. Status: design. No BISU token exists yet.

## Why BISU and not per-client tokens

Per-client system-user tokens mean N credentials to issue, store,
rotate, and audit — one per trades business. A BISU (Business
Integration System User) token lets our platform act on behalf of
multiple client WABAs under one credential, with Meta's own
partner-scoping as the outer boundary and our per-business records
(business_id everywhere) as the inner one.

## Rules

1. BISU token lives server-side only, 600 perms, never in chat/logs/repos.
2. Every call carries explicit business_id; the bridge layer rejects
   calls without one (no ambient authority).
3. Per-business scopes enforced locally even though BISU is broad:
   a compromised bridge process can only touch what the mapping allows.
4. Token rotation quarterly + on any exposure. Rotation drills recorded.
5. If BISU is ever unavailable, fall back to per-client system-user
   tokens — same interface, narrower blast radius per credential.

## What we still need from Meta/human

- Solution Partner / Tech Provider status (or equivalent) to obtain BISU.
- Per-client WABA onboarding flow (Embedded Signup preferred — client
  never hands us Meta credentials).
- Webhook subscriptions per client for inbound + agent-reply copies
  (feeds our audit trail).
