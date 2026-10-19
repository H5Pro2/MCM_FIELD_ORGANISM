"""Passive baselines for Methodik 002.

The functions in this module characterize simple known filters. They are not
MCM runtime mechanics and contain no carrier-to-carrier interaction.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable


class BaselineValidationError(ValueError):
    """Raised when a baseline probe is outside its declared technical domain."""


@dataclass(frozen=True, slots=True)
class CarrierFrame:
    """One passive baseline result for independent local carriers."""

    activation: tuple[float, ...]
    afterimage: tuple[float, ...]


def _unit_vector(values: Iterable[float], role: str) -> tuple[float, ...]:
    try:
        vector = tuple(float(value) for value in values)
    except (TypeError, ValueError) as exc:
        raise BaselineValidationError(f"{role} must contain numeric values") from exc
    if not vector:
        raise BaselineValidationError(f"{role} cannot be empty")
    if any(not math.isfinite(value) for value in vector):
        raise BaselineValidationError(f"{role} must contain only finite values")
    if any(abs(value) > 1.0 for value in vector):
        raise BaselineValidationError(f"{role} must stay within the normalized -1..1 probe domain")
    return vector


def decay_factor(*, dt: float, tau: float) -> float:
    """Return the exact first-order decay over one technical interval."""

    dt = float(dt)
    tau = float(tau)
    if not math.isfinite(dt) or dt <= 0.0:
        raise BaselineValidationError("dt must be finite and greater than zero")
    if not math.isfinite(tau) or tau <= 0.0:
        raise BaselineValidationError("tau must be finite and greater than zero")
    return math.exp(-dt / tau)


def stateless_baseline(contact: Iterable[float]) -> CarrierFrame:
    """B0: pass current contact through and retain no afterimage."""

    activation = _unit_vector(contact, "contact")
    return CarrierFrame(activation=activation, afterimage=(0.0,) * len(activation))


def independent_leaky_step(
    previous_afterimage: Iterable[float],
    contact: Iterable[float],
    *,
    dt: float,
    tau: float,
) -> CarrierFrame:
    """B1: advance independent first-order afterimages from one snapshot."""

    previous = _unit_vector(previous_afterimage, "previous_afterimage")
    activation = _unit_vector(contact, "contact")
    if len(previous) != len(activation):
        raise BaselineValidationError("previous_afterimage and contact must have equal geometry")
    decay = decay_factor(dt=dt, tau=tau)
    afterimage = tuple(
        (decay * old_value) + ((1.0 - decay) * input_value)
        for old_value, input_value in zip(previous, activation, strict=True)
    )
    return CarrierFrame(activation=activation, afterimage=afterimage)


def run_independent_history(
    contacts: Iterable[Iterable[float]],
    *,
    dt: float,
    tau: float,
    initial_afterimage: Iterable[float] | None = None,
) -> tuple[CarrierFrame, ...]:
    """Run a finite probe history without storing state outside the result."""

    contact_vectors = tuple(tuple(contact) for contact in contacts)
    if not contact_vectors:
        raise BaselineValidationError("contacts cannot be empty")
    width = len(contact_vectors[0])
    previous = tuple(initial_afterimage) if initial_afterimage is not None else (0.0,) * width
    frames = []
    for contact in contact_vectors:
        frame = independent_leaky_step(previous, contact, dt=dt, tau=tau)
        frames.append(frame)
        previous = frame.afterimage
    return tuple(frames)
