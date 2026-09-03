"""One focused real-fixture regression test for the S2-KK Fast gate."""

from __future__ import annotations

import unittest

from tools import _s2kk_context_utility_fixtures as fixtures
from tools._s2jw_default_live_profile import build_s2jw_default_live_profile


QUALIFICATION_ID = "s2kk-fast-gate-regression-20260903-01"


class S2KKFastSeparationGateTests(unittest.TestCase):
    def test_01_all_real_distractors_use_joint_fast_match_rule(self) -> None:
        stream = fixtures.S2KKFixtureStream(
            build_s2jw_default_live_profile(),
            clock_id="s2kk-fast-gate-regression-clock",
        )
        roles = fixtures.FORMATION_SEQUENCE + ("H_FULL", "H_MASKED")
        reduced = tuple(stream.materialize(role, index) for index, role in enumerate(roles))
        result = fixtures.validate_fast_separation_preflight(reduced)
        self.assertEqual((63, 27, 36, 0), (
            result.relation_count,
            result.anchor_relation_count,
            result.distractor_pair_count,
            result.native_fast_match_count,
        ))
        self.assertTrue(fixtures._fast_separated(0.1, 0.3))
        self.assertTrue(fixtures._fast_separated(0.3, 0.1))
        self.assertFalse(fixtures._fast_separated(0.1, 0.1))


if __name__ == "__main__":
    unittest.main()
