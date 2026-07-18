from __future__ import annotations

import unittest

from mcm_field_organism import (
    CommonFieldTime,
    MCMFieldStepTime,
    MCMNeuronDrive,
    MCMNeuronOutput,
    OrganismTimedReceptorFrame,
    PassiveFieldSegmentationError,
    ReceptorContactFrame,
    ReceptorDistribution,
    ReceptorDockAnatomy,
    ReceptorTimeSequence,
    build_shared_mcm_field,
    compare_passive_field_segmentations,
    contact_free_boundary_distribution,
    hold_state_baseline,
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


if __name__ == "__main__":
    unittest.main()
