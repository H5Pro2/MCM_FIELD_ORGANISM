"""One shared MCM field with multiple receptor docks and one neuron layer."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import re
from typing import Iterable, Mapping

from .mcm_neuron import MCMFieldPerception, MCMNeuron
from .mcm_neuron_layer import MCMNeuronLayer, MCMNeuronTransition
from .receptor_distributor import ReceptorDistribution
from .sensor_mcm_field import ReceptorContactFrame, ReceptorNeuronDockMap


class SharedMCMFieldError(ValueError):
    """Raised when shared-field identities or causal steps do not align."""


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")


def _identifier(value: object, role: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise SharedMCMFieldError(
            f"{role} must be a lowercase technical identifier"
        )
    return value


@dataclass(frozen=True, slots=True)
class ReceptorDockAnatomy:
    """Technical placement of one receptor surface in the shared field."""

    modality_id: str
    dock_id: str
    positions: tuple[tuple[int, ...], ...]
    sample_offsets: tuple[tuple[int, ...], ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "modality_id", _identifier(self.modality_id, "modality_id")
        )
        object.__setattr__(self, "dock_id", _identifier(self.dock_id, "dock_id"))
        positions = tuple(tuple(position) for position in self.positions)
        offsets = tuple(tuple(offset) for offset in self.sample_offsets)
        if not positions or not offsets:
            raise SharedMCMFieldError(
                "dock anatomy requires local positions and sample offsets"
            )
        dimension = len(positions[0])
        if dimension == 0 or any(len(position) != dimension for position in positions):
            raise SharedMCMFieldError(
                "all local dock positions must share a non-empty dimension"
            )
        if len(set(positions)) != len(positions):
            raise SharedMCMFieldError("local dock positions must be unique")
        if any(len(offset) != dimension for offset in offsets):
            raise SharedMCMFieldError(
                "sample offsets must match the local dock dimension"
            )
        object.__setattr__(self, "positions", positions)
        object.__setattr__(self, "sample_offsets", offsets)


@dataclass(frozen=True, slots=True)
class SharedFieldDock:
    """One receptor-to-neuron map inside the common field boundary."""

    dock_id: str
    dock_map: ReceptorNeuronDockMap

    def __post_init__(self) -> None:
        object.__setattr__(self, "dock_id", _identifier(self.dock_id, "dock_id"))
        if not isinstance(self.dock_map, ReceptorNeuronDockMap):
            raise SharedMCMFieldError(
                "shared field dock requires a receptor-neuron map"
            )


@dataclass(frozen=True, slots=True)
class SharedMCMFieldSnapshot:
    """Completed current state of the whole field, not a pattern database."""

    field_id: str
    layer_id: str
    geometry_id: str
    clock_id: str
    window_start_tick: int
    window_end_tick: int
    tick: int
    neuron_ids: tuple[str, ...]
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    dock_neuron_ids: tuple[tuple[str, tuple[str, ...]], ...]

    def __post_init__(self) -> None:
        for role in ("field_id", "layer_id", "geometry_id", "clock_id"):
            object.__setattr__(self, role, _identifier(getattr(self, role), role))
        if (
            self.window_start_tick < 0
            or self.window_end_tick <= self.window_start_tick
            or self.tick < 0
        ):
            raise SharedMCMFieldError("snapshot time roles are invalid")
        neuron_ids = tuple(self.neuron_ids)
        if not neuron_ids or len(set(neuron_ids)) != len(neuron_ids):
            raise SharedMCMFieldError("snapshot neuron identities must be unique")
        if len(self.activation) != len(neuron_ids) or len(self.afterimage) != len(
            neuron_ids
        ):
            raise SharedMCMFieldError("snapshot vectors must match the neuron layer")
        dock_neuron_ids = tuple(
            (dock_id, tuple(ids)) for dock_id, ids in self.dock_neuron_ids
        )
        all_docked = [neuron_id for _, ids in dock_neuron_ids for neuron_id in ids]
        if len(set(all_docked)) != len(all_docked):
            raise SharedMCMFieldError("one neuron cannot belong to multiple docks")
        if not set(all_docked).issubset(neuron_ids):
            raise SharedMCMFieldError("dock snapshot references an unknown neuron")
        object.__setattr__(self, "neuron_ids", neuron_ids)
        object.__setattr__(
            self, "dock_neuron_ids", tuple(sorted(dock_neuron_ids))
        )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "field_id": self.field_id,
            "layer_id": self.layer_id,
            "geometry_id": self.geometry_id,
            "clock_id": self.clock_id,
            "window_start_tick": self.window_start_tick,
            "window_end_tick": self.window_end_tick,
            "tick": self.tick,
            "neuron_ids": list(self.neuron_ids),
            "activation": list(self.activation),
            "afterimage": list(self.afterimage),
            "dock_neuron_ids": [
                [dock_id, list(neuron_ids)]
                for dock_id, neuron_ids in self.dock_neuron_ids
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
class SharedMCMField:
    """One organism field; all receptor docks drive one synchronous layer."""

    layer: MCMNeuronLayer
    docks: tuple[SharedFieldDock, ...]
    last_distribution: ReceptorDistribution | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.layer, MCMNeuronLayer):
            raise SharedMCMFieldError("shared field requires one MCM neuron layer")
        docks = tuple(self.docks)
        if not docks or any(not isinstance(item, SharedFieldDock) for item in docks):
            raise SharedMCMFieldError("shared field requires receptor docks")
        dock_ids = [item.dock_id for item in docks]
        modalities = [item.dock_map.modality_id for item in docks]
        if len(set(dock_ids)) != len(dock_ids):
            raise SharedMCMFieldError("shared field dock identities must be unique")
        if len(set(modalities)) != len(modalities):
            raise SharedMCMFieldError("shared field modalities must be unique")
        mapped_ids = [
            neuron_id
            for item in docks
            for neuron_id in item.dock_map.neuron_ids
        ]
        layer_ids = {neuron.neuron_id for neuron in self.layer.neurons}
        if len(set(mapped_ids)) != len(mapped_ids):
            raise SharedMCMFieldError("one neuron cannot receive multiple docks")
        if set(mapped_ids) != set(self.layer.docked_neuron_ids):
            raise SharedMCMFieldError(
                "shared layer receptor contacts must match all dock maps"
            )
        if not set(mapped_ids).issubset(layer_ids):
            raise SharedMCMFieldError("dock map contains an unknown field neuron")
        if len({neuron.field_id for neuron in self.layer.neurons}) != 1:
            raise SharedMCMFieldError("all neurons must belong to the same field")
        object.__setattr__(self, "docks", tuple(sorted(docks, key=lambda item: item.dock_id)))

    @property
    def field_id(self) -> str:
        return self.layer.neurons[0].field_id

    @property
    def geometry_id(self) -> str:
        return self.layer.neurons[0].geometry_id

    def advance(
        self,
        distribution: ReceptorDistribution,
        transition: MCMNeuronTransition,
    ) -> "SharedMCMField":
        if not isinstance(distribution, ReceptorDistribution):
            raise SharedMCMFieldError(
                "world contact must arrive through the receptor distributor"
            )
        if self.last_distribution is not None:
            previous_time = self.last_distribution.field_time
            current_time = distribution.field_time
            if current_time.clock_id != previous_time.clock_id:
                raise SharedMCMFieldError("organism clock cannot change")
            if current_time.window_end_tick <= previous_time.window_end_tick:
                raise SharedMCMFieldError("common field time must advance")

        contacts_by_dock = {item.dock_id: item.frame for item in distribution.contacts}
        expected_docks = {item.dock_id for item in self.docks}
        unknown_docks = set(contacts_by_dock) - expected_docks
        if unknown_docks:
            raise SharedMCMFieldError(
                f"world-contact distribution contains unknown docks: {sorted(unknown_docks)}"
            )

        receptor_contacts: dict[str, float] = {}
        for dock in self.docks:
            frame = contacts_by_dock.get(dock.dock_id)
            if frame is None:
                continue
            try:
                mapped = dock.dock_map.contacts_for(frame)
            except ValueError as exc:
                raise SharedMCMFieldError(
                    f"receptor dock {dock.dock_id} rejected its frame: {exc}"
                ) from exc
            overlap = set(receptor_contacts) & set(mapped)
            if overlap:
                raise SharedMCMFieldError(
                    f"multiple docks target the same neurons: {sorted(overlap)}"
                )
            receptor_contacts.update(mapped)

        try:
            next_layer = self.layer.advance(
                receptor_contacts,
                transition,
                allow_missing_contacts=True,
            )
        except ValueError as exc:
            raise SharedMCMFieldError(f"shared neuron layer advance failed: {exc}") from exc
        return SharedMCMField(next_layer, self.docks, distribution)

    def snapshot(self) -> SharedMCMFieldSnapshot:
        if self.last_distribution is None:
            raise SharedMCMFieldError(
                "shared field has no completed receptor-driven state"
            )
        field_time = self.last_distribution.field_time
        neurons = self.layer.neurons
        return SharedMCMFieldSnapshot(
            field_id=self.field_id,
            layer_id=self.layer.layer_id,
            geometry_id=self.geometry_id,
            clock_id=field_time.clock_id,
            window_start_tick=field_time.window_start_tick,
            window_end_tick=field_time.window_end_tick,
            tick=self.layer.tick,
            neuron_ids=tuple(neuron.neuron_id for neuron in neurons),
            activation=tuple(neuron.activation for neuron in neurons),
            afterimage=tuple(neuron.afterimage for neuron in neurons),
            dock_neuron_ids=tuple(
                (dock.dock_id, dock.dock_map.neuron_ids) for dock in self.docks
            ),
        )


def build_shared_mcm_field(
    reference_frames: Iterable[ReceptorContactFrame],
    anatomies: Mapping[str, ReceptorDockAnatomy],
    *,
    field_id: str = "organism.mcm_field",
    layer_id: str = "organism.mcm_layer",
    geometry_id: str = "organism.shared.v1",
) -> SharedMCMField:
    """Build one layer; modality lanes only preserve inlet origin."""

    field_id = _identifier(field_id, "field_id")
    layer_id = _identifier(layer_id, "layer_id")
    geometry_id = _identifier(geometry_id, "geometry_id")
    frames = tuple(reference_frames)
    if not frames:
        raise SharedMCMFieldError("shared field requires reference receptor frames")
    frame_by_modality = {frame.modality_id: frame for frame in frames}
    if len(frame_by_modality) != len(frames):
        raise SharedMCMFieldError("reference modalities must be unique")
    anatomy_by_modality = dict(anatomies)
    if set(frame_by_modality) != set(anatomy_by_modality):
        raise SharedMCMFieldError(
            "dock anatomies must match the reference receptor modalities"
        )

    local_dimensions = {
        len(anatomy.positions[0]) for anatomy in anatomy_by_modality.values()
    }
    if len(local_dimensions) != 1:
        raise SharedMCMFieldError(
            "all receptor docks must expose one compatible local dimension"
        )

    neurons = []
    shared_docks = []
    shared_offsets: set[tuple[int, ...]] = set()
    for lane_index, modality_id in enumerate(sorted(frame_by_modality)):
        frame = frame_by_modality[modality_id]
        anatomy = anatomy_by_modality[modality_id]
        if anatomy.modality_id != modality_id:
            raise SharedMCMFieldError("dock anatomy modality mismatch")
        if len(anatomy.positions) != len(frame.carrier_ids):
            raise SharedMCMFieldError(
                "one local dock position is required per receptor carrier"
            )
        neuron_ids = tuple(
            f"{field_id}.{modality_id}.n{index}"
            for index in range(len(frame.carrier_ids))
        )
        for neuron_id, local_position in zip(
            neuron_ids, anatomy.positions, strict=True
        ):
            neurons.append(
                MCMNeuron(
                    neuron_id=neuron_id,
                    field_id=field_id,
                    modality_id="organism",
                    geometry_id=geometry_id,
                    position=(lane_index, *local_position),
                    activation=0.0,
                    afterimage=0.0,
                    perception=MCMFieldPerception(
                        tick=0,
                        receptor_contact=0.0,
                        local_samples=(),
                    ),
                )
            )
        for offset in anatomy.sample_offsets:
            shared_offsets.add((0, *offset))
        shared_docks.append(
            SharedFieldDock(
                dock_id=anatomy.dock_id,
                dock_map=ReceptorNeuronDockMap(
                    modality_id=modality_id,
                    receptor_geometry_id=frame.geometry_id,
                    pairs=tuple(
                        zip(frame.carrier_ids, neuron_ids, strict=True)
                    ),
                ),
            )
        )

    layer = MCMNeuronLayer(
        layer_id=layer_id,
        neurons=tuple(neurons),
        sample_offsets=tuple(shared_offsets),
    )
    return SharedMCMField(layer=layer, docks=tuple(shared_docks))


def shared_mcm_field_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            ReceptorDockAnatomy,
            SharedFieldDock,
            SharedMCMFieldSnapshot,
            SharedMCMField,
        )
        for item in fields(cls)
    )
