from __future__ import annotations

import unittest

from mcm_field_organism import (
    ReceptorNeuronDockMap,
    SharedFieldDock,
    TransientNeuronDockInput,
    TransientNeuronInputError,
    map_proposal_batch_to_transient_docks,
    project_transient_docks_to_neuron_inputs,
    run_receptor_proposal_handoff_audit,
    shared_mcm_field_public_roles,
    transient_neuron_input_public_roles,
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


def local_inputs(batch_index: int, *, fine: bool = True):
    comparison = run_receptor_proposal_handoff_audit()
    handoff = comparison.fine if fine else comparison.coarse
    trajectory = map_proposal_batch_to_transient_docks(
        handoff.batches[batch_index],
        docks(),
    )
    return trajectory, project_transient_docks_to_neuron_inputs(
        trajectory,
        docks(),
    )


class TransientNeuronInputTests(unittest.TestCase):
    def test_every_dock_value_reaches_only_its_mapped_neuron(self) -> None:
        trajectory, inputs = local_inputs(0, fine=False)

        self.assertEqual(trajectory.step_time, inputs.step_time)
        for dock in docks():
            neuron_id = dock.dock_map.neuron_ids[0]
            local = inputs.for_neuron(neuron_id)
            source = trajectory.frames_for_dock(dock.dock_id)
            self.assertEqual(dock.dock_id, local.dock_id)
            self.assertEqual(
                tuple(item.frame.values[0] for item in source),
                tuple(item.value for item in local.contacts),
            )
            self.assertEqual(
                tuple(item.frame.snapshot_id for item in source),
                tuple(item.snapshot_id for item in local.contacts),
            )

    def test_absent_modality_is_an_empty_local_input_not_zero_contact(self) -> None:
        _, inputs = local_inputs(1, fine=True)
        visual = inputs.for_neuron("field.visual.n0")

        self.assertEqual((), visual.contacts)
        self.assertFalse(hasattr(visual, "receptor_contact"))
        self.assertFalse(hasattr(visual, "held_value"))

    def test_dock_declaration_order_does_not_change_local_inputs(self) -> None:
        comparison = run_receptor_proposal_handoff_audit()
        batch = comparison.coarse.batches[0]
        trajectory = map_proposal_batch_to_transient_docks(batch, docks())
        self.assertEqual(
            project_transient_docks_to_neuron_inputs(trajectory, docks()),
            project_transient_docks_to_neuron_inputs(
                trajectory,
                tuple(reversed(docks())),
            ),
        )

    def test_mismatched_field_anatomy_is_rejected(self) -> None:
        trajectory, _ = local_inputs(0, fine=False)
        with self.assertRaisesRegex(TransientNeuronInputError, "anatomy"):
            project_transient_docks_to_neuron_inputs(trajectory, docks()[:1])

    def test_one_neuron_cannot_receive_competing_same_boundary_contacts(self) -> None:
        _, inputs = local_inputs(0, fine=False)
        auditory = inputs.for_neuron("field.auditory.n0")
        with self.assertRaisesRegex(
            TransientNeuronInputError,
            "unique ordered completions",
        ):
            TransientNeuronDockInput(
                auditory.neuron_id,
                auditory.dock_id,
                auditory.carrier_id,
                auditory.step_time,
                (auditory.contacts[0], auditory.contacts[0]),
            )

    def test_local_input_is_not_persisted_or_connected_to_field_state(self) -> None:
        _, inputs = local_inputs(0, fine=False)
        self.assertFalse(hasattr(inputs, "to_json"))
        self.assertFalse(hasattr(inputs, "canonical_payload"))
        self.assertTrue(
            {
                "transient_neuron_input",
                "neuron_inputs",
                "contacts",
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
                "reader",
                "selected_contact",
                "held_value",
            }.isdisjoint(transient_neuron_input_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
