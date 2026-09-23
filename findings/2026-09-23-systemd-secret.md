# Finding: hardcoded token in pow-site.service — 2026-09-23

Severity: **high**. Status: **open, needs owner action**.

## Evidence
`~/.config/systemd/user/pow-site.service` line 13 sets
`Environment=POW_SITE_TOKEN=<32-char token>` inline. Unit files are
world-readable (644); any local user can read the token. Caught by
`scripts/perms-audit.sh` (systemd section).

## Blast radius
Whoever holds the token can likely authenticate to the pow-site dashboard
API as the service. Same-user VPS, so local boundary only — but backups
and snapshots of home dirs would carry it.

## Remediation (owner: powpowpow)
1. `head -c 32 /dev/urandom | base64` → new token (or keep value, just relocate).
2. Write to `/home/ubuntu/.config/systemd/user/pow-site.env` with 600.
3. Unit: replace `Environment=` line with `EnvironmentFile=/home/ubuntu/.config/systemd/user/pow-site.env`.
4. `systemctl --user daemon-reload && systemctl --user restart pow-site.service`.
5. If the value was ever committed to git or shared in chat, rotate instead of relocate.

## Detection going forward
perms-audit.sh now fails on any `Environment|ExecStart` line containing
TOKEN|KEY|SECRET|PASSWORD= in user units.
