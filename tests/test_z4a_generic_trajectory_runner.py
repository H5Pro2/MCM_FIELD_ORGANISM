from __future__ import annotations

import hashlib
import unittest

from mcm_field_organism import (
    CommonFieldTime,
    MCMFieldStepTime,
    OrganismTimedReceptorFrame,
    ReceptorContactFrame,
    ReceptorDockAnatomy,
    ReceptorTimeSequence,
)
from mcm_field_organism.z4a_generic_trajectory_runner import (
    Z4AGenericTrajectoryRunnerError,
    build_z4a_world_arm_input,
    build_z4a_world_input,
    execute_z4a_technical_packet,
    prepare_z4a_execution,
    z4a_generic_trajectory_runner_public_roles,
)


_CLOCK_ID = "z4a.synthetic"


def sequence(values):
    return ReceptorTimeSequence(
        "synthetic",
        "synthetic.geometry.v1",
        _CLOCK_ID,
        tuple(
            OrganismTimedReceptorFrame(
                ReceptorContactFrame(
                    "synthetic",
                    "synthetic.geometry.v1",
                    f"synthetic.snapshot.{index}",
                    "synthetic.source",
                    index,
                    index + 1,
                    ("synthetic.carrier.0", "synthetic.carrier.1"),
                    (value, -0.5 * value),
                ),
                CommonFieldTime(_CLOCK_ID, tick - 1, tick),
            )
            for index, (tick, value) in enumerate(zip((2, 4, 6), values, strict=True))
        ),
    )


def steps(boundaries):
    return tuple(
        MCMFieldStepTime(_CLOCK_ID, start, end, 10.0)
        for start, end in zip(boundaries, boundaries[1:])
    )


def world(world_id="z4a.synthetic.unit.v1"):
    reference = (sequence((0.2, 0.4, 0.6)),)
    arms = (
        build_z4a_world_arm_input("reference", reference, steps((0, 2, 4, 6))),
        build_z4a_world_arm_input(
            "reproduction",
            (sequence((0.2, 0.4, 0.6)),),
            steps((0, 2, 4, 6)),
        ),
        build_z4a_world_arm_input(
            "partitioned",
            (sequence((0.2, 0.4, 0.6)),),
            steps((0, 1, 2, 3, 4, 5, 6)),
        ),
        build_z4a_world_arm_input(
            "reversed",
            (sequence((0.6, 0.4, 0.2)),),
            steps((0, 2, 4, 6)),
        ),
        build_z4a_world_arm_input(
            "permuted",
            (sequence((0.4, 0.2, 0.6)),),
            steps((0, 2, 4, 6)),
        ),
        build_z4a_world_arm_input(
            "independent",
            (sequence((-0.3, 0.1, 0.7)),),
            steps((0, 2, 4, 6)),
        ),
    )
    source_digest = hashlib.sha256(b"z4a.synthetic.source.v1").hexdigest()
    return build_z4a_world_input(
        world_id,
        (("z4a.synthetic.source.v1", source_digest),),
        ("synthetic",),
        _CLOCK_ID,
        10.0,
        0,
        6,
        (
            (
                "synthetic",
                ReceptorDockAnatomy(
                    "synthetic",
                    "dock.synthetic",
                    ((0,), (1,)),
                ),
            ),
        ),
        ((-1,), (1,)),
        arms,
    )


class Z4AGenericTrajectoryRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.world = world()
        cls.plan = prepare_z4a_execution(cls.world)
        cls.packet = execute_z4a_technical_packet(cls.world)

    def test_plan_has_exact_ordered_42_task_inventory(self) -> None:
        self.assertEqual(42, len(self.plan.tasks))
        self.assertEqual(
            (6, 18, 18),
            tuple(
                sum(task.model_id == model_id for task in self.plan.tasks)
                for model_id in (
                    "p0.exact",
                    "f3.candidate",
                    "b3.linear-coupled",
                )
            ),
        )
        self.assertEqual(
            ("p0.exact", "reference", None),
            self.plan.tasks[0].task_key,
        )
        self.assertEqual(
            ("b3.linear-coupled", "independent", 4),
            self.plan.tasks[-1].task_key,
        )

    def test_plan_builds_each_arm_handoff_once(self) -> None:
        self.assertEqual(6, len(self.plan.handoffs))
        self.assertEqual(6, len({id(item) for _, item in self.plan.handoffs}))
        for arm_id, handoff in self.plan.handoffs:
            self.assertIs(handoff, self.plan.handoff_for(arm_id))

    def test_packet_contains_42_technical_results_and_no_run_decision(self) -> None:
        self.assertEqual(42, len(self.packet.trajectories))
        self.assertIsNone(self.packet.research_decision)
        self.assertIsNone(self.packet.run_id)
        self.assertTrue(all(value for _, value in self.packet.controls))

    def test_model_roles_and_state_budgets_remain_separate(self) -> None:
        expected = {
            "p0.exact": (("activation", "afterimage"), 2),
            "f3.candidate": (("activation", "afterimage", "mcm_mass"), 3),
            "b3.linear-coupled": (
                ("activation", "afterimage", "baseline_state"),
                3,
            ),
        }
        for result in self.packet.trajectories:
            component_ids, multiplier = expected[result.model_id]
            self.assertEqual(
                component_ids,
                result.support.technical_trajectory.component_ids,
            )
            self.assertEqual(
                multiplier * result.support.technical_trajectory.field_node_count,
                result.dynamic_scalar_state_budget,
            )

    def test_partition_changes_only_full_technical_support(self) -> None:
        p0 = {
            result.arm_id: result
            for result in self.packet.trajectories
            if result.model_id == "p0.exact"
        }
        self.assertEqual(
            p0["reference"].support.required_ticks,
            p0["partitioned"].support.required_ticks,
        )
        self.assertEqual(4, len(p0["reference"].support.technical_trajectory.samples))
        self.assertEqual(7, len(p0["partitioned"].support.technical_trajectory.samples))
        self.assertEqual(4, len(p0["partitioned"].support.decision_trajectory.samples))

    def test_world_rejects_a_false_reproduction_binding(self) -> None:
        original = world()
        arms = list(original.arms)
        arms[1] = build_z4a_world_arm_input(
            "reproduction",
            (sequence((0.2, 0.4, 0.5)),),
            steps((0, 2, 4, 6)),
        )
        with self.assertRaisesRegex(
            Z4AGenericTrajectoryRunnerError,
            "reproduction digest",
        ):
            build_z4a_world_input(
                original.world_id,
                original.source_binding_digests,
                original.modality_ids,
                original.clock_id,
                original.ticks_per_second,
                original.horizon_start_tick,
                original.horizon_end_tick,
                original.dock_anatomies,
                original.field_sample_offsets,
                tuple(arms),
            )

    def test_public_contract_has_no_claim_raw_payload_or_run_role(self) -> None:
        forbidden = {
            "memory",
            "semantic",
            "meaning",
            "reward",
            "label",
            "raw_samples",
            "raw_frames",
        }
        self.assertTrue(
            forbidden.isdisjoint(z4a_generic_trajectory_runner_public_roles())
        )
        self.assertIn("research_decision", z4a_generic_trajectory_runner_public_roles())
        self.assertIn("run_id", z4a_generic_trajectory_runner_public_roles())


if __name__ == "__main__":
    unittest.main()
