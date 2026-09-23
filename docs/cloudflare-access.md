# Cloudflare Access in front of dashboard origins

> Status: not started. The token gate works; this removes the origin as a
> direct target. Do this once, then every dashboard is covered.

## Why

The powops dashboard binds loopback and is exposed via Cloudflare Tunnel.
Token auth stops casual browsing, but the origin URL + a leaked token still
means direct access. Access adds identity (email/OTP or SSO) before traffic
reaches the tunnel — stolen tokens alone stop working.

## Steps (dashboard owner, ~30 min)

1. Cloudflare Zero Trust dashboard → Access → Applications → Add.
2. Application: `admin.pow.systems`, session 24h.
3. Policy: Allow, emails matching your domain (or one-time PIN to your email).
4. Tunnel: confirm the tunnel's public hostname routes through the
   application (it does by default once the app exists for that hostname).
5. Test in a private window: expect identity challenge before the dashboard.
6. Keep the token gate in place (defense in depth, and the SPA needs it).
7. Rotate the dashboard token once after enabling (`token-rotate.sh`) so
   any previously leaked token + URL combination dies.

## Verify

- Private window, no login: challenged, cannot reach UI.
- Logged in, no token: API 401s (token gate still enforced).
- Logged in + token: 200s.
- `scripts/headers-check.sh` still passes (tunnel forwards headers).

## Rollback

Delete the Access application. Token gate continues to work unchanged.
