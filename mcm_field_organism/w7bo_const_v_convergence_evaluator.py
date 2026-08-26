"""Private numerical CONST-V R1/R2/R4 evaluator without interpretation."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math

from .w7bl_const_v_seven_path_gate import W7BLConstVSevenPathGate
from .w7bm_const_v_seven_path_executor import W7BMConstVSevenPathRole
from .w7bj_const_v_r4_convergence_contract import W7BJConstVR4ConvergenceContract


class W7BOConstVConvergenceEvaluatorError(ValueError):
    """Raised when numerical CONST-V comparison inputs are incomplete."""


_EVALUATOR_ID = "w7bo.const-v-r1-r2-r4-convergence-evaluator.v1"
_PATH_IDS = ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
_REFINEMENTS = (1, 2, 4)
_METRICS = ("s", "h")
_CHECKPOINTS = range(5)


def _digest(payload: object) -> str:
    encoded = json.dumps(payload, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _distance(left_measurement, right_measurement, metric: str) -> float:
    if len(left_measurement.samples) != len(right_measurement.samples):
        raise W7BOConstVConvergenceEvaluatorError("sample inventory differs")
    values = []
    for left_sample, right_sample in zip(left_measurement.samples, right_measurement.samples, strict=True):
        if left_sample.tick != right_sample.tick:
            raise W7BOConstVConvergenceEvaluatorError("sample ticks differ")
        left_values = left_sample.s_values if metric == "s" else left_sample.h_values
        right_values = right_sample.s_values if metric == "s" else right_sample.h_values
        if len(left_values) != len(right_values):
            raise W7BOConstVConvergenceEvaluatorError("sample geometry differs")
        values.extend(abs(a - b) for a, b in zip(left_values, right_values, strict=True))
    if not values or any(not math.isfinite(value) for value in values):
        raise W7BOConstVConvergenceEvaluatorError("distance values are invalid")
    return max(values)


@dataclass(frozen=True, slots=True)
class W7BOComponentCheck:
    path_id: str
    checkpoint: int
    metric: str
    d12: float
    d24: float
    exact_zero_exception: bool
    converged: bool
    component_digest: str

    def __post_init__(self) -> None:
        exact_zero = self.d12 == 0.0 and self.d24 == 0.0
        if (
            self.path_id not in _PATH_IDS
            or self.checkpoint not in _CHECKPOINTS
            or self.metric not in _METRICS
            or not math.isfinite(self.d12)
            or not math.isfinite(self.d24)
            or self.d12 < 0.0
            or self.d24 < 0.0
            or self.exact_zero_exception is not exact_zero
            or self.converged is not (self.d24 < self.d12 or exact_zero)
        ):
            raise W7BOConstVConvergenceEvaluatorError("component check differs")
        payload = {
            "path_id": self.path_id,
            "checkpoint": self.checkpoint,
            "metric": self.metric,
            "d12": self.d12,
            "d24": self.d24,
            "exact_zero_exception": exact_zero,
            "converged": self.converged,
        }
        if self.component_digest != _digest(payload):
            raise W7BOConstVConvergenceEvaluatorError("component digest differs")


@dataclass(frozen=True, slots=True)
class W7BOConstVConvergenceResult:
    evaluator_id: str
    contract_digest: str
    gate_digest: str
    components: tuple[W7BOComponentCheck, ...] = field(repr=False)
    all_components_converged: bool
    epsilon: float | None
    effect_floor: float | None
    outcome: str
    field_function_decision_allowed: bool
    memory_claim_allowed: bool
    result_digest: str

    def __post_init__(self) -> None:
        components = tuple(self.components)
        expected = tuple(
            (path_id, checkpoint, metric)
            for path_id in _PATH_IDS
            for checkpoint in _CHECKPOINTS
            for metric in _METRICS
        )
        converged = all(item.converged for item in components)
        if (
            self.evaluator_id != _EVALUATOR_ID
            or tuple((item.path_id, item.checkpoint, item.metric) for item in components) != expected
            or self.all_components_converged is not converged
            or self.field_function_decision_allowed
            or self.memory_claim_allowed
        ):
            raise W7BOConstVConvergenceEvaluatorError("result binding differs")
        if converged:
            epsilon = max(item.d24 for item in components)
            if self.epsilon != epsilon or self.effect_floor != 10.0 * epsilon:
                raise W7BOConstVConvergenceEvaluatorError("converged threshold differs")
            if self.outcome != "RESOLUTION_COMPARISON_CONVERGED":
                raise W7BOConstVConvergenceEvaluatorError("converged outcome differs")
        else:
            if self.epsilon is not None or self.effect_floor is not None or self.outcome != "NUMERICALLY_UNRESOLVED":
                raise W7BOConstVConvergenceEvaluatorError("unresolved outcome differs")
        payload = {
            "evaluator_id": _EVALUATOR_ID,
            "contract_digest": self.contract_digest,
            "gate_digest": self.gate_digest,
            "component_digests": tuple(item.component_digest for item in components),
            "all_components_converged": converged,
            "epsilon": self.epsilon,
            "effect_floor": self.effect_floor,
            "outcome": self.outcome,
            "field_function_decision_allowed": False,
            "memory_claim_allowed": False,
        }
        if self.result_digest != _digest(payload):
            raise W7BOConstVConvergenceEvaluatorError("result digest differs")
        object.__setattr__(self, "components", components)


def evaluate_w7bo_const_v_convergence(
    roles: tuple[W7BMConstVSevenPathRole, ...],
    contract: W7BJConstVR4ConvergenceContract,
    gate: W7BLConstVSevenPathGate,
) -> W7BOConstVConvergenceResult:
    """Evaluate the 70 preregistered S/H comparisons only."""

    roles = tuple(roles)
    expected = tuple(
        (path_id, refinement)
        for refinement in _REFINEMENTS
        for path_id in _PATH_IDS
    )
    if (
        not isinstance(contract, W7BJConstVR4ConvergenceContract)
        or not isinstance(gate, W7BLConstVSevenPathGate)
        or gate.contract_digest != contract.contract_digest
        or len(roles) != 21
        or tuple((item.path_id, item.refinement) for item in roles) != expected
    ):
        raise W7BOConstVConvergenceEvaluatorError("W7-BN role inventory differs")
    by_key = {(item.path_id, item.refinement): item for item in roles}
    components = []
    for path_id in _PATH_IDS:
        r1, r2, r4 = (by_key[(path_id, refinement)] for refinement in _REFINEMENTS)
        for checkpoint in _CHECKPOINTS:
            for metric in _METRICS:
                d12 = _distance(r1.measurements[checkpoint], r2.measurements[checkpoint], metric)
                d24 = _distance(r2.measurements[checkpoint], r4.measurements[checkpoint], metric)
                exact_zero = d12 == 0.0 and d24 == 0.0
                payload = {
                    "path_id": path_id,
                    "checkpoint": checkpoint,
                    "metric": metric,
                    "d12": d12,
                    "d24": d24,
                    "exact_zero_exception": exact_zero,
                    "converged": d24 < d12 or exact_zero,
                }
                components.append(W7BOComponentCheck(path_id, checkpoint, metric, d12, d24, exact_zero, d24 < d12 or exact_zero, _digest(payload)))
    components_out = tuple(components)
    all_converged = all(item.converged for item in components_out)
    epsilon = max(item.d24 for item in components_out) if all_converged else None
    effect_floor = 10.0 * epsilon if epsilon is not None else None
    outcome = "RESOLUTION_COMPARISON_CONVERGED" if all_converged else "NUMERICALLY_UNRESOLVED"
    payload = {
        "evaluator_id": _EVALUATOR_ID,
        "contract_digest": contract.contract_digest,
        "gate_digest": gate.gate_digest,
        "component_digests": tuple(item.component_digest for item in components_out),
        "all_components_converged": all_converged,
        "epsilon": epsilon,
        "effect_floor": effect_floor,
        "outcome": outcome,
        "field_function_decision_allowed": False,
        "memory_claim_allowed": False,
    }
    return W7BOConstVConvergenceResult(
        _EVALUATOR_ID,
        contract.contract_digest,
        gate.gate_digest,
        components_out,
        all_converged,
        epsilon,
        effect_floor,
        outcome,
        False,
        False,
        _digest(payload),
    )
