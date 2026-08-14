"""Static W7-AQ numerical evaluation contract without result values."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json


class W7AQNumericalEvaluationContractError(ValueError):
    """Raised when the W7-AQ preregistration is changed inconsistently."""


_CONTRACT_ID = "w7aq.numerical-resolution-evaluation-contract.v1"
_W7AN_CONTAINER_DIGEST = (
    "4f150aad9f5c3803f1432550aa4db79b40aea3f7a4975b49802694fad2fff3e5"
)
_W7AO_CONTRACT_DIGEST = (
    "14455f15e6f3d0f96106aa766ae544ec76f19b5c94308329ec45fd0cd12067dc"
)
_W7AP_COMPOSITOR_ID = (
    "w7ap.raw-r1-r2-r2-r4-resolution-distance-compositor.v1"
)
_PRIMARY_METRICS = ("S_linf", "H_linf")
_DIAGNOSTIC_METRICS = ("SH_l2",)
_OUTCOMES = (
    "NUMERICALLY_UNRESOLVED",
    "RESOLUTION_COMPARISON_CONVERGED",
)
_RESULT_FIELDS = (
    "contract_digest",
    "raw_resolution_distance_composition_digest",
    "component_check_digests",
    "all_components_converged",
    "epsilon_num",
    "effect_floor",
    "outcome",
    "field_function_decision_allowed",
    "memory_claim_allowed",
    "evaluation_result_digest",
)
_MISSING_FUNCTION_BASELINES = (
    "LEAK",
    "LIN",
    "F3",
    "CONST-V",
    "SAT",
    "MOB",
    "NORM",
    "ETA0",
    "KAPPA0",
    "SIGN",
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


def _payload() -> dict[str, object]:
    return {
        "contract_id": _CONTRACT_ID,
        "required_w7an_container_digest": _W7AN_CONTAINER_DIGEST,
        "required_w7ao_contract_digest": _W7AO_CONTRACT_DIGEST,
        "required_w7ap_compositor_id": _W7AP_COMPOSITOR_ID,
        "role_count": 35,
        "distance_count": 70,
        "identity_control_count": 105,
        "component_check_count": 70,
        "primary_metrics": _PRIMARY_METRICS,
        "diagnostic_metrics": _DIAGNOSTIC_METRICS,
        "convergence_rule": (
            "each-role-and-primary-metric-d24-less-than-d12-or-both-zero"
        ),
        "epsilon_source": "maximum-of-all-r2-r4-primary-linf-distances",
        "effect_floor_factor": _EFFECT_FLOOR_FACTOR,
        "unresolved_policy": "no-epsilon-and-no-effect-floor",
        "outcomes": _OUTCOMES,
        "result_fields": _RESULT_FIELDS,
        "missing_function_baselines": _MISSING_FUNCTION_BASELINES,
        "accept_result_values": False,
        "field_function_decision_allowed": False,
        "memory_claim_allowed": False,
    }


@dataclass(frozen=True, slots=True)
class W7AQNumericalEvaluationContract:
    """Immutable rules for a later one-shot W7-AP numerical evaluation."""

    contract_id: str
    required_w7an_container_digest: str
    required_w7ao_contract_digest: str
    required_w7ap_compositor_id: str
    role_count: int
    distance_count: int
    identity_control_count: int
    component_check_count: int
    primary_metrics: tuple[str, ...]
    diagnostic_metrics: tuple[str, ...]
    convergence_rule: str
    epsilon_source: str
    effect_floor_factor: float
    unresolved_policy: str
    outcomes: tuple[str, ...]
    result_fields: tuple[str, ...]
    missing_function_baselines: tuple[str, ...]
    accept_result_values: bool
    field_function_decision_allowed: bool
    memory_claim_allowed: bool
    contract_digest: str

    def __post_init__(self) -> None:
        if (
            self.contract_id != _CONTRACT_ID
            or self.required_w7an_container_digest != _W7AN_CONTAINER_DIGEST
            or self.required_w7ao_contract_digest != _W7AO_CONTRACT_DIGEST
            or self.required_w7ap_compositor_id != _W7AP_COMPOSITOR_ID
            or self.role_count != 35
            or self.distance_count != 70
            or self.identity_control_count != 105
            or self.component_check_count != 70
            or tuple(self.primary_metrics) != _PRIMARY_METRICS
            or tuple(self.diagnostic_metrics) != _DIAGNOSTIC_METRICS
            or self.convergence_rule
            != "each-role-and-primary-metric-d24-less-than-d12-or-both-zero"
            or self.epsilon_source
            != "maximum-of-all-r2-r4-primary-linf-distances"
            or self.effect_floor_factor != _EFFECT_FLOOR_FACTOR
            or self.unresolved_policy != "no-epsilon-and-no-effect-floor"
            or tuple(self.outcomes) != _OUTCOMES
            or tuple(self.result_fields) != _RESULT_FIELDS
            or tuple(self.missing_function_baselines)
            != _MISSING_FUNCTION_BASELINES
            or self.accept_result_values is not False
            or self.field_function_decision_allowed is not False
            or self.memory_claim_allowed is not False
            or self.contract_digest != _digest(_payload())
        ):
            raise W7AQNumericalEvaluationContractError(
                "W7-AQ numerical evaluation contract differs"
            )


def build_w7aq_numerical_evaluation_contract(
) -> W7AQNumericalEvaluationContract:
    """Build the preregistration without accepting W7-AP values."""

    payload = _payload()
    return W7AQNumericalEvaluationContract(
        _CONTRACT_ID,
        _W7AN_CONTAINER_DIGEST,
        _W7AO_CONTRACT_DIGEST,
        _W7AP_COMPOSITOR_ID,
        35,
        70,
        105,
        70,
        _PRIMARY_METRICS,
        _DIAGNOSTIC_METRICS,
        "each-role-and-primary-metric-d24-less-than-d12-or-both-zero",
        "maximum-of-all-r2-r4-primary-linf-distances",
        _EFFECT_FLOOR_FACTOR,
        "no-epsilon-and-no-effect-floor",
        _OUTCOMES,
        _RESULT_FIELDS,
        _MISSING_FUNCTION_BASELINES,
        False,
        False,
        False,
        _digest(payload),
    )
