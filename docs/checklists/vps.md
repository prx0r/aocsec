# VPS checklist (quarterly)

- [ ] `~/.ssh/authorized_keys` reviewed (no unknown keys)
- [ ] Secret files are 600 (`dashboard_token`, `.env` files, R2 env)
- [ ] No world-writable dirs in repo paths
- [ ] systemd user units reviewed (ExecStart, no secret args)
- [ ] `git remote -v` shows no embedded credentials in any repo
- [ ] Old tokens rotated after chat/log exposure
- [ ] Backup of `~/.powops/` exists (state is irreplaceable-ish)
