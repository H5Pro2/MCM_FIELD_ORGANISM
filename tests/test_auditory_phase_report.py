from __future__ import annotations

from dataclasses import fields
import unittest

from mcm_field_organism import (
    AuditoryReceptorContact,
    AuditoryReceptorState,
)
from mcm_field_organism.auditory_phase_report import (
    AudioGateMode,
    AuditoryPhaseLayerReport,
    AuditoryPhaseReportError,
    summarize_auditory_phase_layers,
)
from mcm_field_organism.mcm_distributor import MCMFieldWindow


CARRIERS = ("band.0", "band.1")
GEOMETRY = "auditory.report.v1"


def receptor(index: int, energy: tuple[float, float]) -> AuditoryReceptorState:
    return AuditoryReceptorState(
        modality_id="auditory",
        geometry_id=GEOMETRY,
        snapshot_index=index,
        window_start_sample=index * 480,
        window_end_sample=(index * 480) + 4800,
        carrier_ids=CARRIERS,
        energy=energy,
        contact=(
            AuditoryReceptorContact.ACTIVE_ENERGY
            if any(value != 0.0 for value in energy)
            else AuditoryReceptorContact.ACTIVE_ZERO
        ),
    )


def field(index: int, activation: tuple[float, float], afterimage: tuple[float, float]) -> MCMFieldWindow:
    return MCMFieldWindow(
        dock_id="auditory",
        modality_id="auditory",
        field_id="auditory.fast_candidate",
        geometry_id=GEOMETRY,
        snapshot_id=f"auditory.fast.{index}",
        clock_id="audio.sample",
        window_start_tick=index * 480,
        window_end_tick=(index * 480) + 4800,
        carrier_ids=CARRIERS,
        activation=activation,
        afterimage=afterimage,
    )


class AuditoryPhaseReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.states = (
            receptor(0, (0.4, 0.2)),
            receptor(1, (0.0, 0.0)),
            receptor(2, (0.0, 0.0)),
            receptor(3, (0.0, 0.0)),
        )
        self.windows = (
            field(0, (0.4, 0.2), (0.5, 0.25)),
            field(1, (0.0, 0.0), (0.2, 0.1)),
            field(2, (0.0, 0.0), (0.08, 0.04)),
            field(3, (0.0, 0.0), (0.032, 0.016)),
        )

    def test_mute_report_separates_transition_stable_receptor_and_afterimage(self) -> None:
        report = summarize_auditory_phase_layers(
            phase_id="mute",
            gate_mode=AudioGateMode.MUTE,
            gate_output_exact_zero=True,
            receptor_states=self.states,
            field_windows=self.windows,
            transition_state_count=1,
        )
        self.assertEqual(1, report.transition_states)
        self.assertEqual(3, report.stable_states)
        self.assertAlmostEqual(0.6, report.transition_mean_receptor_energy)
        self.assertEqual(0.0, report.stable_mean_receptor_energy)
        self.assertEqual(3, report.stable_active_zero_count)
        self.assertTrue(report.stable_receptor_exact_zero)
        self.assertGreater(report.stable_mean_field_afterimage, 0.0)
        self.assertAlmostEqual(0.048, report.final_field_afterimage)

    def test_report_has_no_combined_mute_receptor_mean_role(self) -> None:
        roles = {item.name for item in fields(AuditoryPhaseLayerReport)}
        self.assertNotIn("phase_mean_receptor_energy", roles)
        self.assertIn("transition_mean_receptor_energy", roles)
        self.assertIn("stable_mean_receptor_energy", roles)

    def test_pass_phase_may_observe_an_exactly_silent_source(self) -> None:
        silent_states = self.states[1:]
        silent_windows = self.windows[1:]
        report = summarize_auditory_phase_layers(
            phase_id="silent_pass",
            gate_mode=AudioGateMode.PASS,
            gate_output_exact_zero=True,
            receptor_states=silent_states,
            field_windows=silent_windows,
            transition_state_count=0,
        )
        self.assertTrue(report.gate_output_exact_zero)
        self.assertTrue(report.stable_receptor_exact_zero)

    def test_layer_mismatch_is_rejected(self) -> None:
        mismatched = list(self.windows)
        mismatched[-1] = field(3, (0.1, 0.0), (0.032, 0.016))
        with self.assertRaises(AuditoryPhaseReportError):
            summarize_auditory_phase_layers(
                phase_id="mute",
                gate_mode=AudioGateMode.MUTE,
                gate_output_exact_zero=True,
                receptor_states=self.states,
                field_windows=mismatched,
                transition_state_count=1,
            )

    def test_invalid_phase_contracts_are_rejected(self) -> None:
        invalid = (
            {"phase_id": "Mute Phase", "gate_mode": AudioGateMode.MUTE, "gate_output_exact_zero": True, "transition_state_count": 1},
            {"phase_id": "mute", "gate_mode": AudioGateMode.MUTE, "gate_output_exact_zero": True, "transition_state_count": 4},
        )
        for arguments in invalid:
            with self.assertRaises(AuditoryPhaseReportError):
                summarize_auditory_phase_layers(
                    receptor_states=self.states,
                    field_windows=self.windows,
                    **arguments,
                )


if __name__ == "__main__":
    unittest.main()
