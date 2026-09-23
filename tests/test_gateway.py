"""Tests for the MCP gateway. Backend subprocesses are stubbed."""

import json
import unittest
from unittest import mock

from gateway.server import Backend, GatewayConfig, handle_request


def _cfg(**kw):
    tokens = {"t1": {"secret": "s3cret-token", "scopes": ["legislation:read"]},
              "t2": {"secret": "other-secret", "scopes": []}}
    backends = {"leg": Backend(name="leg", command=["true"], cwd=".",
                               tools={"legislation_lookup": "legislation:read",
                                      "admin_tool": "admin:write"})}
    cfg = GatewayConfig(tokens=tokens, backends=backends)
    for k, v in kw.items():
        setattr(cfg, k, v)
    return cfg


def _stub_backend(result):
    """Fake _backend_call returning a fixed payload."""
    def fake(backend, payload, timeout=60):
        return {"jsonrpc": "2.0", "id": 999,
                "result": {"content": [{"type": "text",
                                        "text": json.dumps(result)}]}}
    return fake


class TestAuth(unittest.TestCase):
    def test_bad_token_401(self):
        code, _ = handle_request(_cfg(), "Bearer wrong", {"method": "x"})
        self.assertEqual(code, 401)

    def test_missing_token_401(self):
        code, _ = handle_request(_cfg(), "", {"method": "x"})
        self.assertEqual(code, 401)

    def test_timing_safe_compare(self):
        # different lengths must not raise / match
        code, _ = handle_request(_cfg(), "Bearer s3", {"method": "x"})
        self.assertEqual(code, 401)


class TestScopes(unittest.TestCase):
    def test_list_shows_only_scoped_tools(self):
        code, resp = handle_request(
            _cfg(), "Bearer s3cret-token",
            {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})
        self.assertEqual(code, 200)
        names = [t["name"] for t in resp["result"]["tools"]]
        self.assertIn("legislation_lookup", names)
        self.assertNotIn("admin_tool", names)

    def test_unscoped_tool_403(self):
        code, resp = handle_request(
            _cfg(), "Bearer s3cret-token",
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
             "params": {"name": "admin_tool", "arguments": {}}})
        self.assertEqual(code, 403)

    def test_unknown_tool_404(self):
        code, _ = handle_request(
            _cfg(), "Bearer s3cret-token",
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
             "params": {"name": "nope", "arguments": {}}})
        self.assertEqual(code, 404)

    def test_unknown_method_404(self):
        code, _ = handle_request(
            _cfg(), "Bearer s3cret-token",
            {"jsonrpc": "2.0", "id": 1, "method": "nope", "params": {}})
        self.assertEqual(code, 404)


class TestForwarding(unittest.TestCase):
    def test_call_rewrites_id(self):
        import gateway.server as srv
        with mock.patch.object(srv, "_backend_call",
                               side_effect=_stub_backend({"ok": True})):
            code, resp = handle_request(
                _cfg(), "Bearer s3cret-token",
                {"jsonrpc": "2.0", "id": 7, "method": "tools/call",
                 "params": {"name": "legislation_lookup", "arguments": {}}})
        self.assertEqual(code, 200)
        self.assertEqual(resp["id"], 7)

    def test_backend_error_502(self):
        import gateway.server as srv

        def boom(backend, payload, timeout=60):
            raise RuntimeError("down")

        with mock.patch.object(srv, "_backend_call", side_effect=boom):
            code, _ = handle_request(
                _cfg(), "Bearer s3cret-token",
                {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                 "params": {"name": "legislation_lookup", "arguments": {}}})
        self.assertEqual(code, 502)


class TestAudit(unittest.TestCase):
    def test_audit_log_written_without_values(self):
        import tempfile
        with tempfile.NamedTemporaryFile(
                mode="r", suffix=".jsonl", delete=False) as f:
            path = f.name
        import gateway.server as srv
        with mock.patch.object(srv, "_backend_call",
                               side_effect=_stub_backend({"ok": True})):
            handle_request(
                _cfg(audit_log=path), "Bearer s3cret-token",
                {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                 "params": {"name": "legislation_lookup",
                            "arguments": {"secret_stuff": "x"}}})
        import os
        content = open(path).read()
        os.unlink(path)
        self.assertIn("legislation_lookup", content)
        self.assertNotIn("secret_stuff", content)
        self.assertNotIn("s3cret-token", content)


if __name__ == "__main__":
    unittest.main()
