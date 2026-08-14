from __future__ import annotations

import unittest

from mcm_field_organism.controlled_audio_video_test_world import (
    controlled_history_holdout_world_family,
    run_controlled_test_world_phases,
)
from mcm_field_organism.controlled_probe_baseline_comparison import (
    ControlledProbeComparisonError,
    compare_controlled_probe_baseline_set,
    compare_controlled_probe_snapshots,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)


class ControlledProbeBaselineComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        worlds = controlled_history_holdout_world_family()
        config = NeutralLocalFieldSubstrateConfig(1.0)
        afterimage = NeutralFastAfterimageConfig(0.5)
        runs = tuple(
            run_controlled_test_world_phases(
                world,
                config,
                afterimage_config=afterimage,
            )
            for world in worlds
        )
        cls.same_probe = runs[0][-1].field_run.field.snapshot()
        cls.changed_probe = runs[1][-1].field_run.field.snapshot()

    def test_comparison_is_passive_and_reports_numeric_distances(self) -> None:
        result = compare_controlled_probe_snapshots(
            "same",
            self.same_probe,
            "changed",
            self.changed_probe,
        )

        self.assertTrue(result.same_geometry)
        self.assertTrue(result.same_clock)
        self.assertFalse(result.snapshot_digest_equal)
        self.assertGreater(result.activation_linf, 0.0)
        self.assertGreater(result.afterimage_linf, 0.0)

    def test_identical_snapshot_compares_equal(self) -> None:
        result = compare_controlled_probe_snapshots(
            "same",
            self.same_probe,
            "same-copy",
            self.same_probe,
        )

        self.assertTrue(result.snapshot_digest_equal)
        self.assertEqual(0.0, result.activation_linf)
        self.assertEqual(0.0, result.afterimage_linf)

    def test_baseline_set_is_compared_in_declared_order(self) -> None:
        results = compare_controlled_probe_baseline_set(
            self.same_probe,
            (
                ("null", self.same_probe),
                ("changed", self.changed_probe),
            ),
        )

        self.assertEqual(("null", "changed"), tuple(item.candidate_id for item in results))
        self.assertTrue(results[0].snapshot_digest_equal)
        self.assertFalse(results[1].snapshot_digest_equal)

    def test_empty_baseline_set_is_rejected(self) -> None:
        with self.assertRaises(ControlledProbeComparisonError):
            compare_controlled_probe_baseline_set(self.same_probe, ())

    def test_invalid_comparison_id_is_rejected(self) -> None:
        with self.assertRaises(ControlledProbeComparisonError):
            compare_controlled_probe_snapshots(
                "",
                self.same_probe,
                "altered",
                self.changed_probe,
            )


if __name__ == "__main__":
    unittest.main()
