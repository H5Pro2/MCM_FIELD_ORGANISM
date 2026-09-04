"""Private missing-aware pose/form projection for a bound visual mask."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math

import numpy as np


SCHEMA = "s2lx.private-masked-pose-form-projection.v1"
GRID_ROWS = 8
GRID_COLUMNS = 12
CHANNELS = 3
FULL_DIMENSION = 288
OBSERVED_DIMENSION = 96
FORM_GRID_SIZE = 12


class S2LXProjectionError(ValueError):
    """The masked receptor evidence cannot support a form projection."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2LXProjectionError(message)


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _coordinate(position: int) -> tuple[int, int, int]:
    return position // (GRID_COLUMNS * CHANNELS), (position % (GRID_COLUMNS * CHANNELS)) // CHANNELS, position % CHANNELS


@dataclass(frozen=True, slots=True)
class MaskedVisualViewV1:
    mask_digest: str
    source_values_digest: str
    observed_positions: tuple[int, ...]
    observed_values: tuple[float, ...]
    observed_values_digest: str

    def __post_init__(self) -> None:
        _require(type(self.mask_digest) is str and len(self.mask_digest) == 64, "mask digest differs")
        _require(type(self.source_values_digest) is str and len(self.source_values_digest) == 64, "source digest differs")
        _require(type(self.observed_positions) is tuple and len(self.observed_positions) == OBSERVED_DIMENSION, "observed positions differ")
        _require(len(set(self.observed_positions)) == OBSERVED_DIMENSION, "observed positions repeat")
        _require(all(type(item) is int and 0 <= item < FULL_DIMENSION for item in self.observed_positions), "observed position domain differs")
        _require(type(self.observed_values) is tuple and len(self.observed_values) == OBSERVED_DIMENSION, "observed values differ")
        _require(all(type(item) is float and math.isfinite(item) and 0.0 <= item <= 1.0 for item in self.observed_values), "observed value domain differs")
        _require(self.observed_values_digest == _digest(list(self.observed_values)), "observed values digest differs")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema": "s2lx.masked-visual-view.v1",
            "mask_digest": self.mask_digest,
            "source_values_digest": self.source_values_digest,
            "observed_positions": list(self.observed_positions),
            "observed_values": list(self.observed_values),
            "observed_values_digest": self.observed_values_digest,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class MaskedPoseV1:
    observed_cell_count: int
    support_cell_count: int
    background_channels: tuple[float, float, float]
    total_observed_activation: float
    centroid_x: float
    centroid_y: float
    extent_width: float
    extent_height: float

    def __post_init__(self) -> None:
        values = (*self.background_channels, self.total_observed_activation, self.centroid_x, self.centroid_y, self.extent_width, self.extent_height)
        _require(all(type(item) is float and math.isfinite(item) for item in values), "masked pose value differs")
        _require(type(self.observed_cell_count) is int and 0 < self.observed_cell_count <= 96, "observed cell count differs")
        _require(type(self.support_cell_count) is int and 0 < self.support_cell_count <= self.observed_cell_count, "support cell count differs")
        _require(self.total_observed_activation > 0.0, "observed activation differs")
        _require(0.0 <= self.centroid_x <= 1.0 and 0.0 <= self.centroid_y <= 1.0, "masked centroid differs")
        _require(0.0 < self.extent_width <= 1.0 and 0.0 < self.extent_height <= 1.0, "masked extent differs")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema": "s2lx.masked-pose.v1",
            "observed_cell_count": self.observed_cell_count,
            "support_cell_count": self.support_cell_count,
            "background_channels": list(self.background_channels),
            "total_observed_activation": self.total_observed_activation,
            "centroid_x": self.centroid_x,
            "centroid_y": self.centroid_y,
            "extent_width": self.extent_width,
            "extent_height": self.extent_height,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class MaskedFormDescriptorV1:
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        _require(type(self.values) is tuple and len(self.values) == FORM_GRID_SIZE * FORM_GRID_SIZE, "masked form dimension differs")
        _require(all(type(item) is float and math.isfinite(item) and item >= 0.0 for item in self.values), "masked form value differs")
        _require(abs(math.fsum(self.values) - 1.0) <= 1e-12, "masked form mass differs")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema": "s2lx.masked-form-descriptor.v1",
            "grid_size": FORM_GRID_SIZE,
            "normalization": "OBSERVED_UNIT_TOTAL_MASS",
            "missing_values": "NOT_PRESENT_NOT_IMPUTED",
            "values": list(self.values),
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class MaskedPoseFormProjectionV1:
    masked_view_digest: str
    pose: MaskedPoseV1
    form_descriptor: MaskedFormDescriptorV1

    def __post_init__(self) -> None:
        _require(type(self.masked_view_digest) is str and len(self.masked_view_digest) == 64, "masked view digest differs")
        _require(type(self.pose) is MaskedPoseV1 and type(self.form_descriptor) is MaskedFormDescriptorV1, "masked projection role differs")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema": SCHEMA,
            "masked_view_digest": self.masked_view_digest,
            "pose": self.pose.canonical_payload(),
            "form_descriptor": self.form_descriptor.canonical_payload(),
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def bind_masked_visual_view(
    full_values: tuple[float, ...],
    observed_positions: tuple[int, ...],
    mask_digest: str,
) -> MaskedVisualViewV1:
    _require(type(full_values) is tuple and len(full_values) == FULL_DIMENSION, "full visual values differ")
    _require(all(type(item) is float and math.isfinite(item) and 0.0 <= item <= 1.0 for item in full_values), "full visual value domain differs")
    _require(type(observed_positions) is tuple and len(observed_positions) == OBSERVED_DIMENSION, "mask positions differ")
    _require(len(set(observed_positions)) == OBSERVED_DIMENSION, "mask positions repeat")
    _require(all(type(item) is int and 0 <= item < FULL_DIMENSION for item in observed_positions), "mask position domain differs")
    observed = tuple(full_values[position] for position in observed_positions)
    return MaskedVisualViewV1(
        mask_digest=mask_digest,
        source_values_digest=_digest(list(full_values)),
        observed_positions=observed_positions,
        observed_values=observed,
        observed_values_digest=_digest(list(observed)),
    )


