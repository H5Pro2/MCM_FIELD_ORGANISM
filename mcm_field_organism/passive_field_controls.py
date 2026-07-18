"""Passive role projections and fixed controls for local field comparisons."""

from __future__ import annotations

from dataclasses import dataclass, fields
from enum import Enum
import math
from statistics import fmean
from typing import Callable

from .mcm_neuron_layer import (
    MCMNeuronDrive,
    MCMNeuronOutput,
    MCMNeuronTransition,
)


class PassiveFieldControlError(ValueError):
    """Raised when a passive control hides or invents a local input role."""


class PassiveDriveRole(Enum):
    PREVIOUS_LOCAL_STATE = "previous_local_state"
    CURRENT_RECEPTOR_CONTACT = "current_receptor_contact"
    LOCAL_FIELD_SAMPLES = "local_field_samples"
    ELAPSED_DURATION = "elapsed_duration"
    TRANSIENT_LOCAL_RECEPTOR_HISTORY = "transient_local_receptor_history"


@dataclass(frozen=True, slots=True)
class PassiveDriveRoleMask:
    """Explicit set of local roles visible to one passive transition."""

    active_roles: tuple[PassiveDriveRole, ...]

    def __post_init__(self) -> None:
        roles = tuple(self.active_roles)
        if any(not isinstance(role, PassiveDriveRole) for role in roles):
            raise PassiveFieldControlError(
                "passive role mask accepts only declared local drive roles"
            )
        if len(set(roles)) != len(roles):
            raise PassiveFieldControlError(
                "every passive local drive role may occur only once"
            )
        object.__setattr__(
            self,
            "active_roles",
            tuple(sorted(roles, key=lambda role: role.value)),
        )

    def includes(self, role: PassiveDriveRole) -> bool:
        if not isinstance(role, PassiveDriveRole):
            raise PassiveFieldControlError("unknown passive local drive role")
        return role in self.active_roles

    def without(self, role: PassiveDriveRole) -> "PassiveDriveRoleMask":
        if not self.includes(role):
            raise PassiveFieldControlError(
                f"cannot ablate inactive role: {role.value}"
            )
        return PassiveDriveRoleMask(
            tuple(item for item in self.active_roles if item is not role)
        )


@dataclass(frozen=True, slots=True)
class PassivePreviousLocalState:
    activation: float
    afterimage: float

    def __post_init__(self) -> None:
        for role in ("activation", "afterimage"):
            value = float(getattr(self, role))
            if not math.isfinite(value) or abs(value) > 1.0:
                raise PassiveFieldControlError(
                    f"{role} must stay within the normalized field domain"
                )
            object.__setattr__(self, role, value)


@dataclass(frozen=True, slots=True)
class PassiveLocalFieldSample:
    relative_position: tuple[int, ...]
    activation: float
    afterimage: float

    def __post_init__(self) -> None:
        position = tuple(self.relative_position)
        if (
            not position
            or any(
                isinstance(value, bool) or not isinstance(value, int)
                for value in position
            )
            or all(value == 0 for value in position)
        ):
            raise PassiveFieldControlError(
                "local sample requires one non-origin integer offset"
            )
        object.__setattr__(self, "relative_position", position)
        for role in ("activation", "afterimage"):
            value = float(getattr(self, role))
            if not math.isfinite(value) or abs(value) > 1.0:
                raise PassiveFieldControlError(
                    f"sample {role} must stay within the normalized field domain"
                )
            object.__setattr__(self, role, value)


@dataclass(frozen=True, slots=True)
class PassiveLocalDockContact:
    read_start_offset_seconds: float
    completion_offset_seconds: float
    value: float

    def __post_init__(self) -> None:
        start = float(self.read_start_offset_seconds)
        completion = float(self.completion_offset_seconds)
        value = float(self.value)
        if (
            not math.isfinite(start)
            or not math.isfinite(completion)
            or completion <= start
        ):
            raise PassiveFieldControlError(
                "local dock contact offsets must form one finite ordered read"
            )
        if not math.isfinite(value) or abs(value) > 1.0:
            raise PassiveFieldControlError(
                "local dock value must stay within the normalized field domain"
            )
        object.__setattr__(self, "read_start_offset_seconds", start)
        object.__setattr__(self, "completion_offset_seconds", completion)
        object.__setattr__(self, "value", value)


