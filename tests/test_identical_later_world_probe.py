from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import unittest

from mcm_field_organism import (
    OccludedWorldInterventionError,
    run_identical_later_world_probe,
)


class IdenticalLaterWorldProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_identical_later_world_probe()

    def test_probe_a_aligns_current_contact_and_direct_outputs(self) -> None:
        self.assertTrue(self.result.probe_a_current_contact_equal)
        self.assertTrue(self.result.probe_a_activation_equal)
        self.assertTrue(self.result.probe_a_afterimage_equal)
        self.assertEqual(
            ((2, 3, 4, 5, 6, 7), (2, 3, 4, 3, 2, 1)),
            tuple(branch.history_positions for branch in self.result.branches),
        )
        self.assertTrue(
            all(
                branch.probe_a.position == branch.probe_b.position == 8
                for branch in self.result.branches
            )
        )

    def test_probe_a_still_exposes_the_known_previous_local_sample(self) -> None:
        self.assertFalse(self.result.probe_a_full_snapshot_equal)
        self.assertTrue(self.result.known_one_step_perception_visible_at_probe_a)

    def test_probe_b_aligns_the_complete_known_runtime_state(self) -> None:
        self.assertTrue(self.result.probe_b_receptor_distribution_equal)
        self.assertTrue(self.result.probe_b_activation_equal)
        self.assertTrue(self.result.probe_b_afterimage_equal)
        self.assertTrue(self.result.probe_b_layer_equal)
        self.assertTrue(self.result.probe_b_full_snapshot_equal)
        self.assertTrue(self.result.no_residual_after_known_alignment)

    def test_no_metadata_or_new_mechanics_enter_runtime(self) -> None:
        self.assertFalse(self.result.forbidden_metadata_reaches_runtime)
        for role in (
            "writes_back",
            "adds_memory_role",
            "changes_field_transition",
            "adds_noise",
            "adds_variance",
            "adds_rest_dynamics",
        ):
            with self.assertRaises(OccludedWorldInterventionError):
                replace(self.result, **{role: True})

    def test_order_repetition_and_observer_are_neutral(self) -> None:
        observed = []
        permuted = run_identical_later_world_probe(
            branch_order=("h1", "h0"),
            observer=observed.append,
        )
        repeated = run_identical_later_world_probe()
        self.assertEqual(self.result, permuted)
        self.assertEqual(self.result, repeated)
        self.assertEqual(self.result.digest(), repeated.digest())
        self.assertTrue(self.result.order_and_repetition_neutral)
        self.assertTrue(permuted.observer_is_neutral)
        with self.assertRaises(FrozenInstanceError):
            observed[0].branch_id = "changed"  # type: ignore[misc]

    def test_invalid_branch_orders_are_rejected(self) -> None:
        for order in (("h0",), ("h0", "h0"), ("v0", "h1")):
            with self.assertRaises(OccludedWorldInterventionError):
                run_identical_later_world_probe(branch_order=order)


if __name__ == "__main__":
    unittest.main()
