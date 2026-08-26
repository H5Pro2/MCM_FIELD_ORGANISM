from __future__ import annotations

import inspect
import unittest

from mcm_field_organism.e1_common_probe_small_real_fixture import (
    S1_EC55_ROLES,
    run_e1_common_probe_small_real_fixture,
)


class E1CommonProbeSmallRealFixtureTests(unittest.TestCase):
    def test_scope_is_exactly_three_n2_r2_roles(self) -> None:
        self.assertEqual(
            (
                "p0-reset-ab",
                "e1-active-ab",
                "e1-probe-feedback-ablated-ab",
            ),
            S1_EC55_ROLES,
        )

    def test_runner_has_no_persistence_or_full_matrix_loop(self) -> None:
        source = inspect.getsource(run_e1_common_probe_small_real_fixture)
        for forbidden in ("write_text", "write_bytes", "open(", "for contact_count in", "for refinement in"):
            self.assertNotIn(forbidden, source)
        self.assertIn('(2, "r2", role)', source)
        self.assertIn('"full_matrix_executed": False', source)
        self.assertIn('"research_decision_permitted": False', source)
        self.assertIn('"memory_claim_permitted": False', source)


if __name__ == "__main__":
    unittest.main()
