from __future__ import annotations

import unittest

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
    observer(
        1,
        (1.0, 0.5),
        (0.25, 1.0),
        (0.4, 0.6),
    )
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


class MCMF3Z1RunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = prepare_mcm_f3_z1_execution()

    def test_plan_contains_all_56_bound_tasks(self) -> None:
        self.assertEqual(56, len(self.plan.tasks))
        self.assertEqual(56, len({item.task_key for item in self.plan.tasks}))
        self.assertEqual(14, sum(item.reproduction for item in self.plan.tasks))

    def test_every_source_handoff_is_complete_without_field_advance(self) -> None:
        self.assertEqual(7, len(self.plan.handoff_controls))
        self.assertTrue(all(value for _, value in self.plan.handoff_controls))

    def test_every_task_starts_from_one_unmodified_base_layer(self) -> None:
        self.assertIsNone(self.plan.base_field.substrate)
        self.assertEqual(
            self.plan.base_layer_digest,
            self.plan.base_field.layer.digest(),
        )

    def test_packet_coordination_has_no_run_or_research_decision(self) -> None:
        packet = _execute_mcm_f3_z1_packet(self.plan, fake_executor)
        self.assertEqual(56, len(packet.trajectories))
        self.assertTrue(all(value for _, value in packet.controls))
        self.assertIsNone(packet.run_id)
        self.assertIsNone(packet.research_decision)


if __name__ == "__main__":
    unittest.main()
