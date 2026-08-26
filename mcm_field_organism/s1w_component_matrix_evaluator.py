"""Passive full evaluator for the preregistered S1-T component matrix."""

from __future__ import annotations

from dataclasses import dataclass, fields
from functools import lru_cache
import math

from .s1l_f3_history_function_adapter import (
    S1L_ABSOLUTE_FLOOR,
    S1L_LINEAR_EQUIVALENCE_LIMIT,
)
from .s1u_f3_component_observer import run_s1u_component_cell
from .s1v_four_curve_component_matrix import (
    S1V_MODELS,
    S1VLedgerCellContract,
    run_s1v_ledger_cell,
    s1v_ledger_inventory,
)


class S1WComponentMatrixEvaluationError(ValueError):
    """Raised when the fixed S1-W matrix loses a bound control."""


@dataclass(frozen=True, slots=True)
class S1WLedgerEvaluation:
    cell: S1VLedgerCellContract
    transport_linf: float
    activation_forcing_linf: float
    mass_increment_linf: float
    transport_detection_floor: float
    activation_forcing_detection_floor: float
    mass_increment_detection_floor: float
    transport_linear_relative_residual: float
    activation_forcing_linear_relative_residual: float
    active_mass_direction: str
    kappa_null_mass_direction: str
    eta_difference_linf: float
    eta_difference_floor: float
    eta_difference_detected: bool
    maximum_closure_linf: float
    all_arms_transparent: bool


@dataclass(frozen=True, slots=True)
class S1WComponentMatrixEvaluation:
    cells: tuple[S1WLedgerEvaluation, ...]
    inventory_control_holds: bool
    balance_controls_hold: bool
    observer_transparency_holds: bool
    kappa_null_controls_hold: bool
    null_controls_hold: bool
    repeatability_control_holds: bool
    finite_metrics_hold: bool
    all_controls_hold: bool
    detected_direct_component_count: int
    active_late_increase_count: int
    active_late_decrease_count: int
    kappa_null_late_increase_count: int
    eta_different_late_interval_count: int
    maximum_linear_relative_residual: float
    maximum_closure_linf: float
    direct_drive_classification: str
    backreaction_classification: str
    mechanism_classification: str
    raw_payload_retained: bool = False
    runtime_writeback_allowed: bool = False
    formal_research_run: bool = False
    memory_claim_allowed: bool = False
    learning_claim_allowed: bool = False
    field_time_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False


def _difference_linf(
    first: tuple[float, ...],
    second: tuple[float, ...],
) -> float:
    return max(
        (
            abs(left - right)
            for left, right in zip(first, second, strict=True)
        ),
        default=0.0,
    )


def _vector_floor(
    coarse: tuple[float, ...],
    fine: tuple[float, ...],
) -> float:
    return max(S1L_ABSOLUTE_FLOOR, 8.0 * _difference_linf(coarse, fine))


def _linf(vector: tuple[float, ...]) -> float:
    return max((abs(value) for value in vector), default=0.0)


def _relative_residual(
    active: tuple[float, ...],
    baseline: tuple[float, ...],
    detection_floor: float,
) -> float:
    return _difference_linf(active, baseline) / max(
        _linf(active),
        detection_floor,
    )


def _centered_mass_linf(
    mass: tuple[float, ...],
    total_mass: float = 1.0,
) -> float:
    neutral = total_mass / len(mass)
    return max((abs(value - neutral) for value in mass), default=0.0)


def _direction(ledger, floor: float) -> str:
    start = _centered_mass_linf(ledger.mass_start)
    end = _centered_mass_linf(ledger.mass_end)
    if end > start + floor:
        return "INCREASE"
    if start > end + floor:
        return "DECREASE"
    return "STABLE_WITHIN_FLOOR"


def _combined_vector(ledger) -> tuple[float, ...]:
    return (
        *ledger.delta_transport,
        *ledger.delta_activation_forcing,
        *ledger.delta_mass,
    )


