from __future__ import annotations

from statistics import fmean
import unittest

from mcm_field_organism import (
    CommonFieldTime,
    MCMFieldStepTime,
    MCMNeuronOutput,
    OrganismTimedReceptorFrame,
    PassiveCarrierReflection,
    PassiveFieldGeometryControlError,
    PassiveNeuronReflection,
    ReceptorContactFrame,
    ReceptorDockAnatomy,
    ReceptorTimeSequence,
    adapt_passive_local_transition,
    all_passive_drive_roles,
    build_shared_mcm_field,
    compare_passive_field_reflection,
    contact_free_boundary_distribution,
    passive_field_geometry_control_public_roles,
)


CARRIER_IDS = tuple(f"auditory.carrier.{index}" for index in range(3))


def frame(snapshot_id: str, values: tuple[float, ...]) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id="auditory",
        geometry_id="auditory.geometry.v1",
        snapshot_id=snapshot_id,
        clock_id="auditory.source",
        window_start_tick=0,
        window_end_tick=1,
        carrier_ids=CARRIER_IDS,
        values=values,
    )


def sequence(snapshot_id: str, values: tuple[float, ...]) -> ReceptorTimeSequence:
    return ReceptorTimeSequence(
        "auditory",
        "auditory.geometry.v1",
        "organism.test",
        (
            OrganismTimedReceptorFrame(
                frame(snapshot_id, values),
                CommonFieldTime("organism.test", 1, 2),
            ),
        ),
    )


def fresh_field():
    return build_shared_mcm_field(
        (frame("auditory.reference.0", (0.0, 0.0, 0.0)),),
        {
            "auditory": ReceptorDockAnatomy(
                "auditory",
                "dock.auditory",
                ((0,), (1,), (2,)),
            )
        },
        sample_offsets=((-1,), (1,)),
    )


def steps() -> tuple[
    tuple[MCMFieldStepTime, ...],
    tuple[MCMFieldStepTime, ...],
]:
    return (
        (
            MCMFieldStepTime("organism.test", 0, 3, 10.0),
            MCMFieldStepTime("organism.test", 3, 6, 10.0),
        ),
        (
            MCMFieldStepTime("organism.test", 0, 2, 10.0),
            MCMFieldStepTime("organism.test", 2, 3, 10.0),
            MCMFieldStepTime("organism.test", 3, 5, 10.0),
            MCMFieldStepTime("organism.test", 5, 6, 10.0),
        ),
    )


def carrier_reflections() -> tuple[PassiveCarrierReflection, ...]:
    return tuple(
        PassiveCarrierReflection(
            "auditory",
            CARRIER_IDS[index],
            CARRIER_IDS[2 - index],
        )
        for index in range(3)
    )


def neuron_reflections() -> tuple[PassiveNeuronReflection, ...]:
    return tuple(
        PassiveNeuronReflection(
            f"organism.mcm_field.auditory.n{index}",
            f"organism.mcm_field.auditory.n{2 - index}",
        )
        for index in range(3)
    )


def symmetric_transition(drive) -> MCMNeuronOutput:
    if drive.transient_receptor_history:
        activation = fmean(
            item.value for item in drive.transient_receptor_history
        )
    elif drive.local_field_samples:
        activation = fmean(
            item.activation for item in drive.local_field_samples
        )
    elif drive.previous_state is not None:
        activation = drive.previous_state.activation
    else:
        activation = 0.0
    return MCMNeuronOutput(activation, 0.0)


def oriented_transition(drive) -> MCMNeuronOutput:
    if drive.transient_receptor_history:
        activation = fmean(
            item.value for item in drive.transient_receptor_history
        )
    elif drive.local_field_samples:
        activation = sum(
            (1.0 if item.relative_position[0] > 0 else -1.0)
            * item.activation
            for item in drive.local_field_samples
        ) / len(drive.local_field_samples)
    elif drive.previous_state is not None:
        activation = drive.previous_state.activation
    else:
        activation = 0.0
    return MCMNeuronOutput(activation, 0.0)


