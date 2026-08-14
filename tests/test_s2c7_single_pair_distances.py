from __future__ import annotations

import unittest

from mcm_field_organism.s2_reference_runner import (
    S2ReferenceRunnerError,
    advance_s2c3_r1_world,
    advance_s2c5_n8_world,
    measure_s2c7_single_pair_distances,
    observe_s2c6_probe_pair,
)
from mcm_field_organism.s2_reference_worlds import (
    prepare_s2c3_r1_receptor_plan,
    prepare_s2c4_probe_plan,
    prepare_s2c5_n8_receptor_plan,
)


class S2C7SinglePairDistanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        r1_plan = prepare_s2c3_r1_receptor_plan()
        n8_plan = prepare_s2c5_n8_receptor_plan()
        probe_plan = prepare_s2c4_probe_plan()
        cls.r1_b0 = advance_s2c3_r1_world(r1_plan, "b0")
        cls.n8_b0 = advance_s2c5_n8_world(n8_plan, "b0")
        cls.r1_b2 = advance_s2c3_r1_world(r1_plan, "b2")
        cls.n8_b2 = advance_s2c5_n8_world(n8_plan, "b2")
        cls.b0_traces = observe_s2c6_probe_pair(
            cls.r1_b0,
            cls.n8_b0,
            probe_plan,
        )
        cls.b2_traces = observe_s2c6_probe_pair(
            cls.r1_b2,
            cls.n8_b2,
            probe_plan,
        )
        cls.b0 = measure_s2c7_single_pair_distances(
            cls.r1_b0,
            cls.n8_b0,
            cls.b0_traces,
        )
        cls.b2 = measure_s2c7_single_pair_distances(
            cls.r1_b2,
            cls.n8_b2,
            cls.b2_traces,
        )

    def test_b0_is_an_exact_s_h_null_control_without_l_metric(self) -> None:
        self.assertEqual(("d_s", "d_h"), tuple(item.metric_id for item in self.b0.metrics))
        self.assertEqual(0.0, self.b0.d_s)
        self.assertEqual(0.0, self.b0.d_h)
        self.assertIsNone(self.b0.d_l)

    def test_b2_contains_only_d_l_d_s_and_d_h(self) -> None:
        self.assertEqual(
            ("d_l", "d_s", "d_h"),
            tuple(item.metric_id for item in self.b2.metrics),
        )
        self.assertGreater(self.b2.d_l, 0.0)
        self.assertGreater(self.b2.d_s, 0.0)
        self.assertGreater(self.b2.d_h, 0.0)
        self.assertEqual(31, self.b2.support_count)

    def test_s_h_maxima_equal_direct_reduction_of_all_c6_samples(self) -> None:
        expected_s = max(
            abs(history_value - neutral_value)
            for history_sample, neutral_sample in zip(
                self.b2_traces.history.samples,
                self.b2_traces.neutral.samples,
                strict=True,
            )
            for history_value, neutral_value in zip(
                history_sample.activation,
                neutral_sample.activation,
                strict=True,
            )
        )
        expected_h = max(
            abs(history_value - neutral_value)
            for history_sample, neutral_sample in zip(
                self.b2_traces.history.samples,
                self.b2_traces.neutral.samples,
                strict=True,
            )
            for history_value, neutral_value in zip(
                history_sample.afterimage,
                neutral_sample.afterimage,
                strict=True,
            )
        )

        self.assertEqual(expected_s, self.b2.d_s)
        self.assertEqual(expected_h, self.b2.d_h)

    def test_d_l_equals_pre_equalization_formation_distance(self) -> None:
        expected = max(
            abs(history_value - neutral_value)
            for history_value, neutral_value in zip(
                self.r1_b2.field.development.dispositions,
                self.n8_b2.field.development.dispositions,
                strict=True,
            )
        )

        self.assertEqual(expected, self.b2.d_l)

    def test_scalar_reduction_is_exactly_reproducible_and_has_no_decision(self) -> None:
        repeated = measure_s2c7_single_pair_distances(
            self.r1_b2,
            self.n8_b2,
            self.b2_traces,
        )

        self.assertEqual(self.b2, repeated)
        self.assertFalse(hasattr(self.b2, "decision"))
        self.assertFalse(hasattr(self.b2, "interpretation"))

    def test_mismatched_formations_and_traces_are_rejected(self) -> None:
        with self.assertRaisesRegex(S2ReferenceRunnerError, "share one arm"):
            measure_s2c7_single_pair_distances(
                self.r1_b2,
                self.n8_b2,
                self.b0_traces,
            )


if __name__ == "__main__":
    unittest.main()
