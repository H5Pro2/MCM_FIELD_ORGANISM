"""Passive information audit of the existing local MCM neuron drive."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math

from .field_step_time import MCMFieldStepTime
from .mcm_neuron import MCMFieldPerception, MCMNeuron
from .mcm_neuron_layer import MCMNeuronDrive


class NeuronDriveInformationAuditError(ValueError):
    """Raised when a controlled endpoint history is invalid."""


@dataclass(frozen=True, slots=True)
class NeuronDriveInformation:
    prior_receptor_contact: float | None
    current_receptor_contact: float | None
    receptor_endpoint_change: float | None
    previous_activation: float
    previous_afterimage: float
    elapsed_seconds: float | None


@dataclass(frozen=True, slots=True)
class EndpointContactHistory:
    history_id: str
    contacts: tuple[float, ...]
    elapsed_seconds: float

    def __post_init__(self) -> None:
        if not isinstance(self.history_id, str) or not self.history_id:
            raise NeuronDriveInformationAuditError("history_id must not be empty")
        contacts = tuple(float(value) for value in self.contacts)
        if len(contacts) < 2 or any(
            not math.isfinite(value) or abs(value) > 1.0 for value in contacts
        ):
            raise NeuronDriveInformationAuditError(
                "history requires at least two normalized contacts"
            )
        elapsed = float(self.elapsed_seconds)
        if not math.isfinite(elapsed) or elapsed <= 0.0:
            raise NeuronDriveInformationAuditError(
                "elapsed_seconds must be finite and positive"
            )
        object.__setattr__(self, "contacts", contacts)
        object.__setattr__(self, "elapsed_seconds", elapsed)

    @property
    def sampled_contact_sum(self) -> float:
        return sum(self.contacts)


@dataclass(frozen=True, slots=True)
class DriveAxisComparison:
    comparison_id: str
    first: NeuronDriveInformation
    second: NeuronDriveInformation
    differing_roles: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class NeuronDriveInformationAuditResult:
    current_contact_axis: DriveAxisComparison
    prior_contact_axis: DriveAxisComparison
    elapsed_time_axis: DriveAxisComparison
    missing_current_contact: NeuronDriveInformation
    continuous_history: EndpointContactHistory
    interrupted_history: EndpointContactHistory
    endpoint_history_information_equal: bool


def observe_neuron_drive_information(
    drive: MCMNeuronDrive,
) -> NeuronDriveInformation:
    """Read existing drive roles without evaluating a transition."""

    if not isinstance(drive, MCMNeuronDrive):
        raise NeuronDriveInformationAuditError(
            "information audit requires one MCMNeuronDrive"
        )
    prior = drive.previous.perception.receptor_contact
    current = drive.perception.receptor_contact
    change = None if prior is None or current is None else current - prior
    return NeuronDriveInformation(
        prior_receptor_contact=prior,
        current_receptor_contact=current,
        receptor_endpoint_change=change,
        previous_activation=drive.previous.activation,
        previous_afterimage=drive.previous.afterimage,
        elapsed_seconds=(
            None if drive.step_time is None else drive.step_time.elapsed_seconds
        ),
    )


def _drive(
    *,
    prior_contact: float | None,
    current_contact: float | None,
    elapsed_seconds: float,
    activation: float = 0.3,
    afterimage: float = 0.2,
) -> MCMNeuronDrive:
    ticks_per_second = 1000.0
    elapsed_ticks = round(elapsed_seconds * ticks_per_second)
    previous = MCMNeuron(
        neuron_id="neuron.audit",
        field_id="field.audit",
        modality_id="audit",
        geometry_id="audit.line.v1",
        position=(0,),
        activation=activation,
        afterimage=afterimage,
        perception=MCMFieldPerception(0, prior_contact, ()),
    )
    return MCMNeuronDrive(
        previous=previous,
        perception=MCMFieldPerception(1, current_contact, ()),
        step_time=MCMFieldStepTime(
            "organism.test",
            0,
            elapsed_ticks,
            ticks_per_second,
        ),
    )


def _comparison(
    comparison_id: str,
    first: MCMNeuronDrive,
    second: MCMNeuronDrive,
) -> DriveAxisComparison:
    left = observe_neuron_drive_information(first)
    right = observe_neuron_drive_information(second)
    differing = tuple(
        item.name
        for item in fields(NeuronDriveInformation)
        if getattr(left, item.name) != getattr(right, item.name)
    )
    return DriveAxisComparison(comparison_id, left, right, differing)


def _drive_from_history(history: EndpointContactHistory) -> MCMNeuronDrive:
    return _drive(
        prior_contact=history.contacts[0],
        current_contact=history.contacts[-1],
        elapsed_seconds=history.elapsed_seconds,
    )


def run_neuron_drive_information_audit() -> NeuronDriveInformationAuditResult:
    """Separate available endpoint axes and expose their path collision."""

    current_axis = _comparison(
        "current_contact_axis",
        _drive(prior_contact=0.2, current_contact=0.2, elapsed_seconds=0.5),
        _drive(prior_contact=0.2, current_contact=0.8, elapsed_seconds=0.5),
    )
    prior_axis = _comparison(
        "prior_contact_axis",
        _drive(prior_contact=0.2, current_contact=0.8, elapsed_seconds=0.5),
        _drive(prior_contact=0.6, current_contact=0.8, elapsed_seconds=0.5),
    )
    time_axis = _comparison(
        "elapsed_time_axis",
        _drive(prior_contact=0.2, current_contact=0.8, elapsed_seconds=0.1),
        _drive(prior_contact=0.2, current_contact=0.8, elapsed_seconds=0.5),
    )
    missing = observe_neuron_drive_information(
        _drive(prior_contact=0.2, current_contact=None, elapsed_seconds=0.5)
    )
    continuous = EndpointContactHistory("continuous", (1.0, 1.0, 1.0), 1.0)
    interrupted = EndpointContactHistory("interrupted", (1.0, 0.0, 1.0), 1.0)
    continuous_information = observe_neuron_drive_information(
        _drive_from_history(continuous)
    )
    interrupted_information = observe_neuron_drive_information(
        _drive_from_history(interrupted)
    )
    return NeuronDriveInformationAuditResult(
        current_contact_axis=current_axis,
        prior_contact_axis=prior_axis,
        elapsed_time_axis=time_axis,
        missing_current_contact=missing,
        continuous_history=continuous,
        interrupted_history=interrupted,
        endpoint_history_information_equal=(
            continuous_information == interrupted_information
        ),
    )


def neuron_drive_information_audit_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            NeuronDriveInformation,
            EndpointContactHistory,
            DriveAxisComparison,
            NeuronDriveInformationAuditResult,
        )
        for item in fields(contract)
    )
