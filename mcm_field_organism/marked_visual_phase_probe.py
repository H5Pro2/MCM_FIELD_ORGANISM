"""Passive time marking for visual rest-change-rest research phases."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math
import re
from typing import Iterable

from .local_neuron_function_probe import MCMLocalFunctionObservation
from .visual_spatiotemporal_input_probe import VisualSpatiotemporalProbeResult


class MarkedVisualPhaseError(ValueError):
    """Raised when measured visual intervals do not satisfy the phase contract."""


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")


@dataclass(frozen=True, slots=True)
class VisualWorldPhase:
    """External research mark; it is not a field-recognized state or label."""

    phase_id: str
    duration_ticks: int

    def __post_init__(self) -> None:
        if not isinstance(self.phase_id, str) or not _IDENTIFIER.fullmatch(self.phase_id):
            raise MarkedVisualPhaseError("phase_id must be a lowercase technical identifier")
        if (
            isinstance(self.duration_ticks, bool)
            or not isinstance(self.duration_ticks, int)
            or self.duration_ticks <= 0
        ):
            raise MarkedVisualPhaseError("duration_ticks must be a positive integer")


@dataclass(frozen=True, slots=True)
class MeasuredVisualPhase:
    phase_id: str
    window_start_tick: int
    window_end_tick: int

    def __post_init__(self) -> None:
        if not isinstance(self.phase_id, str) or not _IDENTIFIER.fullmatch(self.phase_id):
            raise MarkedVisualPhaseError("phase_id must be a lowercase technical identifier")
        if (
            isinstance(self.window_start_tick, bool)
            or isinstance(self.window_end_tick, bool)
            or not isinstance(self.window_start_tick, int)
            or not isinstance(self.window_end_tick, int)
            or self.window_start_tick < 0
            or self.window_end_tick <= self.window_start_tick
        ):
            raise MarkedVisualPhaseError("measured phase must be a positive interval")


@dataclass(frozen=True, slots=True)
class VisualPhaseFrameAssignment:
    frame_index: int
    window_start_tick: int
    window_end_tick: int
    phase_id: str | None
    crosses_phase_boundary: bool
    initialization_frame: bool


@dataclass(frozen=True, slots=True)
class VisualPhaseExistingFieldSummary:
    """Observer-only summary of quantities already exposed by the field probe."""

    phase_id: str
    frame_count: int
    mean_absolute_receptor_change: float
    mean_absolute_local_activation_difference: float


@dataclass(frozen=True, slots=True)
class VisualLocalPhaseValue:
    """One observer-side local aggregate; not a retained image or field state."""

    neuron_id: str
    position: tuple[int, int, int]
    frame_count: int
    mean_absolute_receptor_change: float
    mean_absolute_local_activation_difference: float

    def __post_init__(self) -> None:
        if not isinstance(self.neuron_id, str) or not _IDENTIFIER.fullmatch(self.neuron_id):
            raise MarkedVisualPhaseError("neuron_id must be a technical identifier")
        position = tuple(self.position)
        if len(position) != 3 or any(
            isinstance(value, bool) or not isinstance(value, int) for value in position
        ):
            raise MarkedVisualPhaseError("local visual position must contain three integers")
        if (
            isinstance(self.frame_count, bool)
            or not isinstance(self.frame_count, int)
            or self.frame_count <= 0
        ):
            raise MarkedVisualPhaseError("local profile frame_count must be positive")
        for role in (
            "mean_absolute_receptor_change",
            "mean_absolute_local_activation_difference",
        ):
            value = float(getattr(self, role))
            if not math.isfinite(value) or value < 0.0:
                raise MarkedVisualPhaseError(f"{role} must be finite and non-negative")
            object.__setattr__(self, role, value)
        object.__setattr__(self, "position", position)


@dataclass(frozen=True, slots=True)
class VisualPhaseLocalFieldProfile:
    phase_id: str
    values: tuple[VisualLocalPhaseValue, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.phase_id, str) or not _IDENTIFIER.fullmatch(self.phase_id):
            raise MarkedVisualPhaseError("phase_id must be a lowercase technical identifier")
        values = tuple(self.values)
        if any(not isinstance(value, VisualLocalPhaseValue) for value in values):
            raise MarkedVisualPhaseError("local profile contains an invalid value")
        if len({value.neuron_id for value in values}) != len(values):
            raise MarkedVisualPhaseError("local profile neuron identities must be unique")
        if len({value.position for value in values}) != len(values):
            raise MarkedVisualPhaseError("local profile positions must be unique")
        object.__setattr__(self, "values", tuple(sorted(values, key=lambda item: item.neuron_id)))


@dataclass(frozen=True, slots=True)
class MarkedVisualPhaseResult:
    clock_id: str
    probe_digest: str
    phases: tuple[MeasuredVisualPhase, ...]
    assignments: tuple[VisualPhaseFrameAssignment, ...]
    summaries: tuple[VisualPhaseExistingFieldSummary, ...]

    @property
    def boundary_frame_count(self) -> int:
        return sum(item.crosses_phase_boundary for item in self.assignments)

    @property
    def outside_schedule_frame_count(self) -> int:
        return sum(
            item.phase_id is None and not item.crosses_phase_boundary
            for item in self.assignments
        )

    @property
    def initialization_frame_count(self) -> int:
        return sum(item.initialization_frame for item in self.assignments)


def _probe_digest(probe: VisualSpatiotemporalProbeResult) -> str:
    payload = {
        "clock_id": probe.clock_id,
        "geometry": [probe.grid_rows, probe.grid_columns, probe.channel_count],
        "ticks": [
            {
                "frame_index": tick.frame_index,
                "field_tick": tick.field_tick,
                "window": [tick.window_start_tick, tick.window_end_tick],
                "observations": [
                    {
                        "neuron_id": observation.neuron_id,
                        "position": list(observation.position),
                        "receptor_contact": observation.local_input.receptor_contact,
                        "prior_activation": observation.local_input.prior_activation,
                        "prior_afterimage": observation.local_input.prior_afterimage,
                        "pairs": [
                            {
                                "sample_id": pair.sample_id,
                                "relative_position": list(pair.relative_position),
                                "activation_difference": pair.activation_difference,
                                "afterimage_difference": pair.afterimage_difference,
                            }
                            for pair in observation.local_input.pair_differences
                        ],
                    }
                    for observation in tick.observations
                ],
            }
            for tick in probe.ticks
        ],
    }
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_visual_phase_schedule(
    *,
    clock_id: str,
    anchor_tick: int,
    phases: Iterable[VisualWorldPhase],
) -> tuple[MeasuredVisualPhase, ...]:
    """Build contiguous external marks on the same clock used by the probe."""

    if not isinstance(clock_id, str) or not _IDENTIFIER.fullmatch(clock_id):
        raise MarkedVisualPhaseError("clock_id must be a lowercase technical identifier")
    if isinstance(anchor_tick, bool) or not isinstance(anchor_tick, int) or anchor_tick < 0:
        raise MarkedVisualPhaseError("anchor_tick must be a non-negative integer")
    definitions = tuple(phases)
    if len(definitions) < 3:
        raise MarkedVisualPhaseError("visual null probe requires at least three phases")
    if any(not isinstance(item, VisualWorldPhase) for item in definitions):
        raise MarkedVisualPhaseError("phases must contain VisualWorldPhase values")
    if len({item.phase_id for item in definitions}) != len(definitions):
        raise MarkedVisualPhaseError("phase identifiers must be unique")

    cursor = anchor_tick
    measured = []
    for definition in definitions:
        end = cursor + definition.duration_ticks
        measured.append(MeasuredVisualPhase(definition.phase_id, cursor, end))
        cursor = end
    return tuple(measured)


def rest_change_rest_visual_schedule(
    *,
    clock_id: str,
    anchor_tick: int,
    phase_duration_ticks: int,
) -> tuple[MeasuredVisualPhase, ...]:
    return build_visual_phase_schedule(
        clock_id=clock_id,
        anchor_tick=anchor_tick,
        phases=(
            VisualWorldPhase("rest.1", phase_duration_ticks),
            VisualWorldPhase("change", phase_duration_ticks),
            VisualWorldPhase("rest.2", phase_duration_ticks),
        ),
    )


def _assignment(
    frame_index: int,
    start: int,
    end: int,
    phases: tuple[MeasuredVisualPhase, ...],
    *,
    initialization_frame: bool,
) -> VisualPhaseFrameAssignment:
    contained = tuple(
        phase
        for phase in phases
        if start >= phase.window_start_tick and end <= phase.window_end_tick
    )
    if len(contained) == 1:
        phase_id = contained[0].phase_id
        crossing = False
    else:
        phase_id = None
        crossing = any(start < phase.window_end_tick < end for phase in phases[:-1])
    return VisualPhaseFrameAssignment(
        frame_index,
        start,
        end,
        phase_id,
        crossing,
        initialization_frame,
    )


def observe_marked_visual_phases(
    probe: VisualSpatiotemporalProbeResult,
    *,
    clock_id: str,
    phases: Iterable[MeasuredVisualPhase],
) -> MarkedVisualPhaseResult:
    """Relate completed probe ticks to external marks without field writeback."""

    if probe.clock_id != clock_id:
        raise MarkedVisualPhaseError("phase schedule and visual probe must share one clock")
    phase_set = tuple(phases)
    if len(phase_set) < 3 or any(not isinstance(item, MeasuredVisualPhase) for item in phase_set):
        raise MarkedVisualPhaseError("at least three measured phases are required")
    if len({item.phase_id for item in phase_set}) != len(phase_set):
        raise MarkedVisualPhaseError("measured phase identifiers must be unique")
    for previous, current in zip(phase_set, phase_set[1:]):
        if previous.window_end_tick != current.window_start_tick:
            raise MarkedVisualPhaseError("measured phases must be contiguous")

    first_frame_index = probe.ticks[0].frame_index
    assignments = tuple(
        _assignment(
            tick.frame_index,
            tick.window_start_tick,
            tick.window_end_tick,
            phase_set,
            initialization_frame=tick.frame_index == first_frame_index,
        )
        for tick in probe.ticks
    )
    tick_by_index = {tick.frame_index: tick for tick in probe.ticks}
    summaries = []
    for phase in phase_set:
        selected = tuple(
            item
            for item in assignments
            if item.phase_id == phase.phase_id and not item.initialization_frame
        )
        receptor_changes = []
        local_differences = []
        for assignment in selected:
            for observation in tick_by_index[assignment.frame_index].observations:
                local = observation.local_input
                contact = 0.0 if local.receptor_contact is None else local.receptor_contact
                receptor_changes.append(abs(contact - local.prior_activation))
                local_differences.extend(
                    abs(item.activation_difference) for item in local.pair_differences
                )
        summaries.append(
            VisualPhaseExistingFieldSummary(
                phase_id=phase.phase_id,
                frame_count=len(selected),
                mean_absolute_receptor_change=(
                    math.fsum(receptor_changes) / len(receptor_changes)
                    if receptor_changes
                    else 0.0
                ),
                mean_absolute_local_activation_difference=(
                    math.fsum(local_differences) / len(local_differences)
                    if local_differences
                    else 0.0
                ),
            )
        )
    return MarkedVisualPhaseResult(
        clock_id=clock_id,
        probe_digest=_probe_digest(probe),
        phases=phase_set,
        assignments=assignments,
        summaries=tuple(summaries),
    )


def observe_visual_phase_local_profiles(
    probe: VisualSpatiotemporalProbeResult,
    marked: MarkedVisualPhaseResult,
) -> tuple[VisualPhaseLocalFieldProfile, ...]:
    """Preserve local phase aggregates without ranking or interpreting them."""

    if probe.clock_id != marked.clock_id:
        raise MarkedVisualPhaseError("local profiles require the marked probe clock")
    if _probe_digest(probe) != marked.probe_digest:
        raise MarkedVisualPhaseError("local profiles require the exact marked probe")
    tick_by_index = {tick.frame_index: tick for tick in probe.ticks}
    if set(tick_by_index) != {item.frame_index for item in marked.assignments}:
        raise MarkedVisualPhaseError("marked assignments must cover the complete probe")

    profiles = []
    for phase in marked.phases:
        selected_indices = tuple(
            item.frame_index
            for item in marked.assignments
            if item.phase_id == phase.phase_id and not item.initialization_frame
        )
        observations_by_neuron: dict[str, list[MCMLocalFunctionObservation]] = {}
        positions: dict[str, tuple[int, int, int]] = {}
        for frame_index in selected_indices:
            for observation in tick_by_index[frame_index].observations:
                observations_by_neuron.setdefault(observation.neuron_id, []).append(
                    observation.local_input
                )
                positions[observation.neuron_id] = observation.position

        values = []
        for neuron_id in sorted(observations_by_neuron):
            observations = observations_by_neuron[neuron_id]
            receptor_changes = []
            local_differences = []
            for local in observations:
                contact = 0.0 if local.receptor_contact is None else local.receptor_contact
                receptor_changes.append(abs(contact - local.prior_activation))
                local_differences.extend(
                    abs(item.activation_difference) for item in local.pair_differences
                )
            values.append(
                VisualLocalPhaseValue(
                    neuron_id=neuron_id,
                    position=positions[neuron_id],
                    frame_count=len(observations),
                    mean_absolute_receptor_change=(
                        math.fsum(receptor_changes) / len(receptor_changes)
                        if receptor_changes
                        else 0.0
                    ),
                    mean_absolute_local_activation_difference=(
                        math.fsum(local_differences) / len(local_differences)
                        if local_differences
                        else 0.0
                    ),
                )
            )
        profiles.append(VisualPhaseLocalFieldProfile(phase.phase_id, tuple(values)))
    return tuple(profiles)


def marked_visual_phase_public_roles() -> tuple[str, ...]:
    classes = (
        VisualWorldPhase,
        MeasuredVisualPhase,
        VisualPhaseFrameAssignment,
        VisualPhaseExistingFieldSummary,
        VisualLocalPhaseValue,
        VisualPhaseLocalFieldProfile,
        MarkedVisualPhaseResult,
    )
    return tuple(item.name for cls in classes for item in fields(cls))
