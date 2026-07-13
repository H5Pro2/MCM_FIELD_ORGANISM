from __future__ import annotations

import math
import unittest

from mcm_field_organism import (
    BaselineValidationError,
    decay_factor,
    independent_leaky_step,
    run_independent_history,
    stateless_baseline,
)


TAUS = (0.25, 1.0, 4.0)
DTS = (1.0, 0.5, 0.25)


class StatelessBaselineTests(unittest.TestCase):
    def test_b0_carries_current_contact_but_no_afterimage(self) -> None:
        contact = (0.7, 0.0, -0.4)
        frame = stateless_baseline(contact)
        self.assertEqual(contact, frame.activation)
        self.assertEqual((0.0, 0.0, 0.0), frame.afterimage)

        removed = stateless_baseline((0.0, 0.0, 0.0))
        self.assertEqual((0.0, 0.0, 0.0), removed.afterimage)


class IndependentLeakyBaselineTests(unittest.TestCase):
    def test_zero_history_stays_exactly_neutral_across_parameter_family(self) -> None:
        for tau in TAUS:
            for dt in DTS:
                frames = run_independent_history([(0.0, 0.0)] * 12, dt=dt, tau=tau)
                self.assertTrue(all(frame.afterimage == (0.0, 0.0) for frame in frames))

    def test_positive_and_negative_impulses_retain_polarity(self) -> None:
        for sign in (-1.0, 1.0):
            frames = run_independent_history(
                [(sign,), (0.0,), (0.0,)],
                dt=0.5,
                tau=1.0,
            )
            self.assertGreater(sign * frames[0].afterimage[0], 0.0)
            self.assertGreater(sign * frames[-1].afterimage[0], 0.0)

    def test_unforced_afterimage_relaxes_monotonically_for_all_parameters(self) -> None:
        for tau in TAUS:
            for dt in DTS:
                frames = run_independent_history(
                    [(1.0,)] + [(0.0,)] * 16,
                    dt=dt,
                    tau=tau,
                )
                magnitudes = [abs(frame.afterimage[0]) for frame in frames]
                self.assertTrue(all(later < earlier for earlier, later in zip(magnitudes, magnitudes[1:])))

    def test_afterimage_remains_bounded_without_clipping(self) -> None:
        histories = (
            [(1.0,)] * 20,
            [(-1.0,)] * 20,
            [(1.0,), (-1.0,)] * 10,
        )
        for tau in TAUS:
            for dt in DTS:
                for history in histories:
                    frames = run_independent_history(history, dt=dt, tau=tau)
                    self.assertLessEqual(max(abs(frame.afterimage[0]) for frame in frames), 1.0)

    def test_contact_affects_only_its_own_carrier(self) -> None:
        frame = independent_leaky_step(
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            dt=1.0,
            tau=1.0,
        )
        self.assertGreater(frame.afterimage[0], 0.0)
        self.assertEqual((0.0, 0.0), frame.afterimage[1:])

    def test_vector_update_matches_independent_scalar_orderings(self) -> None:
        previous = (0.2, -0.4, 0.7)
        contact = (-0.3, 0.8, 0.0)
        vector = independent_leaky_step(previous, contact, dt=0.5, tau=1.0)

        order = (2, 0, 1)
        permuted = independent_leaky_step(
            tuple(previous[index] for index in order),
            tuple(contact[index] for index in order),
            dt=0.5,
            tau=1.0,
        )
        restored = tuple(permuted.afterimage[order.index(index)] for index in range(3))
        self.assertEqual(vector.afterimage, restored)

    def test_same_duration_is_consistent_across_time_resolutions(self) -> None:
        end_states = []
        duration = 2.0
        for dt in DTS:
            step_count = int(duration / dt)
            frames = run_independent_history([(0.75,)] * step_count, dt=dt, tau=1.0)
            end_states.append(frames[-1].afterimage[0])
        for value in end_states[1:]:
            self.assertAlmostEqual(end_states[0], value, places=14)

    def test_amplitude_scaling_is_linear(self) -> None:
        full = run_independent_history(
            [(0.8,), (0.0,), (-0.4,), (0.2,)],
            dt=0.5,
            tau=1.0,
        )
        half = run_independent_history(
            [(0.4,), (0.0,), (-0.2,), (0.1,)],
            dt=0.5,
            tau=1.0,
        )
        for full_frame, half_frame in zip(full, half, strict=True):
            self.assertAlmostEqual(full_frame.afterimage[0] * 0.5, half_frame.afterimage[0], places=15)

    def test_same_present_contact_can_retain_different_immediate_history(self) -> None:
        with_history = run_independent_history([(1.0,), (0.0,)], dt=1.0, tau=1.0)
        without_history = run_independent_history([(0.0,), (0.0,)], dt=1.0, tau=1.0)
        self.assertEqual(with_history[-1].activation, without_history[-1].activation)
        self.assertNotEqual(with_history[-1].afterimage, without_history[-1].afterimage)

    def test_different_histories_can_collapse_to_identical_state(self) -> None:
        decay = decay_factor(dt=1.0, tau=1.0)
        first = run_independent_history([(1.0,), (0.0,)], dt=1.0, tau=1.0)
        second = run_independent_history([(0.0,), (decay,)], dt=1.0, tau=1.0)
        self.assertAlmostEqual(first[-1].afterimage[0], second[-1].afterimage[0], places=15)

        first_probe = independent_leaky_step(first[-1].afterimage, (0.25,), dt=1.0, tau=1.0)
        second_probe = independent_leaky_step(second[-1].afterimage, (0.25,), dt=1.0, tau=1.0)
        self.assertAlmostEqual(first_probe.afterimage[0], second_probe.afterimage[0], places=15)

    def test_counter_contact_can_weaken_an_existing_trace(self) -> None:
        frame = independent_leaky_step((0.8,), (-1.0,), dt=0.25, tau=4.0)
        self.assertLess(abs(frame.afterimage[0]), 0.8)

    def test_reset_is_exact_because_history_is_explicit_input(self) -> None:
        history = [(0.7,), (0.0,), (-0.2,), (0.0,)]
        first = run_independent_history(history, dt=0.5, tau=1.0)
        contrasting = run_independent_history([(-1.0,)] * 8, dt=0.5, tau=1.0)
        self.assertNotEqual(first[-1], contrasting[-1])
        repeated = run_independent_history(history, dt=0.5, tau=1.0)
        self.assertEqual(first, repeated)

    def test_invalid_domains_are_rejected_instead_of_clipped(self) -> None:
        invalid_calls = (
            lambda: independent_leaky_step((0.0,), (1.1,), dt=1.0, tau=1.0),
            lambda: independent_leaky_step((0.0,), (0.5,), dt=0.0, tau=1.0),
            lambda: independent_leaky_step((0.0,), (0.5,), dt=1.0, tau=0.0),
            lambda: independent_leaky_step((0.0,), (math.nan,), dt=1.0, tau=1.0),
            lambda: independent_leaky_step((0.0, 0.0), (0.5,), dt=1.0, tau=1.0),
        )
        for call in invalid_calls:
            with self.assertRaises(BaselineValidationError):
                call()


if __name__ == "__main__":
    unittest.main()
