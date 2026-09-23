# MCP dependencies — evaluated, with verdicts

> Rule: adopt boring official surfaces, never privileged third parties
> in the payment/message path. Verified September 2026 from official
> docs. Re-evaluate quarterly — this ecosystem moves monthly.

## Adopt (with the stated guardrails)

**Meta WhatsApp Business Tools MCP** (official, remote, OAuth)
- What: setup + manage WhatsApp Business (accounts, numbers, templates,
  webhooks) from coding agents. `whatsapp_biz_` prefix.
- Why safe enough: OAuth sign-in, admin-of-app required, ToS gating,
  state changes need an authenticated person, per-tool review possible.
- Limits that matter to us: beta (tools may change), dev/test workflows
  — NOT production sending at scale; gradually rolling out (may be
  unavailable); remote only (needs mcp-remote bridge for stdio clients).
- Verdict: use for per-install WhatsApp setup automation. Never for
  bulk sending. Scope-review each new tool version (checklist in
  docs/whatsapp-tools-mcp-review.md).

**seayniclabs/stripe-mcp pattern (read-only Stripe)**
- What: third-party but architecturally right — balance, customers,
  invoices, products, prices. No create/update/delete tools exist.
- Verdict: adopt the PATTERN (and the package after code review):
  read-only Stripe access for turnover/invoice visibility. Writes stay
  in Stripe dashboards by humans.

## Track (don't depend on yet)

**metabusiness-mcp (third-party compliance engine)**
- What: 24 tools, compliance pre-checks (24h window, opt-out, frequency
  caps), Go binary, open-source tier claimed.
- Why not now: privileged position (every message through it), young
  project, Pro upsell on campaign tools. Our own 24h logic
  (business_agent/window.py) already covers the core check without a
  dependency. Revisit if their audit trail or caps exceed ours.
- If ever adopted: pin version, mcpscan every update, run behind our
  gateway scopes — never direct.

**WAME (Meta partner, unified WhatsApp/IG/Messenger)**
- What: Embedded Signup (clients never need their own Meta app),
  normalized webhooks, llms.txt for assistants.
- Verdict: strongest partner candidate for multi-channel onboarding.
  Evaluate commercially (fees, terms, data handling) before technical
  work. No code until a customer needs IG/Messenger alongside WhatsApp.

**whatsapp-sdk / waclient (Python, MIT)**
- Lightweight Cloud API wrappers. Useful as reference for webhook
  signature verification patterns. Don't add as dependencies until a
  build needs them — stdlib urllib covers our current call volume.

## Avoid

**Official Stripe MCP with write tools enabled** (`stripe_api_write`,
`create_refund`, `cancel_subscription`, `update_dispute`)
- Stripe's own docs warn: enable human confirmation, beware prompt
  injection with other servers. A refund tool reachable by an agent
  is the quote-fraud class with real money. Restricted keys help but
  the tool's existence is the risk.
- Rule: if Stripe MCP is ever enabled, it runs with a read-only
  restricted key AND our approval gate in front. Refunds, disputes,
  and subscription changes stay human-in-Stripe-Dashboard. No exceptions.

**Any MCP server that asks for secrets at setup time**
- Tokens go in env/secret stores via documented flows, never pasted
  into chats or config files. Our secret-scan covers our repos; extend
  the same rule to every customer install checklist.

**Unofficial WhatsApp Cloud API proxies (Kapso-proxied SDKs etc.)**
- Extra middleman in the message path = extra breach surface + extra
  terms to review. Use Meta direct or WAME partner only.

## Standing rules (from MCP spec July 2026, adopted verbatim)

- Tool annotations are untrusted unless from trusted servers.
- Human in the loop with deny capability on sensitive operations.
- Show tool inputs before calling; validate outputs before passing on.
- Timeouts on every call; log tool usage for audit.
- Deterministic tool ordering where we control the server (cache hits).
