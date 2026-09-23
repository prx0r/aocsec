"""Yes-flow orchestrator — what happens after "yes", in order.

Stages run in sequence; the first block stops the flow with reasons.
Nothing here contacts customers, sends messages, or spends money —
it records state transitions and produces the work list for humans.

Flow: consent -> eligibility -> isolation -> install -> verify ->
maintenance. Each stage reads evidence recorded by whoever did the
work (human installer, usually) and advances the pipeline.
"""

from __future__ import annotations

from . import pipeline
from .runbooks import runbook_for


def run_yes_flow(connection, business_id: str, *, consent_basis: str,
                 eligibility: dict, isolation_done: list[str],
                 install_done: list[str],
                 verify_evidence: dict | None = None,
                 plan_id: str = "") -> dict:
    """Execute the yes-flow. Returns stage-by-stage receipt.

    Callers supply evidence gathered by humans:
    - eligibility: result of business_agent.gate_install()
    - isolation_done / install_done: completed step id lists
    - verify_evidence: {"redteam": "green ...", ...}
    - plan_id: maintenance plan for the final stage
    """
    log = []
    st = pipeline.pipeline_status(connection, business_id)

    # 1. consent (advances interested -> consent_recorded)
    if st["stage"] == "interested":
        st = pipeline.record_consent(connection, business_id,
                                     basis=consent_basis)
        log.append(("consent", st["stage"]))
    elif st["stage"] == "contacted":
        # record interest first, then consent
        pipeline.record_evidence(connection, business_id, "interested",
                                 "positive_response", "yes-flow")
        st = pipeline.advance(connection, business_id)
        st = pipeline.record_consent(connection, business_id,
                                     basis=consent_basis)
        log.append(("consent", st["stage"]))

    # 2. eligibility
    if st["stage"] == "consent_recorded":
        if eligibility.get("go"):
            pipeline.record_evidence(connection, business_id, "eligible",
                                     "eligibility_pass", "gate_install green")
            st = pipeline.advance(connection, business_id)
            log.append(("eligibility", st["stage"]))
        else:
            return {"business_id": business_id, "stopped_at": st["stage"],
                    "reason": "eligibility failed",
                    "detail": eligibility, "log": log}

    # 3. isolation
    if st["stage"] == "eligible":
        from isolation import STEPS, isolation_status, mark_done, onboarding_checklist
        cl = onboarding_checklist()
        for step in isolation_done:
            try:
                cl = mark_done(cl, step)
            except ValueError:
                return {"business_id": business_id,
                        "stopped_at": st["stage"],
                        "reason": f"unknown isolation step: {step}",
                        "log": log}
        status = isolation_status(cl)
        if status["isolated"]:
            pipeline.record_evidence(connection, business_id, "isolated",
                                     "isolation_complete", "7/7 steps")
            st = pipeline.advance(connection, business_id)
            log.append(("isolation", st["stage"]))
        else:
            return {"business_id": business_id, "stopped_at": st["stage"],
                    "reason": "isolation incomplete",
                    "detail": status["remaining"], "log": log}

    # 4. install (vertical runbook)
    if st["stage"] == "isolated":
        vertical = _vertical_of(connection, business_id)
        rb = runbook_for(vertical)
        needed = [s["id"] for s in rb["steps"]]
        missing = [s for s in needed if s not in install_done]
        if missing:
            return {"business_id": business_id, "stopped_at": st["stage"],
                    "reason": "install incomplete",
                    "detail": {"missing": missing,
                               "security_focus": rb["security_focus"]},
                    "log": log}
        pipeline.record_evidence(connection, business_id, "installed",
                                 "install_checklist",
                                 f"{len(needed)}/{len(needed)} steps")
        st = pipeline.advance(connection, business_id)
        log.append(("install", st["stage"]))

    # 5. verify
    if st["stage"] == "installed":
        verify_evidence = verify_evidence or {}
        if verify_evidence.get("redteam_green") and \
                verify_evidence.get("audit_clean"):
            pipeline.record_evidence(connection, business_id, "verified",
                                     "verification_evidence",
                                     "redteam green + audit clean")
            st = pipeline.advance(connection, business_id)
            log.append(("verify", st["stage"]))
        else:
            return {"business_id": business_id, "stopped_at": st["stage"],
                    "reason": "verification incomplete",
                    "detail": "need redteam_green + audit_clean evidence",
                    "log": log}

    # 6. maintenance
    if st["stage"] == "verified":
        if not plan_id:
            return {"business_id": business_id, "stopped_at": st["stage"],
                    "reason": "no maintenance plan selected",
                    "detail": "care or care_plus", "log": log}
        try:
            from maintenance import plan_for
            plan_for(plan_id)
        except ValueError as e:
            return {"business_id": business_id, "stopped_at": st["stage"],
                    "reason": str(e), "log": log}
        pipeline.record_evidence(connection, business_id, "maintenance",
                                 "plan_id", plan_id)
        st = pipeline.advance(connection, business_id)
        log.append(("maintenance", st["stage"]))

    return {"business_id": business_id, "stage": st["stage"],
            "complete": st["stage"] == "maintenance", "log": log}


def _vertical_of(connection, business_id: str) -> str:
    row = connection.execute(
        "SELECT vertical FROM ob_prospects WHERE business_id=?",
        (business_id,)).fetchone()
    return row[0] if row else ""
