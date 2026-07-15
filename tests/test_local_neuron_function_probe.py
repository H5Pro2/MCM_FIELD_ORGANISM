from __future__ import annotations

import unittest

from mcm_field_organism import (
    MCMLocalFunctionObservation,
    MCMFieldPerception,
    MCMFieldSample,
    MCMNeuron,
    MCMNeuronDrive,
    MCMNeuronLayer,
    MCMNeuronOutput,
    observe_local_mcm_function,
)


def neuron(
    neuron_id: str,
    position: tuple[int, ...],
    activation: float,
    afterimage: float = 0.0,
) -> MCMNeuron:
    return MCMNeuron(
        neuron_id=neuron_id,
        field_id="field.local",
        modality_id="test",
        geometry_id="line.v1",
        position=position,
        activation=activation,
        afterimage=afterimage,
        perception=MCMFieldPerception(tick=0, receptor_contact=None, local_samples=()),
    )


def drive(
    own_activation: float,
    neighbor_activations: tuple[float, ...],
    *,
    receptor_contact: float | None = None,
    own_afterimage: float = 0.0,
    neighbor_afterimages: tuple[float, ...] | None = None,
) -> MCMNeuronDrive:
    afterimages = neighbor_afterimages or (0.0,) * len(neighbor_activations)
    samples = tuple(
        MCMFieldSample(
            sample_id=f"sample.n{index}",
            source_field_id="field.local",
            source_tick=0,
            relative_position=(index + 1,),
            activation=activation,
            afterimage=afterimage,
        )
        for index, (activation, afterimage) in enumerate(
            zip(neighbor_activations, afterimages, strict=True)
        )
    )
    return MCMNeuronDrive(
        previous=neuron("n.center", (0,), own_activation, own_afterimage),
        perception=MCMFieldPerception(
            tick=1,
            receptor_contact=receptor_contact,
            local_samples=samples,
        ),
    )


class LocalNeuronFunctionProbeTests(unittest.TestCase):
    def test_uniform_local_field_has_no_pair_difference(self) -> None:
        observed = observe_local_mcm_function(drive(0.4, (0.4, 0.4)))
        self.assertEqual(0.0, observed.activation_pair_sum)
        self.assertEqual(0.0, observed.activation_pair_mean)

    def test_receptor_contact_stays_separate_from_prior_field(self) -> None:
        quiet = observe_local_mcm_function(drive(0.2, (0.5,), receptor_contact=0.0))
        contact = observe_local_mcm_function(drive(0.2, (0.5,), receptor_contact=0.9))
        self.assertEqual(quiet.pair_differences, contact.pair_differences)
        self.assertEqual((0.0, 0.9), (quiet.receptor_contact, contact.receptor_contact))

    def test_polarity_inversion_reverses_every_local_difference(self) -> None:
        positive = observe_local_mcm_function(drive(0.2, (0.7, -0.1)))
        negative = observe_local_mcm_function(drive(-0.2, (-0.7, 0.1)))
        self.assertAlmostEqual(
            positive.activation_pair_sum,
            -negative.activation_pair_sum,
        )

    def test_afterimage_is_observed_as_a_distinct_state_role(self) -> None:
        observed = observe_local_mcm_function(
            drive(
                0.1,
                (0.1, 0.1),
                own_afterimage=0.2,
                neighbor_afterimages=(0.6, -0.2),
            )
        )
        self.assertEqual(0.0, observed.activation_pair_sum)
        self.assertAlmostEqual(0.0, observed.afterimage_pair_sum)
        self.assertNotEqual(
            tuple(item.afterimage_difference for item in observed.pair_differences),
            (0.0, 0.0),
        )

    def test_raw_pair_differences_conserve_a_closed_symmetric_layer(self) -> None:
        layer = MCMNeuronLayer(
            layer_id="line.layer",
            neurons=(
                neuron("n.left", (0,), -0.4),
                neuron("n.center", (1,), 0.1),
                neuron("n.right", (2,), 0.8),
            ),
            sample_offsets=((-1,), (1,)),
        )
        observations: list[MCMLocalFunctionObservation] = []

        def collect(item: MCMNeuronDrive) -> MCMNeuronOutput:
            observations.append(observe_local_mcm_function(item))
            return MCMNeuronOutput(item.previous.activation, item.previous.afterimage)

        layer.advance({}, collect)
        self.assertAlmostEqual(
            0.0,
            sum(item.activation_pair_sum for item in observations),
        )

    def test_neighbor_mean_is_not_conservative_at_a_boundary(self) -> None:
        layer = MCMNeuronLayer(
            layer_id="line.layer",
            neurons=(
                neuron("n.left", (0,), -0.4),
                neuron("n.center", (1,), 0.1),
                neuron("n.right", (2,), 0.8),
            ),
            sample_offsets=((-1,), (1,)),
        )
        observations: list[MCMLocalFunctionObservation] = []

        def collect(item: MCMNeuronDrive) -> MCMNeuronOutput:
            observations.append(observe_local_mcm_function(item))
            return MCMNeuronOutput(item.previous.activation, item.previous.afterimage)

        layer.advance({}, collect)
        self.assertNotAlmostEqual(
            0.0,
            sum(item.activation_pair_mean for item in observations),
        )


if __name__ == "__main__":
    unittest.main()
