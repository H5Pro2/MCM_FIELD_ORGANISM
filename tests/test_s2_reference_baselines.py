from __future__ import annotations

import math
import unittest

import numpy as np

from mcm_field_organism.s2_reference_baselines import (
    S2ReferenceBaselineError,
    S2ReferenceModelConfig,
    S2ReferenceState,
    advance_s2_reference_model,
)


ZERO_STATE = S2ReferenceState((0.0,), (0.0,), (0.0,))
CONFIG = S2ReferenceModelConfig()


class S2ReferenceBaselineTests(unittest.TestCase):
    def test_all_models_preserve_the_exact_zero_fixture(self) -> None:
        generator = np.zeros((1, 1))
        boundary = np.zeros(1)

        for model_id in ("b0", "b1", "b2", "b3", "b4", "b5"):
            result = advance_s2_reference_model(
                model_id, ZERO_STATE, generator, boundary, 1.0, CONFIG
            )
            self.assertEqual(ZERO_STATE, result.state)
            self.assertEqual(0.0, result.partition_error)

    def test_b0_matches_scalar_affine_solution_and_retains_l(self) -> None:
        state = S2ReferenceState((0.0,), (0.0,), (0.3,))
        result = advance_s2_reference_model(
            "b0", state, np.asarray([[-1.0]]), np.asarray([1.0]), 1.0, CONFIG
        ).state

        self.assertAlmostEqual(1.0 - math.exp(-1.0), result.activation[0], places=14)
        self.assertEqual((0.3,), result.development)

    def test_b2_closes_capacity_weighted_exchange_without_external_drive(self) -> None:
        state = S2ReferenceState((0.6,), (0.0,), (0.1,))
        result = advance_s2_reference_model(
            "b2", state, np.zeros((1, 1)), np.zeros(1), 2.0, CONFIG
        ).state

        before = state.activation[0] + 8.0 * state.development[0]
        after = result.activation[0] + 8.0 * result.development[0]
        self.assertAlmostEqual(before, after, places=13)

    def test_b3_uses_the_bound_tanh_integral(self) -> None:
        result = advance_s2_reference_model(
            "b3", ZERO_STATE, np.zeros((1, 1)), np.asarray([0.4]), 1.0, CONFIG
        ).state

        self.assertAlmostEqual(0.4, result.activation[0], places=14)
        self.assertAlmostEqual(math.tanh((0.25 / 8.0) * 0.2), result.development[0], places=14)

    def test_b5_removes_l_to_s_effect(self) -> None:
        first = S2ReferenceState((0.2,), (0.0,), (-0.8,))
        second = S2ReferenceState((0.2,), (0.0,), (0.8,))
        first_out = advance_s2_reference_model(
            "b5", first, np.zeros((1, 1)), np.zeros(1), 1.0, CONFIG
        ).state
        second_out = advance_s2_reference_model(
            "b5", second, np.zeros((1, 1)), np.zeros(1), 1.0, CONFIG
        ).state

        self.assertEqual(first_out.activation, second_out.activation)
        self.assertNotEqual(first_out.development, second_out.development)

    def test_b4_reports_fixed_partition_control(self) -> None:
        state = S2ReferenceState((0.2,), (0.1,), (0.3,))
        result = advance_s2_reference_model(
            "b4", state, np.asarray([[-0.5]]), np.asarray([0.1]), 0.01, CONFIG
        )

        self.assertGreaterEqual(result.partition_error, 0.0)
        self.assertLessEqual(result.partition_error, 2e-12)

    def test_invalid_shapes_and_unknown_models_stop_before_integration(self) -> None:
        with self.assertRaises(S2ReferenceBaselineError):
            advance_s2_reference_model(
                "b6", ZERO_STATE, np.zeros((1, 1)), np.zeros(1), 1.0, CONFIG
            )
        with self.assertRaises(S2ReferenceBaselineError):
            advance_s2_reference_model(
                "b0", ZERO_STATE, np.zeros((2, 2)), np.zeros(2), 1.0, CONFIG
            )


if __name__ == "__main__":
    unittest.main()
