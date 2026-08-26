"""Bounded temporal contract for visual MCM effector frames."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .visual_mcm_effector_surface import VisualMCMEffectorFrame


MAX_EFFECTOR_SEQUENCE_FRAMES = 10
MIN_EFFECTOR_FRAME_DURATION_MS = 100
MAX_EFFECTOR_SEQUENCE_DURATION_MS = 30_000


class VisualMCMEffectorSequenceError(ValueError):
    """Raised when a temporal effector sequence violates its fixed contract."""


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class VisualMCMEffectorSequencePlan:
    frame_digests: tuple[str, ...]
    source_field_id: str
    source_geometry_id: str
    source_ticks: tuple[int, ...]
    source_windows: tuple[tuple[int, int], ...]
    frame_duration_ms: int
    total_duration_ms: int
    writes_back: bool = False
    camera_connected: bool = False
    adaptive_timing: bool = False
    content_selection: bool = False
    stateful: bool = False

    def __post_init__(self) -> None:
        frame_digests = tuple(self.frame_digests)
        source_ticks = tuple(self.source_ticks)
        source_windows = tuple(tuple(window) for window in self.source_windows)
        count = len(frame_digests)
        if count < 1 or count > MAX_EFFECTOR_SEQUENCE_FRAMES:
            raise VisualMCMEffectorSequenceError(
                f"sequence requires 1..{MAX_EFFECTOR_SEQUENCE_FRAMES} frames"
            )
        if any(not isinstance(value, str) or not value for value in frame_digests):
            raise VisualMCMEffectorSequenceError(
                "frame digests must be non-empty technical identifiers"
            )
        if not isinstance(self.source_field_id, str) or not self.source_field_id:
            raise VisualMCMEffectorSequenceError("source_field_id must be non-empty")
        if not isinstance(self.source_geometry_id, str) or not self.source_geometry_id:
            raise VisualMCMEffectorSequenceError("source_geometry_id must be non-empty")
        if len(source_ticks) != count or len(source_windows) != count:
            raise VisualMCMEffectorSequenceError(
                "source time roles must match the frame count"
            )
        if any(
            isinstance(tick, bool) or not isinstance(tick, int) or tick < 0
            for tick in source_ticks
        ):
            raise VisualMCMEffectorSequenceError("source ticks must be non-negative integers")
        if any(later <= earlier for earlier, later in zip(source_ticks, source_ticks[1:])):
            raise VisualMCMEffectorSequenceError("source ticks must increase strictly")
        if any(
            len(window) != 2
            or any(isinstance(value, bool) or not isinstance(value, int) for value in window)
            or window[0] < 0
            or window[0] >= window[1]
            for window in source_windows
        ):
            raise VisualMCMEffectorSequenceError("source windows must have positive duration")
        if any(
            later[0] < earlier[1]
            for earlier, later in zip(source_windows, source_windows[1:])
        ):
            raise VisualMCMEffectorSequenceError("source windows must not overlap")
        if (
            isinstance(self.frame_duration_ms, bool)
            or not isinstance(self.frame_duration_ms, int)
            or self.frame_duration_ms < MIN_EFFECTOR_FRAME_DURATION_MS
        ):
            raise VisualMCMEffectorSequenceError(
                f"frame_duration_ms must be at least {MIN_EFFECTOR_FRAME_DURATION_MS}"
            )
        expected_total = count * self.frame_duration_ms
        if self.total_duration_ms != expected_total:
            raise VisualMCMEffectorSequenceError(
                "total duration must equal frame count times fixed frame duration"
            )
        if expected_total > MAX_EFFECTOR_SEQUENCE_DURATION_MS:
            raise VisualMCMEffectorSequenceError(
                f"sequence duration exceeds {MAX_EFFECTOR_SEQUENCE_DURATION_MS} ms"
            )
        behavior_flags = (
            self.writes_back,
            self.camera_connected,
            self.adaptive_timing,
            self.content_selection,
            self.stateful,
        )
        if any(not isinstance(value, bool) for value in behavior_flags):
            raise VisualMCMEffectorSequenceError("sequence behavior flags must be boolean")
        if any(behavior_flags):
            raise VisualMCMEffectorSequenceError(
                "sequence cannot write back, connect a camera, adapt timing, select content, or store state"
            )
        object.__setattr__(self, "frame_digests", frame_digests)
        object.__setattr__(self, "source_ticks", source_ticks)
        object.__setattr__(self, "source_windows", source_windows)

    def canonical_payload(self) -> dict[str, object]:
        return {
            item.name: (
                [list(window) for window in value]
                if item.name == "source_windows"
                else list(value)
                if item.name in {"frame_digests", "source_ticks"}
                else value
            )
            for item in fields(self)
            for value in (getattr(self, item.name),)
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def prepare_visual_mcm_effector_sequence(
    frames: tuple[VisualMCMEffectorFrame, ...],
    *,
    frame_duration_ms: int,
) -> VisualMCMEffectorSequencePlan:
    """Prepare a fixed-rate sequence without inspecting frame contents."""

    frames = tuple(frames)
    if not frames or any(not isinstance(frame, VisualMCMEffectorFrame) for frame in frames):
        raise VisualMCMEffectorSequenceError(
            "sequence source must contain visual MCM effector frames"
        )
    if len(frames) > MAX_EFFECTOR_SEQUENCE_FRAMES:
        raise VisualMCMEffectorSequenceError(
            f"sequence requires 1..{MAX_EFFECTOR_SEQUENCE_FRAMES} frames"
        )
    field_ids = {frame.source_field_id for frame in frames}
    geometry_ids = {frame.source_geometry_id for frame in frames}
    if len(field_ids) != 1 or len(geometry_ids) != 1:
        raise VisualMCMEffectorSequenceError(
            "all frames must belong to one field and geometry"
        )
    return VisualMCMEffectorSequencePlan(
        frame_digests=tuple(frame.digest() for frame in frames),
        source_field_id=frames[0].source_field_id,
        source_geometry_id=frames[0].source_geometry_id,
        source_ticks=tuple(frame.source_tick for frame in frames),
        source_windows=tuple(
            (frame.source_window_start_tick, frame.source_window_end_tick)
            for frame in frames
        ),
        frame_duration_ms=frame_duration_ms,
        total_duration_ms=len(frames) * frame_duration_ms,
    )


def visual_mcm_effector_sequence_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(VisualMCMEffectorSequencePlan))
