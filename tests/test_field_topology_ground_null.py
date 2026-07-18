from __future__ import annotations

from dataclasses import replace
import unittest

import numpy as np

from mcm_field_organism import (
    CommonFieldTime,
    MCMFieldStepTime,
    MCMNeuronLayer,
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    ReceptorContactFrame,
    ReceptorDistributor,
    ReceptorDock,
    ReceptorDockAnatomy,
    SharedMCMField,
    advance_neutral_fast_shared_field,
    build_shared_mcm_field,
)


def receptor_frame(
    snapshot_id: str,
    values: tuple[float, ...],
) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id="auditory",
        geometry_id="auditory.line.v1",
        snapshot_id=snapshot_id,
        clock_id="auditory.source",
        window_start_tick=0,
        window_end_tick=10,
        carrier_ids=tuple(
            f"auditory.carrier.{index}" for index in range(len(values))
        ),
        values=values,
    )


def fresh_field() -> SharedMCMField:
    reference = receptor_frame("auditory.reference", (0.0, 0.0, 0.0))
    return build_shared_mcm_field(
        (reference,),
        {
            "auditory": ReceptorDockAnatomy(
                "auditory",
                "dock.auditory",
                ((0,), (1,), (2,)),
            )
        },
        sample_offsets=((-1,), (1,)),
    )


def distribution(
    start_tick: int,
    end_tick: int,
    snapshot_id: str,
    values: tuple[float, ...],
):
    distributor = ReceptorDistributor()
    distributor.attach(
        ReceptorDock(
            "dock.auditory",
            "auditory",
            "auditory.line.v1",
        )
    )
    return distributor.distribute(
        (receptor_frame(snapshot_id, values),),
        CommonFieldTime("organism.ground_null", start_tick, end_tick),
    )


def step(start_tick: int, end_tick: int) -> MCMFieldStepTime:
    return MCMFieldStepTime(
        "organism.ground_null",
        start_tick,
        end_tick,
        10.0,
    )


def advance(
    field: SharedMCMField,
    start_tick: int,
    end_tick: int,
    snapshot_id: str,
    values: tuple[float, ...],
) -> SharedMCMField:
    return advance_neutral_fast_shared_field(
        field,
        distribution(start_tick, end_tick, snapshot_id, values),
        step(start_tick, end_tick),
        NeutralLocalFieldSubstrateConfig(1.0),
        NeutralFastAfterimageConfig(0.5),
    )


def fast_state(field: SharedMCMField) -> tuple[tuple[float, float], ...]:
    return tuple(
        (neuron.activation, neuron.afterimage)
        for neuron in field.layer.neurons
    )


def perception_state(field: SharedMCMField) -> tuple[dict[str, object], ...]:
    return tuple(
        neuron.perception.canonical_payload()
        for neuron in field.layer.neurons
    )


def match_fast_state(
    field: SharedMCMField,
    reference: SharedMCMField,
) -> SharedMCMField:
    reference_by_id = {
        neuron.neuron_id: neuron for neuron in reference.layer.neurons
    }
    neurons = tuple(
        replace(
            neuron,
            activation=reference_by_id[neuron.neuron_id].activation,
            afterimage=reference_by_id[neuron.neuron_id].afterimage,
        )
        for neuron in field.layer.neurons
    )
    return SharedMCMField(
        layer=MCMNeuronLayer(
            layer_id=field.layer.layer_id,
            neurons=neurons,
            sample_offsets=field.layer.sample_offsets,
            periodic_axes=field.layer.periodic_axes,
            receptor_dock_ids=field.layer.docked_neuron_ids,
        ),
        docks=field.docks,
        last_distribution=field.last_distribution,
    )


class FieldTopologyGroundNullTests(unittest.TestCase):
    def test_matched_fast_state_has_no_further_history_effect(self) -> None:
        history_a = advance(
            fresh_field(),
            0,
            10,
            "history.a",
            (1.0, 0.0, -1.0),
        )
        history_b = advance(
            fresh_field(),
            0,
            10,
            "history.b",
            (-1.0, 0.0, 1.0),
        )
        reference = advance(
            fresh_field(),
            0,
            10,
            "history.reference",
            (0.4, -0.2, 0.1),
        )
        history_a = advance(
            history_a,
            10,
            20,
            "common.current",
            (0.2, 0.2, 0.2),
        )
        history_b = advance(
            history_b,
            10,
            20,
            "common.current",
            (0.2, 0.2, 0.2),
        )
        reference = advance(
            reference,
            10,
            20,
            "common.current",
            (0.2, 0.2, 0.2),
        )

        self.assertNotEqual(fast_state(history_a), fast_state(history_b))
        self.assertNotEqual(perception_state(history_a), perception_state(history_b))

        matched_a = match_fast_state(history_a, reference)
        matched_b = match_fast_state(history_b, reference)

        self.assertEqual(fast_state(matched_a), fast_state(matched_b))
        self.assertEqual(
            matched_a.last_distribution.canonical_payload(),
            matched_b.last_distribution.canonical_payload(),
        )
        self.assertNotEqual(
            perception_state(matched_a),
            perception_state(matched_b),
        )
        self.assertNotEqual(
            matched_a.snapshot().digest(),
            matched_b.snapshot().digest(),
        )

        probe_a = advance(
            matched_a,
            20,
            30,
            "identical.probe",
            (0.7, -0.4, 0.1),
        )
        probe_b = advance(
            matched_b,
            20,
            30,
            "identical.probe",
            (0.7, -0.4, 0.1),
        )

        np.testing.assert_allclose(
            np.asarray(fast_state(probe_a)),
            np.asarray(fast_state(probe_b)),
            rtol=0.0,
            atol=0.0,
        )
        self.assertEqual(
            probe_a.snapshot().digest(),
            probe_b.snapshot().digest(),
        )


if __name__ == "__main__":
    unittest.main()
