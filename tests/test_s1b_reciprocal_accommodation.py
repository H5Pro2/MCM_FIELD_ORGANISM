from __future__ import annotations

import json
import unittest

import numpy as np

from mcm_field_organism import (
    CommonFieldTime,
    MCMFieldStepTime,
    MCMLocalDevelopmentContract,
    MCMSubstrateArmContract,
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    ReceptorContactFrame,
    ReceptorDistribution,
    ReceptorDistributor,
    ReceptorDock,
    ReceptorDockAnatomy,
    S1BReciprocalAccommodationError,
    SharedMCMFieldError,
    SharedMCMFieldSnapshot,
    advance_neutral_fast_shared_field,
    advance_s1b_reciprocal_shared_field,
    attach_uniform_mcm_substrate,
    attach_zero_mcm_local_development,
    build_shared_mcm_field,
    neutralize_mcm_local_development,
    receptor_projection_baseline,
    restore_shared_mcm_field,
    swap_mcm_local_development,
)


EQUATION_ID = "mcm.s1b.capacity-weighted-reciprocal-accommodation.v1"
OFFSETS = ((0, -1), (0, 1))
FIELD_CONFIG = NeutralLocalFieldSubstrateConfig(1.0)
AFTERIMAGE_CONFIG = NeutralFastAfterimageConfig(0.5)


def source(values: tuple[float, float], snapshot: int) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id="visual",
        geometry_id="visual.s1b.v1",
        snapshot_id=f"visual.s1b.snapshot.{snapshot}",
        clock_id="visual.source",
        window_start_tick=snapshot * 10,
        window_end_tick=(snapshot + 1) * 10,
        carrier_ids=("visual.carrier.0", "visual.carrier.1"),
        values=values,
    )


def initial_field(*, coupling_rate: float = 0.25):
    reference = source((0.0, 0.0), 0)
    field = build_shared_mcm_field(
        (reference,),
        {
            "visual": ReceptorDockAnatomy(
                modality_id="visual",
                dock_id="dock.visual",
                positions=((0, 0), (0, 1)),
            )
        },
        sample_offsets=OFFSETS,
    )
    contract = MCMLocalDevelopmentContract(
        equation_id=EQUATION_ID,
        capacity_ratio=8.0,
        coupling_rate_per_second=coupling_rate,
    )
    return attach_zero_mcm_local_development(field, contract)


def distribution(
    values: tuple[float, float] | None,
    start_tick: int,
    end_tick: int,
    snapshot: int,
) -> ReceptorDistribution:
    distributor = ReceptorDistributor()
    distributor.attach(
        ReceptorDock("dock.visual", "visual", "visual.s1b.v1")
    )
    frames = () if values is None else (source(values, snapshot),)
    return distributor.distribute(
        frames,
        CommonFieldTime("organism.s1b", start_tick, end_tick),
    )


def step(start_tick: int, end_tick: int) -> MCMFieldStepTime:
    return MCMFieldStepTime(
        clock_id="organism.s1b",
        start_tick=start_tick,
        end_tick=end_tick,
        ticks_per_second=1000.0,
    )


def advance(field, values, start_tick, end_tick, snapshot):
    return advance_s1b_reciprocal_shared_field(
        field,
        distribution(values, start_tick, end_tick, snapshot),
        step(start_tick, end_tick),
        FIELD_CONFIG,
        AFTERIMAGE_CONFIG,
    )


def vectors(field) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return (
        np.asarray(
            [item.activation for item in field.layer.neurons],
            dtype=np.float64,
        ),
        np.asarray(
            [item.afterimage for item in field.layer.neurons],
            dtype=np.float64,
        ),
        np.asarray(field.development.dispositions, dtype=np.float64),
    )


