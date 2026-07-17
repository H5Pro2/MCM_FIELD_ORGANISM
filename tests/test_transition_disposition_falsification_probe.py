import json
import subprocess
import sys
import unittest

from mcm_field_organism import (
    MATRIX_BASELINE_IDS,
    MATRIX_BRANCH_IDS,
    P1_A_HISTORY,
    P2_COMPETITION_B,
    P2_IDLE,
    P2_MATCHED_NONCOMPETITION,
    P2_UNRELATED_U,
    SATURATION_CAPACITIES,
    TRANSITION_DECAYS,
    TransitionDispositionFalsificationProbeError,
    run_transition_disposition_falsification_probe,
    transition_disposition_falsification_probe_public_roles,
)


class TransitionDispositionFalsificationProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_transition_disposition_falsification_probe()
        cls.branches = {item.branch_id: item for item in cls.result.branches}
        cls.counters = {item.branch_id: item for item in cls.result.counters}
        cls.globals = {
            item.branch_id: item for item in cls.result.global_normalizations
        }

    def test_world_matches_preregistration(self):
        self.assertEqual(P1_A_HISTORY, (2, 3, None, None) * 4)
        self.assertEqual(P2_COMPETITION_B, (4, 3, None, None) * 4)
        self.assertEqual(P2_MATCHED_NONCOMPETITION, (4, None, 3, None) * 4)
        self.assertEqual(P2_UNRELATED_U, (5, 6, None, None) * 4)
        self.assertEqual(P2_IDLE, (None,) * 16)

    def test_branch_lengths_and_energies_are_exact(self):
        for branch in self.result.branches:
            self.assertEqual(branch.frame_count, 33)
            self.assertEqual(branch.p1_energy, 8.0)
        self.assertEqual(self.branches["competition_b"].p2_energy, 8.0)
        self.assertEqual(self.branches["matched_noncompetition"].p2_energy, 8.0)
        self.assertEqual(self.branches["unrelated_u"].p2_energy, 8.0)
        self.assertEqual(self.branches["idle"].p2_energy, 0.0)

    def test_competition_and_matched_control_have_equal_frequency(self):
        competition = self.branches["competition_b"]
        matched = self.branches["matched_noncompetition"]
        self.assertEqual(competition.position_frequency, matched.position_frequency)
        self.assertTrue(
            self.result.competition_and_matched_are_position_energy_equal
        )
        self.assertTrue(self.result.neuron_frequency_cannot_detect_competition)

    def test_transition_events_are_local_and_exact(self):
        self.assertTrue(self.result.preregistered_transition_counts_exact)
        self.assertEqual(self.branches["competition_b"].a_event_count, 4.0)
        self.assertEqual(self.branches["competition_b"].b_event_count, 4.0)
        self.assertEqual(self.branches["matched_noncompetition"].b_event_count, 0.0)
        self.assertEqual(self.branches["unrelated_u"].u_event_count, 4.0)
        for branch in self.result.branches:
            for event in branch.events:
                self.assertEqual(event.source_tick, event.target_tick - 1)
                self.assertEqual(event.evidence, 1.0)

    def test_fast_field_and_baseline_fresh_states_are_zero(self):
        self.assertTrue(self.result.fast_field_resets_all_branches)
        self.assertTrue(self.result.baseline_resets_are_zero)
        for branch in self.result.branches:
            self.assertEqual(branch.final_activation_max, 0.0)
            self.assertEqual(branch.final_afterimage_max, 0.0)

    def test_counter_and_permanent_edge_keep_old_a(self):
        self.assertTrue(self.result.counter_keeps_a_equal_under_competition)
        self.assertTrue(self.result.permanent_edges_keep_a_equal_under_competition)
        self.assertEqual(self.counters["competition_b"].a_count, 4.0)
        self.assertEqual(self.counters["matched_noncompetition"].a_count, 4.0)
        self.assertEqual(self.counters["competition_b"].a_permanent, 1.0)

    def test_leaky_transition_families_keep_old_a(self):
        self.assertTrue(self.result.leaky_traces_keep_a_equal_under_competition)
        by_key = {
            (item.branch_id, item.decay): item
            for item in self.result.leaky_traces
        }
        for decay in TRANSITION_DECAYS:
            self.assertEqual(
                by_key[("competition_b", decay)].a_value,
                by_key[("matched_noncompetition", decay)].a_value,
            )

    def test_independent_saturation_keeps_old_a(self):
        self.assertTrue(self.result.saturation_keeps_a_equal_under_competition)
        by_key = {
            (item.branch_id, item.capacity): item
            for item in self.result.saturated_traces
        }
        for capacity in SATURATION_CAPACITIES:
            self.assertEqual(
                by_key[("competition_b", capacity)].a_value,
                by_key[("matched_noncompetition", capacity)].a_value,
            )

    def test_global_normalization_reduces_a_but_breaks_locality(self):
        self.assertTrue(
            self.result.global_normalization_reduces_a_under_competition
        )
        self.assertTrue(
            self.result.global_normalization_violates_locality_under_u
        )
        self.assertEqual(self.globals["competition_b"].a_share, 0.5)
        self.assertEqual(self.globals["matched_noncompetition"].a_share, 1.0)
        self.assertEqual(self.globals["unrelated_u"].a_share, 0.5)
        self.assertEqual(self.globals["idle"].a_share, 1.0)

    def test_matrix_carries_only_the_preregistered_negative_result(self):
        self.assertTrue(
            self.result.no_local_baseline_carries_competition_coupled_release
        )
        self.assertFalse(self.result.retains_raw_frames)
        self.assertFalse(self.result.writes_back)
        self.assertFalse(self.result.releases_resource_or_disposition)
        self.assertTrue(all(item.input_frames_unchanged for item in self.result.branches))

    def test_observer_order_and_repetition_are_neutral(self):
        observed = []
        result = run_transition_disposition_falsification_probe(
            observer=lambda branch: observed.append(branch.branch_id)
        )
        self.assertEqual(len(observed), len(MATRIX_BRANCH_IDS))
        self.assertTrue(result.observer_is_neutral)
        self.assertTrue(result.branch_order_is_neutral)
        self.assertTrue(result.baseline_order_is_neutral)
        self.assertTrue(result.repeated_run_is_neutral)

    def test_invalid_orders_are_rejected(self):
        with self.assertRaises(TransitionDispositionFalsificationProbeError):
            run_transition_disposition_falsification_probe(
                branch_order=MATRIX_BRANCH_IDS[:-1],
            )
        with self.assertRaises(TransitionDispositionFalsificationProbeError):
            run_transition_disposition_falsification_probe(
                baseline_order=MATRIX_BASELINE_IDS[:-1],
            )

    def test_public_roles_contain_no_semantic_or_learning_state(self):
        roles = transition_disposition_falsification_probe_public_roles()
        forbidden = {
            "label",
            "meaning",
            "semantic",
            "reward",
            "action",
            "learned_weight",
        }
        self.assertFalse(forbidden.intersection(roles))

    def test_digest_is_stable_across_processes(self):
        script = (
            "from mcm_field_organism import "
            "run_transition_disposition_falsification_probe as run;"
            "print(run().digest())"
        )
        first = subprocess.check_output(
            [sys.executable, "-c", script],
            text=True,
        ).strip()
        second = subprocess.check_output(
            [sys.executable, "-c", script],
            text=True,
        ).strip()
        self.assertEqual(first, second)
        self.assertEqual(first, self.result.digest())
        self.assertEqual(len(first), 64)

    def test_canonical_payload_is_json_serializable(self):
        encoded = json.dumps(
            self.result.canonical_payload(),
            allow_nan=False,
            sort_keys=True,
        )
        self.assertIn('"competition_b"', encoded)


if __name__ == "__main__":
    unittest.main()
