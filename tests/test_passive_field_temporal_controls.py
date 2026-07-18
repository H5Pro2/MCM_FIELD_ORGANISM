from __future__ import annotations

import unittest

from mcm_field_organism import (
    CommonFieldTime,
    MCMFieldStepTime,
    MCMNeuronOutput,
    OrganismTimedReceptorFrame,
    PassiveFieldTemporalControlError,
    ReceptorContactFrame,
    ReceptorDockAnatomy,
    ReceptorTimeSequence,
    adapt_passive_local_transition,
    all_passive_drive_roles,
    build_shared_mcm_field,
    compare_passive_future_event_causality,
    compare_passive_receptor_rate,
    compare_passive_simultaneous_order,
    contact_free_boundary_distribution,
    hold_state_baseline,
    passive_field_temporal_controls_public_roles,
)


def frame(
    snapshot_id: str,
    source_start: int,
    value: float,
) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id="auditory",
        geometry_id="auditory.geometry.v1",
        snapshot_id=snapshot_id,
        clock_id="auditory.source",
        window_start_tick=source_start,
        window_end_tick=source_start + 1,
        carrier_ids=("auditory.carrier.0",),
        values=(value,),
    )


def timed(
    receptor_frame: ReceptorContactFrame,
    start_tick: int,
    end_tick: int,
) -> OrganismTimedReceptorFrame:
    return OrganismTimedReceptorFrame(
        receptor_frame,
        CommonFieldTime("organism.test", start_tick, end_tick),
    )


def sequence(
    frames: tuple[OrganismTimedReceptorFrame, ...],
) -> ReceptorTimeSequence:
    return ReceptorTimeSequence(
        "auditory",
        "auditory.geometry.v1",
        "organism.test",
        frames,
    )


def fresh_field():
    return build_shared_mcm_field(
        (frame("auditory.reference.0", 0, 0.0),),
        {
            "auditory": ReceptorDockAnatomy(
                "auditory",
                "dock.auditory",
                ((0,),),
            )
        },
        sample_offsets=((-1,), (1,)),
    )


def modality_frame(
    modality_id: str,
    snapshot_id: str,
    source_start: int,
    value: float,
) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id=modality_id,
        geometry_id=f"{modality_id}.geometry.v1",
        snapshot_id=snapshot_id,
        clock_id=f"{modality_id}.source",
        window_start_tick=source_start,
        window_end_tick=source_start + 1,
        carrier_ids=(f"{modality_id}.carrier.0",),
        values=(value,),
    )


def multimodal_field():
    auditory = modality_frame(
        "auditory",
        "auditory.reference.0",
        0,
        0.0,
    )
    visual = modality_frame(
        "visual",
        "visual.reference.0",
        0,
        0.0,
    )
    return build_shared_mcm_field(
        (auditory, visual),
        {
            "auditory": ReceptorDockAnatomy(
                "auditory",
                "dock.auditory",
                ((0,),),
            ),
            "visual": ReceptorDockAnatomy(
                "visual",
                "dock.visual",
                ((1,),),
            ),
        },
        sample_offsets=((-1,), (1,)),
    )


def rate_steps() -> tuple[
    tuple[MCMFieldStepTime, ...],
    tuple[MCMFieldStepTime, ...],
]:
    return (
        (MCMFieldStepTime("organism.test", 0, 12, 10.0),),
        (
            MCMFieldStepTime("organism.test", 0, 6, 10.0),
            MCMFieldStepTime("organism.test", 6, 12, 10.0),
        ),
    )


def causality_steps() -> tuple[
    tuple[MCMFieldStepTime, ...],
    tuple[MCMFieldStepTime, ...],
]:
    return (
        (
            MCMFieldStepTime("organism.test", 0, 6, 10.0),
            MCMFieldStepTime("organism.test", 6, 12, 10.0),
        ),
        tuple(
            MCMFieldStepTime("organism.test", start, start + 3, 10.0)
            for start in range(0, 12, 3)
        ),
    )


