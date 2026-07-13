from __future__ import annotations

from itertools import permutations
import math
import unittest

from mcm_field_organism import (
    AuditoryProbeConfig,
    BaselineValidationError,
    auditory_receptor_frame,
    integrate_and_fire_step,
    project_frequency_amplitude,
    run_independent_history,
    run_integrate_and_fire,
    synthesize_tone_frame,
    threshold_events,
)


class AuditoryReceptorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = AuditoryProbeConfig()
        self.silence = (0.0,) * self.config.frame_size

    def tone(self, frequency: float, amplitude: float = 0.6, phase: float = 0.0) -> tuple[float, ...]:
        return synthesize_tone_frame(self.config, [(frequency, amplitude, phase)])

    def test_probe_configuration_is_explicit(self) -> None:
        self.assertEqual(0.01, self.config.dt)
        self.assertEqual(
            ("frequency.200hz", "frequency.400hz", "frequency.800hz"),
            self.config.channel_ids,
        )

    def test_silence_is_exact_zero(self) -> None:
        self.assertEqual((0.0, 0.0, 0.0), auditory_receptor_frame(self.silence, self.config))

    def test_each_probe_tone_is_local_to_its_frequency_channel(self) -> None:
        for target_index, frequency in enumerate(self.config.frequencies):
            energies = auditory_receptor_frame(self.tone(frequency), self.config)
            self.assertAlmostEqual(0.6, energies[target_index], places=14)
            for index, value in enumerate(energies):
                if index != target_index:
                    self.assertAlmostEqual(0.0, value, places=14)

    def test_phase_shift_preserves_frequency_amplitude(self) -> None:
        baseline = auditory_receptor_frame(self.tone(400.0, phase=0.0), self.config)
        shifted = auditory_receptor_frame(self.tone(400.0, phase=1.234), self.config)
        for left, right in zip(baseline, shifted, strict=True):
            self.assertAlmostEqual(left, right, places=14)

    def test_two_tones_remain_two_local_energy_components(self) -> None:
        samples = synthesize_tone_frame(
            self.config,
            [(200.0, 0.35, 0.0), (800.0, 0.25, 0.4)],
        )
        energies = auditory_receptor_frame(samples, self.config)
        self.assertAlmostEqual(0.35, energies[0], places=14)
        self.assertAlmostEqual(0.0, energies[1], places=14)
        self.assertAlmostEqual(0.25, energies[2], places=14)

    def test_receptor_amplitude_scales_linearly(self) -> None:
        full = auditory_receptor_frame(self.tone(200.0, amplitude=0.8), self.config)
        half = auditory_receptor_frame(self.tone(200.0, amplitude=0.4), self.config)
        for full_value, half_value in zip(full, half, strict=True):
            self.assertAlmostEqual(full_value * 0.5, half_value, places=14)

    def test_channel_calculation_order_does_not_change_values(self) -> None:
        samples = synthesize_tone_frame(
            self.config,
            [(200.0, 0.3, 0.1), (400.0, 0.2, 0.2), (800.0, 0.1, 0.3)],
        )
        expected = dict(zip(self.config.frequencies, auditory_receptor_frame(samples, self.config), strict=True))
        for order in permutations(self.config.frequencies):
            measured = {
                frequency: project_frequency_amplitude(
                    samples,
                    sample_rate=self.config.sample_rate,
                    frequency=frequency,
                )
                for frequency in order
            }
            for frequency in self.config.frequencies:
                self.assertAlmostEqual(expected[frequency], measured[frequency], places=15)

    def test_invalid_audio_domains_are_rejected(self) -> None:
        invalid_calls = (
            lambda: auditory_receptor_frame((0.0,) * 79, self.config),
            lambda: auditory_receptor_frame((2.0,) * 80, self.config),
            lambda: synthesize_tone_frame(self.config, [(200.0, 1.0, 0.0), (400.0, 1.0, 0.0)]),
            lambda: AuditoryProbeConfig(frequencies=(0.0,)),
        )
        for call in invalid_calls:
            with self.assertRaises(BaselineValidationError):
                call()


