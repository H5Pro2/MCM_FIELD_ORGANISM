"""Private missing-aware form projection for one or two S2-LY views."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math

import numpy as np


SCHEMA = "s2ly.private-masked-form-projection.v1"
GRID_ROWS = 8
GRID_COLUMNS = 12
CHANNELS = 3
FULL_DIMENSION = 288
ALLOWED_OBSERVED_DIMENSIONS = (96, 192)
FORM_GRID_SIZE = 12


class S2LYProjectionError(ValueError):
    """Observed receptor evidence cannot support the requested projection."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2LYProjectionError(message)


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _coordinate(position: int) -> tuple[int, int, int]:
    return position // (GRID_COLUMNS * CHANNELS), (position % (GRID_COLUMNS * CHANNELS)) // CHANNELS, position % CHANNELS


@dataclass(frozen=True, slots=True)
class ObservedVisualViewV1:
    mask_id: str
    mask_digest: str
    source_values_digest: str
    observed_positions: tuple[int, ...]
    observed_values: tuple[float, ...]
    observed_values_digest: str

    def __post_init__(self) -> None:
        _require(type(self.mask_id) is str and self.mask_id in {"VIEW_A_96", "VIEW_B_96", "UNION_192"}, "mask role differs")
        _require(type(self.mask_digest) is str and len(self.mask_digest) == 64, "mask digest differs")
        _require(type(self.source_values_digest) is str and len(self.source_values_digest) == 64, "source digest differs")
        _require(type(self.observed_positions) is tuple and len(self.observed_positions) in ALLOWED_OBSERVED_DIMENSIONS, "observed positions differ")
        _require(len(set(self.observed_positions)) == len(self.observed_positions), "observed positions repeat")
        _require(all(type(item) is int and 0 <= item < FULL_DIMENSION for item in self.observed_positions), "observed position domain differs")
        _require(type(self.observed_values) is tuple and len(self.observed_values) == len(self.observed_positions), "observed values differ")
        _require(all(type(item) is float and math.isfinite(item) and 0.0 <= item <= 1.0 for item in self.observed_values), "observed value domain differs")
        _require(self.observed_values_digest == _digest(list(self.observed_values)), "observed values digest differs")
        _require((self.mask_id == "UNION_192") == (len(self.observed_positions) == 192), "mask dimension binding differs")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema": "s2ly.observed-visual-view.v1",
            "mask_id": self.mask_id,
            "mask_digest": self.mask_digest,
            "source_values_digest": self.source_values_digest,
            "observed_positions": list(self.observed_positions),
            "observed_values": list(self.observed_values),
            "observed_values_digest": self.observed_values_digest,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class MaskConditionedFormV1:
    observed_view_digest: str
    observed_value_count: int
    observed_cell_count: int
    support_cell_count: int
    background_channels: tuple[float, float, float]
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        _require(type(self.observed_view_digest) is str and len(self.observed_view_digest) == 64, "view digest differs")
        _require(self.observed_value_count in ALLOWED_OBSERVED_DIMENSIONS, "observed value count differs")
        _require(type(self.observed_cell_count) is int and 0 < self.observed_cell_count <= 96, "observed cell count differs")
        _require(type(self.support_cell_count) is int and 0 < self.support_cell_count <= self.observed_cell_count, "support count differs")
        _require(type(self.background_channels) is tuple and len(self.background_channels) == CHANNELS, "background differs")
        _require(all(type(item) is float and math.isfinite(item) for item in self.background_channels), "background value differs")
        _require(type(self.values) is tuple and len(self.values) == FORM_GRID_SIZE * FORM_GRID_SIZE, "form dimension differs")
        _require(all(type(item) is float and math.isfinite(item) and item >= 0.0 for item in self.values), "form value differs")
        _require(abs(math.fsum(self.values) - 1.0) <= 1e-12, "form mass differs")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema": SCHEMA,
            "observed_view_digest": self.observed_view_digest,
            "observed_value_count": self.observed_value_count,
            "observed_cell_count": self.observed_cell_count,
            "support_cell_count": self.support_cell_count,
            "background_channels": list(self.background_channels),
            "grid_size": FORM_GRID_SIZE,
            "normalization": "OBSERVED_UNIT_TOTAL_MASS",
            "missing_values": "NOT_PRESENT_NOT_IMPUTED",
            "values": list(self.values),
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def bind_observed_view(
    full_values: tuple[float, ...],
    mask_id: str,
    positions: tuple[int, ...],
    mask_digest: str,
) -> ObservedVisualViewV1:
    _require(type(full_values) is tuple and len(full_values) == FULL_DIMENSION, "full visual values differ")
    _require(all(type(item) is float and math.isfinite(item) and 0.0 <= item <= 1.0 for item in full_values), "full visual value domain differs")
    _require(type(positions) is tuple and len(positions) in ALLOWED_OBSERVED_DIMENSIONS, "mask positions differ")
    observed = tuple(full_values[position] for position in positions)
    return ObservedVisualViewV1(
        mask_id=mask_id,
        mask_digest=mask_digest,
        source_values_digest=_digest(list(full_values)),
        observed_positions=positions,
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


def project_mask_conditioned_form(view: ObservedVisualViewV1) -> MaskConditionedFormV1:
    _require(type(view) is ObservedVisualViewV1, "observed view role differs")
    border_by_channel: dict[int, list[float]] = {channel: [] for channel in range(CHANNELS)}
    values_by_cell: dict[tuple[int, int], list[tuple[int, float]]] = {}
    for position, value in zip(view.observed_positions, view.observed_values, strict=True):
        row, column, channel = _coordinate(position)
        values_by_cell.setdefault((row, column), []).append((channel, value))
        if row in {0, GRID_ROWS - 1} or column in {0, GRID_COLUMNS - 1}:
            border_by_channel[channel].append(value)
    _require(all(border_by_channel[channel] for channel in range(CHANNELS)), "masked border lacks a channel")
    background = tuple(float(np.median(border_by_channel[channel])) for channel in range(CHANNELS))
    activation = {
        cell: math.fsum(abs(value - background[channel]) for channel, value in cell_values) / len(cell_values)
        for cell, cell_values in values_by_cell.items()
    }
    positive = {cell: value for cell, value in activation.items() if value > 0.0}
    _require(bool(positive), "observed values contain no form activation")
    return MaskConditionedFormV1(
        observed_view_digest=view.digest(),
        observed_value_count=len(view.observed_values),
        observed_cell_count=len(values_by_cell),
        support_cell_count=len(positive),
        background_channels=background,
        values=_bilinear_descriptor(positive),
    )


__all__: tuple[str, ...] = ()
