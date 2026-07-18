from __future__ import annotations

import math
import unittest

import numpy as np

from mcm_field_organism import (
    CommonFieldTime,
    MCMFieldStepTime,
    NeutralLocalFieldSubstrateConfig,
    NeutralLocalFieldSubstrateError,
    ReceptorContactFrame,
    ReceptorDistributor,
    ReceptorDock,
    ReceptorDockAnatomy,
    advance_neutral_shared_field,
    build_shared_mcm_field,
    restore_shared_mcm_field,
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


def shared_field(size: int = 3):
    reference = receptor_frame(
        "auditory.reference",
        tuple(0.0 for _ in range(size)),
    )
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
):
    distributor = ReceptorDistributor()
    distributor.attach(
        ReceptorDock(
            "dock.auditory",
            "auditory",
            "auditory.line.v1",
        )
    )
    frames = () if values is None else (receptor_frame(snapshot_id, values),)
    return distributor.distribute(
        frames,
        CommonFieldTime("organism.test", start_tick, end_tick),
    )


def step_time(start_tick: int, end_tick: int) -> MCMFieldStepTime:
    return MCMFieldStepTime(
        "organism.test",
        start_tick,
        end_tick,
        10.0,
    )


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


class NeutralLocalFieldSubstrateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = NeutralLocalFieldSubstrateConfig(1.0)

    def test_configuration_requires_one_explicit_positive_time_scale(self) -> None:
        for value in (0.0, -1.0, math.inf, math.nan):
            with self.subTest(value=value), self.assertRaises(
                NeutralLocalFieldSubstrateError
            ):
                NeutralLocalFieldSubstrateConfig(value)

    def test_world_contact_enters_and_spreads_through_local_adjacency(self) -> None:
        result = advance_neutral_shared_field(
            shared_field(),
            distribution(0, 10, "contact", (1.0, 0.0, 0.0)),
            step_time(0, 10),
            self.config,
        )
        values = activation(result)
        self.assertGreater(values[0], values[1])
        self.assertGreater(values[1], values[2])
        self.assertGreater(values[2], 0.0)
        self.assertTrue(np.all(values <= 1.0))
        self.assertTrue(np.all(values >= -1.0))

    def test_absence_is_not_converted_to_measured_zero_contact(self) -> None:
        seeded = advance_neutral_shared_field(
            shared_field(),
            distribution(0, 10, "seed", (0.4, 0.4, 0.4)),
            step_time(0, 10),
            self.config,
        )
        absent = advance_neutral_shared_field(
            seeded,
            distribution(10, 20, "absent", None),
            step_time(10, 20),
            self.config,
        )
        measured_zero = advance_neutral_shared_field(
            seeded,
            distribution(10, 20, "zero", (0.0, 0.0, 0.0)),
            step_time(10, 20),
            self.config,
        )
        np.testing.assert_allclose(
            activation(absent),
            activation(seeded),
            rtol=0.0,
            atol=1e-14,
        )
        self.assertTrue(np.all(activation(measured_zero) < activation(absent)))

    def test_spatial_dynamics_are_invariant_to_observation_partition(self) -> None:
        seeded = advance_neutral_shared_field(
            shared_field(),
            distribution(0, 10, "seed", (1.0, 0.0, -1.0)),
            step_time(0, 10),
            self.config,
        )
        coarse = advance_neutral_shared_field(
            seeded,
            distribution(10, 20, "coarse", (0.2, 0.2, 0.2)),
            step_time(10, 20),
            self.config,
        )
        fine = advance_neutral_shared_field(
            seeded,
            distribution(10, 15, "fine.1", (0.2, 0.2, 0.2)),
            step_time(10, 15),
            self.config,
        )
        fine = advance_neutral_shared_field(
            fine,
            distribution(15, 20, "fine.2", (0.2, 0.2, 0.2)),
            step_time(15, 20),
            self.config,
        )
        np.testing.assert_allclose(
            activation(coarse),
            activation(fine),
            rtol=0.0,
            atol=2e-15,
        )

    def test_snapshot_resume_recreates_the_same_next_field(self) -> None:
        first = advance_neutral_shared_field(
            shared_field(),
            distribution(0, 10, "first", (1.0, 0.0, -1.0)),
            step_time(0, 10),
            self.config,
        )
        restored = restore_shared_mcm_field(first.snapshot())
        next_distribution = distribution(10, 20, "next", (0.1, 0.2, 0.3))
        uninterrupted = advance_neutral_shared_field(
            first,
            next_distribution,
            step_time(10, 20),
            self.config,
        )
        resumed = advance_neutral_shared_field(
            restored,
            next_distribution,
            step_time(10, 20),
            NeutralLocalFieldSubstrateConfig(1.0),
        )
        self.assertEqual(
            uninterrupted.snapshot().digest(),
            resumed.snapshot().digest(),
        )

    def test_larger_field_preserves_mirror_symmetry(self) -> None:
        size = 16
        left_contact = (1.0,) + tuple(0.0 for _ in range(size - 1))
        right_contact = tuple(reversed(left_contact))
        left = advance_neutral_shared_field(
            shared_field(size),
            distribution(0, 10, "left", left_contact),
            step_time(0, 10),
            self.config,
        )
        right = advance_neutral_shared_field(
            shared_field(size),
            distribution(0, 10, "right", right_contact),
            step_time(0, 10),
            self.config,
        )
        np.testing.assert_allclose(
            activation(left),
            activation(right)[::-1],
            rtol=0.0,
            atol=2e-15,
        )

    def test_contact_free_diffusion_conserves_mean_and_reduces_spread(self) -> None:
        seeded = advance_neutral_shared_field(
            shared_field(),
            distribution(0, 10, "seed", (1.0, 0.0, -1.0)),
            step_time(0, 10),
            self.config,
        )
        relaxed = advance_neutral_shared_field(
            seeded,
            distribution(10, 20, "absent", None),
            step_time(10, 20),
            self.config,
        )
        self.assertAlmostEqual(
            float(np.mean(activation(seeded))),
            float(np.mean(activation(relaxed))),
            places=15,
        )
        self.assertLess(
            float(np.var(activation(relaxed))),
            float(np.var(activation(seeded))),
        )

    def test_field_step_must_match_distribution_time(self) -> None:
        with self.assertRaisesRegex(
            NeutralLocalFieldSubstrateError,
            "must match",
        ):
            advance_neutral_shared_field(
                shared_field(),
                distribution(0, 10, "contact", (0.0, 0.0, 0.0)),
                step_time(0, 9),
                self.config,
            )


if __name__ == "__main__":
    unittest.main()
