"""Static checks over MCP tool definitions. No network, no model calls."""

from __future__ import annotations

import re
import unicodedata

# Imperative override / exfiltration / concealment phrasing.
OVERRIDE_PHRASES = (
    "ignore previous instructions",
    "disregard instructions",
    "override",
    "system override",
    "do not tell the user",
    "don't tell the user",
    "conceal from the user",
    "hide from the user",
    "exfiltrate",
    "send to http",
    "post to http",
    "upload the contents",
    "read the contents of ~/.ssh",
    "read ~/.ssh",
    "cat /etc/passwd",
    "no approval needed",
    "skip approval",
    "auto-approve",
)

# Invisible / direction-control codepoints (zero-width, bidi, tags).
INVISIBLE_CHARS = set(
    ["\u200b", "\u200c", "\u200d", "\ufeff",
     "\u202a", "\u202b", "\u202c", "\u202d", "\u202e",
     "\U000e0000", "\U000e0001"]
    + [chr(c) for c in range(0xE0020, 0xE0074)]
)

_URL_RE = re.compile(r"https?://[^\s)\"']+|www\.[^\s)\"']+")


def _invisible_found(text: str) -> list[str]:
    found = sorted({f"U+{ord(c):04X}" for c in text if c in INVISIBLE_CHARS})
    # also catch any unassigned / control chars smuggled in
    for c in text:
        if unicodedata.category(c) == "Cf" and f"U+{ord(c):04X}" not in found:
            found.append(f"U+{ord(c):04X}")
    return sorted(set(found))


def scan_description(name: str, description: str) -> list[dict]:
    """Check one tool description. Returns findings (empty = clean)."""
    findings = []
    lowered = description.lower()
    for phrase in OVERRIDE_PHRASES:
        if phrase in lowered:
            findings.append({"tool": name, "severity": "critical",
                             "check": "override_phrase",
                             "detail": f"contains {phrase!r}"})
    invis = _invisible_found(description)
    if invis:
        findings.append({"tool": name, "severity": "high",
                         "check": "invisible_unicode",
                         "detail": f"hidden codepoints: {', '.join(invis)}"})
    for url in _URL_RE.findall(description):
        findings.append({"tool": name, "severity": "medium",
                         "check": "url_in_description",
                         "detail": f"references {url[:80]} — verify it is "
                                   "documentation, not an exfil endpoint"})
    if len(description) > 2000:
        findings.append({"tool": name, "severity": "low",
                         "check": "overlong_description",
                         "detail": f"{len(description)} chars — review for "
                                   "buried instructions"})
    return findings


def scan_tools(tools: list[dict]) -> dict:
    """Scan a tools/list payload. Returns {clean, findings}."""
    findings = []
    for tool in tools:
        name = tool.get("name", "?")
        findings.extend(scan_description(
            name, tool.get("description", "")))
    return {"clean": not findings, "findings": findings,
            "tools_scanned": len(tools)}


def scan_server(server_name: str, tools: list[dict]) -> dict:
    """Scan one server's toolset. Adds server context to findings."""
    result = scan_tools(tools)
    result["server"] = server_name
    for f in result["findings"]:
        f["server"] = server_name
    return result
