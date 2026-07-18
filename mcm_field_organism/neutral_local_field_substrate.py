"""Minimal semantically neutral local activation dynamics for the shared field."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math
from statistics import fmean

from .mcm_neuron_layer import MCMNeuronOutput, MCMNeuronTransition
from .passive_field_controls import (
    PassiveDriveRole,
    PassiveDriveRoleMask,
    PassiveLocalDrive,
    PassiveLocalFieldSample,
    PassivePreviousLocalState,
    adapt_passive_local_transition,
)


class NeutralLocalFieldSubstrateError(ValueError):
    """Raised when the minimal local substrate cannot advance explicitly."""


@dataclass(frozen=True, slots=True)
class NeutralLocalFieldSubstrateConfig:
    """One exposed physical time scale, without semantic or modal weights."""

    response_time_seconds: float

    def __post_init__(self) -> None:
        value = float(self.response_time_seconds)
        if not math.isfinite(value) or value <= 0.0:
            raise NeutralLocalFieldSubstrateError(
                "response_time_seconds must be finite and greater than zero"
            )
        object.__setattr__(self, "response_time_seconds", value)


def _required_previous(
    drive: PassiveLocalDrive,
) -> PassivePreviousLocalState:
    previous = drive.previous_state
    if not isinstance(previous, PassivePreviousLocalState):
        raise NeutralLocalFieldSubstrateError(
            "neutral local substrate requires the previous local state"
        )
    return previous


def _required_samples(
    drive: PassiveLocalDrive,
) -> tuple[PassiveLocalFieldSample, ...]:
    samples = drive.local_field_samples
    if not isinstance(samples, tuple):
        raise NeutralLocalFieldSubstrateError(
            "neutral local substrate requires local field samples"
        )
    return samples


def neutral_local_field_substrate_step(
    drive: PassiveLocalDrive,
    config: NeutralLocalFieldSubstrateConfig,
) -> MCMNeuronOutput:
    """Relax activation toward equally admitted local field and world contact."""

    if not isinstance(drive, PassiveLocalDrive):
        raise NeutralLocalFieldSubstrateError(
            "neutral local substrate requires one passive local drive"
        )
    if not isinstance(config, NeutralLocalFieldSubstrateConfig):
        raise NeutralLocalFieldSubstrateError(
            "neutral local substrate requires an explicit configuration"
        )
    previous = _required_previous(drive)
    samples = _required_samples(drive)
    elapsed = drive.elapsed_seconds
    if not isinstance(elapsed, float):
        raise NeutralLocalFieldSubstrateError(
            "neutral local substrate requires measured elapsed duration"
        )

    influences = []
    if samples:
        influences.append(fmean(sample.activation for sample in samples))
    if drive.receptor_contact is not None:
        influences.append(drive.receptor_contact)

    if not influences:
        return MCMNeuronOutput(previous.activation, previous.afterimage)

    target = fmean(influences)
    retention = math.exp(-elapsed / config.response_time_seconds)
    activation = (
        retention * previous.activation
        + (1.0 - retention) * target
    )
    activation = max(-1.0, min(1.0, activation))
    return MCMNeuronOutput(activation, previous.afterimage)


def make_neutral_local_field_transition(
    config: NeutralLocalFieldSubstrateConfig,
) -> MCMNeuronTransition:
    """Expose the substrate through the existing identity-free local adapter."""

    if not isinstance(config, NeutralLocalFieldSubstrateConfig):
        raise NeutralLocalFieldSubstrateError(
            "neutral local substrate requires an explicit configuration"
        )
    roles = PassiveDriveRoleMask(
        (
            PassiveDriveRole.PREVIOUS_LOCAL_STATE,
            PassiveDriveRole.CURRENT_RECEPTOR_CONTACT,
            PassiveDriveRole.LOCAL_FIELD_SAMPLES,
            PassiveDriveRole.ELAPSED_DURATION,
        )
    )

    def transition(drive: PassiveLocalDrive) -> MCMNeuronOutput:
        return neutral_local_field_substrate_step(drive, config)

    return adapt_passive_local_transition(transition, roles)


def neutral_local_field_substrate_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(NeutralLocalFieldSubstrateConfig))
