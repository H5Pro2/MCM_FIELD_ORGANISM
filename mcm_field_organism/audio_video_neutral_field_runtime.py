"""Finite audio-video capture into one neutral asynchronous MCM field."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math
import time
from typing import Callable, Iterable

from .broadband_hearing_path import BroadbandHearingPath
from .finite_audio_video_field_run import (
    ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    audio_video_dock_anatomies,
)
from .finite_video_path import LocalChannelGridReceptor, VideoFrameSource
from .field_step_time import MCMFieldStepTime
from .live_audio_adapter import AudioFrameSource
from .neutral_asynchronous_field_runtime import (
    NeutralAsynchronousFieldRun,
    run_neutral_asynchronous_field,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_time_alignment import (
    ReceptorTimeSequence,
    capture_timed_audio_video_receptor_sequences,
)
from .shared_mcm_field import SharedMCMField, build_shared_mcm_field


class AudioVideoNeutralFieldRuntimeError(ValueError):
    """Raised when a bounded audio-video history cannot enter one field."""


@dataclass(frozen=True, slots=True)
class CapturedAudioVideoNeutralFieldRun:
    """Reduced timed receptor history and its resulting shared field."""

    receptor_sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    field_run: NeutralAsynchronousFieldRun

    def __post_init__(self) -> None:
        sequences = tuple(self.receptor_sequences)
        if (
            len(sequences) != 2
            or any(not isinstance(item, ReceptorTimeSequence) for item in sequences)
            or tuple(item.modality_id for item in sequences)
            != ("auditory", "visual")
        ):
            raise AudioVideoNeutralFieldRuntimeError(
                "captured field run requires auditory and visual time sequences"
            )
        if not isinstance(self.field_run, NeutralAsynchronousFieldRun):
            raise AudioVideoNeutralFieldRuntimeError(
                "captured field run requires one neutral field run"
            )
        object.__setattr__(self, "receptor_sequences", sequences)


def _complete_field_step(
    sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence],
    ticks_per_second: float,
    *,
    start_tick: int | None = None,
) -> MCMFieldStepTime:
    all_frames = tuple(
        timed_frame
        for sequence in sequences
        for timed_frame in sequence.frames
    )
    return MCMFieldStepTime(
        clock_id=sequences[0].clock_id,
        start_tick=(
            min(
                timed_frame.field_time.window_start_tick
                for timed_frame in all_frames
            )
            if start_tick is None
            else start_tick
        ),
        end_tick=max(
            timed_frame.field_time.window_end_tick
            for timed_frame in all_frames
        ),
        ticks_per_second=ticks_per_second,
    )


def capture_audio_video_into_neutral_field(
    audio_source: AudioFrameSource,
    video_source: VideoFrameSource,
    auditory_path: BroadbandHearingPath,
    visual_receptor: LocalChannelGridReceptor,
    field_config: NeutralLocalFieldSubstrateConfig,
    *,
    afterimage_config: NeutralFastAfterimageConfig | None = None,
    initial_field: SharedMCMField | None = None,
    auditory_path_must_be_fresh: bool = True,
    visual_frame_index_start: int = 0,
    nominal_duration_seconds: float,
    field_sample_offsets: Iterable[Iterable[int]] = (
        ORTHOGONAL_FIELD_SAMPLE_OFFSETS
    ),
    clock: Callable[[], int] = time.monotonic_ns,
    clock_id: str = "organism.monotonic_ns",
    ticks_per_second: float = 1_000_000_000.0,
) -> CapturedAudioVideoNeutralFieldRun:
    """Capture native receptor rates and apply every completion to one field."""

    if not isinstance(field_config, NeutralLocalFieldSubstrateConfig):
        raise AudioVideoNeutralFieldRuntimeError(
            "audio-video field capture requires an explicit field configuration"
        )
    if initial_field is not None and not isinstance(initial_field, SharedMCMField):
        raise AudioVideoNeutralFieldRuntimeError(
            "initial_field must be one shared MCM field"
        )
    rate = float(ticks_per_second)
    if not math.isfinite(rate) or rate <= 0.0:
        raise AudioVideoNeutralFieldRuntimeError(
            "ticks_per_second must be finite and greater than zero"
        )
    offsets = tuple(tuple(offset) for offset in field_sample_offsets)
    if not offsets:
        raise AudioVideoNeutralFieldRuntimeError(
            "audio-video field capture requires local sample offsets"
        )

    try:
        sequences = capture_timed_audio_video_receptor_sequences(
            audio_source,
            video_source,
            auditory_path,
            visual_receptor,
            nominal_duration_seconds=nominal_duration_seconds,
            clock=clock,
            clock_id=clock_id,
            auditory_path_must_be_fresh=auditory_path_must_be_fresh,
            visual_frame_index_start=visual_frame_index_start,
        )
        field = initial_field
        if field is None:
            reference_frames = tuple(
                sequence.frames[0].frame for sequence in sequences
            )
            anatomies = audio_video_dock_anatomies(
                auditory_carrier_count=len(reference_frames[0].carrier_ids),
                visual_grid_columns=visual_receptor.config.grid_columns,
                visual_grid_rows=visual_receptor.config.grid_rows,
            )
            field = build_shared_mcm_field(
                reference_frames,
                anatomies,
                sample_offsets=offsets,
            )
        previous_end_tick = (
            None
            if field.last_distribution is None
            else field.last_distribution.field_time.window_end_tick
        )
        field_run = run_neutral_asynchronous_field(
            field,
            sequences,
            (
                _complete_field_step(
                    sequences,
                    rate,
                    start_tick=previous_end_tick,
                ),
            ),
            field_config,
            afterimage_config=afterimage_config,
        )
    except ValueError as exc:
        raise AudioVideoNeutralFieldRuntimeError(str(exc)) from exc

    return CapturedAudioVideoNeutralFieldRun(sequences, field_run)


def audio_video_neutral_field_runtime_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(CapturedAudioVideoNeutralFieldRun))
