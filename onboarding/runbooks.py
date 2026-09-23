"""Per-vertical install runbooks — what "installed" means per trade.

Each runbook combines: legislation obligations for the vertical
(graph), security checklist items that matter most for it
(vertical-security profiles), and the universal baseline (accounts
package, isolation, email auth). Steps map to pipeline evidence keys
so completing a runbook satisfies the installed gate.
"""

from __future__ import annotations

# Universal baseline: every install, every vertical.
BASELINE_STEPS: tuple[dict, ...] = (
    {"id": "accounts", "detail": "Password manager + 2FA on email first."},
    {"id": "email_auth", "detail": "SPF/DKIM/DMARC checked for their domain."},
    {"id": "device_backup", "detail": "Screen lock, encryption, photo backup verified."},
    {"id": "approvals", "detail": "Approval receipts explained; owner grants once supervised."},
    {"id": "handoff", "detail": "'Talk to a human' path demonstrated."},
)

# Vertical extras: (legislation domain or topic to pull, security focus).
VERTICAL_EXTRAS: dict[str, dict] = {
    "electrician": {
        "legislation_topics": ["Part P", "EICR", "EV charger", "CIS"],
        "security_focus": ["quote_fraud", "approval_bypass"],
        "extra_steps": [
            {"id": "part_p_check",
             "detail": "Confirm competent-person registration status for notifiable work."},
        ],
    },
    "beauty": {
        "legislation_topics": ["patch test", "chemical"],
        "security_focus": ["pii_leakage"],
        "extra_steps": [
            {"id": "health_data_rule",
             "detail": "No allergy/patch-test details in prompts, tickets, or photos without explicit per-item consent."},
        ],
    },
    "hair": {
        "legislation_topics": ["patch test", "chemical"],
        "security_focus": ["pii_leakage"],
        "extra_steps": [
            {"id": "health_data_rule",
             "detail": "Same as beauty: patch-test and chemical data stays out of prompts."},
        ],
    },
    "lashes": {
        "legislation_topics": ["patch test", "adhesive"],
        "security_focus": ["pii_leakage"],
        "extra_steps": [
            {"id": "health_data_rule",
             "detail": "Eye-reaction and allergy data never enters prompts or tickets."},
        ],
    },
    "nails": {
        "legislation_topics": ["chemical", "salon"],
        "security_focus": ["pii_leakage"],
        "extra_steps": [
            {"id": "health_data_rule",
             "detail": "Skin-condition notes stay out of prompts and tickets."},
        ],
    },
    "cleaners": {
        "legislation_topics": ["COSHH", "chemical"],
        "security_focus": ["pii_leakage", "cross_session"],
        "extra_steps": [
            {"id": "access_data_rule",
             "detail": "Keys, alarm codes, and access routines never enter prompts, tickets, or logs."},
            {"id": "coshh_check",
             "detail": "Cleaning-chemical safety data sheets on file."},
        ],
    },
    "gardeners-window-cleaners": {
        "legislation_topics": ["waste", "pesticide"],
        "security_focus": ["booking_manipulation"],
        "extra_steps": [
            {"id": "waste_carrier_check",
             "detail": "Waste carrier registration confirmed for green waste."},
        ],
    },
    "dog-groomers": {
        "legislation_topics": ["animal", "welfare"],
        "security_focus": ["pii_leakage"],
        "extra_steps": [
            {"id": "incident_consent",
             "detail": "Pet-injury photo and vet-report consent process documented."},
        ],
    },
    "car-detailers": {
        "legislation_topics": ["COSHH", "chemical"],
        "security_focus": ["booking_manipulation"],
        "extra_steps": [
            {"id": "custody_docs",
             "detail": "Before/after vehicle condition photos are standard on every job."},
        ],
    },
    "driving-instructors": {
        "legislation_topics": ["ADI", "instructor"],
        "security_focus": ["pii_leakage", "cross_session"],
        "extra_steps": [
            {"id": "adi_check",
             "detail": "ADI registration verified and badge displayed."},
            {"id": "safeguarding_note",
             "detail": "Young-pupil safeguarding awareness covered (no DBS rule asserted)."},
        ],
    },
    "weddings": {
        "legislation_topics": ["deposit", "contract"],
        "security_focus": ["invoice_fraud", "quote_fraud"],
        "extra_steps": [
            {"id": "deposit_workflow",
             "detail": "Deposit terms written; supplier invoice verification active (highest fraud exposure)."},
        ],
    },
}


def runbook_for(vertical: str) -> dict:
    """Install runbook for a vertical: baseline + extras.

    Unknown verticals get the baseline only (never refuse outright —
    flag for review instead).
    """
    extra = VERTICAL_EXTRAS.get(vertical, {})
    steps = [{"id": s["id"], "detail": s["detail"]} for s in BASELINE_STEPS]
    steps += [{"id": s["id"], "detail": s["detail"]}
              for s in extra.get("extra_steps", [])]
    return {
        "vertical": vertical,
        "known": vertical in VERTICAL_EXTRAS,
        "legislation_topics": list(extra.get("legislation_topics", [])),
        "security_focus": list(extra.get("security_focus", [])),
        "steps": steps,
    }
