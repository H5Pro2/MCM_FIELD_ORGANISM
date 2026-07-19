"""Neutral finite radial morphology for owner-local contact material."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math
from typing import Iterable

from .structural_contact_substrate import ContactMaterialLayerState


class RadialContactMorphologyError(ValueError):
    """Raised when radial material anatomy violates its neutral contract."""


def _finite(value: object, role: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise RadialContactMorphologyError(f"{role} must be numeric") from exc
    if not math.isfinite(result):
        raise RadialContactMorphologyError(f"{role} must be finite")
    return result


def _radial_edges(values: Iterable[float]) -> tuple[float, ...]:
    edges = tuple(_finite(value, "radial edge") for value in values)
    if len(edges) < 2:
        raise RadialContactMorphologyError(
            "radial geometry requires at least two edges"
        )
    if edges[0] != 0.0 or edges[-1] != 1.0:
        raise RadialContactMorphologyError(
            "radial geometry must span the normalized 0..1 interval"
        )
    if any(left >= right for left, right in zip(edges, edges[1:], strict=False)):
        raise RadialContactMorphologyError(
            "radial geometry edges must be strictly increasing"
        )
    return edges


def _direction(values: Iterable[int]) -> tuple[int, ...]:
    result = tuple(values)
    if (
        not result
        or all(value == 0 for value in result)
        or any(isinstance(value, bool) or not isinstance(value, int) for value in result)
    ):
        raise RadialContactMorphologyError(
            "radial profile direction must be one non-zero integer offset"
        )
    return result


def _position(values: Iterable[int]) -> tuple[int, ...]:
    result = tuple(values)
    if not result or any(
        isinstance(value, bool) or not isinstance(value, int) for value in result
    ):
        raise RadialContactMorphologyError(
            "owner position must contain integers"
        )
    return result


def _material(value: object, role: str, *, positive: bool = False) -> float:
    result = _finite(value, role)
    if result < 0.0 or (positive and result == 0.0):
        requirement = "greater than zero" if positive else "non-negative"
        raise RadialContactMorphologyError(f"{role} must be {requirement}")
    return result


@dataclass(frozen=True, slots=True)
class RadialMaterialCell:
    """One anonymous radial support interval, not a material particle."""

    q_start: float
    q_end: float
    material_amount: float

    def __post_init__(self) -> None:
        start = _finite(self.q_start, "q_start")
        end = _finite(self.q_end, "q_end")
        if start < 0.0 or end > 1.0 or start >= end:
            raise RadialContactMorphologyError(
                "radial cell must lie within 0..1 and have positive width"
            )
        object.__setattr__(self, "q_start", start)
        object.__setattr__(self, "q_end", end)
        object.__setattr__(
            self,
            "material_amount",
            _material(self.material_amount, "material_amount"),
        )

    @property
    def is_boundary_cell(self) -> bool:
        return self.q_end == 1.0

    def canonical_payload(self) -> dict[str, object]:
        return {
            "q_start": self.q_start,
            "q_end": self.q_end,
            "material_amount": self.material_amount,
        }


@dataclass(frozen=True, slots=True)
class RadialContactProfile:
    """Owner-local material distribution along one anatomical direction."""

    relative_position: tuple[int, ...]
    cells: tuple[RadialMaterialCell, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "relative_position",
            _direction(self.relative_position),
        )
        cells = tuple(self.cells)
        if not cells or any(not isinstance(item, RadialMaterialCell) for item in cells):
            raise RadialContactMorphologyError(
                "radial profile requires material cells"
            )
        if cells[0].q_start != 0.0 or cells[-1].q_end != 1.0:
            raise RadialContactMorphologyError(
                "radial profile must span the complete normalized direction"
            )
        if any(
            left.q_end != right.q_start
            for left, right in zip(cells, cells[1:], strict=False)
        ):
            raise RadialContactMorphologyError(
                "radial profile cells must form one contiguous partition"
            )
        object.__setattr__(self, "cells", cells)

    @property
    def material_amount(self) -> float:
        return math.fsum(item.material_amount for item in self.cells)

    @property
    def boundary_material(self) -> float:
        return self.cells[-1].material_amount

    def canonical_payload(self) -> dict[str, object]:
        return {
            "relative_position": list(self.relative_position),
            "cells": [item.canonical_payload() for item in self.cells],
        }


@dataclass(frozen=True, slots=True)
class NeuronRadialMaterialState:
    """Finite owner material plus anonymous radial directional profiles."""

    owner_neuron_id: str
    geometry_id: str
    owner_position: tuple[int, ...]
    field_tick: int
    total_material: float
    unbound_material: float
    profiles: tuple[RadialContactProfile, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.owner_neuron_id, str) or not self.owner_neuron_id:
            raise RadialContactMorphologyError(
                "owner_neuron_id must be non-empty"
            )
        if not isinstance(self.geometry_id, str) or not self.geometry_id:
            raise RadialContactMorphologyError("geometry_id must be non-empty")
        object.__setattr__(self, "owner_position", _position(self.owner_position))
        if (
            isinstance(self.field_tick, bool)
            or not isinstance(self.field_tick, int)
            or self.field_tick < 0
        ):
            raise RadialContactMorphologyError(
                "field_tick must be a non-negative integer"
            )
        total = _material(self.total_material, "total_material", positive=True)
        unbound = _material(self.unbound_material, "unbound_material")
        object.__setattr__(self, "total_material", total)
        object.__setattr__(self, "unbound_material", unbound)
        profiles = tuple(self.profiles)
        if not profiles or any(
            not isinstance(item, RadialContactProfile) for item in profiles
        ):
            raise RadialContactMorphologyError(
                "neuron radial state requires directional profiles"
            )
        directions = [item.relative_position for item in profiles]
        if len(set(directions)) != len(directions):
            raise RadialContactMorphologyError(
                "radial profile directions must be unique"
            )
        accounted = unbound + math.fsum(
            item.material_amount for item in profiles
        )
        if not math.isclose(accounted, total, rel_tol=0.0, abs_tol=1e-12):
            raise RadialContactMorphologyError(
                "unbound and radial material must conserve the owner total"
            )
        object.__setattr__(
            self,
            "profiles",
            tuple(sorted(profiles, key=lambda item: item.relative_position)),
        )

    @property
    def is_neutral(self) -> bool:
        return (
            self.unbound_material == self.total_material
            and all(item.material_amount == 0.0 for item in self.profiles)
        )

    @property
    def has_boundary_material(self) -> bool:
        return any(item.boundary_material > 0.0 for item in self.profiles)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "owner_neuron_id": self.owner_neuron_id,
            "geometry_id": self.geometry_id,
            "owner_position": list(self.owner_position),
            "field_tick": self.field_tick,
            "total_material": self.total_material,
            "unbound_material": self.unbound_material,
            "profiles": [item.canonical_payload() for item in self.profiles],
        }


@dataclass(frozen=True, slots=True)
class RadialContactMaterialLayerState:
    """Complete neutral radial anatomy beside the unchanged organism field."""

    source_layer_id: str
    geometry_id: str
    field_tick: int
    radial_edges: tuple[float, ...]
    source_contact_material_digest: str
    substrates: tuple[NeuronRadialMaterialState, ...]

    def __post_init__(self) -> None:
        for role in (
            "source_layer_id",
            "geometry_id",
            "source_contact_material_digest",
        ):
            if not isinstance(getattr(self, role), str) or not getattr(self, role):
                raise RadialContactMorphologyError(f"{role} must be non-empty")
        if (
            isinstance(self.field_tick, bool)
            or not isinstance(self.field_tick, int)
            or self.field_tick < 0
        ):
            raise RadialContactMorphologyError(
                "field_tick must be a non-negative integer"
            )
        edges = _radial_edges(self.radial_edges)
        object.__setattr__(self, "radial_edges", edges)
        substrates = tuple(self.substrates)
        if not substrates or any(
            not isinstance(item, NeuronRadialMaterialState)
            for item in substrates
        ):
            raise RadialContactMorphologyError(
                "radial layer requires neuron material states"
            )
        owners = [item.owner_neuron_id for item in substrates]
        positions = [item.owner_position for item in substrates]
        if len(set(owners)) != len(owners) or len(set(positions)) != len(positions):
            raise RadialContactMorphologyError(
                "radial layer owners and positions must be unique"
            )
        expected_intervals = tuple(zip(edges, edges[1:], strict=False))
        for item in substrates:
            if item.geometry_id != self.geometry_id or item.field_tick != self.field_tick:
                raise RadialContactMorphologyError(
                    "all radial material must share layer geometry and tick"
                )
            if any(
                tuple((cell.q_start, cell.q_end) for cell in profile.cells)
                != expected_intervals
                for profile in item.profiles
            ):
                raise RadialContactMorphologyError(
                    "every profile must use the layer radial geometry"
                )
        direction_sets = {
            tuple(profile.relative_position for profile in item.profiles)
            for item in substrates
        }
        if len(direction_sets) != 1:
            raise RadialContactMorphologyError(
                "every neuron must expose the same radial directions"
            )
        object.__setattr__(
            self,
            "substrates",
            tuple(sorted(substrates, key=lambda item: item.owner_neuron_id)),
        )

    @property
    def is_neutral(self) -> bool:
        return all(item.is_neutral for item in self.substrates)

    @property
    def profile_count(self) -> int:
        return sum(len(item.profiles) for item in self.substrates)

    @property
    def radial_cell_count(self) -> int:
        return sum(
            len(profile.cells)
            for item in self.substrates
            for profile in item.profiles
        )

    @property
    def has_boundary_material(self) -> bool:
        return any(item.has_boundary_material for item in self.substrates)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "source_layer_id": self.source_layer_id,
            "geometry_id": self.geometry_id,
            "field_tick": self.field_tick,
            "radial_edges": list(self.radial_edges),
            "source_contact_material_digest": self.source_contact_material_digest,
            "substrates": [
                item.canonical_payload() for item in self.substrates
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


def build_neutral_radial_contact_morphology(
    contact_material: ContactMaterialLayerState,
    *,
    radial_edges: Iterable[float],
) -> RadialContactMaterialLayerState:
    """Expand neutral surface accounting into empty radial profile anatomy."""

    if not isinstance(contact_material, ContactMaterialLayerState):
        raise RadialContactMorphologyError(
            "radial morphology requires one contact-material state"
        )
    if not contact_material.is_neutral:
        raise RadialContactMorphologyError(
            "radial anatomy can only expand neutral unbound material"
        )
    edges = _radial_edges(radial_edges)
    cells = tuple(
        RadialMaterialCell(start, end, 0.0)
        for start, end in zip(edges, edges[1:], strict=False)
    )
    substrates = tuple(
        NeuronRadialMaterialState(
            owner_neuron_id=item.owner_neuron_id,
            geometry_id=item.geometry_id,
            owner_position=item.owner_position,
            field_tick=item.field_tick,
            total_material=item.total_material,
            unbound_material=item.unbound_material,
            profiles=tuple(
                RadialContactProfile(
                    surface.relative_position,
                    cells,
                )
                for surface in item.surfaces
            ),
        )
        for item in contact_material.substrates
    )
    return RadialContactMaterialLayerState(
        source_layer_id=contact_material.source_layer_id,
        geometry_id=contact_material.geometry_id,
        field_tick=contact_material.field_tick,
        radial_edges=edges,
        source_contact_material_digest=contact_material.digest(),
        substrates=substrates,
    )


def radial_contact_morphology_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            RadialMaterialCell,
            RadialContactProfile,
            NeuronRadialMaterialState,
            RadialContactMaterialLayerState,
        )
        for item in fields(contract)
    )
