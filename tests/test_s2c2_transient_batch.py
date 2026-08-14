from __future__ import annotations

import unittest

import numpy as np

from mcm_field_organism import (
    CommonFieldTime,
    MCMFieldStepTime,
    MCMLocalDevelopmentContract,
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    OrganismTimedReceptorFrame,
    ReceptorContactFrame,
    ReceptorDistribution,
    ReceptorDockAnatomy,
    ReceptorTimeSequence,
    S2ReferenceState,
    advance_neutral_fast_shared_field_transient,
    advance_s2_controlled_receptor_batch,
    advance_s2_reference_model,
    apply_s2_reference_point_contacts,
    attach_zero_mcm_local_development,
    build_shared_mcm_field,
    handoff_receptor_completion_groups,
    map_proposal_batch_to_transient_docks,
    project_transient_docks_to_neuron_inputs,
)
from mcm_field_organism.neutral_local_field_substrate import (
    _diffusion_generator,
)


EQUATION_ID = "mcm.s1b.capacity-weighted-reciprocal-accommodation.v1"
FIELD_CONFIG = NeutralLocalFieldSubstrateConfig(1.0)
AFTERIMAGE_CONFIG = NeutralFastAfterimageConfig(0.5)


def _frame(modality_id: str, index: int, value: float) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id,
        f"{modality_id}.s2c2.v1",
        f"{modality_id}.s2c2.snapshot.{index}",
        f"{modality_id}.source",
        index,
        index + 1,
        (f"{modality_id}.carrier.0",),
        (value,),
    )


def _sequence(
    modality_id: str,
    events: tuple[tuple[int, float], ...],
) -> ReceptorTimeSequence:
    return ReceptorTimeSequence(
        modality_id,
        f"{modality_id}.s2c2.v1",
        "organism.s2c2",
        tuple(
            OrganismTimedReceptorFrame(
                _frame(modality_id, index, value),
                CommonFieldTime("organism.s2c2", tick - 1, tick),
            )
            for index, (tick, value) in enumerate(events)
        ),
    )


def _sequences() -> tuple[ReceptorTimeSequence, ...]:
    return (
        _sequence("auditory", ((2, 0.8), (5, -0.2), (9, 0.4))),
        _sequence("visual", ((4, -0.6), (9, 0.3))),
    )


def _plain_field():
    return build_shared_mcm_field(
        (_frame("auditory", 100, 0.0), _frame("visual", 100, 0.0)),
        {
            "auditory": ReceptorDockAnatomy(
                "auditory", "dock.auditory", ((0,),)
            ),
            "visual": ReceptorDockAnatomy(
                "visual", "dock.visual", ((1,),)
            ),
        },
        sample_offsets=((-1,), (1,)),
    )


def _b2_field(coupling_rate: float = 0.25):
    return attach_zero_mcm_local_development(
        _plain_field(),
        MCMLocalDevelopmentContract(EQUATION_ID, 8.0, coupling_rate),
    )


def _steps(boundaries: tuple[int, ...]) -> tuple[MCMFieldStepTime, ...]:
    return tuple(
        MCMFieldStepTime("organism.s2c2", start, end, 10.0)
        for start, end in zip(boundaries, boundaries[1:])
    )


def _batch(field, step: MCMFieldStepTime):
    handoff = handoff_receptor_completion_groups(_sequences(), (step,))
    batch = handoff.batches[0]
    trajectory = map_proposal_batch_to_transient_docks(batch, field.docks)
    inputs = project_transient_docks_to_neuron_inputs(trajectory, field.docks)
    distribution = ReceptorDistribution(
        CommonFieldTime(step.clock_id, step.start_tick, step.end_tick), ()
    )
    return distribution, inputs


def _vectors(field) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return (
        np.asarray([item.activation for item in field.layer.neurons]),
        np.asarray([item.afterimage for item in field.layer.neurons]),
        np.asarray(field.development.dispositions),
    )


