"""Tests for aocsec legislation graph + MCP server."""

import asyncio
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent

from legislation.graph import (
    build_graph,
    instruments,
    obligations_for,
    stale_rules,
)


class TestGraph(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = build_graph()

    def test_loads_both_sources(self):
        ids = [o.id for o in self.graph]
        self.assertTrue(any(i.startswith("LEG-") for i in ids))
        self.assertIn("LEG-UK-CIS-SUB", ids)

    def test_every_record_has_source_and_review(self):
        for o in self.graph:
            self.assertTrue(o.source_url, o.id)
            self.assertTrue(o.review_date, o.id)
            self.assertTrue(o.owner_action, o.id)

    def test_tailored_electrician_tax(self):
        res = obligations_for(self.graph, vertical="electrician", topic="tax")
        self.assertTrue(len(res) >= 1)
        self.assertTrue(all(not o.is_stale() for o in res))

    def test_stale_excluded_by_default(self):
        from legislation.graph import Obligation
        old = Obligation(id="X", law="Old", requirement="x",
                         review_date="2020-01-01")
        self.assertEqual(
            obligations_for([old], vertical="", topic=""), [])
        self.assertEqual(len(stale_rules([old])), 1)

    def test_general_rules_apply_to_all(self):
        res = obligations_for(self.graph, vertical="electrician")
        self.assertTrue(any(not o.applies_to for o in res))


class TestMCP(unittest.TestCase):
    def test_stdio_all_tools(self):
        async def go():
            proc = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "legislation.mcp_server",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(ROOT), limit=2 ** 20)

            async def rpc(i, method, params):
                proc.stdin.write((json.dumps(
                    {"jsonrpc": "2.0", "id": i, "method": method,
                     "params": params}) + "\n").encode())
                await proc.stdin.drain()
                return json.loads(await asyncio.wait_for(
                    proc.stdout.readline(), timeout=30))

            try:
                r = await rpc(1, "initialize", {
                    "protocolVersion": "2024-11-05", "capabilities": {},
                    "clientInfo": {"name": "t", "version": "0"}})
                self.assertEqual(
                    r["result"]["serverInfo"]["name"], "aocsec-legislation")
                r = await rpc(2, "tools/list", {})
                names = [t["name"] for t in r["result"]["tools"]]
                self.assertEqual(len(names), 4)
                r = await rpc(3, "tools/call", {
                    "name": "obligations_for_business",
                    "arguments": {"vertical": "electrician"}})
                d = json.loads(r["result"]["content"][0]["text"])
                self.assertGreater(d["count"], 0)
                r = await rpc(4, "tools/call", {
                    "name": "instrument_detail",
                    "arguments": {"law": "no-such-law"}})
                d = json.loads(r["result"]["content"][0]["text"])
                self.assertIn("error", d)
            finally:
                proc.terminate()
                try:
                    await asyncio.wait_for(proc.wait(), timeout=2)
                except asyncio.TimeoutError:
                    proc.kill()

        asyncio.run(go())


if __name__ == "__main__":
    unittest.main()
