# Muse hardening guide

> How to be secure on Muse specifically. Sources: Meta Help Centre
> (Connectors), muse.ai/platform, Meta connector review requirements.
> Verified September 2026. Re-verify quarterly — this platform is weeks old.

## 1. The two ways onto Muse (different trust levels)

| Path | Review | Credential handling | Verdict for us |
|------|--------|--------------------|----------------|
| Directory connector (muse.ai/platform) | Functional + security + legal review, end-to-end testing | Scoped OAuth via Meta | **Target.** Submit the read-only buddy + gated draft_quote. |
| Custom connector ("ask Muse") | NO Meta review. Credentials in Muse Secure Credentials Store. | User-pasted API keys, stored by Meta | **Never recommend.** Tell customers to refuse custom-connector setups that ask for bank, email passwords, or API keys. |

The dangerous sentence a customer will hear: "just paste your API key and I'll connect it." Our onboarding must explicitly warn against this for financial inboxes. Directory connectors only.

## 2. What we declare (and therefore what Muse can do)

Muse connectors support read-only mode per connector plus per-action
approval cards. Our manifest declares:

- Reads: business_lookup, pain_lookup, install_status, opportunity_digest.
  No approval needed, least-privilege OAuth scopes.
- One gated write: draft_quote. Returns a draft + approval receipt.
  Never sends. Approval card enforced on Meta's side AND ours
  (approvals.py) — either side can stop it.

There is no payment capability in the manifest. Muse cannot request what
isn't declared. If Meta ever offers transactional connectors, that is a
new submission, new review, new threat model — not an upgrade.

## 3. Memory persistence is a PII finding

Meta documents: disconnecting a connector stops future exchange, but data
Muse already used "might still remain in Muse's memories and conversation
history." Consequences for onboarding:

- Never let business or customer PII flow through Muse prompts that
  persist. Drafts reference job IDs and amounts, not names/addresses/
  phone numbers, unless the customer explicitly puts them there.
- Teach every customer: Settings → ask Muse to forget an interaction
  after sensitive jobs. Part of the handover checklist.
- Our audit logs already store shapes+hashes, never values — same rule
  applies to anything pasted into Muse.
- Red-team class `memory-persistence` covers this (see redteam/attacks.py).

## 4. Remote MCP requirement

Muse builds MCP clients on its own VMs using the official SDK over
**streamable HTTP**. Our garden MCPs are stdio-only (local processes).
Implications:

- Muse cannot reach stdio servers. A remote MCP gateway (HTTPS +
  per-customer auth) is prerequisite to any Muse↔garden integration.
- Do NOT expose raw stdio servers over HTTP with no auth to satisfy
  this. Gateway must enforce the same scopes + approval receipts as
  local use.
- Until the gateway exists, Muse integration is directory-connector
  only (our API behind our auth), not direct MCP.

## 5. Approval cards + our receipts (both must agree)

Muse asks approval for important actions by default; connectors can be
set read-only. Our layer adds: propose → grant → execute in separate
steps with separate actors, audit entries on both. An action needs Meta's
card AND our receipt. Either side vetoes silently (fail closed).

## 6. Submission checklist (muse.ai/platform)

- [ ] Connector manifest matches deployed behavior exactly
- [ ] No payment/bank credential flows anywhere in the product
- [ ] Privacy policy covers connector data use
- [ ] Red-team evidence pack green (ATTACKS suite + report)
- [ ] Approval-card copy reviewed (what the owner sees and grants)
- [ ] Revocation path tested (disconnect → verify no further exchange)
- [ ] No fee/revenue-share terms accepted blindly (none published yet —
  read whatever is offered at submission time)
