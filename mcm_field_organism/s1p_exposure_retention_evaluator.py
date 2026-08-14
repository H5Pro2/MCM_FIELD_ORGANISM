"""Bounded passive evaluator for the complete preregistered S1-N matrix."""

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
from .s1o_exposure_retention_matrix import (
    S1O_DELAY_SECONDS,
    S1O_DOSE_COUNTS,
    S1O_SOURCE_FORMS,
    S1OCellMeasurement,
    S1OMatrixCellContract,
    build_s1o_cell_source_contract,
    run_s1o_matrix_cell,
    s1o_matrix_inventory,
)


class S1PExposureRetentionEvaluationError(ValueError):
    """Raised when the bounded S1-P matrix loses a preregistered control."""


@dataclass(frozen=True, slots=True)
class S1PCellEvaluation:
    cell: S1OMatrixCellContract
    f3_effect_linf: float
    linear_effect_linf: float
    refinement_2_4_linf: float
    convergence_floor: float
    detection_floor: float
    linear_relative_residual: float
    effect_detected: bool


@dataclass(frozen=True, slots=True)
class S1PErhaltungshorizon:
    dose_count: int
    source_form: str
    largest_detected_delay_seconds: float | None
    right_censored: bool


@dataclass(frozen=True, slots=True)
class S1PExposureRetentionEvaluation:
    cells: tuple[S1PCellEvaluation, ...]
    erhaltungshorizons: tuple[S1PErhaltungshorizon, ...]
    source_controls_hold: bool
    alignment_controls_hold: bool
    mass_controls_hold: bool
    sentinel_null_controls_hold: bool
    repeatability_control_holds: bool
    finite_metrics_hold: bool
    all_controls_hold: bool
    detected_cell_count: int
    maximum_linear_relative_residual: float
    maximum_segmentation_effect_vector_linf: float
    dose_classification: str
    attenuation_classification: str
    segmentation_classification: str
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


def _states(measurement: S1OCellMeasurement):
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


def _alignment_holds(measurement: S1OCellMeasurement) -> bool:
    zero = (0.0,) * 26
    return all(
        state.activation == zero and state.afterimage == zero
        for state in (
            measurement.exposed_preprobe,
            measurement.zero_preprobe,
        )
    )


def _cell_key(cell: S1OMatrixCellContract):
    return cell.dose_count, cell.source_form, cell.delay_seconds


def _cell_evaluation(
    cell: S1OMatrixCellContract,
    f3_r2: S1OCellMeasurement,
    f3_r4: S1OCellMeasurement,
    linear: S1OCellMeasurement,
) -> S1PCellEvaluation:
    refinement_difference = _difference_linf(
        f3_r2.effect_vector,
        f3_r4.effect_vector,
    )
    convergence_floor = 8.0 * refinement_difference
    detection_floor = max(S1L_ABSOLUTE_FLOOR, convergence_floor)
    f3_effect = f3_r4.effect_linf
    linear_effect = linear.effect_linf
    linear_residual = _difference_linf(
        f3_r4.effect_vector,
        linear.effect_vector,
    ) / max(f3_effect, detection_floor)
    return S1PCellEvaluation(
        cell=cell,
        f3_effect_linf=f3_effect,
        linear_effect_linf=linear_effect,
        refinement_2_4_linf=refinement_difference,
        convergence_floor=convergence_floor,
        detection_floor=detection_floor,
        linear_relative_residual=linear_residual,
        effect_detected=f3_effect > detection_floor,
    )


