"""Finite auditory and visual receptor contact in one shared MCM field."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math
from typing import Iterable

from .broadband_hearing_path import (
    AuditoryReceptorState,
    BroadbandHearingPath,
    BroadbandHearingSummary,
    capture_finite_broadband_hearing,
)
from .finite_multimodal_field_run import (
    FiniteSharedMCMFieldResult,
    TimedReceptorFrame,
    assemble_shared_mcm_field,
    capture_overlapping_receptor_frames,
)
from .finite_video_path import (
    FiniteVideoSummary,
    LocalChannelGridReceptor,
    VideoFrameSource,
    VisualReceptorState,
    capture_finite_video,
)
from .live_audio_adapter import AudioFrameSource
from .receptor_contract import (
    from_auditory_receptor_state,
    from_visual_receptor_state,
)
from .shared_mcm_field import ReceptorDockAnatomy


class FiniteAudioVideoFieldError(ValueError):
    """Raised when one finite auditory-visual field contact is incomplete."""


ORTHOGONAL_FIELD_SAMPLE_OFFSETS = ((-1, 0), (0, -1), (0, 1), (1, 0))


@dataclass(frozen=True, slots=True)
class FiniteAudioVideoFieldResult:
    """Reduced receptor summaries and their one shared field state."""

    auditory_summary: BroadbandHearingSummary
    visual_summary: FiniteVideoSummary
    timed_receptor_frames: tuple[TimedReceptorFrame, ...]
    shared_field_result: FiniteSharedMCMFieldResult

    def __post_init__(self) -> None:
        frames = tuple(self.timed_receptor_frames)
        if tuple(item.frame.modality_id for item in frames) != (
            "auditory",
            "visual",
        ):
            raise FiniteAudioVideoFieldError(
                "result requires one ordered auditory and one visual receptor frame"
            )
        distributed = self.shared_field_result.receptor_distribution
        if distributed.modality_ids != ("auditory", "visual"):
            raise FiniteAudioVideoFieldError(
                "shared field result must contain auditory and visual contacts"
            )
        object.__setattr__(self, "timed_receptor_frames", frames)


def audio_video_dock_anatomies(
    *,
    auditory_carrier_count: int,
    visual_grid_columns: int,
    visual_grid_rows: int,
    visual_channel_count: int = 3,
) -> dict[str, ReceptorDockAnatomy]:
    """Place both receptor docks in one explicit two-dimensional geometry."""

    dimensions = {
        "auditory_carrier_count": auditory_carrier_count,
        "visual_grid_columns": visual_grid_columns,
        "visual_grid_rows": visual_grid_rows,
        "visual_channel_count": visual_channel_count,
    }
    if any(
        isinstance(value, bool) or not isinstance(value, int) or value <= 0
        for value in dimensions.values()
    ):
        raise FiniteAudioVideoFieldError(
            "dock anatomy dimensions must be positive integers"
        )

    visual_row_width = visual_grid_columns * visual_channel_count
    visual_count = visual_row_width * visual_grid_rows
    return {
        "auditory": ReceptorDockAnatomy(
            modality_id="auditory",
            dock_id="dock.auditory",
            positions=tuple((0, column) for column in range(auditory_carrier_count)),
        ),
        "visual": ReceptorDockAnatomy(
            modality_id="visual",
            dock_id="dock.visual",
            positions=tuple(
                (1 + index // visual_row_width, index % visual_row_width)
                for index in range(visual_count)
            ),
        ),
    }


def capture_finite_audio_video_field(
    audio_source: AudioFrameSource,
    video_source: VideoFrameSource,
    auditory_path: BroadbandHearingPath,
    visual_receptor: LocalChannelGridReceptor,
    *,
    duration_seconds: float,
    video_frame_count: int,
    field_sample_offsets: Iterable[Iterable[int]] = (
        ORTHOGONAL_FIELD_SAMPLE_OFFSETS
    ),
) -> FiniteAudioVideoFieldResult:
    """Capture concurrent reduced contacts and advance one shared field once."""

    if not isinstance(auditory_path, BroadbandHearingPath):
        raise FiniteAudioVideoFieldError(
            "auditory_path must be a BroadbandHearingPath"
        )
    if not isinstance(visual_receptor, LocalChannelGridReceptor):
        raise FiniteAudioVideoFieldError(
            "visual_receptor must be a LocalChannelGridReceptor"
        )
    duration = float(duration_seconds)
    if not math.isfinite(duration) or duration <= 0.0:
        raise FiniteAudioVideoFieldError(
            "duration_seconds must be finite and greater than zero"
        )
    if (
        isinstance(video_frame_count, bool)
        or not isinstance(video_frame_count, int)
        or video_frame_count <= 0
    ):
        raise FiniteAudioVideoFieldError(
            "video_frame_count must be a positive integer"
        )
    visual_duration = (
        video_frame_count / visual_receptor.config.frames_per_second
    )
    if not math.isclose(
        visual_duration,
        duration,
        rel_tol=0.0,
        abs_tol=1e-10,
    ):
        raise FiniteAudioVideoFieldError(
            "audio and video requests must describe the same nominal duration"
        )

    auditory_states: list[AuditoryReceptorState] = []
    visual_states: list[VisualReceptorState] = []
    summaries: dict[str, object] = {}

    def capture_auditory():
        summary = capture_finite_broadband_hearing(
            audio_source,
            auditory_path,
            duration_seconds=duration,
            observer=auditory_states.append,
        )
        summaries["auditory"] = summary
        return from_auditory_receptor_state(auditory_states[-1])

    def capture_visual():
        summary = capture_finite_video(
            video_source,
            visual_receptor,
            frame_count=video_frame_count,
            observer=visual_states.append,
        )
        summaries["visual"] = summary
        return from_visual_receptor_state(visual_states[-1])

    timed = capture_overlapping_receptor_frames(
        {
            "auditory": capture_auditory,
            "visual": capture_visual,
        }
    )
    if not auditory_states or not visual_states:
        raise FiniteAudioVideoFieldError(
            "both receptors must produce a completed reduced state"
        )
    auditory_summary = summaries.get("auditory")
    visual_summary = summaries.get("visual")
    if not isinstance(auditory_summary, BroadbandHearingSummary):
        raise FiniteAudioVideoFieldError(
            "auditory capture did not return its completed summary"
        )
    if not isinstance(visual_summary, FiniteVideoSummary):
        raise FiniteAudioVideoFieldError(
            "visual capture did not return its completed summary"
        )

    anatomies = audio_video_dock_anatomies(
        auditory_carrier_count=len(auditory_states[-1].carrier_ids),
        visual_grid_columns=visual_receptor.config.grid_columns,
        visual_grid_rows=visual_receptor.config.grid_rows,
    )
    shared = assemble_shared_mcm_field(
        timed,
        anatomies,
        field_sample_offsets=field_sample_offsets,
    )
    return FiniteAudioVideoFieldResult(
        auditory_summary=auditory_summary,
        visual_summary=visual_summary,
        timed_receptor_frames=timed,
        shared_field_result=shared,
    )


def finite_audio_video_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(FiniteAudioVideoFieldResult))
