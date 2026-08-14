from __future__ import annotations

import unittest

from mcm_field_organism.current_api import (
    W7BLinearHistoryDiscriminationError,
    W7BLinearHistoryDiscriminationResult,
    run_w7b_linear_history_discrimination,
)


class W7BLinearHistoryDiscriminationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_w7b_linear_history_discrimination()

    def test_linear_reciprocal_trace_is_sufficient_for_r8_c8(self) -> None:
        self.assertEqual(
            "LINEAR_RECIPROCAL_TRACE_SUFFICIENT",
            self.result.technical_decision,
        )
        self.assertEqual(0.0, self.result.d_pair_b0)
        self.assertEqual(0.0, self.result.d_pair_b1)
        self.assertGreater(self.result.l_pair_b1, self.result.tolerance)
        self.assertGreater(self.result.l_pair_b2, self.result.tolerance)
        self.assertGreater(self.result.d_pair_b2, self.result.tolerance)
        self.assertLessEqual(
            self.result.b2_reference_error,
            self.result.tolerance,
        )

    def test_support_and_controls_remain_bounded(self) -> None:
        self.assertEqual(871, self.result.formation_support_count_r8)
        self.assertEqual(871, self.result.formation_support_count_c8)
        self.assertEqual(31, self.result.probe_support_count)
        self.assertTrue(self.result.b0_exact)
        self.assertTrue(self.result.b1_no_feedback_effect)
        self.assertTrue(self.result.b2_production_reproduced)
        self.assertTrue(self.result.finite_scalars)

    def test_result_retains_no_trajectory_and_writes_nothing(self) -> None:
        payload = self.result.canonical_payload()
        self.assertFalse(self.result.raw_trajectories_retained)
        self.assertFalse(self.result.report_written)
        self.assertFalse(self.result.browser_started)
        self.assertFalse(any("trace" in role for role in payload))
        self.assertEqual(64, len(self.result.digest()))

    def test_result_rejects_a_claim_with_incomplete_controls(self) -> None:
        payload = self.result.canonical_payload()
        payload["b1_no_feedback_effect"] = False
        with self.assertRaisesRegex(
            W7BLinearHistoryDiscriminationError,
            "controls failed",
        ):
            W7BLinearHistoryDiscriminationResult(**payload)


if __name__ == "__main__":
    unittest.main()
