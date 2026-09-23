# Threat model — POW estate

## Assets

| Asset | Where | Impact if compromised |
|-------|-------|----------------------|
| Dashboard (admin interface) | powops, port 8796 + tunnel | Full read of all garden health, history, incidents |
| GitHub PATs / API keys | VPS env, .env files | Repo write, supplier API abuse, billing |
| Companies House keys | powuk/.env | API quota abuse |
| Garden databases | each repo warehouse/ | Historical data tampering |
| Customer PII | aionboard CRM (local, gitignored) | Privacy breach, ICO liability |
| R2 credentials | garden env | Raw archive read/write |

## Actors

- Opportunistic scanners (open ports, default creds)
- Curious readers (public repos — everything committed is public)
- Supply chain (PyPI deps, GitHub Actions, MCP clients)
- Insiders (agents with shell — every coding agent is privileged)

## Attack surfaces

1. **Public git history.** Anything ever committed is public forever.
   Controls: secret-scan in CI, .gitignore for .env/*.db, fast rotation.
2. **Dashboard tunnel.** Token in URL leaks via logs/history. Controls:
   Bearer header support (done), Cloudflare Access (open), rotation (scripted).
3. **MCP stdio.** Local-only by design. Risk is a malicious MCP *client*,
   not the servers. Servers must stay read-only (powops) or approval-gated
   (aionboard design).
4. **Collector inputs.** Upstream URLs, CSVs, XLSX (openpyxl), JSON feeds.
   Parsers run on untrusted bytes. Controls: timeouts, size caps, no eval.
5. **Agent shell.** Every agent on this VPS can read every repo and env file.
   Controls: file permissions (600 for secrets), no secrets in chat logs.

## Non-goals

- Hardening GitHub/Cloudflare themselves.
- Formal certification. Judgment + checklists, not compliance theatre.
