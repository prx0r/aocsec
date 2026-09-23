"""Tests for aocsec audit scripts."""

import subprocess
import unittest


def run(script):
    return subprocess.run(
        ["bash", f"scripts/{script}"],
        capture_output=True, text=True, cwd="/home/ubuntu/aocsec",
    )


class TestSecretScan(unittest.TestCase):
    def test_clean_estate(self):
        r = run("secret-scan.sh")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("secret-scan: clean", r.stdout)

    def test_self_match_excluded(self):
        r = run("secret-scan.sh")
        self.assertNotIn("secret-scan.sh", r.stdout)


class TestPermsAudit(unittest.TestCase):
    def test_catches_systemd_secret(self):
        r = run("perms-audit.sh")
        # pow-site.service finding is open -> nonzero + FAIL line
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("pow-site.service", r.stdout)

    def test_no_embedded_git_credentials(self):
        r = run("perms-audit.sh")
        self.assertIn("no embedded credentials in remotes", r.stdout)


class TestHeadersCheck(unittest.TestCase):
    def test_dashboard_headers(self):
        r = run("headers-check.sh")
        self.assertIn("default-src 'self'", r.stdout)
        self.assertIn("bad token: 401", r.stdout)
        self.assertIn("bearer: 200", r.stdout)


if __name__ == "__main__":
    unittest.main()
