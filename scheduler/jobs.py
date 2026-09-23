"""Scheduled jobs registry. Each job: cadence, payload builder, template.

Cadences: daily, weekly, monthly, quarterly. Payload builders return
lists of per-business work items; the runner turns customer-facing
ones into WhatsApp template payloads via whatsapp.build_message.
"""

from __future__ import annotations

JOB_DEFS: dict[str, dict] = {
    "sla_watch": {
        "cadence": "daily",
        "description": "Overdue tickets get draft nudges.",
        "template": None,  # internal: nudges go to the owner dashboard
    },
    "review_due": {
        "cadence": "weekly",
        "description": "Quarterly reviews coming due get a heads-up.",
        "template": "review_due",
    },
    "cert_expiry": {
        "cadence": "weekly",
        "description": "Qualifications, insurance, registrations expiring soon.",
        "template": "cert_expiring",
    },
    "maintenance_run": {
        "cadence": "monthly",
        "description": "Full maintenance engine run + certified report.",
        "template": "maintenance_done",
    },
    "opportunity_digest": {
        "cadence": "weekly",
        "description": "Scored local opportunities for opted-in businesses.",
        "template": "opportunity_digest",
    },
    "backup_check": {
        "cadence": "daily",
        "description": "Backup freshness verification. Silent unless stale.",
        "template": None,
    },
}


def due_jobs(cadence: str) -> list[dict]:
    """Job defs for one cadence tick (e.g. a daily timer calls 'daily')."""
    return [{"id": jid, **spec} for jid, spec in JOB_DEFS.items()
            if spec["cadence"] == cadence]


def job_ids() -> list[str]:
    return sorted(JOB_DEFS)
