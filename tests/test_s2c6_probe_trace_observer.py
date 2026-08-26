from __future__ import annotations

import unittest

from mcm_field_organism.s2_reference_runner import (
    S2ReferenceRunnerError,
    advance_s2c3_r1_world,
    advance_s2c4_r1_probe,
    advance_s2c5_n8_probe,
    advance_s2c5_n8_world,
    observe_s2c6_probe_pair,
)
from mcm_field_organism.s2_reference_worlds import (
    prepare_s2c3_r1_receptor_plan,
    prepare_s2c4_probe_plan,
    prepare_s2c5_n8_receptor_plan,
)


class S2C6ProbeTraceObserverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.r1_plan = prepare_s2c3_r1_receptor_plan()
        cls.n8_plan = prepare_s2c5_n8_receptor_plan()
        cls.probe_plan = prepare_s2c4_probe_plan()
        cls.r1_b0 = advance_s2c3_r1_world(cls.r1_plan, "b0")
        cls.n8_b0 = advance_s2c5_n8_world(cls.n8_plan, "b0")
        cls.r1_b2 = advance_s2c3_r1_world(cls.r1_plan, "b2")
        cls.n8_b2 = advance_s2c5_n8_world(cls.n8_plan, "b2")
        cls.b0_pair = observe_s2c6_probe_pair(
            cls.r1_b0,
            cls.n8_b0,
            cls.probe_plan,
        )
        cls.b2_pair = observe_s2c6_probe_pair(
            cls.r1_b2,
            cls.n8_b2,
            cls.probe_plan,
        )

    def test_probe_support_contains_exactly_31_ordered_completion_ticks(self) -> None:
        expected = tuple(range(8_100_000, 8_400_001, 10_000))

        self.assertEqual(expected, self.b0_pair.history.completion_ticks)
        self.assertEqual(expected, self.b0_pair.neutral.completion_ticks)
        self.assertEqual(expected, self.b2_pair.history.completion_ticks)
        self.assertEqual(expected, self.b2_pair.neutral.completion_ticks)

    def test_every_sample_contains_the_same_84_location_s_h_anatomy(self) -> None:
        traces = (
            self.b0_pair.history,
            self.b0_pair.neutral,
            self.b2_pair.history,
            self.b2_pair.neutral,
        )
        self.assertTrue(
            all(
                len(sample.activation) == len(sample.afterimage) == 84
                for trace in traces
                for sample in trace.samples
            )
        )

    def test_observed_endpoints_equal_the_existing_unobserved_probe_paths(self) -> None:
        expected = (
            advance_s2c4_r1_probe(self.r1_b0, self.probe_plan),
            advance_s2c5_n8_probe(self.n8_b0, self.probe_plan),
            advance_s2c4_r1_probe(self.r1_b2, self.probe_plan),
            advance_s2c5_n8_probe(self.n8_b2, self.probe_plan),
        )
        actual = (
            self.b0_pair.history,
            self.b0_pair.neutral,
            self.b2_pair.history,
            self.b2_pair.neutral,
        )

        self.assertEqual(
            tuple(item.end_snapshot_digest for item in expected),
            tuple(item.end_snapshot_digest for item in actual),
        )

    def test_observed_traces_reproduce_exactly(self) -> None:
        repeated = observe_s2c6_probe_pair(
            self.r1_b2,
            self.n8_b2,
            self.probe_plan,
        )

        self.assertEqual(self.b2_pair, repeated)

    def test_trace_contains_no_metric_distance_or_decision(self) -> None:
        for role in ("metrics", "distance", "d_s", "d_h", "decision"):
            self.assertFalse(hasattr(self.b2_pair, role))
            self.assertFalse(hasattr(self.b2_pair.history, role))
            self.assertFalse(hasattr(self.b2_pair.neutral, role))

    def test_pair_rejects_different_model_arms(self) -> None:
        with self.assertRaisesRegex(S2ReferenceRunnerError, "matching B0 or B2"):
            observe_s2c6_probe_pair(
                self.r1_b0,
                self.n8_b2,
                self.probe_plan,
            )


if __name__ == "__main__":
    unittest.main()
