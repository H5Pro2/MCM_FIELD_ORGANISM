from __future__ import annotations

from dataclasses import replace
import json
import unittest

from mcm_field_organism.mcm_f3_z1_evaluation import (
    evaluate_mcm_f3_z1_packet,
    mcm_f3_z1_evaluation_json_value,
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


def partition_changed_executor(plan, task):
    item = fake_executor(plan, task)
    if task.arm_id != "a.partitioned":
        return item
    observer = MCMF3Z1TrajectoryObserver(
        0,
        (0.0, 0.0),
        (0.0, 0.0),
        (0.5, 0.5),
    )
    observer(1, (1.0, 0.5), (0.25, 1.0), (0.4, 0.6))
    observer(2, (2.0, 1.0), (0.5, 2.0), (0.3, 0.7))
    return replace(item, trajectory=observer.trajectory())


class MCMF3Z1EvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        plan = prepare_mcm_f3_z1_execution()
        cls.packet = _execute_mcm_f3_z1_packet(plan, fake_executor)

    def test_identical_synthetic_paths_are_covariant_and_baseline_explained(self) -> None:
        result = evaluate_mcm_f3_z1_packet(self.packet)
        self.assertEqual(
            (
                "TECHNICAL_PARTITION_INVARIANT",
                "TIME_REPARAMETERIZATION_COVARIANT",
            ),
            result.decision_ids,
        )
        self.assertTrue(result.baseline_explains_f3)
        self.assertIsNone(result.evaluation_error)

    def test_failed_packet_control_stops_scientific_classification(self) -> None:
        controls = tuple(
            (name, False if name == "reproductions_exact" else value)
            for name, value in self.packet.controls
        )
        result = evaluate_mcm_f3_z1_packet(replace(self.packet, controls=controls))
        self.assertEqual(("TECHNICALLY_UNDECIDABLE",), result.decision_ids)
        self.assertFalse(result.baseline_explains_f3)
        self.assertIn("reproductions_exact", result.evaluation_error or "")

    def test_partition_difference_makes_each_model_undecidable(self) -> None:
        plan = prepare_mcm_f3_z1_execution()
        packet = _execute_mcm_f3_z1_packet(plan, partition_changed_executor)
        result = evaluate_mcm_f3_z1_packet(packet)
        self.assertEqual(("TECHNICALLY_UNDECIDABLE",), result.decision_ids)
        self.assertTrue(
            all(
                model.classification_ids == ("TECHNICALLY_UNDECIDABLE",)
                for model in result.model_evaluations
            )
        )
        self.assertFalse(result.baseline_explains_f3)

    def test_json_projection_contains_no_raw_trajectories(self) -> None:
        result = evaluate_mcm_f3_z1_packet(self.packet)
        payload = mcm_f3_z1_evaluation_json_value(result)
        encoded = json.dumps(payload, allow_nan=False, sort_keys=True)
        self.assertEqual("mcm.f3.z1.evaluation.v1", payload["schema_id"])
        self.assertNotIn('"trajectories"', encoded)
        self.assertIn('"raw_trajectories_retained": false', encoded)


if __name__ == "__main__":
    unittest.main()
