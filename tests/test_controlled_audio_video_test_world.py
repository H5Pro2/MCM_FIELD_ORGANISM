from __future__ import annotations

import unittest

from mcm_field_organism.controlled_audio_video_test_world import (
    controlled_history_holdout_world_family,
    controlled_reentry_world_family,
    controlled_test_world_public_roles,
    run_controlled_test_world,
    run_controlled_test_world_phases,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)


class ControlledAudioVideoTestWorldTests(unittest.TestCase):
    def test_world_family_is_repeatable_and_geometry_matched(self) -> None:
        same_a, changed_a = controlled_reentry_world_family()
        same_b, changed_b = controlled_reentry_world_family()

        self.assertEqual(same_a.digest(), same_b.digest())
        self.assertEqual(changed_a.digest(), changed_b.digest())
        self.assertNotEqual(same_a.digest(), changed_a.digest())
        self.assertEqual(same_a.audio_config, changed_a.audio_config)
        self.assertEqual(same_a.visual_config, changed_a.visual_config)
        self.assertEqual(3.0, same_a.duration_seconds)

    def test_opening_world_twice_recreates_identical_external_sources(self) -> None:
        same, _ = controlled_reentry_world_family()
        first = same.open_sources()
        second = same.open_sources()

        first_audio = tuple(first[0].read_frame() for _ in range(same.audio_frame_count))
        second_audio = tuple(
            second[0].read_frame() for _ in range(same.audio_frame_count)
        )
        first_video = tuple(
            first[1].read_frame().tobytes() for _ in range(same.video_frame_count)
        )
        second_video = tuple(
            second[1].read_frame().tobytes() for _ in range(same.video_frame_count)
        )

        self.assertEqual(first_audio, second_audio)
        self.assertEqual(first_video, second_video)

    def test_same_and_changed_worlds_share_history_until_reentry(self) -> None:
        same, changed = controlled_reentry_world_family()
        same_sources = same.open_sources()
        changed_sources = changed.open_sources()
        common_audio_frames = round(2.0 / same.audio_config.hop_seconds)
        common_video_frames = round(2.0 * same.visual_config.frames_per_second)

        for _ in range(common_audio_frames):
            self.assertEqual(
                same_sources[0].read_frame(),
                changed_sources[0].read_frame(),
            )
        for _ in range(common_video_frames):
            self.assertEqual(
                same_sources[1].read_frame().tobytes(),
                changed_sources[1].read_frame().tobytes(),
            )

        self.assertNotEqual(
            same_sources[0].read_frame(),
            changed_sources[0].read_frame(),
        )
        self.assertNotEqual(
            same_sources[1].read_frame().tobytes(),
            changed_sources[1].read_frame().tobytes(),
        )

    def test_public_contract_has_no_semantic_or_memory_role(self) -> None:
        roles = set(controlled_test_world_public_roles())
        self.assertTrue(
            {
                "label",
                "meaning",
                "object",
                "class_id",
                "memory",
                "reward",
            }.isdisjoint(roles)
        )

    def test_history_worlds_end_with_the_same_holdout_media(self) -> None:
        same, changed = controlled_history_holdout_world_family()
        same_sources = same.open_sources()
        changed_sources = changed.open_sources()
        first_three_audio = round(3.0 / same.audio_config.hop_seconds)
        first_three_video = round(
            3.0 * same.visual_config.frames_per_second
        )
        for _ in range(first_three_audio):
            same_sources[0].read_frame()
            changed_sources[0].read_frame()
        for _ in range(first_three_video):
            same_sources[1].read_frame()
            changed_sources[1].read_frame()

        for _ in range(
            round(1.0 / same.audio_config.hop_seconds)
        ):
            self.assertEqual(
                same_sources[0].read_frame(),
                changed_sources[0].read_frame(),
            )
        for _ in range(round(same.visual_config.frames_per_second)):
            self.assertEqual(
                same_sources[1].read_frame().tobytes(),
                changed_sources[1].read_frame().tobytes(),
            )

    def test_phase_runner_is_exact_until_the_histories_diverge(self) -> None:
        same, changed = controlled_history_holdout_world_family()
        field_config = NeutralLocalFieldSubstrateConfig(1.0)
        afterimage_config = NeutralFastAfterimageConfig(0.5)
        same_runs = run_controlled_test_world_phases(
            same,
            field_config,
            afterimage_config=afterimage_config,
        )
        changed_runs = run_controlled_test_world_phases(
            changed,
            field_config,
            afterimage_config=afterimage_config,
        )

        self.assertEqual(4, len(same_runs))
        self.assertEqual(
            same_runs[0].field_run.field.snapshot().digest(),
            changed_runs[0].field_run.field.snapshot().digest(),
        )
        self.assertEqual(
            same_runs[1].field_run.field.snapshot().digest(),
            changed_runs[1].field_run.field.snapshot().digest(),
        )
        self.assertNotEqual(
            same_runs[2].field_run.field.snapshot().digest(),
            changed_runs[2].field_run.field.snapshot().digest(),
        )
        self.assertNotEqual(
            same_runs[3].field_run.field.snapshot().digest(),
            changed_runs[3].field_run.field.snapshot().digest(),
        )
        self.assertEqual(4, same_runs[-1].field_run.field.layer.tick)

    def test_world_reaches_the_existing_shared_field_without_raw_retention(self) -> None:
        same, _ = controlled_reentry_world_family()
        result = run_controlled_test_world(
            same,
            NeutralLocalFieldSubstrateConfig(1.0),
            afterimage_config=NeutralFastAfterimageConfig(0.5),
        )

        self.assertEqual(
            ("auditory", "visual"),
            tuple(sequence.modality_id for sequence in result.receptor_sequences),
        )
        self.assertEqual(84, len(result.field_run.field.layer.neurons))
        self.assertGreater(result.field_run.source_support_count, 0)
        self.assertEqual(1, result.field_run.field.layer.neurons[0].tick)
        self.assertFalse(
            hasattr(result, "raw_audio") or hasattr(result, "raw_video")
        )


if __name__ == "__main__":
    unittest.main()
