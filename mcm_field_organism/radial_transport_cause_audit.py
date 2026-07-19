"""Passive role audit for possible radial transport causes."""

from __future__ import annotations

from dataclasses import dataclass, fields
from enum import Enum

from .mcm_neuron import MCMFieldSample, MCMNeuron
from .mcm_neuron_layer import MCMNeuronLayer
from .structural_contact_drive import (
    LocalContactSurfaceDrive,
    NeuronContactDrive,
    StructuralContactDriveMap,
)


class RadialTransportCauseAuditError(ValueError):
    """Raised when field cause roles cannot be audited at one causal boundary."""


class RadialTransportCauseDisposition(str, Enum):
    REJECTED_AS_DIRECT_CAUSE = "rejected_as_direct_cause"
    NOT_PRESENT_IN_DRIVE_CONTRACT = "not_present_in_drive_contract"
    OPEN_FOR_PASSIVE_ISOLATION = "open_for_passive_isolation"


@dataclass(frozen=True, slots=True)
class RadialTransportCauseAssessment:
    """Architecture-role assessment, not a runtime cause selector."""

    cause_id: str
    disposition: RadialTransportCauseDisposition
    present_in_contact_drive: bool
    owner_local: bool
    direction_resolved: bool
    carries_fast_history: bool
    geometric_sign_available: bool
    requires_added_direction_rule: bool
    inherits_fixed_leak: bool
    selected_as_material_cause: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.cause_id, str) or not self.cause_id:
            raise RadialTransportCauseAuditError(
                "cause_id must be non-empty"
            )
        if not isinstance(
            self.disposition,
            RadialTransportCauseDisposition,
        ):
            raise RadialTransportCauseAuditError(
                "cause disposition must be explicit"
            )


@dataclass(frozen=True, slots=True)
class RadialTransportCauseAudit:
    """Observed role boundary beside unchanged field and drive states."""

    assessments: tuple[RadialTransportCauseAssessment, ...]
    receptor_surface_selector_absent: bool
    owner_activation_surface_selector_absent: bool
    owner_afterimage_surface_selector_absent: bool
    sampled_afterimage_excluded_from_drive: bool
    signed_local_field_flow_direction_available: bool
    direct_receptor_cause_rejected: bool
    direct_afterimage_cause_rejected: bool
    open_candidate_ids: tuple[str, ...]
    source_layer_preserved: bool
    drive_map_preserved: bool
    material_motion_performed: bool = False
    runtime_candidate_released: bool = False

    def __post_init__(self) -> None:
        assessments = tuple(self.assessments)
        if not assessments or any(
            not isinstance(item, RadialTransportCauseAssessment)
            for item in assessments
        ):
            raise RadialTransportCauseAuditError(
                "cause audit requires explicit assessments"
            )
        cause_ids = [item.cause_id for item in assessments]
        if len(set(cause_ids)) != len(cause_ids):
            raise RadialTransportCauseAuditError(
                "cause assessment identities must be unique"
            )
        open_ids = tuple(self.open_candidate_ids)
        expected_open = tuple(
            sorted(
                item.cause_id
                for item in assessments
                if item.disposition
                is RadialTransportCauseDisposition.OPEN_FOR_PASSIVE_ISOLATION
            )
        )
        if tuple(sorted(open_ids)) != expected_open:
            raise RadialTransportCauseAuditError(
                "open candidate identities must match the assessments"
            )
        object.__setattr__(
            self,
            "assessments",
            tuple(sorted(assessments, key=lambda item: item.cause_id)),
        )
        object.__setattr__(self, "open_candidate_ids", expected_open)

    def assessment(self, cause_id: str) -> RadialTransportCauseAssessment:
        for item in self.assessments:
            if item.cause_id == cause_id:
                return item
        raise RadialTransportCauseAuditError(
            f"unknown cause assessment: {cause_id}"
        )


