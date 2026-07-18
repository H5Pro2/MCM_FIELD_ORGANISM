from __future__ import annotations

import unittest

import numpy as np

from mcm_field_organism import (
    CommonFieldTime,
    MCMFieldStepTime,
    NeutralAsynchronousFieldRuntimeError,
    NeutralLocalFieldSubstrateConfig,
    OrganismTimedReceptorFrame,
    ReceptorContactFrame,
    ReceptorDockAnatomy,
    ReceptorTimeSequence,
    build_shared_mcm_field,
    run_neutral_asynchronous_field,
)


def receptor_frame(
    modality_id: str,
    snapshot_index: int,
    value: float,
    *,
    source_start: int | None = None,
) -> ReceptorContactFrame:
    source_start = snapshot_index if source_start is None else source_start
    return ReceptorContactFrame(
        modality_id=modality_id,
        geometry_id=f"{modality_id}.geometry.v1",
        snapshot_id=f"{modality_id}.snapshot.{snapshot_index}",
        clock_id=f"{modality_id}.source",
        window_start_tick=source_start,
        window_end_tick=source_start + 1,
        carrier_ids=(f"{modality_id}.carrier.0",),
        values=(value,),
    )


def sequence(
    modality_id: str,
    events: tuple[tuple[int, int, float, int | None], ...],
) -> ReceptorTimeSequence:
    return ReceptorTimeSequence(
        modality_id,
        f"{modality_id}.geometry.v1",
        "organism.test",
        tuple(
            OrganismTimedReceptorFrame(
                receptor_frame(
                    modality_id,
                    snapshot_index,
                    value,
                    source_start=source_start,
                ),
                CommonFieldTime(
                    "organism.test",
                    completion_tick - 1,
                    completion_tick,
                ),
            )
            for snapshot_index, completion_tick, value, source_start in events
        ),
    )


def source_sequences() -> tuple[ReceptorTimeSequence, ...]:
    return (
        sequence(
            "auditory",
            ((0, 2, 0.8, None), (1, 5, -0.2, None), (2, 9, 0.4, None)),
        ),
        sequence("visual", ((0, 4, -0.6, None), (1, 9, 0.3, None))),
    )


def fresh_field():
    auditory = receptor_frame("auditory", 100, 0.0)
    visual = receptor_frame("visual", 100, 0.0)
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


def activation(run) -> np.ndarray:
    return np.asarray(
        [
            neuron.activation
            for neuron in sorted(run.field.layer.neurons, key=lambda item: item.position)
        ]
    )


class NeutralAsynchronousFieldRunTests(unittest.TestCase):
    def test_complete_unique_source_history_runs_once(self) -> None:
        result = run_neutral_asynchronous_field(
            fresh_field(),
            source_sequences(),
            steps((0, 3, 6, 9, 12)),
            NeutralLocalFieldSubstrateConfig(1.0),
        )
        self.assertEqual(5, result.source_support_count)
        self.assertEqual(5, result.handoff.assigned_event_count)
        self.assertTrue(result.handoff.every_in_horizon_event_assigned_once)

    def test_observation_partition_does_not_change_the_field(self) -> None:
        coarse = run_neutral_asynchronous_field(
            fresh_field(),
            source_sequences(),
            steps((0, 12)),
            NeutralLocalFieldSubstrateConfig(1.0),
        )
        fine = run_neutral_asynchronous_field(
            fresh_field(),
            source_sequences(),
            steps((0, 3, 6, 9, 12)),
            NeutralLocalFieldSubstrateConfig(1.0),
        )
        np.testing.assert_allclose(
            activation(coarse),
            activation(fine),
            rtol=0.0,
            atol=2e-15,
        )

    def test_duplicate_source_support_is_rejected_before_field_change(self) -> None:
        field = fresh_field()
        before = field.layer
        duplicated = sequence(
            "auditory",
            ((0, 2, 0.8, 7), (1, 5, 0.8, 7)),
        )
        with self.assertRaisesRegex(
            NeutralAsynchronousFieldRuntimeError,
            "duplicate technical completion",
        ):
            run_neutral_asynchronous_field(
                field,
                (duplicated,),
                steps((0, 6)),
                NeutralLocalFieldSubstrateConfig(1.0),
            )
        self.assertEqual(before, field.layer)

    def test_conflicting_duplicate_source_support_is_rejected(self) -> None:
        conflicting = sequence(
            "auditory",
            ((0, 2, 0.8, 7), (1, 5, -0.2, 7)),
        )
        with self.assertRaisesRegex(
            NeutralAsynchronousFieldRuntimeError,
            "conflicting technical completions",
        ):
            run_neutral_asynchronous_field(
                fresh_field(),
                (conflicting,),
                steps((0, 6)),
                NeutralLocalFieldSubstrateConfig(1.0),
            )

    def test_equal_source_ticks_from_different_modalities_are_independent(self) -> None:
        result = run_neutral_asynchronous_field(
            fresh_field(),
            (
                sequence("auditory", ((0, 2, 0.8, 7),)),
                sequence("visual", ((0, 2, -0.6, 7),)),
            ),
            steps((0, 3)),
            NeutralLocalFieldSubstrateConfig(1.0),
        )
        self.assertEqual(2, result.source_support_count)

    def test_supplied_history_must_fit_the_bounded_horizon(self) -> None:
        with self.assertRaisesRegex(
            NeutralAsynchronousFieldRuntimeError,
            "inside its horizon",
        ):
            run_neutral_asynchronous_field(
                fresh_field(),
                source_sequences(),
                steps((0, 6)),
                NeutralLocalFieldSubstrateConfig(1.0),
            )


if __name__ == "__main__":
    unittest.main()
