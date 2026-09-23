# OWASP Agentic Top 10 mapping (2026) — our controls vs gaps

> Source: OWASP Top 10 for Agentic Applications 2026 (ASI01–ASI10),
> built from real incidents (EchoLeak, GitHub MCP exploit, Gemini
> memory attack, Replit meltdown). Each entry: what covers it here,
> what's missing. Re-audit when architecture changes.

| ID | Threat (incident) | Our control | Gap |
|----|-------------------|-------------|-----|
| ASI01 | Goal hijack (EchoLeak) | Approval receipts; drafts never send; scoped mandates | Prompt-level hijack of a *running* session relies on red-team coverage — keep suite current |
| ASI02 | Tool misuse (Amazon Q) | Least-privilege scopes per MCP tool; read-only default; gated writes | Third-party tools (future garden MCPs) need per-tool review before enabling |
| ASI03 | Identity & privilege abuse | Bearer tokens, constant-time compare, per-token scopes; no passwords held | Token inventory across repos is manual (see findings) |
| ASI04 | Supply-chain poisoning (GitHub MCP exploit) | mcpscan self-scan (this repo) + external mcp-scanner clean 2026-09-23; allowlisted opencode.jsonc | Re-scan on every MCP addition; description changes need re-review |
| ASI05 | Unexpected code execution (AutoGPT RCE) | No eval/exec anywhere; collectors parse, never execute; stdlib only | Supplier-fetched content (CSV/XLSX/JSON) parsed with strict libs — keep it that way |
| ASI06 | Memory & context poisoning (Gemini) | Memory-hygiene rules; shapes-not-values logs; forget-after-sensitive-jobs | No automated memory audit — manual handover step only |
| ASI07 | Insecure inter-agent comms | Single-agent design today; MCP stdio is local-only | **Gateway changes this**: authenticated HTTPS bridge needs mutual review before Muse traffic |
| ASI08 | Cascading failures | Rate limits, timeouts, fail-closed defaults, dry-run-first | No circuit breaker on repeated upstream failures (retry storms possible) |
| ASI09 | Human-agent trust exploitation | Red-team suite (14 classes); receipts force human verification points | Polished wrong answers remain the hardest vector — receipts + evidence discipline is the mitigation, not a fix |
| ASI10 | Rogue agents (Replit meltdown) | **Gap until now**: no documented kill path | **Fixed**: scripts/kill-switch.sh (this commit) |

## Verification status

- Self-scan (mcpscan/): powops 17 tools + legislation 4 tools clean.
- External (mcp-scanner 0.1.0, 9 checks): clean 2026-09-23.
- Re-run both on any MCP addition, description change, or quarterly.