def _cell_evaluation(cell, measurements) -> S1WLedgerEvaluation:
    active_r2 = measurements[("f3", 2)].ledger
    active_r4 = measurements[("f3", 4)].ledger
    linear_r4 = measurements[("linear-coupled-field", 4)].ledger
    kappa_r2 = measurements[("kappa-null", 2)].ledger
    kappa_r4 = measurements[("kappa-null", 4)].ledger
    eta_r2 = measurements[("eta-null", 2)].ledger
    eta_r4 = measurements[("eta-null", 4)].ledger

    transport_floor = _vector_floor(
        active_r2.delta_transport,
        active_r4.delta_transport,
    )
    forcing_floor = _vector_floor(
        active_r2.delta_activation_forcing,
        active_r4.delta_activation_forcing,
    )
    mass_floor = _vector_floor(active_r2.delta_mass, active_r4.delta_mass)
    kappa_mass_floor = _vector_floor(
        kappa_r2.delta_mass,
        kappa_r4.delta_mass,
    )
    eta_difference = _difference_linf(
        _combined_vector(active_r4),
        _combined_vector(eta_r4),
    )
    eta_difference_floor = max(
        _vector_floor(
            _combined_vector(active_r2),
            _combined_vector(active_r4),
        ),
        _vector_floor(
            _combined_vector(eta_r2),
            _combined_vector(eta_r4),
        ),
    )
    ledgers = tuple(
        measurement.ledger for measurement in measurements.values()
    )
    return S1WLedgerEvaluation(
        cell=cell,
        transport_linf=_linf(active_r4.delta_transport),
        activation_forcing_linf=_linf(
            active_r4.delta_activation_forcing
        ),
        mass_increment_linf=_linf(active_r4.delta_mass),
        transport_detection_floor=transport_floor,
        activation_forcing_detection_floor=forcing_floor,
        mass_increment_detection_floor=mass_floor,
        transport_linear_relative_residual=_relative_residual(
            active_r4.delta_transport,
            linear_r4.delta_transport,
            transport_floor,
        ),
        activation_forcing_linear_relative_residual=_relative_residual(
            active_r4.delta_activation_forcing,
            linear_r4.delta_activation_forcing,
            forcing_floor,
        ),
        active_mass_direction=_direction(active_r4, mass_floor),
        kappa_null_mass_direction=_direction(kappa_r4, kappa_mass_floor),
        eta_difference_linf=eta_difference,
        eta_difference_floor=eta_difference_floor,
        eta_difference_detected=eta_difference > eta_difference_floor,
        maximum_closure_linf=max(
            ledger.closure_linf for ledger in ledgers
        ),
        all_arms_transparent=all(
            ledger.observer_transparent for ledger in ledgers
        ),
    )


def _balance_holds(measurements) -> bool:
    for group in measurements.values():
        for measurement in group.values():
            ledger = measurement.ledger
            if (
                ledger.closure_linf > 1e-12
                or abs(ledger.transport_sum) > 1e-12
                or abs(ledger.activation_forcing_sum) > 1e-12
                or abs(ledger.total_rate_sum) > 1e-12
                or abs(ledger.delta_mass_sum) > 1e-12
            ):
                return False
    return True


def _null_controls_hold() -> bool:
    for model_id, source_role in (
        ("p0", "exposed"),
        ("f3", "uniform-null"),
    ):
        result = run_s1u_component_cell(
            model_id,
            1,
            "repeated-supports",
            0.2,
            4,
            source_role=source_role,
        )
        if any(
            value != 0.0
            for vector in (
                result.delta_transport,
                result.delta_activation_forcing,
                result.delta_mass,
            )
            for value in vector
        ):
            return False
    return True


