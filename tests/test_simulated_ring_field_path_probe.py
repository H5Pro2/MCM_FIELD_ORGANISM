from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import unittest

from mcm_field_organism import (
    METHODIK_031_OPEN_DIGEST,
    SimulatedRingFieldPathProbeError,
    WORLD_CAUSES,
    WORLD_DELTAS,
    WORLD_POSITIONS,
    run_simulated_ring_field_path_probe,
    run_simulated_world_mcm_path_probe,
    simulated_ring_field_path_public_roles,
)


class SimulatedRingFieldPathProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_simulated_ring_field_path_probe()

    def test_complete_preregistered_families_are_present(self) -> None:
        self.assertEqual(42, len(self.result.branches))
        self.assertEqual(21, len(self.result.cause_pairs))
        self.assertEqual(14, len(self.result.transformations))

    def test_historical_open_path_digest_remains_unchanged(self) -> None:
        self.assertTrue(self.result.historical_open_digest_unchanged)
        self.assertEqual(
            METHODIK_031_OPEN_DIGEST,
            run_simulated_world_mcm_path_probe().digest(),
        )

    def test_each_step_adds_only_the_two_wrap_samples(self) -> None:
        self.assertTrue(self.result.all_steps_have_two_wrap_samples)
        for branch in self.result.branches:
            for step in (branch.step_one, branch.step_two):
                self.assertEqual(
                    {(0, -1, 6), (6, 1, 0)},
                    {
                        (
                            sample.target_position,
                            sample.offset,
                            sample.source_position,
                        )
                        for sample in step.wrap_samples
                    },
                )

    def test_first_step_wraps_read_only_the_initial_zero_state(self) -> None:
        self.assertTrue(self.result.step_one_wraps_are_initial_zero)
        for branch in self.result.branches:
            for sample in branch.step_one.wrap_samples:
                self.assertEqual(
                    (0, 0.0, 0.0),
                    (
                        sample.source_tick,
                        sample.activation,
                        sample.afterimage,
                    ),
                )

    def test_second_step_has_the_exact_active_wrap_counts(self) -> None:
        self.assertTrue(self.result.active_wrap_counts_exact)
        self.assertEqual(6, self.result.active_source_six_count)
        self.assertEqual(6, self.result.active_source_zero_count)
        self.assertEqual(30, self.result.inactive_branch_count)

    def test_fast_state_is_equal_while_geometry_digest_is_distinct(self) -> None:
        self.assertTrue(self.result.all_fast_states_equal)
        self.assertTrue(self.result.all_full_digests_geometry_distinct)
        self.assertTrue(self.result.all_normalized_states_equal)
        for branch in self.result.branches:
            for step in (branch.step_one, branch.step_two):
                self.assertNotEqual(step.open_window_digest, step.ring_window_digest)
                self.assertEqual(
                    step.normalized_open_window_digest,
                    step.normalized_ring_window_digest,
                )
                self.assertNotEqual(
                    step.open_constellation_digest,
                    step.ring_constellation_digest,
                )
                self.assertEqual(
                    step.normalized_open_constellation_digest,
                    step.normalized_ring_constellation_digest,
                )

    def test_all_cause_pairs_collapse_after_outer_provenance(self) -> None:
        self.assertTrue(self.result.all_cause_pairs_collapse)
        for pair in self.result.cause_pairs:
            self.assertTrue(pair.first_provenance_distinct)
            self.assertTrue(pair.hold_provenance_distinct)
            self.assertTrue(pair.first_receptor_equal)
            self.assertTrue(pair.hold_receptor_equal)
            self.assertTrue(pair.step_one_equal)
            self.assertTrue(pair.step_two_equal)

    def test_all_rotations_and_reflections_are_equivariant(self) -> None:
        self.assertTrue(self.result.all_transformations_equivariant)
        self.assertEqual(
            {(rotation, orientation) for rotation in range(7) for orientation in (-1, 1)},
            {
                (item.rotation, item.orientation)
                for item in self.result.transformations
            },
        )

    def test_reset_observer_order_and_repetition_are_neutral(self) -> None:
        self.assertTrue(self.result.reset_is_clean)
        observed = []
        permuted = run_simulated_ring_field_path_probe(
            position_order=reversed(WORLD_POSITIONS),
            delta_order=reversed(WORLD_DELTAS),
            cause_order=reversed(WORLD_CAUSES),
            reverse_neurons=True,
            reverse_offsets=True,
            observer=observed.append,
        )
        self.assertEqual(self.result, permuted)
        self.assertTrue(permuted.observer_is_neutral)
        self.assertTrue(permuted.order_is_neutral)
        self.assertTrue(permuted.repeated_run_is_neutral)
        self.assertEqual(42, len(observed))
        with self.assertRaises(FrozenInstanceError):
            observed[0].delta = 0  # type: ignore[misc]

    def test_invalid_probe_orders_are_rejected(self) -> None:
        invalid_calls = (
            lambda: run_simulated_ring_field_path_probe(position_order=(0, 1)),
            lambda: run_simulated_ring_field_path_probe(delta_order=(-1, 0, 0)),
            lambda: run_simulated_ring_field_path_probe(
                cause_order=("unknown", "external")  # type: ignore[arg-type]
            ),
        )
        for call in invalid_calls:
            with self.assertRaises(SimulatedRingFieldPathProbeError):
                call()

    def test_result_cannot_claim_writeback_rule_or_effector_connection(self) -> None:
        self.assertFalse(self.result.writes_back)
        self.assertFalse(self.result.releases_field_rule)
        self.assertFalse(self.result.connects_effector)
        with self.assertRaises(SimulatedRingFieldPathProbeError):
            replace(self.result, writes_back=True)
        with self.assertRaises(SimulatedRingFieldPathProbeError):
            replace(self.result, releases_field_rule=True)
        with self.assertRaises(SimulatedRingFieldPathProbeError):
            replace(self.result, connects_effector=True)

    def test_inner_roles_contain_no_action_relationship_or_semantics(self) -> None:
        forbidden = {
            "action",
            "reward",
            "winner",
            "weight",
            "continuity",
            "relationship",
            "semantic_label",
            "effector_value",
        }
        for roles in simulated_ring_field_path_public_roles()[:2]:
            self.assertTrue(forbidden.isdisjoint(roles))


if __name__ == "__main__":
    unittest.main()
