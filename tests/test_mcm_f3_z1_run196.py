from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from mcm_field_organism.mcm_f3_z1_run196 import (
    execute_mcm_f3_z1_run196,
    mcm_f3_z1_run196_json_value,
)
from mcm_field_organism.mcm_f3_z1_runner import (
    MCMF3Z1ArmTrajectory,
    _execute_mcm_f3_z1_packet,
    prepare_mcm_f3_z1_execution,
)
from mcm_field_organism.mcm_f3_z1_trajectory import MCMF3Z1TrajectoryObserver


def full_support_fake_executor(plan, task):
    arm = plan.source.arm(task.arm_id)
    observer = MCMF3Z1TrajectoryObserver(
        arm.start_tick,
        (0.0, 0.0),
        (0.0, 0.0),
        (0.5, 0.5),
    )
    for step in arm.proposal_steps:
        phase = step.end_tick / arm.end_tick
        observer(
            step.end_tick,
            (phase, 0.5 * phase),
            (0.25 * phase, phase),
            (0.5 - 0.1 * phase, 0.5 + 0.1 * phase),
        )
    return MCMF3Z1ArmTrajectory(
        task.model_id,
        task.arm_id,
        task.refinement,
        task.reproduction,
        observer.trajectory(),
        f"digest.{task.model_id}.{task.arm_id}.{task.refinement}",
        len(arm.proposal_steps),
        0.0,
        0.4,
        1.0,
        1.0,
    )


class MCMF3Z1Run196Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        plan = prepare_mcm_f3_z1_execution()
        cls.full_packet = _execute_mcm_f3_z1_packet(
            plan,
            full_support_fake_executor,
        )

    def test_run196_applies_support_before_unchanged_evaluation(self) -> None:
        with patch(
            "mcm_field_organism.mcm_f3_z1_run196.execute_mcm_f3_z1_technical_packet",
            return_value=self.full_packet,
        ):
            result = execute_mcm_f3_z1_run196()
        self.assertEqual("lauf-196", result.run_id)
        self.assertTrue(all(value for _, value in result.support_controls))
        by_arm = {item.arm_id: item for item in result.support_measurements}
        self.assertEqual(183, by_arm["a.partitioned"].full_sample_count)
        self.assertEqual(92, by_arm["a.partitioned"].decision_sample_count)
        self.assertEqual(
            (
                "TECHNICAL_PARTITION_INVARIANT",
                "TIME_REPARAMETERIZATION_COVARIANT",
            ),
            result.evaluation.decision_ids,
        )

    def test_run196_json_contains_no_trajectory_payload(self) -> None:
        with patch(
            "mcm_field_organism.mcm_f3_z1_run196.execute_mcm_f3_z1_technical_packet",
            return_value=self.full_packet,
        ):
            payload = mcm_f3_z1_run196_json_value(execute_mcm_f3_z1_run196())
        encoded = json.dumps(payload, allow_nan=False, sort_keys=True)
        self.assertEqual("mcm.f3.z1.run196.v1", payload["schema_id"])
        self.assertNotIn('"trajectories"', encoded)
        self.assertIn('"run_id": "lauf-196"', encoded)


if __name__ == "__main__":
    unittest.main()