class S1BReciprocalAccommodationTests(unittest.TestCase):
    def test_schema_three_roundtrip_carries_complete_l_state(self) -> None:
        field = advance(initial_field(), (0.8, -0.4), 0, 1000, 1)
        snapshot = field.snapshot()
        restored = restore_shared_mcm_field(
            SharedMCMFieldSnapshot.from_json(snapshot.to_json())
        )

        self.assertEqual(3, snapshot.schema_version)
        self.assertIsNone(snapshot.substrate)
        self.assertIsNotNone(snapshot.development)
        self.assertEqual(snapshot.digest(), restored.snapshot().digest())
        self.assertEqual(
            snapshot.fast_state_projection_payload(),
            restored.snapshot().fast_state_projection_payload(),
        )

    def test_null_arm_reproduces_the_existing_fast_path_exactly(self) -> None:
        base = initial_field(coupling_rate=0.0)
        plain = build_shared_mcm_field(
            (source((0.0, 0.0), 0),),
            {
                "visual": ReceptorDockAnatomy(
                    "visual",
                    "dock.visual",
                    ((0, 0), (0, 1)),
                )
            },
            sample_offsets=OFFSETS,
        )
        current_distribution = distribution((0.7, -0.2), 0, 1000, 1)
        current_step = step(0, 1000)
        expected = advance_neutral_fast_shared_field(
            plain,
            current_distribution,
            current_step,
            FIELD_CONFIG,
            AFTERIMAGE_CONFIG,
        )
        actual = advance_s1b_reciprocal_shared_field(
            base,
            current_distribution,
            current_step,
            FIELD_CONFIG,
            AFTERIMAGE_CONFIG,
        )

        self.assertEqual(
            expected.snapshot().digest(),
            actual.snapshot().fast_state_projection_digest(),
        )
        self.assertEqual((0.0, 0.0), actual.development.dispositions)

    def test_isolated_exchange_closes_the_capacity_weighted_balance(self) -> None:
        seeded = advance(initial_field(), (0.6, 0.6), 0, 1000, 1)
        before_s, _, before_l = vectors(seeded)
        relaxed = advance(seeded, None, 1000, 2000, 2)
        after_s, _, after_l = vectors(relaxed)
        rho = seeded.development.contract.capacity_ratio

        np.testing.assert_allclose(
            before_s + rho * before_l,
            after_s + rho * after_l,
            rtol=0.0,
            atol=2e-13,
        )
        self.assertTrue(np.all(np.abs(after_l - before_l) < np.abs(after_s - before_s)))

    def test_constant_generator_is_invariant_to_time_partition(self) -> None:
        whole = advance(initial_field(), (0.5, -0.25), 0, 1000, 1)
        split = advance(initial_field(), (0.5, -0.25), 0, 500, 1)
        split = advance(split, (0.5, -0.25), 500, 1000, 2)

        for whole_values, split_values in zip(vectors(whole), vectors(split), strict=True):
            np.testing.assert_allclose(
                whole_values,
                split_values,
                rtol=0.0,
                atol=2e-13,
            )

    def test_observer_cannot_change_the_integrated_state(self) -> None:
        observed = []

        def observer(tick, activation, afterimage, local):
            observed.append((tick, activation.copy(), afterimage.copy(), local.copy()))
            activation[:] = 99.0
            afterimage[:] = 99.0
            local[:] = 99.0

        current_distribution = distribution((0.2, 0.9), 0, 1000, 1)
        current_step = step(0, 1000)
        expected = advance_s1b_reciprocal_shared_field(
            initial_field(),
            current_distribution,
            current_step,
            FIELD_CONFIG,
            AFTERIMAGE_CONFIG,
        )
        actual = advance_s1b_reciprocal_shared_field(
            initial_field(),
            current_distribution,
            current_step,
            FIELD_CONFIG,
            AFTERIMAGE_CONFIG,
            observer=observer,
        )

        self.assertEqual(1, len(observed))
        for expected_values, actual_values in zip(vectors(expected), vectors(actual), strict=True):
            np.testing.assert_array_equal(expected_values, actual_values)

    def test_swap_and_neutralization_change_only_l(self) -> None:
        first = advance(initial_field(), (0.8, 0.1), 0, 1000, 1)
        second = advance(initial_field(), (-0.3, -0.7), 0, 1000, 1)
        first_fast = first.snapshot().fast_state_projection_payload()
        second_fast = second.snapshot().fast_state_projection_payload()
        swapped_first, swapped_second = swap_mcm_local_development(first, second)

        self.assertEqual(second.development, swapped_first.development)
        self.assertEqual(first.development, swapped_second.development)
        self.assertEqual(first_fast, swapped_first.snapshot().fast_state_projection_payload())
        self.assertEqual(second_fast, swapped_second.snapshot().fast_state_projection_payload())

        neutral = neutralize_mcm_local_development(first)
        self.assertEqual((0.0, 0.0), neutral.development.dispositions)
        self.assertEqual(first_fast, neutral.snapshot().fast_state_projection_payload())

    def test_generic_advance_and_m_l_coexistence_are_rejected(self) -> None:
        field = initial_field()
        with self.assertRaisesRegex(SharedMCMFieldError, "dedicated S1-B"):
            field.advance(
                distribution((0.1, 0.2), 0, 1000, 1),
                receptor_projection_baseline,
            )
        with self.assertRaisesRegex(SharedMCMFieldError, "keeps M and L"):
            attach_uniform_mcm_substrate(
                field,
                MCMSubstrateArmContract("m.null", 0.0, 0.0, 0.0),
            )

    def test_schema_three_rejects_hidden_or_out_of_range_development(self) -> None:
        payload = json.loads(
            advance(initial_field(), (0.2, 0.4), 0, 1000, 1)
            .snapshot()
            .to_json()
        )
        payload["development"]["raw_frames"] = []
        with self.assertRaisesRegex(SharedMCMFieldError, "unknown"):
            SharedMCMFieldSnapshot.from_json(json.dumps(payload))

        payload = json.loads(
            advance(initial_field(), (0.2, 0.4), 0, 1000, 1)
            .snapshot()
            .to_json()
        )
        payload["development"]["values"][0]["value"] = 1.1
        with self.assertRaisesRegex(SharedMCMFieldError, "-1..1"):
            SharedMCMFieldSnapshot.from_json(json.dumps(payload))

    def test_replacement_rejects_contract_change(self) -> None:
        first = advance(initial_field(), (0.5, 0.5), 0, 1000, 1)
        second = advance(
            initial_field(coupling_rate=0.5),
            (0.5, 0.5),
            0,
            1000,
            1,
        )
        with self.assertRaises(S1BReciprocalAccommodationError):
            swap_mcm_local_development(first, second)


if __name__ == "__main__":
    unittest.main()
