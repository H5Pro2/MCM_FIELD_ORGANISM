from __future__ import annotations

import unittest

from mcm_field_organism.snapshot_change_baseline_probe import (
    SnapshotChangeBaselineProbeError,
    SnapshotValueSequence,
    TimedSnapshotValue,
    run_snapshot_change_baseline_probe,
    snapshot_change_baseline_probe_public_roles,
)


class SnapshotChangeBaselineProbeTests(unittest.TestCase):
    def test_monotonic_change_is_invariant_to_exact_rate_split(self) -> None:
        comparison = run_snapshot_change_baseline_probe().monotonic_rate_split
        self.assertEqual(0.0, comparison.signed_change_difference)
        self.assertEqual(0.0, comparison.absolute_change_difference)
        self.assertEqual(0.0, comparison.span_difference_seconds)
        self.assertEqual(1.0, comparison.first.absolute_change_sum)

    def test_return_path_keeps_variation_but_signed_sum_collapses(self) -> None:
        comparison = run_snapshot_change_baseline_probe().return_path_rate_split
        self.assertEqual(0.0, comparison.signed_change_difference)
        self.assertEqual(0.0, comparison.absolute_change_difference)
        self.assertEqual(0.0, comparison.first.signed_change_sum)
        self.assertEqual(2.0, comparison.first.absolute_change_sum)

    def test_duplicate_snapshots_do_not_add_change(self) -> None:
        comparison = run_snapshot_change_baseline_probe().duplicate_density
        self.assertEqual(0.0, comparison.signed_change_difference)
        self.assertEqual(0.0, comparison.absolute_change_difference)
        self.assertNotEqual(
            comparison.first.snapshot_count,
            comparison.second.snapshot_count,
        )

    def test_unobserved_oscillation_is_not_reconstructed(self) -> None:
        comparison = run_snapshot_change_baseline_probe().omitted_oscillation
        self.assertEqual(0.0, comparison.signed_change_difference)
        self.assertEqual(4.0, comparison.absolute_change_difference)
        self.assertEqual(0.0, comparison.second.absolute_change_sum)

    def test_change_measures_do_not_encode_dwell_duration(self) -> None:
        comparison = run_snapshot_change_baseline_probe().unequal_dwell
        self.assertEqual(0.0, comparison.signed_change_difference)
        self.assertEqual(0.0, comparison.absolute_change_difference)
        self.assertEqual(0.8, comparison.span_difference_seconds)

    def test_disordered_or_single_snapshot_sequences_are_rejected(self) -> None:
        with self.assertRaisesRegex(
            SnapshotChangeBaselineProbeError, "at least two"
        ):
            SnapshotValueSequence(
                "single",
                0.1,
                (TimedSnapshotValue(0, 0.0),),
            )
        with self.assertRaisesRegex(
            SnapshotChangeBaselineProbeError, "strictly"
        ):
            SnapshotValueSequence(
                "disordered",
                0.1,
                (
                    TimedSnapshotValue(0, 0.0),
                    TimedSnapshotValue(0, 1.0),
                ),
            )

    def test_public_roles_add_no_buffer_hold_or_field_effect(self) -> None:
        forbidden = {
            "previous_snapshot_buffer",
            "held_value",
            "valid_until",
            "selected_change_measure",
            "field_activation",
            "memory",
            "topology",
            "meaning",
        }
        self.assertTrue(
            forbidden.isdisjoint(snapshot_change_baseline_probe_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
