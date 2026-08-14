from __future__ import annotations

import math
import unittest

from mcm_field_organism.s2_reference_runner import (
    S2N8ABScalarContainer,
    S2N8WorldPairDistance,
    S2ReferenceRunnerError,
    S2ScalarMetric,
    S2WorldPairMetric,
    measure_s2c15_n8_world_pair_distance,
)


_DIGEST_A = "a" * 64
_DIGEST_B = "b" * 64
_DIGEST_C = "c" * 64
_DIGEST_D = "d" * 64


def _container(model_id: str, a_value: float, b_value: float) -> S2N8ABScalarContainer:
    return S2N8ABScalarContainer(
        model_id,
        0.0 if model_id == "b0" else 0.25,
        _DIGEST_C,
        _DIGEST_D,
        31,
        _DIGEST_A,
        _DIGEST_B,
        S2ScalarMetric("d_pair", a_value),
        S2ScalarMetric("d_pair", b_value),
    )


class S2C15N8WorldPairDistanceTests(unittest.TestCase):
    def test_b0_distance_is_exactly_zero_without_decision_fields(self) -> None:
        result = measure_s2c15_n8_world_pair_distance(
            _container("b0", 0.0, 0.0)
        )

        self.assertEqual(0.0, result.d_world_pair)
        self.assertFalse(hasattr(result, "threshold"))
        self.assertFalse(hasattr(result, "decision"))
        self.assertFalse(hasattr(result, "world_specificity"))

    def test_b2_distance_is_absolute_reproducible_scalar(self) -> None:
        container = _container("b2", 0.3, 0.2)
        first = measure_s2c15_n8_world_pair_distance(container)
        second = measure_s2c15_n8_world_pair_distance(container)

        self.assertAlmostEqual(0.1, first.d_world_pair)
        self.assertEqual(first, second)
        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(container.digest(), first.container_digest)

    def test_distance_is_symmetric_in_source_scalar_values(self) -> None:
        first = measure_s2c15_n8_world_pair_distance(
            _container("b2", 0.3, 0.2)
        )
        second = measure_s2c15_n8_world_pair_distance(
            _container("b2", 0.2, 0.3)
        )

        self.assertAlmostEqual(first.d_world_pair, second.d_world_pair)

    def test_measurement_rejects_noncontainer_input(self) -> None:
        with self.assertRaisesRegex(S2ReferenceRunnerError, "bound n=8 A/B"):
            measure_s2c15_n8_world_pair_distance(object())  # type: ignore[arg-type]

    def test_result_rejects_metric_inconsistent_with_sources(self) -> None:
        with self.assertRaisesRegex(S2ReferenceRunnerError, "differs from source"):
            S2N8WorldPairDistance(
                "b2",
                0.25,
                _DIGEST_A,
                _DIGEST_C,
                _DIGEST_D,
                31,
                0.3,
                0.2,
                S2WorldPairMetric("d_world_pair", 0.2),
            )

    def test_metric_rejects_nonfinite_or_wrong_identifier(self) -> None:
        with self.assertRaisesRegex(S2ReferenceRunnerError, "only d_world_pair"):
            S2WorldPairMetric("d_pair", 0.0)
        with self.assertRaisesRegex(S2ReferenceRunnerError, "finite"):
            S2WorldPairMetric("d_world_pair", math.inf)


if __name__ == "__main__":
    unittest.main()
