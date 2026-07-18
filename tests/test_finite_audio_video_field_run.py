from __future__ import annotations

from dataclasses import fields
import time
import unittest

import numpy as np

from mcm_field_organism.broadband_hearing_path import BroadbandHearingPath
from mcm_field_organism.finite_audio_video_field_run import (
    FiniteAudioVideoFieldError,
    FiniteAudioVideoFieldResult,
    audio_video_dock_anatomies,
    capture_finite_audio_video_field,
)
from mcm_field_organism.finite_video_path import (
    LocalChannelGridReceptor,
    SyntheticVideoFrameSource,
    VisualGridConfig,
)
from mcm_field_organism.live_audio_adapter import SyntheticAudioFrameSource
from mcm_field_organism.log_spectral_receptor import (
    LogSpectralConfig,
    LogSpectralReceptor,
)


class DelayedAudioSource:
    def __init__(
        self,
        source: SyntheticAudioFrameSource,
        delay_seconds: float,
    ) -> None:
        self.source = source
        self.delay_seconds = delay_seconds

    @property
    def overflow_count(self) -> int:
        return self.source.overflow_count

    def read_frame(self) -> tuple[float, ...]:
        time.sleep(self.delay_seconds)
        return self.source.read_frame()


class DelayedVideoSource:
    def __init__(
        self,
        source: SyntheticVideoFrameSource,
        delay_seconds: float,
    ) -> None:
        self.source = source
        self.delay_seconds = delay_seconds

    def read_frame(self) -> np.ndarray:
        time.sleep(self.delay_seconds)
        return self.source.read_frame()


def fixture():
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
            0.25 * np.sin(2.0 * np.pi * 100.0 * sample / 1000.0)
            for sample in range(index * 20, (index + 1) * 20)
        )
        for index in range(10)
    )
    visual_config = VisualGridConfig(
        source_width=12,
        source_height=8,
        grid_columns=2,
        grid_rows=2,
        frames_per_second=10.0,
    )
    visual_frames = (
        np.full((8, 12, 3), 32, dtype=np.uint8),
        np.full((8, 12, 3), 224, dtype=np.uint8),
    )
    return (
        DelayedAudioSource(
            SyntheticAudioFrameSource(audio_frames),
            delay_seconds=0.006,
        ),
        DelayedVideoSource(
            SyntheticVideoFrameSource(visual_frames),
            delay_seconds=0.025,
        ),
        BroadbandHearingPath(LogSpectralReceptor(audio_config)),
        LocalChannelGridReceptor(visual_config),
    )


class FiniteAudioVideoFieldRunTests(unittest.TestCase):
    def test_concurrent_receptors_advance_one_shared_field(self) -> None:
        audio, video, auditory_path, visual_receptor = fixture()
        result = capture_finite_audio_video_field(
            audio,
            video,
            auditory_path,
            visual_receptor,
            duration_seconds=0.2,
            video_frame_count=2,
        )

        self.assertEqual(
            ("auditory", "visual"),
            tuple(
                item.frame.modality_id
                for item in result.timed_receptor_frames
            ),
        )
        self.assertLess(
            max(
                item.capture_start_tick
                for item in result.timed_receptor_frames
            ),
            min(
                item.capture_end_tick
                for item in result.timed_receptor_frames
            ),
        )
        field = result.shared_field_result
        self.assertEqual(1, field.field_state.tick)
        self.assertEqual(
            result.timed_receptor_frames[0].frame.values
            + result.timed_receptor_frames[1].frame.values,
            field.field_state.activation,
        )
        self.assertEqual(
            {"organism.mcm_field"},
            {neuron.field_id for neuron in field.shared_field.layer.neurons},
        )

    def test_dock_boundary_is_a_local_cross_receptor_neighborhood(self) -> None:
        audio, video, auditory_path, visual_receptor = fixture()
        result = capture_finite_audio_video_field(
            audio,
            video,
            auditory_path,
            visual_receptor,
            duration_seconds=0.2,
            video_frame_count=2,
        )
        layer = result.shared_field_result.shared_field.layer
        visual_first = layer.neuron("organism.mcm_field.visual.n0")
        sample_ids = {
            sample.sample_id
            for sample in visual_first.perception.local_samples
        }
        self.assertIn(
            "sample.organism.mcm_field.auditory.n0",
            sample_ids,
        )

    def test_nominal_duration_mismatch_is_rejected_before_capture(self) -> None:
        audio, video, auditory_path, visual_receptor = fixture()
        with self.assertRaisesRegex(
            FiniteAudioVideoFieldError,
            "same nominal duration",
        ):
            capture_finite_audio_video_field(
                audio,
                video,
                auditory_path,
                visual_receptor,
                duration_seconds=0.2,
                video_frame_count=1,
            )
        self.assertEqual(0, audio.source.read_count)
        self.assertEqual(0, video.source.frames_read)

    def test_dock_anatomy_has_no_overlapping_positions(self) -> None:
        anatomies = audio_video_dock_anatomies(
            auditory_carrier_count=4,
            visual_grid_columns=2,
            visual_grid_rows=2,
        )
        auditory = set(anatomies["auditory"].positions)
        visual = set(anatomies["visual"].positions)
        self.assertTrue(auditory.isdisjoint(visual))
        self.assertIn((0, 0), auditory)
        self.assertIn((1, 0), visual)

    def test_public_result_retains_no_raw_sensor_payload(self) -> None:
        roles = {item.name for item in fields(FiniteAudioVideoFieldResult)}
        self.assertTrue(
            {
                "raw_audio",
                "raw_video",
                "samples",
                "images",
                "label",
                "meaning",
                "memory",
            }.isdisjoint(roles)
        )


if __name__ == "__main__":
    unittest.main()
