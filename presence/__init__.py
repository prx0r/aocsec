"""Online-presence ownership checklist: GBP, socials, reviews.

Hijack and extortion vectors, not completeness scoring. Each item is
verifiable by the owner in 5 minutes.
"""

from __future__ import annotations


def presence_checklist() -> list[dict]:
    return [
        {"step": "gbp_ownership",
         "detail": "Google Business Profile claimed under an account you "
                   "control (not an ex-employee, agency, or 'someone who "
                   "set it up once'). Check the primary owner email.",
         "done": False},
        {"step": "gbp_recovery",
         "detail": "Recovery email + phone on the Google account are "
                   "yours and current.",
         "done": False},
        {"step": "social_admins",
         "detail": "Facebook/Instagram pages list only current people as "
                   "admins. Remove ex-staff, old agencies, unknown names.",
         "done": False},
        {"step": "social_2fa",
         "detail": "2FA on every account that can post as the business.",
         "done": False},
        {"step": "review_watch",
         "detail": "Know where reviews land (Google, Checkatrade, Trustpilot) "
                   "and who gets notified. Fake-review extortion starts "
                   "with 'pay for removal' — never pay, report instead.",
         "done": False},
        {"step": "domain_control",
         "detail": "Domain registered in your name/account with auto-renew "
                   "on. An expired domain takes email + site with it.",
         "done": False},
    ]


def mark_done(checklist: list[dict], step: str) -> list[dict]:
    if step not in [s["step"] for s in checklist]:
        raise ValueError(f"unknown step: {step}")
    return [{**s, "done": s["step"] == step or s["done"]} for s in checklist]


def checklist_status(checklist: list[dict]) -> dict:
    done = [s["step"] for s in checklist if s["done"]]
    left = [s["step"] for s in checklist if not s["done"]]
    return {"done": len(done), "total": len(checklist),
            "complete": not left, "remaining": left}