class ThresholdEventTests(unittest.TestCase):
    def test_onset_hold_and_offset_are_local_signed_events(self) -> None:
        zero = (0.0, 0.0, 0.0)
        tone = (0.0, 0.7, 0.0)
        self.assertEqual((0, 1, 0), threshold_events(zero, tone, threshold=0.5))
        self.assertEqual((0, 0, 0), threshold_events(tone, tone, threshold=0.5))
        self.assertEqual((0, -1, 0), threshold_events(tone, zero, threshold=0.5))

    def test_subthreshold_energy_is_not_represented(self) -> None:
        self.assertEqual(
            (0, 0, 0),
            threshold_events((0.0, 0.0, 0.0), (0.19, 0.0, 0.0), threshold=0.2),
        )

    def test_different_amplitudes_collide_in_the_same_event(self) -> None:
        previous = (0.0,)
        self.assertEqual(
            threshold_events(previous, (0.6,), threshold=0.5),
            threshold_events(previous, (0.9,), threshold=0.5),
        )

    def test_threshold_choice_changes_event_output(self) -> None:
        previous = (0.0,)
        current = (0.4,)
        self.assertEqual((1,), threshold_events(previous, current, threshold=0.2))
        self.assertEqual((0,), threshold_events(previous, current, threshold=0.5))

    def test_pulse_spacing_is_present_only_as_event_timing(self) -> None:
        energy_history = [(0.0,), (0.8,), (0.0,), (0.0,), (0.8,), (0.0,)]
        events = [
            threshold_events(previous, current, threshold=0.5)[0]
            for previous, current in zip(energy_history, energy_history[1:])
        ]
        self.assertEqual([1, -1, 0, 1, -1], events)

    def test_regular_and_irregular_pulses_have_different_event_timing(self) -> None:
        regular = [(0.0,), (0.8,), (0.0,), (0.8,), (0.0,), (0.8,), (0.0,)]
        irregular = [(0.0,), (0.8,), (0.0,), (0.0,), (0.8,), (0.0,), (0.8,)]

        def event_trace(history: list[tuple[float, ...]]) -> tuple[int, ...]:
            return tuple(
                threshold_events(previous, current, threshold=0.5)[0]
                for previous, current in zip(history, history[1:])
            )

        self.assertNotEqual(event_trace(regular), event_trace(irregular))

    def test_ascending_and_descending_frequency_sequences_remain_distinct(self) -> None:
        zero = (0.0, 0.0, 0.0)
        ascending = ((0.8, 0.0, 0.0), (0.0, 0.8, 0.0), (0.0, 0.0, 0.8))
        descending = tuple(reversed(ascending))

        def events(sequence: tuple[tuple[float, ...], ...]) -> tuple[tuple[int, ...], ...]:
            previous = zero
            trace = []
            for current in sequence:
                trace.append(threshold_events(previous, current, threshold=0.5))
                previous = current
            return tuple(trace)

        self.assertNotEqual(events(ascending), events(descending))


class AuditoryLeakyReferenceTests(unittest.TestCase):
    def test_same_current_frequency_lage_retains_different_immediate_history(self) -> None:
        first = run_independent_history(
            [(0.8, 0.0, 0.0), (0.0, 0.5, 0.0)],
            dt=0.01,
            tau=0.05,
        )
        second = run_independent_history(
            [(0.0, 0.0, 0.8), (0.0, 0.5, 0.0)],
            dt=0.01,
            tau=0.05,
        )
        self.assertEqual(first[-1].activation, second[-1].activation)
        self.assertNotEqual(first[-1].afterimage, second[-1].afterimage)


