"""Bounded fixed-time presentation of visual MCM effector sequences."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import time
from typing import Protocol

from .visual_mcm_effector_presenter import (
    GRAY16_MAX,
    MAX_CELL_PIXELS,
    MAX_PRESENTATION_DURATION_MS,
    MAX_PRESENTATION_EDGE_PIXELS,
    VisualMCMEffectorPresentationError,
    prepare_visual_mcm_effector_presentation,
)
from .visual_mcm_effector_sequence import VisualMCMEffectorSequencePlan
from .visual_mcm_effector_surface import VisualMCMEffectorFrame


MIN_NEUTRAL_OUTPUT_DURATION_MS = 100
NEUTRAL_GRAY16 = (GRAY16_MAX + 1) // 2


class VisualMCMEffectorSequencePresentationError(ValueError):
    """Raised when sequence presentation violates its bounded contract."""


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _bounded_integer(value: object, role: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise VisualMCMEffectorSequencePresentationError(f"{role} must be an integer")
    if value < minimum or value > maximum:
        raise VisualMCMEffectorSequencePresentationError(
            f"{role} must stay within {minimum}..{maximum}"
        )
    return value


@dataclass(frozen=True, slots=True)
class VisualMCMEffectorSequencePresentationPlan:
    source_sequence_digest: str
    source_frame_digests: tuple[str, ...]
    rows: int
    columns: int
    cell_pixels: int
    frame_duration_ms: int
    neutral_duration_ms: int
    total_runtime_ms: int
    width_pixels: int
    height_pixels: int
    gray16_rasters: tuple[tuple[tuple[int, ...], ...], ...]
    neutral_gray16_raster: tuple[tuple[int, ...], ...]
    writes_back: bool = False
    camera_connected: bool = False
    adaptive_timing: bool = False
    content_selection: bool = False
    stateful: bool = False
    random_source: bool = False

    def __post_init__(self) -> None:
        digests = tuple(self.source_frame_digests)
        rasters = tuple(tuple(tuple(row) for row in raster) for raster in self.gray16_rasters)
        neutral = tuple(tuple(row) for row in self.neutral_gray16_raster)
        if not isinstance(self.source_sequence_digest, str) or not self.source_sequence_digest:
            raise VisualMCMEffectorSequencePresentationError(
                "source_sequence_digest must be a non-empty technical identifier"
            )
        if not digests or any(not isinstance(value, str) or not value for value in digests):
            raise VisualMCMEffectorSequencePresentationError(
                "source_frame_digests must be non-empty technical identifiers"
            )
        rows = _bounded_integer(self.rows, "rows", 1, MAX_PRESENTATION_EDGE_PIXELS)
        columns = _bounded_integer(
            self.columns, "columns", 1, MAX_PRESENTATION_EDGE_PIXELS
        )
        cell_pixels = _bounded_integer(self.cell_pixels, "cell_pixels", 1, MAX_CELL_PIXELS)
        frame_duration = _bounded_integer(
            self.frame_duration_ms,
            "frame_duration_ms",
            1,
            MAX_PRESENTATION_DURATION_MS,
        )
        neutral_duration = _bounded_integer(
            self.neutral_duration_ms,
            "neutral_duration_ms",
            MIN_NEUTRAL_OUTPUT_DURATION_MS,
            MAX_PRESENTATION_DURATION_MS,
        )
        expected_runtime = len(digests) * frame_duration + neutral_duration
        if self.total_runtime_ms != expected_runtime or expected_runtime > MAX_PRESENTATION_DURATION_MS:
            raise VisualMCMEffectorSequencePresentationError(
                "total runtime must include every fixed frame and neutral output within 30000 ms"
            )
        if self.width_pixels != columns * cell_pixels or self.height_pixels != rows * cell_pixels:
            raise VisualMCMEffectorSequencePresentationError(
                "presentation dimensions must follow geometry and fixed cell size"
            )
        if len(rasters) != len(digests):
            raise VisualMCMEffectorSequencePresentationError(
                "one raster is required for every source frame"
            )
        for raster in (*rasters, neutral):
            if len(raster) != rows or any(len(row) != columns for row in raster):
                raise VisualMCMEffectorSequencePresentationError(
                    "every raster must match the declared geometry"
                )
            if any(
                isinstance(value, bool)
                or not isinstance(value, int)
                or value < 0
                or value > GRAY16_MAX
                for row in raster
                for value in row
            ):
                raise VisualMCMEffectorSequencePresentationError(
                    "raster values must be 16-bit unsigned integers"
                )
        if any(value != NEUTRAL_GRAY16 for row in neutral for value in row):
            raise VisualMCMEffectorSequencePresentationError(
                "neutral output must be uniform middle gray"
            )
        behavior_flags = (
            self.writes_back,
            self.camera_connected,
            self.adaptive_timing,
            self.content_selection,
            self.stateful,
            self.random_source,
        )
        if any(not isinstance(value, bool) for value in behavior_flags) or any(behavior_flags):
            raise VisualMCMEffectorSequencePresentationError(
                "presentation cannot write back, connect a camera, adapt timing, select content, store state, or add randomness"
            )
        object.__setattr__(self, "source_frame_digests", digests)
        object.__setattr__(self, "gray16_rasters", rasters)
        object.__setattr__(self, "neutral_gray16_raster", neutral)

    def canonical_payload(self) -> dict[str, object]:
        return {
            item.name: getattr(self, item.name)
            for item in fields(self)
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class VisualMCMEffectorSequencePresentationObservation:
    plan_digest: str
    started_monotonic_ns: int
    ended_monotonic_ns: int
    frames_presented: int
    termination: str
    neutral_output_applied: bool

    def __post_init__(self) -> None:
        if not isinstance(self.plan_digest, str) or not self.plan_digest:
            raise VisualMCMEffectorSequencePresentationError("plan_digest must be non-empty")
        start = _bounded_integer(self.started_monotonic_ns, "started_monotonic_ns", 0, 2**63 - 1)
        end = _bounded_integer(self.ended_monotonic_ns, "ended_monotonic_ns", 0, 2**63 - 1)
        if end < start:
            raise VisualMCMEffectorSequencePresentationError(
                "presentation end cannot precede its start"
            )
        frames_presented = _bounded_integer(self.frames_presented, "frames_presented", 0, 10)
        if self.termination not in {"completed", "manual_stop"}:
            raise VisualMCMEffectorSequencePresentationError(
                "termination must describe completion or manual stop"
            )
        if not isinstance(self.neutral_output_applied, bool) or not self.neutral_output_applied:
            raise VisualMCMEffectorSequencePresentationError(
                "a successful observation requires neutral output"
            )
        object.__setattr__(self, "started_monotonic_ns", start)
        object.__setattr__(self, "ended_monotonic_ns", end)
        object.__setattr__(self, "frames_presented", frames_presented)


class _SequencePresentationBackend(Protocol):
    def render(self, raster: tuple[tuple[int, ...], ...], cell_pixels: int) -> None: ...
    def wait(self, duration_ms: int) -> bool: ...
    def close(self) -> None: ...


class _TkSequencePresentationBackend:
    def __init__(self, width_pixels: int, height_pixels: int) -> None:
        try:
            import tkinter as tk
        except ImportError as exc:
            raise VisualMCMEffectorSequencePresentationError(
                "tkinter is required for manual screen presentation"
            ) from exc
        self._tk = tk
        self._root = tk.Tk()
        self._root.title("")
        self._root.resizable(False, False)
        self._canvas = tk.Canvas(
            self._root,
            width=width_pixels,
            height=height_pixels,
            borderwidth=0,
            highlightthickness=0,
        )
        self._canvas.pack(padx=0, pady=0)
        self._manual_stop = False
        self._root.bind("<Escape>", self._stop)
        self._root.protocol("WM_DELETE_WINDOW", self._stop)

    def _stop(self, _event: object = None) -> None:
        self._manual_stop = True
        self._root.quit()

    def render(self, raster: tuple[tuple[int, ...], ...], cell_pixels: int) -> None:
        self._canvas.delete("all")
        for row_index, row in enumerate(raster):
            for column_index, gray16 in enumerate(row):
                component = f"{gray16:04x}"
                color = f"#{component}{component}{component}"
                x0 = column_index * cell_pixels
                y0 = row_index * cell_pixels
                self._canvas.create_rectangle(
                    x0,
                    y0,
                    x0 + cell_pixels,
                    y0 + cell_pixels,
                    fill=color,
                    outline=color,
                    width=0,
                )
        self._root.update_idletasks()

    def wait(self, duration_ms: int) -> bool:
        if self._manual_stop:
            return True
        timer = self._root.after(duration_ms, self._root.quit)
        self._root.mainloop()
        try:
            self._root.after_cancel(timer)
        except self._tk.TclError:
            pass
        return self._manual_stop

    def close(self) -> None:
        try:
            self._root.destroy()
        except self._tk.TclError:
            pass


def prepare_visual_mcm_effector_sequence_presentation(
    sequence: VisualMCMEffectorSequencePlan,
    frames: tuple[VisualMCMEffectorFrame, ...],
    *,
    cell_pixels: int = 16,
    neutral_duration_ms: int = MIN_NEUTRAL_OUTPUT_DURATION_MS,
) -> VisualMCMEffectorSequencePresentationPlan:
    """Bind a validated sequence to unchanged deterministic screen rasters."""

    if not isinstance(sequence, VisualMCMEffectorSequencePlan):
        raise VisualMCMEffectorSequencePresentationError(
            "sequence presentation requires a validated sequence plan"
        )
    frames = tuple(frames)
    if len(frames) != len(sequence.frame_digests) or any(
        not isinstance(frame, VisualMCMEffectorFrame) for frame in frames
    ):
        raise VisualMCMEffectorSequencePresentationError(
            "source frames must match the sequence frame count"
        )
    if tuple(frame.digest() for frame in frames) != sequence.frame_digests:
        raise VisualMCMEffectorSequencePresentationError(
            "source frame order and digests must match the sequence"
        )
    neutral_duration = _bounded_integer(
        neutral_duration_ms,
        "neutral_duration_ms",
        MIN_NEUTRAL_OUTPUT_DURATION_MS,
        MAX_PRESENTATION_DURATION_MS,
    )
    total_runtime = sequence.total_duration_ms + neutral_duration
    if total_runtime > MAX_PRESENTATION_DURATION_MS:
        raise VisualMCMEffectorSequencePresentationError(
            "sequence plus neutral output exceeds the hard runtime boundary"
        )
    try:
        frame_plans = tuple(
            prepare_visual_mcm_effector_presentation(
                frame,
                duration_ms=sequence.frame_duration_ms,
                cell_pixels=cell_pixels,
            )
            for frame in frames
        )
    except VisualMCMEffectorPresentationError as exc:
        raise VisualMCMEffectorSequencePresentationError(str(exc)) from exc
    first = frame_plans[0]
    neutral = tuple(
        tuple(NEUTRAL_GRAY16 for _ in range(first.columns))
        for _ in range(first.rows)
    )
    return VisualMCMEffectorSequencePresentationPlan(
        source_sequence_digest=sequence.digest(),
        source_frame_digests=sequence.frame_digests,
        rows=first.rows,
        columns=first.columns,
        cell_pixels=first.cell_pixels,
        frame_duration_ms=sequence.frame_duration_ms,
        neutral_duration_ms=neutral_duration,
        total_runtime_ms=total_runtime,
        width_pixels=first.width_pixels,
        height_pixels=first.height_pixels,
        gray16_rasters=tuple(plan.gray16_raster for plan in frame_plans),
        neutral_gray16_raster=neutral,
    )


def present_visual_mcm_effector_sequence_plan(
    plan: VisualMCMEffectorSequencePresentationPlan,
    *,
    _backend: _SequencePresentationBackend | None = None,
) -> VisualMCMEffectorSequencePresentationObservation:
    """Present fixed-rate frames and always attempt bounded neutral output."""

    if not isinstance(plan, VisualMCMEffectorSequencePresentationPlan):
        raise VisualMCMEffectorSequencePresentationError(
            "screen presentation requires a validated sequence presentation plan"
        )
    backend = _backend or _TkSequencePresentationBackend(
        plan.width_pixels,
        plan.height_pixels,
    )
    started = time.monotonic_ns()
    frames_presented = 0
    manual_stop = False
    neutral_applied = False
    try:
        for raster in plan.gray16_rasters:
            backend.render(raster, plan.cell_pixels)
            frames_presented += 1
            if backend.wait(plan.frame_duration_ms):
                manual_stop = True
                break
        backend.render(plan.neutral_gray16_raster, plan.cell_pixels)
        neutral_applied = True
        backend.wait(plan.neutral_duration_ms)
    except BaseException:
        if not neutral_applied:
            try:
                backend.render(plan.neutral_gray16_raster, plan.cell_pixels)
                neutral_applied = True
                backend.wait(plan.neutral_duration_ms)
            except BaseException:
                pass
        raise
    finally:
        backend.close()
    ended = time.monotonic_ns()
    return VisualMCMEffectorSequencePresentationObservation(
        plan_digest=plan.digest(),
        started_monotonic_ns=started,
        ended_monotonic_ns=ended,
        frames_presented=frames_presented,
        termination="manual_stop" if manual_stop else "completed",
        neutral_output_applied=neutral_applied,
    )


def visual_mcm_effector_sequence_presentation_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            VisualMCMEffectorSequencePresentationPlan,
            VisualMCMEffectorSequencePresentationObservation,
        )
        for item in fields(cls)
    )
