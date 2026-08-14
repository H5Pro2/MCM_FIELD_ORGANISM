"""Passive evaluator for the complete preregistered S1-Q matrix."""

from __future__ import annotations

from dataclasses import dataclass, fields
from functools import lru_cache
import math

from .s1l_f3_history_function_adapter import (
    S1L_ABSOLUTE_FLOOR,
    S1L_LINEAR_EQUIVALENCE_LIMIT,
    S1L_MASS_TOLERANCE,
    S1LFieldState,
)
from .s1r_phase_separation_matrix import (
    S1R_DELAY_SECONDS,
    S1R_DOSE_COUNTS,
    S1R_PHASE_BOUNDARY_SECONDS,
    S1R_SENTINEL_DELAYS,
    S1R_SOURCE_FORMS,
    S1RCellMeasurement,
    S1RMatrixCellContract,
    build_s1r_cell_source_contract,
    run_s1r_matrix_cell,
    s1r_matrix_inventory,
)


class S1SPhaseSeparationEvaluationError(ValueError):
    """Raised when the fixed S1-S evaluation loses a bound control."""


@dataclass(frozen=True, slots=True)
class S1SCellEvaluation:
    cell: S1RMatrixCellContract
    f3_preprobe_mass_linf: float
    f3_probe_effect_linf: float
    mass_refinement_2_4_linf: float
    probe_refinement_2_4_linf: float
    mass_detection_floor: float
    probe_detection_floor: float
    mass_linear_relative_residual: float
    probe_linear_relative_residual: float
    mass_detected: bool
    probe_detected: bool


@dataclass(frozen=True, slots=True)
class S1SWindowEvaluation:
    metric_role: str
    dose_count: int
    source_form: str
    window_role: str
    classification: str


@dataclass(frozen=True, slots=True)
class S1SPhaseSeparationEvaluation:
    cells: tuple[S1SCellEvaluation, ...]
    windows: tuple[S1SWindowEvaluation, ...]
    source_controls_hold: bool
    alignment_controls_hold: bool
    mass_controls_hold: bool
    sentinel_null_controls_hold: bool
    repeatability_control_holds: bool
    finite_metrics_hold: bool
    all_controls_hold: bool
    detected_mass_cell_count: int
    detected_probe_cell_count: int
    maximum_mass_linear_relative_residual: float
    maximum_probe_linear_relative_residual: float
    phase_classification: str
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


def _cell_key(cell: S1RMatrixCellContract):
    return cell.dose_count, cell.source_form, cell.delay_seconds


def _states(measurement: S1RCellMeasurement):
    return (
        measurement.exposed_preprobe,
        measurement.zero_preprobe,
        *measurement.exposed_probe,
        *measurement.zero_probe,
    )


def _mass_holds(state: S1LFieldState) -> bool:
    return bool(
        state.mass
        and min(state.mass) >= 0.0
        and abs(math.fsum(state.mass) - 1.0) <= S1L_MASS_TOLERANCE
        and all(math.isfinite(value) for value in state.mass)
    )


def _alignment_holds(measurement: S1RCellMeasurement) -> bool:
    zero = (0.0,) * 26
    return all(
        state.activation == zero and state.afterimage == zero
        for state in (
            measurement.exposed_preprobe,
            measurement.zero_preprobe,
        )
    )


def _relative_residual(
    f3_vector: tuple[float, ...],
    linear_vector: tuple[float, ...],
    f3_linf: float,
    detection_floor: float,
) -> float:
    return _difference_linf(f3_vector, linear_vector) / max(
        f3_linf,
        detection_floor,
    )


def _cell_evaluation(
    cell: S1RMatrixCellContract,
    f3_r2: S1RCellMeasurement,
    f3_r4: S1RCellMeasurement,
    linear: S1RCellMeasurement,
) -> S1SCellEvaluation:
    mass_refinement = _difference_linf(
        f3_r2.preprobe_mass_vector,
        f3_r4.preprobe_mass_vector,
    )
    probe_refinement = _difference_linf(
        f3_r2.probe_effect_vector,
        f3_r4.probe_effect_vector,
    )
    mass_floor = max(S1L_ABSOLUTE_FLOOR, 8.0 * mass_refinement)
    probe_floor = max(S1L_ABSOLUTE_FLOOR, 8.0 * probe_refinement)
    mass_linf = f3_r4.preprobe_mass_linf
    probe_linf = f3_r4.probe_effect_linf
    return S1SCellEvaluation(
        cell=cell,
        f3_preprobe_mass_linf=mass_linf,
        f3_probe_effect_linf=probe_linf,
        mass_refinement_2_4_linf=mass_refinement,
        probe_refinement_2_4_linf=probe_refinement,
        mass_detection_floor=mass_floor,
        probe_detection_floor=probe_floor,
        mass_linear_relative_residual=_relative_residual(
            f3_r4.preprobe_mass_vector,
            linear.preprobe_mass_vector,
            mass_linf,
            mass_floor,
        ),
        probe_linear_relative_residual=_relative_residual(
            f3_r4.probe_effect_vector,
            linear.probe_effect_vector,
            probe_linf,
            probe_floor,
        ),
        mass_detected=mass_linf > mass_floor,
        probe_detected=probe_linf > probe_floor,
    )


