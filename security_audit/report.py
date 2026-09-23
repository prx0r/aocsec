"""Paid-tier report builder: findings + red-team + remediation, digest-pinned.

The report is a dated markdown document: what was checked, what failed,
how to fix each item, and the red-team evidence summary. It is evidence
and advice — never a guarantee, never a pentest certificate.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from .checks import free_check


def build_report(
    domain: str,
    *,
    business_name: str = "",
    redteam_summary: dict | None = None,
    timeout: int = 15,
) -> dict:
    """Run free checks (+ optional red-team summary) and build a report.

    Returns {"markdown": str, "digest": str, "summary": dict}.
    """
    result = free_check(domain, timeout)
    now = result["checked_at"]
    lines = [
        f"# Security report — {business_name or domain}",
        f"Checked {now}. Scope: {domain} (customer-authorized).",
        "",
        "This report lists observations and fixes. It is not a penetration "
        "test certificate and does not guarantee security.",
        "",
        "## Findings",
        "",
    ]
    if not result["findings"]:
        lines.append("No checks ran.")
    for f in result["findings"]:
        mark = "PASS" if f["pass"] else f["severity"].upper()
        lines.append(f"### [{mark}] {f['check']}")
        lines.append(f"{f['detail']}")
        if f.get("remediation"):
            lines.append(f"Fix: {f['remediation']}")
        lines.append("")

    if redteam_summary is not None:
        lines += [
            "## Assistant red-team",
            "",
            f"Held {redteam_summary.get('held', '?')}/"
            f"{redteam_summary.get('total', '?')} attacks. "
            f"Evidence: `{redteam_summary.get('evidence', 'n/a')}`.",
        ]
        if redteam_summary.get("breached"):
            lines.append(f"Breached: {', '.join(redteam_summary['breached'])}")
        lines.append("")

    lines += [
        "## What this doesn't cover",
        "",
        "- Anything you didn't authorize us to check.",
        "- Your email, suppliers, or third-party accounts.",
        "- Future changes to the site after this date.",
        "",
        f"Summary: {result['fail_count']} failing checks, "
        f"worst severity {result['worst_severity']}.",
    ]
    markdown = "\n".join(lines)
    digest = "sha256:" + hashlib.sha256(markdown.encode()).hexdigest()
    return {"markdown": markdown, "digest": digest,
            "summary": {"domain": domain, "checked_at": now,
                        "fail_count": result["fail_count"],
                        "worst_severity": result["worst_severity"]}}
