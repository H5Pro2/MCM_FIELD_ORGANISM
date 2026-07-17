from __future__ import annotations

from dataclasses import asdict
import unittest

import numpy as np

from mcm_field_organism import (
    BRANCH_IDS,
    FORM_A_BASE,
    FORM_B_BASE,
    FORM_HOLDOUT,
    CondensedFieldFormNullProbeError,
    condensed_field_form_null_probe_public_roles,
    run_condensed_field_form_null_probe,
)


class CondensedFieldFormNullProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_condensed_field_form_null_probe()

    def test_preregistered_geometry_is_fixed_and_nonidentical(self) -> None:
        self.assertEqual(((1, 1), (2, 1), (3, 1), (3, 2)), FORM_A_BASE)
        self.assertEqual(((1, 1), (1, 2), (1, 3), (2, 2)), FORM_B_BASE)
        self.assertEqual(((1, 3), (2, 3), (3, 2), (3, 3)), FORM_HOLDOUT)
        self.assertEqual(4, len(set(FORM_A_BASE)))
        self.assertEqual(4, len(set(FORM_B_BASE)))
        self.assertNotEqual(set(FORM_A_BASE), set(FORM_B_BASE))

    def test_complete_preregistered_result_families_are_present(self) -> None:
        self.assertEqual(4, len(self.result.branches))
        self.assertEqual(3, len(self.result.pair_comparisons))
        self.assertEqual(9, len(self.result.leaky_baselines))
        self.assertEqual(9, len(self.result.recurrent_baselines))
        self.assertEqual(4, len(self.result.template_baselines))
        self.assertEqual(
            tuple(sorted(BRANCH_IDS)),
            tuple(item.branch_id for item in self.result.branches),
        )

    def test_history_energy_is_matched_except_for_declared_zero_branch(self) -> None:
        energy = {
            item.branch_id: item.history_contact_energy
            for item in self.result.branches
        }
        self.assertEqual(16.0, energy["history_a"])
        self.assertEqual(16.0, energy["history_b"])
        self.assertEqual(16.0, energy["history_permuted"])
        self.assertEqual(0.0, energy["history_zero"])

    def test_fast_state_and_prior_local_field_are_exactly_empty(self) -> None:
        self.assertTrue(self.result.all_pre_holdout_fast_states_zero)
        for branch in self.result.branches:
            self.assertEqual(0.0, branch.pre_holdout_activation_max)
            self.assertEqual(0.0, branch.pre_holdout_afterimage_max)
            self.assertEqual(0.0, branch.holdout_previous_field_max)

    def test_identical_holdout_collides_after_every_history(self) -> None:
        self.assertTrue(self.result.all_holdout_windows_equal)
        self.assertTrue(self.result.all_holdout_local_inputs_equal)
        for comparison in self.result.pair_comparisons:
            self.assertEqual(0.0, comparison.activation_l1)
            self.assertEqual(0.0, comparison.afterimage_l1)
            self.assertTrue(comparison.window_digest_equal)
            self.assertTrue(comparison.local_input_digest_equal)

    def test_fixed_traces_expose_only_natural_residuals(self) -> None:
        self.assertTrue(self.result.leaky_exact_resets_equal)
        self.assertTrue(self.result.recurrent_exact_resets_equal)
        self.assertTrue(
            all(item.natural_holdout_l1 > 0.0 for item in self.result.leaky_baselines)
        )
        self.assertTrue(
            all(
                item.exact_reset_holdout_l1 == 0.0
                for item in self.result.leaky_baselines
            )
        )
        self.assertTrue(
            all(
                item.natural_holdout_l1 > 0.0
                for item in self.result.recurrent_baselines
            )
        )
        self.assertTrue(
            all(
                item.exact_reset_holdout_l1 == 0.0
                for item in self.result.recurrent_baselines
            )
        )

    def test_fixed_edges_cannot_add_history(self) -> None:
        self.assertTrue(self.result.fixed_edge_holdouts_equal)

    def test_external_template_baseline_is_explicitly_separate(self) -> None:
        scores = {
            item.branch_id: item.minimum_transformed_l1
            for item in self.result.template_baselines
        }
        self.assertEqual(0.0, scores["history_a"])
        self.assertEqual(0.0, scores["history_permuted"])
        self.assertEqual(2.0, scores["history_b"])
        self.assertEqual(4.0, scores["history_zero"])
        self.assertTrue(self.result.template_separates_related_from_control)

    def test_spatial_channel_and_unequal_holdout_controls_close(self) -> None:
        self.assertTrue(self.result.reflection_equivariant)
        self.assertTrue(self.result.channel_permutation_equivariant)
        self.assertTrue(self.result.unequal_holdout_detected)

    def test_observer_order_and_repetition_are_neutral(self) -> None:
        observed = []
        with_observer = run_condensed_field_form_null_probe(
            observer=lambda item: observed.append(item.branch_id)
        )
        reversed_result = run_condensed_field_form_null_probe(
            branch_order=reversed(BRANCH_IDS)
        )
        self.assertEqual(list(BRANCH_IDS), observed)
        self.assertEqual(self.result.digest(), with_observer.digest())
        self.assertEqual(self.result.digest(), reversed_result.digest())
        self.assertTrue(with_observer.observer_is_neutral)
        self.assertTrue(reversed_result.order_is_neutral)
        self.assertTrue(self.result.repeated_run_is_neutral)

    def test_invalid_branch_orders_are_rejected(self) -> None:
        invalid_orders = (
            (),
            BRANCH_IDS[:-1],
            BRANCH_IDS + ("history_a",),
            ("history_a", "history_a", "history_b", "history_zero"),
            ("history_a", "history_b", "history_permuted", "unknown"),
        )
        for order in invalid_orders:
            with self.subTest(order=order):
                with self.assertRaises(CondensedFieldFormNullProbeError):
                    run_condensed_field_form_null_probe(branch_order=order)

    def test_result_retains_no_frames_and_releases_no_mechanic(self) -> None:
        self.assertFalse(self.result.retains_raw_frames)
        self.assertFalse(self.result.writes_back)
        self.assertFalse(self.result.releases_persistence)
        self.assertFalse(
            any(
                isinstance(value, np.ndarray)
                for branch in self.result.branches
                for value in asdict(branch).values()
            )
        )

    def test_public_roles_exclude_inner_storage_and_semantics(self) -> None:
        roles = set(condensed_field_form_null_probe_public_roles())
        forbidden = {
            "frame",
            "image",
            "pixels",
            "object",
            "chair",
            "label",
            "meaning",
            "class_id",
            "pattern_id",
            "memory",
            "weight",
            "edge",
            "learning_rate",
            "reward",
            "winner",
            "attention",
        }
        self.assertTrue(forbidden.isdisjoint(roles))


if __name__ == "__main__":
    unittest.main()
