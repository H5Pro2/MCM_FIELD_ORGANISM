from __future__ import annotations

import math
import threading
import unittest

import numpy as np

from mcm_field_organism.current_api import (
    BroadbandHearingPath,
    LocalChannelGridReceptor,
    LogSpectralConfig,
    LogSpectralReceptor,
    NeutralLocalFieldSubstrateConfig,
    SharedMCMField,
    SharedMCMFieldSnapshot,
    SyntheticAudioFrameSource,
    SyntheticVideoFrameSource,
    VisualGridConfig,
    advance_audio_video_receptor_sequences,
    capture_audio_video_into_neutral_field,
    restore_shared_mcm_field,
)


class IncrementingConsumerClock:
    def __init__(self) -> None:
        self._tick = 0
        self._lock = threading.Lock()

    def __call__(self) -> int:
        with self._lock:
            tick = self._tick
            self._tick += 1
            return tick


def consumer_components(repetitions: int = 1):
    audio_config = LogSpectralConfig(
        sample_rate=1000,
        window_size=100,
        hop_size=20,
        min_frequency=10.0,
        max_frequency=400.0,
        band_count=4,
    )
    audio_frames = tuple(
        tuple(
            0.25
            * math.sin(
                2.0 * math.pi * 100.0 * sample / audio_config.sample_rate
            )
            for sample in range(index * 20, (index + 1) * 20)
        )
        for index in range(10 * repetitions)
    )
    visual_config = VisualGridConfig(
        source_width=12,
        source_height=8,
        grid_columns=2,
        grid_rows=2,
        frames_per_second=10.0,
    )
    visual_frames = tuple(
        np.full(
            (8, 12, 3),
            32 if index % 2 == 0 else 224,
            dtype=np.uint8,
        )
        for index in range(2 * repetitions)
    )
    return (
        SyntheticAudioFrameSource(audio_frames),
        SyntheticVideoFrameSource(visual_frames),
        BroadbandHearingPath(LogSpectralReceptor(audio_config)),
        LocalChannelGridReceptor(visual_config),
    )


class CurrentAPIEndToEndConsumerTests(unittest.TestCase):
    def test_controlled_av_field_snapshot_restore_uses_only_current_api(self) -> None:
        result = capture_audio_video_into_neutral_field(
            *consumer_components(),
            NeutralLocalFieldSubstrateConfig(1.0),
            nominal_duration_seconds=0.2,
            clock=IncrementingConsumerClock(),
            clock_id="organism.current_api.test",
            ticks_per_second=1000.0,
        )

        self.assertEqual(
            (6, 2),
            tuple(len(sequence.frames) for sequence in result.receptor_sequences),
        )
        self.assertEqual(8, result.field_run.source_support_count)
        self.assertEqual(8, result.field_run.handoff.assigned_event_count)
        snapshot = result.field_run.field.snapshot()
        restored = restore_shared_mcm_field(snapshot)
        self.assertEqual(1, snapshot.schema_version)
        self.assertEqual(
            {"schema_version", "layer", "docks", "last_distribution"},
            set(snapshot.canonical_payload()),
        )
        self.assertIsInstance(restored, SharedMCMField)
        self.assertEqual(snapshot.digest(), restored.snapshot().digest())
        self.assertIsNone(restored.substrate)
        self.assertIsNone(restored.development)

    def test_restored_field_matches_uninterrupted_identical_continuation(self) -> None:
        components = consumer_components(repetitions=2)
        audio_source, video_source, auditory_path, visual_receptor = components
        field_config = NeutralLocalFieldSubstrateConfig(1.0)
        clock = IncrementingConsumerClock()
        first = capture_audio_video_into_neutral_field(
            *components,
            field_config,
            nominal_duration_seconds=0.2,
            clock=clock,
            clock_id="organism.current_api.test",
            ticks_per_second=1000.0,
        )
        first_snapshot = first.field_run.field.snapshot()
        restored = restore_shared_mcm_field(first_snapshot)

        uninterrupted = capture_audio_video_into_neutral_field(
            audio_source,
            video_source,
            auditory_path,
            visual_receptor,
            field_config,
            initial_field=first.field_run.field,
            auditory_path_must_be_fresh=False,
            visual_frame_index_start=2,
            nominal_duration_seconds=0.2,
            clock=clock,
            clock_id="organism.current_api.test",
            ticks_per_second=1000.0,
        )
        resumed = advance_audio_video_receptor_sequences(
            uninterrupted.receptor_sequences,
            visual_receptor,
            field_config,
            initial_field=restored,
            ticks_per_second=1000.0,
        )

        self.assertEqual(
            (10, 2),
            tuple(
                len(sequence.frames)
                for sequence in uninterrupted.receptor_sequences
            ),
        )
        self.assertEqual(
            uninterrupted.field_run.field.snapshot().digest(),
            resumed.field_run.field.snapshot().digest(),
        )
        self.assertEqual(
            first_snapshot.digest(),
            first.field_run.field.snapshot().digest(),
        )

    def test_json_restored_field_matches_identical_continuation(self) -> None:
        components = consumer_components(repetitions=2)
        audio_source, video_source, auditory_path, visual_receptor = components
        field_config = NeutralLocalFieldSubstrateConfig(1.0)
        clock = IncrementingConsumerClock()
        first = capture_audio_video_into_neutral_field(
            *components,
            field_config,
            nominal_duration_seconds=0.2,
            clock=clock,
            clock_id="organism.current_api.test",
            ticks_per_second=1000.0,
        )
        first_snapshot = first.field_run.field.snapshot()
        encoded = first_snapshot.to_json()
        decoded = SharedMCMFieldSnapshot.from_json(encoded)
        restored = restore_shared_mcm_field(decoded)

        uninterrupted = capture_audio_video_into_neutral_field(
            audio_source,
            video_source,
            auditory_path,
            visual_receptor,
            field_config,
            initial_field=first.field_run.field,
            auditory_path_must_be_fresh=False,
            visual_frame_index_start=2,
            nominal_duration_seconds=0.2,
            clock=clock,
            clock_id="organism.current_api.test",
            ticks_per_second=1000.0,
        )
        resumed = advance_audio_video_receptor_sequences(
            uninterrupted.receptor_sequences,
            visual_receptor,
            field_config,
            initial_field=restored,
            ticks_per_second=1000.0,
        )

        self.assertIsInstance(encoded, str)
        self.assertEqual(encoded, decoded.to_json())
        self.assertEqual(first_snapshot.digest(), decoded.digest())
        self.assertEqual(
            uninterrupted.field_run.field.snapshot().digest(),
            resumed.field_run.field.snapshot().digest(),
        )


if __name__ == "__main__":
    unittest.main()
