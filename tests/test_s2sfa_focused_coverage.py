from __future__ import annotations

import unittest

import numpy as np

from tools import _s2sfa_private_visual_method as sfa


def learning_segments() -> tuple[np.ndarray, np.ndarray]:
    return (
        np.asarray(((0.0, 0.0, 0.0, 7.0), (1.0, 0.0, 1.0, 7.0), (2.0, 0.0, 0.0, 7.0), (3.0, 0.0, 1.0, 7.0))),
        np.asarray(((0.0, 1.0, 0.0, 7.0), (1.0, 1.0, 1.0, 7.0), (2.0, 1.0, 0.0, 7.0), (3.0, 1.0, 1.0, 7.0))),
    )


class FocusedSFACoverageTests(unittest.TestCase):
    def test_sufficient_rank_with_ambiguous_slowest_direction_fails_closed(self) -> None:
        covariance = np.eye(2)
        projected_derivative = np.eye(2)
        self.assertEqual(np.linalg.matrix_rank(covariance), 2)
        with self.assertRaisesRegex(sfa.SFAError, "not unique") as failure:
            sfa._require_simple_slowest(projected_derivative, epsilon=sfa.EPSILON)
        self.assertEqual(failure.exception.code, "SFA_TRAINING_DEGENERATE")

    def test_freeze_blocks_future_learning_and_preserves_prior_projection(self) -> None:
        first, second = learning_segments()
        learner = sfa.LinearSFALearner()
        learner.observe(first)
        learner.observe(second)
        frozen = learner.freeze()
        digest = frozen.digest
        first_future = np.asarray(((8.0, -1.0, 2.0, 7.0), (9.0, -1.0, 3.0, 7.0)))
        second_future = np.asarray(((-8.0, 4.0, -2.0, 7.0), (-9.0, 4.0, -3.0, 7.0)))
        frozen.transform_feature(first_future)
        frozen.transform_raw(second_future)
        self.assertEqual(frozen.digest, digest)
        with self.assertRaisesRegex(sfa.SFAError, "forbidden after freeze") as failure:
            learner.observe(first_future)
        self.assertEqual(failure.exception.code, "SFA_LEARNER_FROZEN")


if __name__ == "__main__":
    unittest.main()
