"""Message templates — pre-approved texts by category.

WhatsApp rule: free-form inside 24h of user's last message, approved
templates outside it. These templates cover every message our system
sends. Anything not matching a template needs human drafting +
approval receipt. No ad-hoc agent prose goes to customers.
"""

from __future__ import annotations

TEMPLATES: dict[str, dict] = {
    "review_due": {
        "category": "utility",
        "body": "Hi {name} — your quarterly security review is due. "
                "Reply YES and we'll run the checks this week, or pick a time: {link}",
        "variables": ["name", "link"],
    },
    "cert_expiring": {
        "category": "utility",
        "body": "Hi {name} — your {item} expires on {date}. "
                "Reply RENEW and we'll sort it, or ignore if already handled.",
        "variables": ["name", "item", "date"],
    },
    "appointment_reminder": {
        "category": "utility",
        "body": "Hi {name} — reminder: {job} on {when} at {where}. "
                "Reply CONFIRM, or RESCHEDULE to move it.",
        "variables": ["name", "job", "when", "where"],
    },
    "sla_breach_owner": {
        "category": "utility",
        "body": "Heads up: ticket #{ticket} ({subject}) is past SLA. "
                "Reply ACK to take it, or ESCALATE for help.",
        "variables": ["ticket", "subject"],
    },
    "maintenance_done": {
        "category": "utility",
        "body": "Hi {name} — this month's maintenance is done: {passed}/{total} "
                "checks green. Full report: {link}",
        "variables": ["name", "passed", "total", "link"],
    },
    "opportunity_digest": {
        "category": "utility",
        "body": "Hi {name} — {count} new opportunities near {area} this week. "
                "Reply LIST to see them, STOP to pause these.",
        "variables": ["name", "count", "area"],
    },
    "auth_code": {
        "category": "authentication",
        "body": "Your verification code is {code}. It expires in 10 minutes. "
                "Never share it.",
        "variables": ["code"],
    },
}


def get_template(name: str) -> dict:
    """Fetch a template. Unknown names rejected (no free-form fallback)."""
    if name not in TEMPLATES:
        raise ValueError(f"unknown template: {name}. "
                         f"Known: {sorted(TEMPLATES)}")
    return {"name": name, **TEMPLATES[name]}


def render_template(name: str, variables: dict) -> str:
    """Fill a template. Missing variables rejected, never blanked."""
    t = get_template(name)
    missing = [v for v in t["variables"] if v not in variables]
    if missing:
        raise ValueError(f"missing variables for {name}: {missing}")
    text = t["body"]
    for var in t["variables"]:
        text = text.replace("{" + var + "}", str(variables[var]))
    if "{" in text and "}" in text[text.index("{"):]:
        raise ValueError(f"unfilled placeholder remains in {name}")
    return text
