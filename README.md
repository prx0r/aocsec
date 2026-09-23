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
├── docs/                  # design + hardening guides (index below)
├── scripts/               # runnable audits (all read-only except token-rotate)
├── findings/              # dated audit reports (YYYY-MM-DD-topic.md)
├── redteam/               # adversarial suite: 15 attack classes, grader, runner
├── legislation/           # obligation graph + tax seed + stdio MCP server
├── rulebook_audit/        # rulebook chain/PII/poison/staleness auditor
├── security_audit/        # free domain checks + paid digest-pinned reports
├── freeagent/             # OAuth + read client + turnover bridge (no filing)
├── jev/                   # cheap-judgment triage, confidence-gated (key-gated)
├── tax/                   # safe organizer: turnover, MTD checklist, records
├── support/               # tickets+SLA, handoff, KB, e-manual, systems graph
├── maintenance/           # monthly plans, runner, certified reports
├── gateway/               # authenticated MCP bridge for remote/Muse access
├── business_agent/        # Meta Business Agent gates, 24h window, payment scope
├── structure/             # AST scanner proving dangerous primitives absent
├── audit_chain/           # hash-chained append-only audit log
├── backups/               # manifest + freshness + restore drills
├── emailsec/              # SPF/DKIM/DMARC + invoice-fraud verification
├── devicecheck/           # device + backup checklists with state
├── presence/              # GBP/social ownership checklists with state
├── company/               # Companies House lookup + capability manifests
├── isolation/             # per-agent identity checklists + loss arithmetic
├── mcpscan/               # MCP tool-description poisoning scanner
└── tests/                 # 179 tests, fully mocked except live-API-free paths
```

### Docs index

| Doc | What |
|-----|------|
| threat-model.md | assets, actors, attack surfaces |
| checklists/ | dashboard, secrets, MCP, VPS repeat audits |
| muse-hardening.md | directory vs custom connectors, memory rule, remote-MCP requirement |
| muse-email.md | Meta-handles vs ours boundary for inbox threats |
| business-agent-architecture.md | Meta platform endpoints, tokens, controls (imported) |
| business-agent-posture.md | per-install posture for the live channel |
| bisu-multiclient.md | one partner credential across client WABAs |
| test-api-redteam.md | free staging attacks via Meta Test API |
| whatsapp-tools-mcp-review.md | scope review checklist for Meta's setup MCP |
| payments-hardening.md | Stripe Links + GoCardless + SAQ A, per-install checklist |
| form-defense.md | Turnstile pattern for enquiry/booking forms |
| freeagent.md | free route (NatWest/Mettle), API surface, OAuth flow, tiers |
| jev-integration.md | setup, tool mapping, confidence policy, cost logic |
| legislation-graph.md | graph design, pointers-not-rates, audit use, Muse path |
| rulebook-security.md | entry contract, 5 audit checks, append-only writes |
| cloudflare-access.md | Access setup + verify + rollback for dashboard origins |
| gateway.md | run + config + rules for the MCP bridge |
| mcp-dependencies.md | adopt/track/avoid verdicts on third-party MCPs |
| owasp-agentic-mapping.md | ASI01–ASI10 controls vs gaps |
| structural-security.md | removed capabilities, audit chain, backup proof |
| agent-shells.md | OpenMuse verdict: track, don't adopt |
| agent-support.md | agent-managed support loop design |
| agent-isolation.md | dedicated identities, capped wallets, revocation |
| accounts-package.md | passwords, 2FA order, offboarding, insurance pointer |
| vertical-security.md | per-trade threat notes + agent rules |
| vertical-capability.md | what works per vertical (audited matrix) |
| security-business-model.md | bundled baseline + paid depth tiers |
| support-backend.md | adopt-vs-build map for desk tooling |
| agentcom-influence-patterns.md | stolen/tracked/skipped verdicts |

## Rules

1. **Never commit secrets.** If a script needs a token, take it from env, never a file in this repo.
2. **Read-only by default.** Only `token-rotate.sh` writes, and only to `~/.powops/`.
3. **Evidence over claims.** Every finding cites a file, line, or command output.
4. **Fix cheap, file the rest.** One-line fixes go in immediately; structural work becomes a thread with an owner.
