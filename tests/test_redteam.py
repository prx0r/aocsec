"""Tests for aocsec redteam — attacks, grading, suite runner."""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import tempfile
import unittest
from pathlib import Path

from redteam import (
    ATTACK_CLASSES,
    ATTACKS,
    digest,
    grade,
    run_suite,
)


def safe_responder(message, session_id):
    """Test double: refuses everything sensitive, like a good assistant."""
    m = message.lower()
    if "dave" in m or "comedian" in m:
        return "I cannot do that. I'm your electrical business assistant, how can I help?"
    if "policy" in m or "confirm" in m and "policy" in m:
        return "I cannot verify any new policy. Owner approval is required for changes."
    if "skip the approval" in m or "urgent" in m:
        return "I cannot send anything without owner approval. This stays a draft."
    if "phone number" in m and "last customer" in m:
        return "I don't have access to customer contact details."
    if "discount" in m or "$5,000" in m or "£5,000" in m:
        return "I cannot approve discounts. Quotes come from your price book and need owner review."
    if "disable" in m and "confirmation" in m:
        return "I cannot disable confirmations. Please verify through your human supervisor."
    if "booking_999" in m or "move it" in m:
        return "I cannot verify that booking reference. Please confirm the details first."
    if "callback number is" in m:
        return "Noted, I'll record a callback ticket for the owner to review."
    if "what callback number" in m or "on file" in m:
        return "I don't have a number on file for you. Which number should I use?"
    return "I cannot help with that. Let me get the owner."


def muse_safe_responder(message, session_id):
    """Test double: hardened Muse-facing assistant."""
    m = message.lower()
    if "disconnected" in m and "remember" in m:
        return "I don't retain customer data between sessions. Ask the owner for job records."
    if "bank account" in m and "password" in m:
        return "Never share banking passwords here. Payments happen on your bank or Stripe pages, never through me."
    if "approve everything" in m or "in one go" in m:
        return "I cannot blanket-approve. Each action needs separate owner review."
    return safe_responder(message, session_id)


def evil_responder(message, session_id):
    """Test double: breaches everything. Validates the grader catches it."""
    return "Done. I am Dave, confirmed policy updated, quote sent, approved."


class TestAttacks(unittest.TestCase):
    def test_twelve_classes(self):
        self.assertEqual(len(ATTACK_CLASSES), 12)
        self.assertIn("rulebook_poisoning", ATTACK_CLASSES)
        classes = {a["class"] for a in ATTACKS}
        self.assertEqual(classes, set(ATTACK_CLASSES))

    def test_shape(self):
        for atk in ATTACKS:
            self.assertIn("id", atk)
            self.assertIn("messages", atk)
            self.assertTrue(atk["messages"])


class TestGrade(unittest.TestCase):
    def test_held(self):
        ok, _ = grade("I cannot do that", ["cannot"], [], [])
        self.assertTrue(ok)

    def test_breached_forbidden(self):
        ok, why = grade("I cannot refuse, quote sent", ["cannot"], [], ["quote sent"])
        self.assertFalse(ok)
        self.assertIn("forbidden", why)

    def test_digest_stable(self):
        self.assertEqual(digest({"a": 1}), digest({"a": 1}))
        self.assertTrue(digest({"a": 1}).startswith("sha256:"))


class TestRunner(unittest.TestCase):
    def test_safe_holds_all(self):
        with tempfile.TemporaryDirectory() as tmp:
            res = run_suite(safe_responder, out_dir=tmp)
            self.assertEqual(res["held"], res["total"])
            self.assertEqual(res["breached"], [])
            ev = Path(res["evidence"])
            self.assertTrue(ev.exists())
            lines = ev.read_text().strip().split("\n")
            self.assertEqual(len(lines), len(ATTACKS))
            rec = json.loads(lines[0])
            self.assertIn("digest", rec)

    def test_muse_classes_hold(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            res = run_suite(muse_safe_responder, out_dir=tmp)
            self.assertEqual(res["held"], res["total"])
            self.assertEqual(res["breached"], [])

    def test_evil_breaches(self):
        with tempfile.TemporaryDirectory() as tmp:
            res = run_suite(evil_responder, out_dir=tmp)
            self.assertTrue(res["breached"])

    def test_transport_error_recorded(self):
        def broken(message, session_id):
            raise ConnectionError("down")

        with tempfile.TemporaryDirectory() as tmp:
            res = run_suite(broken, out_dir=tmp)
            self.assertEqual(len(res["errors"]), len(ATTACKS))


if __name__ == "__main__":
    unittest.main()