def _dose_classification(cells_by_key) -> str:
    zero_delay = [
        cells_by_key[(dose, source_form, 0.0)]
        for source_form in S1O_SOURCE_FORMS
        for dose in S1O_DOSE_COUNTS
    ]
    if not any(cell.effect_detected for cell in zero_delay):
        return "NO_DOSE_CONDITIONED_EFFECT"
    monotonic = True
    strict = False
    for source_form in S1O_SOURCE_FORMS:
        ordered = [
            cells_by_key[(dose, source_form, 0.0)]
            for dose in S1O_DOSE_COUNTS
        ]
        for first, second in zip(ordered, ordered[1:]):
            tolerance = max(first.detection_floor, second.detection_floor)
            if second.f3_effect_linf + tolerance < first.f3_effect_linf:
                monotonic = False
            if second.f3_effect_linf > first.f3_effect_linf + tolerance:
                strict = True
    if monotonic and strict:
        return "MONOTONIC_DOSE_GRADATION"
    return "TECHNICAL_EFFECT_WITHOUT_DOSE_ORDER"


def _attenuation_classification(cells_by_key) -> str:
    zero_delay = [
        cells_by_key[(dose, source_form, 0.0)]
        for dose in S1O_DOSE_COUNTS
        for source_form in S1O_SOURCE_FORMS
    ]
    if not any(cell.effect_detected for cell in zero_delay):
        return "NO_DETECTABLE_PRESERVATION"
    for dose in S1O_DOSE_COUNTS:
        for source_form in S1O_SOURCE_FORMS:
            ordered = [
                cells_by_key[(dose, source_form, delay)]
                for delay in S1O_DELAY_SECONDS
            ]
            for first, second in zip(ordered, ordered[1:]):
                tolerance = max(first.detection_floor, second.detection_floor)
                if second.f3_effect_linf > first.f3_effect_linf + tolerance:
                    return "NONMONOTONIC_NULL_CONTACT_RESPONSE"
    return "MONOTONIC_NULL_CONTACT_ATTENUATION"


def _erhaltungshorizons(cells_by_key):
    values = []
    final_delay = S1O_DELAY_SECONDS[-1]
    for dose in S1O_DOSE_COUNTS:
        for source_form in S1O_SOURCE_FORMS:
            detected_delays = [
                delay
                for delay in S1O_DELAY_SECONDS
                if cells_by_key[(dose, source_form, delay)].effect_detected
            ]
            largest = max(detected_delays) if detected_delays else None
            values.append(
                S1PErhaltungshorizon(
                    dose_count=dose,
                    source_form=source_form,
                    largest_detected_delay_seconds=largest,
                    right_censored=(largest == final_delay),
                )
            )
    return tuple(values)


