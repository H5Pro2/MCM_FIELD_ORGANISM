from __future__ import annotations

import unittest

import numpy as np

from tools import _s2sfa_private_visual_method as sfa


def neutral_segments() -> tuple[np.ndarray, np.ndarray]:
    return (
        np.asarray(((0.0, 0.0, 0.0, 0.0, 7.0), (1.0, 0.0, 1.0, 0.0, 7.0), (2.0, 0.0, 0.0, 1.0, 7.0), (3.0, 0.0, 1.0, 1.0, 7.0))),
        np.asarray(((0.0, 1.0, 0.0, 0.0, 7.0), (1.0, 1.0, 1.0, 0.0, 7.0), (2.0, 1.0, 0.0, 1.0, 7.0), (3.0, 1.0, 1.0, 1.0, 7.0))),
    )


class PrivateVisualSFATests(unittest.TestCase):
    def test_binding_is_plan_only(self) -> None:
        self.assertEqual(sfa.PLANNED_CORPUS_BINDING["frame_count"], 32)
        self.assertEqual(sfa.PLANNED_CORPUS_BINDING["feature_count"], 1)
        self.assertEqual(len(sfa.PLANNED_CORPUS_DIGEST), 64)

    def test_fit_uses_only_within_segment_transitions_and_freezes(self) -> None:
        frozen = sfa.fit_linear_sfa(neutral_segments())
        source = neutral_segments()[0]
        before = frozen.digest
        features = frozen.transform_feature(source)
        raw = frozen.transform_raw(source)
        self.assertEqual(before, frozen.digest)
        self.assertEqual(features.shape, (4, 1))
        self.assertEqual(raw.shape, (4, 5))
        self.assertIn(4, frozen.constant_indices)

    def test_constant_and_rank_one_training_fail_closed(self) -> None:
        with self.assertRaisesRegex(sfa.SFAError, "positive variance") as constant:
            sfa.fit_linear_sfa((np.zeros((4, 4)),))
        self.assertEqual(constant.exception.code, "SFA_TRAINING_DEGENERATE")
        rank_one = np.asarray(((0.0, 0.0), (1.0, 1.0), (2.0, 2.0), (3.0, 3.0)))
        with self.assertRaisesRegex(sfa.SFAError, "rank is insufficient") as deficient:
            sfa.fit_linear_sfa((rank_one,))
        self.assertEqual(deficient.exception.code, "SFA_TRAINING_DEGENERATE")

    def test_repeated_covariance_eigenvalues_do_not_reject_unique_slowest_direction(self) -> None:
        covariance = np.diag((2.0, 2.0))
        derivative = np.diag((0.25, 0.75))
        root = np.linalg.cholesky(covariance)
        inverse_root = np.linalg.inv(root)
        projected = inverse_root @ derivative @ inverse_root.T
        slowest, vector = sfa._require_simple_slowest(projected, epsilon=sfa.EPSILON)
        direction = inverse_root.T @ vector
        residual = derivative @ direction - slowest * covariance @ direction
        self.assertLessEqual(float(np.max(np.abs(residual))), sfa.RESIDUAL_ATOL)
        self.assertAlmostEqual(float(direction @ covariance @ direction), 1.0, places=10)

    def test_rotated_whitening_basis_preserves_projected_solution(self) -> None:
        covariance = np.diag((4.0, 1.0))
        derivative = np.diag((0.5, 0.8))
        whitening = np.diag((0.5, 1.0))
        rotation = np.asarray(((0.0, -1.0), (1.0, 0.0)))
        first = whitening.T @ derivative @ whitening
        second = rotation @ first @ rotation.T
        first_value, first_vector = sfa._require_simple_slowest(first, epsilon=sfa.EPSILON)
        second_value, second_vector = sfa._require_simple_slowest(second, epsilon=sfa.EPSILON)
        first_direction = whitening @ first_vector
        second_direction = whitening @ rotation.T @ second_vector
        self.assertAlmostEqual(first_value, second_value, places=12)
        self.assertAlmostEqual(abs(float(first_direction @ covariance @ second_direction)), 1.0, places=12)

    def test_direct_residual_and_raw_coordinate_normalization_are_independent(self) -> None:
        frozen = sfa.fit_linear_sfa(neutral_segments())
        stacked = np.concatenate(neutral_segments())
        mean = np.asarray(frozen.mean)
        covariance = (stacked - mean).T @ (stacked - mean) / len(stacked)
        transitions = np.concatenate(tuple(np.diff(item, axis=0) for item in neutral_segments()))
        derivative = transitions.T @ transitions / len(transitions)
        direction = np.asarray(frozen.direction)
        residual = derivative @ direction - frozen.slowest_eigenvalue * covariance @ direction
        self.assertLessEqual(float(np.max(np.abs(residual))), frozen.config.residual_atol)
        raw = frozen.transform_raw(np.asarray(((7.0, 3.0, 5.0, 9.0, 3.0), (8.0, 3.0, 5.0, 9.0, 3.0))))
        self.assertNotEqual(float(raw[0, 4]), 0.0)

    def test_rank_tie_and_gain_loss_confusion_remain_separate(self) -> None:
        reference_a = np.asarray(((0.0,), (0.0,)))
        reference_b = np.asarray(((2.0,), (2.0,)))
        tie = sfa.rank_two_references(np.asarray(((1.0,), (1.0,))), reference_a, reference_b, expected_reference="A")
        correct = sfa.rank_two_references(reference_a, reference_a, reference_b, expected_reference="A")
        wrong = sfa.rank_two_references(reference_b, reference_a, reference_b, expected_reference="A")
        self.assertEqual(tie.status, "ABSTAIN_TIE")
        self.assertEqual(correct.status, "CORRECT")
        self.assertEqual(wrong.status, "CONFUSION")
        summary = sfa.summarize_comparison((("gain", tie, correct), ("loss", correct, tie), ("confusion", correct, wrong)))
        self.assertEqual(summary.additional_correct, ("gain",))
        self.assertEqual(summary.losses, ("loss", "confusion"))
        self.assertEqual(summary.confusions, ("confusion",))
        self.assertEqual(summary.abstentions, ("loss",))


if __name__ == "__main__":
    unittest.main()
