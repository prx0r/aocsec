# Muse + email: who handles what

> Meta secures the connector. We secure everything the connector touches.
> Status: boundary defined, email-vector attacks in suite, invoice
> workflow covers the money case.

## What Meta handles (their docs, verified Sept 2026)

- Connector sandboxing, per-action approval cards, read-only modes.
- Secure Credentials Store for OAuth tokens.
- Directory review (functional + security + legal) for listed connectors.
- Google Workspace Limited Use policy compliance on their side.

## What Meta explicitly does NOT handle

- **Custom connectors: zero review.** "Ask Muse" integrations get no
  security, legal, or functional review. Our rule: directory connectors
  only; custom connectors refused during onboarding.
- **Memories persist past disconnect.** Email content Muse has seen may
  remain. Our rule: drafts reference job IDs and amounts, never names,
  numbers, or addresses. Teach forget-after-sensitive-jobs at handover.
- **Approval fatigue is ours to prevent.** Meta shows cards; if everything
  needs one, owners blanket-approve. Our tiering (reads auto, writes
  gated, destructive blocked) keeps card volume meaningful.

## The hole Meta can't close: the inbox is untrusted input

Every email Muse reads is a potential indirect prompt injection:
supplier bank-change notices, customer "the owner said 50% off" claims,
phishing forwarded for "review". Muse will summarize attacker content
fluently and neutrally — fluency is not verification.

Our defenses (all built, all tested):

1. **email_indirect redteam class** — quoted-email injection, bank-change
   emails, inbox exfiltration requests. Assistant must verify, refuse, or
   escalate; never act on email content as instruction.
2. **Invoice verification workflow** (emailsec/) — bank-detail changes
   go through call-known-number + two facts + written record, no matter
   which surface presented them (email, Muse summary, WhatsApp).
3. **Read-only connector posture** — Muse drafts replies; sending needs
   the human grant through approvals.py, same as every other channel.
4. **Memory hygiene** — no customer PII in prompts that persist; shapes
   and hashes in logs, never values.

## Per-install checklist additions

- [ ] Connector is directory-listed, not custom. Verify in Muse settings.
- [ ] Connector set to least privilege (reads needed, nothing more).
- [ ] Owner can state the bank-detail rule back: "call a known number".
- [ ] Red-team email_indirect suite green against their assistant config.
- [ ] Disconnect + forget flow demonstrated at handover.
