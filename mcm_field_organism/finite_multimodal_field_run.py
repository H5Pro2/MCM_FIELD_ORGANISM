"""Finite concurrent receptor capture through separate MCM sensor fields."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, fields
import threading
import time
from typing import Callable, Iterable, Mapping

from .mcm_distributor import DistributedMCMConstellation, MCMDistributor, MCMFieldWindow
from .multimodal_pattern_checker import (
    MultimodalPatternChecker,
    MultimodalPatternResult,
    TemporalRelation,
)
from .mcm_neuron_layer import receptor_projection_baseline
from .sensor_mcm_field import (
    CommonFieldTime,
    ReceptorContactFrame,
    build_receptor_aligned_mcm_field,
)


class FiniteMultimodalFieldError(ValueError):
    """Raised when a finite multimodal field run violates its causal boundary."""


ReceptorCapture = Callable[[], ReceptorContactFrame]
Clock = Callable[[], int]


@dataclass(frozen=True, slots=True)
class TimedReceptorFrame:
    """Reduced receptor state plus its measured organism-clock interval."""

    frame: ReceptorContactFrame
    organism_clock_id: str
    capture_start_tick: int
    capture_end_tick: int

    def __post_init__(self) -> None:
        if not isinstance(self.frame, ReceptorContactFrame):
            raise FiniteMultimodalFieldError("frame must be a completed receptor contact")
        if not isinstance(self.organism_clock_id, str) or not self.organism_clock_id:
            raise FiniteMultimodalFieldError("organism_clock_id must be non-empty")
        if (
            isinstance(self.capture_start_tick, bool)
            or isinstance(self.capture_end_tick, bool)
            or not isinstance(self.capture_start_tick, int)
            or not isinstance(self.capture_end_tick, int)
            or self.capture_start_tick < 0
            or self.capture_end_tick <= self.capture_start_tick
        ):
            raise FiniteMultimodalFieldError("capture ticks must form a positive interval")


@dataclass(frozen=True, slots=True)
class SensorFieldAnatomy:
    """Explicit technical anatomy for one receptor-aligned sensor field."""

    modality_id: str
    positions: tuple[tuple[int, ...], ...]
    sample_offsets: tuple[tuple[int, ...], ...]
    dock_id: str
    layer_id: str
    field_id: str
    field_geometry_id: str

    def __post_init__(self) -> None:
        identifiers = (
            self.modality_id,
            self.dock_id,
            self.layer_id,
            self.field_id,
            self.field_geometry_id,
        )
        if any(not isinstance(value, str) or not value for value in identifiers):
            raise FiniteMultimodalFieldError("field anatomy identifiers must be non-empty")
        positions = tuple(tuple(position) for position in self.positions)
        offsets = tuple(tuple(offset) for offset in self.sample_offsets)
        if not positions or not offsets:
            raise FiniteMultimodalFieldError("field anatomy requires positions and offsets")
        object.__setattr__(self, "positions", positions)
        object.__setattr__(self, "sample_offsets", offsets)


@dataclass(frozen=True, slots=True)
class FiniteMultimodalFieldResult:
    """Completed field windows and passive constellation observation only."""

    field_windows: tuple[MCMFieldWindow, ...]
    constellation: DistributedMCMConstellation
    pattern: MultimodalPatternResult

    def __post_init__(self) -> None:
        windows = tuple(sorted(self.field_windows, key=lambda item: item.modality_id))
        if not windows:
            raise FiniteMultimodalFieldError("result requires completed field windows")
        if self.pattern.temporal_relation is not TemporalRelation.OVERLAP:
            raise FiniteMultimodalFieldError("multimodal result requires measured overlap")
        if self.constellation.states != windows:
            raise FiniteMultimodalFieldError("constellation must contain the exported windows")
        object.__setattr__(self, "field_windows", windows)


def _capture_one(
    capture: ReceptorCapture,
    *,
    clock: Clock,
    clock_id: str,
    start_gate: threading.Barrier,
) -> TimedReceptorFrame:
    start_gate.wait()
    start = clock()
    frame = capture()
    end = clock()
    if end <= start:
        raise FiniteMultimodalFieldError("organism clock did not advance during capture")
    return TimedReceptorFrame(frame, clock_id, start, end)


def capture_overlapping_receptor_frames(
    captures: Mapping[str, ReceptorCapture],
    *,
    clock: Clock = time.monotonic_ns,
    clock_id: str = "organism.monotonic_ns",
) -> tuple[TimedReceptorFrame, ...]:
    """Capture independent modalities concurrently and require actual time overlap."""

    requests = dict(captures)
    if len(requests) < 2:
        raise FiniteMultimodalFieldError("multimodal capture requires at least two modalities")
    if any(not isinstance(key, str) or not key or not callable(value) for key, value in requests.items()):
        raise FiniteMultimodalFieldError("capture requests require named callables")

    start_gate = threading.Barrier(len(requests))
    with ThreadPoolExecutor(max_workers=len(requests)) as executor:
        futures = {
            modality_id: executor.submit(
                _capture_one,
                capture,
                clock=clock,
                clock_id=clock_id,
                start_gate=start_gate,
            )
            for modality_id, capture in requests.items()
        }
        timed = tuple(future.result() for future in futures.values())

    modalities = [item.frame.modality_id for item in timed]
    if set(modalities) != set(requests) or len(set(modalities)) != len(modalities):
        raise FiniteMultimodalFieldError("capture result modalities do not match requests")
    if max(item.capture_start_tick for item in timed) >= min(item.capture_end_tick for item in timed):
        raise FiniteMultimodalFieldError("receptor captures did not overlap on organism time")
    return tuple(sorted(timed, key=lambda item: item.frame.modality_id))


def assemble_multimodal_field_constellation(
    captures: Iterable[TimedReceptorFrame],
    anatomies: Mapping[str, SensorFieldAnatomy],
) -> FiniteMultimodalFieldResult:
    """Project reduced receptor states into separate fields, then distribute them."""

    timed = tuple(captures)
    if len(timed) < 2:
        raise FiniteMultimodalFieldError("assembly requires at least two receptor captures")
    clock_ids = {item.organism_clock_id for item in timed}
    if len(clock_ids) != 1:
        raise FiniteMultimodalFieldError("all captures must use one organism clock")
    modalities = [item.frame.modality_id for item in timed]
    if len(set(modalities)) != len(modalities):
        raise FiniteMultimodalFieldError("assembly requires unique modalities")
    anatomy_by_modality = dict(anatomies)
    if set(anatomy_by_modality) != set(modalities):
        raise FiniteMultimodalFieldError("field anatomies must match captured modalities")

    fields_out = []
    for item in timed:
        anatomy = anatomy_by_modality[item.frame.modality_id]
        if anatomy.modality_id != item.frame.modality_id:
            raise FiniteMultimodalFieldError("field anatomy modality mismatch")
        field = build_receptor_aligned_mcm_field(
            item.frame,
            positions=anatomy.positions,
            sample_offsets=anatomy.sample_offsets,
            dock_id=anatomy.dock_id,
            layer_id=anatomy.layer_id,
            field_id=anatomy.field_id,
            field_geometry_id=anatomy.field_geometry_id,
        ).advance(
            item.frame,
            CommonFieldTime(
                clock_id=item.organism_clock_id,
                window_start_tick=item.capture_start_tick,
                window_end_tick=item.capture_end_tick,
            ),
            receptor_projection_baseline,
        )
        fields_out.append(field)

    distributor = MCMDistributor()
    for field in fields_out:
        distributor.attach(field.distributor_dock())
    windows = tuple(field.field_window() for field in fields_out)
    constellation = distributor.distribute(windows)
    pattern = MultimodalPatternChecker().check(constellation)
    if pattern.temporal_relation is not TemporalRelation.OVERLAP:
        raise FiniteMultimodalFieldError("field windows do not retain measured overlap")
    return FiniteMultimodalFieldResult(windows, constellation, pattern)


def finite_multimodal_public_roles() -> tuple[str, ...]:
    return tuple(item.name for cls in (TimedReceptorFrame, FiniteMultimodalFieldResult) for item in fields(cls))
