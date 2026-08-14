from __future__ import annotations

import unittest

import mcm_field_organism as package_api
from mcm_field_organism import audio_video_neutral_field_runtime
from mcm_field_organism import broadband_hearing_path
from mcm_field_organism import common_receptor_window
from mcm_field_organism import controlled_audio_phase_source
from mcm_field_organism import controlled_audio_video_test_world
from mcm_field_organism import finite_audio_video_field_run
from mcm_field_organism import live_audio_adapter
from mcm_field_organism import public_av_container_source
from mcm_field_organism import receptor_time_alignment
from mcm_field_organism.controlled_audio_source import (
    AudioCaptureError,
    AudioFrameSource,
    SyntheticAudioFrameSource,
)


class ControlledAudioSourceBoundaryTests(unittest.TestCase):
    def test_legacy_and_root_exports_keep_exact_identity(self) -> None:
        self.assertIs(AudioCaptureError, live_audio_adapter.AudioCaptureError)
        self.assertIs(AudioCaptureError, package_api.AudioCaptureError)
        self.assertIs(AudioFrameSource, live_audio_adapter.AudioFrameSource)
        self.assertIs(AudioCaptureError, public_av_container_source.AudioCaptureError)
        self.assertIs(
            SyntheticAudioFrameSource,
            live_audio_adapter.SyntheticAudioFrameSource,
        )
        self.assertIs(SyntheticAudioFrameSource, package_api.SyntheticAudioFrameSource)

    def test_controlled_modules_share_the_device_neutral_protocol(self) -> None:
        modules = (
            audio_video_neutral_field_runtime,
            broadband_hearing_path,
            common_receptor_window,
            controlled_audio_phase_source,
            finite_audio_video_field_run,
            receptor_time_alignment,
        )
        for module in modules:
            with self.subTest(module=module.__name__):
                self.assertIs(AudioFrameSource, module.AudioFrameSource)
        self.assertIs(
            SyntheticAudioFrameSource,
            controlled_audio_video_test_world.SyntheticAudioFrameSource,
        )

    def test_synthetic_source_behavior_and_error_contract_are_unchanged(self) -> None:
        source = SyntheticAudioFrameSource(((0, 0.5), (1, -0.5)))
        self.assertEqual((0.0, 0.5), source.read_frame())
        self.assertEqual((1.0, -0.5), source.read_frame())
        self.assertEqual(2, source.read_count)
        self.assertEqual(0, source.overflow_count)
        with self.assertRaisesRegex(AudioCaptureError, "ended before"):
            source.read_frame()


if __name__ == "__main__":
    unittest.main()
