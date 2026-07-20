"""Pixel-only public video input for one bounded shared-field observation."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import math
from pathlib import Path

import numpy as np

from .field_step_time import MCMFieldStepTime
from .finite_video_path import (
    LocalChannelGridReceptor,
    VisualGridConfig,
    VisualReceptorState,
)
from .neutral_asynchronous_field_runtime import run_neutral_asynchronous_field
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_time_alignment import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)
from .shared_mcm_field import ReceptorDockAnatomy, build_shared_mcm_field


class PublicVisualWorldError(ValueError):
    """Raised when a public video cannot remain a bounded pixel-only source."""


@dataclass(frozen=True, slots=True)
class PublicVisualReceptorSequence:
    """Reduced visual states and their observed source timestamps."""

    states: tuple[VisualReceptorState, ...]
    source_timestamps_ms: tuple[int, ...]
    sampling_interval_ms: int
    decoded_frame_count: int

    def __post_init__(self) -> None:
        states = tuple(self.states)
        timestamps = tuple(self.source_timestamps_ms)
        if not states or any(
            not isinstance(item, VisualReceptorState) for item in states
        ):
            raise PublicVisualWorldError(
                "public visual sequence requires reduced visual receptor states"
            )
        if len(states) != len(timestamps):
            raise PublicVisualWorldError(
                "public visual states and source timestamps must align"
            )
        if any(
            isinstance(value, bool)
            or not isinstance(value, int)
            or value < 0
            for value in timestamps
        ):
            raise PublicVisualWorldError(
                "public visual timestamps must be non-negative integers"
            )
        if any(later <= earlier for earlier, later in zip(timestamps, timestamps[1:])):
            raise PublicVisualWorldError(
                "public visual timestamps must advance strictly"
            )
        interval = self.sampling_interval_ms
        decoded = self.decoded_frame_count
        if (
            isinstance(interval, bool)
            or not isinstance(interval, int)
            or interval < 1
        ):
            raise PublicVisualWorldError(
                "sampling_interval_ms must be a positive integer"
            )
        if (
            isinstance(decoded, bool)
            or not isinstance(decoded, int)
            or decoded < len(states)
        ):
            raise PublicVisualWorldError(
                "decoded_frame_count must cover every reduced state"
            )
        geometry_ids = {item.geometry_id for item in states}
        carrier_ids = {item.carrier_ids for item in states}
        frame_indices = tuple(item.frame_index for item in states)
        if len(geometry_ids) != 1 or len(carrier_ids) != 1:
            raise PublicVisualWorldError(
                "one public visual sequence requires one receptor geometry"
            )
        if frame_indices != tuple(range(len(states))):
            raise PublicVisualWorldError(
                "public visual receptor states must use canonical sequence indices"
            )
        object.__setattr__(self, "states", states)
        object.__setattr__(self, "source_timestamps_ms", timestamps)

    @property
    def duration_ms(self) -> int:
        return len(self.states) * self.sampling_interval_ms

    def reduced_digest(self) -> str:
        digest = hashlib.sha256()
        for state, timestamp in zip(
            self.states,
            self.source_timestamps_ms,
            strict=True,
        ):
            digest.update(state.digest().encode("ascii"))
            digest.update(str(timestamp).encode("ascii"))
        return digest.hexdigest()


@dataclass(frozen=True, slots=True)
class PublicVisualWorldObservation:
    """Compact observer result without raw frames, labels, audio, or metadata."""

    receptor_geometry_id: str
    sampled_frame_count: int
    decoded_frame_count: int
    duration_ms: int
    sampling_interval_ms: int
    reduced_sequence_digest: str
    repeated_sequence_digest: str
    receptor_value_span_max: float
    field_activation_min: float
    field_activation_max: float
    field_afterimage_min: float
    field_afterimage_max: float
    static_baseline_activation_max_difference: float
    static_baseline_afterimage_max_difference: float
    exact_reduced_repeat: bool
    audio_used: bool = False
    metadata_used_by_receptor: bool = False
    raw_frames_retained: bool = False
    semantic_roles_used: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.receptor_geometry_id, str) or not self.receptor_geometry_id:
            raise PublicVisualWorldError(
                "receptor_geometry_id must be a technical identifier"
            )
        for role in (
            "sampled_frame_count",
            "decoded_frame_count",
            "duration_ms",
            "sampling_interval_ms",
        ):
            value = getattr(self, role)
            if (
                isinstance(value, bool)
                or not isinstance(value, int)
                or value < 1
            ):
                raise PublicVisualWorldError(f"{role} must be a positive integer")
        for role in ("reduced_sequence_digest", "repeated_sequence_digest"):
            value = getattr(self, role)
            if not isinstance(value, str) or not value:
                raise PublicVisualWorldError(f"{role} must be non-empty")
        for role in (
            "receptor_value_span_max",
            "field_activation_min",
            "field_activation_max",
            "field_afterimage_min",
            "field_afterimage_max",
            "static_baseline_activation_max_difference",
            "static_baseline_afterimage_max_difference",
        ):
            value = float(getattr(self, role))
            if not math.isfinite(value):
                raise PublicVisualWorldError(f"{role} must be finite")
            object.__setattr__(self, role, value)
        if self.field_activation_min > self.field_activation_max:
            raise PublicVisualWorldError("field activation range is inverted")
        if self.field_afterimage_min > self.field_afterimage_max:
            raise PublicVisualWorldError("field afterimage range is inverted")
        flags = (
            self.exact_reduced_repeat,
            self.audio_used,
            self.metadata_used_by_receptor,
            self.raw_frames_retained,
            self.semantic_roles_used,
        )
        if any(not isinstance(value, bool) for value in flags):
            raise PublicVisualWorldError(
                "public visual observation flags must be boolean"
            )
        if (
            not self.exact_reduced_repeat
            or self.audio_used
            or self.metadata_used_by_receptor
            or self.raw_frames_retained
            or self.semantic_roles_used
        ):
            raise PublicVisualWorldError(
                "public visual observation violated its pixel-only boundary"
            )


def decode_public_visual_receptor_sequence(
    path: Path,
    receptor: LocalChannelGridReceptor,
    *,
    sampling_interval_ms: int = 125,
    max_duration_ms: int = 60_000,
) -> PublicVisualReceptorSequence:
    """Decode video pixels at fixed observed timestamps without reading audio."""

    if not isinstance(path, Path) or not path.is_file():
        raise PublicVisualWorldError("public visual source must be a local file")
    if not isinstance(receptor, LocalChannelGridReceptor):
        raise PublicVisualWorldError(
            "public visual source requires the existing visual receptor"
        )
    if (
        isinstance(sampling_interval_ms, bool)
        or not isinstance(sampling_interval_ms, int)
        or sampling_interval_ms < 1
    ):
        raise PublicVisualWorldError(
            "sampling_interval_ms must be a positive integer"
        )
    if (
        isinstance(max_duration_ms, bool)
        or not isinstance(max_duration_ms, int)
        or max_duration_ms < sampling_interval_ms
    ):
        raise PublicVisualWorldError(
            "max_duration_ms must cover at least one sampling interval"
        )
    try:
        import cv2  # type: ignore[import-not-found]
    except ImportError as exc:
        raise PublicVisualWorldError(
            "optional dependency 'opencv-python' is required"
        ) from exc

    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        capture.release()
        raise PublicVisualWorldError("public visual source cannot be opened")
    states = []
    timestamps = []
    decoded = 0
    next_target_ms = 0
    last_source_ms = -1
    try:
        while next_target_ms < max_duration_ms:
            ok, frame = capture.read()
            if not ok:
                break
            decoded += 1
            timestamp = float(capture.get(cv2.CAP_PROP_POS_MSEC))
            if not math.isfinite(timestamp) or timestamp < 0.0:
                raise PublicVisualWorldError(
                    "decoded frame lacks a valid source timestamp"
                )
            source_ms = int(round(timestamp))
            if source_ms < last_source_ms:
                raise PublicVisualWorldError(
                    "decoded source timestamps moved backwards"
                )
            last_source_ms = source_ms
            if source_ms < next_target_ms:
                continue
            expected_shape = (
                receptor.config.source_height,
                receptor.config.source_width,
                3,
            )
            if not isinstance(frame, np.ndarray) or frame.shape != expected_shape:
                raise PublicVisualWorldError(
                    "decoded frame does not match the declared receptor geometry"
                )
            if frame.dtype != np.uint8:
                raise PublicVisualWorldError(
                    "decoded frame must use uint8 channel values"
                )
            states.append(
                receptor.analyze(frame, frame_index=len(states))
            )
            timestamps.append(source_ms)
            next_target_ms += sampling_interval_ms
    finally:
        capture.release()
    if not states:
        raise PublicVisualWorldError(
            "public visual source ended before one receptor sample"
        )
    return PublicVisualReceptorSequence(
        states=tuple(states),
        source_timestamps_ms=tuple(timestamps),
        sampling_interval_ms=sampling_interval_ms,
        decoded_frame_count=decoded,
    )


def _timed_sequence(
    reduced: PublicVisualReceptorSequence,
    *,
    static: bool,
) -> ReceptorTimeSequence:
    values = reduced.states[0].channel_values if static else None
    timed = []
    for index, state in enumerate(reduced.states):
        start = index * reduced.sampling_interval_ms
        end = start + reduced.sampling_interval_ms
        frame_values = values if values is not None else state.channel_values
        frame = ReceptorContactFrame(
            modality_id="visual",
            geometry_id=state.geometry_id,
            snapshot_id=f"visual.receptor.{index}",
            clock_id="public.video.pixel_time",
            window_start_tick=start,
            window_end_tick=end,
            carrier_ids=state.carrier_ids,
            values=frame_values,
        )
        timed.append(
            OrganismTimedReceptorFrame(
                frame=frame,
                field_time=CommonFieldTime(
                    "public.video.pixel_time",
                    start,
                    end,
                ),
            )
        )
    return ReceptorTimeSequence(
        modality_id="visual",
        geometry_id=reduced.states[0].geometry_id,
        clock_id="public.video.pixel_time",
        frames=tuple(timed),
    )


def _visual_anatomy(config: VisualGridConfig) -> ReceptorDockAnatomy:
    row_width = config.grid_columns * 3
    return ReceptorDockAnatomy(
        modality_id="visual",
        dock_id="dock.visual",
        positions=tuple(
            (index // row_width, index % row_width)
            for index in range(config.carrier_count)
        ),
    )


def _run_reduced_sequence(
    reduced: PublicVisualReceptorSequence,
    receptor: LocalChannelGridReceptor,
    *,
    static: bool,
):
    sequence = _timed_sequence(reduced, static=static)
    field = build_shared_mcm_field(
        (sequence.frames[0].frame,),
        {"visual": _visual_anatomy(receptor.config)},
        sample_offsets=((-1, 0), (0, -1), (0, 1), (1, 0)),
    )
    step = MCMFieldStepTime(
        clock_id=sequence.clock_id,
        start_tick=0,
        end_tick=reduced.duration_ms,
        ticks_per_second=1_000.0,
    )
    return run_neutral_asynchronous_field(
        field,
        (sequence,),
        (step,),
        NeutralLocalFieldSubstrateConfig(1.0),
        afterimage_config=NeutralFastAfterimageConfig(0.5),
    ).field


def observe_public_visual_world(
    reduced: PublicVisualReceptorSequence,
    repeated: PublicVisualReceptorSequence,
    receptor: LocalChannelGridReceptor,
) -> PublicVisualWorldObservation:
    """Compare one pixel history with repetition and a static visual baseline."""

    if not isinstance(reduced, PublicVisualReceptorSequence) or not isinstance(
        repeated,
        PublicVisualReceptorSequence,
    ):
        raise PublicVisualWorldError(
            "public visual observation requires two reduced decodings"
        )
    if not isinstance(receptor, LocalChannelGridReceptor):
        raise PublicVisualWorldError(
            "public visual observation requires the existing visual receptor"
        )
    if reduced.sampling_interval_ms != repeated.sampling_interval_ms:
        raise PublicVisualWorldError(
            "repeated visual sequence changed the sampling interval"
        )
    if len(reduced.states) != len(repeated.states):
        raise PublicVisualWorldError(
            "repeated visual sequence changed the sample count"
        )
    first_digest = reduced.reduced_digest()
    repeated_digest = repeated.reduced_digest()
    if first_digest != repeated_digest:
        raise PublicVisualWorldError(
            "public visual source did not reproduce its reduced pixel sequence"
        )

    actual = _run_reduced_sequence(reduced, receptor, static=False)
    static = _run_reduced_sequence(reduced, receptor, static=True)
    actual_activation = np.asarray(
        [item.activation for item in actual.layer.neurons],
        dtype=np.float64,
    )
    static_activation = np.asarray(
        [item.activation for item in static.layer.neurons],
        dtype=np.float64,
    )
    actual_afterimage = np.asarray(
        [item.afterimage for item in actual.layer.neurons],
        dtype=np.float64,
    )
    static_afterimage = np.asarray(
        [item.afterimage for item in static.layer.neurons],
        dtype=np.float64,
    )
    values = np.asarray(
        [state.channel_values for state in reduced.states],
        dtype=np.float64,
    )
    return PublicVisualWorldObservation(
        receptor_geometry_id=reduced.states[0].geometry_id,
        sampled_frame_count=len(reduced.states),
        decoded_frame_count=reduced.decoded_frame_count,
        duration_ms=reduced.duration_ms,
        sampling_interval_ms=reduced.sampling_interval_ms,
        reduced_sequence_digest=first_digest,
        repeated_sequence_digest=repeated_digest,
        receptor_value_span_max=float(np.max(np.ptp(values, axis=0))),
        field_activation_min=float(np.min(actual_activation)),
        field_activation_max=float(np.max(actual_activation)),
        field_afterimage_min=float(np.min(actual_afterimage)),
        field_afterimage_max=float(np.max(actual_afterimage)),
        static_baseline_activation_max_difference=float(
            np.max(np.abs(actual_activation - static_activation))
        ),
        static_baseline_afterimage_max_difference=float(
            np.max(np.abs(actual_afterimage - static_afterimage))
        ),
        exact_reduced_repeat=True,
    )


def public_visual_world_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(PublicVisualWorldObservation))
