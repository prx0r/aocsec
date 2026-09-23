# Agent shells: build vs borrow (OpenMuse assessment)

> Question: should our per-target chatbot run on an existing free agent
> shell instead of custom UI? Assessed 2026-09-23 against OpenMuse
> (CopilotKit, MIT, 1.5k stars, active). Verdict: track, don't adopt yet.

## What OpenMuse is (verified from repo + docs)

Personal agent app: chat, agent computer (persistent Chromium + isolated
Linux terminal via Docker), Gmail/Calendar OAuth adapters, approvals +
receipts, durable tasks, identity/memory, finance CSV import. 154 tests,
real Chromium/Docker smoke tests, honest boundary docs. Single owner per
deployment — fits the sole-trader model well.

## What maps to our stack

| OpenMuse piece | Our equivalent | Verdict |
|---|---|---|
| Chat + approvals + receipts | approvals.py + assistant/ | Overlap — theirs is richer UI, ours is simpler + tested |
| Gmail/Calendar OAuth | Planned, not built | Their adapters are real code worth studying |
| Agent identity (name/tone/avatar) | AgentIdentity + TargetProfile fields | Same idea, both sides |
| Isolated terminal (nonroot, no net, caps) | Isolation doc (policy only) | Theirs is enforced; ours is checklist — gap |
| Durable tasks + leases | Nothing (we have stateless tools) | Genuine gap if assistants run long jobs |
| Finance CSV import | FreeAgent bridge (live data) | Ours is better (real bank data vs CSV upload) |

## Why not now

1. **Ops burden.** Node 24 + pnpm + Docker + Expo + CopilotKit project
   key. Our stack is stdlib Python on one VPS. Adopting OpenMuse means
   operating a second platform for every customer.
2. **Blast radius.** Browser + terminal in the agent loop is the largest
   attack surface in this whole estate. Our redteam suite has no coverage
   against a live browser/terminal agent. Adopting before testing that
   would violate our own rules.
3. **Key dependency.** CopilotKit Intelligence project key is server-side
   and required. Vendor gate on the critical path — evaluate terms
   before building on it.
4. **MCP interop unproven.** "Compatible with any harness" refers to
   AG-UI, not confirmed MCP consumption. Our garden MCPs may not plug
   in without bridge work.

## Adoption criteria (all must hold)

- [ ] Red-team suite (ours, 15 classes) green against a live deployment
- [ ] Terminal isolation claims independently verified (their smoke test
      re-run by us, not just read)
- [ ] Approval-bypass + tool-abuse probes written for browser/terminal
      vectors specifically
- [ ] CopilotKit key terms reviewed (data use, retention, egress)
- [ ] Single-customer pilot with full audit log review before second install

## Adjacent free solutions, same lens

- **FreeAgent** (adopted): free books via bank, OAuth API. No shell needed.
- **Turnstile** (adopted): free bot defense. No interaction model change.
- **GoCardless/Stripe Links** (adopted): payments stay on provider pages.
- **MCP scanners** (adopted): supply-chain vetting for anything we connect.
- Anything that adds a runtime, a key dependency, or a browser to the
  agent loop: track, red-team first, adopt only on evidence.
