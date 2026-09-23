# Security Policy

## Reporting a vulnerability

Email the repo owner directly. Do not open public issues for active exposures.

Include: affected system, reproduction steps, impact assessment. Redact secrets.

## What counts as critical

- Secret committed to any public repo (API key, token, private key)
- Dashboard or API accessible without auth
- Remote code execution vector
- Customer PII readable outside its owning system

## Response targets

| Severity | Acknowledge | Fix/defer with reason |
|----------|-------------|----------------------|
| critical | same day | 48 hours |
| high | 2 days | 2 weeks |
| medium | 1 week | next cycle |
| low | best effort | backlog |

## Out of scope

- Social engineering, physical access
- Third-party services' own infrastructure (GitHub, Cloudflare)
- Theoretical issues without a reproduction on our systems
