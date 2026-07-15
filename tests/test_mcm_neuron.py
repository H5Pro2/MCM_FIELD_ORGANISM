from __future__ import annotations

from dataclasses import FrozenInstanceError
import unittest

from mcm_field_organism import (
    MCMFieldPerception,
    MCMFieldSample,
    MCMNeuron,
    MCMNeuronValidationError,
    mcm_neuron_public_roles,
)


def sample(
    sample_id: str,
    relative_position: tuple[int, int],
    *,
    source_tick: int = 3,
) -> MCMFieldSample:
    return MCMFieldSample(
        sample_id=sample_id,
        source_field_id="auditory.local",
        source_tick=source_tick,
        relative_position=relative_position,
        activation=0.4,
        afterimage=0.2,
    )


class MCMNeuronTests(unittest.TestCase):
    def test_neuron_keeps_world_contact_and_prior_field_perception_separate(self) -> None:
        perception = MCMFieldPerception(
            tick=4,
            receptor_contact=0.7,
            local_samples=(sample("right", (1, 0)), sample("left", (-1, 0))),
        )
        neuron = MCMNeuron(
            neuron_id="auditory.n12",
            field_id="auditory.local",
            modality_id="auditory",
            geometry_id="auditory.grid.v1",
            position=(4, 2),
            activation=0.6,
            afterimage=0.3,
            perception=perception,
        )
        self.assertEqual(4, neuron.tick)
        self.assertEqual(0.7, neuron.perception.receptor_contact)
        self.assertEqual(("left", "right"), tuple(item.sample_id for item in neuron.perception.local_samples))

    def test_no_receptor_dock_is_distinct_from_exact_zero_contact(self) -> None:
        undocked = MCMFieldPerception(tick=0, receptor_contact=None, local_samples=())
        zero_contact = MCMFieldPerception(tick=0, receptor_contact=0.0, local_samples=())
        self.assertFalse(undocked.has_receptor_dock)
        self.assertTrue(zero_contact.has_receptor_dock)

    def test_same_tick_field_feedback_is_rejected(self) -> None:
        with self.assertRaises(MCMNeuronValidationError):
            MCMFieldPerception(
                tick=4,
                receptor_contact=None,
                local_samples=(sample("same_tick", (1, 0), source_tick=4),),
            )

    def test_samples_are_not_connections_or_weights(self) -> None:
        forbidden = {
            "connections",
            "edges",
            "weight",
            "threshold",
            "learning_rate",
            "meaning",
            "label",
            "reward",
            "resource",
        }
        self.assertTrue(forbidden.isdisjoint(mcm_neuron_public_roles()))
        self.assertTrue(forbidden.isdisjoint(MCMFieldSample.__dataclass_fields__))
        self.assertTrue(forbidden.isdisjoint(MCMFieldPerception.__dataclass_fields__))

    def test_geometry_dimension_mismatch_is_rejected(self) -> None:
        perception = MCMFieldPerception(
            tick=4,
            receptor_contact=None,
            local_samples=(sample("three_dimensional", (1, 0, 0)),),
        )
        with self.assertRaises(MCMNeuronValidationError):
            MCMNeuron(
                neuron_id="auditory.n12",
                field_id="auditory.local",
                modality_id="auditory",
                geometry_id="auditory.grid.v1",
                position=(4, 2),
                activation=0.0,
                afterimage=0.0,
                perception=perception,
            )

    def test_snapshot_is_immutable_and_digest_is_reproducible(self) -> None:
        perception = MCMFieldPerception(
            tick=4,
            receptor_contact=0.1,
            local_samples=(sample("left", (-1, 0)),),
        )
        neuron = MCMNeuron(
            neuron_id="auditory.n12",
            field_id="auditory.local",
            modality_id="auditory",
            geometry_id="auditory.grid.v1",
            position=(4, 2),
            activation=0.2,
            afterimage=0.1,
            perception=perception,
        )
        self.assertEqual(neuron.digest(), neuron.digest())
        with self.assertRaises(FrozenInstanceError):
            neuron.activation = 0.9  # type: ignore[misc]

    def test_invalid_identity_position_and_values_are_rejected(self) -> None:
        with self.assertRaises(MCMNeuronValidationError):
            sample("invalid sample", (1, 0))
        with self.assertRaises(MCMNeuronValidationError):
            sample("self", (0, 0))
        with self.assertRaises(MCMNeuronValidationError):
            MCMFieldSample("high", "field", 0, (1,), 1.1, 0.0)
        with self.assertRaises(MCMNeuronValidationError):
            MCMFieldPerception(tick=1, receptor_contact=None, local_samples=(object(),))  # type: ignore[arg-type]

    def test_duplicate_sample_identity_is_rejected(self) -> None:
        with self.assertRaises(MCMNeuronValidationError):
            MCMFieldPerception(
                tick=4,
                receptor_contact=None,
                local_samples=(sample("same", (-1, 0)), sample("same", (1, 0))),
            )


if __name__ == "__main__":
    unittest.main()
