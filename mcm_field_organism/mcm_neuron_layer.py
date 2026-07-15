"""Atomic spatial runtime shell for MCM neurons without a fixed field rule."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Callable, Iterable, Mapping

from .mcm_neuron import (
    MCMFieldPerception,
    MCMFieldSample,
    MCMNeuron,
    MCMNeuronValidationError,
)


class MCMNeuronLayerError(ValueError):
    """Raised when a neuron layer violates geometry or atomic-time invariants."""


@dataclass(frozen=True, slots=True)
class MCMNeuronDrive:
    """Causal transition input: prior self-state plus next local perception."""

    previous: MCMNeuron
    perception: MCMFieldPerception

    def __post_init__(self) -> None:
        if not isinstance(self.previous, MCMNeuron):
            raise MCMNeuronLayerError("previous must be a completed MCM neuron state")
        if not isinstance(self.perception, MCMFieldPerception):
            raise MCMNeuronLayerError("perception must be a completed MCM field perception")
        if self.perception.tick != self.previous.tick + 1:
            raise MCMNeuronLayerError(
                "neuron perception must advance exactly one completed field tick"
            )


@dataclass(frozen=True, slots=True)
class MCMNeuronOutput:
    """Minimal transition output; meaning and topology are deliberately absent."""

    activation: float
    afterimage: float


MCMNeuronTransition = Callable[[MCMNeuronDrive], MCMNeuronOutput]


def advance_mcm_neuron(
    previous: MCMNeuron,
    perception: MCMFieldPerception,
    transition: MCMNeuronTransition,
) -> MCMNeuron:
    """Advance one neuron through an explicit transition without hidden defaults."""

    if not callable(transition):
        raise MCMNeuronLayerError("transition must be callable")
    drive = MCMNeuronDrive(previous=previous, perception=perception)
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

        object.__setattr__(self, "neurons", tuple(sorted(neurons, key=lambda item: item.neuron_id)))
        object.__setattr__(self, "sample_offsets", tuple(sorted(offsets)))

    @property
    def tick(self) -> int:
        return self.neurons[0].tick

    @property
    def docked_neuron_ids(self) -> tuple[str, ...]:
        return tuple(
            neuron.neuron_id
            for neuron in self.neurons
            if neuron.perception.has_receptor_dock
        )

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
            source_position = tuple(
                coordinate + delta
                for coordinate, delta in zip(target.position, offset, strict=True)
            )
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
            receptor_contacts[target.neuron_id]
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
    ) -> "MCMNeuronLayer":
        """Return the complete next layer after all proposals succeed."""

        contacts = dict(receptor_contacts)
        required = set(self.docked_neuron_ids)
        supplied = set(contacts)
        if supplied != required:
            raise MCMNeuronLayerError(
                f"receptor contacts mismatch; missing={sorted(required - supplied)}, "
                f"unknown={sorted(supplied - required)}"
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
            proposals.append(advance_mcm_neuron(neuron, perception, transition))
        return MCMNeuronLayer(
            layer_id=self.layer_id,
            neurons=tuple(proposals),
            sample_offsets=self.sample_offsets,
        )

    def digest(self) -> str:
        payload = {
            "layer_id": self.layer_id,
            "sample_offsets": [list(offset) for offset in self.sample_offsets],
            "neurons": [neuron.canonical_payload() for neuron in self.neurons],
        }
        encoded = json.dumps(
            payload,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
