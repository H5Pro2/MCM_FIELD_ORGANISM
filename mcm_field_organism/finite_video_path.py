"""Finite passive video path before the visual MCM field boundary."""

from __future__ import annotations

from dataclasses import dataclass, fields
from enum import Enum
import hashlib
import json
import math
from typing import Callable, Iterable, Protocol

import numpy as np


class VisualCaptureError(ValueError):
    """Raised when a finite visual source violates its technical contract."""


class VisualReceptorContact(str, Enum):
    ACTIVE_ZERO = "active_zero"
    ACTIVE_LIGHT = "active_light"


@dataclass(frozen=True, slots=True)
class VisualGridConfig:
    source_width: int = 1920
    source_height: int = 1080
    grid_columns: int = 12
    grid_rows: int = 8
    frames_per_second: float = 30.0

    def __post_init__(self) -> None:
        integer_roles = (
            "source_width",
            "source_height",
            "grid_columns",
            "grid_rows",
        )
        for role in integer_roles:
            value = getattr(self, role)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise VisualCaptureError(f"{role} must be a positive integer")
        if self.source_width % self.grid_columns != 0:
            raise VisualCaptureError("grid_columns must divide source_width exactly")
        if self.source_height % self.grid_rows != 0:
            raise VisualCaptureError("grid_rows must divide source_height exactly")
        rate = float(self.frames_per_second)
        if not math.isfinite(rate) or rate <= 0.0:
            raise VisualCaptureError("frames_per_second must be finite and greater than zero")
        object.__setattr__(self, "frames_per_second", rate)

    @property
    def carrier_count(self) -> int:
        return self.grid_rows * self.grid_columns * 3

    @property
    def geometry_id(self) -> str:
        return (
            f"visual.grid{self.grid_columns}x{self.grid_rows}.channels3."
            f"source{self.source_width}x{self.source_height}.v1"
        )

    @property
    def carrier_ids(self) -> tuple[str, ...]:
        return tuple(
            f"visual.cell.r{row}.c{column}.channel{channel}"
            for row in range(self.grid_rows)
            for column in range(self.grid_columns)
            for channel in range(3)
        )


@dataclass(frozen=True, slots=True)
class VisualReceptorState:
    modality_id: str
    geometry_id: str
    frame_index: int
    carrier_ids: tuple[str, ...]
    channel_values: tuple[float, ...]
    contact: VisualReceptorContact

    def __post_init__(self) -> None:
        if self.modality_id != "visual":
            raise VisualCaptureError("visual receptor state requires modality_id='visual'")
        if not isinstance(self.geometry_id, str) or not self.geometry_id:
            raise VisualCaptureError("geometry_id must be a non-empty technical identifier")
        if isinstance(self.frame_index, bool) or not isinstance(self.frame_index, int):
            raise VisualCaptureError("frame_index must be an integer")
        if self.frame_index < 0:
            raise VisualCaptureError("frame_index must be non-negative")
        carriers = tuple(self.carrier_ids)
        values = tuple(float(value) for value in self.channel_values)
        if not carriers or len(set(carriers)) != len(carriers):
            raise VisualCaptureError("carrier_ids must be non-empty and unique")
        if len(values) != len(carriers):
            raise VisualCaptureError("channel_values must match carrier geometry")
        if any(not math.isfinite(value) or value < 0.0 or value > 1.0 for value in values):
            raise VisualCaptureError("channel_values must stay within the finite 0..1 domain")
        contact = VisualReceptorContact(self.contact)
        expected = (
            VisualReceptorContact.ACTIVE_LIGHT
            if any(value != 0.0 for value in values)
            else VisualReceptorContact.ACTIVE_ZERO
        )
        if contact is not expected:
            raise VisualCaptureError("contact must match exact local-channel zero status")
        object.__setattr__(self, "carrier_ids", carriers)
        object.__setattr__(self, "channel_values", values)
        object.__setattr__(self, "contact", contact)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "modality_id": self.modality_id,
            "geometry_id": self.geometry_id,
            "frame_index": self.frame_index,
            "carrier_ids": list(self.carrier_ids),
            "channel_values": list(self.channel_values),
            "contact": self.contact.value,
        }

    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class FiniteVideoSummary:
    geometry_id: str
    carrier_ids: tuple[str, ...]
    input_frames: int
    output_states: int
    duration_seconds: float
    value_min: tuple[float, ...]
    value_max: tuple[float, ...]
    value_mean: tuple[float, ...]
    active_zero_count: int
    active_light_count: int
    sequence_digest: str


class VideoFrameSource(Protocol):
    def read_frame(self) -> np.ndarray: ...


