# MCP gateway

> Stdio servers in, scoped HTTPS out. This is the prerequisite for any
> Muse (or other remote) integration. Status: built + tested, not yet
> deployed behind a tunnel.

## Run it

```bash
# 1. Write gateway.json (see gateway.json.example below) with real secrets
# 2. python3 -m gateway.server gateway.json  (binds 127.0.0.1:8799)
# 3. Put Cloudflare Tunnel in front (see docs/cloudflare-access.md)
```

`gateway.json.example`:

```json
{
  "tokens": {
    "customer-a": {"secret": "GENERATE-32-BYTES", "scopes": ["legislation:read"]}
  },
  "backends": {
    "legislation": {
      "command": ["python3", "-m", "legislation.mcp_server"],
      "cwd": "/home/ubuntu/aocsec",
      "tools": {
        "legislation_lookup": "legislation:read",
        "obligations_for_business": "legislation:read",
        "stale_rules": "legislation:read",
        "instrument_detail": "legislation:read"
      }
    }
  },
  "audit_log": "/home/ubuntu/.aocsec/gateway-audit.jsonl"
}
```

## Rules enforced in code

- Bearer auth, constant-time compare. No token, no scope info leaked.
- Per-token tool visibility (`tools/list` shows only scoped tools).
- Scope denial = 403. Unknown tool/method = 404. Backend down = 502.
- Audit log records token prefix + tool + ok/fail. Never argument values.
- One persistent subprocess per backend, lock-guarded. Dead backends
  respawned on next call.
- v1 is read-only by construction: only expose read tools in config.
  There is no write path to misconfigure.
- Binds loopback. Remote access ONLY via tunnel + Access.