def _metric_value(cell: S1SCellEvaluation, metric_role: str) -> float:
    if metric_role == "preprobe-mass":
        return cell.f3_preprobe_mass_linf
    return cell.f3_probe_effect_linf


def _metric_floor(cell: S1SCellEvaluation, metric_role: str) -> float:
    if metric_role == "preprobe-mass":
        return cell.mass_detection_floor
    return cell.probe_detection_floor


def _window_delays(window_role: str) -> tuple[float, ...]:
    if window_role == "early":
        return tuple(
            delay
            for delay in S1R_DELAY_SECONDS
            if delay <= S1R_PHASE_BOUNDARY_SECONDS
        )
    return tuple(
        delay
        for delay in S1R_DELAY_SECONDS
        if delay >= S1R_PHASE_BOUNDARY_SECONDS
    )


def _classify_window(
    cells_by_key,
    metric_role: str,
    dose_count: int,
    source_form: str,
    window_role: str,
) -> str:
    ordered = [
        cells_by_key[(dose_count, source_form, delay)]
        for delay in _window_delays(window_role)
    ]
    increase = False
    decrease = False
    for first, second in zip(ordered, ordered[1:]):
        tolerance = max(
            _metric_floor(first, metric_role),
            _metric_floor(second, metric_role),
        )
        first_value = _metric_value(first, metric_role)
        second_value = _metric_value(second, metric_role)
        if second_value > first_value + tolerance:
            increase = True
        if first_value > second_value + tolerance:
            decrease = True
    if increase and decrease:
        return "WINDOW_MIXED"
    if increase:
        return "WINDOW_INCREASE"
    if decrease:
        return "WINDOW_DECREASE"
    return "WINDOW_STABLE_WITHIN_FLOOR"


def _window_evaluations(cells_by_key) -> tuple[S1SWindowEvaluation, ...]:
    return tuple(
        S1SWindowEvaluation(
            metric_role=metric_role,
            dose_count=dose,
            source_form=source_form,
            window_role=window_role,
            classification=_classify_window(
                cells_by_key,
                metric_role,
                dose,
                source_form,
                window_role,
            ),
        )
        for metric_role in ("preprobe-mass", "probe-effect")
        for dose in S1R_DOSE_COUNTS
        for source_form in S1R_SOURCE_FORMS
        for window_role in ("early", "late")
    )


def _phase_classification(windows: tuple[S1SWindowEvaluation, ...]) -> str:
    lookup = {
        (item.metric_role, item.dose_count, item.source_form, item.window_role): (
            item.classification
        )
        for item in windows
    }
    mass_early = [
        lookup[("preprobe-mass", dose, source_form, "early")]
        for dose in S1R_DOSE_COUNTS
        for source_form in S1R_SOURCE_FORMS
    ]
    mass_late = [
        lookup[("preprobe-mass", dose, source_form, "late")]
        for dose in S1R_DOSE_COUNTS
        for source_form in S1R_SOURCE_FORMS
    ]
    contains_increase = {"WINDOW_INCREASE", "WINDOW_MIXED"}
    if not any(role in contains_increase for role in mass_early):
        return "NO_EARLY_FORMATION_AT_FIXED_BOUNDARY"
    if any(role in contains_increase for role in mass_late):
        return "FORMATION_EXTENDS_BEYOND_FIXED_BOUNDARY"
    probe_contradiction = any(
        lookup[("probe-effect", dose, source_form, "early")]
        == "WINDOW_DECREASE"
        or lookup[("probe-effect", dose, source_form, "late")]
        == "WINDOW_INCREASE"
        for dose in S1R_DOSE_COUNTS
        for source_form in S1R_SOURCE_FORMS
    )
    if (
        all(role == "WINDOW_INCREASE" for role in mass_early)
        and all(role == "WINDOW_DECREASE" for role in mass_late)
        and not probe_contradiction
    ):
        return "FIXED_BOUNDARY_FORMATION_THEN_ATTENUATION"
    return "MIXED_PHASE_RESPONSE"


def _source_controls_hold() -> bool:
    inventory = s1r_matrix_inventory()
    if len(inventory) != 32 or len({cell.cell_id for cell in inventory}) != 32:
        return False
    for dose in S1R_DOSE_COUNTS:
        repeated = build_s1r_cell_source_contract(
            dose,
            "repeated-supports",
            0.0,
        )
        continuous = build_s1r_cell_source_contract(
            dose,
            "continuous-support",
            0.0,
        )
        if (
            repeated.exposure_invariants.duration_seconds
            != continuous.exposure_invariants.duration_seconds
            or repeated.exposure_invariants.integrated_l1
            != continuous.exposure_invariants.integrated_l1
            or repeated.exposure_invariants.integrated_l2
            != continuous.exposure_invariants.integrated_l2
            or repeated.exposure_digest == repeated.exposure_zero_digest
            or continuous.exposure_digest == continuous.exposure_zero_digest
        ):
            return False
    return True


