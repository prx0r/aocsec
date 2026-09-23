"""Monthly runner — execute a plan's checks for one customer.

Inputs are explicit (domain, vertical, ledgers); nothing is discovered
by scanning third parties. Red-team runs against a supplied responder
(the customer's assistant config under test). Results feed the monthly
report + certificate.
"""

from __future__ import annotations

from .plans import plan_for


def run_monthly(*, business_id: str, plan_id: str, domain: str = "",
                vertical: str = "", responder=None) -> dict:
    """Run every check in the plan. Returns structured results.

    responder: callable(message, session_id)->str for the redteam leg.
    Required when the plan includes redteam; otherwise unused.
    """
    plan = plan_for(plan_id)
    results: dict = {"business_id": business_id, "plan": plan_id,
                     "checks": {}}

    if "domain" in plan["checks"] and domain:
        from security_audit import free_check
        try:
            fc = free_check(domain, timeout=15)
            results["checks"]["domain"] = {
                "fail_count": fc["fail_count"],
                "worst": fc["worst_severity"]}
        except Exception as e:
            results["checks"]["domain"] = {"error": str(e)[:120]}

    if "email_auth" in plan["checks"] and domain:
        from emailsec import dmarc_record, spf_record
        results["checks"]["email_auth"] = {
            "spf": spf_record(domain)["pass"],
            "dmarc": dmarc_record(domain)["pass"]}

    if "legislation_stale" in plan["checks"]:
        from legislation.graph import build_graph, stale_rules
        stale = stale_rules(build_graph())
        mine = [s for s in stale
                if not vertical or vertical in [
                    a.lower() for a in s.applies_to] or not s.applies_to]
        results["checks"]["legislation"] = {
            "stale_total": len(stale), "relevant_stale": len(mine)}

    if "redteam" in plan["checks"]:
        if responder is None:
            results["checks"]["redteam"] = {
                "error": "responder required for redteam leg"}
        else:
            from redteam import run_suite
            import tempfile
            with tempfile.TemporaryDirectory() as tmp:
                summary = run_suite(responder, out_dir=tmp)
            results["checks"]["redteam"] = {
                "held": summary["held"], "total": summary["total"],
                "breached": summary["breached"]}

    if "backups" in plan["checks"]:
        from backups import check_freshness
        fresh = check_freshness()
        results["checks"]["backups"] = {
            "fresh": fresh["fresh"], "total": fresh["total"]}

    try:
        from audit import audit as _audit
        _audit(actor="maintenance", action="run.completed",
               business_id=business_id,
               detail={"plan": plan_id,
                       "legs": sorted(results["checks"])})
    except Exception:
        pass
    return results
