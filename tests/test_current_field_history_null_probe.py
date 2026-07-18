from __future__ import annotations

import unittest

from mcm_field_organism import (
    current_field_history_null_probe_public_roles,
    run_current_field_history_null_probe,
)


class CurrentFieldHistoryNullProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.result = run_current_field_history_null_probe()

    def test_histories_differ_only_in_order_and_end_contact(self) -> None:
        self.assertTrue(self.result.histories_distinct)
        self.assertTrue(self.result.history_contact_multisets_equal)
        self.assertNotEqual(
            self.result.first_branch.history[-1],
            self.result.second_branch.history[-1],
        )

    def test_terminal_full_layer_states_are_initially_distinct(self) -> None:
        self.assertTrue(self.result.terminal_full_states_distinct)

    def test_one_alignment_step_matches_fast_vectors_not_full_state(self) -> None:
        self.assertTrue(self.result.first_alignment_fast_vectors_equal)
        self.assertFalse(self.result.first_alignment_full_states_equal)
        self.assertEqual(
            (0.0, 0.0),
            self.result.first_branch.first_alignment_activation,
        )
        self.assertEqual(
            (0.0, 0.0),
            self.result.first_branch.first_alignment_afterimage,
        )

    def test_second_alignment_step_matches_complete_layer_state(self) -> None:
        self.assertTrue(self.result.second_alignment_full_states_equal)
        self.assertEqual(
            (0.0, 0.0),
            self.result.first_branch.second_alignment_activation,
        )
        self.assertEqual(
            (0.0, 0.0),
            self.result.first_branch.second_alignment_afterimage,
        )

    def test_identical_probe_produces_identical_complete_state(self) -> None:
        self.assertTrue(self.result.identical_probe_full_states_equal)
        self.assertFalse(self.result.functional_difference_observed)
        self.assertEqual(
            (0.6, 0.4),
            self.result.first_branch.probe_activation,
        )
        self.assertEqual(
            (0.0, 0.0),
            self.result.first_branch.probe_afterimage,
        )

    def test_probe_uses_only_existing_runtime_without_manual_reset(self) -> None:
        self.assertFalse(self.result.manual_state_copy_used)
        self.assertFalse(self.result.new_history_carrier_added)
        self.assertFalse(self.result.observer_writeback_performed)
        self.assertFalse(self.result.runtime_candidate_released)

    def test_public_roles_add_no_history_storage_or_effect(self) -> None:
        forbidden = {
            "history_template",
            "sequence_archive",
            "history_carrier",
            "effect_weight",
            "memory",
            "topology",
            "meaning",
        }
        self.assertTrue(
            forbidden.isdisjoint(
                current_field_history_null_probe_public_roles()
            )
        )


if __name__ == "__main__":
    unittest.main()
