from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism import (
    CONTINUOUS_WORLD_BASELINE_IDS,
    ContinuousTwoRelationWorldError,
    continuous_world_baseline_public_roles,
    run_continuous_world_baselines,
)


class ContinuousWorldBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_continuous_world_baselines()

    def test_all_preregistered_baselines_are_present(self) -> None:
        self.assertEqual(
            "d2039a9f515ad450e44b97493eb29b57c44d50ac10a2311b515ed9eabd154c37",
            self.result.digest(),
        )
        self.assertEqual(
            tuple(CONTINUOUS_WORLD_BASELINE_IDS),
            tuple(item.baseline_id for item in self.result.scores),
        )
        self.assertTrue(all(item.total == 768 for item in self.result.scores))

    def test_b0_reports_exact_fast_null_without_inventing_an_answer(self) -> None:
        b0 = self.result.score("b0")
        self.assertTrue(self.result.b0_fast_state_is_exact_null)
        self.assertEqual(0, b0.answered)
        self.assertEqual(0.0, b0.coverage)
        self.assertIsNone(b0.accuracy)

    def test_fixed_motion_baseline_separates_stationary_relations(self) -> None:
        b5 = self.result.score("b5")
        self.assertEqual(1.0, b5.control("k0").accuracy)
        self.assertEqual(0.0, b5.control("k1").accuracy)

    def test_latest_relation_baseline_needs_new_world_experience(self) -> None:
        b6 = self.result.score("b6")
        self.assertTrue(self.result.b6_solves_after_new_experience)
        self.assertEqual(0.0, b6.control("k2").accuracy)
        self.assertEqual(0.0, b6.control("k6").accuracy)
        self.assertEqual(0.8, b6.control("k3").accuracy)
        self.assertEqual(0.8, b6.control("k7").accuracy)

    def test_permanent_dual_storage_adds_no_power_to_same_fixed_reader(self) -> None:
        self.assertTrue(self.result.b6_and_b9_are_functionally_equal)
        b6 = self.result.score("b6")
        b9 = self.result.score("b9")
        self.assertEqual(
            (b6.total, b6.answered, b6.correct, b6.controls),
            (b9.total, b9.answered, b9.correct, b9.controls),
        )

    def test_event_count_and_exact_template_do_not_cover_the_world(self) -> None:
        self.assertTrue(self.result.b7_fails_shifted_switch_positions)
        self.assertTrue(self.result.exact_template_has_partial_coverage)
        b8 = self.result.score("b8")
        self.assertLess(b8.coverage, 1.0)
        self.assertGreater(b8.coverage, 0.0)

    def test_control_scores_preserve_answer_and_accuracy_separation(self) -> None:
        for score in self.result.scores:
            self.assertEqual(768, sum(item.total for item in score.controls))
            self.assertLessEqual(score.correct, score.answered)
            self.assertLessEqual(score.answered, score.total)

    def test_baselines_cannot_release_runtime_behavior(self) -> None:
        for role in ("writes_back", "adds_memory_role", "changes_field_transition"):
            with self.assertRaises(ContinuousTwoRelationWorldError):
                replace(self.result, **{role: True})

    def test_public_roles_contain_no_runtime_memory_or_semantics(self) -> None:
        forbidden = {
            "memory_state",
            "topology",
            "semantic_label",
            "reward",
            "field_write",
            "world_seed",
        }
        self.assertTrue(forbidden.isdisjoint(continuous_world_baseline_public_roles()))


if __name__ == "__main__":
    unittest.main()
