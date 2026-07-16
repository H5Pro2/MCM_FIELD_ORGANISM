"""Passive probe for local visual inputs across a finite frame sequence."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Iterable

import numpy as np

from .finite_video_path import VisualGridConfig
from .local_neuron_function_probe import (
    MCMLocalFunctionObservation,
    observe_local_mcm_function,
)
from .mcm_neuron_layer import MCMNeuronDrive, receptor_projection_baseline
from .sensor_mcm_field import CommonFieldTime
from .visual_mcm_interface import build_visual_mcm_interface


class VisualSpatiotemporalProbeError(ValueError):
    """Raised when a passive visual sequence violates the probe contract."""


@dataclass(frozen=True, slots=True)
class VisualLocalInputObservation:
    neuron_id: str
    position: tuple[int, int, int]
    local_input: MCMLocalFunctionObservation


@dataclass(frozen=True, slots=True)
class VisualSpatiotemporalTick:
    frame_index: int
    field_tick: int
    observations: tuple[VisualLocalInputObservation, ...]


@dataclass(frozen=True, slots=True)
class VisualSpatiotemporalProbeResult:
    """Finite observer output; no frames or inferred movement roles are retained."""

    grid_rows: int
    grid_columns: int
    channel_count: int
    ticks: tuple[VisualSpatiotemporalTick, ...]

    def __post_init__(self) -> None:
        if len(self.ticks) < 2:
            raise VisualSpatiotemporalProbeError("probe result requires at least two ticks")
        if tuple(item.frame_index for item in self.ticks) != tuple(range(len(self.ticks))):
            raise VisualSpatiotemporalProbeError("frame indices must remain complete")
        if tuple(item.field_tick for item in self.ticks) != tuple(range(1, len(self.ticks) + 1)):
            raise VisualSpatiotemporalProbeError("field ticks must remain complete")


def _observation(drive: MCMNeuronDrive) -> VisualLocalInputObservation:
    position = drive.previous.position
    if len(position) != 3:
        raise VisualSpatiotemporalProbeError("visual neuron positions must be three-dimensional")
    return VisualLocalInputObservation(
        neuron_id=drive.previous.neuron_id,
        position=(position[0], position[1], position[2]),
        local_input=observe_local_mcm_function(drive),
    )


def run_visual_spatiotemporal_input_probe(
    frames_in: Iterable[np.ndarray],
    config: VisualGridConfig,
    *,
    clock_id: str = "organism.visual_probe",
    tick_width: int = 1,
) -> VisualSpatiotemporalProbeResult:
    """Expose local causal inputs while retaining the receptor projection baseline."""

    frames_in = tuple(frames_in)
    if len(frames_in) < 2:
        raise VisualSpatiotemporalProbeError("probe requires at least two frames")
    if isinstance(tick_width, bool) or not isinstance(tick_width, int) or tick_width <= 0:
        raise VisualSpatiotemporalProbeError("tick_width must be a positive integer")

    interface = build_visual_mcm_interface(config)
    ticks = []
    for frame_index, frame in enumerate(frames_in):
        observed = []

        def transition(drive: MCMNeuronDrive):
            observed.append(_observation(drive))
            return receptor_projection_baseline(drive)

        start = frame_index * tick_width
        interface, output = interface.advance(
            frame,
            CommonFieldTime(clock_id, start, start + tick_width),
            transition,
        )
        ordered = tuple(sorted(observed, key=lambda item: item.neuron_id))
        if len(ordered) != config.carrier_count:
            raise VisualSpatiotemporalProbeError("every visual neuron must be observed once")
        if any(value != 0.0 for value in output.field_window.afterimage):
            raise VisualSpatiotemporalProbeError("passive probe must not introduce afterimage")
        ticks.append(
            VisualSpatiotemporalTick(
                frame_index=output.frame_index,
                field_tick=interface.current_field.layer.tick,
                observations=ordered,
            )
        )

    return VisualSpatiotemporalProbeResult(
        grid_rows=config.grid_rows,
        grid_columns=config.grid_columns,
        channel_count=3,
        ticks=tuple(ticks),
    )


def visual_spatiotemporal_probe_public_roles() -> tuple[str, ...]:
    classes = (
        VisualLocalInputObservation,
        VisualSpatiotemporalTick,
        VisualSpatiotemporalProbeResult,
    )
    return tuple(item.name for cls in classes for item in fields(cls))
