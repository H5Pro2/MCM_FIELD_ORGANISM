"""Passive alignment of existing field causes with neutral contact surfaces."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math

from .mcm_neuron import MCMNeuron
from .mcm_neuron_layer import MCMNeuronLayer
from .structural_contact_substrate import ContactMaterialLayerState


class StructuralContactDriveError(ValueError):
    """Raised when field causes cannot be aligned with contact anatomy."""


def _finite(value: object, role: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise StructuralContactDriveError(f"{role} must be numeric") from exc
    if not math.isfinite(result):
        raise StructuralContactDriveError(f"{role} must be finite")
    return result


@dataclass(frozen=True, slots=True)
class LocalContactSurfaceDrive:
    """Existing Vortakt field cause at one owner-local surface direction."""

    relative_position: tuple[int, ...]
    owner_activation: float
    local_sample_present: bool
    local_activation: float | None
    signed_field_flow: float | None

    def __post_init__(self) -> None:
        direction = tuple(self.relative_position)
        if not direction or all(value == 0 for value in direction):
            raise StructuralContactDriveError(
                "surface drive requires one non-zero local direction"
            )
        if any(isinstance(value, bool) or not isinstance(value, int) for value in direction):
            raise StructuralContactDriveError(
                "surface drive direction must contain integers"
            )
        object.__setattr__(self, "relative_position", direction)
        object.__setattr__(
            self,
            "owner_activation",
            _finite(self.owner_activation, "owner_activation"),
        )
        if not isinstance(self.local_sample_present, bool):
            raise StructuralContactDriveError(
                "local_sample_present must be boolean"
            )
        if self.local_sample_present:
            if self.local_activation is None or self.signed_field_flow is None:
                raise StructuralContactDriveError(
                    "a present local sample requires activation and field flow"
                )
            object.__setattr__(
                self,
                "local_activation",
                _finite(self.local_activation, "local_activation"),
            )
            object.__setattr__(
                self,
                "signed_field_flow",
                _finite(self.signed_field_flow, "signed_field_flow"),
            )
        elif self.local_activation is not None or self.signed_field_flow is not None:
            raise StructuralContactDriveError(
                "an empty surface direction cannot carry a local field drive"
            )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "relative_position": list(self.relative_position),
            "owner_activation": self.owner_activation,
            "local_sample_present": self.local_sample_present,
            "local_activation": self.local_activation,
            "signed_field_flow": self.signed_field_flow,
        }


@dataclass(frozen=True, slots=True)
class NeuronContactDrive:
    """One neuron's causal fast-field inputs without a material update rule."""

    owner_neuron_id: str
    owner_position: tuple[int, ...]
    source_tick: int
    target_tick: int
    receptor_contact: float | None
    surfaces: tuple[LocalContactSurfaceDrive, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.owner_neuron_id, str) or not self.owner_neuron_id:
            raise StructuralContactDriveError("owner_neuron_id must be non-empty")
        position = tuple(self.owner_position)
        if not position or any(
            isinstance(value, bool) or not isinstance(value, int)
            for value in position
        ):
            raise StructuralContactDriveError(
                "owner_position must contain integers"
            )
        object.__setattr__(self, "owner_position", position)
        if (
            isinstance(self.source_tick, bool)
            or isinstance(self.target_tick, bool)
            or not isinstance(self.source_tick, int)
            or not isinstance(self.target_tick, int)
            or self.source_tick < 0
            or self.target_tick != self.source_tick + 1
        ):
            raise StructuralContactDriveError(
                "contact drive must span exactly one completed field tick"
            )
        if self.receptor_contact is not None:
            object.__setattr__(
                self,
                "receptor_contact",
                _finite(self.receptor_contact, "receptor_contact"),
            )
        surfaces = tuple(self.surfaces)
        if not surfaces or any(
            not isinstance(item, LocalContactSurfaceDrive) for item in surfaces
        ):
            raise StructuralContactDriveError(
                "neuron contact drive requires local surface drives"
            )
        directions = [item.relative_position for item in surfaces]
        if len(set(directions)) != len(directions):
            raise StructuralContactDriveError(
                "surface drive directions must be unique"
            )
        object.__setattr__(
            self,
            "surfaces",
            tuple(sorted(surfaces, key=lambda item: item.relative_position)),
        )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "owner_neuron_id": self.owner_neuron_id,
            "owner_position": list(self.owner_position),
            "source_tick": self.source_tick,
            "target_tick": self.target_tick,
            "receptor_contact": self.receptor_contact,
            "surfaces": [item.canonical_payload() for item in self.surfaces],
        }


