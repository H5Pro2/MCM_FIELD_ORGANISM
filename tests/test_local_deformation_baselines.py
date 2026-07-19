from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism import (
    LOCAL_DEFORMATION_BASELINE_IDS,
    LocalDeformationWorldError,
    local_deformation_baseline_public_roles,
    run_local_deformation_baselines,
)


class LocalDeformationBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_local_deformation_baselines()

    def test_all_preregistered_baselines_are_present(self) -> None:
        self.assertEqual(
            "386543c684b05dcdafcb2663f45e65109f722c685436a8ff216a9170ab7f0bec",
            self.result.digest(),
        )
        self.assertEqual(
            tuple(LOCAL_DEFORMATION_BASELINE_IDS),
            tuple(item.baseline_id for item in self.result.scores),
        )
        self.assertTrue(all(item.total == 336 for item in self.result.scores))

    def test_piecewise_baseline_carries_identifiable_holdouts(self) -> None:
        self.assertTrue(self.result.l4_solves_all_identifiable_valid_holdouts)
        self.assertTrue(self.result.l4_requires_bracketing_contacts)
        l4 = self.result.score("l4")
        self.assertGreater(l4.coverage, 0.0)
        self.assertGreater(l4.correct, 0)

    def test_archive_does_not_add_power_to_the_same_fixed_reader(self) -> None:
        self.assertTrue(self.result.l9_archive_does_not_outperform_l4)
        self.assertEqual(
            self.result.score("l4").group("g5").correct,
            self.result.score("l9").group("g5").correct,
        )

    def test_pairing_and_old_history_controls_are_separated(self) -> None:
        self.assertTrue(self.result.d5_breaks_local_interpolation)
        self.assertTrue(self.result.old_history_is_irrelevant_after_d4)

    def test_scores_keep_coverage_and_accuracy_separate(self) -> None:
        for score in self.result.scores:
            self.assertEqual(336, sum(item.total for item in score.groups))
            self.assertLessEqual(score.correct, score.answered)
            self.assertLessEqual(score.answered, score.total)

    def test_baselines_cannot_release_runtime_behavior(self) -> None:
        for role in ("writes_back", "adds_memory_role", "changes_field_transition"):
            with self.assertRaises(LocalDeformationWorldError):
                replace(self.result, **{role: True})

    def test_public_roles_contain_no_runtime_memory_or_semantics(self) -> None:
        forbidden = {
            "memory_state",
            "topology",
            "semantic_label",
            "reward",
            "field_write",
            "form_id",
            "interpolation_weight",
        }
        self.assertTrue(forbidden.isdisjoint(local_deformation_baseline_public_roles()))


if __name__ == "__main__":
    unittest.main()
