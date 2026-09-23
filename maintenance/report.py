"""Combined monthly report + certificate.

Takes runner results, renders one markdown report covering every leg,
attaches a self-hashing certificate. The certificate is the artifact
the customer keeps; verification needs no trust in us.
"""

from __future__ import annotations

from datetime import datetime, timezone

from audit_chain.certificates import Certificate


def build_monthly_report(business_name: str, results: dict) -> dict:
    """Render report + certificate from run_monthly() results."""
    now = datetime.now(timezone.utc).isoformat()
    checks = results.get("checks", {})
    lines = [
        f"# Monthly maintenance — {business_name}",
        f"Ran {now}. Plan: {results.get('plan', '?')}.",
        "",
        "Point-in-time evidence, not a guarantee. See exclusions at the end.",
        "",
    ]
    problems = 0
    for name, data in checks.items():
        lines.append(f"## {name}")
        if "error" in data:
            lines.append(f"Could not run: {data['error']}")
            problems += 1
        else:
            lines.append(_summarize(name, data))
            if _is_bad(name, data):
                problems += 1
        lines.append("")

    lines += [
        "## Exclusions",
        "",
        "- Anything not listed above was not checked.",
        "- Customer systems changed after this date are not covered.",
        "- Findings need human review before action; nothing here "
        "authorizes changes.",
        "",
        f"Open items: {problems}.",
    ]
    markdown = "\n".join(lines)
    cert = Certificate(
        cert_type="report",
        subject=f"monthly maintenance: {business_name}",
        evidence=[{"checks": sorted(checks), "problems": problems,
                   "at": now}]).seal()
    return {"markdown": markdown, "problems": problems,
            "certificate": cert.to_dict(),
            "digest": cert.certificate_hash}


def _summarize(name: str, data: dict) -> str:
    if name == "domain":
        return (f"{data.get('fail_count', '?')} failing checks, "
                f"worst {data.get('worst', '?')}.")
    if name == "email_auth":
        return (f"SPF {'pass' if data.get('spf') else 'FAIL'}, "
                f"DMARC {'pass' if data.get('dmarc') else 'FAIL'}.")
    if name == "legislation":
        return (f"{data.get('relevant_stale', '?')} stale rules relevant "
                f"({data.get('stale_total', '?')} total).")
    if name == "redteam":
        if "error" in data:
            return data["error"]
        return (f"Held {data.get('held', '?')}/{data.get('total', '?')}. "
                f"Breached: {', '.join(data.get('breached', [])) or 'none'}.")
    if name == "backups":
        return f"{data.get('fresh', '?')}/{data.get('total', '?')} fresh."
    return str(data)


def _is_bad(name: str, data: dict) -> bool:
    if "error" in data:
        return True
    if name == "domain":
        return (data.get("fail_count", 0) or 0) > 0
    if name == "email_auth":
        return not (data.get("spf") and data.get("dmarc"))
    if name == "legislation":
        return (data.get("relevant_stale", 0) or 0) > 0
    if name == "redteam":
        return bool(data.get("breached"))
    if name == "backups":
        return data.get("fresh", 0) != data.get("total", 0)
    return False
