"""Tests for central audit sink, export, gateway limits."""

import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock


class TestAuditSink(unittest.TestCase):
    def test_disabled(self):
        from audit import audit
        with mock.patch.dict(os.environ, {"AOCSEC_AUDIT": "off"}):
            self.assertIsNone(audit(actor="t", action="a"))

    def test_writes_chained_record(self):
        from audit import audit
        from audit_chain import verify
        with tempfile.TemporaryDirectory() as tmp:
            log = str(Path(tmp) / "a.jsonl")
            with mock.patch.dict(os.environ, {"AOCSEC_AUDIT_LOG": log},
                                 clear=False):
                # ensure enabled even if env has off
                os.environ.pop("AOCSEC_AUDIT", None)
                r = audit(actor="t", action="a", business_id="b1",
                          detail={"k": "v"})
            self.assertIsNotNone(r)
            self.assertEqual(r["detail"]["business_id"], "b1")
            self.assertTrue(verify(log)["ok"])

    def test_secret_redaction(self):
        from audit import audit
        with tempfile.TemporaryDirectory() as tmp:
            log = str(Path(tmp) / "a.jsonl")
            with mock.patch.dict(os.environ, {"AOCSEC_AUDIT_LOG": log},
                                 clear=False):
                os.environ.pop("AOCSEC_AUDIT", None)
                audit(actor="t", action="a",
                      detail={"api_key": "SUPERSECRETVALUE1234567890"})
            content = open(log).read()
            self.assertNotIn("SUPERSECRET", content)


class TestExport(unittest.TestCase):
    def _setup(self):
        from audit import audit as audit_fn
        tmp = tempfile.TemporaryDirectory()
        log = str(Path(tmp.name) / "a.jsonl")
        sconn = sqlite3.connect(":memory:")
        from support.tickets import init_support_tables, open_ticket
        init_support_tables(sconn)
        open_ticket(sconn, business_id="b1", subject="x")
        aconn = sqlite3.connect(":memory:")
        from verify import init_verify_tables, record_attestation
        init_verify_tables(aconn)
        record_attestation(aconn, business_id="b1", qualification="gas_safe",
                           verdict="verified", verified_by="amy")
        with mock.patch.dict(os.environ, {"AOCSEC_AUDIT_LOG": log},
                             clear=False):
            os.environ.pop("AOCSEC_AUDIT", None)
            audit_fn(actor="t", action="stage.installed", business_id="b1")
            audit_fn(actor="t", action="other", business_id="b2")
        return tmp, log, sconn, aconn

    def test_export_combines(self):
        from audit import export_business_audit
        tmp, log, sconn, aconn = self._setup()
        try:
            out = export_business_audit(
                "b1", chain_logs=[log], support_conn=sconn,
                attest_conn=aconn)
            self.assertEqual(out["counts"],
                             {"chain": 1, "tickets": 1, "attestations": 1})
            self.assertTrue(out["exported_at"])
        finally:
            tmp.cleanup()
            sconn.close()
            aconn.close()

    def test_export_empty(self):
        from audit import export_business_audit
        out = export_business_audit("nobody")
        self.assertEqual(out["counts"],
                         {"chain": 0, "tickets": 0, "attestations": 0})

    def test_export_rejects_blank(self):
        from audit import export_business_audit
        with self.assertRaises(ValueError):
            export_business_audit("  ")


class TestGatewayLimits(unittest.TestCase):
    def _cfg(self):
        from gateway.server import GatewayConfig, Backend
        return GatewayConfig(
            tokens={"t1": {"secret": "s3cret-token",
                           "scopes": ["legislation:read"]}},
            backends={"leg": Backend(
                name="leg", command=["true"], cwd=".",
                tools={"legislation_lookup": "legislation:read"})})

    def test_rate_limit_429(self):
        from gateway.server import LIMITER, handle_request
        cfg = self._cfg()
        # shrink budget for this token
        cfg.tokens["t1"]["rate_limit"] = {"calls": 2, "window_s": 60}
        # reset limiter state for determinism
        LIMITER._hits.pop("t1", None)
        body = {"jsonrpc": "2.0", "id": 1, "method": "tools/list",
                "params": {}}
        auth = "Bearer s3cret-token"
        self.assertEqual(handle_request(cfg, auth, body)[0], 200)
        self.assertEqual(handle_request(cfg, auth, body)[0], 200)
        code, resp = handle_request(cfg, auth, body)
        self.assertEqual(code, 429)
        LIMITER._hits.pop("t1", None)


if __name__ == "__main__":
    unittest.main()