class SyntheticVideoFrameSource:
    """Finite in-memory source reserved for controlled technical tests."""

    def __init__(self, frames_in: Iterable[np.ndarray]) -> None:
        frames_out = []
        for frame in frames_in:
            stored = np.array(frame, copy=True)
            stored.setflags(write=False)
            frames_out.append(stored)
        self._frames = tuple(frames_out)
        self._cursor = 0

    @property
    def frames_read(self) -> int:
        return self._cursor

    def read_frame(self) -> np.ndarray:
        if self._cursor >= len(self._frames):
            raise VisualCaptureError("video source ended before finite capture completed")
        frame = self._frames[self._cursor]
        self._cursor += 1
        return frame


def _validated_frame(frame: object, config: VisualGridConfig) -> np.ndarray:
    if not isinstance(frame, np.ndarray):
        raise VisualCaptureError("video frame must be a numpy array")
    if frame.dtype != np.uint8:
        raise VisualCaptureError("video frame must use uint8 channel values")
    expected_shape = (config.source_height, config.source_width, 3)
    if frame.shape != expected_shape:
        raise VisualCaptureError(f"video frame must have exact shape {expected_shape}")
    return frame


class LocalChannelGridReceptor:
    """Map one raw frame to independent local technical channel means."""

    def __init__(self, config: VisualGridConfig = VisualGridConfig()) -> None:
        self.config = config

    def analyze(self, frame: object, *, frame_index: int) -> VisualReceptorState:
        if isinstance(frame_index, bool) or not isinstance(frame_index, int) or frame_index < 0:
            raise VisualCaptureError("frame_index must be a non-negative integer")
        image = _validated_frame(frame, self.config)
        block_height = self.config.source_height // self.config.grid_rows
        block_width = self.config.source_width // self.config.grid_columns
        local = image.reshape(
            self.config.grid_rows,
            block_height,
            self.config.grid_columns,
            block_width,
            3,
        ).mean(axis=(1, 3))
        values = tuple(float(value) / 255.0 for value in local.reshape(-1))
        contact = (
            VisualReceptorContact.ACTIVE_LIGHT
            if any(value != 0.0 for value in values)
            else VisualReceptorContact.ACTIVE_ZERO
        )
        return VisualReceptorState(
            modality_id="visual",
            geometry_id=self.config.geometry_id,
            frame_index=frame_index,
            carrier_ids=self.config.carrier_ids,
            channel_values=values,
            contact=contact,
        )


def global_channel_mean_baseline(
    frame: object,
    config: VisualGridConfig,
) -> tuple[float, float, float]:
    image = _validated_frame(frame, config)
    result = image.mean(axis=(0, 1)) / 255.0
    return float(result[0]), float(result[1]), float(result[2])


VisualObserver = Callable[[VisualReceptorState], object]


def capture_finite_video(
    source: VideoFrameSource,
    receptor: LocalChannelGridReceptor,
    *,
    frame_count: int,
    max_frame_count: int = 300,
    observer: VisualObserver | None = None,
) -> FiniteVideoSummary:
    if isinstance(frame_count, bool) or not isinstance(frame_count, int) or frame_count <= 0:
        raise VisualCaptureError("frame_count must be a positive integer")
    if (
        isinstance(max_frame_count, bool)
        or not isinstance(max_frame_count, int)
        or max_frame_count <= 0
    ):
        raise VisualCaptureError("max_frame_count must be a positive integer")
    if frame_count > max_frame_count:
        raise VisualCaptureError("frame_count exceeds the finite capture limit")

    width = receptor.config.carrier_count
    minima = [math.inf] * width
    maxima = [-math.inf] * width
    totals = [0.0] * width
    zero_count = 0
    light_count = 0
    digest = hashlib.sha256()

    for frame_index in range(frame_count):
        try:
            frame = source.read_frame()
            state = receptor.analyze(frame, frame_index=frame_index)
        except VisualCaptureError as exc:
            raise VisualCaptureError(f"finite video capture failed at frame {frame_index}") from exc
        before = state.digest()
        if observer is not None:
            observer(state)
        if state.digest() != before:
            raise VisualCaptureError("observer changed an immutable visual receptor state")
        digest.update(before.encode("ascii"))
        zero_count += state.contact is VisualReceptorContact.ACTIVE_ZERO
        light_count += state.contact is VisualReceptorContact.ACTIVE_LIGHT
        for index, value in enumerate(state.channel_values):
            minima[index] = min(minima[index], value)
            maxima[index] = max(maxima[index], value)
            totals[index] += value

    return FiniteVideoSummary(
        geometry_id=receptor.config.geometry_id,
        carrier_ids=receptor.config.carrier_ids,
        input_frames=frame_count,
        output_states=frame_count,
        duration_seconds=frame_count / receptor.config.frames_per_second,
        value_min=tuple(minima),
        value_max=tuple(maxima),
        value_mean=tuple(total / frame_count for total in totals),
        active_zero_count=zero_count,
        active_light_count=light_count,
        sequence_digest=digest.hexdigest(),
    )


def visual_public_roles() -> tuple[tuple[str, ...], tuple[str, ...]]:
    return (
        tuple(item.name for item in fields(VisualReceptorState)),
        tuple(item.name for item in fields(FiniteVideoSummary)),
    )
