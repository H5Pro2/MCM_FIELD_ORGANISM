"""Historical separate-field baseline retained for reproducible experiments.

The active architecture uses ``ReceptorDistributor`` and ``SharedMCMField``.
This module must not be used to assemble the current organism field.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Iterable

from .mcm_distributor import MCMDock, MCMFieldWindow
from .mcm_neuron import MCMFieldPerception, MCMNeuron
from .mcm_neuron_layer import (
    MCMNeuronLayer,
    MCMNeuronTransition,
    PeriodicSamplingAxis,
)
from .receptor_contract import (
    CommonFieldTime,
    ReceptorContactFrame,
    ReceptorContractError,
    ReceptorNeuronDockMap,
    from_auditory_receptor_state,
    from_visual_receptor_state,
    technical_identifier,
)


SensorMCMFieldError = ReceptorContractError


@dataclass(frozen=True, slots=True)
class SensorMCMField:
    """One sensor field: dock map, neuron layer, and completed window export."""

    dock_id: str
    layer: MCMNeuronLayer
    dock_map: ReceptorNeuronDockMap
    last_receptor_frame: ReceptorContactFrame | None = None
    last_field_time: CommonFieldTime | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "dock_id",
            technical_identifier(self.dock_id, "dock_id"),
        )
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


def sensor_mcm_field_public_roles() -> tuple[tuple[str, ...], tuple[str, ...]]:
    return (
        tuple(item.name for item in fields(ReceptorContactFrame)),
        tuple(item.name for item in fields(SensorMCMField)),
    )
