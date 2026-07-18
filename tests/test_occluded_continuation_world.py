from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import unittest

from mcm_field_organism import (
    FORBIDDEN_RUNTIME_WORLD_ROLES,
    WORLD_CASE_IDS,
    WORLD_DIRECTIONS,
    OccludedContinuationWorldError,
    occluded_continuation_world_public_roles,
    receptor_contract_public_roles,
    run_occluded_continuation_world_probe,
)


class OccludedContinuationWorldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_occluded_continuation_world_probe()

    def test_preregistered_world_groups_are_complete(self) -> None:
        self.assertEqual(36, len(self.result.branches))
        self.assertEqual(
            {"w0", "w1", "w2", "w3", "w4"},
            {branch.group_id for branch in self.result.branches},
        )
        self.assertEqual(
            set(WORLD_CASE_IDS),
            {branch.case_id for branch in self.result.branches},
        )

    def test_w0_carries_world_dependency_after_exact_current_alignment(self) -> None:
        self.assertTrue(self.result.w0_world_dependency_present)
        self.assertTrue(self.result.w0_alignment_exact)
        self.assertTrue(self.result.current_state_baselines_collide)
        for case_id in WORLD_CASE_IDS:
            branches = [
                branch
                for branch in self.result.branches
                if branch.group_id == "w0" and branch.case_id == case_id
            ]
            self.assertEqual(2, len(branches))
            self.assertEqual(
                branches[0].alignment_layer_digest,
                branches[1].alignment_layer_digest,
            )
            self.assertEqual(
                branches[0].alignment_snapshot_digest,
                branches[1].alignment_snapshot_digest,
            )
            for branch in branches:
                self.assertEqual(3, branch.alignment_frame_index)
                self.assertIsNone(branch.alignment_contact)
                self.assertIsNotNone(branch.first_exit_contact)
                self.assertTrue(
                    all(value == 0.0 for value in branch.alignment_activation)
                )
                self.assertTrue(
                    all(value == 0.0 for value in branch.alignment_afterimage)
                )

    def test_w1_breaks_history_to_exit_dependency(self) -> None:
        self.assertTrue(self.result.w1_dependency_absent)
        for case_id in WORLD_CASE_IDS:
            for history_direction in WORLD_DIRECTIONS:
                exits = {
                    branch.exit_direction
                    for branch in self.result.branches
                    if branch.group_id == "w1"
                    and branch.case_id == case_id
                    and branch.history_direction == history_direction
                }
                self.assertEqual(set(WORLD_DIRECTIONS), exits)

    def test_short_and_visible_controls_retain_current_trace(self) -> None:
        self.assertTrue(self.result.w2_current_trace_distinct)
        self.assertTrue(self.result.w3_short_occlusion_trace_distinct)
        self.assertTrue(self.result.w4_contact_free_null_equal)

    def test_transformations_and_holdouts_do_not_replay_exact_sequences(self) -> None:
        self.assertTrue(self.result.transformations_equivariant)
        self.assertTrue(self.result.holdout_sequences_novel)
        self.assertTrue(self.result.exact_replay_absent)
        w0_digests = {
            branch.receptor_sequence_digest
            for branch in self.result.branches
            if branch.group_id == "w0"
        }
        self.assertEqual(2 * len(WORLD_CASE_IDS), len(w0_digests))

    def test_strong_fixed_baselines_remain_visible(self) -> None:
        self.assertTrue(self.result.finite_leaky_residual_present)
        self.assertTrue(self.result.transition_counter_explains_world)
        self.assertTrue(self.result.fixed_automaton_explains_world)

    def test_world_metadata_does_not_enter_receptor_runtime_contract(self) -> None:
        self.assertFalse(self.result.forbidden_metadata_reaches_runtime)
        receptor_roles = set().union(*map(set, receptor_contract_public_roles()))
        self.assertTrue(FORBIDDEN_RUNTIME_WORLD_ROLES.isdisjoint(receptor_roles))

    def test_observer_order_repetition_and_immutability_are_neutral(self) -> None:
        observed = []
        permuted = run_occluded_continuation_world_probe(
            case_order=reversed(WORLD_CASE_IDS),
            direction_order=reversed(WORLD_DIRECTIONS),
            observer=observed.append,
        )
        repeated = run_occluded_continuation_world_probe()
        self.assertEqual(self.result, permuted)
        self.assertEqual(self.result, repeated)
        self.assertEqual(self.result.digest(), permuted.digest())
        self.assertEqual(self.result.digest(), repeated.digest())
        self.assertTrue(permuted.observer_is_neutral)
        self.assertEqual(len(permuted.branches), len(observed))
        with self.assertRaises(FrozenInstanceError):
            observed[0].group_id = "changed"  # type: ignore[misc]

    def test_result_cannot_release_memory_or_writeback(self) -> None:
        for role in ("writes_back", "adds_memory_role", "changes_field_transition"):
            with self.assertRaises(OccludedContinuationWorldError):
                replace(self.result, **{role: True})

    def test_public_observer_roles_contain_no_raw_frames_or_semantics(self) -> None:
        forbidden = {
            "frame",
            "image",
            "pixels",
            "object",
            "person",
            "meaning",
            "semantic_label",
            "reward",
            "winner",
            "memory_state",
            "topology",
        }
        self.assertTrue(
            forbidden.isdisjoint(occluded_continuation_world_public_roles())
        )

    def test_invalid_orders_are_rejected_before_a_run(self) -> None:
        invalid = (
            lambda: run_occluded_continuation_world_probe(case_order=("base",)),
            lambda: run_occluded_continuation_world_probe(direction_order=(1, 1)),
            lambda: run_occluded_continuation_world_probe(
                direction_order=(-1, True)
            ),
        )
        for call in invalid:
            with self.assertRaises(OccludedContinuationWorldError):
                call()


if __name__ == "__main__":
    unittest.main()
