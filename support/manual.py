"""E-manual generator + company systems graph.

The e-manual is the per-business operating document: their systems
inventory (what exists, who owns it, how to reach it), how to interact
with the assistant (what it can/can't do, how approvals work), escalation
paths, and the legislation pointers that apply to them.

The systems graph is the machine-readable twin: business -> systems ->
contacts -> qualifications. Support, audits, and handoffs read it so
nobody asks the customer what they already told us.
"""

from __future__ import annotations


def build_systems_graph(*, business: dict, systems: list[dict],
                        contacts: list[dict] | None = None,
                        qualifications: list[str] | None = None) -> dict:
    """Assemble the company structure graph. Plain data, no storage."""
    return {
        "business": {
            "id": business.get("business_id", ""),
            "name": business.get("business_name", business.get("name", "")),
            "vertical": business.get("vertical", ""),
            "postcode": business.get("postcode", ""),
        },
        "systems": [
            {"name": s.get("name", ""), "kind": s.get("kind", ""),
             "owner": s.get("owner", "customer"),
             "access": s.get("access", ""),
             "notes": s.get("notes", "")}
            for s in systems
        ],
        "contacts": [
            {"role": c.get("role", ""), "channel": c.get("channel", ""),
             "detail": c.get("detail", "")}
            for c in (contacts or [])
        ],
        "qualifications": list(qualifications or []),
    }


def generate_emanual(*, business_name: str, vertical: str,
                     systems: list[dict], obligations: list[dict],
                     support_channel: str = "",
                     assistant_name: str = "Buddy") -> str:
    """Render the e-manual markdown for one business."""
    lines = [
        f"# Operating manual — {business_name}",
        "",
        f"Trade: {vertical}. Keep this where the owner can find it.",
        "",
        "## Your systems",
        "",
    ]
    if not systems:
        lines.append("No systems recorded yet.")
    for s in systems:
        lines.append(
            f"- **{s.get('name', '?')}** ({s.get('kind', '?')}) — "
            f"owned by {s.get('owner', 'customer')}. "
            f"{s.get('notes', '')}".rstrip())
    lines += [
        "",
        f"## Working with {assistant_name}",
        "",
        "- Ask anything about jobs, quotes, bookings, regulations, suppliers.",
        "- Quotes are drafts until you approve them. Nothing sends itself.",
        "- Money moves only on provider pages you open (bank, Stripe).",
        "- Say 'talk to a human' any time — the conversation hands over "
        "with full context, you never repeat yourself.",
        "",
        "## Rules that apply to you",
        "",
    ]
    if not obligations:
        lines.append("No specific obligations on file — ask about your trade.")
    for o in obligations:
        lines.append(
            f"- **{o.get('law', '?')}**: {o.get('requirement', '')[:160]} "
            f"([source]({o.get('source_url', '')}))")
        if o.get("owner_action"):
            lines.append(f"  Action: {o.get('owner_action')}")
    lines += [
        "",
        "## If something goes wrong",
        "",
        f"- Support: {support_channel or 'reply to any message from us'}",
        "- Urgent (money moving, account lockout): call, don't chat.",
        "- Suspected fraud (new bank details, pressure to pay): stop, "
        "call the supplier on a number you already hold.",
        "",
        "This manual is point-in-time. Ask for a fresh copy any time.",
    ]
    return "\n".join(lines)
