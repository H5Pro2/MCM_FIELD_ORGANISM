"""Predeclared organism windows for selection-free receptor occupancy audits."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, fields
import threading
import time
from typing import Iterable

from .broadband_hearing_path import BroadbandHearingPath
from .finite_video_path import LocalChannelGridReceptor, VideoFrameSource
from .live_audio_adapter import AudioFrameSource
from .receptor_contract import (
    CommonFieldTime,
    from_auditory_receptor_state,
    from_visual_receptor_state,
    technical_identifier,
)
from .receptor_time_alignment import (
    Clock,
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)


class CommonReceptorWindowError(ValueError):
    """Raised when a common window schedule or assignment is invalid."""


@dataclass(frozen=True, slots=True)
class CommonReceptorWindow:
    window_index: int
    field_time: CommonFieldTime

    def __post_init__(self) -> None:
        if (
            isinstance(self.window_index, bool)
            or not isinstance(self.window_index, int)
            or self.window_index < 0
        ):
            raise CommonReceptorWindowError("window_index must be non-negative")
        if not isinstance(self.field_time, CommonFieldTime):
            raise CommonReceptorWindowError(
                "common receptor window requires CommonFieldTime"
            )


@dataclass(frozen=True, slots=True)
class CommonReceptorWindowSchedule:
    clock_id: str
    windows: tuple[CommonReceptorWindow, ...]

    def __post_init__(self) -> None:
        clock_id = technical_identifier(self.clock_id, "clock_id")
        windows = tuple(self.windows)
        if not windows:
            raise CommonReceptorWindowError("window schedule cannot be empty")
        for expected_index, window in enumerate(windows):
            if window.window_index != expected_index:
                raise CommonReceptorWindowError(
                    "window indices must be contiguous and start at zero"
                )
            if window.field_time.clock_id != clock_id:
                raise CommonReceptorWindowError(
                    "every window must use the schedule organism clock"
                )
        for earlier, later in zip(windows, windows[1:]):
            if (
                earlier.field_time.window_end_tick
                != later.field_time.window_start_tick
            ):
                raise CommonReceptorWindowError(
                    "common receptor windows must be contiguous"
                )
        object.__setattr__(self, "clock_id", clock_id)
        object.__setattr__(self, "windows", windows)

    @property
    def start_tick(self) -> int:
        return self.windows[0].field_time.window_start_tick

    @property
    def end_tick(self) -> int:
        return self.windows[-1].field_time.window_end_tick


@dataclass(frozen=True, slots=True)
class ReceptorWindowAssignment:
    modality_id: str
    snapshot_id: str
    window_index: int


@dataclass(frozen=True, slots=True)
class ReceptorWindowOccupancy:
    window_index: int
    modality_counts: tuple[tuple[str, int], ...]

    def count_for(self, modality_id: str) -> int:
        return dict(self.modality_counts)[modality_id]


@dataclass(frozen=True, slots=True)
class ReceptorWindowAudit:
    clock_id: str
    modality_ids: tuple[str, ...]
    occupancies: tuple[ReceptorWindowOccupancy, ...]
    assignments: tuple[ReceptorWindowAssignment, ...]
    crossing_snapshot_ids: tuple[str, ...]
    outside_snapshot_ids: tuple[str, ...]
    exact_window_indices: tuple[int, ...]

    @property
    def every_window_has_exactly_one_state_per_modality(self) -> bool:
        return len(self.exact_window_indices) == len(self.occupancies)


@dataclass(frozen=True, slots=True)
class CapturedCommonReceptorWindowAudit:
    schedule: CommonReceptorWindowSchedule
    sequences: tuple[ReceptorTimeSequence, ...]
    audit: ReceptorWindowAudit

    def __post_init__(self) -> None:
        if not isinstance(self.schedule, CommonReceptorWindowSchedule):
            raise CommonReceptorWindowError("capture requires its declared schedule")
        sequences = tuple(self.sequences)
        if not sequences or any(
            not isinstance(item, ReceptorTimeSequence) for item in sequences
        ):
            raise CommonReceptorWindowError("capture requires receptor sequences")
        if tuple(item.modality_id for item in sequences) != self.audit.modality_ids:
            raise CommonReceptorWindowError(
                "captured sequences must match audited modalities"
            )
        object.__setattr__(self, "sequences", sequences)


def build_common_receptor_windows(
    *,
    anchor_tick: int,
    window_width_ticks: int,
    window_count: int,
    clock_id: str = "organism.monotonic_ns",
) -> CommonReceptorWindowSchedule:
    """Declare contiguous common windows before any receptor read occurs."""

    for value, role in (
        (anchor_tick, "anchor_tick"),
        (window_width_ticks, "window_width_ticks"),
        (window_count, "window_count"),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise CommonReceptorWindowError(f"{role} must be a positive integer")
    windows = tuple(
        CommonReceptorWindow(
            index,
            CommonFieldTime(
                clock_id,
                anchor_tick + index * window_width_ticks,
                anchor_tick + (index + 1) * window_width_ticks,
            ),
        )
        for index in range(window_count)
    )
    return CommonReceptorWindowSchedule(clock_id, windows)


def audit_receptor_window_assignment(
    sequences: Iterable[ReceptorTimeSequence],
    schedule: CommonReceptorWindowSchedule,
) -> ReceptorWindowAudit:
    """Count native completed states without selecting or reducing them."""

    if not isinstance(schedule, CommonReceptorWindowSchedule):
        raise CommonReceptorWindowError("audit requires a common window schedule")
    sequences_in = tuple(sorted(tuple(sequences), key=lambda item: item.modality_id))
    if not sequences_in or any(
        not isinstance(sequence, ReceptorTimeSequence)
        for sequence in sequences_in
    ):
        raise CommonReceptorWindowError(
            "audit requires receptor time sequences"
        )
    modality_ids = tuple(sequence.modality_id for sequence in sequences_in)
    if len(set(modality_ids)) != len(modality_ids):
        raise CommonReceptorWindowError("audit modalities must be unique")
    if any(sequence.clock_id != schedule.clock_id for sequence in sequences_in):
        raise CommonReceptorWindowError(
            "schedule and receptor sequences must share one organism clock"
        )

    assignments: list[ReceptorWindowAssignment] = []
    crossing: list[str] = []
    outside: list[str] = []
    counts = {
        window.window_index: {modality_id: 0 for modality_id in modality_ids}
        for window in schedule.windows
    }
    for sequence in sequences_in:
        for item in sequence.frames:
            start = item.field_time.window_start_tick
            end = item.field_time.window_end_tick
            contained = tuple(
                window
                for window in schedule.windows
                if start >= window.field_time.window_start_tick
                and end <= window.field_time.window_end_tick
            )
            if len(contained) == 1:
                window_index = contained[0].window_index
                counts[window_index][sequence.modality_id] += 1
                assignments.append(
                    ReceptorWindowAssignment(
                        sequence.modality_id,
                        item.frame.snapshot_id,
                        window_index,
                    )
                )
                continue
            intersects_schedule = (
                start < schedule.end_tick and end > schedule.start_tick
            )
            target = crossing if intersects_schedule else outside
            target.append(item.frame.snapshot_id)

    occupancies = tuple(
        ReceptorWindowOccupancy(
            window.window_index,
            tuple(
                (modality_id, counts[window.window_index][modality_id])
                for modality_id in modality_ids
            ),
        )
        for window in schedule.windows
    )
    exact = tuple(
        occupancy.window_index
        for occupancy in occupancies
        if all(count == 1 for _, count in occupancy.modality_counts)
    )
    return ReceptorWindowAudit(
        clock_id=schedule.clock_id,
        modality_ids=modality_ids,
        occupancies=occupancies,
        assignments=tuple(assignments),
        crossing_snapshot_ids=tuple(sorted(crossing)),
        outside_snapshot_ids=tuple(sorted(outside)),
        exact_window_indices=exact,
    )


def capture_audio_video_in_common_windows(
    audio_source: AudioFrameSource,
    video_source: VideoFrameSource,
    auditory_path: BroadbandHearingPath,
    visual_receptor: LocalChannelGridReceptor,
    schedule: CommonReceptorWindowSchedule,
    *,
    clock: Clock = time.monotonic_ns,
) -> CapturedCommonReceptorWindowAudit:
    """Capture native reduced states against a schedule declared beforehand."""

    if not isinstance(auditory_path, BroadbandHearingPath):
        raise CommonReceptorWindowError("auditory_path must be a BroadbandHearingPath")
    if not isinstance(visual_receptor, LocalChannelGridReceptor):
        raise CommonReceptorWindowError(
            "visual_receptor must be a LocalChannelGridReceptor"
        )
    if not isinstance(schedule, CommonReceptorWindowSchedule) or not callable(clock):
        raise CommonReceptorWindowError(
            "capture requires a declared schedule and callable organism clock"
        )
    if not auditory_path.is_fresh:
        raise CommonReceptorWindowError("auditory path must be fresh before capture")
    if clock() >= schedule.start_tick:
        raise CommonReceptorWindowError(
            "common window schedule must start after capture preparation"
        )

    start_gate = threading.Barrier(2)

    def wait_for_schedule() -> None:
        start_gate.wait()
        while True:
            remaining = schedule.start_tick - clock()
            if remaining <= 0:
                return
            time.sleep(min(remaining / 1_000_000_000.0, 0.001))

    def capture_auditory() -> ReceptorTimeSequence:
        frames_out = []
        wait_for_schedule()
        while True:
            start = clock()
            if start >= schedule.end_tick:
                break
            samples = audio_source.read_frame()
            state = auditory_path.push(samples)
            end = clock()
            if end <= start:
                raise CommonReceptorWindowError(
                    "organism clock must advance during every auditory read"
                )
            if state is not None:
                frames_out.append(
                    OrganismTimedReceptorFrame(
                        from_auditory_receptor_state(state),
                        CommonFieldTime(schedule.clock_id, start, end),
                    )
                )
        if not frames_out:
            raise CommonReceptorWindowError(
                "common windows produced no completed auditory receptor state"
            )
        return ReceptorTimeSequence(
            "auditory",
            auditory_path.geometry_id,
            schedule.clock_id,
            tuple(frames_out),
        )

    def capture_visual() -> ReceptorTimeSequence:
        frames_out = []
        frame_index = 0
        wait_for_schedule()
        while True:
            start = clock()
            if start >= schedule.end_tick:
                break
            frame = video_source.read_frame()
            state = visual_receptor.analyze(frame, frame_index=frame_index)
            end = clock()
            if end <= start:
                raise CommonReceptorWindowError(
                    "organism clock must advance during every visual read"
                )
            frames_out.append(
                OrganismTimedReceptorFrame(
                    from_visual_receptor_state(state),
                    CommonFieldTime(schedule.clock_id, start, end),
                )
            )
            frame_index += 1
        if not frames_out:
            raise CommonReceptorWindowError(
                "common windows produced no completed visual receptor state"
            )
        return ReceptorTimeSequence(
            "visual",
            visual_receptor.config.geometry_id,
            schedule.clock_id,
            tuple(frames_out),
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
    audit = audit_receptor_window_assignment(sequences, schedule)
    return CapturedCommonReceptorWindowAudit(schedule, sequences, audit)


def common_receptor_window_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            CommonReceptorWindow,
            CommonReceptorWindowSchedule,
            ReceptorWindowAssignment,
            ReceptorWindowOccupancy,
            ReceptorWindowAudit,
            CapturedCommonReceptorWindowAudit,
        )
        for item in fields(cls)
    )
