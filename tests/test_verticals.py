"""Tests for vertical map, seed, and coverage."""

import unittest

from legislation.graph import build_graph, load_vertical_seed, obligations_for
from legislation.verticals import VERTICALS, coverage_report


class TestVerticals(unittest.TestCase):
    def test_eleven_verticals(self):
        self.assertEqual(len(VERTICALS), 11)

    def test_seed_loads(self):
        seed = load_vertical_seed()
        self.assertEqual(len(seed), 4)
        for o in seed:
            self.assertTrue(o.source_url)
            self.assertTrue(o.review_date)
            self.assertTrue(o.owner_action)

    def test_gaps_closed(self):
        g = build_graph()
        self.assertGreater(
            len(obligations_for(g, vertical="driving-instructors")), 0)
        self.assertGreater(
            len(obligations_for(g, vertical="car-detailers")), 0)

    def test_coverage_report(self):
        rep = coverage_report(build_graph())
        self.assertEqual(len(rep), 11)
        self.assertFalse(rep["electrician"]["gap"])
        # car-detailers has no native registry industries (gap flag true)
        # but the seed gives it specific coverage anyway
        self.assertTrue(rep["car-detailers"]["gap"])
        self.assertGreater(rep["car-detailers"]["specific"], 0)
        self.assertTrue(rep["weddings"]["total"] > 0)  # general rules apply


if __name__ == "__main__":
    unittest.main()
