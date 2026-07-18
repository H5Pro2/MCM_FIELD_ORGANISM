"""Passive capacity audit of the current receptor-to-field boundary."""

from __future__ import annotations

from dataclasses import dataclass, fields

from .mcm_neuron import MCMFieldPerception, MCMNeuron, MCMNeuronValidationError
from .mcm_neuron_layer import MCMNeuronDrive
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_distributor import (
    ReceptorDistributionError,
    ReceptorDistributor,
    ReceptorDock,
)


@dataclass(frozen=True, slots=True)
class CurrentFieldInputCapacity:
    single_frame_distribution_accepted: bool
    same_dock_batch_frame_count: int
    same_dock_batch_rejected: bool
    same_dock_batch_error: str
    scalar_contact_accepted: bool
    contact_sequence_rejected: bool
    contact_sequence_error: str
    serial_distribution_count: int
    required_complete_field_advances_if_serialized: int


@dataclass(frozen=True, slots=True)
class EndpointOnlyDriveCollision:
    first_contact_history: tuple[float, ...]
    second_contact_history: tuple[float, ...]
    shared_endpoint: float
    shared_previous_state_digest: str
    endpoint_only_drives_equal: bool


@dataclass(frozen=True, slots=True)
class FieldInputCapacityAuditResult:
    capacity: CurrentFieldInputCapacity
    endpoint_collision: EndpointOnlyDriveCollision
    variable_same_dock_batch_directly_representable: bool


def _frame(snapshot_index: int, value: float) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id="auditory",
        geometry_id="auditory.receptor.v1",
        snapshot_id=f"auditory.snapshot.{snapshot_index}",
        clock_id="auditory.source",
        window_start_tick=snapshot_index,
        window_end_tick=snapshot_index + 1,
        carrier_ids=("auditory.carrier.0",),
        values=(value,),
    )


def _distributor() -> ReceptorDistributor:
    distributor = ReceptorDistributor()
    distributor.attach(
        ReceptorDock(
            "dock.auditory",
            "auditory",
            "auditory.receptor.v1",
        )
    )
    return distributor


def _endpoint_drive(previous: MCMNeuron, endpoint: float) -> MCMNeuronDrive:
    return MCMNeuronDrive(
        previous=previous,
        perception=MCMFieldPerception(
            tick=previous.tick + 1,
            receptor_contact=endpoint,
            local_samples=(),
        ),
    )


def run_field_input_capacity_audit() -> FieldInputCapacityAuditResult:
    """Probe existing contracts without adding a batch-to-field adapter."""

    first_frame = _frame(0, 0.1)
    endpoint_frame = _frame(1, 0.9)
    field_time = CommonFieldTime("organism.test", 0, 10)
    single_accepted = bool(
        _distributor().distribute((first_frame,), field_time).contacts
    )

    batch_error = ""
    try:
        _distributor().distribute((first_frame, endpoint_frame), field_time)
    except ReceptorDistributionError as exc:
        batch_error = str(exc)

    scalar_accepted = (
        MCMFieldPerception(1, 0.9, ()).receptor_contact == 0.9
    )
    sequence_error = ""
    try:
        MCMFieldPerception(1, (0.1, 0.9), ())  # type: ignore[arg-type]
    except MCMNeuronValidationError as exc:
        sequence_error = str(exc)

    serial_distributions = (
        _distributor().distribute(
            (first_frame,),
            CommonFieldTime("organism.test", 0, 5),
        ),
        _distributor().distribute(
            (endpoint_frame,),
            CommonFieldTime("organism.test", 5, 10),
        ),
    )

    previous = MCMNeuron(
        neuron_id="organism.audit.n0",
        field_id="organism.audit",
        modality_id="organism",
        geometry_id="organism.audit.v1",
        position=(0,),
        activation=0.3,
        afterimage=0.2,
        perception=MCMFieldPerception(0, 0.0, ()),
    )
    first_history = (0.1, 0.9)
    second_history = (0.8, 0.9)
    first_drive = _endpoint_drive(previous, first_history[-1])
    second_drive = _endpoint_drive(previous, second_history[-1])

    capacity = CurrentFieldInputCapacity(
        single_frame_distribution_accepted=single_accepted,
        same_dock_batch_frame_count=2,
        same_dock_batch_rejected=bool(batch_error),
        same_dock_batch_error=batch_error,
        scalar_contact_accepted=scalar_accepted,
        contact_sequence_rejected=bool(sequence_error),
        contact_sequence_error=sequence_error,
        serial_distribution_count=len(serial_distributions),
        required_complete_field_advances_if_serialized=len(serial_distributions),
    )
    collision = EndpointOnlyDriveCollision(
        first_contact_history=first_history,
        second_contact_history=second_history,
        shared_endpoint=first_history[-1],
        shared_previous_state_digest=previous.digest(),
        endpoint_only_drives_equal=first_drive == second_drive,
    )
    return FieldInputCapacityAuditResult(
        capacity=capacity,
        endpoint_collision=collision,
        variable_same_dock_batch_directly_representable=(
            not capacity.same_dock_batch_rejected
            or not capacity.contact_sequence_rejected
        ),
    )


def field_input_capacity_audit_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            CurrentFieldInputCapacity,
            EndpointOnlyDriveCollision,
            FieldInputCapacityAuditResult,
        )
        for item in fields(contract)
    )
