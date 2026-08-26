from __future__ import annotations

import unittest

import numpy as np

from mcm_field_organism import (
    CommonFieldTime,
    DistributedReceptorContact,
    MCMFieldStepTime,
    MCMSubstrateArmContract,
    NeutralLocalFieldSubstrateConfig,
    NeutralLocalFieldSubstrateError,
    OrganismTimedReceptorFrame,
    ReceptorContactFrame,
    ReceptorDistribution,
    ReceptorDockAnatomy,
    ReceptorTimeSequence,
    attach_uniform_mcm_substrate,
    advance_neutral_shared_field_transient,
    build_shared_mcm_field,
    handoff_receptor_completion_groups,
    map_proposal_batch_to_transient_docks,
    project_transient_docks_to_neuron_inputs,
    restore_shared_mcm_field,
)


def frame(
    modality_id: str,
    index: int,
    value: float,
) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id=modality_id,
        geometry_id=f"{modality_id}.geometry.v1",
        snapshot_id=f"{modality_id}.snapshot.{index}",
        clock_id=f"{modality_id}.source",
        window_start_tick=index,
        window_end_tick=index + 1,
        carrier_ids=(f"{modality_id}.carrier.0",),
        values=(value,),
    )


def sequence(
    modality_id: str,
    events: tuple[tuple[int, float], ...],
) -> ReceptorTimeSequence:
    return ReceptorTimeSequence(
        modality_id,
        f"{modality_id}.geometry.v1",
        "organism.test",
        tuple(
            OrganismTimedReceptorFrame(
                frame(modality_id, index, value),
                CommonFieldTime(
                    "organism.test",
                    completion_tick - 1,
                    completion_tick,
                ),
            )
            for index, (completion_tick, value) in enumerate(events)
        ),
    )


def sequences() -> tuple[ReceptorTimeSequence, ...]:
    return (
        sequence("auditory", ((2, 0.8), (5, -0.2), (9, 0.4))),
        sequence("visual", ((4, -0.6), (9, 0.3))),
    )


def fresh_field():
    auditory = frame("auditory", 100, 0.0)
    visual = frame("visual", 100, 0.0)
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


def steps(boundaries: tuple[int, ...]) -> tuple[MCMFieldStepTime, ...]:
    return tuple(
        MCMFieldStepTime("organism.test", start, end, 10.0)
        for start, end in zip(boundaries, boundaries[1:])
    )


def run(
    source_sequences: tuple[ReceptorTimeSequence, ...],
    field_steps: tuple[MCMFieldStepTime, ...],
    *,
    field=None,
):
    current = fresh_field() if field is None else field
    handoff = handoff_receptor_completion_groups(
        source_sequences,
        field_steps,
    )
    for batch in handoff.batches:
        trajectory = map_proposal_batch_to_transient_docks(
            batch,
            current.docks,
        )
        local_inputs = project_transient_docks_to_neuron_inputs(
            trajectory,
            current.docks,
        )
        current = advance_neutral_shared_field_transient(
            current,
            ReceptorDistribution(
                CommonFieldTime(
                    batch.step_time.clock_id,
                    batch.step_time.start_tick,
                    batch.step_time.end_tick,
                ),
                (),
            ),
            local_inputs,
            NeutralLocalFieldSubstrateConfig(1.0),
        )
    return current, handoff


def activation(field) -> np.ndarray:
    return np.asarray(
        [
            neuron.activation
            for neuron in sorted(
                field.layer.neurons,
                key=lambda item: item.position,
            )
        ],
        dtype=np.float64,
    )


