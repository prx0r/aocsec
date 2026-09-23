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


def _audit_build(to: str, kind: str, sendable: bool, reason: str = "") -> None:
    try:
        from audit import audit as _audit
        _audit(actor="whatsapp", action=f"message.{kind}",
               detail={"to_prefix": to[:6], "sendable": sendable,
                       "reason": reason[:120]})
    except Exception:
        pass


def build_message(connection, *, to: str, body: str = "",
                  template: str = "", variables: dict | None = None,
                  last_user_message_at: str = "") -> dict:
    """Build a sendable payload or refuse with reasons.

    - Free-form (body, no template): needs opt-in + open window.
    - Template: needs opt-in only (templates work outside the window).
    Every outcome (including refusals) is audit-logged.
    """
    if not is_opted_in(connection, to):
        _audit_build(to, "refused", False, "recipient not opted in")
        return {"sendable": False, "reason": "recipient not opted in",
                "to": to}
    if template:
        try:
            text = render_template(template, variables or {})
        except ValueError as e:
            _audit_build(to, "refused", False, str(e))
            return {"sendable": False, "reason": str(e), "to": to}
        _audit_build(to, "template", True)
        return {"sendable": True, "to": to, "kind": "template",
                "template": template, "text": text}
    if not body.strip():
        _audit_build(to, "refused", False, "empty body")
        return {"sendable": False,
                "reason": "free-form needs body text", "to": to}
    if not last_user_message_at:
        _audit_build(to, "refused", False, "no timestamp")
        return {"sendable": False,
                "reason": "free-form needs last_user_message_at for "
                          "window check (or use a template)", "to": to}
    if not in_freeform_window(last_user_message_at):
        _audit_build(to, "refused", False, "window closed")
        return {"sendable": False,
                "reason": "24h window closed — use a template",
                "to": to,
                "suggest_template": True}
    _audit_build(to, "freeform", True)
    return {"sendable": True, "to": to, "kind": "freeform", "text": body}
