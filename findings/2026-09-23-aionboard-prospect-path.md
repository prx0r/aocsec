# Finding: prospect-engine failures are a hardcoded path, not broken logic

> Filed 2026-09-23 from aocsec after pull of aionboard `2ca5501`.
> Read-only on their side. Reproduce: see commands below.

## Severity: medium (P0 for sales ops, not security)

## Reproduce

```bash
cd /home/ubuntu/aionboard
git log --oneline -1   # 2ca5501
python3 -m pytest tests/test_prospects_engine.py -q   # 16 failed, 6 passed
python3 -m pytest tests/test_prospects_engine.py::TestLoadElectricalBusinesses::test_returns_non_empty_list -q
# E PermissionError: [Errno 13] Permission denied: '/root/powuk/data/normalized/ch_capacity'
```

## Root cause

`aionboard/prospects.py:21,94,339,493-494` and
`tests/test_prospects_engine.py:21` hardcode `POWUK_BASE =
"/root/powuk"`. On this VPS the data lives at
`/home/ubuntu/powuk/data/normalized` (exists, `ubuntu:ubuntu`,
readable). The engine logic may be fine; every test dies at the
filesystem boundary before asserting anything.

The "P0 fixes" commit `620c708` (stubs, false matches, consent,
scoring) did not touch this — the 16 failures are identical before
and after it.

## Fix (one line each, their repo)

```python
# aionboard/prospects.py
def load_electrical_businesses(powuk_base: str = os.environ.get(
        "POWUK_BASE", "/home/ubuntu/powuk")) -> list[dict]:

# tests/test_prospects_engine.py
POWUK_BASE = os.environ.get("POWUK_BASE", "/home/ubuntu/powuk")
```

Better: default to env var, fail with a clear message if the path
is missing, and keep one committed small fixture so the suite passes
offline on any machine (AGENTS.md convention #2).

## Why it matters

- Sales playbooks and outreach templates assume ranked prospect
  lists exist. This is the machine that makes them; it's red at the
  first function call.
- 1,166 prospects reportedly wired into the pipeline — if that came
  from a manual one-off run on a path that works interactively, the
  pipeline is fine but the regression suite is blind. Both facts
  should be checked before anyone claims the engine is fixed.

## Acceptance

- `python3 -m pytest tests/test_prospects_engine.py -q` → green
- Suite green offline without /root access
- One sentence in THREADS.md when closed
