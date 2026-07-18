from __future__ import annotations

import unittest

from mcm_field_organism import (
    CommonFieldTime,
    MCMFieldPerception,
    MCMFieldStepTime,
    MCMNeuron,
    MCMNeuronDrive,
    MCMNeuronLayer,
    MCMNeuronLayerError,
    MCMNeuronOutput,
    TransientLocalReceptorContact,
    TransientNeuronDockInput,
    advance_mcm_neuron,
    hold_state_baseline,
    receptor_projection_baseline,
)


def proposal_time(*, start_tick: int = 100, end_tick: int = 110) -> MCMFieldStepTime:
    return MCMFieldStepTime(
        clock_id="organism.test",
        start_tick=start_tick,
        end_tick=end_tick,
        ticks_per_second=100.0,
    )


def transient_inputs(
    step_time: MCMFieldStepTime,
) -> dict[str, TransientNeuronDockInput]:
    left_contact = TransientLocalReceptorContact(
        snapshot_id="audio.snapshot.1",
        source_clock_id="audio.sample",
        source_window_start_tick=0,
        source_window_end_tick=4,
        organism_read_time=CommonFieldTime(
            clock_id=step_time.clock_id,
            window_start_tick=step_time.start_tick + 1,
            window_end_tick=step_time.start_tick + 2,
        ),
        value=0.25,
    )
    return {
        "n.left": TransientNeuronDockInput(
            neuron_id="n.left",
            dock_id="dock.n.left",
            carrier_id="carrier.n.left",
            step_time=step_time,
            contacts=(left_contact,),
        ),
        "n.right": TransientNeuronDockInput(
            neuron_id="n.right",
            dock_id="dock.n.right",
            carrier_id="carrier.n.right",
            step_time=step_time,
            contacts=(),
        ),
    }


def neuron(
    neuron_id: str,
    position: tuple[int, ...],
    *,
    activation: float = 0.0,
    afterimage: float = 0.0,
    docked: bool = False,
) -> MCMNeuron:
    return MCMNeuron(
        neuron_id=neuron_id,
        field_id="auditory.local",
        modality_id="auditory",
        geometry_id="auditory.line.v1",
        position=position,
        activation=activation,
        afterimage=afterimage,
        perception=MCMFieldPerception(
            tick=0,
            receptor_contact=0.0 if docked else None,
            local_samples=(),
        ),
    )


def line_layer(*, reverse: bool = False) -> MCMNeuronLayer:
    neurons = (
        neuron("n.left", (0,), activation=0.2, docked=True),
        neuron("n.center", (1,), activation=0.4),
        neuron("n.right", (2,), activation=0.6, docked=True),
    )
    return MCMNeuronLayer(
        layer_id="auditory.layer",
        neurons=tuple(reversed(neurons)) if reverse else neurons,
        sample_offsets=((-1,), (1,)),
    )