class NeutralAsynchronousFieldRuntimeTests(unittest.TestCase):
    def test_asynchronous_audio_video_history_is_partition_invariant(self) -> None:
        coarse, coarse_handoff = run(sequences(), steps((0, 12)))
        fine, fine_handoff = run(sequences(), steps((0, 3, 6, 9, 12)))
        self.assertTrue(coarse_handoff.every_in_horizon_event_assigned_once)
        self.assertTrue(fine_handoff.every_in_horizon_event_assigned_once)
        self.assertEqual(5, coarse_handoff.assigned_event_count)
        self.assertEqual(5, fine_handoff.assigned_event_count)
        np.testing.assert_allclose(
            activation(coarse),
            activation(fine),
            rtol=0.0,
            atol=2e-15,
        )

    def test_simultaneous_completion_is_declaration_order_neutral(self) -> None:
        declared, _ = run(sequences(), steps((0, 12)))
        reversed_order, _ = run(tuple(reversed(sequences())), steps((0, 12)))
        np.testing.assert_allclose(
            activation(declared),
            activation(reversed_order),
            rtol=0.0,
            atol=0.0,
        )

    def test_future_completion_cannot_change_an_earlier_prefix(self) -> None:
        common = (
            sequence("auditory", ((2, 0.8),)),
            sequence("visual", ((4, -0.6),)),
        )
        with_future = (
            sequence("auditory", ((2, 0.8), (9, 0.4))),
            sequence("visual", ((4, -0.6),)),
        )
        prefix_steps = steps((0, 6))
        control, _ = run(common, prefix_steps)
        future, _ = run(with_future, prefix_steps)
        np.testing.assert_allclose(
            activation(control),
            activation(future),
            rtol=0.0,
            atol=0.0,
        )

    def test_snapshot_resume_preserves_the_next_asynchronous_interval(self) -> None:
        first_sequences = (
            sequence("auditory", ((2, 0.8),)),
            sequence("visual", ((4, -0.6),)),
        )
        first, _ = run(first_sequences, steps((0, 6)))
        restored = restore_shared_mcm_field(first.snapshot())
        later_sequences = (
            sequence("auditory", ((9, 0.4),)),
            sequence("visual", ((9, 0.3),)),
        )
        later_steps = steps((6, 12))
        uninterrupted, _ = run(
            later_sequences,
            later_steps,
            field=first,
        )
        resumed, _ = run(
            later_sequences,
            later_steps,
            field=restored,
        )
        self.assertEqual(
            uninterrupted.snapshot().digest(),
            resumed.snapshot().digest(),
        )

    def test_null_substrate_preserves_the_exact_asynchronous_fast_projection(self) -> None:
        legacy, _ = run(sequences(), steps((0, 3, 6, 9, 12)))
        initial = attach_uniform_mcm_substrate(
            fresh_field(),
            MCMSubstrateArmContract("p0.null", 0.0, 0.25, 0.5),
        )
        with_substrate, _ = run(
            sequences(),
            steps((0, 3, 6, 9, 12)),
            field=initial,
        )

        self.assertEqual(
            legacy.snapshot().digest(),
            with_substrate.snapshot().fast_state_projection_digest(),
        )
        self.assertEqual(
            initial.substrate.digest(),
            with_substrate.substrate.digest(),
        )

    def test_transient_path_rejects_a_second_scalar_contact_path(self) -> None:
        source = sequences()
        handoff = handoff_receptor_completion_groups(
            source,
            steps((0, 12)),
        )
        field = fresh_field()
        trajectory = map_proposal_batch_to_transient_docks(
            handoff.batches[0],
            field.docks,
        )
        local_inputs = project_transient_docks_to_neuron_inputs(
            trajectory,
            field.docks,
        )
        scalar_contact = ReceptorDistribution(
            CommonFieldTime("organism.test", 0, 12),
            (
                DistributedReceptorContact(
                    "dock.auditory",
                    frame("auditory", 200, 0.1),
                ),
            ),
        )
        with self.assertRaisesRegex(
            NeutralLocalFieldSubstrateError,
            "contact-free",
        ):
            advance_neutral_shared_field_transient(
                field,
                scalar_contact,
                local_inputs,
                NeutralLocalFieldSubstrateConfig(1.0),
            )


if __name__ == "__main__":
    unittest.main()
