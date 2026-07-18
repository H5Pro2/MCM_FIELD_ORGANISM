from __future__ import annotations

import unittest

from mcm_field_organism import (
    CommonFieldTime,
    MCMFieldStepTime,
    MCMNeuronDrive,
    MCMNeuronOutput,
    OrganismTimedReceptorFrame,
    PassiveDriveRole,
    PassiveFieldSegmentationError,
    ReceptorContactFrame,
    ReceptorDistribution,
    ReceptorDockAnatomy,
    ReceptorTimeSequence,
    adapt_passive_local_transition,
    all_passive_drive_roles,
    build_shared_mcm_field,
    compare_passive_field_role_ablations,
    compare_passive_field_segmentations,
    contact_free_boundary_distribution,
    fixed_leaky_local_afterimage_baseline,
    hold_state_baseline,
    passive_hold_state_baseline,
    passive_receptor_projection_baseline,
    passive_symmetric_local_reader_baseline,
    passive_field_segmentation_comparison_public_roles,
)


COMPLETION_TICKS = (2, 5, 8, 12)


def receptor_frame(index: int) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id="auditory",
        geometry_id="auditory.geometry.v1",
        snapshot_id=f"auditory.snapshot.{index}",
        clock_id="auditory.source",
        window_start_tick=index,
        window_end_tick=index + 1,
        carrier_ids=("auditory.carrier.0", "auditory.carrier.1"),
        values=(0.2 + 0.1 * index, -0.1 * index),
    )


def sequence() -> ReceptorTimeSequence:
    return ReceptorTimeSequence(
        modality_id="auditory",
        geometry_id="auditory.geometry.v1",
        clock_id="organism.test",
        frames=tuple(
            OrganismTimedReceptorFrame(
                receptor_frame(index),
                CommonFieldTime("organism.test", completion - 1, completion),
            )
            for index, completion in enumerate(COMPLETION_TICKS)
        ),
    )


def fresh_field():
    return build_shared_mcm_field(
        (receptor_frame(0),),
        {
            "auditory": ReceptorDockAnatomy(
                "auditory",
                "dock.auditory",
                ((0,), (1,)),
            )
        },
        sample_offsets=((-1,), (1,)),
    )


def coarse_steps() -> tuple[MCMFieldStepTime, ...]:
    return (MCMFieldStepTime("organism.test", 0, 12, 10.0),)


def fine_steps() -> tuple[MCMFieldStepTime, ...]:
    return tuple(
        MCMFieldStepTime("organism.test", start, start + 3, 10.0)
        for start in range(0, 12, 3)
    )


