"""Immutable anatomy contract for local structural contact material."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math
import re
from typing import Iterable

from .mcm_neuron_layer import MCMNeuronLayer


class StructuralContactSubstrateError(ValueError):
    """Raised when structural contact anatomy violates its neutral contract."""


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")


def _identifier(value: object, role: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise StructuralContactSubstrateError(
            f"{role} must be a lowercase technical identifier"
        )
    return value


def _tick(value: object, role: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise StructuralContactSubstrateError(
            f"{role} must be a non-negative integer"
        )
    return value


def _position(
    values: Iterable[int],
    role: str,
    *,
    allow_origin: bool,
) -> tuple[int, ...]:
    result = tuple(values)
    if not result:
        raise StructuralContactSubstrateError(f"{role} cannot be empty")
    if any(
        isinstance(value, bool) or not isinstance(value, int)
        for value in result
    ):
        raise StructuralContactSubstrateError(
            f"{role} must contain only integers"
        )
    if not allow_origin and all(value == 0 for value in result):
        raise StructuralContactSubstrateError(
            f"{role} cannot address the neuron center"
        )
    return result


def _material_amount(
    value: object,
    role: str,
    *,
    positive: bool,
) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise StructuralContactSubstrateError(
            f"{role} must be numeric"
        ) from exc
    if not math.isfinite(result) or result < 0.0 or (positive and result == 0.0):
        requirement = "finite and greater than zero" if positive else "finite and non-negative"
        raise StructuralContactSubstrateError(f"{role} must be {requirement}")
    return result


@dataclass(frozen=True, slots=True)
class LocalContactSurface:
    """One owner-local spatial surface, not a partner or stored edge."""

    relative_position: tuple[int, ...]
    surface_material: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "relative_position",
            _position(
                self.relative_position,
                "relative_position",
                allow_origin=False,
            ),
        )
        object.__setattr__(
            self,
            "surface_material",
            _material_amount(
                self.surface_material,
                "surface_material",
                positive=False,
            ),
        )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "relative_position": list(self.relative_position),
            "surface_material": self.surface_material,
        }


@dataclass(frozen=True, slots=True)
class NeuronContactMaterialState:
    """Finite contact material owned by one neuron without partner identity."""

    owner_neuron_id: str
    geometry_id: str
    owner_position: tuple[int, ...]
    field_tick: int
    total_material: float
    unbound_material: float
    surfaces: tuple[LocalContactSurface, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "owner_neuron_id",
            _identifier(self.owner_neuron_id, "owner_neuron_id"),
        )
        object.__setattr__(
            self,
            "geometry_id",
            _identifier(self.geometry_id, "geometry_id"),
        )
        position = _position(
            self.owner_position,
            "owner_position",
            allow_origin=True,
        )
        object.__setattr__(self, "owner_position", position)
        object.__setattr__(
            self,
            "field_tick",
            _tick(self.field_tick, "field_tick"),
        )
        total = _material_amount(
            self.total_material,
            "total_material",
            positive=True,
        )
        unbound = _material_amount(
            self.unbound_material,
            "unbound_material",
            positive=False,
        )
        object.__setattr__(self, "total_material", total)
        object.__setattr__(self, "unbound_material", unbound)

        surfaces = tuple(self.surfaces)
        if not surfaces or any(
            not isinstance(surface, LocalContactSurface)
            for surface in surfaces
        ):
            raise StructuralContactSubstrateError(
                "surfaces must contain local contact surfaces"
            )
        directions = [surface.relative_position for surface in surfaces]
        if len(set(directions)) != len(directions):
            raise StructuralContactSubstrateError(
                "local contact surface directions must be unique"
            )
        if any(len(direction) != len(position) for direction in directions):
            raise StructuralContactSubstrateError(
                "contact surfaces and owner position must share one dimension"
            )
        accounted = unbound + math.fsum(
            surface.surface_material for surface in surfaces
        )
        if not math.isclose(
            accounted,
            total,
            rel_tol=0.0,
            abs_tol=1e-12,
        ):
            raise StructuralContactSubstrateError(
                "unbound and surface material must conserve the finite total"
            )
        object.__setattr__(
            self,
            "surfaces",
            tuple(sorted(surfaces, key=lambda item: item.relative_position)),
        )

    @property
    def is_neutral(self) -> bool:
        return (
            self.unbound_material == self.total_material
            and all(surface.surface_material == 0.0 for surface in self.surfaces)
        )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "owner_neuron_id": self.owner_neuron_id,
            "geometry_id": self.geometry_id,
            "owner_position": list(self.owner_position),
            "field_tick": self.field_tick,
            "total_material": self.total_material,
            "unbound_material": self.unbound_material,
            "surfaces": [
                surface.canonical_payload() for surface in self.surfaces
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
class ContactMaterialLayerState:
    """One complete contact-material snapshot beside the unchanged field."""

    source_layer_id: str
    geometry_id: str
    field_tick: int
    substrates: tuple[NeuronContactMaterialState, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "source_layer_id",
            _identifier(self.source_layer_id, "source_layer_id"),
        )
        geometry_id = _identifier(self.geometry_id, "geometry_id")
        field_tick = _tick(self.field_tick, "field_tick")
        object.__setattr__(self, "geometry_id", geometry_id)
        object.__setattr__(self, "field_tick", field_tick)

        substrates = tuple(self.substrates)
        if not substrates or any(
            not isinstance(item, NeuronContactMaterialState)
            for item in substrates
        ):
            raise StructuralContactSubstrateError(
                "substrates must contain neuron contact material states"
            )
        owner_ids = [item.owner_neuron_id for item in substrates]
        owner_positions = [item.owner_position for item in substrates]
        if len(set(owner_ids)) != len(owner_ids):
            raise StructuralContactSubstrateError(
                "contact material owners must be unique"
            )
        if len(set(owner_positions)) != len(owner_positions):
            raise StructuralContactSubstrateError(
                "contact material owner positions must be unique"
            )
        if any(
            item.geometry_id != geometry_id or item.field_tick != field_tick
            for item in substrates
        ):
            raise StructuralContactSubstrateError(
                "all contact material must share geometry and field tick"
            )
        direction_sets = {
            tuple(surface.relative_position for surface in item.surfaces)
            for item in substrates
        }
        if len(direction_sets) != 1:
            raise StructuralContactSubstrateError(
                "every neuron must expose the same local surface anatomy"
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
    def surface_slot_count(self) -> int:
        return sum(len(item.surfaces) for item in self.substrates)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "source_layer_id": self.source_layer_id,
            "geometry_id": self.geometry_id,
            "field_tick": self.field_tick,
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


def build_neutral_contact_material_layer(
    layer: MCMNeuronLayer,
    *,
    material_per_neuron: float,
) -> ContactMaterialLayerState:
    """Build neutral owner-local anatomy without changing the MCM layer."""

    if not isinstance(layer, MCMNeuronLayer):
        raise StructuralContactSubstrateError(
            "contact material anatomy requires one completed MCM neuron layer"
        )
    total = _material_amount(
        material_per_neuron,
        "material_per_neuron",
        positive=True,
    )
    substrates = tuple(
        NeuronContactMaterialState(
            owner_neuron_id=neuron.neuron_id,
            geometry_id=neuron.geometry_id,
            owner_position=neuron.position,
            field_tick=neuron.tick,
            total_material=total,
            unbound_material=total,
            surfaces=tuple(
                LocalContactSurface(offset, 0.0)
                for offset in layer.sample_offsets
            ),
        )
        for neuron in layer.neurons
    )
    return ContactMaterialLayerState(
        source_layer_id=layer.layer_id,
        geometry_id=layer.neurons[0].geometry_id,
        field_tick=layer.tick,
        substrates=substrates,
    )


def structural_contact_substrate_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            LocalContactSurface,
            NeuronContactMaterialState,
            ContactMaterialLayerState,
        )
        for item in fields(contract)
    )
