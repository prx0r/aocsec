# HANDOVER — aocsec

> Read this first. Then AGENTS.md for operations, threads (below) for open work.
> Last verified: 2026-09-23. Suite 234/234 green. Estate scans clean.

## What this repo is

Security backend for POW + aionboard trades work: audits, adversarial
testing, legislation, safe tax tooling, support backend, maintenance
engine, and the MCP gateway. 25 modules, all cross-linked (see README
layout). Nothing here collects customer data; everything here protects,
verifies, or evidences.

## Current state

- **Tests:** 234 green (`python3 -m unittest discover -s tests`).
- **Scans:** secret-scan clean (1 documented exception), structure scan
  clean across aocsec/powops/aionboard agent paths (83 files here).
- **Findings open:** pow-site.service token (needs owner),
  webhook URL, 5 API keys, ONS URLs, Cloudflare Access, Jev key.
- **Dormant by design:** Jev live calls, gateway deployment, Muse
  submission, Shop Pay — all need human keys/decisions.

## Scope rule (hard)

Work ONLY in `/home/ubuntu/aocsec`. Never write/commit/push anywhere
else. Read other repos for research. If another repo needs action: stop
and ask. See global `~/.config/opencode/AGENTS.md`.

## Module map (where to work)

| Need | Go here |
|------|---------|
| Customer-facing security product | security_audit/, maintenance/ |
| Attack the assistant | redteam/ (15 classes + runner) |
| Law/tax questions | legislation/ (42 obligations + MCP) |
| Prove history intact | audit_chain/ (+merkle seals, certificates) |
| Prove code can't misbehave | structure/ (AST scanner) |
| Prove survival | backups/ (manifest, freshness, drills) |
| Per-customer ops | support/, onboarding/, billing/, vault/ |
| Money-adjacent (careful) | freeagent/, tax/ (reads only, no filing/paying) |
| Cheap AI judgments | jev/ (dormant until key) |
| Remote access | gateway/ (Bearer + scopes + audit chain) |
| Company checks | company/ (Companies House, PII-minimized) |
| Checklists | devicecheck/, presence/, isolation/ |

## Conventions (don't break these)

1. **Reads never write.** Monitoring/query paths must not mutate state
   (caused our worst bugs historically — see powops peer review).
2. **Tests use fixtures/mocks.** Live network only in explicitly marked
   tests; suite must pass offline.
3. **No secrets in repo.** Tokens via env; `.env` never tracked
   (scanner enforces).
4. **Counts in docs are load-bearing.** README/AGENTS state test + class
   + obligation counts — update them in the same commit that changes
   the numbers.
5. **Findings, not vibes.** Every claim cites file:line or command output.

## threads.md lives where?

There is no threads.md here — open work is tracked in each session's
todos plus `findings/` for filed items. If this repo grows a second
agent, create one.
