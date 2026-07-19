"""Pure digital projection for the visual MCM effector surface."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math

from .shared_mcm_field import SharedMCMFieldSnapshot


class VisualMCMEffectorSurfaceError(ValueError):
    """Raised when a field snapshot violates the visual effector contract."""


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _identifier(value: object, role: str) -> str:
    if not isinstance(value, str) or not value:
        raise VisualMCMEffectorSurfaceError(
            f"{role} must be a non-empty technical identifier"
        )
    return value


def _integer(value: object, role: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise VisualMCMEffectorSurfaceError(f"{role} must be an integer")
    if minimum is not None and value < minimum:
        raise VisualMCMEffectorSurfaceError(
            f"{role} must be at least {minimum}"
        )
    return value


def _field_activation(value: object) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise VisualMCMEffectorSurfaceError(
            "activation must be numeric"
        ) from exc
    if not math.isfinite(result) or result < -1.0 or result > 1.0:
        raise VisualMCMEffectorSurfaceError(
            "activation must stay within the normalized -1..1 field domain"
        )
    return result


def _intensity(value: object, role: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise VisualMCMEffectorSurfaceError(f"{role} must be numeric") from exc
    if not math.isfinite(result) or result < 0.25 or result > 0.75:
        raise VisualMCMEffectorSurfaceError(
            f"{role} must stay within the fixed 0.25..0.75 range"
        )
    return result


@dataclass(frozen=True, slots=True)
class VisualMCMEffectorCell:
    neuron_id: str
    field_position: tuple[int, int]
    output_row: int
    left_column: int
    right_column: int
    activation: float
    left_intensity: float
    right_intensity: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "neuron_id",
            _identifier(self.neuron_id, "neuron_id"),
        )
        position = tuple(self.field_position)
        if len(position) != 2:
            raise VisualMCMEffectorSurfaceError(
                "field_position must be two-dimensional"
            )
        object.__setattr__(
            self,
            "field_position",
            (
                _integer(position[0], "field row"),
                _integer(position[1], "field column"),
            ),
        )
        row = _integer(self.output_row, "output_row", minimum=0)
        left = _integer(self.left_column, "left_column", minimum=0)
        right = _integer(self.right_column, "right_column", minimum=0)
        if right != left + 1 or left % 2 != 0:
            raise VisualMCMEffectorSurfaceError(
                "effector columns must form one aligned adjacent pair"
            )
        activation = _field_activation(self.activation)
        left_intensity = _intensity(self.left_intensity, "left_intensity")
        right_intensity = _intensity(self.right_intensity, "right_intensity")
        if left_intensity != 0.50 + 0.25 * activation:
            raise VisualMCMEffectorSurfaceError(
                "left intensity violates the affine effector transfer"
            )
        if right_intensity != 0.50 - 0.25 * activation:
            raise VisualMCMEffectorSurfaceError(
                "right intensity violates the affine effector transfer"
            )
        object.__setattr__(self, "output_row", row)
        object.__setattr__(self, "left_column", left)
        object.__setattr__(self, "right_column", right)
        object.__setattr__(self, "activation", activation)
        object.__setattr__(self, "left_intensity", left_intensity)
        object.__setattr__(self, "right_intensity", right_intensity)

    def canonical_payload(self) -> dict[str, object]:
        return {
            item.name: (
                list(value)
                if item.name == "field_position"
                else value
            )
            for item in fields(self)
            for value in (getattr(self, item.name),)
        }


@dataclass(frozen=True, slots=True)
class VisualMCMEffectorFrame:
    source_field_id: str
    source_geometry_id: str
    source_tick: int
    source_window_start_tick: int
    source_window_end_tick: int
    source_snapshot_digest: str
    row_origin: int
    column_origin: int
    rows: int
    columns: int
    intensities: tuple[tuple[float, ...], ...]
    cells: tuple[VisualMCMEffectorCell, ...]
    writes_back: bool = False
    stateful: bool = False
    random_source: bool = False

    def __post_init__(self) -> None:
        for role in (
            "source_field_id",
            "source_geometry_id",
            "source_snapshot_digest",
        ):
            object.__setattr__(
                self,
                role,
                _identifier(getattr(self, role), role),
            )
        tick = _integer(self.source_tick, "source_tick", minimum=0)
        start = _integer(
            self.source_window_start_tick,
            "source_window_start_tick",
            minimum=0,
        )
        end = _integer(
            self.source_window_end_tick,
            "source_window_end_tick",
            minimum=0,
        )
        if start >= end:
            raise VisualMCMEffectorSurfaceError(
                "source field window must have positive duration"
            )
        row_origin = _integer(self.row_origin, "row_origin")
        column_origin = _integer(self.column_origin, "column_origin")
        rows = _integer(self.rows, "rows", minimum=1)
        columns = _integer(self.columns, "columns", minimum=2)
        if columns % 2 != 0:
            raise VisualMCMEffectorSurfaceError(
                "effector frame requires an even number of columns"
            )
        intensities = tuple(
            tuple(
                _intensity(value, "frame intensity")
                for value in row
            )
            for row in self.intensities
        )
        if len(intensities) != rows or any(
            len(row) != columns for row in intensities
        ):
            raise VisualMCMEffectorSurfaceError(
                "intensity raster must match the declared frame geometry"
            )
        cells = tuple(self.cells)
        if not cells or any(
            not isinstance(cell, VisualMCMEffectorCell) for cell in cells
        ):
            raise VisualMCMEffectorSurfaceError(
                "effector frame requires immutable mapped cells"
            )
        field_positions = tuple(cell.field_position for cell in cells)
        neuron_ids = tuple(cell.neuron_id for cell in cells)
        output_pairs = tuple(
            (cell.output_row, cell.left_column, cell.right_column)
            for cell in cells
        )
        if (
            len(set(field_positions)) != len(field_positions)
            or len(set(neuron_ids)) != len(neuron_ids)
            or len(set(output_pairs)) != len(output_pairs)
        ):
            raise VisualMCMEffectorSurfaceError(
                "field cells and output pairs must be unique"
            )
        if tuple(sorted(cells, key=lambda item: (item.field_position, item.neuron_id))) != cells:
            raise VisualMCMEffectorSurfaceError(
                "effector cells must use canonical field-position order"
            )
        for cell in cells:
            if cell.output_row >= rows or cell.right_column >= columns:
                raise VisualMCMEffectorSurfaceError(
                    "mapped cell lies outside the effector raster"
                )
            if (
                intensities[cell.output_row][cell.left_column]
                != cell.left_intensity
                or intensities[cell.output_row][cell.right_column]
                != cell.right_intensity
            ):
                raise VisualMCMEffectorSurfaceError(
                    "cell intensities do not match the effector raster"
                )
        if any(
            not isinstance(value, bool)
            for value in (self.writes_back, self.stateful, self.random_source)
        ):
            raise VisualMCMEffectorSurfaceError(
                "effector behavior flags must be boolean"
            )
        if self.writes_back or self.stateful or self.random_source:
            raise VisualMCMEffectorSurfaceError(
                "digital effector surface cannot write back, store state, or add randomness"
            )
        object.__setattr__(self, "source_tick", tick)
        object.__setattr__(self, "source_window_start_tick", start)
        object.__setattr__(self, "source_window_end_tick", end)
        object.__setattr__(self, "row_origin", row_origin)
        object.__setattr__(self, "column_origin", column_origin)
        object.__setattr__(self, "rows", rows)
        object.__setattr__(self, "columns", columns)
        object.__setattr__(self, "intensities", intensities)
        object.__setattr__(self, "cells", cells)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "source_field_id": self.source_field_id,
            "source_geometry_id": self.source_geometry_id,
            "source_tick": self.source_tick,
            "source_window_start_tick": self.source_window_start_tick,
            "source_window_end_tick": self.source_window_end_tick,
            "source_snapshot_digest": self.source_snapshot_digest,
            "row_origin": self.row_origin,
            "column_origin": self.column_origin,
            "rows": self.rows,
            "columns": self.columns,
            "intensities": [list(row) for row in self.intensities],
            "cells": [cell.canonical_payload() for cell in self.cells],
            "writes_back": self.writes_back,
            "stateful": self.stateful,
            "random_source": self.random_source,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def project_visual_mcm_effector_surface(
    snapshot: SharedMCMFieldSnapshot,
) -> VisualMCMEffectorFrame:
    """Project one completed field snapshot without storing or writing back."""

    if not isinstance(snapshot, SharedMCMFieldSnapshot):
        raise VisualMCMEffectorSurfaceError(
            "visual effector source must be a shared MCM field snapshot"
        )
    neurons = tuple(snapshot.layer.neurons)
    if not neurons:
        raise VisualMCMEffectorSurfaceError(
            "visual effector source cannot be empty"
        )
    if any(len(neuron.position) != 2 for neuron in neurons):
        raise VisualMCMEffectorSurfaceError(
            "visual effector source must use one complete two-dimensional field"
        )
    if any(neuron.tick != snapshot.tick for neuron in neurons):
        raise VisualMCMEffectorSurfaceError(
            "visual effector source mixes incomplete field ticks"
        )
    validated = tuple(
        (
            neuron,
            _field_activation(neuron.activation),
        )
        for neuron in neurons
    )
    row_origin = min(neuron.position[0] for neuron, _ in validated)
    column_origin = min(neuron.position[1] for neuron, _ in validated)
    max_row = max(neuron.position[0] for neuron, _ in validated)
    max_column = max(neuron.position[1] for neuron, _ in validated)
    rows = max_row - row_origin + 1
    columns = 2 * (max_column - column_origin + 1)
    raster = [[0.50 for _ in range(columns)] for _ in range(rows)]
    cells = []
    for neuron, activation in sorted(
        validated,
        key=lambda item: (item[0].position, item[0].neuron_id),
    ):
        output_row = neuron.position[0] - row_origin
        left_column = 2 * (neuron.position[1] - column_origin)
        right_column = left_column + 1
        left_intensity = 0.50 + 0.25 * activation
        right_intensity = 0.50 - 0.25 * activation
        raster[output_row][left_column] = left_intensity
        raster[output_row][right_column] = right_intensity
        cells.append(
            VisualMCMEffectorCell(
                neuron_id=neuron.neuron_id,
                field_position=(
                    neuron.position[0],
                    neuron.position[1],
                ),
                output_row=output_row,
                left_column=left_column,
                right_column=right_column,
                activation=activation,
                left_intensity=left_intensity,
                right_intensity=right_intensity,
            )
        )
    return VisualMCMEffectorFrame(
        source_field_id=snapshot.field_id,
        source_geometry_id=snapshot.geometry_id,
        source_tick=snapshot.tick,
        source_window_start_tick=snapshot.window_start_tick,
        source_window_end_tick=snapshot.window_end_tick,
        source_snapshot_digest=snapshot.digest(),
        row_origin=row_origin,
        column_origin=column_origin,
        rows=rows,
        columns=columns,
        intensities=tuple(tuple(row) for row in raster),
        cells=tuple(cells),
    )


def visual_mcm_effector_surface_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (VisualMCMEffectorCell, VisualMCMEffectorFrame)
        for item in fields(cls)
    )
