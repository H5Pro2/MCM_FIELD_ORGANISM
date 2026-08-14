from __future__ import annotations

import unittest

from mcm_field_organism.asynchronous_audio_video_partition_probe import (
    run_asynchronous_audio_video_partition_probe,
)


class AsynchronousAudioVideoPartitionProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_asynchronous_audio_video_partition_probe()

    def test_required_arms_are_present(self) -> None:
        self.assertEqual(
            {
                "w0.coarse",
                "wv.coarse",
                "wa.coarse",
                "wav.coarse",
                "wav.fine",
                "wav.fine.reproduction",
                "wav.fine.permuted",
            },
            {arm.arm_id for arm in self.result.arms},
        )

    def test_source_support_and_horizon_are_matched(self) -> None:
        self.assertTrue(self.result.source_event_counts_equal)
        self.assertTrue(self.result.completion_horizon_equal)
        self.assertEqual(
            1,
            len({arm.final_completion_tick for arm in self.result.arms}),
        )

    def test_reproduction_is_exact(self) -> None:
        self.assertTrue(self.result.reproduction_exact)

    def test_permutation_is_componentwise_invariant(self) -> None:
        self.assertEqual(0.0, self.result.permutation_activation_linf)
        self.assertEqual(0.0, self.result.permutation_afterimage_linf)

    def test_fine_partition_has_more_technical_field_steps(self) -> None:
        by_id = {arm.arm_id: arm for arm in self.result.arms}
        self.assertEqual(1, by_id["wav.coarse"].proposal_step_count)
        self.assertGreater(
            by_id["wav.fine"].proposal_step_count,
            by_id["wav.coarse"].proposal_step_count,
        )


if __name__ == "__main__":
    unittest.main()
