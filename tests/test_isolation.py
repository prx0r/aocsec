"""Tests for isolation checklists + identity-confusion redteam cover."""

import unittest

from isolation import (
    STEPS,
    isolation_status,
    mark_done,
    max_loss_estimate,
    onboarding_checklist,
)


class TestIsolation(unittest.TestCase):
    def test_seven_steps(self):
        cl = onboarding_checklist()
        self.assertEqual(len(cl), 7)
        self.assertEqual([s["step"] for s in cl], list(STEPS))

    def test_lifecycle(self):
        cl = onboarding_checklist()
        self.assertFalse(isolation_status(cl)["isolated"])
        for s in STEPS:
            cl = mark_done(cl, s)
        st = isolation_status(cl)
        self.assertTrue(st["isolated"])
        self.assertEqual(st["remaining"], [])

    def test_unknown_step(self):
        with self.assertRaises(ValueError):
            mark_done(onboarding_checklist(), "nope")

    def test_bounded(self):
        r = max_loss_estimate(50.0, False, False)
        self.assertTrue(r["bounded"])
        self.assertEqual(r["max_money_loss_gbp"], 50.0)

    def test_unbounded(self):
        r = max_loss_estimate(50.0, True, True)
        self.assertFalse(r["bounded"])
        self.assertEqual(len(r["unbounded_risks"]), 2)


class TestIdentityConfusion(unittest.TestCase):
    def test_class_exists(self):
        from redteam import ATTACKS, ATTACK_CLASSES
        self.assertIn("identity_confusion", ATTACK_CLASSES)
        ids = [a["id"] for a in ATTACKS if a["class"] == "identity_confusion"]
        self.assertEqual(len(ids), 3)

    def test_isolated_responder_holds(self):
        from redteam import run_suite
        import tempfile

        def responder(message, session_id):
            m = message.lower()
            if "personal credit card" in m or "capped one" in m:
                return ("I cannot use personal payment instruments. The capped "
                        "agent card is the only one in scope. Human review.")
            if "personal inbox" in m:
                return ("I cannot access inboxes outside my scope. Job mail "
                        "only — human review for anything else.")
            if "full diary" in m or "personal appointment" in m:
                return ("I cannot see the full diary, only work slots. "
                        "Human review.")
            return "I cannot help with that."

        with tempfile.TemporaryDirectory() as tmp:
            res = run_suite(responder, out_dir=tmp)
        mine = [a for a in res["breached"] if a.startswith("ident-")]
        self.assertEqual(mine, [])


if __name__ == "__main__":
    unittest.main()
