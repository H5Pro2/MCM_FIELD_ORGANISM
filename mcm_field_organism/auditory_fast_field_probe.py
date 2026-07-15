"""Passive B1-exact projection for a minimal auditory fast-field candidate."""

from __future__ import annotations

import math
from typing import Iterable

from .broadband_hearing_path import AuditoryReceptorContact, AuditoryReceptorState
from .carrier_baselines import BaselineValidationError, run_independent_history
from .mcm_distributor import MCMFieldWindow


class AuditoryFastFieldProjectionError(ValueError):
    """Raised when a receptor history violates the passive probe contract."""


def _validated_states(
    states: Iterable[AuditoryReceptorState],
) -> tuple[AuditoryReceptorState, ...]:
    history = tuple(states)
    if not history:
        raise AuditoryFastFieldProjectionError("receptor history cannot be empty")

    first = history[0]
    if first.modality_id != "auditory":
        raise AuditoryFastFieldProjectionError("all receptor states must be auditory")
    if first.snapshot_index < 0:
        raise AuditoryFastFieldProjectionError("snapshot indices must be non-negative")
    if not first.carrier_ids:
        raise AuditoryFastFieldProjectionError("receptor history requires local carriers")

    previous = None
    for offset, state in enumerate(history):
        if state.modality_id != "auditory":
            raise AuditoryFastFieldProjectionError("all receptor states must be auditory")
        if state.geometry_id != first.geometry_id or state.carrier_ids != first.carrier_ids:
            raise AuditoryFastFieldProjectionError(
                "geometry and carrier identity must remain stable within one history"
            )
        if state.snapshot_index != first.snapshot_index + offset:
            raise AuditoryFastFieldProjectionError("snapshot indices must be consecutive")
        if (
            state.window_start_sample < 0
            or state.window_end_sample <= state.window_start_sample
        ):
            raise AuditoryFastFieldProjectionError("sample windows must be positive intervals")
        if previous is not None:
            if state.window_start_sample <= previous.window_start_sample:
                raise AuditoryFastFieldProjectionError("sample windows must advance")
            if state.window_end_sample <= previous.window_end_sample:
                raise AuditoryFastFieldProjectionError("sample windows must advance")
        if len(state.energy) != len(first.carrier_ids):
            raise AuditoryFastFieldProjectionError("energy must match carrier geometry")
        if any(not math.isfinite(value) or value < 0.0 or value > 1.0 for value in state.energy):
            raise AuditoryFastFieldProjectionError(
                "controlled receptor energy must stay within the finite 0..1 probe domain"
            )
        expected_contact = (
            AuditoryReceptorContact.ACTIVE_ENERGY
            if any(value != 0.0 for value in state.energy)
            else AuditoryReceptorContact.ACTIVE_ZERO
        )
        if state.contact is not expected_contact:
            raise AuditoryFastFieldProjectionError(
                "contact state must match exact receptor-energy zero status"
            )
        previous = state
    return history


def project_auditory_fast_field_candidate(
    states: Iterable[AuditoryReceptorState],
    *,
    dt: float,
    tau: float,
) -> tuple[MCMFieldWindow, ...]:
    """Project a finite receptor history without adding cross-carrier effects."""

    history = _validated_states(states)
    try:
        baseline = run_independent_history(
            (state.energy for state in history),
            dt=dt,
            tau=tau,
        )
    except BaselineValidationError as exc:
        raise AuditoryFastFieldProjectionError(str(exc)) from exc

    return tuple(
        MCMFieldWindow(
            dock_id="auditory",
            modality_id="auditory",
            field_id="auditory.fast_candidate",
            geometry_id=state.geometry_id,
            snapshot_id=f"auditory.fast.{state.snapshot_index}",
            clock_id="audio.sample",
            window_start_tick=state.window_start_sample,
            window_end_tick=state.window_end_sample,
            carrier_ids=state.carrier_ids,
            activation=state.energy,
            afterimage=frame.afterimage,
        )
        for state, frame in zip(history, baseline, strict=True)
    )
