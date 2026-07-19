"""Passive admissibility checks for proposed contact-material transitions."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math

from .structural_contact_drive import StructuralContactDriveMap
from .structural_contact_substrate import ContactMaterialLayerState


class ContactMaterialAdmissibilityError(ValueError):
    """Raised when an admissibility contract itself is malformed."""


def _positive_duration(value: object) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ContactMaterialAdmissibilityError(
            "duration_seconds must be numeric"
        ) from exc
    if not math.isfinite(result) or result <= 0.0:
        raise ContactMaterialAdmissibilityError(
            "duration_seconds must be finite and greater than zero"
        )
    return result


@dataclass(frozen=True, slots=True)
class ContactMaterialTransitionProposal:
    """One passive candidate result, not an applied organism transition."""

    source_material_digest: str
    source_drive_digest: str
    source_tick: int
    duration_seconds: float
    proposed_state: ContactMaterialLayerState

    def __post_init__(self) -> None:
        for role in ("source_material_digest", "source_drive_digest"):
            if not isinstance(getattr(self, role), str) or not getattr(self, role):
                raise ContactMaterialAdmissibilityError(
                    f"{role} must be non-empty"
                )
        if (
            isinstance(self.source_tick, bool)
            or not isinstance(self.source_tick, int)
            or self.source_tick < 0
        ):
            raise ContactMaterialAdmissibilityError(
                "source_tick must be a non-negative integer"
            )
        object.__setattr__(
            self,
            "duration_seconds",
            _positive_duration(self.duration_seconds),
        )
        if not isinstance(self.proposed_state, ContactMaterialLayerState):
            raise ContactMaterialAdmissibilityError(
                "proposed_state must be a complete contact-material state"
            )
        if self.proposed_state.field_tick != self.source_tick + 1:
            raise ContactMaterialAdmissibilityError(
                "a proposal must advance exactly one material tick"
            )


@dataclass(frozen=True, slots=True)
class ContactMaterialProposalAudit:
    """Necessary physical checks; acceptance does not release a candidate."""

    source_reference_valid: bool
    drive_reference_valid: bool
    layer_identity_preserved: bool
    geometry_preserved: bool
    owners_preserved: bool
    owner_positions_preserved: bool
    owner_totals_preserved: bool
    surface_directions_preserved: bool
    local_balance_valid: bool
    nonnegative_material_valid: bool
    neutral_null_applicable: bool
    neutral_null_preserved: bool
    accepted: bool
    runtime_release_granted: bool = False


@dataclass(frozen=True, slots=True)
class SignedAxisTransform:
    """Axis permutation and reflection used only for equivariance audits."""

    axis_order: tuple[int, ...]
    axis_signs: tuple[int, ...]

    def __post_init__(self) -> None:
        order = tuple(self.axis_order)
        signs = tuple(self.axis_signs)
        if (
            not order
            or len(order) != len(signs)
            or set(order) != set(range(len(order)))
            or any(sign not in (-1, 1) for sign in signs)
        ):
            raise ContactMaterialAdmissibilityError(
                "transform must be one signed permutation of all axes"
            )
        object.__setattr__(self, "axis_order", order)
        object.__setattr__(self, "axis_signs", signs)

    def apply(self, values: tuple[int, ...]) -> tuple[int, ...]:
        if len(values) != len(self.axis_order):
            raise ContactMaterialAdmissibilityError(
                "transform and geometry dimensions must match"
            )
        return tuple(
            self.axis_signs[index] * values[source_axis]
            for index, source_axis in enumerate(self.axis_order)
        )


@dataclass(frozen=True, slots=True)
class ContactMaterialSymmetryAudit:
    """Comparison of one proposal with a transformed local situation."""

    source_material_equivalent: bool
    source_drive_equivalent: bool
    proposal_equivalent: bool
    base_proposal_admissible: bool
    transformed_proposal_admissible: bool
    accepted: bool
    runtime_release_granted: bool = False


def _material_distribution_equal(
    first: ContactMaterialLayerState,
    second: ContactMaterialLayerState,
) -> bool:
    first_by_id = {item.owner_neuron_id: item for item in first.substrates}
    second_by_id = {item.owner_neuron_id: item for item in second.substrates}
    if set(first_by_id) != set(second_by_id):
        return False
    for owner_id, left in first_by_id.items():
        right = second_by_id[owner_id]
        if (
            left.geometry_id != right.geometry_id
            or left.owner_position != right.owner_position
            or left.total_material != right.total_material
            or left.unbound_material != right.unbound_material
            or tuple(
                (item.relative_position, item.surface_material)
                for item in left.surfaces
            )
            != tuple(
                (item.relative_position, item.surface_material)
                for item in right.surfaces
            )
        ):
            return False
    return True


def _drive_is_zero(drives: StructuralContactDriveMap) -> bool:
    return all(
        (neuron.receptor_contact is None or neuron.receptor_contact == 0.0)
        and all(
            surface.owner_activation == 0.0
            and (
                not surface.local_sample_present
                or (
                    surface.local_activation == 0.0
                    and surface.signed_field_flow == 0.0
                )
            )
            for surface in neuron.surfaces
        )
        for neuron in drives.neurons
    )


def audit_contact_material_proposal(
    source: ContactMaterialLayerState,
    drives: StructuralContactDriveMap,
    proposal: ContactMaterialTransitionProposal,
) -> ContactMaterialProposalAudit:
    """Check a proposal without applying it or changing either source."""

    if not isinstance(source, ContactMaterialLayerState):
        raise ContactMaterialAdmissibilityError(
            "source must be one contact-material state"
        )
    if not isinstance(drives, StructuralContactDriveMap):
        raise ContactMaterialAdmissibilityError(
            "drives must be one structural contact drive map"
        )
    if not isinstance(proposal, ContactMaterialTransitionProposal):
        raise ContactMaterialAdmissibilityError(
            "proposal must be one passive material proposal"
        )

    target = proposal.proposed_state
    source_by_id = {item.owner_neuron_id: item for item in source.substrates}
    target_by_id = {item.owner_neuron_id: item for item in target.substrates}
    owners_preserved = set(source_by_id) == set(target_by_id)
    paired = tuple(
        (source_by_id[owner_id], target_by_id[owner_id])
        for owner_id in sorted(set(source_by_id) & set(target_by_id))
    )

    source_reference_valid = (
        proposal.source_material_digest == source.digest()
        and proposal.source_tick == source.field_tick
        and target.field_tick == source.field_tick + 1
    )
    drive_reference_valid = (
        proposal.source_drive_digest == drives.digest()
        and drives.contact_material_digest == source.digest()
        and drives.source_tick == source.field_tick
        and drives.target_tick == target.field_tick
    )
    layer_identity_preserved = target.source_layer_id == source.source_layer_id
    geometry_preserved = target.geometry_id == source.geometry_id and all(
        left.geometry_id == right.geometry_id for left, right in paired
    )
    positions_preserved = owners_preserved and all(
        left.owner_position == right.owner_position for left, right in paired
    )
    totals_preserved = owners_preserved and all(
        left.total_material == right.total_material for left, right in paired
    )
    directions_preserved = owners_preserved and all(
        tuple(item.relative_position for item in left.surfaces)
        == tuple(item.relative_position for item in right.surfaces)
        for left, right in paired
    )
    local_balance_valid = all(
        math.isclose(
            item.unbound_material
            + math.fsum(surface.surface_material for surface in item.surfaces),
            item.total_material,
            rel_tol=0.0,
            abs_tol=1e-12,
        )
        for item in target.substrates
    )
    nonnegative = all(
        item.unbound_material >= 0.0
        and all(surface.surface_material >= 0.0 for surface in item.surfaces)
        for item in target.substrates
    )
    neutral_null_applicable = source.is_neutral and _drive_is_zero(drives)
    neutral_null_preserved = (
        not neutral_null_applicable
        or _material_distribution_equal(source, target)
    )
    checks = (
        source_reference_valid,
        drive_reference_valid,
        layer_identity_preserved,
        geometry_preserved,
        owners_preserved,
        positions_preserved,
        totals_preserved,
        directions_preserved,
        local_balance_valid,
        nonnegative,
        neutral_null_preserved,
    )
    return ContactMaterialProposalAudit(
        source_reference_valid=source_reference_valid,
        drive_reference_valid=drive_reference_valid,
        layer_identity_preserved=layer_identity_preserved,
        geometry_preserved=geometry_preserved,
        owners_preserved=owners_preserved,
        owner_positions_preserved=positions_preserved,
        owner_totals_preserved=totals_preserved,
        surface_directions_preserved=directions_preserved,
        local_balance_valid=local_balance_valid,
        nonnegative_material_valid=nonnegative,
        neutral_null_applicable=neutral_null_applicable,
        neutral_null_preserved=neutral_null_preserved,
        accepted=all(checks),
    )


def _material_signature(
    state: ContactMaterialLayerState,
    transform: SignedAxisTransform | None,
) -> dict[tuple[int, ...], tuple[float, float, tuple[tuple[tuple[int, ...], float], ...]]]:
    result = {}
    for item in state.substrates:
        position = (
            item.owner_position
            if transform is None
            else transform.apply(item.owner_position)
        )
        surfaces = tuple(
            sorted(
                (
                    (
                        surface.relative_position
                        if transform is None
                        else transform.apply(surface.relative_position)
                    ),
                    surface.surface_material,
                )
                for surface in item.surfaces
            )
        )
        result[position] = (
            item.total_material,
            item.unbound_material,
            surfaces,
        )
    return result


def _drive_signature(
    drives: StructuralContactDriveMap,
    transform: SignedAxisTransform | None,
) -> dict[tuple[int, ...], tuple[float | None, tuple[tuple[object, ...], ...]]]:
    result = {}
    for item in drives.neurons:
        position = (
            item.owner_position
            if transform is None
            else transform.apply(item.owner_position)
        )
        surfaces = tuple(
            sorted(
                (
                    (
                        surface.relative_position
                        if transform is None
                        else transform.apply(surface.relative_position)
                    ),
                    surface.owner_activation,
                    surface.local_sample_present,
                    surface.local_activation,
                    surface.signed_field_flow,
                )
                for surface in item.surfaces
            )
        )
        result[position] = (item.receptor_contact, surfaces)
    return result


def audit_contact_material_symmetry(
    base_source: ContactMaterialLayerState,
    base_drives: StructuralContactDriveMap,
    base_proposal: ContactMaterialTransitionProposal,
    transformed_source: ContactMaterialLayerState,
    transformed_drives: StructuralContactDriveMap,
    transformed_proposal: ContactMaterialTransitionProposal,
    transform: SignedAxisTransform,
) -> ContactMaterialSymmetryAudit:
    """Require a transformed input to produce the transformed proposal."""

    if not isinstance(transform, SignedAxisTransform):
        raise ContactMaterialAdmissibilityError(
            "symmetry audit requires one signed axis transform"
        )
    base_audit = audit_contact_material_proposal(
        base_source,
        base_drives,
        base_proposal,
    )
    transformed_audit = audit_contact_material_proposal(
        transformed_source,
        transformed_drives,
        transformed_proposal,
    )
    source_equivalent = _material_signature(
        base_source,
        transform,
    ) == _material_signature(transformed_source, None)
    drive_equivalent = _drive_signature(
        base_drives,
        transform,
    ) == _drive_signature(transformed_drives, None)
    proposal_equivalent = _material_signature(
        base_proposal.proposed_state,
        transform,
    ) == _material_signature(transformed_proposal.proposed_state, None)
    accepted = (
        base_audit.accepted
        and transformed_audit.accepted
        and source_equivalent
        and drive_equivalent
        and proposal_equivalent
    )
    return ContactMaterialSymmetryAudit(
        source_material_equivalent=source_equivalent,
        source_drive_equivalent=drive_equivalent,
        proposal_equivalent=proposal_equivalent,
        base_proposal_admissible=base_audit.accepted,
        transformed_proposal_admissible=transformed_audit.accepted,
        accepted=accepted,
    )


def contact_material_admissibility_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            ContactMaterialTransitionProposal,
            ContactMaterialProposalAudit,
            SignedAxisTransform,
            ContactMaterialSymmetryAudit,
        )
        for item in fields(contract)
    )
