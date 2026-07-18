"""Atomic spatial runtime shell for MCM neurons without a fixed field rule."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
from typing import Callable, Iterable, Mapping

from .mcm_neuron import (
    MCMFieldPerception,
    MCMFieldSample,
    MCMNeuron,
    MCMNeuronValidationError,
)
from .field_step_time import MCMFieldStepTime


class MCMNeuronLayerError(ValueError):
    """Raised when a neuron layer violates geometry or atomic-time invariants."""


@dataclass(frozen=True, slots=True)
class MCMNeuronDrive:
    """Causal transition input: prior self-state plus next local perception."""

    previous: MCMNeuron
    perception: MCMFieldPerception
    step_time: MCMFieldStepTime | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.previous, MCMNeuron):
            raise MCMNeuronLayerError("previous must be a completed MCM neuron state")
        if not isinstance(self.perception, MCMFieldPerception):
            raise MCMNeuronLayerError("perception must be a completed MCM field perception")
        if self.perception.tick != self.previous.tick + 1:
            raise MCMNeuronLayerError(
                "neuron perception must advance exactly one completed field tick"
            )
        if self.step_time is not None and not isinstance(
            self.step_time, MCMFieldStepTime
        ):
            raise MCMNeuronLayerError(
                "step_time must be a passive MCMFieldStepTime contract"
            )


@dataclass(frozen=True, slots=True)
class MCMNeuronOutput:
    """Minimal transition output; meaning and topology are deliberately absent."""

    activation: float
    afterimage: float


MCMNeuronTransition = Callable[[MCMNeuronDrive], MCMNeuronOutput]


@dataclass(frozen=True, slots=True)
class PeriodicSamplingAxis:
    """One explicit technical wrap axis, not a stored field relationship."""

    axis_index: int
    origin: int
    size: int

    def __post_init__(self) -> None:
        for role in ("axis_index", "origin", "size"):
            value = getattr(self, role)
            if isinstance(value, bool) or not isinstance(value, int):
                raise MCMNeuronLayerError(f"{role} must be an integer")
        if self.axis_index < 0:
            raise MCMNeuronLayerError("axis_index must be non-negative")
        if self.size < 2:
            raise MCMNeuronLayerError("periodic axis size must be at least two")

    def canonical_payload(self) -> dict[str, int]:
        return {item.name: getattr(self, item.name) for item in fields(self)}


def advance_mcm_neuron(
    previous: MCMNeuron,
    perception: MCMFieldPerception,
    transition: MCMNeuronTransition,
    *,
    step_time: MCMFieldStepTime | None = None,
) -> MCMNeuron:
    """Advance one neuron through an explicit transition without hidden defaults."""

    if not callable(transition):
        raise MCMNeuronLayerError("transition must be callable")
    drive = MCMNeuronDrive(
        previous=previous,
        perception=perception,
        step_time=step_time,
    )
    before = previous.digest()
    output = transition(drive)
    if not isinstance(output, MCMNeuronOutput):
        raise MCMNeuronLayerError("transition must return MCMNeuronOutput")
    if previous.digest() != before:
        raise MCMNeuronLayerError("transition changed the immutable previous neuron")
    try:
        return MCMNeuron(
            neuron_id=previous.neuron_id,
            field_id=previous.field_id,
            modality_id=previous.modality_id,
            geometry_id=previous.geometry_id,
            position=previous.position,
            activation=output.activation,
            afterimage=output.afterimage,
            perception=perception,
        )
    except MCMNeuronValidationError as exc:
        raise MCMNeuronLayerError(f"invalid neuron transition output: {exc}") from exc


def hold_state_baseline(drive: MCMNeuronDrive) -> MCMNeuronOutput:
    """B0-Hold: retain prior fast state and ignore every current input."""

    return MCMNeuronOutput(
        activation=drive.previous.activation,
        afterimage=drive.previous.afterimage,
    )


def receptor_projection_baseline(drive: MCMNeuronDrive) -> MCMNeuronOutput:
    """B0-Receptor: expose only current dock contact and retain no inner state."""

    contact = drive.perception.receptor_contact
    return MCMNeuronOutput(
        activation=0.0 if contact is None else contact,
        afterimage=0.0,
    )


def _offset(values: Iterable[int], role: str) -> tuple[int, ...]:
    result = tuple(values)
    if not result:
        raise MCMNeuronLayerError(f"{role} cannot be empty")
    if any(isinstance(value, bool) or not isinstance(value, int) for value in result):
        raise MCMNeuronLayerError(f"{role} must contain integers")
    if all(value == 0 for value in result):
        raise MCMNeuronLayerError(f"{role} cannot address the neuron itself")
    return result


@dataclass(frozen=True, slots=True)
class MCMNeuronLayer:
    """One immutable synchronous layer state with geometry-level field sampling."""

    layer_id: str
    neurons: tuple[MCMNeuron, ...]
    sample_offsets: tuple[tuple[int, ...], ...]
    periodic_axes: tuple[PeriodicSamplingAxis, ...] = ()
    receptor_dock_ids: tuple[str, ...] | None = None

    def __post_init__(self) -> None:
        neurons = tuple(self.neurons)
        if not neurons:
            raise MCMNeuronLayerError("neuron layer cannot be empty")
        if any(not isinstance(neuron, MCMNeuron) for neuron in neurons):
            raise MCMNeuronLayerError("neurons must contain completed MCM neuron states")
        if not isinstance(self.layer_id, str) or not self.layer_id:
            raise MCMNeuronLayerError("layer_id must be a non-empty technical identity")

        neuron_ids = [neuron.neuron_id for neuron in neurons]
        positions = [neuron.position for neuron in neurons]
        if len(set(neuron_ids)) != len(neuron_ids):
            raise MCMNeuronLayerError("neuron identities must be unique within a layer")
        if len(set(positions)) != len(positions):
            raise MCMNeuronLayerError("neuron positions must be unique within a layer")

        receptor_dock_ids = (
            tuple(
                neuron.neuron_id
                for neuron in neurons
                if neuron.perception.has_receptor_dock
            )
            if self.receptor_dock_ids is None
            else tuple(self.receptor_dock_ids)
        )
        if len(set(receptor_dock_ids)) != len(receptor_dock_ids):
            raise MCMNeuronLayerError("receptor dock neuron identities must be unique")
        unknown_docks = set(receptor_dock_ids) - set(neuron_ids)
        if unknown_docks:
            raise MCMNeuronLayerError(
                f"receptor docks reference unknown neurons: {sorted(unknown_docks)}"
            )

        first = neurons[0]
        fixed_roles = (
            (neuron.field_id, neuron.modality_id, neuron.geometry_id, neuron.tick)
            for neuron in neurons
        )
        expected = (first.field_id, first.modality_id, first.geometry_id, first.tick)
        if any(roles != expected for roles in fixed_roles):
            raise MCMNeuronLayerError(
                "all layer neurons must share field, modality, geometry, and tick"
            )

        dimension = len(first.position)
        if any(len(position) != dimension for position in positions):
            raise MCMNeuronLayerError("all neuron positions must share one dimension")

        offsets = tuple(_offset(offset, "sample_offset") for offset in self.sample_offsets)
        if not offsets:
            raise MCMNeuronLayerError("layer requires at least one local sample offset")
        if any(len(offset) != dimension for offset in offsets):
            raise MCMNeuronLayerError(
                "sample offsets and neuron positions must share one dimension"
            )
        if len(set(offsets)) != len(offsets):
            raise MCMNeuronLayerError("sample offsets must be unique")
        offset_set = set(offsets)
        if any(tuple(-value for value in offset) not in offset_set for offset in offsets):
            raise MCMNeuronLayerError(
                "technical field sampling must contain every opposite offset"
            )

        periodic_axes = tuple(self.periodic_axes)
        if any(not isinstance(axis, PeriodicSamplingAxis) for axis in periodic_axes):
            raise MCMNeuronLayerError(
                "periodic_axes must contain only periodic sampling axis contracts"
            )
        axis_indices = [axis.axis_index for axis in periodic_axes]
        if len(set(axis_indices)) != len(axis_indices):
            raise MCMNeuronLayerError(
                "each geometry dimension can have at most one periodic axis"
            )
        if any(axis.axis_index >= dimension for axis in periodic_axes):
            raise MCMNeuronLayerError(
                "periodic axis index must fit the neuron position dimension"
            )
        for axis in periodic_axes:
            expected_coordinates = set(
                range(axis.origin, axis.origin + axis.size)
            )
            actual_coordinates = {
                position[axis.axis_index] for position in positions
            }
            if not actual_coordinates.issubset(expected_coordinates):
                raise MCMNeuronLayerError(
                    "neuron position lies outside the periodic axis interval"
                )
            if actual_coordinates != expected_coordinates:
                raise MCMNeuronLayerError(
                    "periodic axis must contain every declared coordinate"
                )

        ordered_axes = tuple(
            sorted(periodic_axes, key=lambda axis: axis.axis_index)
        )
        for target_position in positions:
            mapped_positions = []
            for offset in offsets:
                source_position = [
                    coordinate + delta
                    for coordinate, delta in zip(
                        target_position,
                        offset,
                        strict=True,
                    )
                ]
                for axis in ordered_axes:
                    source_position[axis.axis_index] = axis.origin + (
                        (source_position[axis.axis_index] - axis.origin)
                        % axis.size
                    )
                mapped_positions.append(tuple(source_position))
            if len(set(mapped_positions)) != len(mapped_positions):
                raise MCMNeuronLayerError(
                    "periodic offsets alias the same source for one target"
                )

        object.__setattr__(self, "neurons", tuple(sorted(neurons, key=lambda item: item.neuron_id)))
        object.__setattr__(self, "sample_offsets", tuple(sorted(offsets)))
        object.__setattr__(self, "periodic_axes", ordered_axes)
        object.__setattr__(self, "receptor_dock_ids", tuple(sorted(receptor_dock_ids)))

    @property
    def tick(self) -> int:
        return self.neurons[0].tick

    @property
    def docked_neuron_ids(self) -> tuple[str, ...]:
        return self.receptor_dock_ids or ()

    def neuron(self, neuron_id: str) -> MCMNeuron:
        for neuron in self.neurons:
            if neuron.neuron_id == neuron_id:
                return neuron
        raise MCMNeuronLayerError(f"unknown neuron_id: {neuron_id}")

    def _perception_for(
        self,
        target: MCMNeuron,
        position_map: Mapping[tuple[int, ...], MCMNeuron],
        receptor_contacts: Mapping[str, float],
    ) -> MCMFieldPerception:
        samples = []
        for offset in self.sample_offsets:
            source_position_values = [
                coordinate + delta
                for coordinate, delta in zip(target.position, offset, strict=True)
            ]
            for axis in self.periodic_axes:
                source_position_values[axis.axis_index] = axis.origin + (
                    (source_position_values[axis.axis_index] - axis.origin)
                    % axis.size
                )
            source_position = tuple(source_position_values)
            source = position_map.get(source_position)
            if source is None:
                continue
            samples.append(
                MCMFieldSample(
                    sample_id=f"sample.{source.neuron_id}",
                    source_field_id=source.field_id,
                    source_tick=source.tick,
                    relative_position=offset,
                    activation=source.activation,
                    afterimage=source.afterimage,
                )
            )
        contact = (
            receptor_contacts.get(target.neuron_id)
            if target.neuron_id in self.docked_neuron_ids
            else None
        )
        return MCMFieldPerception(
            tick=self.tick + 1,
            receptor_contact=contact,
            local_samples=tuple(samples),
        )

    def advance(
        self,
        receptor_contacts: Mapping[str, float],
        transition: MCMNeuronTransition,
        *,
        allow_missing_contacts: bool = False,
        step_time: MCMFieldStepTime | None = None,
    ) -> "MCMNeuronLayer":
        """Return the complete next layer after all proposals succeed."""

        contacts = dict(receptor_contacts)
        required = set(self.docked_neuron_ids)
        supplied = set(contacts)
        unknown = supplied - required
        missing = required - supplied
        if unknown or (missing and not allow_missing_contacts):
            raise MCMNeuronLayerError(
                f"receptor contacts mismatch; missing={sorted(missing)}, "
                f"unknown={sorted(unknown)}"
            )
        position_map = {neuron.position: neuron for neuron in self.neurons}
        proposals = []
        for neuron in self.neurons:
            try:
                perception = self._perception_for(neuron, position_map, contacts)
            except (MCMNeuronValidationError, TypeError, ValueError) as exc:
                raise MCMNeuronLayerError(
                    f"invalid perception for {neuron.neuron_id}: {exc}"
                ) from exc
            proposals.append(
                advance_mcm_neuron(
                    neuron,
                    perception,
                    transition,
                    step_time=step_time,
                )
            )
        return MCMNeuronLayer(
            layer_id=self.layer_id,
            neurons=tuple(proposals),
            sample_offsets=self.sample_offsets,
            periodic_axes=self.periodic_axes,
            receptor_dock_ids=self.docked_neuron_ids,
        )

    def digest(self) -> str:
        payload = {
            "layer_id": self.layer_id,
            "sample_offsets": [list(offset) for offset in self.sample_offsets],
            "receptor_dock_ids": list(self.docked_neuron_ids),
            "neurons": [neuron.canonical_payload() for neuron in self.neurons],
        }
        if self.periodic_axes:
            payload["periodic_axes"] = [
                axis.canonical_payload() for axis in self.periodic_axes
            ]
        encoded = json.dumps(
            payload,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