def transition_factory(transition):
    return lambda: adapt_passive_local_transition(
        transition,
        all_passive_drive_roles(),
    )


class PassiveFieldGeometryControlTests(unittest.TestCase):
    def run_control(self, transition):
        coarse, fine = steps()
        return compare_passive_field_reflection(
            (sequence("auditory.reference.path", (0.2, 0.7, -0.4)),),
            (sequence("auditory.reflected.path", (-0.4, 0.7, 0.2)),),
            coarse,
            fine,
            reference_field_factory=fresh_field,
            reflected_field_factory=fresh_field,
            transition_factory=transition_factory(transition),
            distribution_factory=contact_free_boundary_distribution,
            carrier_reflections=carrier_reflections(),
            neuron_reflections=neuron_reflections(),
            reflection_axis=0,
        )

    def test_symmetric_local_fixture_is_reflection_equivariant(self) -> None:
        result = self.run_control(symmetric_transition)
        self.assertEqual(0, result.reflection_axis)
        self.assertEqual(2, result.reflection_coordinate_sum)
        self.assertTrue(result.coarse_traces_equivariant)
        self.assertTrue(result.fine_traces_equivariant)
        self.assertTrue(result.reference.coarse_reproducible)
        self.assertTrue(result.reflected.fine_reproducible)

    def test_oriented_fixture_exposes_a_hidden_preferred_direction(self) -> None:
        result = self.run_control(oriented_transition)
        self.assertFalse(result.coarse_traces_equivariant)
        self.assertFalse(result.fine_traces_equivariant)

    def test_non_bijective_carrier_reflection_is_rejected(self) -> None:
        invalid = (
            PassiveCarrierReflection(
                "auditory",
                CARRIER_IDS[0],
                CARRIER_IDS[2],
            ),
            PassiveCarrierReflection(
                "auditory",
                CARRIER_IDS[1],
                CARRIER_IDS[2],
            ),
            PassiveCarrierReflection(
                "auditory",
                CARRIER_IDS[2],
                CARRIER_IDS[0],
            ),
        )
        coarse, fine = steps()
        with self.assertRaisesRegex(
            PassiveFieldGeometryControlError,
            "bijective",
        ):
            compare_passive_field_reflection(
                (sequence("auditory.reference.path", (0.2, 0.7, -0.4)),),
                (sequence("auditory.reflected.path", (-0.4, 0.7, 0.2)),),
                coarse,
                fine,
                reference_field_factory=fresh_field,
                reflected_field_factory=fresh_field,
                transition_factory=transition_factory(symmetric_transition),
                distribution_factory=contact_free_boundary_distribution,
                carrier_reflections=invalid,
                neuron_reflections=neuron_reflections(),
                reflection_axis=0,
            )

    def test_identity_neuron_mapping_is_not_a_reflection(self) -> None:
        identity = tuple(
            PassiveNeuronReflection(
                f"organism.mcm_field.auditory.n{index}",
                f"organism.mcm_field.auditory.n{index}",
            )
            for index in range(3)
        )
        coarse, fine = steps()
        with self.assertRaisesRegex(
            PassiveFieldGeometryControlError,
            "non-identity reflection",
        ):
            compare_passive_field_reflection(
                (sequence("auditory.reference.path", (0.2, 0.7, -0.4)),),
                (sequence("auditory.reflected.path", (-0.4, 0.7, 0.2)),),
                coarse,
                fine,
                reference_field_factory=fresh_field,
                reflected_field_factory=fresh_field,
                transition_factory=transition_factory(symmetric_transition),
                distribution_factory=contact_free_boundary_distribution,
                carrier_reflections=carrier_reflections(),
                neuron_reflections=identity,
                reflection_axis=0,
            )

    def test_public_roles_contain_no_preferred_geometry(self) -> None:
        roles = set(passive_field_geometry_control_public_roles())
        forbidden = {
            "preferred_direction",
            "left_weight",
            "right_weight",
            "meaning",
            "memory",
            "reward",
            "target_shape",
        }
        self.assertTrue(forbidden.isdisjoint(roles))


if __name__ == "__main__":
    unittest.main()
