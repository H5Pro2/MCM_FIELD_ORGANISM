from __future__ import annotations

from dataclasses import fields
import unittest

from mcm_field_organism import (
    ReceptorNeuronDockMap,
    SharedFieldDock,
    TransientDockTrajectory,
    TransientDockTrajectoryError,
    map_proposal_batch_to_transient_docks,
    run_receptor_proposal_handoff_audit,
    shared_mcm_field_public_roles,
    transient_dock_trajectory_public_roles,
)


def docks() -> tuple[SharedFieldDock, ...]:
    return (
        SharedFieldDock(
            "dock.auditory",
            ReceptorNeuronDockMap(
                "auditory",
                "auditory.geometry.v1",
                (("auditory.carrier.0", "field.auditory.n0"),),
            ),
        ),
        SharedFieldDock(
            "dock.visual",
            ReceptorNeuronDockMap(
                "visual",
                "visual.geometry.v1",
                (("visual.carrier.0", "field.visual.n0"),),
            ),
        ),
    )


class TransientDockTrajectoryTests(unittest.TestCase):
    def test_complete_batch_maps_losslessly_to_stable_docks(self) -> None:
        batch = run_receptor_proposal_handoff_audit().coarse.batches[0]
        trajectory = map_proposal_batch_to_transient_docks(batch, docks())

        self.assertEqual(batch.step_time, trajectory.step_time)
        self.assertEqual(batch.event_count, trajectory.event_count)
        self.assertEqual(
            tuple(
                item.frame
                for item in trajectory.frames_for_dock("dock.auditory")
            ),
            tuple(
                item.frame
                for group in batch.completion_groups
                for item in group.timed_frames
                if item.frame.modality_id == "auditory"
            ),
        )

    def test_dock_declaration_order_does_not_change_the_trajectory(self) -> None:
        batch = run_receptor_proposal_handoff_audit().fine.batches[1]
        self.assertEqual(
            map_proposal_batch_to_transient_docks(batch, docks()),
            map_proposal_batch_to_transient_docks(batch, tuple(reversed(docks()))),
        )

    def test_multiple_states_of_one_dock_remain_ordered_and_unreduced(self) -> None:
        batch = run_receptor_proposal_handoff_audit().coarse.batches[0]
        trajectory = map_proposal_batch_to_transient_docks(batch, docks())
        auditory = trajectory.frames_for_dock("dock.auditory")

        self.assertGreater(len(auditory), 1)
        self.assertEqual(
            tuple(sorted(item.field_time.window_end_tick for item in auditory)),
            tuple(item.field_time.window_end_tick for item in auditory),
        )
        self.assertEqual(
            len(auditory),
            len({item.frame.snapshot_id for item in auditory}),
        )

    def test_geometry_mismatch_and_unattached_modality_are_rejected(self) -> None:
        batch = run_receptor_proposal_handoff_audit().coarse.batches[0]
        wrong_geometry = (
            SharedFieldDock(
                "dock.auditory",
                ReceptorNeuronDockMap(
                    "auditory",
                    "auditory.other.v1",
                    (("auditory.carrier.0", "field.auditory.n0"),),
                ),
            ),
            docks()[1],
        )
        with self.assertRaisesRegex(TransientDockTrajectoryError, "rejected"):
            map_proposal_batch_to_transient_docks(batch, wrong_geometry)
        with self.assertRaisesRegex(
            TransientDockTrajectoryError,
            "unattached modality",
        ):
            map_proposal_batch_to_transient_docks(batch, docks()[:1])

    def test_contract_is_not_part_of_field_snapshot_or_neuron_perception(self) -> None:
        trajectory = map_proposal_batch_to_transient_docks(
            run_receptor_proposal_handoff_audit().coarse.batches[0],
            docks(),
        )
        self.assertIsInstance(trajectory, TransientDockTrajectory)
        self.assertFalse(hasattr(trajectory, "to_json"))
        self.assertFalse(hasattr(trajectory, "canonical_payload"))
        self.assertTrue(
            {
                "transient_dock_trajectory",
                "completion_groups",
                "dock_frames",
            }.isdisjoint(shared_mcm_field_public_roles())
        )
        self.assertTrue(
            {
                "activation",
                "afterimage",
                "weight",
                "meaning",
                "memory",
                "topology",
                "selected_frame",
                "mean_contact",
                "held_contact",
            }.isdisjoint(transient_dock_trajectory_public_roles())
        )
        self.assertTrue(
            {
                "step_time",
                "attached_dock_ids",
                "completion_groups",
                "dock_id",
                "timed_frame",
            }.issubset(
                {
                    item.name
                    for contract in (
                        type(trajectory),
                        type(trajectory.completion_groups[0]),
                        type(trajectory.completion_groups[0].dock_frames[0]),
                    )
                    for item in fields(contract)
                }
            )
        )


if __name__ == "__main__":
    unittest.main()