def _bilinear_descriptor(activation_by_cell: dict[tuple[int, int], float]) -> tuple[float, ...]:
    cells = tuple(sorted(activation_by_cell))
    rows = tuple(item[0] for item in cells)
    columns = tuple(item[1] for item in cells)
    left, right = min(columns), max(columns)
    top, bottom = min(rows), max(rows)
    centre_x = (left + right) / 2.0
    centre_y = (top + bottom) / 2.0
    isotropic_span = float(max(right - left + 1, bottom - top + 1))
    canvas = np.zeros((FORM_GRID_SIZE, FORM_GRID_SIZE), dtype=np.float64)
    for row, column in cells:
        canvas_x = ((column - centre_x) / isotropic_span + 0.5) * (FORM_GRID_SIZE - 1)
        canvas_y = ((row - centre_y) / isotropic_span + 0.5) * (FORM_GRID_SIZE - 1)
        x0, y0 = int(math.floor(canvas_x)), int(math.floor(canvas_y))
        x1, y1 = min(x0 + 1, FORM_GRID_SIZE - 1), min(y0 + 1, FORM_GRID_SIZE - 1)
        fx, fy = canvas_x - x0, canvas_y - y0
        value = activation_by_cell[(row, column)]
        canvas[y0, x0] += value * (1.0 - fx) * (1.0 - fy)
        canvas[y0, x1] += value * fx * (1.0 - fy)
        canvas[y1, x0] += value * (1.0 - fx) * fy
        canvas[y1, x1] += value * fx * fy
    total = float(canvas.sum(dtype=np.float64))
    _require(math.isfinite(total) and total > 0.0, "masked form mass differs")
    return tuple(float(item) for item in (canvas / total).reshape(-1))


def project_masked_pose_form(view: MaskedVisualViewV1) -> MaskedPoseFormProjectionV1:
    _require(type(view) is MaskedVisualViewV1, "masked visual view role differs")
    border_by_channel: dict[int, list[float]] = {channel: [] for channel in range(CHANNELS)}
    values_by_cell: dict[tuple[int, int], list[tuple[int, float]]] = {}
    for position, value in zip(view.observed_positions, view.observed_values, strict=True):
        row, column, channel = _coordinate(position)
        values_by_cell.setdefault((row, column), []).append((channel, value))
        if row in {0, GRID_ROWS - 1} or column in {0, GRID_COLUMNS - 1}:
            border_by_channel[channel].append(value)
    _require(all(border_by_channel[channel] for channel in range(CHANNELS)), "masked border lacks a channel")
    background = tuple(float(np.median(border_by_channel[channel])) for channel in range(CHANNELS))
    activation_by_cell = {
        cell: math.fsum(abs(value - background[channel]) for channel, value in cell_values) / len(cell_values)
        for cell, cell_values in values_by_cell.items()
    }
    positive = {cell: value for cell, value in activation_by_cell.items() if value > 0.0}
    _require(bool(positive), "masked values contain no observed form activation")
    total = math.fsum(positive.values())
    centroid_x_index = math.fsum((column + 0.5) * value for (row, column), value in positive.items()) / total
    centroid_y_index = math.fsum((row + 0.5) * value for (row, column), value in positive.items()) / total
    rows = tuple(cell[0] for cell in positive)
    columns = tuple(cell[1] for cell in positive)
    pose = MaskedPoseV1(
        observed_cell_count=len(values_by_cell),
        support_cell_count=len(positive),
        background_channels=background,
        total_observed_activation=float(total),
        centroid_x=float(centroid_x_index / GRID_COLUMNS),
        centroid_y=float(centroid_y_index / GRID_ROWS),
        extent_width=float((max(columns) - min(columns) + 1) / GRID_COLUMNS),
        extent_height=float((max(rows) - min(rows) + 1) / GRID_ROWS),
    )
    descriptor = MaskedFormDescriptorV1(values=_bilinear_descriptor(positive))
    return MaskedPoseFormProjectionV1(masked_view_digest=view.digest(), pose=pose, form_descriptor=descriptor)


__all__: tuple[str, ...] = ()