class IntegrateAndFireTests(unittest.TestCase):
    def test_silence_from_reset_produces_no_spikes(self) -> None:
        frames = run_integrate_and_fire([(0.0, 0.0, 0.0)] * 20, dt=0.01, tau=0.05, threshold=0.5)
        self.assertTrue(all(frame.spikes == (0, 0, 0) for frame in frames))
        self.assertTrue(all(frame.membrane == (0.0, 0.0, 0.0) for frame in frames))

    def test_sustained_energy_can_produce_repeated_local_spikes(self) -> None:
        frames = run_integrate_and_fire([(0.8,)] * 40, dt=0.01, tau=0.05, threshold=0.2)
        spike_count = sum(frame.spikes[0] for frame in frames)
        self.assertGreater(spike_count, 1)

    def test_energy_in_one_channel_never_charges_another(self) -> None:
        frames = run_integrate_and_fire([(0.8, 0.0, 0.0)] * 20, dt=0.01, tau=0.05, threshold=0.2)
        self.assertTrue(all(frame.spikes[1:] == (0, 0) for frame in frames))
        self.assertTrue(all(frame.membrane[1:] == (0.0, 0.0) for frame in frames))

    def test_silence_relaxes_subthreshold_membrane_without_spike(self) -> None:
        frame = integrate_and_fire_step((0.4,), (0.0,), dt=0.01, tau=0.05, threshold=0.5)
        self.assertEqual((0,), frame.spikes)
        self.assertGreater(frame.membrane[0], 0.0)
        self.assertLess(frame.membrane[0], 0.4)

    def test_threshold_and_tau_control_spike_sequence(self) -> None:
        history = [(0.6,)] * 30
        outputs = {
            (tau, threshold): tuple(frame.spikes[0] for frame in run_integrate_and_fire(
                history,
                dt=0.01,
                tau=tau,
                threshold=threshold,
            ))
            for tau in (0.01, 0.05, 0.2)
            for threshold in (0.2, 0.5, 0.8)
        }
        self.assertGreater(len(set(outputs.values())), 1)

    def test_different_energy_histories_can_have_identical_spike_output(self) -> None:
        first = run_integrate_and_fire([(0.10,)] * 5, dt=0.01, tau=0.05, threshold=0.8)
        second = run_integrate_and_fire([(0.15,)] * 5, dt=0.01, tau=0.05, threshold=0.8)
        self.assertNotEqual(tuple(frame.energy for frame in first), tuple(frame.energy for frame in second))
        self.assertEqual(tuple(frame.spikes for frame in first), tuple(frame.spikes for frame in second))

    def test_reset_repeats_exact_spike_and_membrane_history(self) -> None:
        history = [(0.0,), (0.8,), (0.8,), (0.0,), (0.8,)]
        first = run_integrate_and_fire(history, dt=0.01, tau=0.05, threshold=0.2)
        contrasting = run_integrate_and_fire([(1.0,)] * 12, dt=0.01, tau=0.05, threshold=0.2)
        self.assertNotEqual(first, contrasting)
        repeated = run_integrate_and_fire(history, dt=0.01, tau=0.05, threshold=0.2)
        self.assertEqual(first, repeated)

    def test_channel_permutation_restores_same_independent_result(self) -> None:
        previous = (0.1, 0.05, 0.0)
        energy = (0.7, 0.3, 0.0)
        expected = integrate_and_fire_step(previous, energy, dt=0.01, tau=0.05, threshold=0.5)
        for order in permutations(range(3)):
            permuted = integrate_and_fire_step(
                tuple(previous[index] for index in order),
                tuple(energy[index] for index in order),
                dt=0.01,
                tau=0.05,
                threshold=0.5,
            )
            restored_membrane = tuple(permuted.membrane[order.index(index)] for index in range(3))
            restored_spikes = tuple(permuted.spikes[order.index(index)] for index in range(3))
            self.assertEqual(expected.membrane, restored_membrane)
            self.assertEqual(expected.spikes, restored_spikes)

    def test_invalid_spike_domains_are_rejected(self) -> None:
        invalid_calls = (
            lambda: threshold_events((0.0,), (0.5,), threshold=0.0),
            lambda: integrate_and_fire_step((0.5,), (0.5,), dt=0.01, tau=0.05, threshold=0.5),
            lambda: integrate_and_fire_step((0.0,), (-0.1,), dt=0.01, tau=0.05, threshold=0.5),
            lambda: run_integrate_and_fire([], dt=0.01, tau=0.05, threshold=0.5),
            lambda: integrate_and_fire_step((0.0, 0.0), (0.1,), dt=0.01, tau=0.05, threshold=0.5),
        )
        for call in invalid_calls:
            with self.assertRaises(BaselineValidationError):
                call()


if __name__ == "__main__":
    unittest.main()
