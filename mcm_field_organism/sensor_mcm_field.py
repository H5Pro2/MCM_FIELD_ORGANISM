"""Neutral receptor-to-neuron-to-distributor bridge for sensor MCM fields."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math
import re
from typing import Iterable

from .broadband_hearing_path import AuditoryReceptorState
from .finite_video_path import VisualReceptorState
from .mcm_distributor import MCMDock, MCMFieldWindow
from .mcm_neuron import MCMFieldPerception, MCMNeuron
from .mcm_neuron_layer import (
    MCMNeuronLayer,
    MCMNeuronTransition,
    PeriodicSamplingAxis,
)


class SensorMCMFieldError(ValueError):
    """Raised when receptor, neuron layer, and field-window roles do not align."""


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")


def _identifier(value: object, role: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise SensorMCMFieldError(f"{role} must be a lowercase technical identifier")
    return value


def _values(values: Iterable[float], role: str) -> tuple[float, ...]:
    try:
        result = tuple(float(value) for value in values)
    except (TypeError, ValueError) as exc:
        raise SensorMCMFieldError(f"{role} must contain numeric values") from exc
    if not result or any(not math.isfinite(value) or abs(value) > 1.0 for value in result):
        raise SensorMCMFieldError(
            f"{role} must be non-empty and stay within the normalized -1..1 domain"
        )
    return result


@dataclass(frozen=True, slots=True)
class ReceptorContactFrame:
    """One completed receptor state without raw sensor payload."""

    modality_id: str
    geometry_id: str
    snapshot_id: str
    clock_id: str
    window_start_tick: int
    window_end_tick: int
    carrier_ids: tuple[str, ...]
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        for role in ("modality_id", "geometry_id", "snapshot_id", "clock_id"):
            object.__setattr__(self, role, _identifier(getattr(self, role), role))
        if (
            isinstance(self.window_start_tick, bool)
            or isinstance(self.window_end_tick, bool)
            or not isinstance(self.window_start_tick, int)
            or not isinstance(self.window_end_tick, int)
            or self.window_start_tick < 0
            or self.window_end_tick <= self.window_start_tick
        ):
            raise SensorMCMFieldError(
                "receptor frame ticks must form a positive non-negative interval"
            )
        carriers = tuple(self.carrier_ids)
        if not carriers or len(set(carriers)) != len(carriers):
            raise SensorMCMFieldError("receptor carrier identities must be non-empty and unique")
        for carrier_id in carriers:
            _identifier(carrier_id, "carrier_id")
        values = _values(self.values, "receptor values")
        if len(values) != len(carriers):
            raise SensorMCMFieldError("receptor values must match carrier geometry")
        object.__setattr__(self, "carrier_ids", carriers)
        object.__setattr__(self, "values", values)


@dataclass(frozen=True, slots=True)
class CommonFieldTime:
    """One explicit interval on the shared organism clock."""

    clock_id: str
    window_start_tick: int
    window_end_tick: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "clock_id", _identifier(self.clock_id, "clock_id"))
        if (
            isinstance(self.window_start_tick, bool)
            or isinstance(self.window_end_tick, bool)
            or not isinstance(self.window_start_tick, int)
            or not isinstance(self.window_end_tick, int)
            or self.window_start_tick < 0
            or self.window_end_tick <= self.window_start_tick
        ):
            raise SensorMCMFieldError(
                "common field ticks must form a positive non-negative interval"
            )


@dataclass(frozen=True, slots=True)
class ReceptorNeuronDockMap:
    """Lossless one-to-one technical mapping; no weights or semantic fusion."""

    modality_id: str
    receptor_geometry_id: str
    pairs: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "modality_id", _identifier(self.modality_id, "modality_id"))
        object.__setattr__(
            self,
            "receptor_geometry_id",
            _identifier(self.receptor_geometry_id, "receptor_geometry_id"),
        )
        pairs = tuple(tuple(pair) for pair in self.pairs)
        if not pairs or any(len(pair) != 2 for pair in pairs):
            raise SensorMCMFieldError("dock map requires carrier-to-neuron pairs")
        for carrier_id, neuron_id in pairs:
            _identifier(carrier_id, "carrier_id")
            _identifier(neuron_id, "neuron_id")
        carrier_ids = [pair[0] for pair in pairs]
        neuron_ids = [pair[1] for pair in pairs]
        if len(set(carrier_ids)) != len(carrier_ids):
            raise SensorMCMFieldError("one receptor carrier cannot be copied to multiple docks")
        if len(set(neuron_ids)) != len(neuron_ids):
            raise SensorMCMFieldError("one neuron cannot receive multiple receptor carriers")
        object.__setattr__(self, "pairs", tuple(sorted(pairs)))

    @property
    def carrier_ids(self) -> tuple[str, ...]:
        return tuple(pair[0] for pair in self.pairs)

    @property
    def neuron_ids(self) -> tuple[str, ...]:
        return tuple(pair[1] for pair in self.pairs)

    def contacts_for(self, frame: ReceptorContactFrame) -> dict[str, float]:
        if frame.modality_id != self.modality_id:
            raise SensorMCMFieldError("receptor modality does not match dock map")
        if frame.geometry_id != self.receptor_geometry_id:
            raise SensorMCMFieldError("receptor geometry does not match dock map")
        values_by_carrier = dict(zip(frame.carrier_ids, frame.values, strict=True))
        expected = set(self.carrier_ids)
        supplied = set(values_by_carrier)
        if supplied != expected:
            raise SensorMCMFieldError(
                f"receptor carriers mismatch; missing={sorted(expected - supplied)}, "
                f"unknown={sorted(supplied - expected)}"
            )
        return {
            neuron_id: values_by_carrier[carrier_id]
            for carrier_id, neuron_id in self.pairs
        }


@dataclass(frozen=True, slots=True)
class SensorMCMField:
    """One sensor field: dock map, neuron layer, and completed window export."""

    dock_id: str
    layer: MCMNeuronLayer
    dock_map: ReceptorNeuronDockMap
    last_receptor_frame: ReceptorContactFrame | None = None
    last_field_time: CommonFieldTime | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "dock_id", _identifier(self.dock_id, "dock_id"))
        if not isinstance(self.layer, MCMNeuronLayer):
            raise SensorMCMFieldError("layer must be a completed MCM neuron layer")
        if not isinstance(self.dock_map, ReceptorNeuronDockMap):
            raise SensorMCMFieldError("dock_map must be a receptor-neuron dock map")
        neuron_ids = {neuron.neuron_id for neuron in self.layer.neurons}
        mapped_neuron_ids = set(self.dock_map.neuron_ids)
        if not mapped_neuron_ids.issubset(neuron_ids):
            raise SensorMCMFieldError("dock map contains a neuron outside the field layer")
        if set(self.layer.docked_neuron_ids) != mapped_neuron_ids:
            raise SensorMCMFieldError("mapped neurons and layer receptor docks must match")
        if self.layer.neurons[0].modality_id != self.dock_map.modality_id:
            raise SensorMCMFieldError("layer modality must match receptor dock map")
        if (self.last_receptor_frame is None) != (self.last_field_time is None):
            raise SensorMCMFieldError(
                "receptor frame and common field time must be present together"
            )
        if self.last_receptor_frame is not None:
            self.dock_map.contacts_for(self.last_receptor_frame)

    @property
    def field_id(self) -> str:
        return self.layer.neurons[0].field_id

    @property
    def geometry_id(self) -> str:
        return self.layer.neurons[0].geometry_id

    @property
    def modality_id(self) -> str:
        return self.layer.neurons[0].modality_id

    def advance(
        self,
        frame: ReceptorContactFrame,
        field_time: CommonFieldTime,
        transition: MCMNeuronTransition,
    ) -> "SensorMCMField":
        if not isinstance(field_time, CommonFieldTime):
            raise SensorMCMFieldError("field_time must use the shared field clock contract")
        if self.last_field_time is not None:
            if field_time.clock_id != self.last_field_time.clock_id:
                raise SensorMCMFieldError("common field clock cannot change within one field")
            if field_time.window_end_tick <= self.last_field_time.window_end_tick:
                raise SensorMCMFieldError("common field time must advance")
        contacts = self.dock_map.contacts_for(frame)
        try:
            next_layer = self.layer.advance(contacts, transition)
        except ValueError as exc:
            raise SensorMCMFieldError(f"neuron layer advance failed: {exc}") from exc
        return SensorMCMField(
            dock_id=self.dock_id,
            layer=next_layer,
            dock_map=self.dock_map,
            last_receptor_frame=frame,
            last_field_time=field_time,
        )

    def field_window(self) -> MCMFieldWindow:
        frame = self.last_receptor_frame
        if frame is None:
            raise SensorMCMFieldError(
                "sensor MCM field has no completed receptor-driven state"
            )
        field_time = self.last_field_time
        if field_time is None:
            raise SensorMCMFieldError("sensor MCM field has no common field time")
        neurons = self.layer.neurons
        return MCMFieldWindow(
            dock_id=self.dock_id,
            modality_id=self.modality_id,
            field_id=self.field_id,
            geometry_id=self.geometry_id,
            snapshot_id=f"{self.field_id}.tick.{self.layer.tick}",
            clock_id=field_time.clock_id,
            window_start_tick=field_time.window_start_tick,
            window_end_tick=field_time.window_end_tick,
            carrier_ids=tuple(neuron.neuron_id for neuron in neurons),
            activation=tuple(neuron.activation for neuron in neurons),
            afterimage=tuple(neuron.afterimage for neuron in neurons),
        )

    def distributor_dock(self) -> MCMDock:
        field_time = self.last_field_time
        if field_time is None:
            raise SensorMCMFieldError("clock is unknown before the first receptor frame")
        return MCMDock(
            dock_id=self.dock_id,
            modality_id=self.modality_id,
            geometry_id=self.geometry_id,
            clock_id=field_time.clock_id,
        )


def build_receptor_aligned_mcm_field(
    reference_frame: ReceptorContactFrame,
    *,
    positions: Iterable[Iterable[int]],
    sample_offsets: Iterable[Iterable[int]],
    dock_id: str,
    layer_id: str,
    field_id: str,
    field_geometry_id: str,
    periodic_axes: Iterable[PeriodicSamplingAxis] = (),
) -> SensorMCMField:
    """Create an explicit baseline anatomy without consuming the reference frame."""

    positions_out = tuple(tuple(position) for position in positions)
    if len(positions_out) != len(reference_frame.carrier_ids):
        raise SensorMCMFieldError("one explicit field position is required per receptor carrier")
    neuron_ids = tuple(
        f"{field_id}.n{index}" for index in range(len(reference_frame.carrier_ids))
    )
    neurons = tuple(
        MCMNeuron(
            neuron_id=neuron_id,
            field_id=field_id,
            modality_id=reference_frame.modality_id,
            geometry_id=field_geometry_id,
            position=position,
            activation=0.0,
            afterimage=0.0,
            perception=MCMFieldPerception(
                tick=0,
                receptor_contact=0.0,
                local_samples=(),
            ),
        )
        for neuron_id, position in zip(neuron_ids, positions_out, strict=True)
    )
    layer = MCMNeuronLayer(
        layer_id=layer_id,
        neurons=neurons,
        sample_offsets=tuple(tuple(offset) for offset in sample_offsets),
        periodic_axes=tuple(periodic_axes),
    )
    dock_map = ReceptorNeuronDockMap(
        modality_id=reference_frame.modality_id,
        receptor_geometry_id=reference_frame.geometry_id,
        pairs=tuple(zip(reference_frame.carrier_ids, neuron_ids, strict=True)),
    )
    return SensorMCMField(dock_id=dock_id, layer=layer, dock_map=dock_map)


def from_auditory_receptor_state(state: AuditoryReceptorState) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id=state.modality_id,
        geometry_id=state.geometry_id,
        snapshot_id=f"auditory.receptor.{state.snapshot_index}",
        clock_id="audio.sample",
        window_start_tick=state.window_start_sample,
        window_end_tick=state.window_end_sample,
        carrier_ids=state.carrier_ids,
        values=state.energy,
    )


def from_visual_receptor_state(state: VisualReceptorState) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id=state.modality_id,
        geometry_id=state.geometry_id,
        snapshot_id=f"visual.receptor.{state.frame_index}",
        clock_id="video.frame",
        window_start_tick=state.frame_index,
        window_end_tick=state.frame_index + 1,
        carrier_ids=state.carrier_ids,
        values=state.channel_values,
    )


def sensor_mcm_field_public_roles() -> tuple[tuple[str, ...], tuple[str, ...]]:
    return (
        tuple(item.name for item in fields(ReceptorContactFrame)),
        tuple(item.name for item in fields(SensorMCMField)),
    )
