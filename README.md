# aocsec — security for POW systems

> All security for the POW estate: 7 data gardens, powops, powk, aionboard.

## Mission

Find exposures before attackers do. Fix the cheap ones immediately.
Document the rest with severity, owner, and remediation steps.

## Scope

| System | What aocsec covers |
|--------|-------------------|
| powops dashboard | Auth, CSP, tokens, tunnel, Cloudflare Access |
| All gardens | Secrets in repos, API key handling, .env hygiene |
| MCP servers | Tool scopes, approval gates, secret redaction |
| VPS | File permissions, systemd hardening, log redaction |
| Supply chain | Dependencies, webhook URLs, third-party tokens |
| aionboard | Customer PII boundaries, consent records, CRM secrets |

## Quick start

```bash
# Scan all repos for leaked secrets
./scripts/secret-scan.sh

# Audit file permissions and token storage
./scripts/perms-audit.sh

# Rotate the powops dashboard token
./scripts/token-rotate.sh

# Check dashboard security headers
./scripts/headers-check.sh
```

## Layout

```
aocsec/
├── README.md              # this file
├── AGENTS.md              # how security agents operate
├── SECURITY.md            # vulnerability reporting policy
├── docs/
│   ├── threat-model.md    # assets, actors, attack surfaces
│   └── checklists/        # per-area audit checklists
├── scripts/               # runnable audits (all read-only except token-rotate)
└── findings/              # dated audit reports (YYYY-MM-DD-topic.md)
```

## Rules

1. **Never commit secrets.** If a script needs a token, take it from env, never a file in this repo.
2. **Read-only by default.** Only `token-rotate.sh` writes, and only to `~/.powops/`.
3. **Evidence over claims.** Every finding cites a file, line, or command output.
4. **Fix cheap, file the rest.** One-line fixes go in immediately; structural work becomes a thread with an owner.
