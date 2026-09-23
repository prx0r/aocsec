# AGENTS.md — aocsec operations

> Security function for POW + aionboard. Read-only unless explicitly authorized.
> Test suite: `python3 -m unittest discover -s tests` — 215 tests, must stay green.

## What this repo holds

| Area | Code | Rule |
|------|------|------|
| Estate audits | `scripts/` (secret-scan, perms-audit, headers-check, token-rotate) | read-only except token-rotate |
| Adversarial testing | `redteam/` (15 attack classes, grader, evidence runner) | test doubles live here; live runs need approval |
| Legislation graph | `legislation/` (42 obligations + stdio MCP) | records carry sources; stale excluded |
| Rulebook auditing | `rulebook_audit/` (chain, PII, poison, staleness) | flags, never auto-deletes |
| Customer security product | `security_audit/` (free checks + paid reports) | customer-authorized domains only |
| Bookkeeping integration | `freeagent/` (OAuth, reads, drafts) | no filing, no payments, no bank creds — by construction (no methods exist) |
| Cheap judgments | `jev/` (triage, confidence-gated) | needs key; refuses without one; System One only |
| Safe tax organizer | `tax/` (turnover, MTD checklist, records) | user figures in; thresholds user-supplied; no filing |
| Support backend | `support/` (tickets, handoff, KB, e-manual) | human owns money/legal calls; bot drafts, human sends |
| Maintenance product | `maintenance/` (plans, monthly runner, certificates) | proposals only; humans send/resolve |
| WhatsApp delivery | `whatsapp/` (templates, consent, window gates) | builders return payloads; transport sends |
| Scheduling | `scheduler/` (jobs, compliance calendar) | due-lists, never auto-send |
| Doc vault + billing | `vault/`, `billing/` (hashstore, plan state) | no charging code exists |
| Remote access | `gateway/` (Bearer auth, scoped tools, audit chain) | loopback + tunnel only; read-only v1 |
| Business Agent gates | `business_agent/` (eligibility, ToS, 24h window, payment scope) | gate blocks selling to ineligible numbers |
| Structural proof | `structure/` (AST scan: no eval/exec/shell/pickle) | run per release, fails on new capabilities |
| Audit chain | `audit_chain/` (hash-linked log, redacting writes) | gateway migrated; tamper-evident |
| Backup proof | `backups/` (manifest, freshness, drill records) | drills pass only with evidence |

## How to operate

```bash
cd /home/ubuntu/aocsec
./scripts/secret-scan.sh     # secrets in repos (read-only)
./scripts/perms-audit.sh     # file/token permissions (read-only)
./scripts/headers-check.sh   # dashboard headers (read-only)
python3 -m unittest discover -s tests   # 215 tests
```

Writes require explicit user approval, except `token-rotate.sh` which only
touches `~/.powops/dashboard_token` and restarts the dashboard service.

## Findings workflow

1. Reproduce first. No finding without a command + output.
2. Write to `findings/YYYY-MM-DD-<topic>.md` with severity:
   - **critical**: active exposure (secret in git, open admin, RCE vector)
   - **high**: exploitable with effort (weak auth, permissive CORS, stale dep with CVE)
   - **medium**: hardening gap (headers, permissions, logging of sensitive paths)
   - **low**: hygiene (warnings, docs, cosmetic)
3. Fix critical/high immediately if the fix is safe and reviewable.
4. Everything else gets an owner + remediation steps, never just a description.

## Hard boundaries (violations caused real damage before)

- aocsec is the ONLY repo this agent writes to. See the global scope rule
  in `~/.config/opencode/AGENTS.md` — obey it over any task wording.
- Do NOT read customer PII (aionboard CRM, emails, prospect lists).
- Do NOT display secrets in logs, reports, or chat. Redact to first 4 chars.
- Do NOT run destructive tests against production data.
- Do NOT change garden collector code. File findings in the owning repo.
- Credential rotation needs human confirmation (which credential, blast radius).
- Tests that need network must tolerate absence (skip) or mock. Suite must
  pass offline except checks explicitly marked live.

## Key files

| File | Why |
|------|-----|
| findings/ | dated evidence, newest first |
| docs/ | design docs (see README index) + checklists |
| scripts/allowlist.txt | reviewed scanner exceptions with reasons |
| tests/ | mocked suites; live-network tests skip gracefully |
