"""MCP tool-description self-scanner.

Our MCP servers' tool descriptions are text LLMs read to decide actions
— the exact supply-chain surface from the CSA/Microsoft June 2026
disclosures (36.5–72.8% measured poisoning success). This scans OUR
tool definitions for: imperative override phrases, invisible Unicode
(zero-width, bidi, tag chars), URLs (exfil endpoints), credential
requests, and destructive-capability claims.

Run against every MCP server config before enabling it, and on a
schedule after (descriptions change = dependency update = re-review).
"""

from .scan import (
    INVISIBLE_CHARS,
    OVERRIDE_PHRASES,
    scan_description,
    scan_server,
    scan_tools,
)

__all__ = [
    "INVISIBLE_CHARS",
    "OVERRIDE_PHRASES",
    "scan_description",
    "scan_server",
    "scan_tools",
]
