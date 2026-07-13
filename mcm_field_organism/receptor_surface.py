"""Controlled receptor-surface baselines for Methodik 003.

Geometry in this module is a fixed experimental address space. It defines no
neighbor interaction, field propagation, pattern recognition, or semantics.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Mapping

from .carrier_baselines import (
    BaselineValidationError,
    CarrierFrame,
    run_independent_history,
    stateless_baseline,
)


Position = tuple[int, int]


@dataclass(frozen=True, slots=True)
class ControlledReceptorSurface:
    """A row-major technical surface with no carrier-to-carrier effects."""

    rows: int = 3
    columns: int = 3

    def __post_init__(self) -> None:
        if isinstance(self.rows, bool) or not isinstance(self.rows, int) or self.rows <= 0:
            raise BaselineValidationError("rows must be a positive integer")
        if isinstance(self.columns, bool) or not isinstance(self.columns, int) or self.columns <= 0:
            raise BaselineValidationError("columns must be a positive integer")

    @property
    def size(self) -> int:
        return self.rows * self.columns

    @property
    def carrier_ids(self) -> tuple[str, ...]:
        return tuple(
            f"p{row}{column}"
            for row in range(self.rows)
            for column in range(self.columns)
        )

    def index(self, position: Position) -> int:
        if (
            not isinstance(position, tuple)
            or len(position) != 2
            or any(isinstance(value, bool) or not isinstance(value, int) for value in position)
        ):
            raise BaselineValidationError("position must be an integer (row, column) tuple")
        row, column = position
        if not 0 <= row < self.rows or not 0 <= column < self.columns:
            raise BaselineValidationError(f"position outside surface: {position}")
        return (row * self.columns) + column

    def contact_vector(self, contacts: Mapping[Position, float]) -> tuple[float, ...]:
        vector = [0.0] * self.size
        for position, raw_value in contacts.items():
            try:
                value = float(raw_value)
            except (TypeError, ValueError) as exc:
                raise BaselineValidationError("contact values must be numeric") from exc
            if not math.isfinite(value) or abs(value) > 1.0:
                raise BaselineValidationError("contact values must be finite and within -1..1")
            vector[self.index(position)] = value
        return tuple(vector)

    def translate_vector(
        self,
        values: Iterable[float],
        *,
        row_offset: int,
        column_offset: int,
    ) -> tuple[float, ...]:
        vector = tuple(float(value) for value in values)
        if len(vector) != self.size:
            raise BaselineValidationError("vector must match surface geometry")
        translated = [0.0] * self.size
        for row in range(self.rows):
            for column in range(self.columns):
                value = vector[self.index((row, column))]
                if value == 0.0:
                    continue
                target = (row + row_offset, column + column_offset)
                try:
                    target_index = self.index(target)
                except BaselineValidationError as exc:
                    raise BaselineValidationError("translation would discard a non-zero value") from exc
                translated[target_index] = value
        return tuple(translated)


def stateless_surface_frame(
    surface: ControlledReceptorSurface,
    contacts: Mapping[Position, float],
) -> CarrierFrame:
    return stateless_baseline(surface.contact_vector(contacts))


def run_independent_surface_history(
    surface: ControlledReceptorSurface,
    history: Iterable[Mapping[Position, float]],
    *,
    dt: float,
    tau: float,
) -> tuple[CarrierFrame, ...]:
    contact_vectors = tuple(surface.contact_vector(contacts) for contacts in history)
    return run_independent_history(contact_vectors, dt=dt, tau=tau)


def surface_sum_baseline(
    surface: ControlledReceptorSurface,
    contacts: Mapping[Position, float],
) -> float:
    """B2 loss baseline that discards every position identity."""

    return sum(surface.contact_vector(contacts))
