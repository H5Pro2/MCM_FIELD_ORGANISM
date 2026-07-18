from __future__ import annotations

import math
import unittest

from mcm_field_organism import (
    CommonFieldTime,
    MCMFieldStepTime,
    NeutralLocalFieldSubstrateConfig,
    NeutralLocalFieldSubstrateError,
    PassiveLocalDrive,
    PassiveLocalFieldSample,
    PassivePreviousLocalState,
    ReceptorContactFrame,
    ReceptorDistributor,
    ReceptorDock,
    ReceptorDockAnatomy,
    SharedMCMFieldError,
    build_shared_mcm_field,
    make_neutral_local_field_transition,
    neutral_local_field_substrate_step,
    restore_shared_mcm_field,
)


def local_drive(
    *,
    activation: float = 0.2,
    afterimage: float = -0.1,
    contact: float | None = 0.4,
    sample_values: tuple[float, ...] = (0.8,),
    elapsed_seconds: float = 1.0,
) -> PassiveLocalDrive:
    return PassiveLocalDrive(
        previous_state=PassivePreviousLocalState(activation, afterimage),
        receptor_contact=contact,
        local_field_samples=tuple(
            PassiveLocalFieldSample((index + 1,), value, 0.0)
            for index, value in enumerate(sample_values)
        ),
        elapsed_seconds=elapsed_seconds,
        transient_receptor_history=None,
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


def shared_field():
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
    frame: ReceptorContactFrame | None,
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
        () if frame is None else (frame,),
        CommonFieldTime("organism.test", start_tick, end_tick),
    )


def step_time(start_tick: int, end_tick: int) -> MCMFieldStepTime:
    return MCMFieldStepTime(
        "organism.test",
        start_tick,
        end_tick,
        10.0,
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

    def test_world_contact_and_local_field_are_separately_causal(self) -> None:
        full = neutral_local_field_substrate_step(
            local_drive(),
            self.config,
        )
        no_world = neutral_local_field_substrate_step(
            local_drive(contact=None),
            self.config,
        )
        no_field = neutral_local_field_substrate_step(
            local_drive(sample_values=()),
            self.config,
        )
        self.assertNotEqual(full.activation, no_world.activation)
        self.assertNotEqual(full.activation, no_field.activation)
        self.assertEqual(-0.1, full.afterimage)

    def test_absence_is_not_converted_to_zero_contact(self) -> None:
        absent = neutral_local_field_substrate_step(
            local_drive(
                activation=0.4,
                contact=None,
                sample_values=(0.4,),
            ),
            self.config,
        )
        measured_zero = neutral_local_field_substrate_step(
            local_drive(
                activation=0.4,
                contact=0.0,
                sample_values=(0.4,),
            ),
            self.config,
        )
        self.assertAlmostEqual(0.4, absent.activation)
        self.assertLess(measured_zero.activation, absent.activation)

    def test_static_local_target_composes_over_elapsed_time(self) -> None:
        complete = neutral_local_field_substrate_step(
            local_drive(elapsed_seconds=1.0),
            self.config,
        )
        first = neutral_local_field_substrate_step(
            local_drive(elapsed_seconds=0.4),
            self.config,
        )
        second = neutral_local_field_substrate_step(
            local_drive(
                activation=first.activation,
                afterimage=first.afterimage,
                elapsed_seconds=0.6,
            ),
            self.config,
        )
        self.assertAlmostEqual(complete.activation, second.activation, places=15)
        self.assertEqual(complete.afterimage, second.afterimage)

    def test_shared_field_accepts_explicit_step_time_and_resumes_exactly(self) -> None:
        transition = make_neutral_local_field_transition(self.config)
        first_distribution = distribution(
            0,
            10,
            receptor_frame("auditory.contact.1", (1.0, 0.0, -1.0)),
        )
        first = shared_field().advance(
            first_distribution,
            transition,
            step_time=step_time(0, 10),
        )
        expected_edge = 0.5 * (1.0 - math.exp(-1.0))
        self.assertAlmostEqual(
            expected_edge,
            first.layer.neurons[0].activation,
        )
        self.assertAlmostEqual(
            -expected_edge,
            first.layer.neurons[-1].activation,
        )

        snapshot = first.snapshot()
        restored = restore_shared_mcm_field(snapshot)
        empty_distribution = distribution(10, 20, None)
        uninterrupted = first.advance(
            empty_distribution,
            transition,
            step_time=step_time(10, 20),
        )
        resumed = restored.advance(
            empty_distribution,
            make_neutral_local_field_transition(self.config),
            step_time=step_time(10, 20),
        )
        self.assertEqual(
            uninterrupted.snapshot().digest(),
            resumed.snapshot().digest(),
        )

    def test_shared_field_rejects_mismatched_explicit_step_time(self) -> None:
        with self.assertRaisesRegex(
            SharedMCMFieldError,
            "must match",
        ):
            shared_field().advance(
                distribution(
                    0,
                    10,
                    receptor_frame("auditory.contact.1", (0.0, 0.0, 0.0)),
                ),
                make_neutral_local_field_transition(self.config),
                step_time=step_time(0, 9),
            )


if __name__ == "__main__":
    unittest.main()
