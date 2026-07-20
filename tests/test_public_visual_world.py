from __future__ import annotations

import unittest

import numpy as np

from mcm_field_organism import (
    LocalChannelGridReceptor,
    PublicVisualReceptorSequence,
    VisualGridConfig,
    observe_public_visual_world,
    public_visual_world_public_roles,
)


CONFIG = VisualGridConfig(
    source_width=8,
    source_height=6,
    grid_columns=4,
    grid_rows=3,
    frames_per_second=8.0,
)


def reduced_sequence() -> tuple[PublicVisualReceptorSequence, LocalChannelGridReceptor]:
    receptor = LocalChannelGridReceptor(CONFIG)
    frames = (
        np.full((6, 8, 3), 32, dtype=np.uint8),
        np.full((6, 8, 3), 96, dtype=np.uint8),
        np.full((6, 8, 3), 224, dtype=np.uint8),
    )
    states = tuple(
        receptor.analyze(frame, frame_index=index)
        for index, frame in enumerate(frames)
    )
    return (
        PublicVisualReceptorSequence(
            states=states,
            source_timestamps_ms=(0, 125, 250),
            sampling_interval_ms=125,
            decoded_frame_count=9,
        ),
        receptor,
    )


class PublicVisualWorldTests(unittest.TestCase):
    def test_reduced_sequence_keeps_only_receptor_states_and_time(self) -> None:
        sequence, _ = reduced_sequence()

        self.assertEqual(3, len(sequence.states))
        self.assertEqual(375, sequence.duration_ms)
        self.assertEqual(9, sequence.decoded_frame_count)
        self.assertEqual(sequence.reduced_digest(), sequence.reduced_digest())

    def test_real_sequence_reaches_field_and_differs_from_static_baseline(self) -> None:
        sequence, receptor = reduced_sequence()

        result = observe_public_visual_world(sequence, sequence, receptor)

        self.assertGreater(result.receptor_value_span_max, 0.0)
        self.assertGreater(result.static_baseline_activation_max_difference, 0.0)
        self.assertGreater(result.static_baseline_afterimage_max_difference, 0.0)
        self.assertTrue(result.exact_reduced_repeat)

    def test_changed_repeat_is_rejected(self) -> None:
        sequence, receptor = reduced_sequence()
        altered_states = list(sequence.states)
        altered_states[-1] = receptor.analyze(
            np.zeros((6, 8, 3), dtype=np.uint8),
            frame_index=2,
        )
        altered = PublicVisualReceptorSequence(
            states=tuple(altered_states),
            source_timestamps_ms=sequence.source_timestamps_ms,
            sampling_interval_ms=125,
            decoded_frame_count=9,
        )

        with self.assertRaisesRegex(ValueError, "did not reproduce"):
            observe_public_visual_world(sequence, altered, receptor)

    def test_public_result_exposes_no_raw_semantic_audio_or_metadata_role(self) -> None:
        forbidden = {
            "frame",
            "frames",
            "pixels",
            "raw_video",
            "audio",
            "title",
            "description",
            "transcript",
            "label",
            "object",
            "meaning",
            "source_url",
            "file_path",
        }
        roles = set(public_visual_world_public_roles())

        self.assertTrue(forbidden.isdisjoint(roles))


if __name__ == "__main__":
    unittest.main()
