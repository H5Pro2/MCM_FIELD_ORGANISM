"""Passive finite-volume checks for owner-local radial material transport."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math

from .radial_contact_morphology import (
    NeuronRadialMaterialState,
    RadialContactMaterialLayerState,
    RadialContactProfile,
    RadialMaterialCell,
)


class RadialTransportAdmissibilityError(ValueError):
    """Raised when the radial flux contract itself is malformed."""


def _finite(value: object, role: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise RadialTransportAdmissibilityError(
            f"{role} must be numeric"
        ) from exc
    if not math.isfinite(result):
        raise RadialTransportAdmissibilityError(
            f"{role} must be finite"
        )
    return result


def _positive_duration(value: object) -> float:
    result = _finite(value, "duration_seconds")
    if result <= 0.0:
        raise RadialTransportAdmissibilityError(
            "duration_seconds must be greater than zero"
        )
    return result


def _direction(values: tuple[int, ...]) -> tuple[int, ...]:
    result = tuple(values)
    if (
        not result
        or all(value == 0 for value in result)
        or any(
            isinstance(value, bool) or not isinstance(value, int)
            for value in result
        )
    ):
        raise RadialTransportAdmissibilityError(
            "flux profile direction must be one non-zero integer offset"
        )
    return result


@dataclass(frozen=True, slots=True)
class RadialInterfaceFlux:
    """Signed material rate at one radial interface; positive points outward."""

    q_position: float
    material_rate: float

    def __post_init__(self) -> None:
        q_position = _finite(self.q_position, "q_position")
        if q_position < 0.0 or q_position > 1.0:
            raise RadialTransportAdmissibilityError(
                "q_position must stay within the normalized 0..1 interval"
            )
        object.__setattr__(self, "q_position", q_position)
        object.__setattr__(
            self,
            "material_rate",
            _finite(self.material_rate, "material_rate"),
        )

    def canonical_payload(self) -> dict[str, float]:
        return {
            "q_position": self.q_position,
            "material_rate": self.material_rate,
        }


@dataclass(frozen=True, slots=True)
class RadialProfileFluxProposal:
    """Complete interface fluxes for one owner-local radial direction."""

    relative_position: tuple[int, ...]
    interfaces: tuple[RadialInterfaceFlux, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "relative_position",
            _direction(self.relative_position),
        )
        interfaces = tuple(self.interfaces)
        if not interfaces or any(
            not isinstance(item, RadialInterfaceFlux)
            for item in interfaces
        ):
            raise RadialTransportAdmissibilityError(
                "radial profile flux requires interface rates"
            )
        positions = [item.q_position for item in interfaces]
        if len(set(positions)) != len(positions):
            raise RadialTransportAdmissibilityError(
                "radial interface positions must be unique"
            )
        object.__setattr__(
            self,
            "interfaces",
            tuple(sorted(interfaces, key=lambda item: item.q_position)),
        )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "relative_position": list(self.relative_position),
            "interfaces": [
                item.canonical_payload() for item in self.interfaces
            ],
        }


@dataclass(frozen=True, slots=True)
class NeuronRadialFluxProposal:
    """All directional fluxes for one material owner."""

    owner_neuron_id: str
    profiles: tuple[RadialProfileFluxProposal, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.owner_neuron_id, str) or not self.owner_neuron_id:
            raise RadialTransportAdmissibilityError(
                "owner_neuron_id must be non-empty"
            )
        profiles = tuple(self.profiles)
        if not profiles or any(
            not isinstance(item, RadialProfileFluxProposal)
            for item in profiles
        ):
            raise RadialTransportAdmissibilityError(
                "neuron flux proposal requires radial profiles"
            )
        directions = [item.relative_position for item in profiles]
        if len(set(directions)) != len(directions):
            raise RadialTransportAdmissibilityError(
                "neuron flux profile directions must be unique"
            )
        object.__setattr__(
            self,
            "profiles",
            tuple(sorted(profiles, key=lambda item: item.relative_position)),
        )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "owner_neuron_id": self.owner_neuron_id,
            "profiles": [
                item.canonical_payload() for item in self.profiles
            ],
        }


@dataclass(frozen=True, slots=True)
class RadialTransportProposal:
    """One complete kinematic proposal, not a material movement rule."""

    source_morphology_digest: str
    source_tick: int
    duration_seconds: float
    neurons: tuple[NeuronRadialFluxProposal, ...]

    def __post_init__(self) -> None:
        if (
            not isinstance(self.source_morphology_digest, str)
            or not self.source_morphology_digest
        ):
            raise RadialTransportAdmissibilityError(
                "source_morphology_digest must be non-empty"
            )
        if (
            isinstance(self.source_tick, bool)
            or not isinstance(self.source_tick, int)
            or self.source_tick < 0
        ):
            raise RadialTransportAdmissibilityError(
                "source_tick must be a non-negative integer"
            )
        object.__setattr__(
            self,
            "duration_seconds",
            _positive_duration(self.duration_seconds),
        )
        neurons = tuple(self.neurons)
        if not neurons or any(
            not isinstance(item, NeuronRadialFluxProposal)
            for item in neurons
        ):
            raise RadialTransportAdmissibilityError(
                "radial transport proposal requires owner fluxes"
            )
        owners = [item.owner_neuron_id for item in neurons]
        if len(set(owners)) != len(owners):
            raise RadialTransportAdmissibilityError(
                "radial transport owner identities must be unique"
            )
        object.__setattr__(
            self,
            "neurons",
            tuple(sorted(neurons, key=lambda item: item.owner_neuron_id)),
        )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "source_morphology_digest": self.source_morphology_digest,
            "source_tick": self.source_tick,
            "duration_seconds": self.duration_seconds,
            "neurons": [
                item.canonical_payload() for item in self.neurons
            ],
        }

    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class RadialTransportProposalAudit:
    """Necessary finite-volume checks; acceptance grants no causal mechanism."""

    source_reference_valid: bool
    owner_set_preserved: bool
    profile_directions_preserved: bool
    radial_resolution_preserved: bool
    interface_sets_complete: bool
    outer_boundaries_closed: bool
    reconstructed_nonnegative: bool
    owner_balances_preserved: bool
    zero_flux_applicable: bool
    zero_flux_preserved: bool
    source_state_preserved: bool
    proposed_state: RadialContactMaterialLayerState | None
    accepted: bool
    causal_source_verified: bool = False
    runtime_release_granted: bool = False


def _same_material_distribution(
    source: RadialContactMaterialLayerState,
    target: RadialContactMaterialLayerState,
) -> bool:
    if (
        source.source_layer_id != target.source_layer_id
        or source.geometry_id != target.geometry_id
        or source.radial_edges != target.radial_edges
        or source.source_contact_material_digest
        != target.source_contact_material_digest
    ):
        return False
    source_by_id = {
        item.owner_neuron_id: item for item in source.substrates
    }
    target_by_id = {
        item.owner_neuron_id: item for item in target.substrates
    }
    if set(source_by_id) != set(target_by_id):
        return False
    for owner_id, left in source_by_id.items():
        right = target_by_id[owner_id]
        if (
            left.geometry_id != right.geometry_id
            or left.owner_position != right.owner_position
            or left.total_material != right.total_material
            or left.unbound_material != right.unbound_material
            or tuple(
                (
                    profile.relative_position,
                    tuple(
                        (
                            cell.q_start,
                            cell.q_end,
                            cell.material_amount,
                        )
                        for cell in profile.cells
                    ),
                )
                for profile in left.profiles
            )
            != tuple(
                (
                    profile.relative_position,
                    tuple(
                        (
                            cell.q_start,
                            cell.q_end,
                            cell.material_amount,
                        )
                        for cell in profile.cells
                    ),
                )
                for profile in right.profiles
            )
        ):
            return False
    return True


def audit_radial_transport_proposal(
    source: RadialContactMaterialLayerState,
    proposal: RadialTransportProposal,
) -> RadialTransportProposalAudit:
    """Reconstruct one candidate state without applying it to the organism."""

    if not isinstance(source, RadialContactMaterialLayerState):
        raise RadialTransportAdmissibilityError(
            "source must be one radial contact-material state"
        )
    if not isinstance(proposal, RadialTransportProposal):
        raise RadialTransportAdmissibilityError(
            "proposal must be one radial transport proposal"
        )

    source_digest = source.digest()
    source_by_id = {
        item.owner_neuron_id: item for item in source.substrates
    }
    proposal_by_id = {
        item.owner_neuron_id: item for item in proposal.neurons
    }
    owner_set_preserved = set(source_by_id) == set(proposal_by_id)
    paired_owner_ids = sorted(set(source_by_id) & set(proposal_by_id))
    expected_interfaces = source.radial_edges

    profile_directions_preserved = owner_set_preserved
    radial_resolution_preserved = owner_set_preserved
    interface_sets_complete = owner_set_preserved
    outer_boundaries_closed = owner_set_preserved
    reconstructed_nonnegative = owner_set_preserved
    owner_balances_preserved = owner_set_preserved
    zero_flux_applicable = owner_set_preserved
    rebuilt_owners = []

    for owner_id in paired_owner_ids:
        material = source_by_id[owner_id]
        fluxes = proposal_by_id[owner_id]
        material_by_direction = {
            item.relative_position: item for item in material.profiles
        }
        flux_by_direction = {
            item.relative_position: item for item in fluxes.profiles
        }
        if set(material_by_direction) != set(flux_by_direction):
            profile_directions_preserved = False
            radial_resolution_preserved = False
            interface_sets_complete = False
            outer_boundaries_closed = False
            reconstructed_nonnegative = False
            owner_balances_preserved = False
            zero_flux_applicable = False
            continue

        owner_profiles = []
        core_flux_total = 0.0
        owner_valid = True
        all_owner_rates_zero = True
        for direction in sorted(material_by_direction):
            profile = material_by_direction[direction]
            profile_flux = flux_by_direction[direction]
            q_positions = tuple(
                item.q_position for item in profile_flux.interfaces
            )
            if q_positions != expected_interfaces:
                radial_resolution_preserved = False
                interface_sets_complete = False
                outer_boundaries_closed = False
                reconstructed_nonnegative = False
                owner_balances_preserved = False
                zero_flux_applicable = False
                owner_valid = False
                continue

            rates = tuple(
                item.material_rate for item in profile_flux.interfaces
            )
            all_owner_rates_zero = all_owner_rates_zero and all(
                rate == 0.0 for rate in rates
            )
            if rates[-1] != 0.0:
                outer_boundaries_closed = False
                reconstructed_nonnegative = False
                owner_balances_preserved = False
                owner_valid = False
                continue

            core_flux_total += rates[0]
            cells = []
            for index, cell in enumerate(profile.cells):
                amount = cell.material_amount + proposal.duration_seconds * (
                    rates[index] - rates[index + 1]
                )
                if amount < 0.0:
                    reconstructed_nonnegative = False
                    owner_valid = False
                    break
                cells.append(
                    RadialMaterialCell(
                        cell.q_start,
                        cell.q_end,
                        amount,
                    )
                )
            if not owner_valid:
                continue
            owner_profiles.append(
                RadialContactProfile(direction, tuple(cells))
            )

        zero_flux_applicable = zero_flux_applicable and all_owner_rates_zero
        if not owner_valid or len(owner_profiles) != len(material.profiles):
            continue

        unbound = material.unbound_material - (
            proposal.duration_seconds * core_flux_total
        )
        if unbound < 0.0:
            reconstructed_nonnegative = False
            owner_balances_preserved = False
            continue
        accounted = unbound + math.fsum(
            item.material_amount for item in owner_profiles
        )
        balance_valid = math.isclose(
            accounted,
            material.total_material,
            rel_tol=0.0,
            abs_tol=1e-12,
        )
        owner_balances_preserved = owner_balances_preserved and balance_valid
        if not balance_valid:
            continue
        rebuilt_owners.append(
            NeuronRadialMaterialState(
                owner_neuron_id=material.owner_neuron_id,
                geometry_id=material.geometry_id,
                owner_position=material.owner_position,
                field_tick=source.field_tick + 1,
                total_material=material.total_material,
                unbound_material=unbound,
                profiles=tuple(owner_profiles),
            )
        )

    source_reference_valid = (
        proposal.source_morphology_digest == source_digest
        and proposal.source_tick == source.field_tick
    )
    structural_checks = (
        source_reference_valid,
        owner_set_preserved,
        profile_directions_preserved,
        radial_resolution_preserved,
        interface_sets_complete,
        outer_boundaries_closed,
        reconstructed_nonnegative,
        owner_balances_preserved,
        len(rebuilt_owners) == len(source.substrates),
    )
    proposed_state = None
    if all(structural_checks):
        proposed_state = RadialContactMaterialLayerState(
            source_layer_id=source.source_layer_id,
            geometry_id=source.geometry_id,
            field_tick=source.field_tick + 1,
            radial_edges=source.radial_edges,
            source_contact_material_digest=(
                source.source_contact_material_digest
            ),
            substrates=tuple(rebuilt_owners),
        )
    zero_flux_preserved = (
        not zero_flux_applicable
        or (
            proposed_state is not None
            and _same_material_distribution(source, proposed_state)
        )
    )
    source_state_preserved = source.digest() == source_digest
    accepted = (
        all(structural_checks)
        and zero_flux_preserved
        and source_state_preserved
    )

    return RadialTransportProposalAudit(
        source_reference_valid=source_reference_valid,
        owner_set_preserved=owner_set_preserved,
        profile_directions_preserved=profile_directions_preserved,
        radial_resolution_preserved=radial_resolution_preserved,
        interface_sets_complete=interface_sets_complete,
        outer_boundaries_closed=outer_boundaries_closed,
        reconstructed_nonnegative=reconstructed_nonnegative,
        owner_balances_preserved=owner_balances_preserved,
        zero_flux_applicable=zero_flux_applicable,
        zero_flux_preserved=zero_flux_preserved,
        source_state_preserved=source_state_preserved,
        proposed_state=proposed_state,
        accepted=accepted,
    )


def radial_transport_admissibility_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            RadialInterfaceFlux,
            RadialProfileFluxProposal,
            NeuronRadialFluxProposal,
            RadialTransportProposal,
            RadialTransportProposalAudit,
        )
        for item in fields(contract)
    )
