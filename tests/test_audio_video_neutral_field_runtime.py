from __future__ import annotations

import threading
import unittest
from unittest.mock import MagicMock, patch

import numpy as np

from mcm_field_organism import (
    AudioVideoNeutralFieldRuntimeError,
    CameraStartupSummary,
    NeutralLocalFieldSubstrateConfig,
    audio_video_neutral_field_runtime_public_roles,
    capture_audio_video_into_neutral_field,
    capture_live_audio_video_into_neutral_field,
)
from mcm_field_organism.broadband_hearing_path import BroadbandHearingPath
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


class IncrementingClock:
    def __init__(self) -> None:
        self._value = 0
        self._lock = threading.Lock()

    def __call__(self) -> int:
        with self._lock:
            value = self._value
            self._value += 1
            return value


def capture_components():
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
            * np.sin(
                2.0
                * np.pi
                * 100.0
                * sample
                / audio_config.sample_rate
            )
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
        SyntheticAudioFrameSource(audio_frames),
        SyntheticVideoFrameSource(visual_frames),
        BroadbandHearingPath(LogSpectralReceptor(audio_config)),
        LocalChannelGridReceptor(visual_config),
    )


class AudioVideoNeutralFieldRuntimeTests(unittest.TestCase):
    def test_native_audio_video_capture_reaches_one_shared_field(self) -> None:
        with patch(
            "mcm_field_organism.neutral_local_field_substrate.np.linalg.eigh",
            wraps=np.linalg.eigh,
        ) as decompose:
            result = capture_audio_video_into_neutral_field(
                *capture_components(),
                NeutralLocalFieldSubstrateConfig(1.0),
                nominal_duration_seconds=0.2,
                clock=IncrementingClock(),
                clock_id="organism.test",
                ticks_per_second=1000.0,
            )

        self.assertEqual(
            (6, 2),
            tuple(len(sequence.frames) for sequence in result.receptor_sequences),
        )
        self.assertEqual(8, result.field_run.source_support_count)
        self.assertEqual(8, result.field_run.handoff.assigned_event_count)
        self.assertEqual(
            {"auditory", "visual"},
            {
                dock.dock_map.modality_id
                for dock in result.field_run.field.docks
            },
        )
        self.assertEqual(16, len(result.field_run.field.layer.neurons))
        self.assertEqual((), result.field_run.field.last_distribution.contacts)
        self.assertEqual(1, decompose.call_count)

    def test_clock_rate_must_be_explicitly_physical(self) -> None:
        with self.assertRaisesRegex(
            AudioVideoNeutralFieldRuntimeError,
            "ticks_per_second",
        ):
            capture_audio_video_into_neutral_field(
                *capture_components(),
                NeutralLocalFieldSubstrateConfig(1.0),
                nominal_duration_seconds=0.2,
                clock=IncrementingClock(),
                clock_id="organism.test",
                ticks_per_second=0.0,
            )

    def test_public_result_contains_no_raw_payload_or_semantic_role(self) -> None:
        roles = set(audio_video_neutral_field_runtime_public_roles())
        self.assertTrue(
            {
                "raw_audio",
                "raw_video",
                "samples",
                "image",
                "semantic_label",
                "meaning",
                "object_id",
            }.isdisjoint(roles)
        )

    def test_live_bridge_uses_explicit_devices_and_the_same_field_path(self) -> None:
        field_config = NeutralLocalFieldSubstrateConfig(1.0)
        captured = capture_audio_video_into_neutral_field(
            *capture_components(),
            field_config,
            nominal_duration_seconds=0.2,
            clock=IncrementingClock(),
            clock_id="organism.test",
            ticks_per_second=1000.0,
        )
        startup = CameraStartupSummary(
            device_index=2,
            requested_frames=0,
            consumed_frames=0,
            exact_zero_frames=0,
            active_frames=0,
            reported_width=1920.0,
            reported_height=1080.0,
            reported_frames_per_second=30.0,
        )
        video_source = MagicMock()
        video_source.prepare.return_value = startup
        video_source.capture_frames_read = 2
        video_context = MagicMock()
        video_context.__enter__.return_value = video_source
        audio_source = MagicMock()
        audio_source.overflow_count = 0
        audio_context = MagicMock()
        audio_context.__enter__.return_value = audio_source

        with (
            patch(
                "mcm_field_organism.live_audio_video_field.OpenCVVideoFrameSource",
                return_value=video_context,
            ) as video_adapter,
            patch(
                "mcm_field_organism.live_audio_video_field.SoundDeviceInputSource",
                return_value=audio_context,
            ) as audio_adapter,
            patch(
                "mcm_field_organism.live_audio_video_field."
                "capture_audio_video_into_neutral_field",
                return_value=captured,
            ) as field_capture,
        ):
            result = capture_live_audio_video_into_neutral_field(
                camera_device=2,
                audio_device="microphone.test",
                field_config=field_config,
                nominal_duration_seconds=0.2,
                camera_startup_frames=0,
            )

        self.assertIs(startup, result.camera_startup)
        self.assertIs(captured, result.field_run)
        self.assertEqual(2, result.camera_capture_frame_count)
        self.assertEqual(0, result.audio_overflow_count)
        self.assertEqual(2, video_adapter.call_args.kwargs["device_index"])
        self.assertEqual(
            "microphone.test",
            audio_adapter.call_args.kwargs["device"],
        )
        field_capture.assert_called_once()
        self.assertIs(
            field_config,
            field_capture.call_args.args[4],
        )


if __name__ == "__main__":
    unittest.main()
