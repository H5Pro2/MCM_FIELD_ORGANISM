"""Controlled audio-video capture into device-neutral receptor time models."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import math
import threading
import time
from typing import Callable

from .broadband_hearing_path import BroadbandHearingPath
from .controlled_audio_source import AudioFrameSource
from .finite_video_path import LocalChannelGridReceptor, VideoFrameSource
from .receptor_contract import (
    CommonFieldTime,
    from_auditory_receptor_state,
    from_visual_receptor_state,
)
from .receptor_time_model import (
    OrganismTimedReceptorFrame,
    ReceptorTimeAlignmentError,
    ReceptorTimeSequence,
)


Clock = Callable[[], int]


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
            timed_read = getattr(video_source, "read_timed_frame", None)
            if callable(timed_read):
                source_clock_id = getattr(video_source, "capture_clock_id", None)
                source_tick_rate = getattr(
                    video_source,
                    "capture_ticks_per_second",
                    None,
                )
                if source_clock_id != clock_id or source_tick_rate != 1_000_000_000.0:
                    raise ReceptorTimeAlignmentError(
                        "timed video source must share the organism clock"
                    )
                frame, start, end = timed_read()
            else:
                start = clock()
                frame = video_source.read_frame()
                end = clock()
            state = visual_receptor.analyze(frame, frame_index=frame_index)
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

