"""Counterfactual entry transport from signed local field flow."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math

from .radial_contact_morphology import RadialContactMaterialLayerState
from .radial_transport_admissibility import (
    NeuronRadialFluxProposal,
    RadialInterfaceFlux,
    RadialProfileFluxProposal,
    RadialTransportProposal,
    RadialTransportProposalAudit,
    audit_radial_transport_proposal,
)
from .structural_contact_drive import StructuralContactDriveMap


class SignedFieldFlowCounterfactualError(ValueError):
    """Raised when the counterfactual loses its causal or material boundary."""


def _positive(value: object, role: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise SignedFieldFlowCounterfactualError(
            f"{role} must be numeric"
        ) from exc
    if not math.isfinite(result) or result <= 0.0:
        raise SignedFieldFlowCounterfactualError(
            f"{role} must be finite and greater than zero"
        )
    return result


@dataclass(frozen=True, slots=True)
class SignedFieldFlowEntryCounterfactual:
    """One polarity branch; its proposal remains outside the runtime."""

    polarity: int
    velocity_scale: float
    duration_seconds: float
    proposal: RadialTransportProposal
    audit: RadialTransportProposalAudit
    moved_from_unbound_material: float
    source_morphology_preserved: bool
    source_drive_preserved: bool
    movement_fully_explained_by_mapping: bool
    runtime_candidate_released: bool = False

    def __post_init__(self) -> None:
        if self.polarity not in (-1, 1):
            raise SignedFieldFlowCounterfactualError(
                "counterfactual polarity must be -1 or 1"
            )
        object.__setattr__(
            self,
            "velocity_scale",
            _positive(self.velocity_scale, "velocity_scale"),
        )
        object.__setattr__(
            self,
            "duration_seconds",
            _positive(self.duration_seconds, "duration_seconds"),
        )
        if not isinstance(self.proposal, RadialTransportProposal):
            raise SignedFieldFlowCounterfactualError(
                "counterfactual requires one radial transport proposal"
            )
        if not isinstance(self.audit, RadialTransportProposalAudit):
            raise SignedFieldFlowCounterfactualError(
                "counterfactual requires one radial transport audit"
            )
        moved = float(self.moved_from_unbound_material)
        if not math.isfinite(moved) or moved < 0.0:
            raise SignedFieldFlowCounterfactualError(
                "moved material must be finite and non-negative"
            )
        object.__setattr__(self, "moved_from_unbound_material", moved)


@dataclass(frozen=True, slots=True)
class SignedFieldFlowPolarityComparison:
    """Two equally explicit sign conventions at the same completed field step."""

    aligned: SignedFieldFlowEntryCounterfactual
    reversed: SignedFieldFlowEntryCounterfactual
    both_kinematically_admissible: bool
    resulting_morphologies_different: bool
    polarity_determined_by_field_contract: bool
    scale_determined_by_field_contract: bool
    direct_mapping_released: bool
    material_runtime_changed: bool = False

    def __post_init__(self) -> None:
        if (
            not isinstance(self.aligned, SignedFieldFlowEntryCounterfactual)
            or not isinstance(
                self.reversed,
                SignedFieldFlowEntryCounterfactual,
            )
            or self.aligned.polarity != 1
            or self.reversed.polarity != -1
        ):
            raise SignedFieldFlowCounterfactualError(
                "polarity comparison requires aligned and reversed branches"
            )


def propose_signed_field_flow_entry(
    source: RadialContactMaterialLayerState,
    drives: StructuralContactDriveMap,
    *,
    polarity: int,
    velocity_scale: float,
    duration_seconds: float,
) -> SignedFieldFlowEntryCounterfactual:
    """Map one sign convention to first-cell fluxes for passive comparison."""

    if not isinstance(source, RadialContactMaterialLayerState):
        raise SignedFieldFlowCounterfactualError(
            "counterfactual requires one radial morphology"
        )
    if not isinstance(drives, StructuralContactDriveMap):
        raise SignedFieldFlowCounterfactualError(
            "counterfactual requires one structural drive map"
        )
    if polarity not in (-1, 1):
        raise SignedFieldFlowCounterfactualError(
            "polarity must be -1 or 1"
        )
    scale = _positive(velocity_scale, "velocity_scale")
    duration = _positive(duration_seconds, "duration_seconds")
    if not source.is_neutral:
        raise SignedFieldFlowCounterfactualError(
            "entry counterfactual requires neutral unbound morphology"
        )
    if (
        drives.contact_material_digest
        != source.source_contact_material_digest
        or drives.source_layer_id != source.source_layer_id
        or drives.geometry_id != source.geometry_id
        or drives.source_tick != source.field_tick
    ):
        raise SignedFieldFlowCounterfactualError(
            "drive map and radial morphology must share one source boundary"
        )

    source_digest = source.digest()
    drive_digest = drives.digest()
    source_by_id = {
        item.owner_neuron_id: item for item in source.substrates
    }
    drive_by_id = {
        item.owner_neuron_id: item for item in drives.neurons
    }
    if set(source_by_id) != set(drive_by_id):
        raise SignedFieldFlowCounterfactualError(
            "drive map and morphology owners must match"
        )

    neuron_fluxes = []
    expected_moved = 0.0
    for owner_id in sorted(source_by_id):
        material = source_by_id[owner_id]
        drive = drive_by_id[owner_id]
        surface_by_direction = {
            item.relative_position: item for item in drive.surfaces
        }
        if {
            item.relative_position for item in material.profiles
        } != set(surface_by_direction):
            raise SignedFieldFlowCounterfactualError(
                "drive surfaces and radial profiles must match"
            )
        profiles = []
        for profile in material.profiles:
            surface = surface_by_direction[profile.relative_position]
            signed_flow = (
                0.0
                if surface.signed_field_flow is None
                else surface.signed_field_flow
            )
            radial_velocity = polarity * scale * signed_flow
            core_rate = (
                radial_velocity * material.unbound_material
                if radial_velocity > 0.0
                else 0.0
            )
            expected_moved += duration * core_rate
            profiles.append(
                RadialProfileFluxProposal(
                    relative_position=profile.relative_position,
                    interfaces=tuple(
                        RadialInterfaceFlux(
                            edge,
                            core_rate if index == 0 else 0.0,
                        )
                        for index, edge in enumerate(source.radial_edges)
                    ),
                )
            )
        neuron_fluxes.append(
            NeuronRadialFluxProposal(
                owner_neuron_id=owner_id,
                profiles=tuple(profiles),
            )
        )

    proposal = RadialTransportProposal(
        source_morphology_digest=source_digest,
        source_tick=source.field_tick,
        duration_seconds=duration,
        neurons=tuple(neuron_fluxes),
    )
    audit = audit_radial_transport_proposal(source, proposal)
    moved = 0.0
    if audit.proposed_state is not None:
        moved = math.fsum(
            before.unbound_material - after.unbound_material
            for before, after in zip(
                source.substrates,
                audit.proposed_state.substrates,
                strict=True,
            )
        )

    return SignedFieldFlowEntryCounterfactual(
        polarity=polarity,
        velocity_scale=scale,
        duration_seconds=duration,
        proposal=proposal,
        audit=audit,
        moved_from_unbound_material=moved,
        source_morphology_preserved=source.digest() == source_digest,
        source_drive_preserved=drives.digest() == drive_digest,
        movement_fully_explained_by_mapping=math.isclose(
            moved,
            expected_moved,
            rel_tol=0.0,
            abs_tol=1e-12,
        ),
    )


def compare_signed_field_flow_polarities(
    source: RadialContactMaterialLayerState,
    drives: StructuralContactDriveMap,
    *,
    velocity_scale: float,
    duration_seconds: float,
) -> SignedFieldFlowPolarityComparison:
    """Compare both ungrounded field-flow-to-radial sign conventions."""

    aligned = propose_signed_field_flow_entry(
        source,
        drives,
        polarity=1,
        velocity_scale=velocity_scale,
        duration_seconds=duration_seconds,
    )
    reversed_branch = propose_signed_field_flow_entry(
        source,
        drives,
        polarity=-1,
        velocity_scale=velocity_scale,
        duration_seconds=duration_seconds,
    )
    both_admissible = aligned.audit.accepted and reversed_branch.audit.accepted
    states_different = (
        aligned.audit.proposed_state is not None
        and reversed_branch.audit.proposed_state is not None
        and aligned.audit.proposed_state != reversed_branch.audit.proposed_state
    )
    return SignedFieldFlowPolarityComparison(
        aligned=aligned,
        reversed=reversed_branch,
        both_kinematically_admissible=both_admissible,
        resulting_morphologies_different=states_different,
        polarity_determined_by_field_contract=False,
        scale_determined_by_field_contract=False,
        direct_mapping_released=False,
    )


def signed_field_flow_counterfactual_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            SignedFieldFlowEntryCounterfactual,
            SignedFieldFlowPolarityComparison,
        )
        for item in fields(contract)
    )
