from __future__ import annotations

import math
import unittest

from mcm_field_organism import (
    AuditoryReceptorContact,
    AuditoryReceptorState,
    BroadbandHearingPath,
    LogSpectralConfig,
    LogSpectralReceptor,
    run_independent_history,
)
from mcm_field_organism.auditory_fast_field_probe import (
    AuditoryFastFieldProjectionError,
    project_auditory_fast_field_candidate,
)
from mcm_field_organism.mcm_distributor import MCMDock, MCMDistributor


def receptor_state(
    index: int,
    energy: tuple[float, ...],
    *,
    geometry_id: str = "auditory.test.v1",
    carrier_ids: tuple[str, ...] = ("band.0", "band.1", "band.2"),
) -> AuditoryReceptorState:
    return AuditoryReceptorState(
        modality_id="auditory",
        geometry_id=geometry_id,
        snapshot_index=index,
        window_start_sample=index * 480,
        window_end_sample=(index * 480) + 4800,
        carrier_ids=carrier_ids,
        energy=energy,
        contact=(
            AuditoryReceptorContact.ACTIVE_ENERGY
            if any(value != 0.0 for value in energy)
            else AuditoryReceptorContact.ACTIVE_ZERO
        ),
    )


class AuditoryFastFieldProbeTests(unittest.TestCase):
    def test_projection_is_exactly_the_independent_b1_baseline(self) -> None:
        states = (
            receptor_state(0, (0.8, 0.0, 0.0)),
            receptor_state(1, (0.0, 0.4, 0.0)),
            receptor_state(2, (0.0, 0.0, 0.2)),
            receptor_state(3, (0.1, 0.1, 0.1)),
        )
        for dt, tau in ((0.01, 0.05), (0.02, 0.2), (0.1, 1.0)):
            projected = project_auditory_fast_field_candidate(states, dt=dt, tau=tau)
            baseline = run_independent_history(
                (state.energy for state in states),
                dt=dt,
                tau=tau,
            )
            self.assertEqual(
                tuple(window.afterimage for window in projected),
                tuple(frame.afterimage for frame in baseline),
            )

    def test_activation_preserves_the_current_distributed_receptor_lage(self) -> None:
        states = (
            receptor_state(0, (0.8, 0.1, 0.0)),
            receptor_state(1, (0.0, 0.3, 0.7)),
        )
        projected = project_auditory_fast_field_candidate(states, dt=0.01, tau=0.05)
        self.assertEqual(
            tuple(state.energy for state in states),
            tuple(window.activation for window in projected),
        )
        self.assertTrue(all(window.carrier_ids == states[0].carrier_ids for window in projected))

    def test_one_carrier_contact_never_spreads_to_another_carrier(self) -> None:
        states = tuple(
            receptor_state(index, energy)
            for index, energy in enumerate(
                ((1.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
            )
        )
        projected = project_auditory_fast_field_candidate(states, dt=0.01, tau=0.05)
        self.assertTrue(all(window.afterimage[1:] == (0.0, 0.0) for window in projected))
        self.assertGreater(projected[-1].afterimage[0], 0.0)

    def test_same_present_contact_can_carry_different_local_afterimage(self) -> None:
        left_history = (
            receptor_state(0, (1.0, 0.0, 0.0)),
            receptor_state(1, (0.2, 0.2, 0.2)),
        )
        right_history = (
            receptor_state(0, (0.0, 0.0, 1.0)),
            receptor_state(1, (0.2, 0.2, 0.2)),
        )
        left = project_auditory_fast_field_candidate(left_history, dt=0.01, tau=0.05)[-1]
        right = project_auditory_fast_field_candidate(right_history, dt=0.01, tau=0.05)[-1]
        self.assertEqual(left.activation, right.activation)
        self.assertNotEqual(left.afterimage, right.afterimage)

    def test_real_receptor_window_can_be_zero_while_b1_afterimage_remains(self) -> None:
        config = LogSpectralConfig(band_count=24)
        path = BroadbandHearingPath(LogSpectralReceptor(config))
        tone_chunk = tuple(
            0.5 * math.sin(2.0 * math.pi * 1000.0 * sample / config.sample_rate)
            for sample in range(config.hop_size)
        )
        states = []
        for chunk in (tone_chunk,) * 10 + ((0.0,) * config.hop_size,) * 10:
            state = path.push(chunk)
            if state is not None:
                states.append(state)
        self.assertEqual(AuditoryReceptorContact.ACTIVE_ZERO, states[-1].contact)
        projected = project_auditory_fast_field_candidate(states, dt=0.01, tau=0.05)
        self.assertEqual((0.0,) * config.band_count, projected[-1].activation)
        self.assertTrue(any(value > 0.0 for value in projected[-1].afterimage))

    def test_projection_is_pure_and_reproducible(self) -> None:
        states = (
            receptor_state(0, (0.2, 0.4, 0.6)),
            receptor_state(1, (0.6, 0.4, 0.2)),
        )
        first = project_auditory_fast_field_candidate(states, dt=0.01, tau=0.05)
        second = project_auditory_fast_field_candidate(states, dt=0.01, tau=0.05)
        self.assertEqual(tuple(item.digest() for item in first), tuple(item.digest() for item in second))

    def test_candidate_can_dock_without_rewriting_its_state(self) -> None:
        window = project_auditory_fast_field_candidate(
            (receptor_state(0, (0.2, 0.4, 0.6)),),
            dt=0.01,
            tau=0.05,
        )[0]
        distributor = MCMDistributor()
        distributor.attach(
            MCMDock(
                dock_id="auditory",
                modality_id="auditory",
                geometry_id=window.geometry_id,
                clock_id=window.clock_id,
            )
        )
        distributed = distributor.distribute((window,))
        self.assertEqual((window,), distributed.states)
        self.assertEqual(window.digest(), distributed.states[0].digest())

    def test_invalid_histories_are_rejected(self) -> None:
        valid = receptor_state(0, (0.2, 0.4, 0.6))
        invalid_histories = (
            (),
            (valid, receptor_state(2, (0.2, 0.4, 0.6))),
            (valid, receptor_state(1, (0.2, 0.4, 0.6), geometry_id="auditory.other.v1")),
            (receptor_state(0, (0.2, 1.1, 0.6)),),
            (receptor_state(0, (0.0, 0.0, 0.0)),),
        )
        mismatched_contact = invalid_histories[-1][0]
        mismatched_contact = AuditoryReceptorState(
            modality_id=mismatched_contact.modality_id,
            geometry_id=mismatched_contact.geometry_id,
            snapshot_index=mismatched_contact.snapshot_index,
            window_start_sample=mismatched_contact.window_start_sample,
            window_end_sample=mismatched_contact.window_end_sample,
            carrier_ids=mismatched_contact.carrier_ids,
            energy=mismatched_contact.energy,
            contact=AuditoryReceptorContact.ACTIVE_ENERGY,
        )
        for history in invalid_histories[:-1] + ((mismatched_contact,),):
            with self.assertRaises(AuditoryFastFieldProjectionError):
                project_auditory_fast_field_candidate(history, dt=0.01, tau=0.05)


if __name__ == "__main__":
    unittest.main()
