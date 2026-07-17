"""Finite concurrent receptor capture into one shared MCM field."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, fields
import threading
import time
from typing import Callable, Iterable, Mapping

from .mcm_neuron_layer import receptor_projection_baseline
from .receptor_distributor import (
    ReceptorDistribution,
    ReceptorDistributor,
    ReceptorDock,
)
from .receptor_contract import (
    CommonFieldTime,
    ReceptorContactFrame,
)
from .shared_mcm_field import (
    ReceptorDockAnatomy,
    SharedMCMField,
    SharedMCMFieldSnapshot,
    build_shared_mcm_field,
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
class FiniteSharedMCMFieldResult:
    """One distributed receptor state and one completed shared field state."""

    receptor_distribution: ReceptorDistribution
    shared_field: SharedMCMField
    field_state: SharedMCMFieldSnapshot

    def __post_init__(self) -> None:
        if not isinstance(self.receptor_distribution, ReceptorDistribution):
            raise FiniteMultimodalFieldError(
                "result requires the receptor distributor output"
            )
        if not isinstance(self.shared_field, SharedMCMField):
            raise FiniteMultimodalFieldError("result requires one shared MCM field")
        if not isinstance(self.field_state, SharedMCMFieldSnapshot):
            raise FiniteMultimodalFieldError(
                "result requires one completed shared field state"
            )
        if self.shared_field.snapshot() != self.field_state:
            raise FiniteMultimodalFieldError(
                "field state must be the current state of the shared field"
            )
        field_time = self.receptor_distribution.field_time
        if (
            self.field_state.clock_id != field_time.clock_id
            or self.field_state.window_start_tick != field_time.window_start_tick
            or self.field_state.window_end_tick != field_time.window_end_tick
        ):
            raise FiniteMultimodalFieldError(
                "shared field state must retain the distributed organism time"
            )


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


def assemble_shared_mcm_field(
    captures: Iterable[TimedReceptorFrame],
    anatomies: Mapping[str, ReceptorDockAnatomy],
    *,
    field_sample_offsets: Iterable[Iterable[int]],
    field_id: str = "organism.mcm_field",
    layer_id: str = "organism.mcm_layer",
    field_geometry_id: str = "organism.shared.v1",
) -> FiniteSharedMCMFieldResult:
    """Route reduced receptor contacts into one common synchronous layer."""

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
        raise FiniteMultimodalFieldError(
            "receptor dock anatomies must match captured modalities"
        )
    overlap_start = max(item.capture_start_tick for item in timed)
    overlap_end = min(item.capture_end_tick for item in timed)
    if overlap_start >= overlap_end:
        raise FiniteMultimodalFieldError(
            "receptor captures do not retain measured overlap"
        )
    field_time = CommonFieldTime(
        clock_id=next(iter(clock_ids)),
        window_start_tick=overlap_start,
        window_end_tick=overlap_end,
    )

    distributor = ReceptorDistributor()
    for item in timed:
        anatomy = anatomy_by_modality[item.frame.modality_id]
        if anatomy.modality_id != item.frame.modality_id:
            raise FiniteMultimodalFieldError("receptor dock anatomy modality mismatch")
        distributor.attach(
            ReceptorDock(
                dock_id=anatomy.dock_id,
                modality_id=anatomy.modality_id,
                receptor_geometry_id=item.frame.geometry_id,
            )
        )
    frames = tuple(item.frame for item in timed)
    distribution = distributor.distribute(frames, field_time)
    shared_field = build_shared_mcm_field(
        frames,
        anatomy_by_modality,
        sample_offsets=field_sample_offsets,
        field_id=field_id,
        layer_id=layer_id,
        geometry_id=field_geometry_id,
    ).advance(distribution, receptor_projection_baseline)
    return FiniteSharedMCMFieldResult(
        receptor_distribution=distribution,
        shared_field=shared_field,
        field_state=shared_field.snapshot(),
    )


def finite_multimodal_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (TimedReceptorFrame, FiniteSharedMCMFieldResult)
        for item in fields(cls)
    )
