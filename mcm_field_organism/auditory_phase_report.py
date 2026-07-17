"""Historical reporting for controlled auditory separate-field phases."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
import re
from statistics import fmean
from typing import Iterable

from .broadband_hearing_path import AuditoryReceptorContact, AuditoryReceptorState
from .mcm_distributor import MCMFieldWindow


class AuditoryPhaseReportError(ValueError):
    """Raised when receptor and field layers cannot be reported causally."""


class AudioGateMode(str, Enum):
    PASS = "pass"
    MUTE = "mute"


_PHASE_ID = re.compile(r"^[a-z][a-z0-9_.-]*$")


@dataclass(frozen=True, slots=True)
class AuditoryPhaseLayerReport:
    phase_id: str
    gate_mode: AudioGateMode
    gate_output_exact_zero: bool
    total_states: int
    transition_states: int
    stable_states: int
    transition_mean_receptor_energy: float
    stable_mean_receptor_energy: float
    stable_active_zero_count: int
    stable_receptor_exact_zero: bool
    phase_mean_field_afterimage: float
    stable_mean_field_afterimage: float
    final_field_afterimage: float


def _mean_total(vectors: Iterable[tuple[float, ...]]) -> float:
    totals = tuple(sum(vector) for vector in vectors)
    return fmean(totals) if totals else 0.0


def summarize_auditory_phase_layers(
    *,
    phase_id: str,
    gate_mode: AudioGateMode,
    gate_output_exact_zero: bool,
    receptor_states: Iterable[AuditoryReceptorState],
    field_windows: Iterable[MCMFieldWindow],
    transition_state_count: int,
) -> AuditoryPhaseLayerReport:
    """Separate gate input, receptor-window transition, and field afterimage."""

    if not isinstance(phase_id, str) or not _PHASE_ID.fullmatch(phase_id):
        raise AuditoryPhaseReportError("phase_id must be a lowercase technical identifier")
    try:
        mode = AudioGateMode(gate_mode)
    except (TypeError, ValueError) as exc:
        raise AuditoryPhaseReportError("unknown gate mode") from exc
    if not isinstance(gate_output_exact_zero, bool):
        raise AuditoryPhaseReportError("gate_output_exact_zero must be boolean")
    if isinstance(transition_state_count, bool) or not isinstance(transition_state_count, int):
        raise AuditoryPhaseReportError("transition_state_count must be an integer")

    states = tuple(receptor_states)
    windows = tuple(field_windows)
    if not states or len(states) != len(windows):
        raise AuditoryPhaseReportError("receptor states and field windows must be non-empty and aligned")
    if transition_state_count < 0 or transition_state_count >= len(states):
        raise AuditoryPhaseReportError("transition_state_count must leave at least one stable state")

    for state, window in zip(states, windows, strict=True):
        if state.modality_id != "auditory" or window.modality_id != "auditory":
            raise AuditoryPhaseReportError("phase report accepts only auditory layers")
        if state.geometry_id != window.geometry_id or state.carrier_ids != window.carrier_ids:
            raise AuditoryPhaseReportError("receptor and field geometry must match")
        if state.energy != window.activation:
            raise AuditoryPhaseReportError("field activation must preserve its current receptor state")
        if any(not math.isfinite(value) for value in window.afterimage):
            raise AuditoryPhaseReportError("field afterimage must contain finite values")

    transition = states[:transition_state_count]
    stable = states[transition_state_count:]
    stable_windows = windows[transition_state_count:]
    stable_zero_count = sum(
        state.contact is AuditoryReceptorContact.ACTIVE_ZERO for state in stable
    )
    stable_exact_zero = all(
        state.contact is AuditoryReceptorContact.ACTIVE_ZERO
        and all(value == 0.0 for value in state.energy)
        for state in stable
    )

    return AuditoryPhaseLayerReport(
        phase_id=phase_id,
        gate_mode=mode,
        gate_output_exact_zero=gate_output_exact_zero,
        total_states=len(states),
        transition_states=len(transition),
        stable_states=len(stable),
        transition_mean_receptor_energy=_mean_total(state.energy for state in transition),
        stable_mean_receptor_energy=_mean_total(state.energy for state in stable),
        stable_active_zero_count=stable_zero_count,
        stable_receptor_exact_zero=stable_exact_zero,
        phase_mean_field_afterimage=_mean_total(window.afterimage for window in windows),
        stable_mean_field_afterimage=_mean_total(
            window.afterimage for window in stable_windows
        ),
        final_field_afterimage=sum(windows[-1].afterimage),
    )