@dataclass(frozen=True, slots=True)
class StructuralContactDriveMap:
    """Passive cause map beside unchanged field and contact-material states."""

    source_layer_id: str
    geometry_id: str
    source_tick: int
    target_tick: int
    response_time_seconds: float
    source_layer_digest: str
    contact_material_digest: str
    neurons: tuple[NeuronContactDrive, ...]

    def __post_init__(self) -> None:
        for role in (
            "source_layer_id",
            "geometry_id",
            "source_layer_digest",
            "contact_material_digest",
        ):
            if not isinstance(getattr(self, role), str) or not getattr(self, role):
                raise StructuralContactDriveError(f"{role} must be non-empty")
        if (
            isinstance(self.source_tick, bool)
            or isinstance(self.target_tick, bool)
            or not isinstance(self.source_tick, int)
            or not isinstance(self.target_tick, int)
            or self.source_tick < 0
            or self.target_tick != self.source_tick + 1
        ):
            raise StructuralContactDriveError(
                "drive map must span exactly one completed field tick"
            )
        response_time = _finite(
            self.response_time_seconds,
            "response_time_seconds",
        )
        if response_time <= 0.0:
            raise StructuralContactDriveError(
                "response_time_seconds must be greater than zero"
            )
        object.__setattr__(self, "response_time_seconds", response_time)
        neurons = tuple(self.neurons)
        if not neurons or any(
            not isinstance(item, NeuronContactDrive) for item in neurons
        ):
            raise StructuralContactDriveError(
                "drive map requires neuron contact drives"
            )
        owner_ids = [item.owner_neuron_id for item in neurons]
        if len(set(owner_ids)) != len(owner_ids):
            raise StructuralContactDriveError(
                "drive map neuron owners must be unique"
            )
        object.__setattr__(
            self,
            "neurons",
            tuple(sorted(neurons, key=lambda item: item.owner_neuron_id)),
        )

    @property
    def surface_count(self) -> int:
        return sum(len(item.surfaces) for item in self.neurons)

    @property
    def locally_sampled_surface_count(self) -> int:
        return sum(
            surface.local_sample_present
            for neuron in self.neurons
            for surface in neuron.surfaces
        )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "source_layer_id": self.source_layer_id,
            "geometry_id": self.geometry_id,
            "source_tick": self.source_tick,
            "target_tick": self.target_tick,
            "response_time_seconds": self.response_time_seconds,
            "source_layer_digest": self.source_layer_digest,
            "contact_material_digest": self.contact_material_digest,
            "neurons": [item.canonical_payload() for item in self.neurons],
        }

    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def _mapped_position(
    layer: MCMNeuronLayer,
    neuron: MCMNeuron,
    offset: tuple[int, ...],
) -> tuple[int, ...]:
    values = [
        coordinate + delta
        for coordinate, delta in zip(neuron.position, offset, strict=True)
    ]
    for axis in layer.periodic_axes:
        values[axis.axis_index] = axis.origin + (
            (values[axis.axis_index] - axis.origin) % axis.size
        )
    return tuple(values)


