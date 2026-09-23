"""Companies House lookups. Read-only. Key from env, never code.

API: api.company-information.service.gov.uk, Basic auth with API key.
Returns profile facts (status, type, SIC, incorporation, office
locality). Officer NAMES are redacted to counts — PII minimization:
verify existence and standing, not identities.
"""

from __future__ import annotations

import base64
import json
import os
import urllib.parse
import urllib.request

BASE = "https://api.company-information.service.gov.uk"


class CompanyNotFound(Exception):
    pass


class CompanyError(Exception):
    pass


def _key() -> str:
    key = os.environ.get("COMPANIES_HOUSE_API_KEY", "")
    if not key:
        raise CompanyError("COMPANIES_HOUSE_API_KEY is not set")
    return key


def _get(path: str, timeout: int = 30) -> dict:
    auth = base64.b64encode(f"{_key()}:".encode()).decode()
    req = urllib.request.Request(
        BASE + path, method="GET",
        headers={"Authorization": f"Basic {auth}",
                 "Accept": "application/json",
                 "User-Agent": "aocsec-company/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise CompanyNotFound(f"not found: {path}")
        if e.code == 429:
            raise CompanyError("rate limited — back off")
        if e.code in (401, 403):
            raise CompanyError("key rejected — check COMPANIES_HOUSE_API_KEY")
        raise CompanyError(f"HTTP {e.code}")
    except urllib.error.URLError as e:
        raise CompanyError(f"unreachable: {e.reason}")


def lookup_company(number: str, timeout: int = 30) -> dict:
    """Company profile by number. Officer identities reduced to a flag."""
    number = "".join(c for c in number.upper() if c.isalnum())
    if not number:
        raise ValueError("company number is required")
    d = _get(f"/company/{number}", timeout)
    return {
        "company_number": d.get("company_number", number),
        "name": d.get("company_name", ""),
        "status": d.get("company_status", ""),
        "type": d.get("type", ""),
        "incorporated": d.get("date_of_creation", ""),
        "sic_codes": d.get("sic_codes", []),
        "office_locality": (d.get("registered_office_address") or {}).get("locality", ""),
        "has_officers": bool(d.get("links", {}).get("officers")),
        "dissolution_date": d.get("date_of_cessation", ""),
    }


def search_companies(query: str, items_per_page: int = 5,
                     timeout: int = 30) -> list[dict]:
    """Search by name. Returns candidates with numbers for lookup."""
    query = query.strip()
    if not query:
        raise ValueError("query is required")
    qs = urllib.parse.urlencode({"q": query,
                                 "items_per_page": max(1, min(20, items_per_page))})
    d = _get(f"/search/companies?{qs}", timeout)
    return [{
        "company_number": i.get("company_number", ""),
        "name": i.get("title", ""),
        "status": i.get("company_status", ""),
        "type": i.get("company_type", ""),
        "address": (i.get("address") or {}).get("locality", ""),
    } for i in d.get("items", [])]