def event_count_transition(drive) -> MCMNeuronOutput:
    previous = (
        0.0
        if drive.previous_state is None
        else drive.previous_state.activation
    )
    count = (
        0
        if drive.transient_receptor_history is None
        else len(drive.transient_receptor_history)
    )
    return MCMNeuronOutput(min(1.0, previous + 0.1 * count), 0.0)


def event_count_transition_factory():
    return adapt_passive_local_transition(
        event_count_transition,
        all_passive_drive_roles(),
    )


class PassiveFieldTemporalControlsTests(unittest.TestCase):
    def setUp(self) -> None:
        source_a = frame("auditory.source.a", 0, 0.2)
        source_b = frame("auditory.source.b", 1, 0.6)
        self.reference = sequence(
            (
                timed(source_a, 2, 3),
                timed(source_b, 8, 9),
            )
        )
        self.repeated = sequence(
            (
                timed(frame("auditory.repeat.a0", 0, 0.2), 1, 2),
                timed(frame("auditory.repeat.a1", 0, 0.2), 3, 4),
                timed(frame("auditory.repeat.b0", 1, 0.6), 7, 8),
                timed(frame("auditory.repeat.b1", 1, 0.6), 9, 10),
            )
        )

    def test_hold_control_is_neutral_to_extra_technical_completions(self) -> None:
        coarse, fine = rate_steps()
        result = compare_passive_receptor_rate(
            (self.reference,),
            (self.repeated,),
            coarse,
            fine,
            field_factory=fresh_field,
            transition_factory=lambda: hold_state_baseline,
            distribution_factory=contact_free_boundary_distribution,
        )
        self.assertEqual(2, result.reference_event_count)
        self.assertEqual(4, result.repeated_event_count)
        self.assertTrue(result.coarse_endpoints_equal)
        self.assertTrue(result.fine_endpoints_equal)

    def test_event_count_fixture_exposes_receptor_rate_dependence(self) -> None:
        coarse, fine = rate_steps()
        result = compare_passive_receptor_rate(
            (self.reference,),
            (self.repeated,),
            coarse,
            fine,
            field_factory=fresh_field,
            transition_factory=event_count_transition_factory,
            distribution_factory=contact_free_boundary_distribution,
        )
        self.assertFalse(result.coarse_endpoints_equal)
        self.assertFalse(result.fine_endpoints_equal)
        self.assertTrue(result.reference.coarse_reproducible)
        self.assertTrue(result.repeated.fine_reproducible)

    def test_rate_control_rejects_new_source_support(self) -> None:
        changed = sequence(
            self.repeated.frames
            + (timed(frame("auditory.new.source", 2, -0.4), 10, 11),)
        )
        coarse, fine = rate_steps()
        with self.assertRaisesRegex(
            PassiveFieldTemporalControlError,
            "identical reduced source support",
        ):
            compare_passive_receptor_rate(
                (self.reference,),
                (changed,),
                coarse,
                fine,
                field_factory=fresh_field,
                transition_factory=event_count_transition_factory,
                distribution_factory=contact_free_boundary_distribution,
            )

    def test_future_completion_cannot_change_the_completed_prefix(self) -> None:
        common = timed(frame("auditory.common.0", 0, 0.2), 1, 2)
        control = sequence((common,))
        with_future = sequence(
            (
                common,
                timed(frame("auditory.future.0", 1, 0.8), 3, 7),
            )
        )
        coarse, fine = causality_steps()
        result = compare_passive_future_event_causality(
            (control,),
            (with_future,),
            coarse,
            fine,
            cutoff_tick=6,
            field_factory=fresh_field,
            transition_factory=event_count_transition_factory,
            distribution_factory=contact_free_boundary_distribution,
        )
        self.assertTrue(result.coarse_prefix_endpoints_equal)
        self.assertTrue(result.fine_prefix_endpoints_equal)
        self.assertFalse(result.coarse_final_endpoints_equal)
        self.assertFalse(result.fine_final_endpoints_equal)

    def test_causality_control_requires_a_shared_completed_past(self) -> None:
        control = sequence(
            (timed(frame("auditory.common.0", 0, 0.2), 1, 2),)
        )
        changed_past = sequence(
            (
                timed(frame("auditory.changed.0", 0, -0.2), 1, 2),
                timed(frame("auditory.future.0", 1, 0.8), 6, 7),
            )
        )
        coarse, fine = causality_steps()
        with self.assertRaisesRegex(
            PassiveFieldTemporalControlError,
            "identical completed history",
        ):
            compare_passive_future_event_causality(
                (control,),
                (changed_past,),
                coarse,
                fine,
                cutoff_tick=6,
                field_factory=fresh_field,
                transition_factory=event_count_transition_factory,
                distribution_factory=contact_free_boundary_distribution,
            )

    def test_simultaneous_completions_ignore_sequence_declaration_order(self) -> None:
        auditory = ReceptorTimeSequence(
            "auditory",
            "auditory.geometry.v1",
            "organism.test",
            (
                timed(
                    modality_frame(
                        "auditory",
                        "auditory.simultaneous.0",
                        0,
                        0.2,
                    ),
                    2,
                    3,
                ),
                timed(
                    modality_frame(
                        "auditory",
                        "auditory.simultaneous.1",
                        1,
                        0.4,
                    ),
                    8,
                    9,
                ),
            ),
        )
        visual = ReceptorTimeSequence(
            "visual",
            "visual.geometry.v1",
            "organism.test",
            (
                timed(
                    modality_frame(
                        "visual",
                        "visual.simultaneous.0",
                        0,
                        -0.3,
                    ),
                    1,
                    3,
                ),
                timed(
                    modality_frame(
                        "visual",
                        "visual.simultaneous.1",
                        1,
                        0.5,
                    ),
                    7,
                    9,
                ),
            ),
        )
        coarse, fine = rate_steps()
        result = compare_passive_simultaneous_order(
            (auditory, visual),
            coarse,
            fine,
            field_factory=multimodal_field,
            transition_factory=event_count_transition_factory,
            distribution_factory=contact_free_boundary_distribution,
        )
        self.assertEqual((3, 9), result.simultaneous_completion_ticks)
        self.assertTrue(result.coarse_traces_equal)
        self.assertTrue(result.fine_traces_equal)

    def test_simultaneous_control_rejects_disjoint_completion_times(self) -> None:
        auditory = ReceptorTimeSequence(
            "auditory",
            "auditory.geometry.v1",
            "organism.test",
            (
                timed(
                    modality_frame(
                        "auditory",
                        "auditory.disjoint.0",
                        0,
                        0.2,
                    ),
                    2,
                    3,
                ),
            ),
        )
        visual = ReceptorTimeSequence(
            "visual",
            "visual.geometry.v1",
            "organism.test",
            (
                timed(
                    modality_frame(
                        "visual",
                        "visual.disjoint.0",
                        0,
                        -0.3,
                    ),
                    3,
                    4,
                ),
            ),
        )
        coarse, fine = rate_steps()
        with self.assertRaisesRegex(
            PassiveFieldTemporalControlError,
            "shared completion tick",
        ):
            compare_passive_simultaneous_order(
                (auditory, visual),
                coarse,
                fine,
                field_factory=multimodal_field,
                transition_factory=event_count_transition_factory,
                distribution_factory=contact_free_boundary_distribution,
            )

    def test_public_roles_do_not_encode_a_rate_or_causality_rule(self) -> None:
        roles = set(passive_field_temporal_controls_public_roles())
        forbidden = {
            "rate_weight",
            "preferred_rate",
            "future_prediction",
            "meaning",
            "memory",
            "reward",
            "learning_rule",
            "modality_order",
            "first_modality",
        }
        self.assertTrue(forbidden.isdisjoint(roles))


if __name__ == "__main__":
    unittest.main()
