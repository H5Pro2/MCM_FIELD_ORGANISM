from __future__ import annotations

import unittest

import numpy as np

from mcm_field_organism import (
    CommonFieldTime,
    MCMFieldStepTime,
    MCMSubstrateArmContract,
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    OrganismTimedReceptorFrame,
    ReceptorContactFrame,
    ReceptorDockAnatomy,
    ReceptorTimeSequence,
    attach_uniform_mcm_substrate,
    build_shared_mcm_field,
    restore_shared_mcm_field,
    run_neutral_asynchronous_field,
)
from mcm_field_organism.current_api import (
    MCMLocalDevelopmentContract,
    S1BAsynchronousFieldRuntimeError,
    run_s1b_asynchronous_field,
)


EQUATION_ID = "mcm.s1b.capacity-weighted-reciprocal-accommodation.v1"
FIELD_CONFIG = NeutralLocalFieldSubstrateConfig(1.0)
AFTERIMAGE_CONFIG = NeutralFastAfterimageConfig(0.5)


def frame(modality_id: str, index: int, value: float) -> ReceptorContactFrame:
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
        "organism.s1b.adapter.test",
        tuple(
            OrganismTimedReceptorFrame(
                frame(modality_id, index, value),
                CommonFieldTime(
                    "organism.s1b.adapter.test",
                    completion_tick - 1,
                    completion_tick,
                ),
            )
            for index, (completion_tick, value) in enumerate(events)
        ),
    )


def sequences() -> tuple[ReceptorTimeSequence, ReceptorTimeSequence]:
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


def step(start: int, end: int) -> MCMFieldStepTime:
    return MCMFieldStepTime(
        "organism.s1b.adapter.test",
        start,
        end,
        10.0,
    )


def contract(coupling_rate: float) -> MCMLocalDevelopmentContract:
    return MCMLocalDevelopmentContract(
        EQUATION_ID,
        8.0,
        coupling_rate,
    )


class S1BAsynchronousFieldRuntimeTests(unittest.TestCase):
    def test_null_arm_preserves_exact_neutral_fast_projection(self) -> None:
        neutral = run_neutral_asynchronous_field(
            fresh_field(),
            sequences(),
            (step(0, 12),),
            FIELD_CONFIG,
            afterimage_config=AFTERIMAGE_CONFIG,
        )
        reference = run_s1b_asynchronous_field(
            fresh_field(),
            sequences(),
            (step(0, 12),),
            FIELD_CONFIG,
            contract(0.0),
            afterimage_config=AFTERIMAGE_CONFIG,
        )

        self.assertEqual(
            neutral.field.snapshot().digest(),
            reference.field.snapshot().fast_state_projection_digest(),
        )
        self.assertEqual((0.0, 0.0), reference.field.development.dispositions)
        self.assertEqual(5, reference.source_support_count)

    def test_active_arm_creates_schema_three_l_state(self) -> None:
        result = run_s1b_asynchronous_field(
            fresh_field(),
            sequences(),
            (step(0, 12),),
            FIELD_CONFIG,
            contract(0.25),
            afterimage_config=AFTERIMAGE_CONFIG,
        )

        snapshot = result.field.snapshot()
        self.assertEqual(3, snapshot.schema_version)
        self.assertIsNotNone(snapshot.development)
        self.assertTrue(
            any(value != 0.0 for value in result.field.development.dispositions)
        )

    def test_active_arm_is_invariant_to_equivalent_step_partition(self) -> None:
        coarse = run_s1b_asynchronous_field(
            fresh_field(),
            sequences(),
            (step(0, 12),),
            FIELD_CONFIG,
            contract(0.25),
            afterimage_config=AFTERIMAGE_CONFIG,
        ).field
        fine = run_s1b_asynchronous_field(
            fresh_field(),
            sequences(),
            (step(0, 3), step(3, 6), step(6, 9), step(9, 12)),
            FIELD_CONFIG,
            contract(0.25),
            afterimage_config=AFTERIMAGE_CONFIG,
        ).field

        for coarse_values, fine_values in (
            (
                tuple(item.activation for item in coarse.layer.neurons),
                tuple(item.activation for item in fine.layer.neurons),
            ),
            (
                tuple(item.afterimage for item in coarse.layer.neurons),
                tuple(item.afterimage for item in fine.layer.neurons),
            ),
            (
                coarse.development.dispositions,
                fine.development.dispositions,
            ),
        ):
            np.testing.assert_allclose(
                coarse_values,
                fine_values,
                rtol=0.0,
                atol=2e-15,
            )

    def test_schema_three_restore_continues_bit_exactly(self) -> None:
        first_sequences = (
            sequence("auditory", ((2, 0.8),)),
            sequence("visual", ((4, -0.6),)),
        )
        first = run_s1b_asynchronous_field(
            fresh_field(),
            first_sequences,
            (step(0, 6),),
            FIELD_CONFIG,
            contract(0.25),
            afterimage_config=AFTERIMAGE_CONFIG,
        ).field
        restored = restore_shared_mcm_field(first.snapshot())
        later_sequences = (
            sequence("auditory", ((9, 0.4),)),
            sequence("visual", ((9, 0.3),)),
        )
        expected = run_s1b_asynchronous_field(
            first,
            later_sequences,
            (step(6, 12),),
            FIELD_CONFIG,
            contract(0.25),
            afterimage_config=AFTERIMAGE_CONFIG,
        ).field
        resumed = run_s1b_asynchronous_field(
            restored,
            later_sequences,
            (step(6, 12),),
            FIELD_CONFIG,
            contract(0.25),
            afterimage_config=AFTERIMAGE_CONFIG,
        ).field

        self.assertEqual(expected.snapshot().digest(), resumed.snapshot().digest())

    def test_adapter_rejects_substrate_and_contract_change(self) -> None:
        with_substrate = attach_uniform_mcm_substrate(
            fresh_field(),
            MCMSubstrateArmContract("p0.null", 0.0, 0.25, 0.5),
        )
        with self.assertRaisesRegex(
            S1BAsynchronousFieldRuntimeError,
            "cannot combine M and L",
        ):
            run_s1b_asynchronous_field(
                with_substrate,
                sequences(),
                (step(0, 12),),
                FIELD_CONFIG,
                contract(0.25),
                afterimage_config=AFTERIMAGE_CONFIG,
            )

        active = run_s1b_asynchronous_field(
            fresh_field(),
            sequences(),
            (step(0, 12),),
            FIELD_CONFIG,
            contract(0.25),
            afterimage_config=AFTERIMAGE_CONFIG,
        ).field
        later = (
            sequence("auditory", ((14, 0.1),)),
            sequence("visual", ((15, -0.1),)),
        )
        with self.assertRaisesRegex(
            S1BAsynchronousFieldRuntimeError,
            "cannot change the L nature contract",
        ):
            run_s1b_asynchronous_field(
                active,
                later,
                (step(12, 18),),
                FIELD_CONFIG,
                contract(0.5),
                afterimage_config=AFTERIMAGE_CONFIG,
            )


if __name__ == "__main__":
    unittest.main()
