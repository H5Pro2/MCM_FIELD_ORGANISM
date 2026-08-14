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
)
from mcm_field_organism.s2_reference_worlds import (
    build_s2_reference_worlds,
    prepare_s2c3_r1_receptor_plan,
)


FIELD_CONFIG = NeutralLocalFieldSubstrateConfig(1.0)
AFTERIMAGE_CONFIG = NeutralFastAfterimageConfig(0.5)


class S2C3R1WorldAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = prepare_s2c3_r1_receptor_plan()
        cls.b0 = advance_s2c3_r1_world(
            cls.plan,
            "b0",
            FIELD_CONFIG,
            AFTERIMAGE_CONFIG,
        )
        cls.b2_null = advance_s2c3_r1_world(
            cls.plan,
            "b2",
            FIELD_CONFIG,
            AFTERIMAGE_CONFIG,
            coupling_rate_per_second=0.0,
        )
        cls.b2_first = advance_s2c3_r1_world(
            cls.plan,
            "b2",
            FIELD_CONFIG,
            AFTERIMAGE_CONFIG,
        )
        cls.b2_second = advance_s2c3_r1_world(
            cls.plan,
            "b2",
            FIELD_CONFIG,
            AFTERIMAGE_CONFIG,
        )

    def test_plan_is_deterministic_contiguous_and_offsettable(self) -> None:
        repeated = prepare_s2c3_r1_receptor_plan()
        shifted = prepare_s2c3_r1_receptor_plan(start_seconds=2.0)

        self.assertEqual("r1.a", self.plan.world_id)
        self.assertEqual(self.plan.digest(), repeated.digest())
        self.assertEqual(3, len(self.plan.proposal_steps))
        self.assertEqual(0, self.plan.proposal_steps[0].start_tick)
        self.assertEqual(8_000_000, self.plan.proposal_steps[-1].end_tick)
        self.assertEqual(2_000_000, shifted.proposal_steps[0].start_tick)
        self.assertEqual(10_000_000, shifted.proposal_steps[-1].end_tick)
        self.assertEqual(self.plan.world_digest, shifted.world_digest)
        self.assertNotEqual(self.plan.sequence_digests, shifted.sequence_digests)

    def test_b0_matches_the_existing_controlled_phase_path_exactly(self) -> None:
        world = {
            item.world_id.removeprefix("s2."): item
            for item in build_s2_reference_worlds()
        }["r1.a"]
        expected = run_controlled_test_world_phases(
            world,
            FIELD_CONFIG,
            afterimage_config=AFTERIMAGE_CONFIG,
            clock_id=self.plan.clock_id,
            ticks_per_second=self.plan.ticks_per_second,
        )[-1].field_run.field

        self.assertEqual(expected.snapshot().digest(), self.b0.end_snapshot_digest)
        self.assertEqual(self.plan.source_support_count, self.b0.source_support_count)
        self.assertEqual(3, self.b0.batch_count)

    def test_zero_coupling_b2_has_the_exact_b0_fast_projection(self) -> None:
        self.assertEqual(
            self.b0.end_snapshot_digest,
            self.b2_null.field.snapshot().fast_state_projection_digest(),
        )
        self.assertTrue(
            all(value == 0.0 for value in self.b2_null.field.development.dispositions)
        )

    def test_active_b2_reproduction_is_digest_exact(self) -> None:
        self.assertEqual(
            self.b2_first.end_snapshot_digest,
            self.b2_second.end_snapshot_digest,
        )
        self.assertEqual(self.b2_first.plan_digest, self.plan.digest())
        self.assertEqual(0.25, self.b2_first.coupling_rate_per_second)

    def test_adapter_rejects_unregistered_models_before_world_advance(self) -> None:
        with self.assertRaisesRegex(S2ReferenceRunnerError, "only B0 or B2"):
            advance_s2c3_r1_world(
                self.plan,
                "b1",
                FIELD_CONFIG,
                AFTERIMAGE_CONFIG,
            )


if __name__ == "__main__":
    unittest.main()
