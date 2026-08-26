"""Targeted 2/4/8 replication of S1-W baseline-different components."""

from __future__ import annotations

from dataclasses import dataclass, fields
from functools import lru_cache
import math

from .s1l_f3_history_function_adapter import (
    S1L_ABSOLUTE_FLOOR,
    S1L_LINEAR_EQUIVALENCE_LIMIT,
)
from .s1u_f3_component_observer import (
    run_s1u_component_cell,
    run_s1u_component_late_interval,
)
from .s1w_component_matrix_evaluator import evaluate_s1w_component_matrix


class S1XComponentResidualReplicationError(ValueError):
    """Raised when targeted S1-X replication leaves the S1-W selection."""


@dataclass(frozen=True, slots=True)
class S1XReplicationTarget:
    target_id: str
    ledger_id: str
    component_role: str
    dose_count: int
    source_form: str
    ledger_role: str
    start_seconds: float
    end_seconds: float
    s1w_relative_residual_r4: float


@dataclass(frozen=True, slots=True)
class S1XTargetReplication:
    target: S1XReplicationTarget
    relative_residual_r4: float
    relative_residual_r8: float
    component_detection_floor_4_8: float
    f3_difference_2_4: float
    f3_difference_4_8: float
    linear_difference_2_4: float
    linear_difference_4_8: float
    total_mass_difference_r8: float
    component_difference_r8: float
    total_to_component_difference_ratio: float
    maximum_closure_linf: float
    all_ledgers_transparent: bool
    ordered_convergence: bool
    replicated_above_limit: bool


@dataclass(frozen=True, slots=True)
class S1XComponentResidualReplication:
    targets: tuple[S1XReplicationTarget, ...]
    replications: tuple[S1XTargetReplication, ...]
    deterministic_selection_holds: bool
    recomputation_control_holds: bool
    balance_controls_hold: bool
    observer_transparency_holds: bool
    repeatability_control_holds: bool
    finite_metrics_hold: bool
    all_controls_hold: bool
    selected_target_count: int
    replicated_target_count: int
    maximum_relative_residual_r8: float
    maximum_total_to_component_difference_ratio: float
    classification: str
    raw_payload_retained: bool = False
    runtime_writeback_allowed: bool = False
    formal_research_run: bool = False
    memory_claim_allowed: bool = False
    learning_claim_allowed: bool = False
    field_time_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False


def _difference_linf(first, second) -> float:
    return max(
        (
            abs(left - right)
            for left, right in zip(first, second, strict=True)
        ),
        default=0.0,
    )


def _linf(vector) -> float:
    return max((abs(value) for value in vector), default=0.0)


def _component_vector(ledger, role: str):
    if role == "transport":
        return ledger.delta_transport
    return ledger.delta_activation_forcing


def _run_target(target: S1XReplicationTarget, model_id: str, refinement: int):
    if target.ledger_role == "early-cumulative":
        return run_s1u_component_cell(
            model_id,
            target.dose_count,
            target.source_form,
            target.end_seconds,
            refinement,
        )
    return run_s1u_component_late_interval(
        model_id,
        target.dose_count,
        target.source_form,
        target.start_seconds,
        target.end_seconds,
        refinement,
    )


def _targets(s1w_result) -> tuple[S1XReplicationTarget, ...]:
    values = []
    for cell in s1w_result.cells:
        roles = (
            ("transport", cell.transport_linear_relative_residual),
            (
                "activation-forcing",
                cell.activation_forcing_linear_relative_residual,
            ),
        )
        for role, residual in roles:
            if residual > S1L_LINEAR_EQUIVALENCE_LIMIT:
                contract = cell.cell
                values.append(
                    S1XReplicationTarget(
                        target_id=f"{contract.ledger_id}.{role}",
                        ledger_id=contract.ledger_id,
                        component_role=role,
                        dose_count=contract.dose_count,
                        source_form=contract.source_form,
                        ledger_role=contract.ledger_role,
                        start_seconds=contract.start_seconds,
                        end_seconds=contract.end_seconds,
                        s1w_relative_residual_r4=residual,
                    )
                )
    return tuple(values)


