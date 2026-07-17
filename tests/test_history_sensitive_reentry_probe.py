from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import unittest

from mcm_field_organism import (
    HistorySensitiveReentryProbeError,
    REENTRY_AMPLITUDES,
    REENTRY_PAIR_IDS,
    REENTRY_TAUS,
    REENTRY_TRAJECTORY_IDS,
    history_sensitive_reentry_public_roles,
    run_history_sensitive_reentry_probe,
)


class HistorySensitiveReentryProbeTests(unittest.TestCase):
    def test_all_preregistered_observations_and_pairs_are_present(self) -> None:
        result = run_history_sensitive_reentry_probe()
        self.assertEqual(36, len(result.observations))
        self.assertEqual(18, len(result.pairs))

    def test_world_controls_hold_for_every_parameter_pair(self) -> None:
        result = run_history_sensitive_reentry_probe()
        self.assertTrue(result.all_current_pairs_equal)
        self.assertTrue(result.all_prior_histories_distinct)
        self.assertTrue(result.all_trajectory_mirrors_exact)

    def test_b0_and_b2_collide_as_preregistered(self) -> None:
        result = run_history_sensitive_reentry_probe()
        self.assertTrue(result.b0_collides_all_pairs)
        self.assertTrue(result.b2_collides_all_pairs)
        self.assertTrue(all(pair.b0_distance == 0.0 for pair in result.pairs))
        self.assertTrue(all(pair.b2_distance == 0.0 for pair in result.pairs))

    def test_history_baselines_separate_every_matched_pair(self) -> None:
        result = run_history_sensitive_reentry_probe()
        self.assertTrue(result.b1_separates_all_pairs)
        self.assertTrue(result.b3_separates_all_pairs)
        self.assertTrue(result.b4_separates_all_pairs)
        self.assertTrue(result.b5_separates_all_pairs)

    def test_b1_closes_the_preregistered_function_without_release(self) -> None:
        result = run_history_sensitive_reentry_probe()
        self.assertTrue(result.b1_covers_required_pair_distinction)
        self.assertFalse(result.unexplained_function_rest)
        self.assertFalse(result.writes_back)
        self.assertFalse(result.mechanism_released)
        with self.assertRaises(HistorySensitiveReentryProbeError):
            replace(result, writes_back=True)
        with self.assertRaises(HistorySensitiveReentryProbeError):
            replace(result, mechanism_released=True)

    def test_exact_reset_is_neutral_for_every_baseline(self) -> None:
        self.assertTrue(run_history_sensitive_reentry_probe().all_resets_neutral)

    def test_order_and_observer_do_not_change_canonical_result(self) -> None:
        observed = []
        reference = run_history_sensitive_reentry_probe()
        permuted = run_history_sensitive_reentry_probe(
            amplitude_order=reversed(REENTRY_AMPLITUDES),
            tau_order=reversed(REENTRY_TAUS),
            trajectory_order=reversed(REENTRY_TRAJECTORY_IDS),
            pair_order=reversed(REENTRY_PAIR_IDS),
            observer=observed.append,
        )
        self.assertEqual(reference, permuted)
        self.assertEqual(reference.digest(), permuted.digest())
        self.assertEqual(36, len(observed))
        with self.assertRaises(FrozenInstanceError):
            observed[0].trajectory_id = "changed"  # type: ignore[misc]

    def test_invalid_orders_are_rejected(self) -> None:
        invalid_calls = (
            lambda: run_history_sensitive_reentry_probe(
                amplitude_order=(1.0,)
            ),
            lambda: run_history_sensitive_reentry_probe(
                tau_order=(1.0, 2.0, 2.0)
            ),
            lambda: run_history_sensitive_reentry_probe(
                trajectory_order=("a", "b", "c", "c")
            ),
            lambda: run_history_sensitive_reentry_probe(
                pair_order=("a-d", "a-d")
            ),
        )
        for call in invalid_calls:
            with self.assertRaises(HistorySensitiveReentryProbeError):
                call()

    def test_public_roles_contain_no_field_rule_or_semantics(self) -> None:
        role_groups = history_sensitive_reentry_public_roles()
        forbidden = {
            "raw_input",
            "world_frame",
            "gain",
            "threshold",
            "coupling",
            "weight",
            "learning_rate",
            "target",
            "reward",
            "semantic_label",
            "movement_class",
            "direction_command",
            "continuation_label",
            "return_label",
        }
        for roles in role_groups:
            self.assertTrue(forbidden.isdisjoint(roles))


if __name__ == "__main__":
    unittest.main()
