from __future__ import annotations

import unittest

import numpy as np

from tools import _s2sfa_private_visual_run as run


def neutral_observations() -> dict[str, tuple[float, ...]]:
    values = {}
    for spec in run.PLAN:
        step = (spec.ordinal - 1) % 4
        family = 1.0 if spec.episode in {"L2", "RB", "QB"} else 0.0
        vector = np.zeros(288, dtype=np.float64)
        vector[0] = float(step)
        vector[1] = family
        vector[2] = float(step % 2)
        values[spec.frame_id] = tuple(vector)
    return values


class SFAVisualRunConnectionTests(unittest.TestCase):
    def test_success_verification_and_evaluation_without_frames(self) -> None:
        record = run.run_materialized_once(run_id="neutral-sfa-run", plan_digest=run.PLAN_DIGEST, observations=neutral_observations(), authorized=True)
        verification = run.verify_read_only(record)
        evaluation = run.evaluate_verified(record, verification)
        self.assertEqual(record["status"], "RECORDING_COMPLETE")
        self.assertTrue(verification["evaluation_allowed"])
        self.assertIn("additional_correct", evaluation)

    def test_binding_failure_and_degenerate_failure_block_evaluation(self) -> None:
        with self.assertRaisesRegex(run.SFAVisualRunError, "binding"):
            run.run_materialized_once(run_id="bad", plan_digest="0" * 64, observations=neutral_observations(), authorized=True)
        zeros = {key: tuple(np.zeros(288)) for key in neutral_observations()}
        record = run.run_materialized_once(run_id="degenerate", plan_digest=run.PLAN_DIGEST, observations=zeros, authorized=True)
        verification = run.verify_read_only(record)
        self.assertEqual(record["status"], "INCOMPLETE")
        self.assertEqual(record["error"]["code"], "SFA_TRAINING_DEGENERATE")
        self.assertFalse(verification["evaluation_allowed"])
        with self.assertRaisesRegex(run.SFAVisualRunError, "requires successful verification"):
            run.evaluate_verified(record, verification)


if __name__ == "__main__":
    unittest.main()
