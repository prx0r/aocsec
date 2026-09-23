"""Customer-authorized domain checks. Stdlib only.

Every check targets a domain the customer named. Timeouts are short,
request volume is trivial (one request per check). Findings are
observations with remediation, never exploit attempts.
"""

from __future__ import annotations

import socket
import ssl
import urllib.request
from datetime import datetime, timezone


def _fetch_headers(url: str, timeout: int = 15) -> tuple[int, dict, str]:
    """GET url, return (status, headers dict, final url)."""
    req = urllib.request.Request(url, headers={"User-Agent": "aionboard-audit/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, dict(resp.headers), resp.url


def check_https(domain: str, timeout: int = 15) -> dict:
    """Is the site served over HTTPS? Follows http->https upgrades."""
    try:
        status, _, final = _fetch_headers(f"http://{domain}", timeout)
        return {
            "check": "https",
            "pass": final.startswith("https://"),
            "severity": "high" if not final.startswith("https://") else "ok",
            "detail": f"final URL {final} (HTTP {status})",
            "remediation": None if final.startswith("https://") else (
                "Serve the site over HTTPS and redirect all HTTP traffic. "
                "Free certificates via Let's Encrypt."),
        }
    except Exception as e:
        return {"check": "https", "pass": False, "severity": "info",
                "detail": f"unreachable: {str(e)[:120]}",
                "remediation": "Site did not respond; check hosting/DNS."}


def check_tls_expiry(domain: str, timeout: int = 15) -> dict:
    """Days until the TLS certificate expires."""
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as tls:
                cert = tls.getpeercert()
        import datetime as _dt
        exp = _dt.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
        exp = exp.replace(tzinfo=timezone.utc)
        days = (exp - datetime.now(timezone.utc)).days
        if days < 0:
            sev, ok, rem = "critical", False, "Certificate EXPIRED. Renew immediately."
        elif days < 14:
            sev, ok, rem = "high", False, f"Certificate expires in {days} days. Renew now."
        elif days < 45:
            sev, ok, rem = "medium", True, f"Certificate expires in {days} days. Plan renewal."
        else:
            sev, ok, rem = "ok", True, None
        return {"check": "tls_expiry", "pass": ok, "severity": sev,
                "detail": f"expires {exp.date()} ({days} days)", "remediation": rem}
    except Exception as e:
        return {"check": "tls_expiry", "pass": False, "severity": "info",
                "detail": f"could not check: {str(e)[:120]}",
                "remediation": "Requires port 443 reachable."}


def check_headers(domain: str, timeout: int = 15) -> dict:
    """Security headers present on the homepage."""
    try:
        _, headers, _ = _fetch_headers(f"https://{domain}", timeout)
    except Exception:
        try:
            _, headers, _ = _fetch_headers(f"http://{domain}", timeout)
        except Exception as e:
            return {"check": "headers", "pass": False, "severity": "info",
                    "detail": f"unreachable: {str(e)[:120]}", "remediation": None}
    wanted = {
        "strict-transport-security": "HSTS — first visit still interceptable without preload",
        "content-security-policy": "CSP — limits XSS blast radius",
        "x-frame-options": "Clickjacking protection (or frame-ancestors in CSP)",
        "x-content-type-options": "Stops MIME-sniffing attacks",
        "referrer-policy": "Controls referrer leakage",
    }
    lowered = {k.lower(): v for k, v in headers.items()}
    missing = [h for h in wanted if h not in lowered]
    if not missing:
        return {"check": "headers", "pass": True, "severity": "ok",
                "detail": "all 5 security headers present", "remediation": None}
    return {"check": "headers", "pass": False, "severity": "medium",
            "detail": f"missing: {', '.join(missing)}",
            "remediation": "Add missing headers at hosting/CDN level. " +
                           "; ".join(f"{h}: {wanted[h]}" for h in missing)}


def check_domain(domain: str, timeout: int = 15) -> list[dict]:
    """Run all free checks against one customer-authorized domain."""
    domain = domain.strip().lower().removeprefix("https://").removeprefix("http://").split("/")[0]
    return [
        check_https(domain, timeout),
        check_tls_expiry(domain, timeout),
        check_headers(domain, timeout),
    ]


def free_check(domain: str, timeout: int = 15) -> dict:
    """Free tier: run checks, return findings with counts. No report file."""
    domain = domain.strip().lower().removeprefix("https://").removeprefix("http://").split("/")[0]
    findings = check_domain(domain, timeout)
    fails = [f for f in findings if not f["pass"] and f["severity"] != "info"]
    return {
        "domain": domain,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "findings": findings,
        "fail_count": len(fails),
        "worst_severity": max([f["severity"] for f in fails],
                              default="ok",
                              key=["ok", "info", "medium", "high", "critical"].index),
    }
