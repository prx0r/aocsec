# WhatsApp Business Tools MCP — scope review checklist

> Meta's Sept 2026 MCP lets coding agents manage WhatsApp Business
> setup (accounts, numbers, templates, webhooks). Powerful = review
> before any agent touches it. Same supply-chain rules as any
> third-party MCP, plus Meta-specific items.

## Before first use

- [ ] List every tool the server exposes. For each: read or write?
- [ ] Writes (create account, register number, edit template) mapped
      to named humans who may approve them. No blanket approvals.
- [ ] Token scope minimal: setup-only, no messaging scopes unless
      messaging setup is in scope for this task.
- [ ] Token stored 600, server-side, never in chat or repo.
- [ ] Confirm the server binary/source: official Meta distribution or
      reviewed equivalent. No unofficial forks without diff review.

## Per use

- [ ] Template creation/edits reviewed by a human before submit
      (templates speak as the business once approved).
- [ ] Phone number registration double-checked (wrong number =
      business identity on someone else's SIM).
- [ ] Webhook URLs point at our endpoints only (exfiltration check).
- [ ] ToS/business-verification states recorded per client.

## Ongoing

- [ ] Re-run mcpscan-style description review on server updates
      (tool descriptions change = dependency update = re-review).
- [ ] Monitor for new tools appearing in updates (scope creep).
- [ ] Rotate tokens quarterly + on exposure.