def map_structural_contact_drives(
    contact_material: ContactMaterialLayerState,
    source_layer: MCMNeuronLayer,
    driven_layer: MCMNeuronLayer,
    *,
    response_time_seconds: float,
) -> StructuralContactDriveMap:
    """Align causal fast-field inputs with surfaces without writing material."""

    if not isinstance(contact_material, ContactMaterialLayerState):
        raise StructuralContactDriveError(
            "contact_material must be one completed anatomy state"
        )
    if not isinstance(source_layer, MCMNeuronLayer) or not isinstance(
        driven_layer, MCMNeuronLayer
    ):
        raise StructuralContactDriveError(
            "source_layer and driven_layer must be completed MCM layers"
        )
    response_time = _finite(response_time_seconds, "response_time_seconds")
    if response_time <= 0.0:
        raise StructuralContactDriveError(
            "response_time_seconds must be greater than zero"
        )
    if (
        contact_material.source_layer_id != source_layer.layer_id
        or contact_material.geometry_id != source_layer.neurons[0].geometry_id
        or contact_material.field_tick != source_layer.tick
    ):
        raise StructuralContactDriveError(
            "contact anatomy must describe the completed source layer"
        )
    if (
        driven_layer.layer_id != source_layer.layer_id
        or driven_layer.neurons[0].geometry_id
        != source_layer.neurons[0].geometry_id
        or driven_layer.tick != source_layer.tick + 1
    ):
        raise StructuralContactDriveError(
            "driven layer must be the next state of the same field anatomy"
        )

    source_by_id = {item.neuron_id: item for item in source_layer.neurons}
    driven_by_id = {item.neuron_id: item for item in driven_layer.neurons}
    material_by_id = {
        item.owner_neuron_id: item for item in contact_material.substrates
    }
    if set(source_by_id) != set(driven_by_id) or set(source_by_id) != set(
        material_by_id
    ):
        raise StructuralContactDriveError(
            "field layers and contact material must contain the same neurons"
        )
    position_map = {item.position: item for item in source_layer.neurons}
    rate = 1.0 / response_time
    neuron_drives = []

    for owner_id, source in source_by_id.items():
        driven = driven_by_id[owner_id]
        material = material_by_id[owner_id]
        if (
            driven.position != source.position
            or material.owner_position != source.position
            or tuple(surface.relative_position for surface in material.surfaces)
            != tuple(sorted(source_layer.sample_offsets))
        ):
            raise StructuralContactDriveError(
                "contact surfaces must match the source neuron geometry"
            )
        samples = {
            sample.relative_position: sample
            for sample in driven.perception.local_samples
        }
        if set(samples) - set(source_layer.sample_offsets):
            raise StructuralContactDriveError(
                "driven perception contains an unknown local direction"
            )
        surface_drives = []
        for surface in material.surfaces:
            offset = surface.relative_position
            expected = position_map.get(_mapped_position(source_layer, source, offset))
            sample = samples.get(offset)
            if expected is None:
                if sample is not None:
                    raise StructuralContactDriveError(
                        "empty local geometry cannot expose a field sample"
                    )
                surface_drives.append(
                    LocalContactSurfaceDrive(
                        offset,
                        source.activation,
                        False,
                        None,
                        None,
                    )
                )
                continue
            if (
                sample is None
                or sample.source_tick != source_layer.tick
                or sample.source_field_id != source.field_id
                or sample.activation != expected.activation
                or sample.afterimage != expected.afterimage
            ):
                raise StructuralContactDriveError(
                    "local field sample does not match the completed source layer"
                )
            surface_drives.append(
                LocalContactSurfaceDrive(
                    offset,
                    source.activation,
                    True,
                    sample.activation,
                    rate * (sample.activation - source.activation),
                )
            )
        neuron_drives.append(
            NeuronContactDrive(
                owner_neuron_id=owner_id,
                owner_position=source.position,
                source_tick=source_layer.tick,
                target_tick=driven_layer.tick,
                receptor_contact=driven.perception.receptor_contact,
                surfaces=tuple(surface_drives),
            )
        )

    return StructuralContactDriveMap(
        source_layer_id=source_layer.layer_id,
        geometry_id=source_layer.neurons[0].geometry_id,
        source_tick=source_layer.tick,
        target_tick=driven_layer.tick,
        response_time_seconds=response_time,
        source_layer_digest=source_layer.digest(),
        contact_material_digest=contact_material.digest(),
        neurons=tuple(neuron_drives),
    )


def structural_contact_drive_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            LocalContactSurfaceDrive,
            NeuronContactDrive,
            StructuralContactDriveMap,
        )
        for item in fields(contract)
    )
