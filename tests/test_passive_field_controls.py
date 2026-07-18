from __future__ import annotations

from dataclasses import fields
import math
import unittest

from mcm_field_organism import (
    CommonFieldTime,
    MCMFieldPerception,
    MCMFieldSample,
    MCMFieldStepTime,
    MCMNeuron,
    MCMNeuronDrive,
    MCMNeuronOutput,
    PassiveDriveRole,
    PassiveFieldControlError,
    TransientLocalReceptorContact,
    TransientNeuronDockInput,
    adapt_passive_local_transition,
    all_passive_drive_roles,
    fixed_leaky_local_afterimage_baseline,
    passive_drive_role_ablation,
    passive_field_controls_public_roles,
    passive_hold_state_baseline,
    passive_receptor_projection_baseline,
    passive_symmetric_local_reader_baseline,
    project_passive_local_drive,
)


def completed_drive() -> MCMNeuronDrive:
    step_time = MCMFieldStepTime("organism.test", 0, 10, 10.0)
    previous = MCMNeuron(
        neuron_id="neuron.a",
        field_id="field.test",
        modality_id="auditory",
        geometry_id="field.geometry.v1",
        position=(0,),
        activation=0.25,
        afterimage=0.1,
        perception=MCMFieldPerception(0, None, ()),
    )
    perception = MCMFieldPerception(
        tick=1,
        receptor_contact=0.5,
        local_samples=(
            MCMFieldSample(
                sample_id="sample.neuron.b",
                source_field_id="field.test",
                source_tick=0,
                relative_position=(1,),
                activation=-0.4,
                afterimage=0.2,
            ),
        ),
    )
    transient = TransientNeuronDockInput(
        neuron_id="neuron.a",
        dock_id="dock.auditory",
        carrier_id="auditory.carrier.0",
        step_time=step_time,
        contacts=(
            TransientLocalReceptorContact(
                snapshot_id="auditory.snapshot.0",
                source_clock_id="auditory.source",
                source_window_start_tick=0,
                source_window_end_tick=2,
                organism_read_time=CommonFieldTime(
                    "organism.test",
                    2,
                    4,
                ),
                value=0.75,
            ),
        ),
    )
    return MCMNeuronDrive(
        previous=previous,
        perception=perception,
        step_time=step_time,
        transient_receptor_input=transient,
    )


class PassiveFieldControlsTests(unittest.TestCase):
    def test_complete_projection_contains_only_the_five_local_roles(self) -> None:
        projected = project_passive_local_drive(
            completed_drive(),
            all_passive_drive_roles(),
        )

        self.assertEqual(0.25, projected.previous_state.activation)
        self.assertEqual(0.5, projected.receptor_contact)
        self.assertEqual(-0.4, projected.local_field_samples[0].activation)
        self.assertEqual(1.0, projected.elapsed_seconds)
        self.assertEqual(
            (0.2, 0.4, 0.75),
            (
                projected.transient_receptor_history[
                    0
                ].read_start_offset_seconds,
                projected.transient_receptor_history[
                    0
                ].completion_offset_seconds,
                projected.transient_receptor_history[0].value,
            ),
        )
        self.assertNotIn(
            "neuron_id",
            {item.name for item in fields(type(projected))},
        )
        self.assertNotIn(
            "modality_id",
            {item.name for item in fields(type(projected))},
        )

    def test_each_ablation_removes_exactly_one_local_role(self) -> None:
        attribute_by_role = {
            PassiveDriveRole.PREVIOUS_LOCAL_STATE: "previous_state",
            PassiveDriveRole.CURRENT_RECEPTOR_CONTACT: "receptor_contact",
            PassiveDriveRole.LOCAL_FIELD_SAMPLES: "local_field_samples",
            PassiveDriveRole.ELAPSED_DURATION: "elapsed_seconds",
            PassiveDriveRole.TRANSIENT_LOCAL_RECEPTOR_HISTORY: (
                "transient_receptor_history"
            ),
        }
        full = project_passive_local_drive(
            completed_drive(),
            all_passive_drive_roles(),
        )
        for role, attribute in attribute_by_role.items():
            with self.subTest(role=role.value):
                ablated = project_passive_local_drive(
                    completed_drive(),
                    passive_drive_role_ablation(role),
                )
                self.assertIsNone(getattr(ablated, attribute))
                for other_role, other_attribute in attribute_by_role.items():
                    if other_role is not role:
                        self.assertEqual(
                            getattr(full, other_attribute),
                            getattr(ablated, other_attribute),
                        )

    def test_adapter_does_not_install_or_mutate_the_runtime_drive(self) -> None:
        source = completed_drive()
        before = source.previous.digest()
        adapted = adapt_passive_local_transition(
            passive_hold_state_baseline,
            all_passive_drive_roles(),
        )
        self.assertEqual(MCMNeuronOutput(0.25, 0.1), adapted(source))
        self.assertEqual(before, source.previous.digest())

    def test_b0_to_b3_equations_are_fixed_and_explicit(self) -> None:
        drive = project_passive_local_drive(
            completed_drive(),
            all_passive_drive_roles(),
        )
        self.assertEqual(
            MCMNeuronOutput(0.25, 0.1),
            passive_hold_state_baseline(drive),
        )
        self.assertEqual(
            MCMNeuronOutput(0.5, 0.0),
            passive_receptor_projection_baseline(drive),
        )
        self.assertEqual(
            MCMNeuronOutput(-0.4, 0.0),
            passive_symmetric_local_reader_baseline(drive),
        )
        expected_afterimage = (
            math.exp(-1.0) * 0.1
            + (1.0 - math.exp(-1.0)) * -0.4
        )
        self.assertEqual(
            MCMNeuronOutput(-0.4, expected_afterimage),
            fixed_leaky_local_afterimage_baseline(1.0)(drive),
        )

    def test_baselines_fail_closed_when_a_required_role_is_removed(self) -> None:
        without_previous = project_passive_local_drive(
            completed_drive(),
            passive_drive_role_ablation(
                PassiveDriveRole.PREVIOUS_LOCAL_STATE
            ),
        )
        with self.assertRaisesRegex(
            PassiveFieldControlError,
            "previous_local_state",
        ):
            passive_hold_state_baseline(without_previous)

        without_local = project_passive_local_drive(
            completed_drive(),
            passive_drive_role_ablation(
                PassiveDriveRole.LOCAL_FIELD_SAMPLES
            ),
        )
        with self.assertRaisesRegex(
            PassiveFieldControlError,
            "local_field_samples",
        ):
            passive_symmetric_local_reader_baseline(without_local)

        without_duration = project_passive_local_drive(
            completed_drive(),
            passive_drive_role_ablation(
                PassiveDriveRole.ELAPSED_DURATION
            ),
        )
        with self.assertRaisesRegex(
            PassiveFieldControlError,
            "elapsed_duration",
        ):
            fixed_leaky_local_afterimage_baseline(1.0)(without_duration)

    def test_b3_requires_an_explicit_positive_time_constant(self) -> None:
        for value in (0.0, -1.0, math.inf, math.nan):
            with self.subTest(value=value), self.assertRaises(
                PassiveFieldControlError
            ):
                fixed_leaky_local_afterimage_baseline(value)

    def test_public_controls_contain_no_identity_or_development_roles(self) -> None:
        roles = set(passive_field_controls_public_roles())
        forbidden = {
            "neuron_id",
            "modality_id",
            "meaning",
            "memory",
            "topology",
            "reward",
            "learning_rate",
            "target",
        }
        self.assertTrue(forbidden.isdisjoint(roles))


if __name__ == "__main__":
    unittest.main()
