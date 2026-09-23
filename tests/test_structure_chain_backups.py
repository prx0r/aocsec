"""Tests for structure scanner, audit chain, backups."""

import json
import tempfile
import unittest
from pathlib import Path

from audit_chain import append, create_log, verify
from backups import check_freshness, restore_drill
from structure import scan_file, scan_repo


class TestStructure(unittest.TestCase):
    def _f(self, code):
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False)
        tmp.write(code)
        tmp.close()
        return tmp.name

    def test_eval_exec_flagged(self):
        p = self._f("x = eval(user_input)\ny = exec('a=1')\n")
        kinds = [f["check"] for f in scan_file(p)]
        self.assertIn("no-eval", kinds)
        self.assertIn("no-exec", kinds)
        Path(p).unlink()

    def test_re_compile_not_flagged(self):
        import re  # noqa - ensures re.compile below parses
        p = self._f("import re\nrx = re.compile('a+')\n")
        self.assertEqual(scan_file(p), [])
        Path(p).unlink()

    def test_shell_true_flagged(self):
        p = self._f("import subprocess\nsubprocess.run(cmd, shell=True)\n")
        self.assertTrue(any(f["check"] == "no-shell-true"
                            for f in scan_file(p)))
        Path(p).unlink()

    def test_pickle_flagged_json_not(self):
        p = self._f("import pickle\ndata = pickle.loads(blob)\n")
        self.assertTrue(any(f["check"] == "no-pickle"
                            for f in scan_file(p)))
        Path(p).unlink()
        p = self._f("import json\ndata = json.loads(blob)\n")
        self.assertEqual(scan_file(p), [])
        Path(p).unlink()

    def test_self_clean(self):
        r = scan_repo("/home/ubuntu/aocsec")
        self.assertTrue(r["clean"], r["findings"][:3])


class TestAuditChain(unittest.TestCase):
    def test_append_verify(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = str(Path(tmp) / "a.jsonl")
            a = append(p, actor="t", action="a", detail={"k": "v"})
            b = append(p, actor="t", action="b",
                       detail={"api_key": "SECRET", "n": 1})
            self.assertEqual(b["prev"], a["hash"])
            self.assertNotIn("SECRET", open(p).read())
            r = verify(p)
            self.assertTrue(r["ok"])
            self.assertEqual(r["entries"], 2)

    def test_tamper_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "a.jsonl"
            append(str(p), actor="t", action="a")
            lines = p.read_text().splitlines()
            e = json.loads(lines[0])
            e["action"] = "evil"
            lines[0] = json.dumps(e)
            p.write_text("\n".join(lines) + "\n")
            self.assertFalse(verify(str(p))["ok"])

    def test_missing_file_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = verify(str(Path(tmp) / "nope.jsonl"))
            self.assertTrue(r["ok"])
            self.assertEqual(r["entries"], 0)


class TestMerkleSeal(unittest.TestCase):
    def test_root_and_inclusion(self):
        from audit_chain import (
            inclusion_path, merkle_root, seal_log, verify_inclusion)
        leaves = [f"entry-{i}".encode() for i in range(5)]
        root = merkle_root(leaves)
        for i in range(5):
            path = inclusion_path(leaves, i)
            self.assertTrue(verify_inclusion(leaves[i], path, root))
        self.assertFalse(verify_inclusion(b"forged", inclusion_path(leaves, 0), root))

    def test_seal_sidecar(self):
        import tempfile
        from audit_chain import append, seal_log
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            log = str(Path(tmp) / "a.jsonl")
            append(log, actor="t", action="a")
            append(log, actor="t", action="b")
            seal = seal_log(log)
            self.assertEqual(seal["entries"], 2)
            sidecar = Path(str(log) + ".seals.jsonl")
            self.assertTrue(sidecar.exists())

    def test_empty_root(self):
        from audit_chain import merkle_root
        self.assertEqual(len(merkle_root([])), 64)


class TestCertificates(unittest.TestCase):
    def test_seal_verify(self):
        from audit_chain import Certificate
        c = Certificate(cert_type="report", subject="example.com",
                        evidence=[{"sha": "abc"}]).seal()
        self.assertTrue(c.verify())

    def test_tamper_detected(self):
        from audit_chain import Certificate
        c = Certificate(cert_type="approval", subject="x").seal()
        c.subject = "y"
        self.assertFalse(c.verify())

    def test_unsealed_fails(self):
        from audit_chain import Certificate
        self.assertFalse(Certificate(cert_type="x", subject="y").verify())


class TestBackups(unittest.TestCase):
    def test_fresh_and_stale(self):
        import time
        with tempfile.TemporaryDirectory() as tmp:
            fresh = Path(tmp) / "new.txt"
            fresh.write_text("x")
            man = [{"id": "a", "path": str(fresh), "max_age_hours": 24},
                   {"id": "b", "path": str(Path(tmp) / "missing"),
                    "max_age_hours": 24}]
            r = check_freshness(man)
            self.assertFalse(r["ok"])
            states = {x["id"]: x["status"] for x in r["results"]}
            self.assertEqual(states, {"a": "fresh", "b": "missing"})

    def test_drill_needs_evidence(self):
        good = restore_drill("t", [{"step": "s1", "passed": True,
                                    "evidence": "restored 3 files, diff clean"}])
        self.assertTrue(good["passed"])
        bad = restore_drill("t", [{"step": "s1", "passed": True,
                                   "evidence": ""}])
        self.assertFalse(bad["passed"])
        empty = restore_drill("t", [])
        self.assertFalse(empty["passed"])


if __name__ == "__main__":
    unittest.main()
