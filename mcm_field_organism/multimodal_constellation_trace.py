"""Passive finite trace observation for completed MCM constellations."""

from __future__ import annotations

from dataclasses import dataclass, fields
from itertools import combinations
from typing import Callable, Iterable

from .mcm_distributor import DistributedMCMConstellation, MCMFieldWindow
from .multimodal_pattern_checker import MultimodalPatternChecker, TemporalRelation


class MultimodalTraceError(ValueError):
    """Raised when a passive constellation trace is not causally ordered."""


@dataclass(frozen=True, slots=True)
class MultimodalTraceStep:
    sequence_index: int
    clock_id: str
    window_start_tick: int
    window_end_tick: int
    modality_ids: tuple[str, ...]
    dock_ids: tuple[str, ...]
    carrier_count: int


@dataclass(frozen=True, slots=True)
class MultimodalTraceComparison:
    earlier_index: int
    later_index: int
    separation_ticks: int
    overlap_ticks: int
    unchanged_modalities: tuple[str, ...]
    changed_modalities: tuple[str, ...]
    added_modalities: tuple[str, ...]
    removed_modalities: tuple[str, ...]
    exact_field_repeat: bool


@dataclass(frozen=True, slots=True)
class PassiveMultimodalTrace:
    """Observer result without retained field vectors or runtime writeback."""

    steps: tuple[MultimodalTraceStep, ...]
    comparisons: tuple[MultimodalTraceComparison, ...]

    def __post_init__(self) -> None:
        if len(self.steps) < 2:
            raise MultimodalTraceError("trace requires at least two completed constellations")
        expected = tuple(range(len(self.steps)))
        if tuple(step.sequence_index for step in self.steps) != expected:
            raise MultimodalTraceError("trace step indices must be complete and ordered")


TraceObserver = Callable[[PassiveMultimodalTrace], object]


def _field_content(window: MCMFieldWindow) -> tuple[object, ...]:
    """Comparable field content; technical time and snapshot identity are excluded."""

    return (
        window.modality_id,
        window.field_id,
        window.geometry_id,
        window.carrier_ids,
        window.activation,
        window.afterimage,
    )


def _field_map(
    constellation: DistributedMCMConstellation,
) -> dict[str, MCMFieldWindow]:
    return {window.modality_id: window for window in constellation.states}


def _comparison(
    earlier_index: int,
    later_index: int,
    constellations: tuple[DistributedMCMConstellation, ...],
    steps: tuple[MultimodalTraceStep, ...],
) -> MultimodalTraceComparison:
    earlier_fields = _field_map(constellations[earlier_index])
    later_fields = _field_map(constellations[later_index])
    earlier_modalities = set(earlier_fields)
    later_modalities = set(later_fields)
    shared = earlier_modalities & later_modalities

    unchanged = []
    changed = []
    for modality_id in sorted(shared):
        earlier = earlier_fields[modality_id]
        later = later_fields[modality_id]
        if (
            earlier.field_id != later.field_id
            or earlier.geometry_id != later.geometry_id
            or earlier.carrier_ids != later.carrier_ids
        ):
            raise MultimodalTraceError(
                f"continuing modality changed field anatomy: {modality_id}"
            )
        target = unchanged if _field_content(earlier) == _field_content(later) else changed
        target.append(modality_id)

    earlier_step = steps[earlier_index]
    later_step = steps[later_index]
    separation = max(0, later_step.window_start_tick - earlier_step.window_end_tick)
    overlap = max(0, earlier_step.window_end_tick - later_step.window_start_tick)
    added = tuple(sorted(later_modalities - earlier_modalities))
    removed = tuple(sorted(earlier_modalities - later_modalities))
    return MultimodalTraceComparison(
        earlier_index=earlier_index,
        later_index=later_index,
        separation_ticks=separation,
        overlap_ticks=overlap,
        unchanged_modalities=tuple(unchanged),
        changed_modalities=tuple(changed),
        added_modalities=added,
        removed_modalities=removed,
        exact_field_repeat=not changed and not added and not removed,
    )


def observe_multimodal_constellation_trace(
    constellations: Iterable[DistributedMCMConstellation],
    *,
    observer: TraceObserver | None = None,
) -> PassiveMultimodalTrace:
    """Compare every finite pair exactly, without similarity or pattern identity."""

    sequence = tuple(constellations)
    if len(sequence) < 2:
        raise MultimodalTraceError("trace requires at least two completed constellations")
    if any(not isinstance(item, DistributedMCMConstellation) for item in sequence):
        raise MultimodalTraceError("trace accepts only completed distributed constellations")
    clock_ids = {item.clock_id for item in sequence}
    if len(clock_ids) != 1:
        raise MultimodalTraceError("trace constellations must use one organism clock")

    checker = MultimodalPatternChecker()
    steps_out = []
    previous_start = None
    for sequence_index, constellation in enumerate(sequence):
        pattern = checker.check(constellation)
        if pattern.temporal_relation is not TemporalRelation.OVERLAP:
            raise MultimodalTraceError("each trace step must be a multimodal overlap")
        start = pattern.overlap_start_tick
        end = pattern.overlap_end_tick
        if start is None or end is None:
            raise MultimodalTraceError("overlap bounds are required")
        if previous_start is not None and start <= previous_start:
            raise MultimodalTraceError("trace starts must advance strictly")
        previous_start = start
        steps_out.append(
            MultimodalTraceStep(
                sequence_index=sequence_index,
                clock_id=constellation.clock_id,
                window_start_tick=start,
                window_end_tick=end,
                modality_ids=constellation.modality_ids,
                dock_ids=constellation.dock_ids,
                carrier_count=pattern.carrier_count,
            )
        )

    steps = tuple(steps_out)
    comparisons = tuple(
        _comparison(earlier, later, sequence, steps)
        for earlier, later in combinations(range(len(sequence)), 2)
    )
    result = PassiveMultimodalTrace(steps=steps, comparisons=comparisons)

    source_digests = tuple(item.digest() for item in sequence)
    if observer is not None:
        observer(result)
    if tuple(item.digest() for item in sequence) != source_digests:
        raise MultimodalTraceError("observer changed an immutable source constellation")
    return result


def multimodal_trace_public_roles() -> tuple[str, ...]:
    classes = (MultimodalTraceStep, MultimodalTraceComparison, PassiveMultimodalTrace)
    return tuple(item.name for cls in classes for item in fields(cls))
