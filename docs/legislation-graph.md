# Legislation graph design

> Structured regulatory data that chatbots run on, auditors audit with,
> and Muse reaches via MCP. Status: built, 42 obligations, stdio MCP live.

## What it is

One obligation list, three consumers:

```
aionboard regulations/registry.json (36 trade-law rules)
aocsec tax_seed.json (5 tax/commercial pointers)
        ↓ normalize (legislation/graph.py)
41 Obligation records: id, law, requirement, applies_to,
jurisdiction, domain, citation, source_url, owner_action,
escalation, failure_mode, review_date, basis
        ↓
  chatbot (tailored advice)   audit (stale queue)   MCP (Muse)
```

## Tailored advice, honestly defined

`obligations_for(vertical, topic, domain)` returns matching,
non-stale obligations with citations + owner actions + escalations.
"Tailored" means filtered to the business — never generated. The
chatbot presents records; it does not interpret law. Anything uncertain
escalates to a human (accountant/solicitor) per the record's escalation
field.

## Tax without lying

Tax figures change. The graph stores pointers (what applies to whom,
where to check live, review dates), not rates. CIS, record-keeping,
VAT-threshold pointer, MTD pointer, late-payment interest. Quoting a
number from memory is a failure mode the redteam suite should probe.

## Audit use

- `stale_rules()` = the re-verification queue. Past review_date rules
  are excluded from advice automatically.
- Every record carries source_url + basis (verified-2026 vs
  pointer-live-source). Paid reports cite these.
- Digests: report builder pins content hashes (security_audit pattern).

## Muse path

- Today: stdio MCP (`python3 -m legislation.mcp_server`), 4 read-only
  tools. Same shape as powstock's MCP (verified pattern).
- For Muse: needs the authenticated HTTPS gateway (docs/muse-hardening.md
  §4). Same scopes + approval model as everything else. No gateway, no
  Muse — stdio servers are never exposed raw.

## What it is not

- Not legal advice. Records + citations + escalations. The chatbot says
  what applies and who to ask, never what to do.
- Not a tax calculator. Pointers only.
- Not merged with customer data. Business profiles filter the graph;
  nothing flows back.