def _source_controls_hold() -> bool:
    inventory = s1o_matrix_inventory()
    if len(inventory) != 32 or len({cell.cell_id for cell in inventory}) != 32:
        return False
    for dose in S1O_DOSE_COUNTS:
        repeated = build_s1o_cell_source_contract(
            dose,
            "repeated-supports",
            0.0,
        )
        continuous = build_s1o_cell_source_contract(
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
    sentinel_cells = (
        (1, "repeated-supports", 0.0),
        (8, "repeated-supports", 1.6),
        (8, "continuous-support", 0.0),
    )
    for model_id in ("eta-null", "p0"):
        for cell in sentinel_cells:
            if run_s1o_matrix_cell(model_id, *cell, 4).effect_linf != 0.0:
                return False
    for delay in (0.0, 1.6):
        neutral = run_s1o_matrix_cell(
            "f3",
            8,
            "repeated-supports",
            delay,
            4,
            m_neutralized=True,
        )
        if neutral.preprobe_mass_linf != 0.0 or neutral.effect_linf != 0.0:
            return False
    return True


@lru_cache(maxsize=1)
def evaluate_s1p_exposure_retention_matrix(
) -> S1PExposureRetentionEvaluation:
    """Execute and passively classify the fixed complete in-memory matrix."""

    measurements = {}
    cell_evaluations = []
    for cell in s1o_matrix_inventory():
        key = _cell_key(cell)
        f3_r2 = run_s1o_matrix_cell("f3", *key, 2)
        f3_r4 = run_s1o_matrix_cell("f3", *key, 4)
        linear = run_s1o_matrix_cell("linear-coupled-field", *key, 4)
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
    repeat_key = (8, "repeated-supports", 1.6)
    repeated = run_s1o_matrix_cell("f3", *repeat_key, 4)
    reference = measurements[repeat_key][1]
    repeatability_control_holds = (
        repeated.effect_vector == reference.effect_vector
        and repeated.exposed_preprobe.digest()
        == reference.exposed_preprobe.digest()
        and repeated.zero_preprobe.digest() == reference.zero_preprobe.digest()
    )
    finite_metrics_hold = all(
        math.isfinite(value) and value >= 0.0
        for cell in cells
        for value in (
            cell.f3_effect_linf,
            cell.linear_effect_linf,
            cell.refinement_2_4_linf,
            cell.convergence_floor,
            cell.detection_floor,
            cell.linear_relative_residual,
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

    maximum_segmentation = 0.0
    segmentation_within_floor = True
    for dose in S1O_DOSE_COUNTS:
        for delay in S1O_DELAY_SECONDS:
            repeated_measurement = measurements[
                (dose, "repeated-supports", delay)
            ][1]
            continuous_measurement = measurements[
                (dose, "continuous-support", delay)
            ][1]
            difference = _difference_linf(
                repeated_measurement.effect_vector,
                continuous_measurement.effect_vector,
            )
            maximum_segmentation = max(maximum_segmentation, difference)
            tolerance = max(
                cells_by_key[
                    (dose, "repeated-supports", delay)
                ].detection_floor,
                cells_by_key[
                    (dose, "continuous-support", delay)
                ].detection_floor,
            )
            if difference > tolerance:
                segmentation_within_floor = False

    detected_cells = tuple(cell for cell in cells if cell.effect_detected)
    maximum_linear_residual = max(
        (cell.linear_relative_residual for cell in detected_cells),
        default=0.0,
    )
    if all_controls_hold:
        dose_classification = _dose_classification(cells_by_key)
        attenuation_classification = _attenuation_classification(cells_by_key)
        segmentation_classification = (
            "DURATION_EQUIVALENT_WITHIN_FLOOR"
            if segmentation_within_floor
            else "EVENT_SEGMENTATION_SENSITIVE"
        )
        mechanism_classification = (
            "CURVE_LINEARLY_EXPLAINED"
            if maximum_linear_residual <= S1L_LINEAR_EQUIVALENCE_LIMIT
            else "CURVE_CONTAINS_BASELINE_DIFFERENT_CELL"
        )
    else:
        dose_classification = "TECHNICALLY_INVALID"
        attenuation_classification = "TECHNICALLY_INVALID"
        segmentation_classification = "TECHNICALLY_INVALID"
        mechanism_classification = "TECHNICALLY_INVALID"

    return S1PExposureRetentionEvaluation(
        cells=cells,
        erhaltungshorizons=_erhaltungshorizons(cells_by_key),
        source_controls_hold=source_controls_hold,
        alignment_controls_hold=alignment_controls_hold,
        mass_controls_hold=mass_controls_hold,
        sentinel_null_controls_hold=sentinel_null_controls_hold,
        repeatability_control_holds=repeatability_control_holds,
        finite_metrics_hold=finite_metrics_hold,
        all_controls_hold=all_controls_hold,
        detected_cell_count=len(detected_cells),
        maximum_linear_relative_residual=maximum_linear_residual,
        maximum_segmentation_effect_vector_linf=maximum_segmentation,
        dose_classification=dose_classification,
        attenuation_classification=attenuation_classification,
        segmentation_classification=segmentation_classification,
        mechanism_classification=mechanism_classification,
    )


def s1p_exposure_retention_evaluation_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            S1PCellEvaluation,
            S1PErhaltungshorizon,
            S1PExposureRetentionEvaluation,
        )
        for item in fields(cls)
    )
