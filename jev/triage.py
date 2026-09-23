"""Confidence-gated triage over injected judge callables.

judge(tool_name, arguments) -> dict with the jev-mcp result shape.
Production: JevMCP.call. Tests: stubs. Policy:

- confidence >= floor: accept the judgment, record it.
- confidence < floor (or missing): escalate to human review.
- Nothing here executes, files, pays, or sends. Ever.
"""

from __future__ import annotations

from typing import Any, Callable

CONFIDENCE_FLOOR = 0.75

JudgeFn = Callable[[str, dict], dict]


def _confidence(result: dict) -> float:
    for key in ("confidence", "score", "probability"):
        try:
            return float(result.get(key, 0.0))
        except (TypeError, ValueError):
            continue
    return 0.0


def classify_alerts(alerts: list[dict], judge: JudgeFn,
                    floor: float = CONFIDENCE_FLOOR) -> dict:
    """Bucket alerts into act_now / watch / noise / needs_human.

    Each alert: {"source_id": str, "status": str, "age": str, ...}.
    """
    buckets: dict[str, list] = {
        "act_now": [], "watch": [], "noise": [], "needs_human": []}
    for alert in alerts:
        try:
            res = judge("jev_classify", {
                "items": [f"{alert.get('source_id')}:{alert.get('status')}"],
                "classes": ["act_now", "watch", "noise"]})
            label = str(res.get("label", res.get("class", "watch")))
            conf = _confidence(res)
        except Exception as e:
            buckets["needs_human"].append({**alert, "reason": f"judge error: {e}"})
            continue
        if conf < floor or label not in buckets:
            buckets["needs_human"].append(
                {**alert, "reason": f"low confidence ({conf:.2f})"})
        else:
            buckets[label].append({**alert, "confidence": round(conf, 2)})
    return buckets


def verify_claims(claims: list[dict], judge: JudgeFn,
                  floor: float = CONFIDENCE_FLOOR) -> list[dict]:
    """Check claims against cited evidence. Each claim:
    {"claim": str, "evidence": str}. Returns verdicts; low confidence
    becomes needs_human, never a pass.
    """
    out = []
    for claim in claims:
        try:
            res = judge("jev_verify", {
                "claim": claim.get("claim", ""),
                "evidence": claim.get("evidence", "")})
            conf = _confidence(res)
            verdict = str(res.get("verdict", "unknown"))
        except Exception as e:
            out.append({**claim, "verdict": "needs_human",
                        "reason": f"judge error: {e}"})
            continue
        if conf < floor:
            out.append({**claim, "verdict": "needs_human",
                        "reason": f"low confidence ({conf:.2f})"})
        else:
            out.append({**claim, "verdict": verdict,
                        "confidence": round(conf, 2)})
    return out


def gate_completion(diff_summary: str, test_evidence: str, judge: JudgeFn,
                    floor: float = CONFIDENCE_FLOOR) -> dict:
    """Ship/no-ship gate for a completed task. Default: no-ship.

    Returns {"ship": bool, "reasons": [...]}. Anything uncertain,
    errored, or low-confidence resolves to no-ship with reasons.
    """
    try:
        res = judge("jev_gate", {"diff": diff_summary,
                                 "tests": test_evidence})
        conf = _confidence(res)
        approved = bool(res.get("approved", res.get("ship", False)))
    except Exception as e:
        return {"ship": False, "reasons": [f"judge error: {e}"]}
    if not approved or conf < floor:
        reasons = [f"confidence {conf:.2f} below floor {floor}"] \
            if conf < floor else []
        reasons += [str(r) for r in res.get("reasons", [])
                    if not approved]
        return {"ship": False,
                "reasons": reasons or ["not approved by judge"]}
    return {"ship": True, "confidence": round(conf, 2),
            "reasons": [str(r) for r in res.get("reasons", [])]}
