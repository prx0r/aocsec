"""DNS TXT lookups over HTTPS (dns.google, free, no key)."""

from __future__ import annotations

import json
import urllib.request


def _doh(name: str, rrtype: str = "TXT", timeout: int = 15) -> list[str]:
    """All TXT strings for a name. Empty list when none/error."""
    import urllib.parse
    qs = urllib.parse.urlencode({"name": name, "type": rrtype})
    req = urllib.request.Request(
        f"https://dns.google/resolve?{qs}",
        headers={"Accept": "application/json",
                 "User-Agent": "aocsec-emailsec/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
    except Exception:
        return []
    out = []
    for ans in data.get("Answer", []) or []:
        if ans.get("type") == 16:  # TXT
            out.append(str(ans.get("data", "")).strip('"'))
    return out


def spf_record(domain: str, timeout: int = 15) -> dict:
    """SPF record for a domain. Missing = anyone can spoof you."""
    recs = [r for r in _doh(domain, timeout=timeout)
            if r.lower().startswith("v=spf1")]
    if not recs:
        return {"check": "spf", "pass": False, "severity": "high",
                "detail": "no SPF record: anyone can send mail as your domain",
                "remediation": "Publish a TXT record, e.g. "
                               "'v=spf1 include:_spf.google.com ~all' "
                               "for Google Workspace (adapt to your provider)."}
    strict = recs[0].rstrip().endswith("-all")
    return {"check": "spf", "pass": True, "severity": "ok",
            "detail": f"present ({'strict -all' if strict else 'softfail ~all'})",
            "remediation": None if strict else
            "Consider strict '-all' once legitimate senders are covered."}


def dmarc_record(domain: str, timeout: int = 15) -> dict:
    """DMARC policy at _dmarc.domain. Missing = spoofing unreported."""
    recs = [r for r in _doh(f"_dmarc.{domain}", timeout=timeout)
            if r.lower().startswith("v=dmarc1")]
    if not recs:
        return {"check": "dmarc", "pass": False, "severity": "high",
                "detail": "no DMARC record: spoofed mail is never reported",
                "remediation": "Publish '_dmarc' TXT starting "
                               "'v=DMARC1; p=none; rua=mailto:you@domain' "
                               "then tighten to quarantine/reject."}
    policy = "none"
    for part in recs[0].split(";"):
        if part.strip().lower().startswith("p="):
            policy = part.split("=", 1)[1].strip()
    return {"check": "dmarc", "pass": True, "severity": "ok",
            "detail": f"present (policy p={policy})",
            "remediation": None if policy in ("quarantine", "reject") else
            "Move from p=none to quarantine, then reject, once reviewed."}


def dkim_record(domain: str, selector: str = "google",
                timeout: int = 15) -> dict:
    """DKIM key at <selector>._domainkey.domain. Selector varies by
    provider (google, k1, selector1...); unknown selector = informational."""
    recs = _doh(f"{selector}._domainkey.{domain}", timeout=timeout)
    if not recs:
        return {"check": "dkim", "pass": False, "severity": "info",
                "detail": f"no key at {selector}._domainkey "
                          "(selector may differ by provider)",
                "remediation": "Enable DKIM signing in your mail provider "
                               "and publish the key it gives you."}
    return {"check": "dkim", "pass": True, "severity": "ok",
            "detail": f"key present at {selector}._domainkey",
            "remediation": None}