class S2C2TransientBatchTests(unittest.TestCase):
    def test_b0_bridge_is_exactly_the_existing_fast_transient_path(self) -> None:
        step = _steps((0, 12))[0]
        expected_field = _plain_field()
        distribution, inputs = _batch(expected_field, step)
        expected = advance_neutral_fast_shared_field_transient(
            expected_field,
            distribution,
            inputs,
            FIELD_CONFIG,
            AFTERIMAGE_CONFIG,
        )
        actual_field = _plain_field()
        distribution, inputs = _batch(actual_field, step)
        actual = advance_s2_controlled_receptor_batch(
            "b0",
            actual_field,
            distribution,
            inputs,
            FIELD_CONFIG,
            AFTERIMAGE_CONFIG,
        )

        self.assertEqual(expected.snapshot().digest(), actual.end_snapshot_digest)
        self.assertEqual(5, actual.local_contact_count)

    def test_zero_coupling_b2_preserves_fast_projection_exactly(self) -> None:
        step = _steps((0, 12))[0]
        plain = _plain_field()
        distribution, inputs = _batch(plain, step)
        expected = advance_neutral_fast_shared_field_transient(
            plain,
            distribution,
            inputs,
            FIELD_CONFIG,
            AFTERIMAGE_CONFIG,
        )
        field = _b2_field(coupling_rate=0.0)
        distribution, inputs = _batch(field, step)
        actual = advance_s2_controlled_receptor_batch(
            "b2",
            field,
            distribution,
            inputs,
            FIELD_CONFIG,
            AFTERIMAGE_CONFIG,
        ).field

        self.assertEqual(
            expected.snapshot().digest(),
            actual.snapshot().fast_state_projection_digest(),
        )
        self.assertEqual((0.0, 0.0), actual.development.dispositions)

    def test_active_b2_matches_independent_reference_over_the_same_events(self) -> None:
        step = _steps((0, 12))[0]
        field = _b2_field()
        distribution, inputs = _batch(field, step)
        actual = advance_s2_controlled_receptor_batch(
            "b2",
            field,
            distribution,
            inputs,
            FIELD_CONFIG,
            AFTERIMAGE_CONFIG,
        ).field

        state = S2ReferenceState((0.0, 0.0), (0.0, 0.0), (0.0, 0.0))
        generator = _diffusion_generator(_plain_field(), FIELD_CONFIG)
        neuron_index = {
            neuron.neuron_id: index
            for index, neuron in enumerate(field.layer.neurons)
        }
        events: dict[int, list[tuple[int, float, float]]] = {}
        for neuron_input in inputs.neuron_inputs:
            index = neuron_index[neuron_input.neuron_id]
            for contact in neuron_input.contacts:
                duration = (
                    contact.organism_read_time.window_end_tick
                    - contact.organism_read_time.window_start_tick
                ) / step.ticks_per_second
                events.setdefault(contact.completion_tick, []).append(
                    (index, duration, contact.value)
                )
        current_tick = step.start_tick
        for completion_tick, contacts in sorted(events.items()):
            elapsed = (completion_tick - current_tick) / step.ticks_per_second
            if elapsed:
                state = advance_s2_reference_model(
                    "b2", state, generator, np.zeros(2), elapsed
                ).state
            state = apply_s2_reference_point_contacts(
                state, tuple(contacts), FIELD_CONFIG.response_time_seconds
            )
            current_tick = completion_tick
        remaining = (step.end_tick - current_tick) / step.ticks_per_second
        if remaining:
            state = advance_s2_reference_model(
                "b2", state, generator, np.zeros(2), remaining
            ).state

        for observed, expected in zip(_vectors(actual), state.arrays(), strict=True):
            np.testing.assert_allclose(observed, expected, rtol=0.0, atol=2e-12)

    def test_active_b2_is_invariant_to_batch_partition(self) -> None:
        def run(boundaries: tuple[int, ...]):
            field = _b2_field()
            handoff = handoff_receptor_completion_groups(
                _sequences(), _steps(boundaries)
            )
            for batch in handoff.batches:
                trajectory = map_proposal_batch_to_transient_docks(
                    batch, field.docks
                )
                inputs = project_transient_docks_to_neuron_inputs(
                    trajectory, field.docks
                )
                distribution = ReceptorDistribution(
                    CommonFieldTime(
                        batch.step_time.clock_id,
                        batch.step_time.start_tick,
                        batch.step_time.end_tick,
                    ),
                    (),
                )
                field = advance_s2_controlled_receptor_batch(
                    "b2",
                    field,
                    distribution,
                    inputs,
                    FIELD_CONFIG,
                    AFTERIMAGE_CONFIG,
                ).field
            return field

        coarse = run((0, 12))
        fine = run((0, 3, 6, 9, 12))
        for coarse_values, fine_values in zip(
            _vectors(coarse), _vectors(fine), strict=True
        ):
            np.testing.assert_allclose(
                coarse_values, fine_values, rtol=0.0, atol=2e-12
            )


if __name__ == "__main__":
    unittest.main()
