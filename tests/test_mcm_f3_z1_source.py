from __future__ import annotations

import unittest

from mcm_field_organism.mcm_f3_z1_source import build_mcm_f3_z1_source


class MCMF3Z1SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = build_mcm_f3_z1_source()

    def test_arm_inventory_and_event_budget_are_fixed(self) -> None:
        self.assertEqual(
            (
                "a.reference",
                "a.partitioned",
                "a.stretched",
                "a.compressed",
                "a.reversed",
                "a.permuted",
                "b.independent",
            ),
            tuple(item.arm_id for item in self.source.arms),
        )
        self.assertEqual(1, len({item.event_count for item in self.source.arms}))

    def test_partition_changes_only_proposal_steps(self) -> None:
        reference = self.source.arm("a.reference")
        partitioned = self.source.arm("a.partitioned")
        self.assertEqual(reference.sequence_digest, partitioned.sequence_digest)
        self.assertEqual(reference.sequences, partitioned.sequences)
        self.assertEqual(2 * len(reference.proposal_steps), len(partitioned.proposal_steps))
        self.assertNotEqual(reference.execution_digest, partitioned.execution_digest)

    def test_time_scaling_changes_only_organism_windows(self) -> None:
        reference = self.source.arm("a.reference")
        for arm_id, numerator, denominator in (
            ("a.stretched", 2, 1),
            ("a.compressed", 1, 2),
        ):
            transformed = self.source.arm(arm_id)
            for base_sequence, changed_sequence in zip(
                reference.sequences,
                transformed.sequences,
                strict=True,
            ):
                for base, changed in zip(
                    base_sequence.frames,
                    changed_sequence.frames,
                    strict=True,
                ):
                    self.assertEqual(base.frame, changed.frame)
                    self.assertEqual(
                        base.field_time.window_start_tick * numerator // denominator,
                        changed.field_time.window_start_tick,
                    )
                    self.assertEqual(
                        base.field_time.window_end_tick * numerator // denominator,
                        changed.field_time.window_end_tick,
                    )

    def test_order_controls_retain_target_time_raster(self) -> None:
        reference = self.source.arm("a.reference")
        for arm_id in ("a.reversed", "a.permuted"):
            transformed = self.source.arm(arm_id)
            self.assertNotEqual(reference.sequence_digest, transformed.sequence_digest)
            for base_sequence, changed_sequence in zip(
                reference.sequences,
                transformed.sequences,
                strict=True,
            ):
                self.assertEqual(
                    tuple(item.field_time for item in base_sequence.frames),
                    tuple(item.field_time for item in changed_sequence.frames),
                )
                self.assertCountEqual(
                    (item.frame.snapshot_id for item in base_sequence.frames),
                    (item.frame.snapshot_id for item in changed_sequence.frames),
                )

    def test_independent_control_differs_at_equal_horizon(self) -> None:
        reference = self.source.arm("a.reference")
        independent = self.source.arm("b.independent")
        self.assertNotEqual(reference.sequence_digest, independent.sequence_digest)
        self.assertEqual(reference.event_count, independent.event_count)
        self.assertEqual(reference.end_tick, independent.end_tick)

    def test_source_build_is_deterministic(self) -> None:
        reproduction = build_mcm_f3_z1_source()
        self.assertEqual(
            tuple(item.execution_digest for item in self.source.arms),
            tuple(item.execution_digest for item in reproduction.arms),
        )


if __name__ == "__main__":
    unittest.main()
