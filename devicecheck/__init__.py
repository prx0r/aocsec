"""Device + backup + account checklists for sole traders.

Loss and theft, not hackers: phones die, get stolen, or swim. Job
photos are dispute evidence; contacts are the business. These
checklists verify survival, not perfection.
"""

from __future__ import annotations


def device_checklist() -> list[dict]:
    """Phone/laptop survival checklist. Owner confirms each."""
    return [
        {"step": "screen_lock",
         "detail": "Screen lock on (PIN/biometric), 30s timeout. Without "
                   "this a lost phone is an open business.",
         "done": False},
        {"step": "encryption",
         "detail": "Device encryption on (default on modern iOS/Android; "
                   "verify, don't assume).",
         "done": False},
        {"step": "remote_wipe",
         "detail": "Find My / Find My Device enabled AND tested (locate "
                   "the phone from another device once).",
         "done": False},
        {"step": "work_profile",
         "detail": "Business email + bank app inside a work profile or "
                   "separate user account where supported.",
         "done": False},
        {"step": "sim_pin",
         "detail": "SIM PIN set (stops number theft via SIM swap on a "
                   "stolen phone).",
         "done": False},
    ]


def backup_checklist() -> list[dict]:
    """What survives a dead phone? Verify each, don't assume."""
    return [
        {"step": "photos_backed_up",
         "detail": "Job photos sync somewhere off-phone (cloud photos "
                   "or computer copy). Test: view one photo from another "
                   "device.",
         "done": False},
        {"step": "contacts_backed_up",
         "detail": "Business contacts in an account (Google/iCloud), not "
                   "phone-only storage.",
         "done": False},
        {"step": "price_book_copy",
         "detail": "Price book exists in two places (e.g. laptop + cloud).",
         "done": False},
        {"step": "2fa_recovery",
         "detail": "2FA recovery codes printed/stored somewhere that is "
                   "not the phone. Lose the phone AND the codes = locked "
                   "out of everything.",
         "done": False},
    ]


def mark_done(checklist: list[dict], step: str) -> list[dict]:
    """Mark a step done. Unknown steps rejected (no silent typos)."""
    if step not in [s["step"] for s in checklist]:
        raise ValueError(f"unknown step: {step}")
    return [{**s, "done": s["step"] == step or s["done"]} for s in checklist]


def checklist_status(checklist: list[dict]) -> dict:
    """Done count + what's left."""
    done = [s["step"] for s in checklist if s["done"]]
    left = [s["step"] for s in checklist if not s["done"]]
    return {"done": len(done), "total": len(checklist),
            "complete": not left, "remaining": left}
