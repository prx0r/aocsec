# Secrets checklist (per repo, quarterly)

- [ ] `git log -p --all -S 'ghp_'` clean (no PATs in history)
- [ ] `git log -p --all -S 'sk-live'` clean (no Stripe keys)
- [ ] No `.env` tracked (`git ls-files | grep env`)
- [ ] API keys only via env vars, never hardcoded
- [ ] `~/.powops/dashboard_token` is 600
- [ ] Webhook URLs not committed (use env or server-side config)
- [ ] R2 credentials in 600 env file, not unit files
- [ ] No credentials in systemd unit files
