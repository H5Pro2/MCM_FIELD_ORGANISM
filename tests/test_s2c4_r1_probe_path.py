from __future__ import annotations

import unittest

from mcm_field_organism.s2_reference_runner import (
    advance_s2c3_r1_world,
    advance_s2c4_r1_probe,
    equalize_fast_state_for_probe,
)
from mcm_field_organism.s2_reference_worlds import (
    prepare_s2c3_r1_receptor_plan,
    prepare_s2c4_probe_plan,
)


class S2C4R1ProbePathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.formation_plan = prepare_s2c3_r1_receptor_plan()
        cls.probe_plan = prepare_s2c4_probe_plan()
        cls.b0_formation = advance_s2c3_r1_world(cls.formation_plan, "b0")
        cls.b2_null_formation = advance_s2c3_r1_world(
            cls.formation_plan,
            "b2",
            coupling_rate_per_second=0.0,
        )
        cls.b2_formation_first = advance_s2c3_r1_world(
            cls.formation_plan,
            "b2",
        )
        cls.b2_formation_second = advance_s2c3_r1_world(
            cls.formation_plan,
            "b2",
        )
        cls.b0_probe = advance_s2c4_r1_probe(
            cls.b0_formation,
            cls.probe_plan,
        )
        cls.b2_null_probe = advance_s2c4_r1_probe(
            cls.b2_null_formation,
            cls.probe_plan,
        )
        cls.b2_probe_first = advance_s2c4_r1_probe(
            cls.b2_formation_first,
            cls.probe_plan,
        )
        cls.b2_probe_second = advance_s2c4_r1_probe(
            cls.b2_formation_second,
            cls.probe_plan,
        )

    def test_probe_plan_is_deterministic_and_fixed_to_8_through_8_4_seconds(self) -> None:
        repeated = prepare_s2c4_probe_plan()

        self.assertEqual(self.probe_plan.digest(), repeated.digest())
        self.assertEqual(8_000_000, self.probe_plan.proposal_step.start_tick)
        self.assertEqual(8_400_000, self.probe_plan.proposal_step.end_tick)
        self.assertEqual(31, len(self.probe_plan.receptor_sequences[0].frames))
        self.assertEqual(4, len(self.probe_plan.receptor_sequences[1].frames))
        self.assertEqual(35, self.probe_plan.source_support_count)

    def test_fast_state_equalization_also_supports_plain_b0(self) -> None:
        equalized = equalize_fast_state_for_probe(self.b0_formation.field)

        self.assertIsNone(equalized.development)
        self.assertTrue(all(item.activation == 0.0 for item in equalized.layer.neurons))
        self.assertTrue(all(item.afterimage == 0.0 for item in equalized.layer.neurons))
        self.assertEqual(self.b0_formation.field.layer.tick, equalized.layer.tick)
        self.assertEqual(
            self.b0_formation.field.last_distribution,
            equalized.last_distribution,
        )

    def test_b2_null_probe_has_the_exact_b0_fast_projection(self) -> None:
        self.assertEqual(
            self.b0_probe.end_snapshot_digest,
            self.b2_null_probe.field.snapshot().fast_state_projection_digest(),
        )
        self.assertTrue(
            all(value == 0.0 for value in self.b2_null_probe.field.development.dispositions)
        )

    def test_active_b2_formation_and_probe_reproduce_digest_exactly(self) -> None:
        self.assertEqual(
            self.b2_probe_first.end_snapshot_digest,
            self.b2_probe_second.end_snapshot_digest,
        )
        self.assertEqual(
            self.b2_formation_first.field.development.digest(),
            self.b2_probe_first.development_digest_before_probe,
        )

    def test_every_branch_uses_the_same_probe_and_complete_support(self) -> None:
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
                item.probe_support_count == item.assigned_probe_support_count
                for item in results
            )
        )
        self.assertTrue(all(item.field.layer.tick == 4 for item in results))
        self.assertTrue(
            all(
                item.field.last_distribution.field_time.window_end_tick == 8_400_000
                for item in results
            )
        )


if __name__ == "__main__":
    unittest.main()
