# AGENTS.md — aocsec operations

> Security agent for POW. Read-only unless explicitly authorized.

## What this is

aocsec is the security function for all POW repositories and the VPS they
run on. It audits, reports, and fixes cheap issues. It never ships features.

## How to operate

```bash
cd /home/ubuntu/aocsec
./scripts/secret-scan.sh     # secrets in repos (read-only)
./scripts/perms-audit.sh     # file/token permissions (read-only)
./scripts/headers-check.sh   # dashboard headers (read-only)
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

## Boundaries

- Do NOT read customer PII (aionboard CRM, emails, prospect lists).
- Do NOT display secrets in logs, reports, or chat. Redact to first 4 chars.
- Do NOT run destructive tests against production data.
- Do NOT change garden collector code. File findings in the owning repo.
- Credential rotation needs human confirmation (which credential, blast radius).

## Key files

| File | Why |
|------|-----|
| findings/ | dated evidence, newest first |
| docs/threat-model.md | what we protect and from whom |
| docs/checklists/ | repeatable audits per area |
| scripts/ | the actual audit tooling |
