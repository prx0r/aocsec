"""Tests for aocsec jev triage + client. Fully mocked — no key, no network."""

import json
import unittest
from unittest import mock

from jev import (
    CONFIDENCE_FLOOR,
    JevError,
    JevMCP,
    classify_alerts,
    gate_completion,
    jev_available,
    verify_claims,
)


def stub_judge(mapping):
    def judge(tool, args):
        return dict(mapping.get(tool, {"label": "watch", "confidence": 0.9}))
    return judge


class TestClient(unittest.TestCase):
    def test_no_key_refuses(self):
        with mock.patch.dict("os.environ", {}, clear=False):
            env = {"PATH": "/usr/bin:/bin"}
            with mock.patch("os.environ", env):
                self.assertFalse(jev_available())
                with self.assertRaises(JevError):
                    JevMCP()


class TestClassify(unittest.TestCase):
    ALERTS = [
        {"source_id": "neso_demand", "status": "error"},
        {"source_id": "venue_l2", "status": "stale"},
    ]

    def test_buckets(self):
        judge = stub_judge({"jev_classify": {"label": "act_now",
                                             "confidence": 0.95}})
        out = classify_alerts(self.ALERTS, judge)
        self.assertEqual(len(out["act_now"]), 2)

    def test_low_confidence_escalates(self):
        judge = stub_judge({"jev_classify": {"label": "act_now",
                                             "confidence": 0.4}})
        out = classify_alerts(self.ALERTS, judge)
        self.assertEqual(len(out["needs_human"]), 2)
        self.assertEqual(out["act_now"], [])

    def test_judge_error_escalates(self):
        def boom(tool, args):
            raise RuntimeError("down")
        out = classify_alerts(self.ALERTS, boom)
        self.assertEqual(len(out["needs_human"]), 2)


class TestVerify(unittest.TestCase):
    def test_pass_and_fail(self):
        calls = [
            {"claim": "31/42 sources OK", "evidence": "status table 31/42"},
            {"claim": "all gardens green", "evidence": "powuk 9/24 ok"},
        ]

        def judge(tool, args):
            if "all gardens" in args["claim"]:
                return {"verdict": "refuted", "confidence": 0.88}
            return {"verdict": "supported", "confidence": 0.91}

        out = verify_claims(calls, judge)
        self.assertEqual(out[0]["verdict"], "supported")
        self.assertEqual(out[1]["verdict"], "refuted")

    def test_low_confidence_never_passes(self):
        judge = stub_judge({})
        out = verify_claims(
            [{"claim": "x", "evidence": "y"}],
            lambda t, a: {"verdict": "supported", "confidence": 0.5})
        self.assertEqual(out[0]["verdict"], "needs_human")


class TestClientProtocol(unittest.TestCase):
    def _proc(self, lines):
        proc = mock.MagicMock()
        proc.poll.return_value = None
        proc.stdout.readline.side_effect = lines
        return proc

    def test_hello_and_call(self):
        with mock.patch.dict("os.environ", {"TYPESAFE_API_KEY": "k"}):
            with mock.patch("subprocess.Popen") as popen:
                proc = self._proc([
                    json.dumps({"jsonrpc": "2.0", "id": 1, "result": {}}) + "\n",
                    json.dumps({"jsonrpc": "2.0", "id": 2,
                                "result": {"verdict": "ok"}}) + "\n",
                ])
                popen.return_value = proc
                with JevMCP() as client:
                    out = client.call("jev_verify", {"claim": "x"})
                self.assertEqual(out, {"verdict": "ok"})
                sent = proc.stdin.write.call_args_list[0][0][0]
                self.assertIn("initialize", sent)

    def test_empty_response_raises(self):
        with mock.patch.dict("os.environ", {"TYPESAFE_API_KEY": "k"}):
            with mock.patch("subprocess.Popen") as popen:
                proc = self._proc([
                    json.dumps({"jsonrpc": "2.0", "id": 1, "result": {}}) + "\n",
                    "",
                ])
                popen.return_value = proc
                with JevMCP() as client:
                    with self.assertRaises(JevError):
                        client.call("jev_verify", {})

    def test_error_response_raises(self):
        with mock.patch.dict("os.environ", {"TYPESAFE_API_KEY": "k"}):
            with mock.patch("subprocess.Popen") as popen:
                proc = self._proc([
                    json.dumps({"jsonrpc": "2.0", "id": 1, "result": {}}) + "\n",
                    json.dumps({"jsonrpc": "2.0", "id": 2,
                                "error": {"code": -32601, "message": "nope"}}) + "\n",
                ])
                popen.return_value = proc
                with JevMCP() as client:
                    with self.assertRaises(JevError):
                        client.call("nope", {})


class TestGate(unittest.TestCase):
    def test_ship(self):
        judge = stub_judge({"jev_gate": {"approved": True, "confidence": 0.9,
                                         "reasons": ["tests green"]}})
        out = gate_completion("diff", "70 passed", judge)
        self.assertTrue(out["ship"])

    def test_defaults_no_ship(self):
        judge = stub_judge({"jev_gate": {"approved": False,
                                         "confidence": 0.9,
                                         "reasons": ["no evidence"]}})
        out = gate_completion("diff", "none", judge)
        self.assertFalse(out["ship"])

    def test_low_confidence_blocks(self):
        judge = stub_judge({"jev_gate": {"approved": True, "confidence": 0.5}})
        out = gate_completion("diff", "some", judge)
        self.assertFalse(out["ship"])

    def test_error_blocks(self):
        def boom(tool, args):
            raise RuntimeError("down")
        out = gate_completion("diff", "some", boom)
        self.assertFalse(out["ship"])
        self.assertTrue(out["reasons"])


if __name__ == "__main__":
    unittest.main()