class PassiveFieldSegmentationComparisonTests(unittest.TestCase):
    def test_hold_baseline_is_reproducible_and_segmentation_invariant(self) -> None:
        result = compare_passive_field_segmentations(
            (sequence(),),
            coarse_steps(),
            fine_steps(),
            field_factory=fresh_field,
            transition_factory=lambda: hold_state_baseline,
            distribution_factory=contact_free_boundary_distribution,
        )

        self.assertTrue(result.coarse.every_event_assigned_once)
        self.assertTrue(result.fine.every_event_assigned_once)
        self.assertEqual(4, result.coarse.source_event_count)
        self.assertEqual(4, result.coarse.assigned_event_count)
        self.assertEqual(4, result.fine.assigned_event_count)
        self.assertEqual(1, len(result.coarse.steps))
        self.assertEqual(4, len(result.fine.steps))
        self.assertTrue(result.coarse_reproducible)
        self.assertTrue(result.fine_reproducible)
        self.assertTrue(result.endpoints_equal)
        self.assertEqual(1, result.coarse.steps[-1].technical_layer_tick)
        self.assertEqual(4, result.fine.steps[-1].technical_layer_tick)

    def test_every_drive_receives_only_local_history_and_no_scalar_contact(self) -> None:
        def transition(drive: MCMNeuronDrive) -> MCMNeuronOutput:
            self.assertIsNone(drive.perception.receptor_contact)
            self.assertIsNotNone(drive.transient_receptor_input)
            self.assertEqual(
                drive.previous.neuron_id,
                drive.transient_receptor_input.neuron_id,
            )
            return MCMNeuronOutput(
                drive.previous.activation,
                drive.previous.afterimage,
            )

        result = compare_passive_field_segmentations(
            (sequence(),),
            coarse_steps(),
            fine_steps(),
            field_factory=fresh_field,
            transition_factory=lambda: transition,
            distribution_factory=contact_free_boundary_distribution,
        )
        self.assertTrue(result.endpoints_equal)

    def test_segmentation_sensitive_fixture_is_detected_without_selection(self) -> None:
        def per_call_increment(drive: MCMNeuronDrive) -> MCMNeuronOutput:
            return MCMNeuronOutput(
                min(1.0, drive.previous.activation + 0.1),
                drive.previous.afterimage,
            )

        result = compare_passive_field_segmentations(
            (sequence(),),
            coarse_steps(),
            fine_steps(),
            field_factory=fresh_field,
            transition_factory=lambda: per_call_increment,
            distribution_factory=contact_free_boundary_distribution,
        )
        self.assertTrue(result.coarse_reproducible)
        self.assertTrue(result.fine_reproducible)
        self.assertFalse(result.endpoints_equal)

    def test_mismatched_horizons_are_rejected(self) -> None:
        with self.assertRaisesRegex(
            PassiveFieldSegmentationError,
            "same organism horizon",
        ):
            compare_passive_field_segmentations(
                (sequence(),),
                coarse_steps(),
                (MCMFieldStepTime("organism.test", 0, 9, 10.0),),
                field_factory=fresh_field,
                transition_factory=lambda: hold_state_baseline,
                distribution_factory=contact_free_boundary_distribution,
            )

    def test_wrong_boundary_time_is_rejected(self) -> None:
        def wrong_time(_batch) -> ReceptorDistribution:
            return ReceptorDistribution(
                CommonFieldTime("organism.test", 0, 1),
                (),
            )

        with self.assertRaisesRegex(
            PassiveFieldSegmentationError,
            "transient input time",
        ):
            compare_passive_field_segmentations(
                (sequence(),),
                coarse_steps(),
                fine_steps(),
                field_factory=fresh_field,
                transition_factory=lambda: hold_state_baseline,
                distribution_factory=wrong_time,
            )

    def test_used_initial_field_is_rejected(self) -> None:
        def used_field():
            return fresh_field().advance(
                ReceptorDistribution(
                    CommonFieldTime("organism.test", 0, 1),
                    (),
                ),
                hold_state_baseline,
            )

        with self.assertRaisesRegex(PassiveFieldSegmentationError, "fresh"):
            compare_passive_field_segmentations(
                (sequence(),),
                coarse_steps(),
                fine_steps(),
                field_factory=used_field,
                transition_factory=lambda: hold_state_baseline,
                distribution_factory=contact_free_boundary_distribution,
            )

    def test_public_result_roles_do_not_encode_a_field_candidate(self) -> None:
        roles = set(passive_field_segmentation_comparison_public_roles())
        forbidden = {
            "selected_contact",
            "latest_contact",
            "held_contact",
            "transition_equation",
            "default_transition",
            "meaning",
            "memory",
            "topology",
            "reward",
        }
        self.assertTrue(forbidden.isdisjoint(roles))

    def test_b0_to_b3_controls_connect_only_through_explicit_adapters(self) -> None:
        baselines = (
            passive_hold_state_baseline,
            passive_receptor_projection_baseline,
            passive_symmetric_local_reader_baseline,
            fixed_leaky_local_afterimage_baseline(1.0),
        )
        for baseline in baselines:
            with self.subTest(baseline=baseline):
                result = compare_passive_field_segmentations(
                    (sequence(),),
                    coarse_steps(),
                    fine_steps(),
                    field_factory=fresh_field,
                    transition_factory=lambda baseline=baseline: (
                        adapt_passive_local_transition(
                            baseline,
                            all_passive_drive_roles(),
                        )
                    ),
                    distribution_factory=contact_free_boundary_distribution,
                )
                self.assertTrue(result.coarse_reproducible)
                self.assertTrue(result.fine_reproducible)

    def test_role_ablation_runner_rebuilds_all_five_controls(self) -> None:
        def optional_local_sum(drive) -> MCMNeuronOutput:
            values = []
            if drive.previous_state is not None:
                values.append(drive.previous_state.activation)
            if drive.receptor_contact is not None:
                values.append(drive.receptor_contact)
            if drive.local_field_samples is not None:
                values.extend(
                    sample.activation
                    for sample in drive.local_field_samples
                )
            if drive.elapsed_seconds is not None:
                values.append(min(1.0, drive.elapsed_seconds / 10.0))
            if drive.transient_receptor_history is not None:
                values.extend(
                    contact.value
                    for contact in drive.transient_receptor_history
                )
            return MCMNeuronOutput(
                sum(values) / max(1, len(values)),
                0.0,
            )

        result = compare_passive_field_role_ablations(
            (sequence(),),
            coarse_steps(),
            fine_steps(),
            field_factory=fresh_field,
            passive_transition_factory=lambda: optional_local_sum,
            distribution_factory=contact_free_boundary_distribution,
        )
        self.assertEqual(
            set(PassiveDriveRole),
            {item.role for item in result.ablations},
        )
        self.assertEqual(5, len(result.ablations))
        self.assertTrue(result.reference.coarse_reproducible)
        self.assertTrue(result.reference.fine_reproducible)


if __name__ == "__main__":
    unittest.main()
