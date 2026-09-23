"""Legislation MCP server — stdio JSON-RPC for Muse integration.

Read-only tools over the obligation graph. No auth on stdio (local
transport); the HTTPS gateway (when built for Muse) enforces scopes.
Every answer carries citations + review dates so the chatbot can show
sources instead of asserting law.

Usage: python3 -m legislation.mcp_server  (from aocsec repo root)
Muse needs streamable HTTP — see docs/muse-hardening.md gateway section.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from legislation.graph import (
    build_graph,
    instruments,
    obligations_for,
    stale_rules,
)

TOOLS = [
    {"name": "legislation_lookup",
     "description": "Find obligations by topic, vertical, or domain. Stale rules excluded by default.",
     "inputSchema": {"type": "object",
                     "properties": {"topic": {"type": "string"},
                                    "vertical": {"type": "string"},
                                    "domain": {"type": "string"}},
                     "additionalProperties": False}},
    {"name": "obligations_for_business",
     "description": "Tailored obligation set for a business profile: vertical plus optional topics. Returns citations, owner actions, escalations.",
     "inputSchema": {"type": "object",
                     "properties": {"vertical": {"type": "string"},
                                    "topics": {"type": "array", "items": {"type": "string"}}},
                     "required": ["vertical"],
                     "additionalProperties": False}},
    {"name": "stale_rules",
     "description": "Rules past review_date. The audit queue — re-verify before use.",
     "inputSchema": {"type": "object", "properties": {},
                     "additionalProperties": False}},
    {"name": "instrument_detail",
     "description": "All obligations under one law/instrument.",
     "inputSchema": {"type": "object",
                     "properties": {"law": {"type": "string"}},
                     "required": ["law"],
                     "additionalProperties": False}},
]


def _graph():
    try:
        return build_graph()
    except Exception as e:
        raise RuntimeError(f"graph load failed: {e}")


def handle_tool(name: str, arguments: dict):
    obs = _graph()
    if name == "legislation_lookup":
        res = obligations_for(obs,
                              vertical=arguments.get("vertical", ""),
                              topic=arguments.get("topic", ""),
                              domain=arguments.get("domain", ""))
        return {"count": len(res), "obligations": [o.to_dict() for o in res]}
    if name == "obligations_for_business":
        vertical = arguments.get("vertical", "")
        topics = arguments.get("topics", []) or [""]
        seen: dict[str, dict] = {}
        for t in topics:
            for o in obligations_for(obs, vertical=vertical, topic=t):
                seen[o.id] = o.to_dict()
        out = sorted(seen.values(), key=lambda d: d["id"])
        return {"vertical": vertical, "count": len(out), "obligations": out}
    if name == "stale_rules":
        res = stale_rules(obs)
        return {"count": len(res),
                "rules": [{"id": o.id, "law": o.law,
                           "review_date": o.review_date} for o in res]}
    if name == "instrument_detail":
        law = arguments.get("law", "")
        res = [o.to_dict() for o in obs if o.law == law]
        if not res:
            return {"error": f"unknown instrument: {law}",
                    "known": [i["law"] for i in instruments(obs)]}
        return {"law": law, "count": len(res), "obligations": res}
    raise ValueError(f"unknown tool: {name}")


def run_stdio():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        method = req.get("method", "")
        req_id = req.get("id")
        params = req.get("params", {}) or {}
        try:
            if method == "initialize":
                response = {"jsonrpc": "2.0", "id": req_id,
                            "result": {"protocolVersion": "2024-11-05",
                                       "capabilities": {"tools": {}},
                                       "serverInfo": {"name": "aocsec-legislation",
                                                      "version": "0.1.0"}}}
            elif method == "tools/list":
                response = {"jsonrpc": "2.0", "id": req_id,
                            "result": {"tools": TOOLS}}
            elif method == "tools/call":
                result = handle_tool(params.get("name", ""), params.get("arguments", {}) or {})
                response = {"jsonrpc": "2.0", "id": req_id,
                            "result": {"content": [
                                {"type": "text",
                                 "text": json.dumps(result, default=str, indent=2)}]}}
            else:
                response = {"jsonrpc": "2.0", "id": req_id,
                            "error": {"code": -32601, "message": f"Unknown method: {method}"}}
        except Exception as e:
            response = {"jsonrpc": "2.0", "id": req_id,
                        "error": {"code": -32603, "message": str(e)[:300]}}
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    run_stdio()
