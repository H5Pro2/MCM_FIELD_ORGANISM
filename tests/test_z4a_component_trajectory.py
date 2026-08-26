from __future__ import annotations

from dataclasses import replace
import unittest

import numpy as np

from mcm_field_organism.field_step_time import MCMFieldStepTime
from mcm_field_organism.receptor_contract import CommonFieldTime, ReceptorContactFrame
from mcm_field_organism.receptor_proposal_handoff_audit import (
    handoff_receptor_completion_groups,
)
from mcm_field_organism.receptor_time_alignment import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)
from mcm_field_organism.z4a_component_trajectory import (
    Z4AComponentTrajectoryError,
    Z4ATrajectoryObserver,
    build_z4a_trajectory_support,
    z4a_completion_ticks_from_handoff,
    z4a_component_trajectory_public_roles,
)


def components(model_id: str, value: float = 0.0):
    common = (
        ("activation", (value, 0.5 * value)),
        ("afterimage", (0.25 * value, value)),
    )
    if model_id == "p0.exact":
        return common
    if model_id == "f3.candidate":
        return common + (("mcm_mass", (0.5, 0.5)),)
    return common + (("baseline_state", (0.5, 0.5)),)


def technical_trajectory(model_id: str, ticks=(0, 1, 2, 3, 4, 5, 6)):
    observer = Z4ATrajectoryObserver(model_id, ticks[0], components(model_id))
    for index, tick in enumerate(ticks[1:], start=1):
        observer(tick, components(model_id, index / 10.0))
    return observer.trajectory()


def sequence(completion_ticks=(1, 3, 5)):
    return ReceptorTimeSequence(
        "synthetic",
        "synthetic.geometry.v1",
        "z4a.synthetic",
        tuple(
            OrganismTimedReceptorFrame(
                ReceptorContactFrame(
                    "synthetic",
                    "synthetic.geometry.v1",
                    f"synthetic.{index}",
                    "synthetic.source",
                    index,
                    index + 1,
                    ("synthetic.carrier.0",),
                    (0.25,),
                ),
                CommonFieldTime("z4a.synthetic", tick - 1, tick),
            )
            for index, tick in enumerate(completion_ticks)
        ),
    )


def handoff():
    steps = tuple(
        MCMFieldStepTime("z4a.synthetic", start, end, 1.0)
        for start, end in ((0, 2), (2, 4), (4, 6))
    )
    return handoff_receptor_completion_groups((sequence(),), steps)


class Z4AComponentTrajectoryTests(unittest.TestCase):
    def test_each_model_has_only_its_bound_components(self) -> None:
        expected = {
            "p0.exact": ("activation", "afterimage"),
            "f3.candidate": ("activation", "afterimage", "mcm_mass"),
            "b3.linear-coupled": (
                "activation",
                "afterimage",
                "baseline_state",
            ),
        }
        for model_id, component_ids in expected.items():
            with self.subTest(model_id=model_id):
                trajectory = technical_trajectory(model_id)
                self.assertEqual(component_ids, trajectory.component_ids)
                self.assertEqual(2, trajectory.field_node_count)

    def test_observer_copies_arrays_and_rejects_geometry_change(self) -> None:
        activation = np.asarray([0.0, 0.0])
        observer = Z4ATrajectoryObserver(
            "p0.exact",
            0,
            (("activation", activation), ("afterimage", (0.0, 0.0))),
        )
        activation[:] = 9.0
        observer(1, components("p0.exact", 0.1))
        self.assertEqual(
            (0.0, 0.0),
            observer.trajectory().samples[0].values_for("activation"),
        )
        with self.assertRaises(Z4AComponentTrajectoryError):
            observer(
                2,
                (("activation", (0.0,)), ("afterimage", (0.0,))),
            )

    def test_component_substitution_and_reordering_are_rejected(self) -> None:
        with self.assertRaises(Z4AComponentTrajectoryError):
            Z4ATrajectoryObserver(
                "f3.candidate",
                0,
                components("b3.linear-coupled"),
            )
        with self.assertRaises(Z4AComponentTrajectoryError):
            Z4ATrajectoryObserver(
                "p0.exact",
                0,
                tuple(reversed(components("p0.exact"))),
            )

    def test_support_uses_handoff_completions_not_proposal_ends(self) -> None:
        current_handoff = handoff()
        support = build_z4a_trajectory_support(
            technical_trajectory("p0.exact"),
            current_handoff,
        )
        self.assertEqual((0, 1, 3, 5), support.required_ticks)
        self.assertEqual(
            support.required_ticks,
            tuple(item.tick for item in support.decision_trajectory.samples),
        )
        self.assertEqual(7, len(support.technical_trajectory.samples))
        self.assertEqual(4, len(support.decision_trajectory.samples))

    def test_same_handoff_supports_all_three_model_shapes(self) -> None:
        current_handoff = handoff()
        for model_id in ("p0.exact", "f3.candidate", "b3.linear-coupled"):
            with self.subTest(model_id=model_id):
                support = build_z4a_trajectory_support(
                    technical_trajectory(model_id),
                    current_handoff,
                )
                self.assertEqual((0, 1, 3, 5), support.required_ticks)

    def test_missing_tick_and_invalid_handoff_are_rejected(self) -> None:
        current_handoff = handoff()
        with self.assertRaises(Z4AComponentTrajectoryError):
            build_z4a_trajectory_support(
                technical_trajectory("p0.exact", (0, 1, 2, 4, 5, 6)),
                current_handoff,
            )
        with self.assertRaises(Z4AComponentTrajectoryError):
            z4a_completion_ticks_from_handoff(
                replace(
                    current_handoff,
                    every_in_horizon_event_assigned_once=False,
                )
            )
        with self.assertRaises(Z4AComponentTrajectoryError):
            z4a_completion_ticks_from_handoff(
                replace(current_handoff, assigned_event_count=2)
            )

    def test_public_contract_has_no_claim_or_raw_payload_role(self) -> None:
        forbidden = {
            "memory",
            "semantic",
            "meaning",
            "reward",
            "label",
            "raw_samples",
            "raw_frames",
            "research_decision",
            "run_id",
        }
        self.assertTrue(forbidden.isdisjoint(z4a_component_trajectory_public_roles()))


if __name__ == "__main__":
    unittest.main()