class MCMNeuronLayerTests(unittest.TestCase):
    def test_single_neuron_advances_only_through_explicit_transition(self) -> None:
        previous = neuron("n.one", (0,), activation=0.3, afterimage=0.2, docked=True)
        perception = MCMFieldPerception(tick=1, receptor_contact=0.8, local_samples=())
        held = advance_mcm_neuron(previous, perception, hold_state_baseline)
        projected = advance_mcm_neuron(previous, perception, receptor_projection_baseline)
        self.assertEqual((0.3, 0.2), (held.activation, held.afterimage))
        self.assertEqual((0.8, 0.0), (projected.activation, projected.afterimage))

    def test_layer_builds_local_field_perception_from_prior_tick(self) -> None:
        observed: dict[str, MCMNeuronDrive] = {}

        def observer(drive: MCMNeuronDrive) -> MCMNeuronOutput:
            observed[drive.previous.neuron_id] = drive
            return MCMNeuronOutput(
                activation=drive.previous.activation,
                afterimage=drive.previous.afterimage,
            )

        next_layer = line_layer().advance({"n.left": 0.1, "n.right": 0.9}, observer)
        center = observed["n.center"]
        self.assertEqual(1, next_layer.tick)
        self.assertEqual(("n.left", "n.right"), tuple(
            item.sample_id.removeprefix("sample.")
            for item in center.perception.local_samples
        ))
        self.assertEqual((0.2, 0.6), tuple(
            item.activation for item in center.perception.local_samples
        ))
        self.assertTrue(all(item.source_tick == 0 for item in center.perception.local_samples))

    def test_receptor_contact_is_delivered_only_to_docked_neurons(self) -> None:
        observed: dict[str, float | None] = {}

        def observer(drive: MCMNeuronDrive) -> MCMNeuronOutput:
            observed[drive.previous.neuron_id] = drive.perception.receptor_contact
            return MCMNeuronOutput(0.0, 0.0)

        line_layer().advance({"n.left": 0.0, "n.right": 0.7}, observer)
        self.assertEqual({"n.center": None, "n.left": 0.0, "n.right": 0.7}, observed)

    def test_transient_input_is_visible_only_to_its_docked_neuron(self) -> None:
        observed: dict[str, TransientNeuronDockInput | None] = {}

        def observer(drive: MCMNeuronDrive) -> MCMNeuronOutput:
            observed[drive.previous.neuron_id] = drive.transient_receptor_input
            return MCMNeuronOutput(
                drive.previous.activation,
                drive.previous.afterimage,
            )

        step_time = proposal_time()
        inputs = transient_inputs(step_time)
        next_layer = line_layer().advance(
            {"n.left": 0.1, "n.right": 0.9},
            observer,
            step_time=step_time,
            transient_receptor_inputs=inputs,
        )

        self.assertIsNone(observed["n.center"])
        self.assertIs(inputs["n.left"], observed["n.left"])
        self.assertIs(inputs["n.right"], observed["n.right"])
        self.assertEqual((0.25,), tuple(
            item.value for item in observed["n.left"].contacts
        ))
        self.assertEqual((), observed["n.right"].contacts)
        self.assertTrue(all(
            not hasattr(item, "transient_receptor_input")
            for item in next_layer.neurons
        ))

    def test_ignored_transient_input_cannot_change_existing_transition(self) -> None:
        contacts = {"n.left": 0.1, "n.right": 0.9}
        step_time = proposal_time()
        without = line_layer().advance(
            contacts,
            hold_state_baseline,
            step_time=step_time,
        )
        with_inputs = line_layer().advance(
            contacts,
            hold_state_baseline,
            step_time=step_time,
            transient_receptor_inputs=transient_inputs(step_time),
        )
        self.assertEqual(without.digest(), with_inputs.digest())

    def test_transient_input_requires_atomic_dock_coverage_and_shared_time(self) -> None:
        step_time = proposal_time()
        inputs = transient_inputs(step_time)
        contacts = {"n.left": 0.1, "n.right": 0.9}

        with self.assertRaisesRegex(MCMNeuronLayerError, "atomically cover"):
            line_layer().advance(
                contacts,
                hold_state_baseline,
                step_time=step_time,
                transient_receptor_inputs={"n.left": inputs["n.left"]},
            )
        with self.assertRaisesRegex(MCMNeuronLayerError, "proposal step_time"):
            line_layer().advance(
                contacts,
                hold_state_baseline,
                transient_receptor_inputs=inputs,
            )

        other_time = proposal_time(start_tick=110, end_tick=120)
        wrong_time = dict(inputs)
        wrong_time["n.right"] = TransientNeuronDockInput(
            neuron_id="n.right",
            dock_id="dock.n.right",
            carrier_id="carrier.n.right",
            step_time=other_time,
            contacts=(),
        )
        with self.assertRaisesRegex(MCMNeuronLayerError, "share the proposal"):
            line_layer().advance(
                contacts,
                hold_state_baseline,
                step_time=step_time,
                transient_receptor_inputs=wrong_time,
            )

    def test_iteration_order_cannot_change_the_next_layer(self) -> None:
        def local_probe(drive: MCMNeuronDrive) -> MCMNeuronOutput:
            value = sum(item.activation for item in drive.perception.local_samples) / 2.0
            return MCMNeuronOutput(activation=value, afterimage=0.0)

        contacts = {"n.left": 0.0, "n.right": 0.0}
        first = line_layer().advance(contacts, local_probe)
        second = line_layer(reverse=True).advance(contacts, local_probe)
        self.assertEqual(first.digest(), second.digest())
        self.assertAlmostEqual(0.4, first.neuron("n.center").activation)

    def test_failed_proposal_leaves_previous_layer_unchanged(self) -> None:
        layer = line_layer()
        before = layer.digest()

        def invalid(drive: MCMNeuronDrive) -> MCMNeuronOutput:
            if drive.previous.neuron_id == "n.center":
                return MCMNeuronOutput(activation=2.0, afterimage=0.0)
            return MCMNeuronOutput(activation=0.0, afterimage=0.0)

        with self.assertRaises(MCMNeuronLayerError):
            layer.advance({"n.left": 0.0, "n.right": 0.0}, invalid)
        self.assertEqual(before, layer.digest())
        self.assertEqual(0, layer.tick)

    def test_geometry_must_be_local_unique_and_symmetric(self) -> None:
        base = (neuron("n.one", (0,)), neuron("n.two", (1,)))
        invalid_offsets = (
            ((1,),),
            ((0,),),
            ((-1,), (-1,), (1,)),
            ((-1, 0), (1, 0)),
        )
        for offsets in invalid_offsets:
            with self.subTest(offsets=offsets):
                with self.assertRaises(MCMNeuronLayerError):
                    MCMNeuronLayer("layer", base, offsets)

    def test_receptor_contact_set_must_match_static_docks(self) -> None:
        layer = line_layer()
        with self.assertRaises(MCMNeuronLayerError):
            layer.advance({"n.left": 0.0}, hold_state_baseline)
        with self.assertRaises(MCMNeuronLayerError):
            layer.advance(
                {"n.left": 0.0, "n.right": 0.0, "n.center": 0.0},
                hold_state_baseline,
            )

    def test_transition_cannot_return_an_undeclared_object(self) -> None:
        previous = neuron("n.one", (0,))
        perception = MCMFieldPerception(tick=1, receptor_contact=None, local_samples=())
        with self.assertRaises(MCMNeuronLayerError):
            advance_mcm_neuron(previous, perception, lambda drive: (0.0, 0.0))  # type: ignore[arg-type,return-value]


if __name__ == "__main__":
    unittest.main()
