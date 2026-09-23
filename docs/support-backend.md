# Boring backend map — adopt vs built

> Rule: adopt boring commodity software, build only the AI-specific
> layer. Status: our layer built + tested; adoptions are decisions
> with named candidates below.

## Adopt (don't build)

| Need | Use | Why this one |
|------|-----|--------------|
| Ticket desk | osTicket (free OSS) / Go Help Desk (OSS + native MCP) / ITFlow (OSS PSA+billing) | All free, proven, MCP-native options exist. Our tickets module stays minimal for embedding, not competing. |
| Status page | openstatus (OSS, self-hostable, API+MCP) | Audit-ready incident comms; SOC2-friendly evidence. |
| Bot defense | Cloudflare Turnstile (free) | Already specified in form-defense.md. |
| Payments | Stripe Links + GoCardless | Already specified in payments-hardening.md. |
| Books | FreeAgent via bank (free) | Already specified in freeagent.md. |

## Built here (AI-specific, nobody sells it)

| Need | Module | Why build |
|------|--------|-----------|
| Handoff protocol | support/handoff.py | Explicit/implicit/policy triggers + context packages are our product logic. No OSS desk does AI→human with our approval receipts. |
| Ticket lifecycle + SLA | support/tickets.py | Minimal, embeddable, chained audit. Full desks adopted above; this is the glue + evidence layer. |
| Shared KB | support/kb.py | One answer source for bot + humans; ticket→article promotion loop. Desk KBs are human-only silos. |
| E-manual + systems graph | support/manual.py | Per-business operating doc + machine-readable structure. Nobody generates these from live state. |
| Red-team + approvals | redteam/, approvals pattern | Domain-specific attack classes + receipt model. promptfoo/garak complement as external probers. |

## Integration points (where they meet)

- Desk webhooks → our tickets (import) or ours → desk (export). Either direction, ticket IDs cross-referenced.
- KB articles sync both ways with source tags (ours vs desk).
- Status page incidents reference our incident IDs (powops pattern).
- Support minutes feed the maintenance engine (care_plus review time).
