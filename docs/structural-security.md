# Structural security — remove capability, don't guard it

> Detection asks "did anything bad happen". Structure asks "is the bad
> thing even expressible". Both run; structure runs first because it is
> cheaper and cannot be prompt-injected.

## Removed capabilities (proven absent by structure/scan.py)

| Capability | Proof | Where enforced |
|---|---|---|
| Arbitrary code execution | no `eval`/`exec`/`compile` in agent paths | structure scan, all POW Python repos clean |
| Shell injection | no `os.system`, no `shell=True` | same scan |
| Deserialization attacks | no `pickle`, no unsafe `yaml.load` | same scan |
| Payment initiation | no methods exist (FreeAgent client, assistant) | code review + redteam invoice_fraud |
| Filing returns | no methods exist (tax module, FreeAgent client) | code review |
| Auto-send messages | no send path (assistant drafts only) | code review + redteam approval_bypass |
| Card/bank storage | no fields, no tables, no code paths | schema review |

Run `structure/scan_repo` against every repo on every release. New
capabilities (a send method, an exec call) fail the scan until a
threat review explicitly allows them with gates attached.

## Audit chain (prove what happened)

`audit_chain/` — hash-linked append-only log. Gateway audit migrated
to it. Secrets redacted at write time (key-shaped names + long opaque
strings). Tamper, deletion, and reorder all break verification.

## Backups (prove survival)

`backups/` — manifest of what must survive (powops state, tokens,
gateway audit), freshness checks with max ages, and restore-drill
records that pass only with per-step evidence. Backups nobody restores
are wishes; drills are scheduled evidence.
