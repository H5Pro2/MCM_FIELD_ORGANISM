"""Private immutable pose/form views derived from the 288 visual values."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math

import numpy as np


SCHEMA = "s2lv.private-pose-form-projection.v1"
GRID_ROWS = 8
GRID_COLUMNS = 12
CHANNELS = 3
FORM_GRID_SIZE = 12


class S2LVProjectionError(ValueError):
    """The receptor state cannot be projected without inventing structure."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2LVProjectionError(message)


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


@dataclass(frozen=True, slots=True)
class PoseV1:
    background_channels: tuple[float, float, float]
    total_activation: float
    peak_activation: float
    support_cell_count: int
    centroid_x: float
    centroid_y: float
    bbox_left: float
    bbox_top: float
    bbox_right: float
    bbox_bottom: float
    extent_width: float
    extent_height: float
    weighted_rms_x: float
    weighted_rms_y: float

    def __post_init__(self) -> None:
        values = (
            *self.background_channels,
            self.total_activation,
            self.peak_activation,
            self.centroid_x,
            self.centroid_y,
            self.bbox_left,
            self.bbox_top,
            self.bbox_right,
            self.bbox_bottom,
            self.extent_width,
            self.extent_height,
            self.weighted_rms_x,
            self.weighted_rms_y,
        )
        _require(all(type(value) is float and math.isfinite(value) for value in values), "pose value differs")
        _require(type(self.support_cell_count) is int and 0 < self.support_cell_count <= GRID_ROWS * GRID_COLUMNS, "pose support differs")
        _require(self.total_activation > 0.0 and self.peak_activation > 0.0, "pose activation differs")
        _require(0.0 <= self.centroid_x <= 1.0 and 0.0 <= self.centroid_y <= 1.0, "pose centroid differs")
        _require(0.0 <= self.bbox_left < self.bbox_right <= 1.0, "pose horizontal bounds differ")
        _require(0.0 <= self.bbox_top < self.bbox_bottom <= 1.0, "pose vertical bounds differ")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema": "s2lv.pose.v1",
            "background_channels": list(self.background_channels),
            "total_activation": self.total_activation,
            "peak_activation": self.peak_activation,
            "support_cell_count": self.support_cell_count,
            "centroid_x": self.centroid_x,
            "centroid_y": self.centroid_y,
            "bbox_left": self.bbox_left,
            "bbox_top": self.bbox_top,
            "bbox_right": self.bbox_right,
            "bbox_bottom": self.bbox_bottom,
            "extent_width": self.extent_width,
            "extent_height": self.extent_height,
            "weighted_rms_x": self.weighted_rms_x,
            "weighted_rms_y": self.weighted_rms_y,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class FormDescriptorV1:
    grid_size: int
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        _require(self.grid_size == FORM_GRID_SIZE, "form grid differs")
        _require(type(self.values) is tuple and len(self.values) == self.grid_size * self.grid_size, "form dimension differs")
        _require(all(type(value) is float and math.isfinite(value) and value >= 0.0 for value in self.values), "form value differs")
        _require(abs(math.fsum(self.values) - 1.0) <= 1e-12, "form mass differs")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema": "s2lv.form-descriptor.v1",
            "grid_size": self.grid_size,
            "normalization": "UNIT_TOTAL_MASS",
            "values": list(self.values),
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class PoseFormProjectionV1:
    input_values_digest: str
    pose: PoseV1
    form_descriptor: FormDescriptorV1

    def __post_init__(self) -> None:
        _require(type(self.input_values_digest) is str and len(self.input_values_digest) == 64, "input digest differs")
        _require(type(self.pose) is PoseV1 and type(self.form_descriptor) is FormDescriptorV1, "projection role differs")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema": SCHEMA,
            "input_values_digest": self.input_values_digest,
            "pose": self.pose.canonical_payload(),
            "form_descriptor": self.form_descriptor.canonical_payload(),
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def _border_values(grid: np.ndarray) -> np.ndarray:
    mask = np.zeros((GRID_ROWS, GRID_COLUMNS), dtype=bool)
    mask[0, :] = True
    mask[-1, :] = True
    mask[:, 0] = True
    mask[:, -1] = True
    return grid[mask]


