"""Static two-channel presentation for an independent physical target setup."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math
import time

from .visual_mcm_effector_presenter import (
    GRAY16_MAX,
    MAX_CELL_PIXELS,
    MAX_PRESENTATION_DURATION_MS,
    MAX_PRESENTATION_EDGE_PIXELS,
    VisualMCMEffectorPresentationError,
)
from .visual_mcm_effector_surface import VisualMCMEffectorFrame


MIN_CHANNEL_GAP_PIXELS = 16
MAX_CHANNEL_GAP_PIXELS = 512


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _bounded_integer(
    value: object,
    role: str,
    *,
    minimum: int,
    maximum: int,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise VisualMCMEffectorPresentationError(f"{role} must be an integer")
    if value < minimum or value > maximum:
        raise VisualMCMEffectorPresentationError(
            f"{role} must stay within {minimum}..{maximum}"
        )
    return value


def _gray16(intensity: object) -> int:
    try:
        value = float(intensity)
    except (TypeError, ValueError) as exc:
        raise VisualMCMEffectorPresentationError(
            "effector intensity must be numeric"
        ) from exc
    if not math.isfinite(value) or value < 0.25 or value > 0.75:
        raise VisualMCMEffectorPresentationError(
            "effector intensity must stay within 0.25..0.75"
        )
    return math.floor(value * GRAY16_MAX + 0.5)


def _tk_gray(gray16: int) -> str:
    component = f"{gray16:04x}"
    return f"#{component}{component}{component}"


@dataclass(frozen=True, slots=True)
class IndependentVisualTargetPlan:
    """Immutable output plan for two optically separated target channels."""

    source_frame_digest: str
    rows: int
    columns_per_channel: int
    cell_pixels: int
    channel_gap_pixels: int
    duration_ms: int
    width_pixels: int
    height_pixels: int
    left_gray16_raster: tuple[tuple[int, ...], ...]
    right_gray16_raster: tuple[tuple[int, ...], ...]
    camera_connected: bool = False
    writes_back: bool = False
    stateful: bool = False
    adaptive: bool = False
    random_source: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.source_frame_digest, str) or not self.source_frame_digest:
            raise VisualMCMEffectorPresentationError(
                "source_frame_digest must be a non-empty technical identifier"
            )
        rows = _bounded_integer(
            self.rows,
            "rows",
            minimum=1,
            maximum=MAX_PRESENTATION_EDGE_PIXELS,
        )
        columns = _bounded_integer(
            self.columns_per_channel,
            "columns_per_channel",
            minimum=1,
            maximum=MAX_PRESENTATION_EDGE_PIXELS,
        )
        cell_pixels = _bounded_integer(
            self.cell_pixels,
            "cell_pixels",
            minimum=1,
            maximum=MAX_CELL_PIXELS,
        )
        gap = _bounded_integer(
            self.channel_gap_pixels,
            "channel_gap_pixels",
            minimum=MIN_CHANNEL_GAP_PIXELS,
            maximum=MAX_CHANNEL_GAP_PIXELS,
        )
        duration = _bounded_integer(
            self.duration_ms,
            "duration_ms",
            minimum=1,
            maximum=MAX_PRESENTATION_DURATION_MS,
        )
        width = _bounded_integer(
            self.width_pixels,
            "width_pixels",
            minimum=1,
            maximum=MAX_PRESENTATION_EDGE_PIXELS,
        )
        height = _bounded_integer(
            self.height_pixels,
            "height_pixels",
            minimum=1,
            maximum=MAX_PRESENTATION_EDGE_PIXELS,
        )
        if width != 2 * columns * cell_pixels + gap:
            raise VisualMCMEffectorPresentationError(
                "target width must contain two equal channels and one fixed gap"
            )
        if height != rows * cell_pixels:
            raise VisualMCMEffectorPresentationError(
                "target height must follow rows and fixed cell size"
            )
        left = tuple(tuple(row) for row in self.left_gray16_raster)
        right = tuple(tuple(row) for row in self.right_gray16_raster)
        for role, raster in (("left", left), ("right", right)):
            if len(raster) != rows or any(len(row) != columns for row in raster):
                raise VisualMCMEffectorPresentationError(
                    f"{role} target raster must match the channel geometry"
                )
            if any(
                isinstance(value, bool)
                or not isinstance(value, int)
                or value < 0
                or value > GRAY16_MAX
                for row in raster
                for value in row
            ):
                raise VisualMCMEffectorPresentationError(
                    f"{role} target raster must use 16-bit gray values"
                )
        flags = (
            self.camera_connected,
            self.writes_back,
            self.stateful,
            self.adaptive,
            self.random_source,
        )
        if any(not isinstance(value, bool) for value in flags):
            raise VisualMCMEffectorPresentationError(
                "target presentation behavior flags must be boolean"
            )
        if any(flags):
            raise VisualMCMEffectorPresentationError(
                "target presentation cannot connect a camera, write back, store state, adapt, or add randomness"
            )
        object.__setattr__(self, "rows", rows)
        object.__setattr__(self, "columns_per_channel", columns)
        object.__setattr__(self, "cell_pixels", cell_pixels)
        object.__setattr__(self, "channel_gap_pixels", gap)
        object.__setattr__(self, "duration_ms", duration)
        object.__setattr__(self, "width_pixels", width)
        object.__setattr__(self, "height_pixels", height)
        object.__setattr__(self, "left_gray16_raster", left)
        object.__setattr__(self, "right_gray16_raster", right)

    def canonical_payload(self) -> dict[str, object]:
        return {
            item.name: (
                [list(row) for row in value]
                if item.name in {"left_gray16_raster", "right_gray16_raster"}
                else value
            )
            for item in fields(self)
            for value in (getattr(self, item.name),)
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class IndependentVisualTargetObservation:
    plan_digest: str
    started_monotonic_ns: int
    ended_monotonic_ns: int
    completed_by_timeout: bool

    def __post_init__(self) -> None:
        if not isinstance(self.plan_digest, str) or not self.plan_digest:
            raise VisualMCMEffectorPresentationError(
                "plan_digest must be a non-empty technical identifier"
            )
        start = _bounded_integer(
            self.started_monotonic_ns,
            "started_monotonic_ns",
            minimum=0,
            maximum=2**63 - 1,
        )
        end = _bounded_integer(
            self.ended_monotonic_ns,
            "ended_monotonic_ns",
            minimum=0,
            maximum=2**63 - 1,
        )
        if end < start:
            raise VisualMCMEffectorPresentationError(
                "target presentation end cannot precede its start"
            )
        if not isinstance(self.completed_by_timeout, bool):
            raise VisualMCMEffectorPresentationError(
                "completed_by_timeout must be boolean"
            )
        object.__setattr__(self, "started_monotonic_ns", start)
        object.__setattr__(self, "ended_monotonic_ns", end)


def prepare_independent_visual_target_plan(
    frame: VisualMCMEffectorFrame,
    *,
    duration_ms: int = 5_000,
    cell_pixels: int = 16,
    channel_gap_pixels: int = 64,
) -> IndependentVisualTargetPlan:
    """Separate every affine pair into two geometry-preserving light channels."""

    if not isinstance(frame, VisualMCMEffectorFrame):
        raise VisualMCMEffectorPresentationError(
            "independent target source must be a visual MCM effector frame"
        )
    if frame.columns % 2 != 0:
        raise VisualMCMEffectorPresentationError(
            "independent target source requires affine column pairs"
        )
    duration = _bounded_integer(
        duration_ms,
        "duration_ms",
        minimum=1,
        maximum=MAX_PRESENTATION_DURATION_MS,
    )
    cell_size = _bounded_integer(
        cell_pixels,
        "cell_pixels",
        minimum=1,
        maximum=MAX_CELL_PIXELS,
    )
    gap = _bounded_integer(
        channel_gap_pixels,
        "channel_gap_pixels",
        minimum=MIN_CHANNEL_GAP_PIXELS,
        maximum=MAX_CHANNEL_GAP_PIXELS,
    )
    columns = frame.columns // 2
    width = 2 * columns * cell_size + gap
    height = frame.rows * cell_size
    if width > MAX_PRESENTATION_EDGE_PIXELS or height > MAX_PRESENTATION_EDGE_PIXELS:
        raise VisualMCMEffectorPresentationError(
            "independent target raster exceeds the fixed screen safety boundary"
        )
    return IndependentVisualTargetPlan(
        source_frame_digest=frame.digest(),
        rows=frame.rows,
        columns_per_channel=columns,
        cell_pixels=cell_size,
        channel_gap_pixels=gap,
        duration_ms=duration,
        width_pixels=width,
        height_pixels=height,
        left_gray16_raster=tuple(
            tuple(_gray16(row[column]) for column in range(0, frame.columns, 2))
            for row in frame.intensities
        ),
        right_gray16_raster=tuple(
            tuple(_gray16(row[column]) for column in range(1, frame.columns, 2))
            for row in frame.intensities
        ),
    )


def present_independent_visual_target_plan(
    plan: IndependentVisualTargetPlan,
) -> IndependentVisualTargetObservation:
    """Present two static channels; physical routing remains outside software."""

    if not isinstance(plan, IndependentVisualTargetPlan):
        raise VisualMCMEffectorPresentationError(
            "independent target presentation requires a validated plan"
        )
    try:
        import tkinter as tk
    except ImportError as exc:
        raise VisualMCMEffectorPresentationError(
            "tkinter is required for manual target presentation"
        ) from exc

    root = tk.Tk()
    root.title("")
    root.resizable(False, False)
    canvas = tk.Canvas(
        root,
        width=plan.width_pixels,
        height=plan.height_pixels,
        borderwidth=0,
        highlightthickness=0,
        background="#000000",
    )
    canvas.pack(padx=0, pady=0)
    channel_width = plan.columns_per_channel * plan.cell_pixels
    for raster, x_offset in (
        (plan.left_gray16_raster, 0),
        (
            plan.right_gray16_raster,
            channel_width + plan.channel_gap_pixels,
        ),
    ):
        for row_index, row in enumerate(raster):
            for column_index, gray16 in enumerate(row):
                color = _tk_gray(gray16)
                x0 = x_offset + column_index * plan.cell_pixels
                y0 = row_index * plan.cell_pixels
                canvas.create_rectangle(
                    x0,
                    y0,
                    x0 + plan.cell_pixels,
                    y0 + plan.cell_pixels,
                    fill=color,
                    outline=color,
                    width=0,
                )
    completed_by_timeout = False

    def close_after_timeout() -> None:
        nonlocal completed_by_timeout
        completed_by_timeout = True
        root.destroy()

    root.bind("<Escape>", lambda _event: root.destroy())
    root.after(plan.duration_ms, close_after_timeout)
    started = time.monotonic_ns()
    root.mainloop()
    ended = time.monotonic_ns()
    return IndependentVisualTargetObservation(
        plan_digest=plan.digest(),
        started_monotonic_ns=started,
        ended_monotonic_ns=ended,
        completed_by_timeout=completed_by_timeout,
    )


def independent_visual_target_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            IndependentVisualTargetPlan,
            IndependentVisualTargetObservation,
        )
        for item in fields(cls)
    )
