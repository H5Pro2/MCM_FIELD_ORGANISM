from __future__ import annotations

from itertools import permutations
import unittest

from mcm_field_organism import (
    BaselineValidationError,
    ControlledReceptorSurface,
    decay_factor,
    independent_leaky_step,
    run_independent_surface_history,
    stateless_surface_frame,
    surface_sum_baseline,
)


TAUS = (0.25, 1.0, 4.0)
DTS = (1.0, 0.5, 0.25)


class ControlledReceptorSurfaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.surface = ControlledReceptorSurface()

    def test_surface_has_stable_row_major_technical_identity(self) -> None:
        self.assertEqual(9, self.surface.size)
        self.assertEqual(
            ("p00", "p01", "p02", "p10", "p11", "p12", "p20", "p21", "p22"),
            self.surface.carrier_ids,
        )

    def test_each_single_contact_maps_only_to_its_own_position(self) -> None:
        for row in range(3):
            for column in range(3):
                vector = self.surface.contact_vector({(row, column): 0.75})
                self.assertEqual(0.75, vector[self.surface.index((row, column))])
                self.assertEqual(1, sum(value != 0.0 for value in vector))

    def test_invalid_positions_and_values_are_rejected(self) -> None:
        invalid_calls = (
            lambda: self.surface.contact_vector({(3, 0): 0.5}),
            lambda: self.surface.contact_vector({(-1, 0): 0.5}),
            lambda: self.surface.contact_vector({(0, 0): 1.1}),
            lambda: ControlledReceptorSurface(rows=0),
        )
        for call in invalid_calls:
            with self.assertRaises(BaselineValidationError):
                call()

    def test_b0_preserves_current_distribution_but_no_history(self) -> None:
        contacts = {(0, 0): 0.8, (2, 2): -0.4}
        frame = stateless_surface_frame(self.surface, contacts)
        self.assertEqual(self.surface.contact_vector(contacts), frame.activation)
        self.assertEqual((0.0,) * 9, frame.afterimage)

    def test_equal_sum_distributions_collide_only_in_b2(self) -> None:
        first = {(0, 0): 1.0, (0, 1): 0.5}
        second = {(2, 2): 1.0, (1, 2): 0.5}
        self.assertEqual(surface_sum_baseline(self.surface, first), surface_sum_baseline(self.surface, second))
        self.assertNotEqual(self.surface.contact_vector(first), self.surface.contact_vector(second))

    def test_adjacent_and_separated_contacts_remain_distinct_without_coupling(self) -> None:
        adjacent = self.surface.contact_vector({(1, 0): 0.5, (1, 1): 0.5})
        separated = self.surface.contact_vector({(0, 0): 0.5, (2, 2): 0.5})
        self.assertEqual(sum(adjacent), sum(separated))
        self.assertNotEqual(adjacent, separated)

    def test_forward_and_reverse_paths_leave_different_distributed_traces(self) -> None:
        forward = [{(1, 0): 1.0}, {(1, 1): 1.0}, {(1, 2): 1.0}, {}]
        reverse = [{(1, 2): 1.0}, {(1, 1): 1.0}, {(1, 0): 1.0}, {}]
        for tau in TAUS:
            for dt in DTS:
                forward_end = run_independent_surface_history(self.surface, forward, dt=dt, tau=tau)[-1]
                reverse_end = run_independent_surface_history(self.surface, reverse, dt=dt, tau=tau)[-1]
                self.assertEqual(forward_end.activation, reverse_end.activation)
                self.assertNotEqual(forward_end.afterimage, reverse_end.afterimage)

    def test_same_endpoint_retains_other_position_history_in_full_vector(self) -> None:
        from_left = [{(1, 0): 1.0}, {(1, 1): 1.0}]
        from_right = [{(1, 2): 1.0}, {(1, 1): 1.0}]
        left_end = run_independent_surface_history(self.surface, from_left, dt=1.0, tau=1.0)[-1]
        right_end = run_independent_surface_history(self.surface, from_right, dt=1.0, tau=1.0)[-1]
        center = self.surface.index((1, 1))
        self.assertEqual(left_end.activation, right_end.activation)
        self.assertEqual(left_end.afterimage[center], right_end.afterimage[center])
        self.assertNotEqual(left_end.afterimage, right_end.afterimage)

    def test_pause_changes_the_distributed_trace_without_new_mechanism(self) -> None:
        direct = [{(1, 0): 1.0}, {(1, 1): 1.0}, {(1, 2): 1.0}]
        paused = [{(1, 0): 1.0}, {}, {(1, 1): 1.0}, {(1, 2): 1.0}]
        direct_end = run_independent_surface_history(self.surface, direct, dt=1.0, tau=1.0)[-1]
        paused_end = run_independent_surface_history(self.surface, paused, dt=1.0, tau=1.0)[-1]
        self.assertNotEqual(direct_end.afterimage, paused_end.afterimage)

    def test_translated_history_has_corresponding_translated_state(self) -> None:
        top = [{(0, 0): 0.8}, {(0, 1): 0.4}, {}]
        middle = [{(1, 0): 0.8}, {(1, 1): 0.4}, {}]
        top_end = run_independent_surface_history(self.surface, top, dt=0.5, tau=1.0)[-1]
        middle_end = run_independent_surface_history(self.surface, middle, dt=0.5, tau=1.0)[-1]
        translated = self.surface.translate_vector(top_end.afterimage, row_offset=1, column_offset=0)
        self.assertEqual(translated, middle_end.afterimage)

    def test_no_contact_spreads_to_an_uncontacted_position(self) -> None:
        history = [{(0, 0): 1.0}, {}, {}]
        end = run_independent_surface_history(self.surface, history, dt=1.0, tau=1.0)[-1]
        self.assertGreater(end.afterimage[self.surface.index((0, 0))], 0.0)
        for position in ((0, 1), (1, 0), (1, 1), (2, 2)):
            self.assertEqual(0.0, end.afterimage[self.surface.index(position)])

    def test_positive_and_negative_multicontact_preserve_local_polarity(self) -> None:
        history = [{(0, 0): 1.0, (2, 2): -1.0}, {}]
        end = run_independent_surface_history(self.surface, history, dt=1.0, tau=1.0)[-1]
        self.assertGreater(end.afterimage[self.surface.index((0, 0))], 0.0)
        self.assertLess(end.afterimage[self.surface.index((2, 2))], 0.0)

    def test_full_zero_history_stays_zero(self) -> None:
        frames = run_independent_surface_history(self.surface, [{}, {}, {}], dt=1.0, tau=1.0)
        self.assertTrue(all(frame.activation == (0.0,) * 9 for frame in frames))
        self.assertTrue(all(frame.afterimage == (0.0,) * 9 for frame in frames))

    def test_different_surface_histories_can_collapse_exactly(self) -> None:
        for tau in TAUS:
            for dt in DTS:
                decay = decay_factor(dt=dt, tau=tau)
                first = [{(0, 0): 1.0}, {}, {}]
                second = [{}, {(0, 0): decay}, {}]
                first_end = run_independent_surface_history(self.surface, first, dt=dt, tau=tau)[-1]
                second_end = run_independent_surface_history(self.surface, second, dt=dt, tau=tau)[-1]
                for left, right in zip(first_end.afterimage, second_end.afterimage, strict=True):
                    self.assertAlmostEqual(left, right, places=15)
                self.assertEqual(first_end.activation, second_end.activation)

    def test_permuted_independent_calculation_restores_exact_surface_state(self) -> None:
        previous = self.surface.contact_vector({(0, 0): 0.2, (1, 1): -0.4, (2, 2): 0.7})
        contact = self.surface.contact_vector({(0, 2): -0.3, (1, 1): 0.8})
        expected = independent_leaky_step(previous, contact, dt=0.5, tau=1.0)

        for order in permutations((0, 4, 8)):
            remaining = tuple(index for index in range(9) if index not in order)
            full_order = order + remaining
            permuted = independent_leaky_step(
                tuple(previous[index] for index in full_order),
                tuple(contact[index] for index in full_order),
                dt=0.5,
                tau=1.0,
            )
            restored = tuple(permuted.afterimage[full_order.index(index)] for index in range(9))
            self.assertEqual(expected.afterimage, restored)


if __name__ == "__main__":
    unittest.main()
