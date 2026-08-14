"""Passive evaluator for the preregistered S1-K in-memory measurements."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math

from .s1l_f3_history_function_adapter import (
    S1L_ABSOLUTE_FLOOR,
    S1L_LINEAR_EQUIVALENCE_LIMIT,
    S1L_MASS_TOLERANCE,
    S1LFieldState,
    S1LModelPairMeasurement,
    build_s1l_source_contract,
    run_s1l_model_pair,
    run_s1l_rebind_control,
)


class S1MF3HistoryFunctionEvaluationError(ValueError):
    """Raised when S1-M receives an incomplete technical measurement set."""


@dataclass(frozen=True, slots=True)
class S1MF3HistoryFunctionEvaluation:
    """One passive preregistered classification without runtime authority."""

    f3_effect_linf: float
    linear_effect_linf: float
    refinement_1_2_linf: float
    refinement_2_4_linf: float
    convergence_floor: float
    detection_floor: float
    linear_relative_residual: float
    source_controls_hold: bool
    fast_alignment_controls_hold: bool
    null_controls_hold: bool
    mass_controls_hold: bool
    repeatability_control_holds: bool
    rebind_control_holds: bool
    all_controls_hold: bool
    effect_detected: bool
    linear_equivalent: bool
    classification: str
    raw_payload_retained: bool = False
    runtime_writeback_allowed: bool = False
    formal_research_run: bool = False
    memory_claim_allowed: bool = False
    learning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    topology_claim_allowed: bool = False
    semantics_claim_allowed: bool = False
    ai_claim_allowed: bool = False


_CLASSIFICATIONS = {
    "NO_TECHNICAL_HISTORY_EFFECT",
    "TRANSPARENT_HISTORY_EFFECT_LINEARLY_EXPLAINED",
    "TRANSPARENT_HISTORY_EFFECT_BASELINE_DIFFERENT",
    "TECHNICALLY_INVALID",
}


def _effect_vector(measurement: S1LModelPairMeasurement) -> tuple[float, ...]:
    values = []
    for path_a, path_b in zip(
        measurement.probe_a,
        measurement.probe_b,
        strict=True,
    ):
        values.extend(
            left - right
            for left, right in zip(
                path_a.activation,
                path_b.activation,
                strict=True,
            )
        )
        values.extend(
            left - right
            for left, right in zip(
                path_a.afterimage,
                path_b.afterimage,
                strict=True,
            )
        )
    return tuple(values)


def _linf(values: tuple[float, ...]) -> float:
    return max((abs(value) for value in values), default=0.0)


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


def _fast_alignment_holds(measurements) -> bool:
    zero = (0.0,) * 26
    return all(
        state.activation == zero and state.afterimage == zero
        for measurement in measurements
        for state in (measurement.preprobe_a, measurement.preprobe_b)
    )


def _measurement_states(measurement: S1LModelPairMeasurement):
    return (
        measurement.preprobe_a,
        measurement.preprobe_b,
        *measurement.probe_a,
        *measurement.probe_b,
    )


def _mass_state_holds(state: S1LFieldState) -> bool:
    return (
        state.mass
        and min(state.mass) >= 0.0
        and abs(math.fsum(state.mass) - 1.0) <= S1L_MASS_TOLERANCE
        and all(math.isfinite(value) for value in state.mass)
    )


def _repeatability_holds(
    first: S1LModelPairMeasurement,
    second: S1LModelPairMeasurement,
) -> bool:
    return (
        first.preprobe_a.digest() == second.preprobe_a.digest()
        and first.preprobe_b.digest() == second.preprobe_b.digest()
        and tuple(item.digest() for item in first.probe_a)
        == tuple(item.digest() for item in second.probe_a)
        and tuple(item.digest() for item in first.probe_b)
        == tuple(item.digest() for item in second.probe_b)
    )


def _classification(
    controls_hold: bool,
    effect_detected: bool,
    linear_equivalent: bool,
) -> str:
    if not controls_hold:
        return "TECHNICALLY_INVALID"
    if not effect_detected:
        return "NO_TECHNICAL_HISTORY_EFFECT"
    if linear_equivalent:
        return "TRANSPARENT_HISTORY_EFFECT_LINEARLY_EXPLAINED"
    return "TRANSPARENT_HISTORY_EFFECT_BASELINE_DIFFERENT"


def evaluate_s1m_f3_history_function(
) -> S1MF3HistoryFunctionEvaluation:
    """Evaluate S1-L only through the unchanged S1-K formulas."""

    source = build_s1l_source_contract()
    f3_r1 = run_s1l_model_pair("f3", 1)
    f3_r2 = run_s1l_model_pair("f3", 2)
    f3_r4 = run_s1l_model_pair("f3", 4)
    f3_repeated = run_s1l_model_pair("f3", 4)
    linear = run_s1l_model_pair("linear-coupled-field", 4)
    eta_null = run_s1l_model_pair("eta-null", 4)
    p0 = run_s1l_model_pair("p0", 4)
    neutral = run_s1l_model_pair("f3", 4, neutralized=True)
    rebind = run_s1l_rebind_control(4)

    f3_vector_r1 = _effect_vector(f3_r1)
    f3_vector_r2 = _effect_vector(f3_r2)
    f3_vector_r4 = _effect_vector(f3_r4)
    linear_vector = _effect_vector(linear)
    f3_effect_linf = _linf(f3_vector_r4)
    linear_effect_linf = _linf(linear_vector)
    refinement_1_2_linf = _difference_linf(f3_vector_r1, f3_vector_r2)
    refinement_2_4_linf = _difference_linf(f3_vector_r2, f3_vector_r4)
    convergence_floor = 8.0 * refinement_2_4_linf
    detection_floor = max(S1L_ABSOLUTE_FLOOR, convergence_floor)
    linear_relative_residual = (
        _difference_linf(f3_vector_r4, linear_vector)
        / max(f3_effect_linf, detection_floor)
    )

    measurements = (
        f3_r1,
        f3_r2,
        f3_r4,
        linear,
        eta_null,
        p0,
        neutral,
    )
    source_controls_hold = (
        source.history_a_digest != source.history_b_digest
        and source.history_a_invariants == source.history_b_invariants
    )
    fast_alignment_controls_hold = _fast_alignment_holds(measurements)
    null_controls_hold = (
        eta_null.probe_effect_linf == 0.0
        and p0.probe_effect_linf == 0.0
        and neutral.probe_effect_linf == 0.0
        and neutral.preprobe_mass_linf == 0.0
    )
    mass_controls_hold = all(
        _mass_state_holds(state)
        for measurement in measurements
        for state in _measurement_states(measurement)
    )
    repeatability_control_holds = _repeatability_holds(f3_r4, f3_repeated)
    rebind_control_holds = rebind.maximum_state_linf <= detection_floor
    finite_metrics = all(
        math.isfinite(value) and value >= 0.0
        for value in (
            f3_effect_linf,
            linear_effect_linf,
            refinement_1_2_linf,
            refinement_2_4_linf,
            convergence_floor,
            detection_floor,
            linear_relative_residual,
        )
    )
    all_controls_hold = all(
        (
            source_controls_hold,
            fast_alignment_controls_hold,
            null_controls_hold,
            mass_controls_hold,
            repeatability_control_holds,
            rebind_control_holds,
            finite_metrics,
        )
    )
    effect_detected = f3_effect_linf > detection_floor
    linear_equivalent = (
        linear_relative_residual <= S1L_LINEAR_EQUIVALENCE_LIMIT
    )
    classification = _classification(
        all_controls_hold,
        effect_detected,
        linear_equivalent,
    )
    if classification not in _CLASSIFICATIONS:
        raise S1MF3HistoryFunctionEvaluationError(
            "S1-M produced an unregistered classification"
        )
    return S1MF3HistoryFunctionEvaluation(
        f3_effect_linf=f3_effect_linf,
        linear_effect_linf=linear_effect_linf,
        refinement_1_2_linf=refinement_1_2_linf,
        refinement_2_4_linf=refinement_2_4_linf,
        convergence_floor=convergence_floor,
        detection_floor=detection_floor,
        linear_relative_residual=linear_relative_residual,
        source_controls_hold=source_controls_hold,
        fast_alignment_controls_hold=fast_alignment_controls_hold,
        null_controls_hold=null_controls_hold,
        mass_controls_hold=mass_controls_hold,
        repeatability_control_holds=repeatability_control_holds,
        rebind_control_holds=rebind_control_holds,
        all_controls_hold=all_controls_hold,
        effect_detected=effect_detected,
        linear_equivalent=linear_equivalent,
        classification=classification,
    )


def s1m_f3_history_function_evaluation_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(S1MF3HistoryFunctionEvaluation))
