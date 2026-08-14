from __future__ import annotations

import unittest

from mcm_field_organism.controlled_audio_video_test_world import (
    run_controlled_test_world_phases,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from mcm_field_organism.s2_reference_runner import (
    S2ReferenceRunnerError,
    advance_s2c3_r1_world,
    advance_s2c5_n8_world,
    advance_s2c8_c1_world,
    measure_s2c8_c1_identity,
    observe_s2c6_probe_pair,
    observe_s2c8_c1_probe,
)
from mcm_field_organism.s2_reference_worlds import (
    build_s2_reference_worlds,
    prepare_s2c3_r1_receptor_plan,
    prepare_s2c4_probe_plan,
    prepare_s2c5_n8_receptor_plan,
    prepare_s2c8_c1_receptor_plan,
)


class S2C8C1IdentityControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.r1_plan = prepare_s2c3_r1_receptor_plan()
        cls.c1_plan = prepare_s2c8_c1_receptor_plan()
        n8_plan = prepare_s2c5_n8_receptor_plan()
        probe_plan = prepare_s2c4_probe_plan()
        cls.r1_b0 = advance_s2c3_r1_world(cls.r1_plan, "b0")
        cls.r1_b2 = advance_s2c3_r1_world(cls.r1_plan, "b2")
        n8_b0 = advance_s2c5_n8_world(n8_plan, "b0")
        n8_b2 = advance_s2c5_n8_world(n8_plan, "b2")
        cls.c1_b0 = advance_s2c8_c1_world(cls.c1_plan, "b0")
        cls.c1_b2_null = advance_s2c8_c1_world(
            cls.c1_plan,
            "b2",
            coupling_rate_per_second=0.0,
        )
        cls.c1_b2_first = advance_s2c8_c1_world(cls.c1_plan, "b2")
        cls.c1_b2_second = advance_s2c8_c1_world(cls.c1_plan, "b2")
        cls.r1_b0_trace = observe_s2c6_probe_pair(
            cls.r1_b0,
            n8_b0,
            probe_plan,
        ).history
        cls.r1_b2_trace = observe_s2c6_probe_pair(
            cls.r1_b2,
            n8_b2,
            probe_plan,
        ).history
        cls.c1_b0_trace = observe_s2c8_c1_probe(cls.c1_b0, probe_plan)
        cls.c1_b2_trace = observe_s2c8_c1_probe(cls.c1_b2_first, probe_plan)
        cls.b0_identity = measure_s2c8_c1_identity(
            cls.r1_b0_trace,
            cls.c1_b0_trace,
        )
        cls.b2_identity = measure_s2c8_c1_identity(
            cls.r1_b2_trace,
            cls.c1_b2_trace,
        )

    def test_c1_plan_is_distinct_but_value_and_time_identical_to_r1(self) -> None:
        repeated = prepare_s2c8_c1_receptor_plan()

        self.assertEqual(self.c1_plan.digest(), repeated.digest())
        self.assertNotEqual(self.r1_plan.world_digest, self.c1_plan.world_digest)
        self.assertEqual(
            tuple((step.start_tick, step.end_tick) for step in self.r1_plan.proposal_steps),
            tuple((step.start_tick, step.end_tick) for step in self.c1_plan.proposal_steps),
        )
        self.assertEqual(
            tuple(
                tuple(frame.frame.values for frame in sequence.frames)
                for sequence in self.r1_plan.receptor_sequences
            ),
            tuple(
                tuple(frame.frame.values for frame in sequence.frames)
                for sequence in self.c1_plan.receptor_sequences
            ),
        )

    def test_c1_b0_matches_existing_controlled_phase_path_exactly(self) -> None:
        world = {
            item.world_id.removeprefix("s2."): item
            for item in build_s2_reference_worlds()
        }["c1.a"]
        expected = run_controlled_test_world_phases(
            world,
            NeutralLocalFieldSubstrateConfig(1.0),
            afterimage_config=NeutralFastAfterimageConfig(0.5),
            clock_id=self.c1_plan.clock_id,
            ticks_per_second=self.c1_plan.ticks_per_second,
        )[-1].field_run.field

        self.assertEqual(expected.snapshot().digest(), self.c1_b0.end_snapshot_digest)
        self.assertEqual(3, self.c1_b0.batch_count)

    def test_c1_b2_null_and_active_reproduction_are_bound(self) -> None:
        self.assertEqual(
            self.c1_b0.end_snapshot_digest,
            self.c1_b2_null.field.snapshot().fast_state_projection_digest(),
        )
        self.assertEqual(
            self.c1_b2_first.end_snapshot_digest,
            self.c1_b2_second.end_snapshot_digest,
        )

    def test_r1_c1_d_pair_one_is_exactly_zero_for_b0_and_b2(self) -> None:
        self.assertEqual(0.0, self.b0_identity.d_pair)
        self.assertEqual(0.0, self.b2_identity.d_pair)
        self.assertEqual(31, self.b0_identity.support_count)
        self.assertEqual(31, self.b2_identity.support_count)

    def test_c1_trace_is_value_identical_to_r1_on_the_same_probe_support(self) -> None:
        self.assertEqual(
            self.r1_b0_trace.completion_ticks,
            self.c1_b0_trace.completion_ticks,
        )
        self.assertEqual(self.r1_b0_trace.samples, self.c1_b0_trace.samples)
        self.assertEqual(self.r1_b2_trace.samples, self.c1_b2_trace.samples)
        self.assertFalse(hasattr(self.b2_identity, "decision"))

    def test_identity_rejects_different_model_arms(self) -> None:
        with self.assertRaisesRegex(S2ReferenceRunnerError, "matching model arm"):
            measure_s2c8_c1_identity(
                self.r1_b0_trace,
                self.c1_b2_trace,
            )


if __name__ == "__main__":
    unittest.main()
