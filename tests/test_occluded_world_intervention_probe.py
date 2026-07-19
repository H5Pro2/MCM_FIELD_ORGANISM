from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import unittest

from mcm_field_organism import (
    FORBIDDEN_INTERVENTION_RUNTIME_ROLES,
    INTERVENTION_BRANCH_IDS,
    OccludedWorldInterventionError,
    run_occluded_world_intervention_probe,
)


class OccludedWorldInterventionProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_occluded_world_intervention_probe()

    def test_preregistered_branches_are_complete(self) -> None:
        self.assertEqual(
            tuple(sorted(INTERVENTION_BRANCH_IDS)),
            tuple(branch.branch_id for branch in self.result.branches),
        )

    def test_visible_and_hidden_world_consequences_follow_one_rule(self) -> None:
        self.assertTrue(self.result.null_consequence_preserves_direction)
        self.assertTrue(self.result.reversal_uses_same_world_rule)
        self.assertTrue(self.result.visible_consequence_reaches_current_field)
        self.assertTrue(self.result.hidden_consequence_remains_contact_free)

    def test_fixed_holdouts_and_mirror_are_world_determined(self) -> None:
        self.assertTrue(self.result.holdouts_follow_world_state)
        self.assertTrue(self.result.mirrored_branches_are_equivariant)
        self.assertTrue(self.result.paired_budgets_equal)

    def test_existing_projection_baseline_explains_every_field_state(self) -> None:
        self.assertTrue(self.result.receptor_projection_explains_all_field_states)
        for branch in self.result.branches:
            for frame in branch.frames:
                self.assertTrue(all(value == 0.0 for value in frame.afterimage))

    def test_provenance_is_assigned_only_after_completed_world_runs(self) -> None:
        self.assertTrue(self.result.provenance_is_observer_only)
        self.assertTrue(self.result.recontact_carries_no_event_id)
        self.assertEqual(4, len(self.result.observer_provenance))
        self.assertTrue(
            FORBIDDEN_INTERVENTION_RUNTIME_ROLES.isdisjoint(
                {
                    "activation",
                    "afterimage",
                    "receptor_contact",
                    "neighbor_sample",
                }
            )
        )

    def test_order_repetition_and_observer_are_neutral(self) -> None:
        observed = []
        permuted = run_occluded_world_intervention_probe(
            branch_order=reversed(INTERVENTION_BRANCH_IDS),
            observer=observed.append,
        )
        repeated = run_occluded_world_intervention_probe()
        self.assertEqual(self.result, permuted)
        self.assertEqual(self.result, repeated)
        self.assertEqual(self.result.digest(), repeated.digest())
        self.assertTrue(permuted.observer_is_neutral)
        with self.assertRaises(FrozenInstanceError):
            observed[0].branch_id = "changed"  # type: ignore[misc]

    def test_probe_cannot_release_forbidden_mechanics(self) -> None:
        forbidden = (
            "writes_back",
            "adds_memory_role",
            "changes_field_transition",
            "adds_noise",
            "adds_variance",
            "adds_rest_dynamics",
        )
        for role in forbidden:
            with self.assertRaises(OccludedWorldInterventionError):
                replace(self.result, **{role: True})

    def test_invalid_branch_orders_are_rejected(self) -> None:
        for order in (("v0",), ("v0", "v0", "h0", "h1")):
            with self.assertRaises(OccludedWorldInterventionError):
                run_occluded_world_intervention_probe(branch_order=order)


if __name__ == "__main__":
    unittest.main()
