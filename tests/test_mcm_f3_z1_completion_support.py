from __future__ import annotations

import unittest

from mcm_field_organism.asynchronous_receptor_events import (
    audit_asynchronous_receptor_events,
)
from mcm_field_organism.mcm_f3_z1_completion_support import (
    apply_mcm_f3_z1_completion_support,
    mcm_f3_z1_completion_ticks,
)
from mcm_field_organism.mcm_f3_z1_evaluation import evaluate_mcm_f3_z1_packet
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


class MCMF3Z1CompletionSupportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = prepare_mcm_f3_z1_execution()
        cls.full_packet = _execute_mcm_f3_z1_packet(
            cls.plan,
            full_support_fake_executor,
        )
        cls.audit = apply_mcm_f3_z1_completion_support(cls.full_packet)

    def test_completion_ticks_are_source_defined(self) -> None:
        for arm in self.plan.source.arms:
            event_audit = audit_asynchronous_receptor_events(arm.sequences)
            self.assertEqual(
                (arm.start_tick,)
                + tuple(item.completion_tick for item in event_audit.completion_groups),
                mcm_f3_z1_completion_ticks(arm.arm_id),
            )

    def test_partition_loses_only_empty_intermediate_support(self) -> None:
        by_arm = {item.arm_id: item for item in self.audit.arms}
        self.assertEqual(183, by_arm["a.partitioned"].full_sample_count)
        self.assertEqual(92, by_arm["a.partitioned"].decision_sample_count)
        self.assertFalse(by_arm["a.partitioned"].full_support_unchanged)

    def test_reference_and_partition_share_exact_decision_ticks(self) -> None:
        by_arm = {item.arm_id: item for item in self.audit.arms}
        self.assertEqual(
            by_arm["a.reference"].required_ticks,
            by_arm["a.partitioned"].required_ticks,
        )
        self.assertEqual(92, by_arm["a.reference"].decision_sample_count)
        self.assertEqual(92, by_arm["a.partitioned"].decision_sample_count)

    def test_other_arm_support_is_unchanged(self) -> None:
        self.assertTrue(
            all(
                item.full_support_unchanged
                for item in self.audit.arms
                if item.arm_id != "a.partitioned"
            )
        )

    def test_all_support_controls_pass(self) -> None:
        self.assertTrue(all(value for _, value in self.audit.controls))

    def test_unchanged_evaluation_accepts_corrected_synthetic_support(self) -> None:
        result = evaluate_mcm_f3_z1_packet(self.audit.packet)
        self.assertEqual(
            (
                "TECHNICAL_PARTITION_INVARIANT",
                "TIME_REPARAMETERIZATION_COVARIANT",
            ),
            result.decision_ids,
        )


if __name__ == "__main__":
    unittest.main()
