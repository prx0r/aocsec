# MCP checklist

- [ ] Servers bind stdio only (no network listeners)
- [ ] Write tools require explicit approval + audit log
- [ ] Error paths never echo secrets or env contents
- [ ] Tool payloads have size discipline (status/sources >64KB noted)
- [ ] Only intended servers enabled in opencode.jsonc
- [ ] Fixture-data servers (powphysical) stay disabled until real
