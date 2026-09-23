# Findings: business security gaps closed — 2026-09-23

All verified live or mocked-tested before filing. Severity: what was missing.

## Fixed today
1. **No email authentication checks (high).** SPF/DKIM/DMARC now checked
   via DoH in emailsec/. Live-verified against gmail.com.
2. **No invoice-fraud defense (critical for trades).** Verification
   workflow (ignore → call known number → two facts → record) +
   BLOCKED-by-default verdict + 2 redteam attacks. Fixed.
3. **No device/backup story (high).** Checklists with state in
   devicecheck/. 2FA-recovery emphasis (lose phone + codes = lockout).
4. **No presence-ownership story (medium).** GBP/social/domain checklist
   in presence/. Fake-review extortion guidance included.
5. **No ICO coverage (medium).** LEG-UK-ICO-FEE seed added (URL verified
   200). All 11 verticals now resolve general + specific rules.
6. **Stale counts in docs (low).** README/AGENTS updated to actuals.

## Still open (needs human)
- pow-site.service token (filed 2026-09-23-systemd-secret.md).
- Webhook URL, API keys, ONS URLs, Cloudflare Access rollout.
- Jev live calls (OpenRouter key held by user, deferred).
