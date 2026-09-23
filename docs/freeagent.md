# FreeAgent integration — free books + safe MCP access

> Answer to "is it easy to do taxes with a free QuickBooks-type thing":
> yes — FreeAgent is free with a NatWest/Mettle/RBS/Ulster business
> account, HMRC-recognised end-to-end for MTD, and has an OAuth 2.0 API.
> Verified September 2026. Re-check pricing before quoting.

## 1. The free route (no "FreeBooks" product exists — this is it)

| Route | Cost | What you get |
|-------|------|--------------|
| NatWest / RBS / Ulster business account | Free FreeAgent included | Full software, same features as paid |
| Mettle account (1+ transaction/month) | Free FreeAgent included | Same, via Mettle app |
| No eligible bank | ~£33/mo (often £16.50 intro) or Taxfix from £4.99/mo | Paid fallback |
| HMRC list | Free AND paid options | From 6 April 2027, sole traders/landlords over £30k must use MTD software — check current threshold/phase at gov.uk |

For an electrician: open a Mettle account (free, minutes), get FreeAgent
free, connect bank feed, done. That single move solves bookkeeping, MTD
readiness, and invoice chasing. Recommend this in onboarding before
anything custom.

## 2. The API (what MCP tools can call)

FreeAgent Company API, OAuth 2.0, REST+JSON (`api.freeagent.com/v2`).
Full endpoint list at dev.freeagent.com. The ones that matter:

| Endpoint | Use | Tier |
|----------|-----|------|
| GET /v2/invoices | Sales history → turnover figures | read |
| GET /v2/bills, /v2/expenses | Cost tracking | read |
| GET /v2/bank_transactions | Reconciliation input | read |
| GET /v2/bank_accounts | Which accounts exist | read |
| GET /v2/cis_settings, /v2/bank_transaction_explanations | CIS + categorization | read |
| POST /v2/invoices (draft) | Prepare invoice for owner to send | **gated write** |
| VAT/Self Assessment filing | **NEVER via agent** | blocked |

OAuth flow: register app at dev.freeagent.com → owner authorizes in
THEIR FreeAgent (their login, their consent screen) → scoped tokens.
We hold tokens, never passwords. Token scope = minimum set above.

## 3. How it plugs into our stack

```
Customer's FreeAgent (their account, their bank feed, their data)
        ↓ OAuth 2.0, scoped tokens
aocsec/freeagent/ client (reads + draft-only writes)
        ↓
  a. turnover figures → tax/ ledger (replaces manual entry)
  b. draft invoices → approvals.py receipt → owner sends in FreeAgent
  c. MTD readiness → mtd_checklist() pre-filled from real state
        ↓
Filing happens in FreeAgent, by the owner, on FreeAgent's UI.
The agent loop ends at the draft. Always.
```

What this changes in our code:
- `tax/turnover.py` gains `from_freeagent_invoices()` — monthly sums
  from invoice data instead of hand-typed figures. Same bands, same
  owner-supplied threshold rule.
- MCP tools (when the gateway exists): `freeagent_invoices`,
  `freeagent_expenses`, `freeagent_turnover`, `freeagent_draft_invoice`
  (gated). Filing endpoints are never exposed as tools.

## 4. What we will not do

- Hold FreeAgent passwords or share one app credential across customers
  (each business authorizes its own connection).
- File VAT, Self Assessment, or MTD submissions via agent. The owner
  clicks send in FreeAgent. Our redteam suite treats any filing path
  as a breach.
- Store bank transaction payloads. Read, aggregate, discard; keep only
  monthly totals in the 600-perm ledger.
- Recommend specific products as financial advice. Present options +
  freeness conditions, customer + accountant decide.
