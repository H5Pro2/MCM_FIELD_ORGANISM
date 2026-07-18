from __future__ import annotations

from dataclasses import replace
import math
import unittest

import numpy as np

from mcm_field_organism import (
    CommonFieldTime,
    MCMFieldStepTime,
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    NeutralLocalFieldSubstrateError,
    OrganismTimedReceptorFrame,
    ReceptorContactFrame,
    ReceptorDistribution,
    ReceptorDistributor,
    ReceptorDock,
    ReceptorDockAnatomy,
    ReceptorTimeSequence,
    advance_neutral_fast_shared_field,
    advance_neutral_fast_shared_field_transient,
    build_shared_mcm_field,
    handoff_receptor_completion_groups,
    map_proposal_batch_to_transient_docks,
    project_transient_docks_to_neuron_inputs,
    restore_shared_mcm_field,
)


def receptor_frame(snapshot_id: str, values: tuple[float, ...]):
    return ReceptorContactFrame(
        modality_id="auditory",
        geometry_id="auditory.line.v1",
        snapshot_id=snapshot_id,
        clock_id="auditory.source",
        window_start_tick=0,
        window_end_tick=1,
        carrier_ids=tuple(
            f"auditory.carrier.{index}" for index in range(len(values))
        ),
        values=values,
    )


def shared_field(size: int = 3):
    reference = receptor_frame("auditory.reference", (0.0,) * size)
    return build_shared_mcm_field(
        (reference,),
        {
            "auditory": ReceptorDockAnatomy(
                "auditory",
                "dock.auditory",
                tuple((index,) for index in range(size)),
            )
        },
        sample_offsets=((-1,), (1,)),
    )


def distribution(
    start_tick: int,
    end_tick: int,
    snapshot_id: str,
    values: tuple[float, ...] | None,
) -> ReceptorDistribution:
    distributor = ReceptorDistributor()
    distributor.attach(
        ReceptorDock("dock.auditory", "auditory", "auditory.line.v1")
    )
    frames = () if values is None else (receptor_frame(snapshot_id, values),)
    return distributor.distribute(
        frames,
        CommonFieldTime("organism.test", start_tick, end_tick),
    )


def step(start_tick: int, end_tick: int) -> MCMFieldStepTime:
    return MCMFieldStepTime("organism.test", start_tick, end_tick, 10.0)


def values(field, role: str) -> np.ndarray:
    return np.asarray(
        [
            getattr(neuron, role)
            for neuron in sorted(field.layer.neurons, key=lambda item: item.position)
        ],
        dtype=np.float64,
    )


def with_fast_state(field, activation, afterimage):
    neurons = tuple(
        replace(
            neuron,
            activation=activation[index],
            afterimage=afterimage[index],
        )
        for index, neuron in enumerate(field.layer.neurons)
    )
    return replace(field, layer=replace(field.layer, neurons=neurons))


class NeutralFastAfterimageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.substrate = NeutralLocalFieldSubstrateConfig(1.0)
        self.afterimage = NeutralFastAfterimageConfig(0.5)

    def test_afterimage_time_requires_one_explicit_positive_scale(self) -> None:
        for value in (0.0, -1.0, math.inf, math.nan):
            with self.subTest(value=value), self.assertRaises(
                NeutralLocalFieldSubstrateError
            ):
                NeutralFastAfterimageConfig(value)

    def test_world_driven_activation_builds_a_delayed_local_trace(self) -> None:
        result = advance_neutral_fast_shared_field(
            shared_field(),
            distribution(0, 10, "contact", (1.0, 0.0, 0.0)),
            step(0, 10),
            self.substrate,
            self.afterimage,
        )
        activation = values(result, "activation")
        afterimage = values(result, "afterimage")
        self.assertTrue(np.all(afterimage > 0.0))
        self.assertTrue(np.all(afterimage < activation))

    def test_fast_state_is_invariant_to_observation_partition(self) -> None:
        initial = shared_field()
        coarse = advance_neutral_fast_shared_field(
            initial,
            distribution(0, 10, "coarse", (0.8, -0.2, 0.3)),
            step(0, 10),
            self.substrate,
            self.afterimage,
        )
        fine = advance_neutral_fast_shared_field(
            initial,
            distribution(0, 5, "fine.1", (0.8, -0.2, 0.3)),
            step(0, 5),
            self.substrate,
            self.afterimage,
        )
        fine = advance_neutral_fast_shared_field(
            fine,
            distribution(5, 10, "fine.2", (0.8, -0.2, 0.3)),
            step(5, 10),
            self.substrate,
            self.afterimage,
        )
        np.testing.assert_allclose(
            values(coarse, "activation"),
            values(fine, "activation"),
            rtol=0.0,
            atol=2e-15,
        )
        np.testing.assert_allclose(
            values(coarse, "afterimage"),
            values(fine, "afterimage"),
            rtol=0.0,
            atol=2e-15,
        )

    def test_unforced_trace_relaxes_locally_when_activation_is_neutral(self) -> None:
        initial = with_fast_state(
            shared_field(),
            (0.0, 0.0, 0.0),
            (0.8, 0.0, 0.0),
        )
        result = advance_neutral_fast_shared_field(
            initial,
            distribution(0, 100, "absent", None),
            step(0, 100),
            self.substrate,
            self.afterimage,
        )
        afterimage = values(result, "afterimage")
        self.assertLess(afterimage[0], 2e-9)
        np.testing.assert_allclose(
            afterimage[1:],
            (0.0, 0.0),
            rtol=0.0,
            atol=1e-23,
        )

    def test_snapshot_resume_preserves_both_fast_time_roles(self) -> None:
        first = advance_neutral_fast_shared_field(
            shared_field(),
            distribution(0, 10, "first", (1.0, 0.0, -0.4)),
            step(0, 10),
            self.substrate,
            self.afterimage,
        )
        restored = restore_shared_mcm_field(first.snapshot())
        next_distribution = distribution(10, 20, "next", None)
        uninterrupted = advance_neutral_fast_shared_field(
            first,
            next_distribution,
            step(10, 20),
            self.substrate,
            self.afterimage,
        )
        resumed = advance_neutral_fast_shared_field(
            restored,
            next_distribution,
            step(10, 20),
            self.substrate,
            self.afterimage,
        )
        self.assertEqual(
            uninterrupted.snapshot().digest(),
            resumed.snapshot().digest(),
        )

    def test_asynchronous_contact_enters_trace_only_after_completion(self) -> None:
        field = shared_field(2)
        timed = OrganismTimedReceptorFrame(
            receptor_frame("auditory.event", (1.0, 0.0)),
            CommonFieldTime("organism.test", 1, 2),
        )
        sequence = ReceptorTimeSequence(
            "auditory",
            "auditory.line.v1",
            "organism.test",
            (timed,),
        )
        handoff = handoff_receptor_completion_groups((sequence,), (step(0, 10),))
        trajectory = map_proposal_batch_to_transient_docks(
            handoff.batches[0],
            field.docks,
        )
        local_inputs = project_transient_docks_to_neuron_inputs(
            trajectory,
            field.docks,
        )
        result = advance_neutral_fast_shared_field_transient(
            field,
            distribution(0, 10, "boundary", None),
            local_inputs,
            self.substrate,
            self.afterimage,
        )
        self.assertGreater(float(np.max(values(result, "activation"))), 0.0)
        self.assertGreater(float(np.max(values(result, "afterimage"))), 0.0)


if __name__ == "__main__":
    unittest.main()