@dataclass(frozen=True, slots=True)
class PassiveLocalDrive:
    """Identity-free local information view for one passive transition."""

    previous_state: PassivePreviousLocalState | None
    receptor_contact: float | None
    local_field_samples: tuple[PassiveLocalFieldSample, ...] | None
    elapsed_seconds: float | None
    transient_receptor_history: tuple[PassiveLocalDockContact, ...] | None

    def __post_init__(self) -> None:
        if self.previous_state is not None and not isinstance(
            self.previous_state,
            PassivePreviousLocalState,
        ):
            raise PassiveFieldControlError(
                "previous state must use the passive local state contract"
            )
        if self.receptor_contact is not None:
            contact = float(self.receptor_contact)
            if not math.isfinite(contact) or abs(contact) > 1.0:
                raise PassiveFieldControlError(
                    "receptor contact must stay within the normalized field domain"
                )
            object.__setattr__(self, "receptor_contact", contact)
        if self.local_field_samples is not None:
            samples = tuple(self.local_field_samples)
            if any(
                not isinstance(item, PassiveLocalFieldSample)
                for item in samples
            ):
                raise PassiveFieldControlError(
                    "local field samples violate the passive sample contract"
                )
            object.__setattr__(self, "local_field_samples", samples)
        if self.elapsed_seconds is not None:
            elapsed = float(self.elapsed_seconds)
            if not math.isfinite(elapsed) or elapsed <= 0.0:
                raise PassiveFieldControlError(
                    "elapsed duration must be finite and greater than zero"
                )
            object.__setattr__(self, "elapsed_seconds", elapsed)
        if self.transient_receptor_history is not None:
            history = tuple(self.transient_receptor_history)
            if any(
                not isinstance(item, PassiveLocalDockContact)
                for item in history
            ):
                raise PassiveFieldControlError(
                    "transient history violates the passive dock contract"
                )
            completions = [
                item.completion_offset_seconds for item in history
            ]
            if completions != sorted(set(completions)):
                raise PassiveFieldControlError(
                    "transient contacts require unique ordered completions"
                )
            object.__setattr__(self, "transient_receptor_history", history)


PassiveLocalTransition = Callable[[PassiveLocalDrive], MCMNeuronOutput]


def all_passive_drive_roles() -> PassiveDriveRoleMask:
    return PassiveDriveRoleMask(tuple(PassiveDriveRole))


def passive_drive_role_ablation(
    role: PassiveDriveRole,
) -> PassiveDriveRoleMask:
    return all_passive_drive_roles().without(role)


def _transient_history(
    drive: MCMNeuronDrive,
) -> tuple[PassiveLocalDockContact, ...]:
    transient = drive.transient_receptor_input
    if transient is None:
        return ()
    step_time = drive.step_time
    if step_time is None:
        raise PassiveFieldControlError(
            "transient local history requires measured step time"
        )
    rate = step_time.ticks_per_second
    return tuple(
        PassiveLocalDockContact(
            read_start_offset_seconds=(
                contact.organism_read_time.window_start_tick
                - step_time.start_tick
            )
            / rate,
            completion_offset_seconds=(
                contact.organism_read_time.window_end_tick
                - step_time.start_tick
            )
            / rate,
            value=contact.value,
        )
        for contact in transient.contacts
    )


def project_passive_local_drive(
    drive: MCMNeuronDrive,
    roles: PassiveDriveRoleMask,
) -> PassiveLocalDrive:
    """Expose only selected local values, without neuron or modality identity."""

    if not isinstance(drive, MCMNeuronDrive):
        raise PassiveFieldControlError(
            "passive projection requires one completed MCM neuron drive"
        )
    if not isinstance(roles, PassiveDriveRoleMask):
        raise PassiveFieldControlError(
            "passive projection requires one explicit role mask"
        )

    previous_state = None
    if roles.includes(PassiveDriveRole.PREVIOUS_LOCAL_STATE):
        previous_state = PassivePreviousLocalState(
            drive.previous.activation,
            drive.previous.afterimage,
        )

    local_samples = None
    if roles.includes(PassiveDriveRole.LOCAL_FIELD_SAMPLES):
        local_samples = tuple(
            PassiveLocalFieldSample(
                sample.relative_position,
                sample.activation,
                sample.afterimage,
            )
            for sample in drive.perception.local_samples
        )

    elapsed_seconds = None
    if roles.includes(PassiveDriveRole.ELAPSED_DURATION):
        if drive.step_time is None:
            raise PassiveFieldControlError(
                "elapsed-duration role requires measured step time"
            )
        elapsed_seconds = drive.step_time.elapsed_seconds

    transient_history = None
    if roles.includes(PassiveDriveRole.TRANSIENT_LOCAL_RECEPTOR_HISTORY):
        transient_history = _transient_history(drive)

    return PassiveLocalDrive(
        previous_state=previous_state,
        receptor_contact=(
            drive.perception.receptor_contact
            if roles.includes(PassiveDriveRole.CURRENT_RECEPTOR_CONTACT)
            else None
        ),
        local_field_samples=local_samples,
        elapsed_seconds=elapsed_seconds,
        transient_receptor_history=transient_history,
    )