def audit_radial_transport_cause_roles(
    source_layer: MCMNeuronLayer,
    drive_map: StructuralContactDriveMap,
) -> RadialTransportCauseAudit:
    """Classify existing causes without producing a radial flux proposal."""

    if not isinstance(source_layer, MCMNeuronLayer):
        raise RadialTransportCauseAuditError(
            "cause audit requires one completed source layer"
        )
    if not isinstance(drive_map, StructuralContactDriveMap):
        raise RadialTransportCauseAuditError(
            "cause audit requires one structural contact drive map"
        )
    if (
        drive_map.source_layer_id != source_layer.layer_id
        or drive_map.geometry_id != source_layer.neurons[0].geometry_id
        or drive_map.source_tick != source_layer.tick
        or drive_map.source_layer_digest != source_layer.digest()
    ):
        raise RadialTransportCauseAuditError(
            "drive map must reference the completed source layer"
        )

    layer_digest = source_layer.digest()
    drive_digest = drive_map.digest()
    neuron_drive_roles = {item.name for item in fields(NeuronContactDrive)}
    surface_drive_roles = {
        item.name for item in fields(LocalContactSurfaceDrive)
    }
    neuron_roles = {item.name for item in fields(MCMNeuron)}
    field_sample_roles = {item.name for item in fields(MCMFieldSample)}

    receptor_surface_selector_absent = (
        "receptor_contact" in neuron_drive_roles
        and "receptor_contact" not in surface_drive_roles
        and "surface_receptor_contact" not in surface_drive_roles
        and "selected_surface" not in surface_drive_roles
    )
    owner_activation_surface_selector_absent = all(
        len({surface.owner_activation for surface in neuron.surfaces}) == 1
        for neuron in drive_map.neurons
    )
    owner_afterimage_surface_selector_absent = (
        "afterimage" in neuron_roles
        and "owner_afterimage" not in surface_drive_roles
        and "surface_afterimage" not in surface_drive_roles
    )
    sampled_afterimage_excluded_from_drive = (
        "afterimage" in field_sample_roles
        and "local_afterimage" not in surface_drive_roles
    )
    signed_flow_available = (
        "relative_position" in surface_drive_roles
        and "signed_field_flow" in surface_drive_roles
        and any(
            surface.local_sample_present
            and surface.signed_field_flow is not None
            for neuron in drive_map.neurons
            for surface in neuron.surfaces
        )
    )

    assessments = (
        RadialTransportCauseAssessment(
            cause_id="current_receptor_contact",
            disposition=(
                RadialTransportCauseDisposition.REJECTED_AS_DIRECT_CAUSE
            ),
            present_in_contact_drive=True,
            owner_local=True,
            direction_resolved=False,
            carries_fast_history=False,
            geometric_sign_available=False,
            requires_added_direction_rule=True,
            inherits_fixed_leak=False,
        ),
        RadialTransportCauseAssessment(
            cause_id="owner_activation",
            disposition=(
                RadialTransportCauseDisposition.REJECTED_AS_DIRECT_CAUSE
            ),
            present_in_contact_drive=True,
            owner_local=True,
            direction_resolved=False,
            carries_fast_history=False,
            geometric_sign_available=False,
            requires_added_direction_rule=True,
            inherits_fixed_leak=False,
        ),
        RadialTransportCauseAssessment(
            cause_id="owner_fast_afterimage",
            disposition=(
                RadialTransportCauseDisposition.REJECTED_AS_DIRECT_CAUSE
            ),
            present_in_contact_drive=False,
            owner_local=True,
            direction_resolved=False,
            carries_fast_history=True,
            geometric_sign_available=False,
            requires_added_direction_rule=True,
            inherits_fixed_leak=True,
        ),
        RadialTransportCauseAssessment(
            cause_id="sampled_fast_afterimage",
            disposition=(
                RadialTransportCauseDisposition.NOT_PRESENT_IN_DRIVE_CONTRACT
            ),
            present_in_contact_drive=False,
            owner_local=False,
            direction_resolved=True,
            carries_fast_history=True,
            geometric_sign_available=False,
            requires_added_direction_rule=False,
            inherits_fixed_leak=True,
        ),
        RadialTransportCauseAssessment(
            cause_id="signed_local_field_flow",
            disposition=(
                RadialTransportCauseDisposition.OPEN_FOR_PASSIVE_ISOLATION
            ),
            present_in_contact_drive=True,
            owner_local=False,
            direction_resolved=True,
            carries_fast_history=False,
            geometric_sign_available=True,
            requires_added_direction_rule=False,
            inherits_fixed_leak=False,
        ),
    )
    open_ids = tuple(
        item.cause_id
        for item in assessments
        if item.disposition
        is RadialTransportCauseDisposition.OPEN_FOR_PASSIVE_ISOLATION
    )

    return RadialTransportCauseAudit(
        assessments=assessments,
        receptor_surface_selector_absent=(
            receptor_surface_selector_absent
        ),
        owner_activation_surface_selector_absent=(
            owner_activation_surface_selector_absent
        ),
        owner_afterimage_surface_selector_absent=(
            owner_afterimage_surface_selector_absent
        ),
        sampled_afterimage_excluded_from_drive=(
            sampled_afterimage_excluded_from_drive
        ),
        signed_local_field_flow_direction_available=signed_flow_available,
        direct_receptor_cause_rejected=(
            receptor_surface_selector_absent
        ),
        direct_afterimage_cause_rejected=(
            owner_afterimage_surface_selector_absent
        ),
        open_candidate_ids=open_ids,
        source_layer_preserved=source_layer.digest() == layer_digest,
        drive_map_preserved=drive_map.digest() == drive_digest,
    )


def radial_transport_cause_audit_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            RadialTransportCauseAssessment,
            RadialTransportCauseAudit,
        )
        for item in fields(contract)
    )
