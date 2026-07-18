from __future__ import annotations

import unittest

from mcm_field_organism import (
    CommonFieldTime,
    MCMFieldStepTime,
    MCMNeuronOutput,
    OrganismTimedReceptorFrame,
    PassiveFieldResumeControlError,
    ReceptorContactFrame,
    ReceptorDockAnatomy,
    ReceptorTimeSequence,
    adapt_passive_local_transition,
    all_passive_drive_roles,
    build_shared_mcm_field,
    compare_passive_field_resume,
    contact_free_boundary_distribution,
    passive_field_resume_control_public_roles,
)


def frame(index: int, values: tuple[float, float]) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id="auditory",
        geometry_id="auditory.geometry.v1",
        snapshot_id=f"auditory.snapshot.{index}",
        clock_id="auditory.source",
        window_start_tick=index,
        window_end_tick=index + 1,
        carrier_ids=("auditory.carrier.0", "auditory.carrier.1"),
        values=values,
    )


def sequence() -> ReceptorTimeSequence:
    values = ((0.2, -0.1), (0.4, 0.3), (-0.5, 0.6), (0.1, -0.2))
    completions = (2, 5, 7, 11)
    return ReceptorTimeSequence(
        "auditory",
        "auditory.geometry.v1",
        "organism.test",
        tuple(
            OrganismTimedReceptorFrame(
                frame(index, item),
                CommonFieldTime(
                    "organism.test",
                    completion - 1,
                    completion,
                ),
            )
            for index, (item, completion) in enumerate(
                zip(values, completions, strict=True)
            )
        ),
    )


def fresh_field():
    return build_shared_mcm_field(
        (frame(0, (0.0, 0.0)),),
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
    return tuple(
        MCMFieldStepTime("organism.test", start, start + 3, 10.0)
        for start in range(0, 12, 3)
    )


def fine_steps() -> tuple[MCMFieldStepTime, ...]:
    return tuple(
        MCMFieldStepTime("organism.test", start, start + 2, 10.0)
        for start in range(0, 12, 2)
    )


def stateless_transition(drive) -> MCMNeuronOutput:
    previous = (
        0.0
        if drive.previous_state is None
        else drive.previous_state.activation
    )
    local_sum = sum(
        item.value for item in (drive.transient_receptor_history or ())
    )
    return MCMNeuronOutput(
        max(-1.0, min(1.0, previous + 0.05 * local_sum)),
        0.0,
    )


def stateless_transition_factory():
    return adapt_passive_local_transition(
        stateless_transition,
        all_passive_drive_roles(),
    )


def hidden_counter_transition_factory():
    calls = 0

    def hidden_counter(drive) -> MCMNeuronOutput:
        nonlocal calls
        calls += 1
        previous = (
            0.0
            if drive.previous_state is None
            else drive.previous_state.activation
        )
        return MCMNeuronOutput(
            min(1.0, previous + 0.01 * calls),
            0.0,
        )

    return adapt_passive_local_transition(
        hidden_counter,
        all_passive_drive_roles(),
    )


class PassiveFieldResumeControlTests(unittest.TestCase):
    def test_stateless_transition_resumes_with_exact_complete_traces(self) -> None:
        result = compare_passive_field_resume(
            (sequence(),),
            coarse_steps(),
            fine_steps(),
            resume_tick=6,
            field_factory=fresh_field,
            transition_factory=stateless_transition_factory,
            distribution_factory=contact_free_boundary_distribution,
        )
        self.assertTrue(result.all_events_assigned_once)
        self.assertTrue(result.coarse_resume_exact)
        self.assertTrue(result.fine_resume_exact)
        self.assertTrue(result.coarse.uninterrupted_reproducible)
        self.assertTrue(result.coarse.resumed_reproducible)
        self.assertTrue(result.fine.uninterrupted_reproducible)
        self.assertTrue(result.fine.resumed_reproducible)
        self.assertEqual(
            result.coarse.snapshot_digest,
            result.coarse.restored_snapshot_digest,
        )
        self.assertEqual(
            result.fine.snapshot_digest,
            result.fine.restored_snapshot_digest,
        )
        self.assertEqual(
            4,
            result.coarse.resumed.assigned_event_count,
        )
        self.assertEqual(
            tuple(step.event_count for step in result.coarse.uninterrupted.steps),
            tuple(step.event_count for step in result.coarse.resumed.steps),
        )

    def test_hidden_transition_state_is_exposed_by_fresh_resume_factory(self) -> None:
        result = compare_passive_field_resume(
            (sequence(),),
            coarse_steps(),
            fine_steps(),
            resume_tick=6,
            field_factory=fresh_field,
            transition_factory=hidden_counter_transition_factory,
            distribution_factory=contact_free_boundary_distribution,
        )
        self.assertFalse(result.coarse_resume_exact)
        self.assertFalse(result.fine_resume_exact)
        self.assertTrue(result.coarse.uninterrupted_reproducible)
        self.assertTrue(result.coarse.resumed_reproducible)

    def test_resume_tick_must_be_a_shared_nonfinal_boundary(self) -> None:
        for resume_tick in (5, 12):
            with self.subTest(resume_tick=resume_tick), self.assertRaisesRegex(
                PassiveFieldResumeControlError,
                "non-final field step",
            ):
                compare_passive_field_resume(
                    (sequence(),),
                    coarse_steps(),
                    fine_steps(),
                    resume_tick=resume_tick,
                    field_factory=fresh_field,
                    transition_factory=stateless_transition_factory,
                    distribution_factory=contact_free_boundary_distribution,
                )

    def test_coarse_and_fine_horizons_must_match(self) -> None:
        shortened = fine_steps()[:-1]
        with self.assertRaisesRegex(
            PassiveFieldResumeControlError,
            "same organism horizon",
        ):
            compare_passive_field_resume(
                (sequence(),),
                coarse_steps(),
                shortened,
                resume_tick=6,
                field_factory=fresh_field,
                transition_factory=stateless_transition_factory,
                distribution_factory=contact_free_boundary_distribution,
            )

    def test_public_roles_contain_no_hidden_persistence_mechanism(self) -> None:
        roles = set(passive_field_resume_control_public_roles())
        forbidden = {
            "closure_state",
            "transition_cache",
            "replay_buffer",
            "meaning",
            "memory_rule",
            "learning_rule",
            "reward",
        }
        self.assertTrue(forbidden.isdisjoint(roles))


if __name__ == "__main__":
    unittest.main()
