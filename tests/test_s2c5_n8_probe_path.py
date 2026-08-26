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
    advance_s2c5_n8_probe,
    advance_s2c5_n8_world,
)
from mcm_field_organism.s2_reference_worlds import (
    build_s2_reference_worlds,
    prepare_s2c4_probe_plan,
    prepare_s2c5_n8_receptor_plan,
)


class S2C5N8ProbePathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.formation_plan = prepare_s2c5_n8_receptor_plan()
        cls.probe_plan = prepare_s2c4_probe_plan()
        cls.b0_formation = advance_s2c5_n8_world(cls.formation_plan, "b0")
        cls.b2_null_formation = advance_s2c5_n8_world(
            cls.formation_plan,
            "b2",
            coupling_rate_per_second=0.0,
        )
        cls.b2_formation_first = advance_s2c5_n8_world(
            cls.formation_plan,
            "b2",
        )
        cls.b2_formation_second = advance_s2c5_n8_world(
            cls.formation_plan,
            "b2",
        )
        cls.b0_probe = advance_s2c5_n8_probe(cls.b0_formation, cls.probe_plan)
        cls.b2_null_probe = advance_s2c5_n8_probe(
            cls.b2_null_formation,
            cls.probe_plan,
        )
        cls.b2_probe_first = advance_s2c5_n8_probe(
            cls.b2_formation_first,
            cls.probe_plan,
        )
        cls.b2_probe_second = advance_s2c5_n8_probe(
            cls.b2_formation_second,
            cls.probe_plan,
        )

    def test_n8_plan_is_deterministic_one_batch_and_complete(self) -> None:
        repeated = prepare_s2c5_n8_receptor_plan()

        self.assertEqual("n8", self.formation_plan.world_id)
        self.assertEqual(self.formation_plan.digest(), repeated.digest())
        self.assertEqual(0, self.formation_plan.proposal_step.start_tick)
        self.assertEqual(8_000_000, self.formation_plan.proposal_step.end_tick)
        self.assertEqual(791, len(self.formation_plan.receptor_sequences[0].frames))
        self.assertEqual(80, len(self.formation_plan.receptor_sequences[1].frames))
        self.assertEqual(871, self.formation_plan.source_support_count)
        self.assertEqual(1, self.b0_formation.batch_count)
        self.assertEqual(
            self.b0_formation.source_support_count,
            self.b0_formation.assigned_support_count,
        )

    def test_n8_b0_matches_existing_controlled_phase_path_exactly(self) -> None:
        world = {
            item.world_id.removeprefix("s2."): item
            for item in build_s2_reference_worlds()
        }["n8"]
        expected = run_controlled_test_world_phases(
            world,
            NeutralLocalFieldSubstrateConfig(1.0),
            afterimage_config=NeutralFastAfterimageConfig(0.5),
            clock_id=self.formation_plan.clock_id,
            ticks_per_second=self.formation_plan.ticks_per_second,
        )[-1].field_run.field

        self.assertEqual(expected.snapshot().digest(), self.b0_formation.end_snapshot_digest)

    def test_n8_b2_null_has_exact_b0_fast_projection_before_and_after_probe(self) -> None:
        self.assertEqual(
            self.b0_formation.end_snapshot_digest,
            self.b2_null_formation.field.snapshot().fast_state_projection_digest(),
        )
        self.assertEqual(
            self.b0_probe.end_snapshot_digest,
            self.b2_null_probe.field.snapshot().fast_state_projection_digest(),
        )
        self.assertTrue(
            all(
                value == 0.0
                for value in self.b2_null_probe.field.development.dispositions
            )
        )

    def test_active_n8_b2_formation_and_probe_reproduce_exactly(self) -> None:
        self.assertEqual(
            self.b2_formation_first.end_snapshot_digest,
            self.b2_formation_second.end_snapshot_digest,
        )
        self.assertEqual(
            self.b2_probe_first.end_snapshot_digest,
            self.b2_probe_second.end_snapshot_digest,
        )
        self.assertEqual(
            self.b2_formation_first.field.development.digest(),
            self.b2_probe_first.development_digest_before_probe,
        )

    def test_n8_uses_same_probe_without_scalar_comparison_or_decision(self) -> None:
        results = (
            self.b0_probe,
            self.b2_null_probe,
            self.b2_probe_first,
            self.b2_probe_second,
        )
        self.assertEqual(
            {self.probe_plan.digest()},
            {item.probe_plan_digest for item in results},
        )
        self.assertEqual(
            {self.probe_plan.probe_digest},
            {item.probe_digest for item in results},
        )
        self.assertTrue(
            all(
                item.probe_support_count == item.assigned_probe_support_count == 35
                for item in results
            )
        )
        self.assertFalse(hasattr(self.b2_probe_first, "metrics"))
        self.assertFalse(hasattr(self.b2_probe_first, "decision"))

    def test_r1_and_n8_entrypoints_remain_type_separated(self) -> None:
        with self.assertRaisesRegex(S2ReferenceRunnerError, "canonical r1.a plan"):
            advance_s2c3_r1_world(self.formation_plan, "b0")
        with self.assertRaisesRegex(S2ReferenceRunnerError, "only B0 or B2"):
            advance_s2c5_n8_world(self.formation_plan, "b1")


if __name__ == "__main__":
    unittest.main()