@lru_cache(maxsize=1)
def evaluate_s1w_component_matrix() -> S1WComponentMatrixEvaluation:
    """Execute and classify the fixed S1-T component matrix in memory."""

    inventory = s1v_ledger_inventory()
    measurements = {}
    cell_evaluations = []
    for cell in inventory:
        group = {}
        for model_id in S1V_MODELS:
            for refinement in (2, 4):
                group[(model_id, refinement)] = run_s1v_ledger_cell(
                    model_id,
                    cell.dose_count,
                    cell.source_form,
                    cell.ledger_role,
                    cell.start_seconds,
                    cell.end_seconds,
                    refinement,
                )
        measurements[cell.ledger_id] = group
        cell_evaluations.append(_cell_evaluation(cell, group))

    cells = tuple(cell_evaluations)
    inventory_control_holds = bool(
        len(inventory) == 28
        and len({cell.ledger_id for cell in inventory}) == 28
        and sum(cell.ledger_role == "early-cumulative" for cell in inventory)
        == 16
        and sum(cell.ledger_role == "late-interval" for cell in inventory)
        == 12
    )
    balance_controls_hold = _balance_holds(measurements)
    observer_transparency_holds = all(
        cell.all_arms_transparent for cell in cells
    )
    kappa_null_controls_hold = all(
        measurement.ledger.delta_activation_forcing == (0.0,) * 26
        for group in measurements.values()
        for key, measurement in group.items()
        if key[0] == "kappa-null"
    )
    null_controls_hold = _null_controls_hold()
    repeat_cell = inventory[-1]
    repeat_key = ("f3", 4)
    repeated = run_s1v_ledger_cell(
        repeat_key[0],
        repeat_cell.dose_count,
        repeat_cell.source_form,
        repeat_cell.ledger_role,
        repeat_cell.start_seconds,
        repeat_cell.end_seconds,
        repeat_key[1],
    )
    repeatability_control_holds = (
        repeated == measurements[repeat_cell.ledger_id][repeat_key]
    )
    finite_metrics_hold = all(
        math.isfinite(value) and value >= 0.0
        for cell in cells
        for value in (
            cell.transport_linf,
            cell.activation_forcing_linf,
            cell.mass_increment_linf,
            cell.transport_detection_floor,
            cell.activation_forcing_detection_floor,
            cell.mass_increment_detection_floor,
            cell.transport_linear_relative_residual,
            cell.activation_forcing_linear_relative_residual,
            cell.eta_difference_linf,
            cell.eta_difference_floor,
            cell.maximum_closure_linf,
        )
    )
    all_controls_hold = all(
        (
            inventory_control_holds,
            balance_controls_hold,
            observer_transparency_holds,
            kappa_null_controls_hold,
            null_controls_hold,
            repeatability_control_holds,
            finite_metrics_hold,
        )
    )

    late = tuple(
        cell for cell in cells if cell.cell.ledger_role == "late-interval"
    )
    active_late_increase_count = sum(
        cell.active_mass_direction == "INCREASE" for cell in late
    )
    active_late_decrease_count = sum(
        cell.active_mass_direction == "DECREASE" for cell in late
    )
    kappa_late_increase_count = sum(
        cell.kappa_null_mass_direction == "INCREASE" for cell in late
    )
    eta_different_count = sum(cell.eta_difference_detected for cell in late)

    detected_residuals = []
    detected_direct_count = 0
    for cell in cells:
        if cell.transport_linf > cell.transport_detection_floor:
            detected_direct_count += 1
            detected_residuals.append(
                cell.transport_linear_relative_residual
            )
        if (
            cell.activation_forcing_linf
            > cell.activation_forcing_detection_floor
        ):
            detected_direct_count += 1
            detected_residuals.append(
                cell.activation_forcing_linear_relative_residual
            )
    maximum_linear_residual = max(detected_residuals, default=0.0)
    maximum_closure = max(
        (cell.maximum_closure_linf for cell in cells),
        default=0.0,
    )

    if all_controls_hold:
        if active_late_increase_count == 0:
            direct_drive_classification = "NO_LATE_MIXTURE_IN_COMPONENT_LEDGER"
        elif kappa_late_increase_count > 0:
            direct_drive_classification = (
                "MASS_RELAXATION_ALONE_REPRODUCES_LATE_MIXTURE"
            )
        else:
            direct_drive_classification = (
                "ACTIVATION_FORCING_REQUIRED_FOR_LATE_MIXTURE"
            )
        backreaction_classification = (
            "RECIPROCAL_BACKREACTION_CHANGES_LATE_LEDGER"
            if eta_different_count > 0
            else "LATE_LEDGER_ETA_EQUIVALENT_WITHIN_FLOOR"
        )
        mechanism_classification = (
            "COMPONENT_LEDGER_LINEARLY_EXPLAINED"
            if maximum_linear_residual <= S1L_LINEAR_EQUIVALENCE_LIMIT
            else "COMPONENT_LEDGER_CONTAINS_BASELINE_DIFFERENT_INTERVAL"
        )
    else:
        direct_drive_classification = "TECHNICALLY_INVALID"
        backreaction_classification = "TECHNICALLY_INVALID"
        mechanism_classification = "TECHNICALLY_INVALID"

    return S1WComponentMatrixEvaluation(
        cells=cells,
        inventory_control_holds=inventory_control_holds,
        balance_controls_hold=balance_controls_hold,
        observer_transparency_holds=observer_transparency_holds,
        kappa_null_controls_hold=kappa_null_controls_hold,
        null_controls_hold=null_controls_hold,
        repeatability_control_holds=repeatability_control_holds,
        finite_metrics_hold=finite_metrics_hold,
        all_controls_hold=all_controls_hold,
        detected_direct_component_count=detected_direct_count,
        active_late_increase_count=active_late_increase_count,
        active_late_decrease_count=active_late_decrease_count,
        kappa_null_late_increase_count=kappa_late_increase_count,
        eta_different_late_interval_count=eta_different_count,
        maximum_linear_relative_residual=maximum_linear_residual,
        maximum_closure_linf=maximum_closure,
        direct_drive_classification=direct_drive_classification,
        backreaction_classification=backreaction_classification,
        mechanism_classification=mechanism_classification,
    )


def s1w_component_matrix_evaluation_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (S1WLedgerEvaluation, S1WComponentMatrixEvaluation)
        for item in fields(cls)
    )
