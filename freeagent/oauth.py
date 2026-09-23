"""OAuth 2.0 helpers. No passwords, no stored secrets in code.

Flow: register app at dev.freeagent.com → authorize_url() → owner
approves in THEIR FreeAgent → exchange_code() for scoped tokens.
Tokens live in the caller's 600-perm store, never in this repo.
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request

APPROVE_URL = "https://api.freeagent.com/v2/approve_app"
TOKEN_URL = "https://api.freeagent.com/v2/token_endpoint"


def authorize_url(client_id: str, redirect_uri: str,
                  response_type: str = "code") -> str:
    """Build the owner-facing authorization URL."""
    qs = urllib.parse.urlencode({
        "redirect_uri": redirect_uri,
        "response_type": response_type,
        "client_id": client_id,
    })
    return f"{APPROVE_URL}?{qs}"


def exchange_code(client_id: str, client_secret: str, code: str,
                  redirect_uri: str, timeout: int = 30) -> dict:
    """Exchange an authorization code for tokens. Returns token dict."""
    body = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode()
    req = urllib.request.Request(
        TOKEN_URL, data=body, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded",
                 "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode())
    if "access_token" not in data:
        raise ValueError("token exchange failed: no access_token returned")
    return data
