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
    advance_s2c11_r8c8_world,
    measure_s2c11_r8c8_pair,
    observe_s2c11_r8c8_probe,
)
from mcm_field_organism.s2_reference_worlds import (
    build_s2_reference_worlds,
    prepare_s2c4_probe_plan,
    prepare_s2c11_r8c8_receptor_plans,
)


class S2C11R8C8TimeContrastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.r8_plan, cls.c8_plan = prepare_s2c11_r8c8_receptor_plans()
        probe_plan = prepare_s2c4_probe_plan()
        cls.r8_b0 = advance_s2c11_r8c8_world(cls.r8_plan, "b0")
        cls.c8_b0 = advance_s2c11_r8c8_world(cls.c8_plan, "b0")
        cls.r8_b2_null = advance_s2c11_r8c8_world(
            cls.r8_plan,
            "b2",
            coupling_rate_per_second=0.0,
        )
        cls.c8_b2_null = advance_s2c11_r8c8_world(
            cls.c8_plan,
            "b2",
            coupling_rate_per_second=0.0,
        )
        cls.r8_b2_first = advance_s2c11_r8c8_world(cls.r8_plan, "b2")
        cls.c8_b2_first = advance_s2c11_r8c8_world(cls.c8_plan, "b2")
        cls.r8_b2_second = advance_s2c11_r8c8_world(cls.r8_plan, "b2")
        cls.c8_b2_second = advance_s2c11_r8c8_world(cls.c8_plan, "b2")
        cls.r8_b0_trace = observe_s2c11_r8c8_probe(cls.r8_b0, probe_plan)
        cls.c8_b0_trace = observe_s2c11_r8c8_probe(cls.c8_b0, probe_plan)
        cls.r8_b2_trace = observe_s2c11_r8c8_probe(cls.r8_b2_first, probe_plan)
        cls.c8_b2_trace = observe_s2c11_r8c8_probe(cls.c8_b2_first, probe_plan)
        cls.b0_pair = measure_s2c11_r8c8_pair(
            cls.r8_b0_trace,
            cls.c8_b0_trace,
        )
        cls.b2_pair = measure_s2c11_r8c8_pair(
            cls.r8_b2_trace,
            cls.c8_b2_trace,
        )

    def test_plans_bind_equal_budget_with_seventeen_vs_three_phases(self) -> None:
        repeated = prepare_s2c11_r8c8_receptor_plans()

        self.assertEqual(
            (self.r8_plan.digest(), self.c8_plan.digest()),
            tuple(item.digest() for item in repeated),
        )
        self.assertEqual(17, len(self.r8_plan.proposal_steps))
        self.assertEqual(3, len(self.c8_plan.proposal_steps))
        expected_r8 = [(0, 1_000_000)]
        cursor = 1_000_000
        for _ in range(15):
            expected_r8.append((cursor, cursor + 400_000))
            cursor += 400_000
        expected_r8.append((7_000_000, 8_000_000))
        self.assertEqual(
            tuple(expected_r8),
            tuple((item.start_tick, item.end_tick) for item in self.r8_plan.proposal_steps),
        )
        self.assertEqual(
            (
                (0, 2_400_000),
                (2_400_000, 5_600_000),
                (5_600_000, 8_000_000),
            ),
            tuple((item.start_tick, item.end_tick) for item in self.c8_plan.proposal_steps),
        )
        self.assertEqual(871, self.r8_plan.source_support_count)
        self.assertEqual(871, self.c8_plan.source_support_count)

    def test_b0_paths_match_existing_controlled_world_paths_exactly(self) -> None:
        worlds = {
            item.world_id.removeprefix("s2."): item
            for item in build_s2_reference_worlds()
        }
        for plan, result in (
            (self.r8_plan, self.r8_b0),
            (self.c8_plan, self.c8_b0),
        ):
            expected = run_controlled_test_world_phases(
                worlds[plan.world_id],
                NeutralLocalFieldSubstrateConfig(1.0),
                afterimage_config=NeutralFastAfterimageConfig(0.5),
                clock_id=plan.clock_id,
                ticks_per_second=plan.ticks_per_second,
            )[-1].field_run.field
            self.assertEqual(expected.snapshot().digest(), result.end_snapshot_digest)

    def test_b2_null_arms_have_exact_b0_fast_projections(self) -> None:
        self.assertEqual(
            self.r8_b0.end_snapshot_digest,
            self.r8_b2_null.field.snapshot().fast_state_projection_digest(),
        )
        self.assertEqual(
            self.c8_b0.end_snapshot_digest,
            self.c8_b2_null.field.snapshot().fast_state_projection_digest(),
        )

    def test_active_b2_r8_and_c8_reproduce_exactly(self) -> None:
        self.assertEqual(
            self.r8_b2_first.end_snapshot_digest,
            self.r8_b2_second.end_snapshot_digest,
        )
        self.assertEqual(
            self.c8_b2_first.end_snapshot_digest,
            self.c8_b2_second.end_snapshot_digest,
        )

    def test_b0_d_pair_eight_is_exactly_zero(self) -> None:
        self.assertEqual(0.0, self.b0_pair.d_pair)
        self.assertEqual(self.r8_b0_trace.samples, self.c8_b0_trace.samples)
        self.assertEqual(31, self.b0_pair.support_count)

    def test_b2_time_structure_effect_is_finite_positive_and_reproducible(self) -> None:
        repeated = measure_s2c11_r8c8_pair(
            observe_s2c11_r8c8_probe(
                self.r8_b2_second,
                prepare_s2c4_probe_plan(),
            ),
            observe_s2c11_r8c8_probe(
                self.c8_b2_second,
                prepare_s2c4_probe_plan(),
            ),
        )

        self.assertGreater(self.b2_pair.d_pair, 0.0)
        self.assertEqual(self.b2_pair, repeated)
        self.assertFalse(hasattr(self.b2_pair, "decision"))

    def test_pair_rejects_different_model_arms(self) -> None:
        with self.assertRaisesRegex(S2ReferenceRunnerError, "matching model arm"):
            measure_s2c11_r8c8_pair(
                self.r8_b0_trace,
                self.c8_b2_trace,
            )


if __name__ == "__main__":
    unittest.main()
