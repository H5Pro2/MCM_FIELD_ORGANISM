from __future__ import annotations

from dataclasses import fields
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from mcm_field_organism import (
    AudioCaptureError,
    AuditoryCaptureSummary,
    AuditoryObservation,
    AuditoryProbeConfig,
    SoundDeviceInputSource,
    SyntheticAudioFrameSource,
    auditory_receptor_frame,
    capture_finite_audio,
    public_result_roles,
    synthesize_tone_frame,
)


class FiniteAudioAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = AuditoryProbeConfig()
        self.silence = (0.0,) * self.config.frame_size
        self.tone = synthesize_tone_frame(self.config, [(400.0, 0.7, 0.0)])

    def capture(self, frames: list[tuple[float, ...]], **kwargs: object) -> AuditoryCaptureSummary:
        source = SyntheticAudioFrameSource(frames)
        return capture_finite_audio(
            source,
            self.config,
            duration_seconds=len(frames) * self.config.dt,
            **kwargs,
        )

    def test_finite_duration_reads_exactly_the_requested_frame_count(self) -> None:
        source = SyntheticAudioFrameSource([self.silence] * 4 + [self.tone])
        summary = capture_finite_audio(source, self.config, duration_seconds=0.03)
        self.assertEqual(3, summary.frame_count)
        self.assertEqual(3, source.read_count)

    def test_silence_summary_is_zero_and_contains_no_events(self) -> None:
        summary = self.capture([self.silence] * 5)
        self.assertEqual((0.0, 0.0, 0.0), summary.energy_min)
        self.assertEqual((0.0, 0.0, 0.0), summary.energy_max)
        self.assertEqual((0, 0, 0), summary.onset_counts)
        self.assertEqual((0, 0, 0), summary.offset_counts)
        self.assertEqual((0, 0, 0), summary.spike_counts)

    def test_tone_begin_and_end_are_aggregated_without_raw_audio(self) -> None:
        summary = self.capture([self.silence, self.tone, self.tone, self.silence])
        self.assertEqual((0, 1, 0), summary.onset_counts)
        self.assertEqual((0, 1, 0), summary.offset_counts)
        self.assertAlmostEqual(0.7, summary.energy_max[1], places=14)

    def test_summary_and_observation_roles_exclude_raw_samples(self) -> None:
        forbidden = {"samples", "raw_samples", "audio", "audio_frame", "file_path"}
        self.assertTrue(forbidden.isdisjoint(public_result_roles()))
        self.assertTrue(forbidden.isdisjoint(item.name for item in fields(AuditoryObservation)))

    def test_observer_receives_only_immutable_technical_observations(self) -> None:
        observations: list[AuditoryObservation] = []
        summary = self.capture([self.silence, self.tone], observer=observations.append)
        self.assertEqual(2, len(observations))
        self.assertEqual(summary.energy_max, tuple(max(item.energy[i] for item in observations) for i in range(3)))
        with self.assertRaises((AttributeError, TypeError)):
            observations[0].energy = ()

    def test_observer_on_and_off_produce_identical_summary(self) -> None:
        frames = [self.silence, self.tone, self.silence]
        without = self.capture(frames)
        seen: list[AuditoryObservation] = []
        with_observer = self.capture(frames, observer=seen.append)
        self.assertEqual(without, with_observer)

    def test_identical_reset_sources_produce_identical_digest(self) -> None:
        frames = [self.silence, self.tone, self.tone, self.silence]
        first = self.capture(frames)
        contrasting = self.capture([self.tone] * 4)
        repeated = self.capture(frames)
        self.assertNotEqual(first.observation_digest, contrasting.observation_digest)
        self.assertEqual(first, repeated)

    def test_continuous_energy_reference_is_not_changed_by_spike_parameters(self) -> None:
        frames = [self.silence, self.tone, self.tone, self.silence]
        low = self.capture(frames, event_threshold=0.2, spike_threshold=0.2, spike_tau=0.01)
        high = self.capture(frames, event_threshold=0.8, spike_threshold=0.8, spike_tau=0.2)
        self.assertEqual(low.energy_min, high.energy_min)
        self.assertEqual(low.energy_max, high.energy_max)
        self.assertEqual(low.energy_mean, high.energy_mean)
        self.assertNotEqual((low.onset_counts, low.spike_counts), (high.onset_counts, high.spike_counts))

    def test_energy_aggregate_matches_direct_receptor_output(self) -> None:
        frames = [self.silence, self.tone]
        summary = self.capture(frames)
        direct = auditory_receptor_frame(self.tone, self.config)
        self.assertEqual(direct, summary.energy_max)
        self.assertEqual(tuple(value / 2.0 for value in direct), summary.energy_mean)

    def test_duration_limit_and_frame_alignment_reject_without_reading(self) -> None:
        for duration in (10.01, 0.015, 0.0):
            source = SyntheticAudioFrameSource([self.silence] * 1001)
            with self.assertRaises(AudioCaptureError):
                capture_finite_audio(source, self.config, duration_seconds=duration)
            self.assertEqual(0, source.read_count)

    def test_short_source_fails_without_returning_partial_summary(self) -> None:
        source = SyntheticAudioFrameSource([self.silence])
        with self.assertRaisesRegex(AudioCaptureError, "frame 1"):
            capture_finite_audio(source, self.config, duration_seconds=0.02)
        self.assertEqual(1, source.read_count)

    def test_invalid_frame_fails_at_its_exact_position(self) -> None:
        source = SyntheticAudioFrameSource([self.silence, (2.0,) * 80])
        with self.assertRaisesRegex(AudioCaptureError, "frame 1"):
            capture_finite_audio(source, self.config, duration_seconds=0.02)

    def test_overflow_count_is_technical_summary_only(self) -> None:
        source = SyntheticAudioFrameSource([self.silence])
        source.overflow_count = 2
        summary = capture_finite_audio(source, self.config, duration_seconds=0.01)
        self.assertEqual(2, summary.overflow_count)

    def test_optional_hardware_source_requires_explicit_device(self) -> None:
        with self.assertRaises(AudioCaptureError):
            SoundDeviceInputSource(device="", config=self.config)

    def test_missing_optional_dependency_blocks_before_stream_creation(self) -> None:
        source = SoundDeviceInputSource(device=1, config=self.config)
        with patch.dict(sys.modules, {"sounddevice": None}):
            with self.assertRaisesRegex(AudioCaptureError, "not installed"):
                source.__enter__()

    def test_hardware_source_closes_stream_after_finite_context(self) -> None:
        class FakeStream:
            def __init__(self) -> None:
                self.started = False
                self.stopped = False
                self.closed = False

            def start(self) -> None:
                self.started = True

            def stop(self) -> None:
                self.stopped = True

            def close(self) -> None:
                self.closed = True

        stream = FakeStream()
        module = SimpleNamespace(
            check_input_settings=lambda **kwargs: None,
            InputStream=lambda **kwargs: stream,
        )
        source = SoundDeviceInputSource(device=9, config=self.config)
        with patch.dict(sys.modules, {"sounddevice": module}):
            with source:
                self.assertTrue(stream.started)
                self.assertFalse(stream.closed)
        self.assertTrue(stream.stopped)
        self.assertTrue(stream.closed)

    def test_hardware_callback_buffers_ordered_frames_between_reads(self) -> None:
        class Status:
            input_overflow = False

            def __bool__(self) -> bool:
                return False

        class CallbackStream:
            def __init__(self, callback) -> None:
                self.callback = callback

            def start(self) -> None:
                for value in (0.1, 0.2, 0.3):
                    self.callback(
                        [[value]] * self_config.frame_size,
                        self_config.frame_size,
                        None,
                        Status(),
                    )

            def stop(self) -> None:
                pass

            def close(self) -> None:
                pass

        self_config = self.config
        module = SimpleNamespace(
            check_input_settings=lambda **kwargs: None,
            InputStream=lambda **kwargs: CallbackStream(kwargs["callback"]),
        )
        ticks = iter((1_000_000_000, 1_010_000_000, 1_020_000_000))
        source = SoundDeviceInputSource(
            device=9,
            config=self.config,
            clock=lambda: next(ticks),
        )
        with patch.dict(sys.modules, {"sounddevice": module}):
            with source:
                frames = (
                    source.read_timed_frame(),
                    source.read_timed_frame(),
                    source.read_timed_frame(),
                )
        self.assertEqual(
            (0.1, 0.2, 0.3),
            tuple(frame[0][0] for frame in frames),
        )
        self.assertEqual(
            (
                (990_000_000, 1_000_000_000),
                (1_000_000_000, 1_010_000_000),
                (1_010_000_000, 1_020_000_000),
            ),
            tuple((frame[1], frame[2]) for frame in frames),
        )
        self.assertEqual(0, source.overflow_count)

    def test_hardware_source_closes_stream_when_start_fails(self) -> None:
        class FailingStream:
            def __init__(self) -> None:
                self.stopped = False
                self.closed = False

            def start(self) -> None:
                raise RuntimeError("start failed")

            def stop(self) -> None:
                self.stopped = True

            def close(self) -> None:
                self.closed = True

        stream = FailingStream()
        module = SimpleNamespace(
            check_input_settings=lambda **kwargs: None,
            InputStream=lambda **kwargs: stream,
        )
        source = SoundDeviceInputSource(device=9, config=self.config)
        with patch.dict(sys.modules, {"sounddevice": module}):
            with self.assertRaisesRegex(AudioCaptureError, "cannot open"):
                source.__enter__()
        self.assertTrue(stream.stopped)
        self.assertTrue(stream.closed)


if __name__ == "__main__":
    unittest.main()
