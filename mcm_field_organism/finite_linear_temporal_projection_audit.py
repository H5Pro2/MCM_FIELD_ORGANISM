"""Exact nullspace audit for fixed finite linear temporal projections."""

from __future__ import annotations

from dataclasses import dataclass, fields
from fractions import Fraction


RationalRow = tuple[Fraction, ...]
RationalMatrix = tuple[RationalRow, ...]


@dataclass(frozen=True, slots=True)
class FiniteLinearProjectionBank:
    history_dimension: int
    projection_ids: tuple[str, ...]
    coefficient_rows: tuple[tuple[str, ...], ...]


@dataclass(frozen=True, slots=True)
class FiniteLinearTemporalProjectionAuditResult:
    history_dimension: int
    projection_count: int
    matrix_rank: int
    exact_nullity: int
    null_vector: tuple[str, ...]
    null_vector_nonzero: bool
    null_vector_annihilated: bool
    first_history: tuple[float, ...]
    second_history: tuple[float, ...]
    histories_distinct: bool
    contacts_within_normalized_domain: bool
    endpoints_equal: bool
    first_projection_values: tuple[str, ...]
    second_projection_values: tuple[str, ...]
    projections_equal_exactly: bool
    fixed_linear_bank_injective_on_full_history_space: bool
    all_fixed_finite_representations_falsified: bool
    field_effect_performed: bool
    runtime_candidate_released: bool


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _projection_matrix(history_dimension: int) -> RationalMatrix:
    if history_dimension < 7:
        raise ValueError("audit requires more history dimensions than probes")

    endpoint_first = tuple(
        Fraction(1 if index == 0 else 0)
        for index in range(history_dimension)
    )
    endpoint_last = tuple(
        Fraction(1 if index == history_dimension - 1 else 0)
        for index in range(history_dimension)
    )
    moment_rows = tuple(
        tuple(
            Fraction(
                (index + 1) ** (order + 1) - index ** (order + 1),
                (order + 1) * history_dimension ** (order + 1),
            )
            for index in range(history_dimension)
        )
        for order in range(4)
    )
    return (endpoint_first, endpoint_last, *moment_rows)


def _reduced_row_echelon(
    matrix: RationalMatrix,
) -> tuple[list[list[Fraction]], tuple[int, ...]]:
    rows = [list(row) for row in matrix]
    if not rows:
        return rows, ()
    column_count = len(rows[0])
    pivot_columns: list[int] = []
    pivot_row = 0

    for column in range(column_count):
        source_row = next(
            (
                row_index
                for row_index in range(pivot_row, len(rows))
                if rows[row_index][column] != 0
            ),
            None,
        )
        if source_row is None:
            continue
        rows[pivot_row], rows[source_row] = rows[source_row], rows[pivot_row]
        pivot = rows[pivot_row][column]
        rows[pivot_row] = [value / pivot for value in rows[pivot_row]]
        for row_index, row in enumerate(rows):
            if row_index == pivot_row or row[column] == 0:
                continue
            factor = row[column]
            rows[row_index] = [
                value - factor * pivot_value
                for value, pivot_value in zip(row, rows[pivot_row])
            ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == len(rows):
            break

    return rows, tuple(pivot_columns)


def _one_exact_null_vector(matrix: RationalMatrix) -> tuple[Fraction, ...]:
    reduced, pivots = _reduced_row_echelon(matrix)
    column_count = len(matrix[0])
    free_columns = tuple(
        column for column in range(column_count) if column not in pivots
    )
    if not free_columns:
        raise ValueError("projection matrix has no nonzero null vector")

    free_column = free_columns[0]
    vector = [Fraction(0) for _ in range(column_count)]
    vector[free_column] = Fraction(1)
    for row_index, pivot_column in reversed(tuple(enumerate(pivots))):
        vector[pivot_column] = -sum(
            reduced[row_index][column] * vector[column]
            for column in free_columns
        )
    return tuple(vector)


def _matrix_vector_product(
    matrix: RationalMatrix,
    vector: tuple[Fraction, ...],
) -> tuple[Fraction, ...]:
    return tuple(
        sum(coefficient * value for coefficient, value in zip(row, vector))
        for row in matrix
    )


def finite_linear_projection_bank(
    history_dimension: int = 8,
) -> FiniteLinearProjectionBank:
    matrix = _projection_matrix(history_dimension)
    return FiniteLinearProjectionBank(
        history_dimension=history_dimension,
        projection_ids=(
            "first_endpoint",
            "last_endpoint",
            "temporal_moment_0",
            "temporal_moment_1",
            "temporal_moment_2",
            "temporal_moment_3",
        ),
        coefficient_rows=tuple(
            tuple(_fraction_text(value) for value in row)
            for row in matrix
        ),
    )


def run_finite_linear_temporal_projection_audit(
) -> FiniteLinearTemporalProjectionAuditResult:
    """Construct two valid histories with identical exact projections."""

    history_dimension = 8
    matrix = _projection_matrix(history_dimension)
    _, pivot_columns = _reduced_row_echelon(matrix)
    null_vector = _one_exact_null_vector(matrix)
    null_projection = _matrix_vector_product(matrix, null_vector)
    maximum = max(abs(value) for value in null_vector)
    perturbation = tuple(
        value / maximum * Fraction(1, 4)
        for value in null_vector
    )
    center = tuple(Fraction(1, 2) for _ in range(history_dimension))
    first_history = tuple(
        value + delta for value, delta in zip(center, perturbation)
    )
    second_history = tuple(
        value - delta for value, delta in zip(center, perturbation)
    )
    first_projection = _matrix_vector_product(matrix, first_history)
    second_projection = _matrix_vector_product(matrix, second_history)
    rank = len(pivot_columns)

    return FiniteLinearTemporalProjectionAuditResult(
        history_dimension=history_dimension,
        projection_count=len(matrix),
        matrix_rank=rank,
        exact_nullity=history_dimension - rank,
        null_vector=tuple(_fraction_text(value) for value in null_vector),
        null_vector_nonzero=any(value != 0 for value in null_vector),
        null_vector_annihilated=all(value == 0 for value in null_projection),
        first_history=tuple(float(value) for value in first_history),
        second_history=tuple(float(value) for value in second_history),
        histories_distinct=first_history != second_history,
        contacts_within_normalized_domain=all(
            -1 <= value <= 1
            for history in (first_history, second_history)
            for value in history
        ),
        endpoints_equal=(
            first_history[0] == second_history[0]
            and first_history[-1] == second_history[-1]
        ),
        first_projection_values=tuple(
            _fraction_text(value) for value in first_projection
        ),
        second_projection_values=tuple(
            _fraction_text(value) for value in second_projection
        ),
        projections_equal_exactly=first_projection == second_projection,
        fixed_linear_bank_injective_on_full_history_space=False,
        all_fixed_finite_representations_falsified=False,
        field_effect_performed=False,
        runtime_candidate_released=False,
    )


def finite_linear_temporal_projection_audit_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            FiniteLinearProjectionBank,
            FiniteLinearTemporalProjectionAuditResult,
        )
        for item in fields(contract)
    )
