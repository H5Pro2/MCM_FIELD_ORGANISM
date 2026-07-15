from __future__ import annotations

from dataclasses import fields
import unittest

import numpy as np

from mcm_field_organism import (
    AudioCaptureError,
    AuditoryReceptorContact,
    AuditoryReceptorState,
    BroadbandHearingPath,
    LogSpectralConfig,
    LogSpectralReceptor,
    SyntheticAudioFrameSource,
    broadband_public_roles,
    capture_finite_broadband_hearing,
)


class BroadbandHearingPathTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = LogSpectralConfig()
        self.silence = (0.0,) * self.config.hop_size

    def path(self, band_count: int = 48) -> BroadbandHearingPath:
        return BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig(band_count=band_count)))

    def chunks(
        self,
        frequencies: tuple[tuple[float, float], ...],
        chunk_count: int,
    ) -> list[tuple[float, ...]]:
        index = np.arange(chunk_count * self.config.hop_size)
        samples = sum(
            amplitude * np.sin(2.0 * np.pi * frequency * index / self.config.sample_rate)
            for frequency, amplitude in frequencies
        )
        self.assertLessEqual(float(np.max(np.abs(samples))), 1.0)
        return [
            tuple(float(value) for value in samples[start:start + self.config.hop_size])
            for start in range(0, len(samples), self.config.hop_size)
        ]

    def capture(
        self,
        chunks: list[tuple[float, ...]],
        *,
        path: BroadbandHearingPath | None = None,
        observer=None,
    ):
        selected = path or self.path()
        source = SyntheticAudioFrameSource(chunks)
        summary = capture_finite_broadband_hearing(
            source,
            selected,
            duration_seconds=len(chunks) * self.config.hop_seconds,
            observer=observer,
        )
        return summary, source, selected

    def test_first_state_requires_the_complete_window_and_has_sample_time(self) -> None:
        path = self.path()
        for _ in range(9):
            self.assertIsNone(path.push(self.silence))
        first = path.push(self.silence)
        self.assertIsNotNone(first)
        self.assertEqual(0, first.snapshot_index)
        self.assertEqual(0, first.window_start_sample)
        self.assertEqual(4800, first.window_end_sample)
        second = path.push(self.silence)
        self.assertEqual(1, second.snapshot_index)
        self.assertEqual(480, second.window_start_sample)
        self.assertEqual(5280, second.window_end_sample)

    def test_exact_silence_is_active_zero_without_a_threshold(self) -> None:
        state = None
        path = self.path()
        for _ in range(10):
            state = path.push(self.silence)
        self.assertEqual(AuditoryReceptorContact.ACTIVE_ZERO, state.contact)
        self.assertEqual((0.0,) * 48, state.energy)

    def test_any_nonzero_receptor_energy_is_active_energy(self) -> None:
        state = None
        path = self.path()
        for chunk in self.chunks(((1000.0, 0.5),), 10):
            state = path.push(chunk)
        self.assertEqual(AuditoryReceptorContact.ACTIVE_ENERGY, state.contact)
        self.assertGreater(max(state.energy), 0.0)

    def test_receptor_state_is_immutable_and_has_no_field_roles(self) -> None:
        roles = {item.name for item in fields(AuditoryReceptorState)}
        self.assertTrue({"activation", "afterimage", "local_resources", "samples"}.isdisjoint(roles))
        path = self.path()
        state = None
        for _ in range(10):
            state = path.push(self.silence)
        with self.assertRaises((AttributeError, TypeError)):
            state.energy = ()

    def test_public_roles_exclude_raw_audio_and_semantics(self) -> None:
        forbidden = {
            "samples", "raw_samples", "audio_frame", "file_path", "word",
            "speaker", "meaning", "activation", "afterimage", "local_resources",
        }
        self.assertTrue(forbidden.isdisjoint(broadband_public_roles()))

    def test_finite_capture_reads_exact_chunks_and_counts_completed_states(self) -> None:
        summary, source, path = self.capture([self.silence] * 20)
        self.assertEqual(20, source.read_count)
        self.assertEqual(20, summary.input_chunks)
        self.assertEqual(11, summary.output_snapshots)
        self.assertEqual(11, summary.active_zero_count)
        self.assertEqual(0, summary.active_energy_count)
        self.assertEqual(20, path.input_chunks)
        self.assertEqual(11, path.snapshot_count)

    def test_silence_summary_is_exact_zero(self) -> None:
        summary, _, _ = self.capture([self.silence] * 10)
        self.assertEqual((0.0,) * 48, summary.energy_min)
        self.assertEqual((0.0,) * 48, summary.energy_max)
        self.assertEqual((0.0,) * 48, summary.energy_mean)

    def test_multitone_capture_remains_distributed_across_local_regions(self) -> None:
        seen = []
        summary, _, path = self.capture(
            self.chunks(((250.0, 0.2), (4000.0, 0.2), (12000.0, 0.2)), 10),
            observer=seen.append,
        )
        self.assertEqual(1, summary.output_snapshots)
        centers = np.asarray([band.center_frequency for band in path.receptor.bands])
        for frequency in (250.0, 4000.0, 12000.0):
            nearest = int(np.argmin(np.abs(np.log(centers / frequency))))
            self.assertGreater(seen[0].energy[nearest], 0.1)

    def test_observer_on_and_off_produce_identical_summary(self) -> None:
        chunks = self.chunks(((1000.0, 0.5),), 20)
        without, _, _ = self.capture(chunks)
        seen = []
        with_observer, _, _ = self.capture(chunks, observer=seen.append)
        self.assertEqual(without, with_observer)
        self.assertEqual(11, len(seen))

    def test_explicit_reset_reproduces_the_same_sequence_digest(self) -> None:
        chunks = self.chunks(((440.0, 0.4),), 20)
        path = self.path()
        first, _, _ = self.capture(chunks, path=path)
        path.reset()
        self.assertTrue(path.is_fresh)
        second, _, _ = self.capture(chunks, path=path)
        self.assertEqual(first, second)

    def test_nonfresh_path_is_rejected_before_source_read(self) -> None:
        path = self.path()
        path.push(self.silence)
        source = SyntheticAudioFrameSource([self.silence] * 10)
        with self.assertRaisesRegex(AudioCaptureError, "fresh"):
            capture_finite_broadband_hearing(source, path, duration_seconds=0.1)
        self.assertEqual(0, source.read_count)

    def test_invalid_durations_are_rejected_before_source_read(self) -> None:
        for duration in (0.05, 0.105, 10.01, 0.0):
            source = SyntheticAudioFrameSource([self.silence] * 1001)
            with self.assertRaises(AudioCaptureError):
                capture_finite_broadband_hearing(source, self.path(), duration_seconds=duration)
            self.assertEqual(0, source.read_count)

    def test_short_source_fails_without_returning_a_partial_summary(self) -> None:
        source = SyntheticAudioFrameSource([self.silence] * 10)
        path = self.path()
        with self.assertRaisesRegex(AudioCaptureError, "chunk 10"):
            capture_finite_broadband_hearing(source, path, duration_seconds=0.11)
        self.assertEqual(10, source.read_count)
        self.assertEqual(1, path.snapshot_count)

    def test_invalid_chunk_fails_at_its_exact_position(self) -> None:
        chunks = [self.silence] * 9 + [(2.0,) * self.config.hop_size]
        source = SyntheticAudioFrameSource(chunks)
        path = self.path()
        with self.assertRaisesRegex(AudioCaptureError, "chunk 9"):
            capture_finite_broadband_hearing(source, path, duration_seconds=0.1)
        self.assertEqual(10, source.read_count)
        self.assertEqual(9, path.input_chunks)
        self.assertEqual(0, path.snapshot_count)

    def test_all_candidate_geometries_use_the_same_path_contract(self) -> None:
        for count in (24, 48, 64):
            with self.subTest(count=count):
                path = self.path(count)
                source = SyntheticAudioFrameSource([self.silence] * 10)
                summary = capture_finite_broadband_hearing(source, path, duration_seconds=0.1)
                self.assertEqual(count, len(summary.carrier_ids))
                self.assertEqual(count, len(summary.energy_mean))
                self.assertIn(f"log{count}", summary.geometry_id)


if __name__ == "__main__":
    unittest.main()