def _bilinear_form_descriptor(activation: np.ndarray, support: np.ndarray) -> tuple[float, ...]:
    rows, columns = np.nonzero(support)
    left, right = int(columns.min()), int(columns.max())
    top, bottom = int(rows.min()), int(rows.max())
    centre_x = (left + right) / 2.0
    centre_y = (top + bottom) / 2.0
    isotropic_span = float(max(right - left + 1, bottom - top + 1))
    canvas = np.zeros((FORM_GRID_SIZE, FORM_GRID_SIZE), dtype=np.float64)
    for row, column in zip(rows, columns, strict=True):
        normalized_x = (float(column) - centre_x) / isotropic_span + 0.5
        normalized_y = (float(row) - centre_y) / isotropic_span + 0.5
        canvas_x = normalized_x * (FORM_GRID_SIZE - 1)
        canvas_y = normalized_y * (FORM_GRID_SIZE - 1)
        x0, y0 = int(math.floor(canvas_x)), int(math.floor(canvas_y))
        x1, y1 = min(x0 + 1, FORM_GRID_SIZE - 1), min(y0 + 1, FORM_GRID_SIZE - 1)
        fx, fy = canvas_x - x0, canvas_y - y0
        value = float(activation[row, column])
        canvas[y0, x0] += value * (1.0 - fx) * (1.0 - fy)
        canvas[y0, x1] += value * fx * (1.0 - fy)
        canvas[y1, x0] += value * (1.0 - fx) * fy
        canvas[y1, x1] += value * fx * fy
    total = float(canvas.sum(dtype=np.float64))
    _require(math.isfinite(total) and total > 0.0, "canonical form mass differs")
    normalized = canvas / total
    return tuple(float(value) for value in normalized.reshape(-1))


def project_pose_form(values: tuple[float, ...]) -> PoseFormProjectionV1:
    _require(type(values) is tuple and len(values) == GRID_ROWS * GRID_COLUMNS * CHANNELS, "visual values differ")
    _require(all(type(value) is float and math.isfinite(value) and 0.0 <= value <= 1.0 for value in values), "visual value domain differs")
    grid = np.asarray(values, dtype=np.float64).reshape(GRID_ROWS, GRID_COLUMNS, CHANNELS)
    background = np.median(_border_values(grid), axis=0)
    activation = np.abs(grid - background.reshape(1, 1, CHANNELS)).mean(axis=2, dtype=np.float64)
    support = activation > 0.0
    _require(bool(np.any(support)), "visual state has no form activation")
    rows, columns = np.nonzero(support)
    weights = activation[support]
    total = float(weights.sum(dtype=np.float64))
    centre_x_index = float(np.dot(columns.astype(np.float64) + 0.5, weights) / total)
    centre_y_index = float(np.dot(rows.astype(np.float64) + 0.5, weights) / total)
    rms_x = math.sqrt(float(np.dot((columns.astype(np.float64) + 0.5 - centre_x_index) ** 2, weights) / total))
    rms_y = math.sqrt(float(np.dot((rows.astype(np.float64) + 0.5 - centre_y_index) ** 2, weights) / total))
    left, right = int(columns.min()), int(columns.max())
    top, bottom = int(rows.min()), int(rows.max())
    pose = PoseV1(
        background_channels=tuple(float(value) for value in background),
        total_activation=total,
        peak_activation=float(activation.max()),
        support_cell_count=int(support.sum()),
        centroid_x=centre_x_index / GRID_COLUMNS,
        centroid_y=centre_y_index / GRID_ROWS,
        bbox_left=left / GRID_COLUMNS,
        bbox_top=top / GRID_ROWS,
        bbox_right=(right + 1) / GRID_COLUMNS,
        bbox_bottom=(bottom + 1) / GRID_ROWS,
        extent_width=(right - left + 1) / GRID_COLUMNS,
        extent_height=(bottom - top + 1) / GRID_ROWS,
        weighted_rms_x=rms_x / GRID_COLUMNS,
        weighted_rms_y=rms_y / GRID_ROWS,
    )
    descriptor = FormDescriptorV1(grid_size=FORM_GRID_SIZE, values=_bilinear_form_descriptor(activation, support))
    return PoseFormProjectionV1(
        input_values_digest=_digest(list(values)),
        pose=pose,
        form_descriptor=descriptor,
    )


__all__: tuple[str, ...] = ()
