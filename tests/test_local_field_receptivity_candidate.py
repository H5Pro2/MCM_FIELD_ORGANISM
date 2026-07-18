from __future__ import annotations

import unittest

from mcm_field_organism.local_field_receptivity_candidate import (
    C1_BASELINE_IDS,
    C1_BRANCH_IDS,
    LocalFieldReceptivityCandidateError,
    LocalFieldReceptivityState,
    run_local_field_receptivity_candidate,
)


class LocalFieldReceptivityCandidateTests(unittest.TestCase):
    def test_c1_carries_only_the_preregistered_delayed_effect(self) -> None:
        result = run_local_field_receptivity_candidate()

        self.assertEqual(
            tuple(branch.branch_id for branch in result.branches),
            tuple(sorted(C1_BRANCH_IDS)),
        )
        self.assertEqual(result.baseline_ids, C1_BASELINE_IDS)
        self.assertTrue(result.fast_states_matched_before_probe)
        self.assertTrue(result.raw_mirror_responses_differ)
        self.assertTrue(result.canonical_mirror_response_exact)
        self.assertTrue(result.swapped_state_moves_effect_exactly)
        self.assertTrue(result.equalized_state_collapses_branches)
        self.assertTrue(result.null_state_recovers_neutral_exactly)
        self.assertTrue(result.local_field_ablation_removes_candidate_exactly)
        self.assertTrue(result.candidate_carries_delayed_field_effect)

    def test_strong_baseline_classifies_c1_as_bounded_integrator(self) -> None:
        result = run_local_field_receptivity_candidate()

        self.assertTrue(result.b1_b2_collide_after_fast_state_matching)
        self.assertTrue(result.b3_cannot_separate_field_ablation)
        self.assertTrue(result.b4_explains_candidate_exactly)
        self.assertTrue(result.b5_cannot_separate_histories)
        self.assertFalse(result.topology_supported)
        self.assertFalse(result.organic_memory_supported)
        self.assertFalse(result.runtime_extended)
        self.assertFalse(result.writes_back)

    def test_time_partition_snapshot_observer_and_order_are_neutral(self) -> None:
        observed = []
        result = run_local_field_receptivity_candidate(
            observer=lambda branch: observed.append(branch.digest())
        )

        self.assertEqual(len(observed), len(C1_BRANCH_IDS))
        self.assertLessEqual(result.time_partition_max_error, 1e-12)
        self.assertTrue(result.time_partition_neutral)
        self.assertTrue(result.snapshot_resume_exact)
        self.assertTrue(result.observer_is_neutral)
        self.assertTrue(result.branch_order_is_neutral)

    def test_result_is_reproducible(self) -> None:
        first = run_local_field_receptivity_candidate()
        second = run_local_field_receptivity_candidate()

        self.assertEqual(first.digest(), second.digest())

    def test_candidate_state_roundtrip_and_validation(self) -> None:
        state = LocalFieldReceptivityState(("n0", "n1"), (0.25, -0.5))
        self.assertEqual(
            LocalFieldReceptivityState.from_json(state.to_json()),
            state,
        )
        with self.assertRaises(LocalFieldReceptivityCandidateError):
            LocalFieldReceptivityState(("n0",), (1.1,))
        with self.assertRaises(LocalFieldReceptivityCandidateError):
            run_local_field_receptivity_candidate(branch_order=("h_plus",))


if __name__ == "__main__":
    unittest.main()