def _sentinel_null_controls_hold() -> bool:
    for dose in S1R_DOSE_COUNTS:
        for delay in S1R_SENTINEL_DELAYS:
            for model_id in ("eta-null", "p0"):
                result = run_s1r_matrix_cell(
                    model_id,
                    dose,
                    "repeated-supports",
                    delay,
                    4,
                )
                if result.probe_effect_linf != 0.0:
                    return False
            neutral = run_s1r_matrix_cell(
                "f3",
                dose,
                "repeated-supports",
                delay,
                4,
                m_neutralized=True,
            )
            if (
                neutral.preprobe_mass_linf != 0.0
                or neutral.probe_effect_linf != 0.0
            ):
                return False
    return True


@lru_cache(maxsize=1)
def evaluate_s1s_phase_separation_matrix() -> S1SPhaseSeparationEvaluation:
    """Execute and passively classify the fixed S1-Q in-memory matrix."""

    measurements = {}
    cell_evaluations = []
    for cell in s1r_matrix_inventory():
        key = _cell_key(cell)
        f3_r2 = run_s1r_matrix_cell("f3", *key, 2)
        f3_r4 = run_s1r_matrix_cell("f3", *key, 4)
        linear = run_s1r_matrix_cell("linear-coupled-field", *key, 4)
        measurements[key] = (f3_r2, f3_r4, linear)
        cell_evaluations.append(
            _cell_evaluation(cell, f3_r2, f3_r4, linear)
        )

    cells = tuple(cell_evaluations)
    cells_by_key = {_cell_key(cell.cell): cell for cell in cells}
    source_controls_hold = _source_controls_hold()
    alignment_controls_hold = all(
        _alignment_holds(measurement)
        for group in measurements.values()
        for measurement in group
    )
    mass_controls_hold = all(
        _mass_holds(state)
        for group in measurements.values()
        for measurement in group
        for state in _states(measurement)
    )
    sentinel_null_controls_hold = _sentinel_null_controls_hold()
    repeat_key = (8, "continuous-support", 1.6)
    repeated = run_s1r_matrix_cell("f3", *repeat_key, 4)
    reference = measurements[repeat_key][1]
    repeatability_control_holds = repeated == reference
    finite_metrics_hold = all(
        math.isfinite(value) and value >= 0.0
        for cell in cells
        for value in (
            cell.f3_preprobe_mass_linf,
            cell.f3_probe_effect_linf,
            cell.mass_refinement_2_4_linf,
            cell.probe_refinement_2_4_linf,
            cell.mass_detection_floor,
            cell.probe_detection_floor,
            cell.mass_linear_relative_residual,
            cell.probe_linear_relative_residual,
        )
    )
    all_controls_hold = all(
        (
            source_controls_hold,
            alignment_controls_hold,
            mass_controls_hold,
            sentinel_null_controls_hold,
            repeatability_control_holds,
            finite_metrics_hold,
        )
    )
    windows = _window_evaluations(cells_by_key)
    detected_mass = tuple(cell for cell in cells if cell.mass_detected)
    detected_probe = tuple(cell for cell in cells if cell.probe_detected)
    maximum_mass_residual = max(
        (cell.mass_linear_relative_residual for cell in detected_mass),
        default=0.0,
    )
    maximum_probe_residual = max(
        (cell.probe_linear_relative_residual for cell in detected_probe),
        default=0.0,
    )
    if all_controls_hold:
        phase_classification = _phase_classification(windows)
        mechanism_classification = (
            "PHASE_CURVES_LINEARLY_EXPLAINED"
            if max(maximum_mass_residual, maximum_probe_residual)
            <= S1L_LINEAR_EQUIVALENCE_LIMIT
            else "PHASE_CURVE_CONTAINS_BASELINE_DIFFERENT_CELL"
        )
    else:
        phase_classification = "TECHNICALLY_INVALID"
        mechanism_classification = "TECHNICALLY_INVALID"

    return S1SPhaseSeparationEvaluation(
        cells=cells,
        windows=windows,
        source_controls_hold=source_controls_hold,
        alignment_controls_hold=alignment_controls_hold,
        mass_controls_hold=mass_controls_hold,
        sentinel_null_controls_hold=sentinel_null_controls_hold,
        repeatability_control_holds=repeatability_control_holds,
        finite_metrics_hold=finite_metrics_hold,
        all_controls_hold=all_controls_hold,
        detected_mass_cell_count=len(detected_mass),
        detected_probe_cell_count=len(detected_probe),
        maximum_mass_linear_relative_residual=maximum_mass_residual,
        maximum_probe_linear_relative_residual=maximum_probe_residual,
        phase_classification=phase_classification,
        mechanism_classification=mechanism_classification,
    )


def s1s_phase_separation_evaluation_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            S1SCellEvaluation,
            S1SWindowEvaluation,
            S1SPhaseSeparationEvaluation,
        )
        for item in fields(cls)
    )
