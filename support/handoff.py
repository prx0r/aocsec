"""Handoff protocol — bot to human without repeats.

Three trigger kinds (industry pattern):
- explicit: customer asks for a human.
- implicit: loops (same question twice), reformulation, urgency words,
  complexity beyond scope.
- policy: money, legal exposure, safety, reputation — always human.

Handoff compiles a context package: what they want, what was tried,
what's unresolved, plus business identity. The human starts from the
package, never from "please repeat yourself".
"""

from __future__ import annotations

HANDOFF_TRIGGERS = {
    "explicit": ("talk to a human", "human please", "real person",
                 "call me", "phone me"),
    "urgency": ("urgent", "asap", "emergency", "ridiculous",
                "already explained", "going in circles"),
    "policy": (),  # policy triggers come from flags below, not keywords
}

POLICY_TOPICS = ("payment", "refund", "legal", "court", "safety",
                 "insurance claim", "cancel contract", "complaint")


def should_escalate(message: str, *, turn_count: int = 0,
                    repeats: int = 0, topics: list[str] | None = None) -> dict:
    """Decide whether to hand off. Returns {escalate, reason}."""
    m = message.lower()
    for phrase in HANDOFF_TRIGGERS["explicit"]:
        if phrase in m:
            return {"escalate": True, "reason": "explicit request"}
    for phrase in HANDOFF_TRIGGERS["urgency"]:
        if phrase in m:
            return {"escalate": True, "reason": "urgency signal"}
    for topic in (topics or []):
        if topic.lower() in POLICY_TOPICS:
            return {"escalate": True,
                    "reason": f"policy topic: {topic}"}
    if repeats >= 2:
        return {"escalate": True,
                "reason": f"loop detected ({repeats} repeats)"}
    if turn_count >= 8:
        return {"escalate": True,
                "reason": f"long conversation ({turn_count} turns)"}
    return {"escalate": False, "reason": "within scope"}


def build_context_package(*, customer_wants: str, tried: list[str],
                          unresolved: str, business_id: str,
                          business_name: str = "",
                          transcript_tail: list[str] | None = None,
                          systems: list[dict] | None = None,
                          qualifications: list[str] | None = None,
                          last_user_message_at: str = "",
                          channel: str = "") -> dict:
    """Compile the handoff package. Max 3-sentence summary + facts."""
    pkg = {
        "business_id": business_id,
        "business_name": business_name,
        "wants": customer_wants[:300],
        "tried": [t[:200] for t in tried[-5:]],
        "unresolved": unresolved[:300],
        "transcript_tail": (transcript_tail or [])[-10:],
        "systems": [{"name": s.get("name", ""),
                     "kind": s.get("kind", "")} for s in (systems or [])],
        "qualifications": list(qualifications or []),
        "instruction": "Start from this package. Do not ask the customer "
                       "to repeat anything above.",
    }
    if channel.lower() == "whatsapp" and last_user_message_at:
        from business_agent.window import window_status
        window = window_status(last_user_message_at)
        pkg["channel_constraint"] = (
            f"WhatsApp window {window['window']}: {window['may_send']}. "
            f"{window['note']}")
    return pkg
