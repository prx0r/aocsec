# Zero-knowledge onboarding — verify without seeing

> How we onboard businesses without ever holding their sensitive
> documents. Principle: check public registers, record attestations,
> never collect the document. Status: verify/ module shipped.

## The ladder (in order of preference)

1. **Public register lookup** — Gas Safe, NICEIC, TrustMark, DVSA/ADI,
   Companies House, waste carrier. No document changes hands at all.
   Some registers block scripts (Gas Safe 403s bots) — a human performs
   those lookups. That division is structural: `verify/methods.py`
   marks which are `human_lookup` vs `api`.
2. **Attestation + registration number** — numbers shown to customers
   (Gas Safe ID, NICEIC enrolment) are business credentials, safe to
   record. Stored: verdict + reference + named human + date.
3. **Customer redaction** — only when 1–2 can't answer. Guided: what to
   black out, what to keep. Reviewed on receipt, deleted after verdict.
4. **Never**: unredacted IDs, certificates with personal data, bank
   statements, full customer databases. No field exists for these in
   any table — the schema enforces the policy.

## What the attestation record proves

`business_id + qualification + verdict + reference + verified_by + date`.
Notably `verified_by` must be a named human — verification is an act
with an author, never "system". This is what auditors, insurers, and
the business itself rely on later.

## What we genuinely cannot see (by design)

- Bank credentials, card numbers (no fields, no flows).
- Full customer databases (imports rejected at the boundary).
- Personal documents (no upload path exists for them).
- Anything behind someone else's login (we use OAuth scopes or nothing).

If a workflow ever requires seeing something sensitive, the workflow
is wrong — redesign it to a register check or attestation.
