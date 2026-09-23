# Dashboard checklist

- [ ] No token in README, docs, or chat logs (grep for token prefix)
- [ ] `?token=` links still work (SPA compat) AND Bearer header accepted
- [ ] Bad/missing token returns 401 (test quarterly)
- [ ] CSP has no unsafe-inline (check headers)
- [ ] Static assets served without auth, API gated
- [ ] Cloudflare Access in front of tunnel origin
- [ ] Token rotated after any exposure (script: token-rotate.sh)
- [ ] systemd unit has no hardcoded secrets or world-writable paths
