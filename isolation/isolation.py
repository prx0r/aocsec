"""Isolation checklists + loss arithmetic. No network, no side effects."""

from __future__ import annotations

STEPS = (
    "dedicated_mailbox",
    "capped_spending",
    "no_overdraft",
    "txn_notifications",
    "work_calendar",
    "min_crm_role",
    "revocation_drilled",
)

_STEP_DETAIL = {
    "dedicated_mailbox": "Agent mailbox/alias exists; owner personal inbox out of scope.",
    "capped_spending": "Prepaid/virtual instrument with a verified low cap.",
    "no_overdraft": "No overdraft, credit line, or linked savings on the agent instrument.",
    "txn_notifications": "Per-transaction alerts reach the owner phone (tested).",
    "work_calendar": "Separate work-only calendar shared (not the full diary).",
    "min_crm_role": "CRM access is minimum-permission role, not owner/admin.",
    "revocation_drilled": "Owner revoked everything once in under 5 minutes.",
}


def onboarding_checklist() -> list[dict]:
    """Blank per-install checklist."""
    return [{"step": s, "detail": _STEP_DETAIL[s], "done": False}
            for s in STEPS]


def mark_done(checklist: list[dict], step: str) -> list[dict]:
    """Mark a step done. Unknown steps rejected."""
    if step not in [s["step"] for s in checklist]:
        raise ValueError(f"unknown step: {step}")
    return [{**s, "done": s["step"] == step or s["done"]} for s in checklist]


def isolation_status(checklist: list[dict]) -> dict:
    """Completion + what's left."""
    done = [s["step"] for s in checklist if s["done"]]
    left = [s["step"] for s in checklist if not s["done"]]
    return {"done": len(done), "total": len(checklist),
            "isolated": not left, "remaining": left}


def max_loss_estimate(spending_cap_gbp: float,
                      mailbox_contains_pii: bool,
                      calendar_is_full_diary: bool) -> dict:
    """Worst case if the agent is fully compromised today.

    Money is bounded by the cap. Data exposure is bounded by what's
    in scope. Anything unbounded here is a finding, not a number.
    """
    unbounded = []
    if mailbox_contains_pii:
        unbounded.append("mailbox holds personal data beyond job mail")
    if calendar_is_full_diary:
        unbounded.append("calendar exposes full diary")
    return {"max_money_loss_gbp": round(float(spending_cap_gbp), 2),
            "unbounded_risks": unbounded,
            "bounded": not unbounded,
            "action": ("Isolated: worst case is the cap."
                       if not unbounded else
                       "NOT isolated: fix unbounded risks first — "
                       + "; ".join(unbounded) + ".")}
