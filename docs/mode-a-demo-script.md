# Mode A demo script — prospect plays both seats

> Sales demo on OUR number. Prospect plays customer first, then owner.
> Fictional data only. Runs on staging (test number) or production
> number once verified. Every step maps to a real module + receipt.

## Setup (5 min before the meeting)

1. Test/production number live, `WHATSAPP_TOKEN` in env (never in repo).
2. Prospect's phone opted in: `record_consent(conn, to, "demo-<date>")`.
3. Price book loaded with 3 fictional electrician jobs (their trade,
   fake prices — say so out loud).
4. Dashboard/audit tail visible on your screen for the reveal.

## Act 1 — prospect plays customer (3 min)

Prospect sends: **"hi do you do consumer unit replacements"**

1. Assistant replies free-form (inside 24h window — builder checks
   `in_freeform_window`, consent checked first).
2. Prospect: **"how much roughly"**
3. Assistant replies with the fictional range + "needs photos or a
   visit to confirm" (the honesty line — say it, show it working).

What you narrate: "It answers from YOUR price book, never invents
numbers, and refuses to quote firm without evidence."

## Act 2 — prospect plays owner (4 min, the closer)

Behind the scenes the enquiry became a draft quote. Prospect (as
owner) receives:

> **Approval needed:** Consumer-unit replacement for [fictional
> customer], £400–500 labour. Reply APPROVE to send, EDIT with
> changes, or ignore — nothing sends without you.

Prospect replies **APPROVE**. Quote sends. Show the receipt on your
screen: `{"sent": True, "authorized": True, ...}` from the approvals
module — one-time, payload-bound, marked spent.

Then ask: "Reply nothing to the next one." A second draft arrives,
no reply, nothing sends. Show the pending receipt expiring.

What you narrate: "Your customers get instant answers. You get a
veto on everything. Silence means no."

## Act 3 — the window (2 min, optional if technical)

Prospect waits / you explain: outside 24h, free-form stops and only
approved templates send. Show the refusal receipt:
`"24h window closed — use a template"`. This is the Meta-compliance
moment — prospects who've been burned by bans recognize it.

## Lines to say out loud

- "All demo data is fictional — your install uses your prices."
- "This page is a concept demo with scripted answers" (if showing
  the static pages alongside — never let them think it's live AI).
- "Nothing sends without your tap. Ever. That's the whole product."

## After the meeting

- `record_optout(conn, to, "demo-ended")` — demo consent is
  single-session, never reused for marketing.
- Log objections in CRM (a "no" with a reason beats a polite maybe).
- If yes: T1 install checklist opens, promises-gate check runs first.
