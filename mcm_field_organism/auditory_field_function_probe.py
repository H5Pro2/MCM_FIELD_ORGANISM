"""Passive baseline probe before the auditory MCM field boundary."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

from .carrier_baselines import (
    BaselineValidationError,
    decay_factor,
    run_independent_history,
    stateless_baseline,
)


AuditoryContact = tuple[float, float]
AuditoryHistory = tuple[AuditoryContact, ...]


@dataclass(frozen=True, slots=True)
class AuditoryFieldFunctionProbeResult:
    """Collision profile of two compensated two-carrier histories."""

    decay: float
    forward_history: AuditoryHistory
    reverse_history: AuditoryHistory
    current_contact_equal: bool
    stateless_equal: bool
    independent_leaky_equal: bool
    global_energy_chronology_equal: bool
    fixed_one_step_delay_equal: bool


def _two_carrier_contact(values: Iterable[float], role: str) -> AuditoryContact:
    try:
        contact = tuple(float(value) for value in values)
    except (TypeError, ValueError) as exc:
        raise BaselineValidationError(f"{role} must contain numeric values") from exc
    if len(contact) != 2:
        raise BaselineValidationError(f"{role} must contain exactly two carriers")
    if any(not math.isfinite(value) for value in contact):
        raise BaselineValidationError(f"{role} must contain only finite values")
    if any(value < 0.0 or value > 1.0 for value in contact):
        raise BaselineValidationError(f"{role} must stay within the normalized 0..1 probe domain")
    return contact[0], contact[1]


def compensated_transition_histories(
    *,
    dt: float,
    tau: float,
    common_probe: Iterable[float] = (0.25, 0.25),
) -> tuple[AuditoryHistory, AuditoryHistory]:
    """Build reversed transitions with equal independent leaky endpoints."""

    probe = _two_carrier_contact(common_probe, "common_probe")
    decay = decay_factor(dt=dt, tau=tau)
    forward = ((1.0, 0.0), (0.0, decay), probe)
    reverse = ((0.0, 1.0), (decay, 0.0), probe)
    return forward, reverse


def run_auditory_field_function_probe(
    *,
    dt: float,
    tau: float,
    common_probe: Iterable[float] = (0.25, 0.25),
) -> AuditoryFieldFunctionProbeResult:
    """Compare a candidate temporal distinction against fixed baselines."""

    forward, reverse = compensated_transition_histories(
        dt=dt,
        tau=tau,
        common_probe=common_probe,
    )
    forward_leaky = run_independent_history(forward, dt=dt, tau=tau)[-1]
    reverse_leaky = run_independent_history(reverse, dt=dt, tau=tau)[-1]
    forward_stateless = stateless_baseline(forward[-1])
    reverse_stateless = stateless_baseline(reverse[-1])

    return AuditoryFieldFunctionProbeResult(
        decay=decay_factor(dt=dt, tau=tau),
        forward_history=forward,
        reverse_history=reverse,
        current_contact_equal=forward[-1] == reverse[-1],
        stateless_equal=forward_stateless == reverse_stateless,
        independent_leaky_equal=forward_leaky == reverse_leaky,
        global_energy_chronology_equal=(
            tuple(sum(frame) for frame in forward)
            == tuple(sum(frame) for frame in reverse)
        ),
        fixed_one_step_delay_equal=forward[-2] == reverse[-2],
    )
