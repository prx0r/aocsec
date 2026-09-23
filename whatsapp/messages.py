"""Message builder — window + consent + template gates in one place.

A message is sendable only when: recipient opted in AND (inside 24h
window for free-form OR template provided for outside). Builders
return payloads; transport (Cloud API direct, Business Tools MCP)
sends them. Approval receipts attach upstream, never here.
"""

from __future__ import annotations

from business_agent.window import in_freeform_window

from .optout import is_opted_in
from .templates import render_template


def build_message(connection, *, to: str, body: str = "",
                  template: str = "", variables: dict | None = None,
                  last_user_message_at: str = "") -> dict:
    """Build a sendable payload or refuse with reasons.

    - Free-form (body, no template): needs opt-in + open window.
    - Template: needs opt-in only (templates work outside the window).
    """
    if not is_opted_in(connection, to):
        return {"sendable": False, "reason": "recipient not opted in",
                "to": to}
    if template:
        try:
            text = render_template(template, variables or {})
        except ValueError as e:
            return {"sendable": False, "reason": str(e), "to": to}
        return {"sendable": True, "to": to, "kind": "template",
                "template": template, "text": text}
    if not body.strip():
        return {"sendable": False,
                "reason": "free-form needs body text", "to": to}
    if not last_user_message_at:
        return {"sendable": False,
                "reason": "free-form needs last_user_message_at for "
                          "window check (or use a template)", "to": to}
    if not in_freeform_window(last_user_message_at):
        return {"sendable": False,
                "reason": "24h window closed — use a template",
                "to": to,
                "suggest_template": True}
    return {"sendable": True, "to": to, "kind": "freeform", "text": body}
