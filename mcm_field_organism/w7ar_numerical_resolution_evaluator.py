"""W7-AR one-shot numerical evaluation without functional interpretation."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math

from .w7ap_raw_resolution_distance_compositor import (
    W7APRawResolutionDistanceComposition,
)
from .w7aq_numerical_evaluation_contract import (
    W7AQNumericalEvaluationContract,
)


class W7ARNumericalResolutionEvaluationError(ValueError):
    """Raised when W7-AR input or output leaves the W7-AQ contract."""


_EVALUATOR_ID = "w7ar.one-shot-numerical-resolution-evaluator.v1"
_W7AN_CONTAINER_DIGEST = (
    "4f150aad9f5c3803f1432550aa4db79b40aea3f7a4975b49802694fad2fff3e5"
)
_W7AO_CONTRACT_DIGEST = (
    "14455f15e6f3d0f96106aa766ae544ec76f19b5c94308329ec45fd0cd12067dc"
)
_W7AP_COMPOSITOR_ID = (
    "w7ap.raw-r1-r2-r2-r4-resolution-distance-compositor.v1"
)
_W7AQ_CONTRACT_DIGEST = (
    "66717c7bb1947d44253573a275f326944e5d9aa623389b55162b81a5ea886ee3"
)
_PATH_IDS = ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
_ROLES = tuple(
    (path_id, checkpoint)
    for path_id in _PATH_IDS
    for checkpoint in range(5)
)
_METRICS = ("S_linf", "H_linf")
_OUTCOMES = (
    "NUMERICALLY_UNRESOLVED",
    "RESOLUTION_COMPARISON_CONVERGED",
)
_EFFECT_FLOOR_FACTOR = 10.0


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _nonnegative(value: float, role: str) -> float:
    if isinstance(value, bool):
        raise W7ARNumericalResolutionEvaluationError(
            f"{role} must be numeric"
        )
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise W7ARNumericalResolutionEvaluationError(
            f"{role} must be finite and nonnegative"
        )
    return result


def _component_payload(
    path_id: str,
    checkpoint: int,
    metric: str,
    d12: float,
    d24: float,
    exact_zero_exception: bool,
    converged: bool,
) -> dict[str, object]:
    return {
        "path_id": path_id,
        "checkpoint": checkpoint,
        "metric": metric,
        "d12": d12,
        "d24": d24,
        "exact_zero_exception": exact_zero_exception,
        "converged": converged,
    }


@dataclass(frozen=True, slots=True)
class W7ARComponentCheck:
    """One preregistered D24-versus-D12 primary-metric check."""

    path_id: str
    checkpoint: int
    metric: str
    d12: float
    d24: float
    exact_zero_exception: bool
    converged: bool
    component_check_digest: str

    def __post_init__(self) -> None:
        d12 = _nonnegative(self.d12, "D12")
        d24 = _nonnegative(self.d24, "D24")
        exact_zero = d12 == 0.0 and d24 == 0.0
        converged = d24 < d12 or exact_zero
        if (
            (self.path_id, self.checkpoint) not in _ROLES
            or self.metric not in _METRICS
            or self.exact_zero_exception is not exact_zero
            or self.converged is not converged
        ):
            raise W7ARNumericalResolutionEvaluationError(
                "component check binding is invalid"
            )
        payload = _component_payload(
            self.path_id,
            self.checkpoint,
            self.metric,
            d12,
            d24,
            exact_zero,
            converged,
        )
        if self.component_check_digest != _digest(payload):
            raise W7ARNumericalResolutionEvaluationError(
                "component check digest differs"
            )
        object.__setattr__(self, "d12", d12)
        object.__setattr__(self, "d24", d24)


def _build_component_check(
    path_id: str,
    checkpoint: int,
    metric: str,
    d12: float,
    d24: float,
) -> W7ARComponentCheck:
    d12 = _nonnegative(d12, "D12")
    d24 = _nonnegative(d24, "D24")
    exact_zero = d12 == 0.0 and d24 == 0.0
    converged = d24 < d12 or exact_zero
    payload = _component_payload(
        path_id,
        checkpoint,
        metric,
        d12,
        d24,
        exact_zero,
        converged,
    )
    return W7ARComponentCheck(
        path_id,
        checkpoint,
        metric,
        d12,
        d24,
        exact_zero,
        converged,
        _digest(payload),
    )


def _result_payload(
    raw_distance_digest: str,
    checks: tuple[W7ARComponentCheck, ...],
    all_components_converged: bool,
    epsilon_num: float | None,
    effect_floor: float | None,
    outcome: str,
) -> dict[str, object]:
    return {
        "evaluator_id": _EVALUATOR_ID,
        "w7aq_contract_digest": _W7AQ_CONTRACT_DIGEST,
        "raw_resolution_distance_composition_digest": raw_distance_digest,
        "component_check_digests": tuple(
            item.component_check_digest for item in checks
        ),
        "all_components_converged": all_components_converged,
        "epsilon_num": epsilon_num,
        "effect_floor": effect_floor,
        "outcome": outcome,
        "field_function_decision_allowed": False,
        "memory_claim_allowed": False,
    }


@dataclass(frozen=True, slots=True)
class W7ARNumericalResolutionEvaluation:
    """Complete numerical result with all functional claims locked."""

    evaluator_id: str
    w7aq_contract_digest: str
    raw_resolution_distance_composition_digest: str
    component_checks: tuple[W7ARComponentCheck, ...] = field(repr=False)
    all_components_converged: bool
    epsilon_num: float | None
    effect_floor: float | None
    outcome: str
    field_function_decision_allowed: bool
    memory_claim_allowed: bool
    evaluation_result_digest: str

    def __post_init__(self) -> None:
        checks = tuple(self.component_checks)
        expected_roles = tuple(
            (path_id, checkpoint, metric)
            for path_id, checkpoint in _ROLES
            for metric in _METRICS
        )
        convergence = all(item.converged for item in checks)
        if (
            self.evaluator_id != _EVALUATOR_ID
            or self.w7aq_contract_digest != _W7AQ_CONTRACT_DIGEST
            or not self.raw_resolution_distance_composition_digest
            or tuple(
                (item.path_id, item.checkpoint, item.metric)
                for item in checks
            )
            != expected_roles
            or self.all_components_converged is not convergence
            or self.outcome not in _OUTCOMES
            or self.field_function_decision_allowed is not False
            or self.memory_claim_allowed is not False
        ):
            raise W7ARNumericalResolutionEvaluationError(
                "numerical evaluation binding is invalid"
            )
        if convergence:
            expected_epsilon = max(item.d24 for item in checks)
            expected_floor = _EFFECT_FLOOR_FACTOR * expected_epsilon
            epsilon = _nonnegative(self.epsilon_num, "epsilon_num")
            effect_floor = _nonnegative(self.effect_floor, "effect_floor")
            if (
                self.outcome != "RESOLUTION_COMPARISON_CONVERGED"
                or epsilon != expected_epsilon
                or effect_floor != expected_floor
            ):
                raise W7ARNumericalResolutionEvaluationError(
                    "converged numerical result differs"
                )
        else:
            epsilon = None
            effect_floor = None
            if (
                self.outcome != "NUMERICALLY_UNRESOLVED"
                or self.epsilon_num is not None
                or self.effect_floor is not None
            ):
                raise W7ARNumericalResolutionEvaluationError(
                    "unresolved result must not expose numerical floors"
                )
        payload = _result_payload(
            self.raw_resolution_distance_composition_digest,
            checks,
            convergence,
            epsilon,
            effect_floor,
            self.outcome,
        )
        if self.evaluation_result_digest != _digest(payload):
            raise W7ARNumericalResolutionEvaluationError(
                "numerical evaluation digest differs"
            )
        object.__setattr__(self, "component_checks", checks)
        object.__setattr__(self, "epsilon_num", epsilon)
        object.__setattr__(self, "effect_floor", effect_floor)


def evaluate_w7ar_numerical_resolution(
    composition: W7APRawResolutionDistanceComposition,
    contract: W7AQNumericalEvaluationContract,
) -> W7ARNumericalResolutionEvaluation:
    """Evaluate one complete W7-AP composition exactly once as a whole."""

    if not isinstance(
        composition,
        W7APRawResolutionDistanceComposition,
    ) or not isinstance(contract, W7AQNumericalEvaluationContract):
        raise W7ARNumericalResolutionEvaluationError(
            "W7-AR requires W7-AP and W7-AQ inputs"
        )
    if (
        composition.compositor_id != _W7AP_COMPOSITOR_ID
        or composition.w7an_container_digest != _W7AN_CONTAINER_DIGEST
        or composition.w7ao_contract_digest != _W7AO_CONTRACT_DIGEST
        or len(composition.role_distances) != 70
        or len(composition.identity_distances) != 105
        or not composition.identity_countercontrol_digest
        or not composition.order_countercontrol_digest
        or composition.repeat_baseline_bound_to_canonical_w7an is not True
        or composition.convergence_evaluated is not False
        or composition.epsilon_num_ready is not False
        or composition.effect_floor_ready is not False
        or composition.field_function_decision_allowed is not False
        or contract.contract_digest != _W7AQ_CONTRACT_DIGEST
        or contract.required_w7an_container_digest != _W7AN_CONTAINER_DIGEST
        or contract.required_w7ao_contract_digest != _W7AO_CONTRACT_DIGEST
        or contract.required_w7ap_compositor_id != _W7AP_COMPOSITOR_ID
        or contract.accept_result_values is not False
        or contract.field_function_decision_allowed is not False
        or contract.memory_claim_allowed is not False
    ):
        raise W7ARNumericalResolutionEvaluationError(
            "W7-AR input provenance differs"
        )
    input_digest = composition.raw_resolution_distance_composition_digest
    by_role = {
        (item.comparison_id, item.path_id, item.checkpoint): item
        for item in composition.role_distances
    }
    expected = {
        (comparison_id, path_id, checkpoint)
        for comparison_id in ("r1-r2", "r2-r4")
        for path_id, checkpoint in _ROLES
    }
    if set(by_role) != expected:
        raise W7ARNumericalResolutionEvaluationError(
            "W7-AR distance role inventory differs"
        )
    if any(
        (item.S_linf, item.H_linf, item.SH_l2) != (0.0, 0.0, 0.0)
        for item in composition.identity_distances
    ):
        raise W7ARNumericalResolutionEvaluationError(
            "W7-AR identity countercontrol differs"
        )

    checks = tuple(
        _build_component_check(
            path_id,
            checkpoint,
            metric,
            getattr(by_role[("r1-r2", path_id, checkpoint)], metric),
            getattr(by_role[("r2-r4", path_id, checkpoint)], metric),
        )
        for path_id, checkpoint in _ROLES
        for metric in _METRICS
    )
    all_converged = all(item.converged for item in checks)
    if all_converged:
        epsilon_num = max(item.d24 for item in checks)
        effect_floor = _EFFECT_FLOOR_FACTOR * epsilon_num
        outcome = "RESOLUTION_COMPARISON_CONVERGED"
    else:
        epsilon_num = None
        effect_floor = None
        outcome = "NUMERICALLY_UNRESOLVED"
    if composition.raw_resolution_distance_composition_digest != input_digest:
        raise W7ARNumericalResolutionEvaluationError(
            "W7-AR mutated its W7-AP input"
        )
    payload = _result_payload(
        input_digest,
        checks,
        all_converged,
        epsilon_num,
        effect_floor,
        outcome,
    )
    return W7ARNumericalResolutionEvaluation(
        _EVALUATOR_ID,
        _W7AQ_CONTRACT_DIGEST,
        input_digest,
        checks,
        all_converged,
        epsilon_num,
        effect_floor,
        outcome,
        False,
        False,
        _digest(payload),
    )
