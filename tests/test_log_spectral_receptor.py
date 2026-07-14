from __future__ import annotations

from dataclasses import fields
import math
import unittest

import numpy as np

from mcm_field_organism import (
    BaselineValidationError,
    LogFrequencyBand,
    LogSpectralConfig,
    LogSpectralReceptor,
    RollingLogSpectralReceptor,
    logarithmic_bands,
)


class LogSpectralReceptorTests(unittest.TestCase):
    mandatory_frequencies = (50, 80, 125, 250, 440, 1000, 2000, 4000, 8000, 12000, 16000, 18000)

    def setUp(self) -> None:
        self.config = LogSpectralConfig()
        self.receptor = LogSpectralReceptor(self.config)

    def tone(self, frequency: float, amplitude: float = 0.5, phase: float = 0.0) -> np.ndarray:
        index = np.arange(self.config.window_size)
        return amplitude * np.sin(
            (2.0 * np.pi * frequency * index / self.config.sample_rate) + phase
        )

    def dominant_center(self, energy: tuple[float, ...], receptor: LogSpectralReceptor | None = None) -> float:
        selected = receptor or self.receptor
        index = max(range(len(energy)), key=energy.__getitem__)
        return selected.bands[index].center_frequency

    def test_default_geometry_exposes_the_registered_time_and_frequency_range(self) -> None:
        self.assertEqual(48000, self.config.sample_rate)
        self.assertEqual(0.1, self.config.window_seconds)
        self.assertEqual(0.01, self.config.hop_seconds)
        self.assertEqual(10, self.config.warmup_hops)
        self.assertEqual(48, self.config.band_count)
        self.assertEqual(50.0, self.config.min_frequency)
        self.assertEqual(18000.0, self.config.max_frequency)

    def test_invalid_geometry_is_rejected(self) -> None:
        invalid = (
            lambda: LogSpectralConfig(sample_rate=0),
            lambda: LogSpectralConfig(window_size=2),
            lambda: LogSpectralConfig(hop_size=0),
            lambda: LogSpectralConfig(hop_size=700),
            lambda: LogSpectralConfig(band_count=1),
            lambda: LogSpectralConfig(min_frequency=0.0),
            lambda: LogSpectralConfig(max_frequency=24000.0),
        )
        for call in invalid:
            with self.subTest(call=call), self.assertRaises(BaselineValidationError):
                call()

    def test_centers_are_strictly_logarithmic_and_include_both_edges(self) -> None:
        bands = logarithmic_bands(self.config)
        centers = [band.center_frequency for band in bands]
        ratios = [right / left for left, right in zip(centers[:-1], centers[1:], strict=True)]
        self.assertEqual(50.0, centers[0])
        self.assertEqual(18000.0, centers[-1])
        self.assertTrue(all(left < right for left, right in zip(centers[:-1], centers[1:], strict=True)))
        self.assertLess(max(ratios) - min(ratios), 1e-12)

    def test_channel_roles_are_technical_and_nonsemantic(self) -> None:
        roles = {item.name for item in fields(LogFrequencyBand)}
        self.assertEqual(
            {"channel_id", "lower_frequency", "center_frequency", "upper_frequency"},
            roles,
        )
        forbidden = ("word", "speaker", "music", "meaning", "object")
        self.assertTrue(all(not any(role in channel for role in forbidden) for channel in self.receptor.channel_ids))

    def test_silence_is_exact_zero_for_all_band_counts(self) -> None:
        for count in (24, 48, 64):
            receptor = LogSpectralReceptor(LogSpectralConfig(band_count=count))
            energy = receptor.analyze(np.zeros(receptor.config.window_size))
            self.assertEqual((0.0,) * count, energy)

    def test_all_mandatory_tones_have_a_local_dominant_band(self) -> None:
        center_ratio = self.receptor.bands[1].center_frequency / self.receptor.bands[0].center_frequency
        for frequency in self.mandatory_frequencies:
            with self.subTest(frequency=frequency):
                energy = self.receptor.analyze(self.tone(frequency))
                center = self.dominant_center(energy)
                self.assertLessEqual(abs(math.log(center / frequency)), math.log(center_ratio))
                self.assertGreater(max(energy), 0.25)

    def test_dominant_frequency_region_is_stable_across_band_counts(self) -> None:
        for count in (24, 48, 64):
            config = LogSpectralConfig(band_count=count)
            receptor = LogSpectralReceptor(config)
            center_ratio = receptor.bands[1].center_frequency / receptor.bands[0].center_frequency
            for frequency in self.mandatory_frequencies:
                index = np.arange(config.window_size)
                tone = 0.5 * np.sin(2.0 * np.pi * frequency * index / config.sample_rate)
                center = self.dominant_center(receptor.analyze(tone), receptor)
                self.assertLessEqual(abs(math.log(center / frequency)), math.log(center_ratio))

    def test_amplitude_scaling_is_proportional_without_clipping(self) -> None:
        low = self.receptor.analyze(self.tone(1000, amplitude=0.3))
        high = self.receptor.analyze(self.tone(1000, amplitude=0.6))
        np.testing.assert_allclose(np.asarray(high), 2.0 * np.asarray(low), rtol=1e-12, atol=1e-14)

    def test_phase_does_not_change_the_dominant_frequency_region(self) -> None:
        for frequency in (50, 80, 440, 1000, 18000):
            first = self.receptor.analyze(self.tone(frequency, phase=0.0))
            shifted = self.receptor.analyze(self.tone(frequency, phase=1.234))
            self.assertEqual(self.dominant_center(first), self.dominant_center(shifted))
            relative_error = np.linalg.norm(np.asarray(first) - shifted) / np.linalg.norm(first)
            self.assertLess(relative_error, 1e-4)

    def test_multitone_input_activates_each_local_frequency_region(self) -> None:
        samples = self.tone(250, amplitude=0.2) + self.tone(4000, amplitude=0.2) + self.tone(12000, amplitude=0.2)
        self.assertLessEqual(float(np.max(np.abs(samples))), 1.0)
        energy = self.receptor.analyze(samples)
        centers = np.asarray([band.center_frequency for band in self.receptor.bands])
        for frequency in (250, 4000, 12000):
            nearest = int(np.argmin(np.abs(np.log(centers / frequency))))
            self.assertGreater(energy[nearest], 0.1)

    def test_frequency_limits_are_filter_transitions_not_hard_walls(self) -> None:
        at_lower_edge = max(self.receptor.analyze(self.tone(50)))
        near_below = max(self.receptor.analyze(self.tone(40)))
        far_below = max(self.receptor.analyze(self.tone(20)))
        above = max(self.receptor.analyze(self.tone(19000)))
        self.assertGreater(near_below, 0.1)
        self.assertLess(near_below, at_lower_edge)
        self.assertLess(far_below, 1e-3)
        self.assertLess(above, 1e-3)

    def test_sample_domain_and_window_size_are_enforced(self) -> None:
        invalid = (
            np.zeros(self.config.window_size - 1),
            np.full(self.config.window_size, 2.0),
            np.full(self.config.window_size, np.nan),
        )
        for samples in invalid:
            with self.assertRaises(BaselineValidationError):
                self.receptor.analyze(samples)


class RollingLogSpectralReceptorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = LogSpectralConfig()
        self.receptor = LogSpectralReceptor(self.config)
        index = np.arange(self.config.window_size)
        self.window = 0.5 * np.sin(2.0 * np.pi * 1000 * index / self.config.sample_rate)
        self.chunks = np.split(self.window, self.config.warmup_hops)

    def test_output_starts_only_after_the_complete_technical_window(self) -> None:
        rolling = RollingLogSpectralReceptor(self.receptor)
        for chunk in self.chunks[:-1]:
            self.assertIsNone(rolling.push(chunk))
        self.assertEqual(self.config.window_size - self.config.hop_size, rolling.filled_samples)
        self.assertIsNotNone(rolling.push(self.chunks[-1]))
        self.assertEqual(1, rolling.output_count)

    def test_chunked_window_matches_direct_analysis(self) -> None:
        rolling = RollingLogSpectralReceptor(self.receptor)
        output = None
        for chunk in self.chunks:
            output = rolling.push(chunk)
        self.assertIsNotNone(output)
        np.testing.assert_allclose(output, self.receptor.analyze(self.window), rtol=0.0, atol=0.0)

    def test_reset_repeats_the_same_output_exactly(self) -> None:
        rolling = RollingLogSpectralReceptor(self.receptor)

        def run() -> tuple[float, ...]:
            output = None
            for chunk in self.chunks:
                output = rolling.push(chunk)
            self.assertIsNotNone(output)
            return output

        first = run()
        rolling.reset()
        self.assertEqual(0, rolling.filled_samples)
        self.assertEqual(0, rolling.output_count)
        self.assertEqual(first, run())

    def test_contact_is_exactly_gone_after_one_window_of_silence(self) -> None:
        rolling = RollingLogSpectralReceptor(self.receptor)
        for chunk in self.chunks:
            output = rolling.push(chunk)
        self.assertGreater(max(output or ()), 0.0)
        silence = np.zeros(self.config.hop_size)
        for _ in range(self.config.warmup_hops):
            output = rolling.push(silence)
        self.assertEqual((0.0,) * self.config.band_count, output)

    def test_invalid_chunk_does_not_advance_the_window(self) -> None:
        rolling = RollingLogSpectralReceptor(self.receptor)
        with self.assertRaises(BaselineValidationError):
            rolling.push(np.zeros(self.config.hop_size - 1))
        self.assertEqual(0, rolling.filled_samples)
        self.assertEqual(0, rolling.output_count)


if __name__ == "__main__":
    unittest.main()
