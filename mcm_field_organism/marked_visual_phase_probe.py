"""Passive time marking for visual rest-change-rest research phases."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math
import re
from typing import Iterable

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
class MarkedVisualPhaseResult:
    clock_id: str
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
        phases=phase_set,
        assignments=assignments,
        summaries=tuple(summaries),
    )


def marked_visual_phase_public_roles() -> tuple[str, ...]:
    classes = (
        VisualWorldPhase,
        MeasuredVisualPhase,
        VisualPhaseFrameAssignment,
        VisualPhaseExistingFieldSummary,
        MarkedVisualPhaseResult,
    )
    return tuple(item.name for cls in classes for item in fields(cls))
