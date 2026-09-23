"""Agent-managed support loop.

The agent runs the queue; humans own outcomes. Each round, per business:

1. Triage new tickets (Jev classify when available, keyword fallback).
2. Draft first responses from the KB (drafts, never sent).
3. Watch SLA breaches (draft nudges, never sent).
4. Flag handoff candidates (policy topics, loops, explicit asks).

Output is always proposals + drafts + flags. Sending, resolving, and
priority changes that affect SLAs stay human. The loop is idempotent:
re-running with no changes produces no new actions.
"""

from __future__ import annotations

import sqlite3

from .business import get_business, list_businesses
from .handoff import build_context_package, should_escalate
from .kb import search_articles
from .tickets import get_ticket, list_overdue, set_status

TRIAGE_KEYWORDS = {
    "urgent": "critical",
    "outage": "critical",
    "down": "high",
    "broken": "high",
    "invoice": "high",
    "payment": "high",
    "refund": "high",
    "question": "low",
    "how do": "low",
}


def triage_ticket(connection: sqlite3.Connection, ticket_id: int,
                  judge=None) -> dict:
    """Suggest priority + KB-backed draft for one ticket.

    judge: optional callable(tool, args)->dict (Jev jev_classify shape).
    Without a judge, keyword tiers apply. Returns a proposal, and — only
    with an explicit approval receipt id passed in — applies priority.
    """
    t = get_ticket(connection, ticket_id)
    text = f"{t['subject']} {t['detail']}".lower()

    suggested, confidence, source = "medium", 0.0, "keyword-default"
    if judge is not None:
        try:
            res = judge("jev_classify", {
                "items": [f"{t['subject']}:{t['detail']}"[:500]],
                "classes": ["critical", "high", "medium", "low"]})
            label = str(res.get("label", res.get("class", "")))
            conf = float(res.get("confidence", res.get("score", 0.0)))
            if label in ("critical", "high", "medium", "low") and conf >= 0.75:
                suggested, confidence, source = label, round(conf, 2), "jev"
        except Exception as e:
            return {"ticket_id": ticket_id, "proposal": "needs_human",
                    "reason": f"judge error: {e}"}
    if source == "keyword-default":
        for kw, prio in TRIAGE_KEYWORDS.items():
            if kw in text:
                suggested = prio
                break

    vertical = ""
    biz = get_business(connection, t["business_id"])
    if biz:
        vertical = biz.get("vertical", "")
    drafts = search_articles(connection, t["subject"], vertical=vertical,
                             limit=3)
    return {"ticket_id": ticket_id, "proposal": suggested,
            "confidence": confidence, "source": source,
            "draft_hint": drafts[0]["title"] if drafts else "",
            "draft_ids": [d["id"] for d in drafts],
            "note": "Proposal only. Priority changes and replies need "
                    "human approval."}


def sla_watch(connection: sqlite3.Connection) -> list[dict]:
    """Overdue tickets with draft nudge text. Nudges are drafts."""
    out = []
    for t in list_overdue(connection):
        out.append({
            "ticket_id": t["id"],
            "business_id": t["business_id"],
            "priority": t["priority"],
            "status": t["status"],
            "draft_nudge": (
                f"Ticket #{t['id']} ({t['subject'][:60]}) is past SLA. "
                f"Suggested next step: review and reply or re-prioritize. "
                f"[DRAFT — human sends]"),
        })
    return out


def run_support_round(connection: sqlite3.Connection,
                      judge=None) -> dict:
    """One agent-managed round across the portfolio. Read + propose only.

    Returns per-business action lists. Nothing is sent, resolved, or
    reprioritized — every entry needs a human grant to take effect.
    """
    actions: dict[str, list] = {}
    for biz in list_businesses(connection):
        bid = biz["business_id"]
        items: list[dict] = []
        new_tickets = connection.execute(
            "SELECT id FROM support_tickets WHERE business_id=? "
            "AND status='new' ORDER BY id", (bid,)).fetchall()
        for (tid,) in new_tickets:
            t = get_ticket(connection, tid)
            esc = should_escalate(f"{t['subject']} {t['detail']}")
            prop = triage_ticket(connection, tid, judge=judge)
            items.append({"kind": "triage", "ticket_id": tid,
                          "proposal": prop, "escalate": esc["escalate"],
                          "escalate_reason": esc["reason"]})
            if esc["escalate"]:
                biz_full = get_business(connection, bid) or {}
                pkg = build_context_package(
                    customer_wants=t["subject"],
                    tried=[], unresolved=t["detail"][:300],
                    business_id=bid, business_name=biz.get("name", ""),
                    systems=biz_full.get("systems", []),
                    qualifications=biz_full.get("qualifications", []))
                items.append({"kind": "handoff_package", "ticket_id": tid,
                              "package": pkg})
        for nudge in sla_watch(connection):
            if nudge["business_id"] == bid:
                items.append({"kind": "sla_nudge", **nudge})
        if items:
            actions[bid] = items
    return {"businesses_with_actions": len(actions), "actions": actions}