def adapt_passive_local_transition(
    transition: PassiveLocalTransition,
    roles: PassiveDriveRoleMask,
) -> MCMNeuronTransition:
    """Adapt an explicit passive transition without installing it in runtime."""

    if not callable(transition):
        raise PassiveFieldControlError(
            "passive local transition must be callable"
        )
    if not isinstance(roles, PassiveDriveRoleMask):
        raise PassiveFieldControlError(
            "passive local transition requires one explicit role mask"
        )

    def adapted(drive: MCMNeuronDrive) -> MCMNeuronOutput:
        output = transition(project_passive_local_drive(drive, roles))
        if not isinstance(output, MCMNeuronOutput):
            raise PassiveFieldControlError(
                "passive local transition must return MCMNeuronOutput"
            )
        return output

    return adapted


def _required(value: object, role: str) -> object:
    if value is None:
        raise PassiveFieldControlError(
            f"passive baseline requires active role: {role}"
        )
    return value


def passive_hold_state_baseline(drive: PassiveLocalDrive) -> MCMNeuronOutput:
    """B0: preserve only the previous fast local state."""

    previous = _required(drive.previous_state, "previous_local_state")
    assert isinstance(previous, PassivePreviousLocalState)
    return MCMNeuronOutput(previous.activation, previous.afterimage)


def passive_receptor_projection_baseline(
    drive: PassiveLocalDrive,
) -> MCMNeuronOutput:
    """B1: expose only the current scalar contact or its natural absence."""

    return MCMNeuronOutput(
        0.0 if drive.receptor_contact is None else drive.receptor_contact,
        0.0,
    )


def passive_symmetric_local_reader_baseline(
    drive: PassiveLocalDrive,
) -> MCMNeuronOutput:
    """B2: fixed stateless mean of prior-tick local activation samples."""

    samples = _required(drive.local_field_samples, "local_field_samples")
    assert isinstance(samples, tuple)
    activation = (
        fmean(sample.activation for sample in samples)
        if samples
        else 0.0
    )
    return MCMNeuronOutput(activation, 0.0)


def fixed_leaky_local_afterimage_baseline(
    time_constant_seconds: float,
) -> PassiveLocalTransition:
    """B3: fixed non-adaptive local afterimage carrier."""

    tau = float(time_constant_seconds)
    if not math.isfinite(tau) or tau <= 0.0:
        raise PassiveFieldControlError(
            "B3 time constant must be finite and greater than zero"
        )

    def transition(drive: PassiveLocalDrive) -> MCMNeuronOutput:
        previous = _required(
            drive.previous_state,
            "previous_local_state",
        )
        samples = _required(
            drive.local_field_samples,
            "local_field_samples",
        )
        elapsed = _required(drive.elapsed_seconds, "elapsed_duration")
        assert isinstance(previous, PassivePreviousLocalState)
        assert isinstance(samples, tuple)
        assert isinstance(elapsed, float)
        local_input = (
            fmean(sample.activation for sample in samples)
            if samples
            else 0.0
        )
        retention = math.exp(-elapsed / tau)
        return MCMNeuronOutput(
            activation=local_input,
            afterimage=(
                retention * previous.afterimage
                + (1.0 - retention) * local_input
            ),
        )

    return transition


def passive_field_controls_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            PassiveDriveRoleMask,
            PassivePreviousLocalState,
            PassiveLocalFieldSample,
            PassiveLocalDockContact,
            PassiveLocalDrive,
        )
        for item in fields(contract)
    )
