from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from mcm_field_organism.mcm_f3_z1_evaluation import evaluate_mcm_f3_z1_packet
from mcm_field_organism.mcm_f3_z1_run import (
    execute_mcm_f3_z1_run,
    mcm_f3_z1_run_json_value,
)
from mcm_field_organism.mcm_f3_z1_runner import (
    MCMF3Z1ArmTrajectory,
    _execute_mcm_f3_z1_packet,
    prepare_mcm_f3_z1_execution,
)
from mcm_field_organism.mcm_f3_z1_trajectory import MCMF3Z1TrajectoryObserver


def fake_executor(plan, task):
    del plan
    observer = MCMF3Z1TrajectoryObserver(
        0,
        (0.0, 0.0),
        (0.0, 0.0),
        (0.5, 0.5),
    )
    observer(1, (0.5, 0.25), (0.125, 0.5), (0.45, 0.55))
    observer(2, (1.0, 0.5), (0.25, 1.0), (0.4, 0.6))
    return MCMF3Z1ArmTrajectory(
        task.model_id,
        task.arm_id,
        task.refinement,
        task.reproduction,
        observer.trajectory(),
        f"digest.{task.model_id}.{task.arm_id}.{task.refinement}",
        1,
        0.0,
        0.4,
        1.0,
        1.0,
    )


class MCMF3Z1RunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        plan = prepare_mcm_f3_z1_execution()
        cls.packet = _execute_mcm_f3_z1_packet(plan, fake_executor)

    def test_run_entry_applies_fixed_evaluation_without_real_matrix(self) -> None:
        with patch(
            "mcm_field_organism.mcm_f3_z1_run.execute_mcm_f3_z1_technical_packet",
            return_value=self.packet,
        ):
            result = execute_mcm_f3_z1_run()
        self.assertEqual("lauf-195", result.run_id)
        self.assertEqual(
            evaluate_mcm_f3_z1_packet(self.packet),
            result.evaluation,
        )

    def test_run_json_is_finite_and_contains_no_raw_trajectories(self) -> None:
        with patch(
            "mcm_field_organism.mcm_f3_z1_run.execute_mcm_f3_z1_technical_packet",
            return_value=self.packet,
        ):
            payload = mcm_f3_z1_run_json_value(execute_mcm_f3_z1_run())
        encoded = json.dumps(payload, allow_nan=False, sort_keys=True)
        self.assertEqual("mcm.f3.z1.run.v1", payload["schema_id"])
        self.assertNotIn('"trajectories"', encoded)
        self.assertIn('"run_id": "lauf-195"', encoded)


if __name__ == "__main__":
    unittest.main()
