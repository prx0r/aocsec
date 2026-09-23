"""WhatsApp-native delivery layer.

Every customer-facing message goes through here: template enforcement
outside the 24h window, opt-in/opt-out per recipient, approval receipts
for anything consequential. No direct sends — builders return payloads,
a human or an approved job submits them via the Cloud API / Business
Agent. Transport-agnostic payloads (works for Cloud API direct or the
WhatsApp Business Tools MCP path).
"""

from .messages import build_message
from .optout import is_opted_in, record_consent, record_optout
from .templates import TEMPLATES, get_template
from .transport import send_payload, token_from_env

__all__ = [
    "TEMPLATES",
    "build_message",
    "get_template",
    "is_opted_in",
    "record_consent",
    "record_optout",
    "send_payload",
    "token_from_env",
]
