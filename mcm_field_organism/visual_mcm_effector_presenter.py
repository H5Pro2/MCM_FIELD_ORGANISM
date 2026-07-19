"""Bounded static screen presentation of one visual MCM effector frame."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math
import time

from .visual_mcm_effector_surface import VisualMCMEffectorFrame


MAX_PRESENTATION_DURATION_MS = 30_000
MAX_PRESENTATION_EDGE_PIXELS = 4_096
MAX_CELL_PIXELS = 64
GRAY16_MAX = 65_535


class VisualMCMEffectorPresentationError(ValueError):
    """Raised when a presentation would violate the bounded output contract."""


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
class VisualMCMEffectorPresentationPlan:
    source_frame_digest: str
    rows: int
    columns: int
    cell_pixels: int
    duration_ms: int
    width_pixels: int
    height_pixels: int
    gray16_raster: tuple[tuple[int, ...], ...]
    animated: bool = False
    writes_back: bool = False
    camera_connected: bool = False
    stateful: bool = False
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
            self.columns,
            "columns",
            minimum=1,
            maximum=MAX_PRESENTATION_EDGE_PIXELS,
        )
        cell_pixels = _bounded_integer(
            self.cell_pixels,
            "cell_pixels",
            minimum=1,
            maximum=MAX_CELL_PIXELS,
        )
        duration_ms = _bounded_integer(
            self.duration_ms,
            "duration_ms",
            minimum=1,
            maximum=MAX_PRESENTATION_DURATION_MS,
        )
        width_pixels = _bounded_integer(
            self.width_pixels,
            "width_pixels",
            minimum=1,
            maximum=MAX_PRESENTATION_EDGE_PIXELS,
        )
        height_pixels = _bounded_integer(
            self.height_pixels,
            "height_pixels",
            minimum=1,
            maximum=MAX_PRESENTATION_EDGE_PIXELS,
        )
        if width_pixels != columns * cell_pixels:
            raise VisualMCMEffectorPresentationError(
                "presentation width must follow frame columns and fixed cell size"
            )
        if height_pixels != rows * cell_pixels:
            raise VisualMCMEffectorPresentationError(
                "presentation height must follow frame rows and fixed cell size"
            )
        raster = tuple(tuple(row) for row in self.gray16_raster)
        if len(raster) != rows or any(len(row) != columns for row in raster):
            raise VisualMCMEffectorPresentationError(
                "gray raster must match the declared presentation geometry"
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
                "gray raster values must be 16-bit unsigned integers"
            )
        behavior_flags = (
            self.animated,
            self.writes_back,
            self.camera_connected,
            self.stateful,
            self.random_source,
        )
        if any(not isinstance(value, bool) for value in behavior_flags):
            raise VisualMCMEffectorPresentationError(
                "presentation behavior flags must be boolean"
            )
        if any(behavior_flags):
            raise VisualMCMEffectorPresentationError(
                "presentation cannot animate, write back, connect a camera, store state, or add randomness"
            )
        object.__setattr__(self, "rows", rows)
        object.__setattr__(self, "columns", columns)
        object.__setattr__(self, "cell_pixels", cell_pixels)
        object.__setattr__(self, "duration_ms", duration_ms)
        object.__setattr__(self, "width_pixels", width_pixels)
        object.__setattr__(self, "height_pixels", height_pixels)
        object.__setattr__(self, "gray16_raster", raster)

    def canonical_payload(self) -> dict[str, object]:
        return {
            item.name: (
                [list(row) for row in value]
                if item.name == "gray16_raster"
                else value
            )
            for item in fields(self)
            for value in (getattr(self, item.name),)
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class VisualMCMEffectorPresentationObservation:
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
                "presentation end cannot precede its start"
            )
        if not isinstance(self.completed_by_timeout, bool):
            raise VisualMCMEffectorPresentationError(
                "completed_by_timeout must be boolean"
            )
        object.__setattr__(self, "started_monotonic_ns", start)
        object.__setattr__(self, "ended_monotonic_ns", end)


def prepare_visual_mcm_effector_presentation(
    frame: VisualMCMEffectorFrame,
    *,
    duration_ms: int = 5_000,
    cell_pixels: int = 16,
) -> VisualMCMEffectorPresentationPlan:
    """Create one immutable static screen plan from an effector frame."""

    if not isinstance(frame, VisualMCMEffectorFrame):
        raise VisualMCMEffectorPresentationError(
            "presentation source must be a visual MCM effector frame"
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
    width = frame.columns * cell_size
    height = frame.rows * cell_size
    if width > MAX_PRESENTATION_EDGE_PIXELS or height > MAX_PRESENTATION_EDGE_PIXELS:
        raise VisualMCMEffectorPresentationError(
            "presentation raster exceeds the fixed screen safety boundary"
        )
    return VisualMCMEffectorPresentationPlan(
        source_frame_digest=frame.digest(),
        rows=frame.rows,
        columns=frame.columns,
        cell_pixels=cell_size,
        duration_ms=duration,
        width_pixels=width,
        height_pixels=height,
        gray16_raster=tuple(
            tuple(_gray16(value) for value in row)
            for row in frame.intensities
        ),
    )


def present_visual_mcm_effector_plan(
    plan: VisualMCMEffectorPresentationPlan,
) -> VisualMCMEffectorPresentationObservation:
    """Show one static plan until manual close or its bounded timeout."""

    if not isinstance(plan, VisualMCMEffectorPresentationPlan):
        raise VisualMCMEffectorPresentationError(
            "screen presentation requires a validated presentation plan"
        )
    try:
        import tkinter as tk
    except ImportError as exc:
        raise VisualMCMEffectorPresentationError(
            "tkinter is required for manual screen presentation"
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
    )
    canvas.pack(padx=0, pady=0)
    for row_index, row in enumerate(plan.gray16_raster):
        for column_index, gray16 in enumerate(row):
            color = _tk_gray(gray16)
            x0 = column_index * plan.cell_pixels
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
    return VisualMCMEffectorPresentationObservation(
        plan_digest=plan.digest(),
        started_monotonic_ns=started,
        ended_monotonic_ns=ended,
        completed_by_timeout=completed_by_timeout,
    )


def present_visual_mcm_effector_frame(
    frame: VisualMCMEffectorFrame,
    *,
    duration_ms: int = 5_000,
    cell_pixels: int = 16,
) -> VisualMCMEffectorPresentationObservation:
    """Prepare and manually present one unchanged visual effector frame."""

    return present_visual_mcm_effector_plan(
        prepare_visual_mcm_effector_presentation(
            frame,
            duration_ms=duration_ms,
            cell_pixels=cell_pixels,
        )
    )


def visual_mcm_effector_presentation_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            VisualMCMEffectorPresentationPlan,
            VisualMCMEffectorPresentationObservation,
        )
        for item in fields(cls)
    )
