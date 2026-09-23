"""WhatsApp Cloud API transport — the last mile builders don't cover.

Takes only sendable payloads from messages.build_message() and POSTs
them to the Cloud API. HTTP is injectable (stdlib urllib by default)
so the full path is testable with mocks today and live the moment a
test number exists. Sends nothing without gates passing upstream;
errors return receipts, never raise.

Token comes from the WHATSAPP_TOKEN env var or an explicit argument —
never from the repo, never logged.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import urllib.request
from datetime import datetime, timezone
from typing import Any, Callable

API_VERSION = "v21.0"

SCHEMA = """
CREATE TABLE IF NOT EXISTS whatsapp_receipts (
    idempotency_key TEXT PRIMARY KEY,
    to_prefix TEXT NOT NULL,
    message_id TEXT,
    sent_at TEXT NOT NULL,
    replayed INTEGER NOT NULL DEFAULT 0
)
"""


def token_from_env() -> str:
    return os.environ.get("WHATSAPP_TOKEN", "")


def _default_sender(url: str, token: str, body: dict) -> dict:
    """POST JSON to the Cloud API. Returns the parsed response."""
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def _api_body(payload: dict) -> dict:
    base: dict[str, Any] = {
        "messaging_product": "whatsapp",
        "to": payload["to"],
    }
    if payload.get("kind") == "template":
        base["type"] = "template"
        base["template"] = {"name": payload["template"],
                            "language": {"code": "en_GB"}}
    else:
        base["type"] = "text"
        base["text"] = {"body": payload["text"]}
    return base


def send_payload(connection: sqlite3.Connection, payload: dict, *,
                 phone_number_id: str, token: str = "",
                 sender: Callable[[str, str, dict], dict] | None = None,
                 idempotency_key: str = "") -> dict:
    """Send one builder payload. Returns a receipt, never raises.

    Receipt: {"sent": bool, "message_id": str|None, "reason": str,
              "replayed": bool}. Replays return the stored receipt
    without touching the network.
    """
    now = datetime.now(timezone.utc).isoformat()
    if not payload.get("sendable"):
        return {"sent": False, "message_id": None,
                "reason": payload.get("reason", "payload not sendable"),
                "replayed": False}
    token = token or token_from_env()
    if not token:
        return {"sent": False, "message_id": None,
                "reason": "no WHATSAPP_TOKEN", "replayed": False}
    if not phone_number_id:
        return {"sent": False, "message_id": None,
                "reason": "no phone_number_id", "replayed": False}

    connection.execute(SCHEMA)
    if idempotency_key:
        row = connection.execute(
            "SELECT message_id FROM whatsapp_receipts WHERE "
            "idempotency_key = ?", (idempotency_key,)).fetchone()
        if row:
            connection.execute(
                "UPDATE whatsapp_receipts SET replayed = 1 WHERE "
                "idempotency_key = ?", (idempotency_key,))
            connection.commit()
            return {"sent": True, "message_id": row[0],
                    "reason": "idempotent replay", "replayed": True}

    url = (f"https://graph.facebook.com/{API_VERSION}/"
           f"{phone_number_id}/messages")
    post = sender or _default_sender
    try:
        resp = post(url, token, _api_body(payload))
    except Exception as e:
        return {"sent": False, "message_id": None,
                "reason": f"transport error: {type(e).__name__}",
                "replayed": False}
    msgs = (resp.get("messages") or [{}])
    message_id = str(msgs[0].get("id") or "")
    if not message_id:
        return {"sent": False, "message_id": None,
                "reason": f"no message id: {str(resp)[:120]}",
                "replayed": False}
    if idempotency_key:
        connection.execute(
            "INSERT OR IGNORE INTO whatsapp_receipts "
            "(idempotency_key, to_prefix, message_id, sent_at) "
            "VALUES (?, ?, ?, ?)",
            (idempotency_key, payload["to"][:6], message_id, now))
        connection.commit()
    try:
        from audit import audit as _audit
        _audit(actor="whatsapp", action="message.sent",
               detail={"to_prefix": payload["to"][:6],
                       "kind": payload.get("kind", ""),
                       "mid": hashlib.sha256(
                           message_id.encode()).hexdigest()[:12]})
    except Exception:
        pass
    return {"sent": True, "message_id": message_id,
            "reason": "sent", "replayed": False}