def _replicate_target(target: S1XReplicationTarget) -> S1XTargetReplication:
    measurements = {
        (model_id, refinement): _run_target(target, model_id, refinement)
        for model_id in ("f3", "linear-coupled-field")
        for refinement in (2, 4, 8)
    }
    f3_vectors = {
        refinement: _component_vector(
            measurements[("f3", refinement)],
            target.component_role,
        )
        for refinement in (2, 4, 8)
    }
    linear_vectors = {
        refinement: _component_vector(
            measurements[("linear-coupled-field", refinement)],
            target.component_role,
        )
        for refinement in (2, 4, 8)
    }
    f3_difference_2_4 = _difference_linf(f3_vectors[2], f3_vectors[4])
    f3_difference_4_8 = _difference_linf(f3_vectors[4], f3_vectors[8])
    linear_difference_2_4 = _difference_linf(
        linear_vectors[2],
        linear_vectors[4],
    )
    linear_difference_4_8 = _difference_linf(
        linear_vectors[4],
        linear_vectors[8],
    )
    floor_r4 = max(S1L_ABSOLUTE_FLOOR, 8.0 * f3_difference_2_4)
    floor_r8 = max(S1L_ABSOLUTE_FLOOR, 8.0 * f3_difference_4_8)
    component_difference_r4 = _difference_linf(
        f3_vectors[4],
        linear_vectors[4],
    )
    component_difference_r8 = _difference_linf(
        f3_vectors[8],
        linear_vectors[8],
    )
    residual_r4 = component_difference_r4 / max(
        _linf(f3_vectors[4]),
        floor_r4,
    )
    residual_r8 = component_difference_r8 / max(
        _linf(f3_vectors[8]),
        floor_r8,
    )
    total_mass_difference_r8 = _difference_linf(
        measurements[("f3", 8)].delta_mass,
        measurements[("linear-coupled-field", 8)].delta_mass,
    )
    ratio = total_mass_difference_r8 / max(
        component_difference_r8,
        S1L_ABSOLUTE_FLOOR,
    )
    ledgers = tuple(measurements.values())
    ordered_convergence = bool(
        f3_difference_4_8 <= f3_difference_2_4
        and linear_difference_4_8 <= linear_difference_2_4
    )
    replicated = bool(
        residual_r8 > S1L_LINEAR_EQUIVALENCE_LIMIT
        and _linf(f3_vectors[8]) > floor_r8
        and ordered_convergence
    )
    return S1XTargetReplication(
        target=target,
        relative_residual_r4=residual_r4,
        relative_residual_r8=residual_r8,
        component_detection_floor_4_8=floor_r8,
        f3_difference_2_4=f3_difference_2_4,
        f3_difference_4_8=f3_difference_4_8,
        linear_difference_2_4=linear_difference_2_4,
        linear_difference_4_8=linear_difference_4_8,
        total_mass_difference_r8=total_mass_difference_r8,
        component_difference_r8=component_difference_r8,
        total_to_component_difference_ratio=ratio,
        maximum_closure_linf=max(ledger.closure_linf for ledger in ledgers),
        all_ledgers_transparent=all(
            ledger.observer_transparent for ledger in ledgers
        ),
        ordered_convergence=ordered_convergence,
        replicated_above_limit=replicated,
    )


@lru_cache(maxsize=1)
def evaluate_s1x_component_residual_replication(
) -> S1XComponentResidualReplication:
    """Locate S1-W hits and replicate only those at refinement 2/4/8."""

    s1w_result = evaluate_s1w_component_matrix()
    targets = _targets(s1w_result)
    replications = tuple(_replicate_target(target) for target in targets)
    deterministic_selection_holds = bool(
        targets
        and len({target.target_id for target in targets}) == len(targets)
        and all(
            target.s1w_relative_residual_r4
            > S1L_LINEAR_EQUIVALENCE_LIMIT
            for target in targets
        )
    )
    recomputation_control_holds = all(
        replication.relative_residual_r4
        == replication.target.s1w_relative_residual_r4
        for replication in replications
    )
    balance_controls_hold = all(
        replication.maximum_closure_linf <= 1e-12
        for replication in replications
    )
    observer_transparency_holds = all(
        replication.all_ledgers_transparent
        for replication in replications
    )
    if replications:
        repeated = _replicate_target(targets[-1])
        repeatability_control_holds = repeated == replications[-1]
    else:
        repeatability_control_holds = False
    finite_metrics_hold = all(
        math.isfinite(value) and value >= 0.0
        for replication in replications
        for value in (
            replication.relative_residual_r4,
            replication.relative_residual_r8,
            replication.component_detection_floor_4_8,
            replication.f3_difference_2_4,
            replication.f3_difference_4_8,
            replication.linear_difference_2_4,
            replication.linear_difference_4_8,
            replication.total_mass_difference_r8,
            replication.component_difference_r8,
            replication.total_to_component_difference_ratio,
            replication.maximum_closure_linf,
        )
    )
    all_controls_hold = all(
        (
            s1w_result.all_controls_hold,
            deterministic_selection_holds,
            recomputation_control_holds,
            balance_controls_hold,
            observer_transparency_holds,
            repeatability_control_holds,
            finite_metrics_hold,
        )
    )
    replicated_count = sum(
        replication.replicated_above_limit
        for replication in replications
    )
    if not all_controls_hold:
        classification = "TECHNICALLY_INVALID"
    elif replicated_count == len(replications):
        classification = "COMPONENT_REST_REPLICATED_AT_4_8"
    elif replicated_count == 0:
        classification = "COMPONENT_REST_NOT_REPLICATED_AT_4_8"
    else:
        classification = "COMPONENT_REST_PARTIALLY_REPLICATED_AT_4_8"
    return S1XComponentResidualReplication(
        targets=targets,
        replications=replications,
        deterministic_selection_holds=deterministic_selection_holds,
        recomputation_control_holds=recomputation_control_holds,
        balance_controls_hold=balance_controls_hold,
        observer_transparency_holds=observer_transparency_holds,
        repeatability_control_holds=repeatability_control_holds,
        finite_metrics_hold=finite_metrics_hold,
        all_controls_hold=all_controls_hold,
        selected_target_count=len(targets),
        replicated_target_count=replicated_count,
        maximum_relative_residual_r8=max(
            (
                replication.relative_residual_r8
                for replication in replications
            ),
            default=0.0,
        ),
        maximum_total_to_component_difference_ratio=max(
            (
                replication.total_to_component_difference_ratio
                for replication in replications
            ),
            default=0.0,
        ),
        classification=classification,
    )


def s1x_component_residual_replication_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            S1XReplicationTarget,
            S1XTargetReplication,
            S1XComponentResidualReplication,
        )
        for item in fields(cls)
    )
