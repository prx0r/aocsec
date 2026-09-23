# Form defense (Turnstile)

> Enquiry/booking forms are the most-attacked surface a trade business
> owns (spam, fake bookings, slot exhaustion). Fix: Cloudflare Turnstile.

## Why Turnstile and not CAPTCHA/reCAPTCHA

- Free, unlimited challenges, no traffic proxying required.
- No puzzles for real users; WCAG 2.2 AAA.
- Server-side siteverify keeps the decision off-client.
- Secret key stays server-side. Never in client code.

## Integration pattern (any form)

1. Cloudflare dashboard → Turnstile → new widget per environment
   (dev/staging/prod separate). Note sitekey + secret.
2. Client: widget div with `data-sitekey`, submit button disabled until
   `data-callback` fires.
3. Server: on POST, send token + secret to
   `https://challenges.cloudflare.com/turnstile/v0/siteverify` BEFORE
   processing the form. Reject on failure. Verify AFTER the user fills
   the form (never before — avoids token-replay bypass).
4. Hostname-restrict widgets to owned domains.

## Where it applies here

- aionboard enquiry/booking forms (per-install task).
- Any customer contact form we touch during onboarding.
- NOT a substitute for approval gates — bots stopped at the door,
  malicious instructions still face the red-team-tested agent layer.

## Checklist

- [ ] Every public form has a widget
- [ ] Secret key server-side only, rotatable via dashboard/API
- [ ] siteverify failure path tested (rejects submission)
- [ ] Separate widgets per environment
