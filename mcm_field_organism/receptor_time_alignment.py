"""Organism-clock audit for reduced receptor states without forced pairing."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, fields
import math
import threading
import time
from typing import Callable

from .broadband_hearing_path import BroadbandHearingPath
from .finite_video_path import LocalChannelGridReceptor, VideoFrameSource
from .live_audio_adapter import AudioFrameSource
from .receptor_contract import (
    CommonFieldTime,
    ReceptorContactFrame,
    from_auditory_receptor_state,
    from_visual_receptor_state,
)


class ReceptorTimeAlignmentError(ValueError):
    """Raised when reduced receptor states cannot share one organism clock."""


Clock = Callable[[], int]


@dataclass(frozen=True, slots=True)
class OrganismTimedReceptorFrame:
    """One reduced receptor state measured on the organism clock."""

    frame: ReceptorContactFrame
    field_time: CommonFieldTime

    def __post_init__(self) -> None:
        if not isinstance(self.frame, ReceptorContactFrame):
            raise ReceptorTimeAlignmentError(
                "timed receptor state requires a reduced receptor frame"
            )
        if not isinstance(self.field_time, CommonFieldTime):
            raise ReceptorTimeAlignmentError(
                "timed receptor state requires one organism-clock interval"
            )


@dataclass(frozen=True, slots=True)
class ReceptorTimeSequence:
    """Ordered reduced states from one receptor geometry."""

    modality_id: str
    geometry_id: str
    clock_id: str
    frames: tuple[OrganismTimedReceptorFrame, ...]

    def __post_init__(self) -> None:
        frames_in = tuple(self.frames)
        if not frames_in:
            raise ReceptorTimeAlignmentError(
                "receptor time sequence cannot be empty"
            )
        if any(
            item.frame.modality_id != self.modality_id
            or item.frame.geometry_id != self.geometry_id
            or item.field_time.clock_id != self.clock_id
            for item in frames_in
        ):
            raise ReceptorTimeAlignmentError(
                "sequence identity must match every timed receptor state"
            )
        snapshot_ids = [item.frame.snapshot_id for item in frames_in]
        if len(set(snapshot_ids)) != len(snapshot_ids):
            raise ReceptorTimeAlignmentError(
                "receptor sequence snapshot identities must be unique"
            )
        for earlier, later in zip(frames_in, frames_in[1:]):
            if (
                later.field_time.window_start_tick
                < earlier.field_time.window_end_tick
            ):
                raise ReceptorTimeAlignmentError(
                    "one receptor sequence cannot overlap or move backwards"
                )
        object.__setattr__(self, "frames", frames_in)


@dataclass(frozen=True, slots=True)
class ReceptorTimeOverlap:
    """One measured interval intersection, not a selected field pair."""

    first_snapshot_id: str
    second_snapshot_id: str
    window_start_tick: int
    window_end_tick: int

    def __post_init__(self) -> None:
        if (
            not isinstance(self.first_snapshot_id, str)
            or not self.first_snapshot_id
            or not isinstance(self.second_snapshot_id, str)
            or not self.second_snapshot_id
        ):
            raise ReceptorTimeAlignmentError(
                "time overlap requires two snapshot identities"
            )
        if (
            isinstance(self.window_start_tick, bool)
            or isinstance(self.window_end_tick, bool)
            or not isinstance(self.window_start_tick, int)
            or not isinstance(self.window_end_tick, int)
            or self.window_start_tick < 0
            or self.window_end_tick <= self.window_start_tick
        ):
            raise ReceptorTimeAlignmentError(
                "time overlap must contain a positive interval"
            )


@dataclass(frozen=True, slots=True)
class ReceptorTimeAlignmentAudit:
    """Complete pairwise overlap audit without interpolation or selection."""

    clock_id: str
    modality_ids: tuple[str, str]
    frame_counts: tuple[int, int]
    overlaps: tuple[ReceptorTimeOverlap, ...]
    unambiguous_overlaps: tuple[ReceptorTimeOverlap, ...]
    ambiguous_snapshot_ids: tuple[str, ...]
    unmatched_snapshot_ids: tuple[str, ...]

    @property
    def has_complete_one_to_one_alignment(self) -> bool:
        return (
            not self.ambiguous_snapshot_ids
            and not self.unmatched_snapshot_ids
            and len(self.unambiguous_overlaps) == min(self.frame_counts)
            and self.frame_counts[0] == self.frame_counts[1]
        )


@dataclass(frozen=True, slots=True)
class CapturedReceptorTimeAudit:
    """Two reduced time sequences and their selection-free audit."""

    sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    audit: ReceptorTimeAlignmentAudit

    def __post_init__(self) -> None:
        sequences = tuple(self.sequences)
        if len(sequences) != 2:
            raise ReceptorTimeAlignmentError(
                "captured time audit requires exactly two receptor sequences"
            )
        if tuple(item.modality_id for item in sequences) != self.audit.modality_ids:
            raise ReceptorTimeAlignmentError(
                "captured sequences must match the audited modalities"
            )
        object.__setattr__(self, "sequences", sequences)


def _ordered_sequence(
    modality_id: str,
    geometry_id: str,
    clock_id: str,
    frames_in: list[OrganismTimedReceptorFrame],
) -> ReceptorTimeSequence:
    return ReceptorTimeSequence(
        modality_id=modality_id,
        geometry_id=geometry_id,
        clock_id=clock_id,
        frames=tuple(frames_in),
    )


def audit_receptor_time_alignment(
    first: ReceptorTimeSequence,
    second: ReceptorTimeSequence,
) -> ReceptorTimeAlignmentAudit:
    """Report every real overlap and reject hidden post-capture pairing."""

    if not isinstance(first, ReceptorTimeSequence) or not isinstance(
        second, ReceptorTimeSequence
    ):
        raise ReceptorTimeAlignmentError(
            "alignment audit requires two receptor time sequences"
        )
    if first.modality_id == second.modality_id:
        raise ReceptorTimeAlignmentError(
            "alignment audit requires two different modalities"
        )
    if first.clock_id != second.clock_id:
        raise ReceptorTimeAlignmentError(
            "alignment audit requires one organism clock"
        )
    ordered = tuple(
        sorted((first, second), key=lambda item: item.modality_id)
    )
    left, right = ordered
    overlaps = []
    degree: dict[str, int] = {
        item.frame.snapshot_id: 0
        for sequence in ordered
        for item in sequence.frames
    }
    for left_item in left.frames:
        for right_item in right.frames:
            start = max(
                left_item.field_time.window_start_tick,
                right_item.field_time.window_start_tick,
            )
            end = min(
                left_item.field_time.window_end_tick,
                right_item.field_time.window_end_tick,
            )
            if start >= end:
                continue
            overlap = ReceptorTimeOverlap(
                first_snapshot_id=left_item.frame.snapshot_id,
                second_snapshot_id=right_item.frame.snapshot_id,
                window_start_tick=start,
                window_end_tick=end,
            )
            overlaps.append(overlap)
            degree[overlap.first_snapshot_id] += 1
            degree[overlap.second_snapshot_id] += 1

    unambiguous = tuple(
        item
        for item in overlaps
        if degree[item.first_snapshot_id] == 1
        and degree[item.second_snapshot_id] == 1
    )
    ambiguous = {
        snapshot_id
        for item in overlaps
        if degree[item.first_snapshot_id] > 1
        or degree[item.second_snapshot_id] > 1
        for snapshot_id in (
            item.first_snapshot_id,
            item.second_snapshot_id,
        )
    }
    return ReceptorTimeAlignmentAudit(
        clock_id=left.clock_id,
        modality_ids=(left.modality_id, right.modality_id),
        frame_counts=(len(left.frames), len(right.frames)),
        overlaps=tuple(overlaps),
        unambiguous_overlaps=unambiguous,
        ambiguous_snapshot_ids=tuple(sorted(ambiguous)),
        unmatched_snapshot_ids=tuple(
            sorted(snapshot_id for snapshot_id, count in degree.items() if count == 0)
        ),
    )


def capture_timed_audio_video_receptor_sequences(
    audio_source: AudioFrameSource,
    video_source: VideoFrameSource,
    auditory_path: BroadbandHearingPath,
    visual_receptor: LocalChannelGridReceptor,
    *,
    nominal_duration_seconds: float,
    clock: Clock = time.monotonic_ns,
    clock_id: str = "organism.monotonic_ns",
    auditory_path_must_be_fresh: bool = True,
    visual_frame_index_start: int = 0,
) -> tuple[ReceptorTimeSequence, ReceptorTimeSequence]:
    """Capture reduced native-rate sequences on one organism clock."""

    if not isinstance(auditory_path, BroadbandHearingPath):
        raise ReceptorTimeAlignmentError(
            "auditory_path must be a BroadbandHearingPath"
        )
    if not isinstance(visual_receptor, LocalChannelGridReceptor):
        raise ReceptorTimeAlignmentError(
            "visual_receptor must be a LocalChannelGridReceptor"
        )
    duration = float(nominal_duration_seconds)
    if not math.isfinite(duration) or duration <= 0.0 or duration > 10.0:
        raise ReceptorTimeAlignmentError(
            "nominal_duration_seconds must be within the finite 0..10 second interval"
        )
    auditory_exact = duration / auditory_path.receptor.config.hop_seconds
    auditory_count = round(auditory_exact)
    if (
        auditory_count < auditory_path.receptor.config.warmup_hops
        or not math.isclose(
            auditory_exact,
            auditory_count,
            rel_tol=0.0,
            abs_tol=1e-10,
        )
    ):
        raise ReceptorTimeAlignmentError(
            "duration must contain complete auditory chunks and one receptor window"
        )
    visual_exact = duration * visual_receptor.config.frames_per_second
    visual_count = round(visual_exact)
    if visual_count <= 0 or not math.isclose(
        visual_exact,
        visual_count,
        rel_tol=0.0,
        abs_tol=1e-10,
    ):
        raise ReceptorTimeAlignmentError(
            "duration must contain complete visual frames"
        )
    if not callable(clock) or not isinstance(clock_id, str) or not clock_id:
        raise ReceptorTimeAlignmentError(
            "capture requires one named callable organism clock"
        )
    if not isinstance(auditory_path_must_be_fresh, bool):
        raise ReceptorTimeAlignmentError(
            "auditory_path_must_be_fresh must be boolean"
        )
    if (
        isinstance(visual_frame_index_start, bool)
        or not isinstance(visual_frame_index_start, int)
        or visual_frame_index_start < 0
    ):
        raise ReceptorTimeAlignmentError(
            "visual_frame_index_start must be a non-negative integer"
        )
    if auditory_path_must_be_fresh and not auditory_path.is_fresh:
        raise ReceptorTimeAlignmentError(
            "auditory path must be fresh before timed capture"
        )

    start_gate = threading.Barrier(2)

    def capture_auditory() -> ReceptorTimeSequence:
        frames_out = []
        start_gate.wait()
        for _ in range(auditory_count):
            timed_read = getattr(audio_source, "read_timed_frame", None)
            if callable(timed_read):
                source_clock_id = getattr(audio_source, "capture_clock_id", None)
                source_tick_rate = getattr(
                    audio_source,
                    "capture_ticks_per_second",
                    None,
                )
                if source_clock_id != clock_id or source_tick_rate != 1_000_000_000.0:
                    raise ReceptorTimeAlignmentError(
                        "timed audio source must share the organism clock"
                    )
                samples, start, end = timed_read()
            else:
                start = clock()
                samples = audio_source.read_frame()
                end = clock()
            state = auditory_path.push(samples)
            if end <= start:
                raise ReceptorTimeAlignmentError(
                    "organism clock must advance during every auditory read"
                )
            if state is not None:
                frames_out.append(
                    OrganismTimedReceptorFrame(
                        from_auditory_receptor_state(state),
                        CommonFieldTime(clock_id, start, end),
                    )
                )
        return _ordered_sequence(
            "auditory",
            auditory_path.geometry_id,
            clock_id,
            frames_out,
        )

    def capture_visual() -> ReceptorTimeSequence:
        frames_out = []
        start_gate.wait()
        for frame_index in range(
            visual_frame_index_start,
            visual_frame_index_start + visual_count,
        ):
            start = clock()
            frame = video_source.read_frame()
            state = visual_receptor.analyze(frame, frame_index=frame_index)
            end = clock()
            if end <= start:
                raise ReceptorTimeAlignmentError(
                    "organism clock must advance during every visual read"
                )
            frames_out.append(
                OrganismTimedReceptorFrame(
                    from_visual_receptor_state(state),
                    CommonFieldTime(clock_id, start, end),
                )
            )
        return _ordered_sequence(
            "visual",
            visual_receptor.config.geometry_id,
            clock_id,
            frames_out,
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        auditory_future = executor.submit(capture_auditory)
        visual_future = executor.submit(capture_visual)
        sequences = tuple(
            sorted(
                (auditory_future.result(), visual_future.result()),
                key=lambda item: item.modality_id,
            )
        )
    return sequences


def capture_timed_audio_video_receptors(
    audio_source: AudioFrameSource,
    video_source: VideoFrameSource,
    auditory_path: BroadbandHearingPath,
    visual_receptor: LocalChannelGridReceptor,
    *,
    nominal_duration_seconds: float,
    clock: Clock = time.monotonic_ns,
    clock_id: str = "organism.monotonic_ns",
) -> CapturedReceptorTimeAudit:
    """Audit the neutral concurrent receptor sequences without pairing them."""

    sequences = capture_timed_audio_video_receptor_sequences(
        audio_source,
        video_source,
        auditory_path,
        visual_receptor,
        nominal_duration_seconds=nominal_duration_seconds,
        clock=clock,
        clock_id=clock_id,
    )
    audit = audit_receptor_time_alignment(sequences[0], sequences[1])
    return CapturedReceptorTimeAudit(sequences, audit)


def receptor_time_alignment_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            OrganismTimedReceptorFrame,
            ReceptorTimeSequence,
            ReceptorTimeOverlap,
            ReceptorTimeAlignmentAudit,
            CapturedReceptorTimeAudit,
        )
        for item in fields(cls)
    )
