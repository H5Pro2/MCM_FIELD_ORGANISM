"""Static W7-AW contract for observer-only resolution and profile matching."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json


class W7AWObserverProfileEvaluationContractError(ValueError):
    """Raised when the observer profile preregistration changes."""


_CONTRACT_ID = "w7aw.observer-profile-evaluation-contract.v1"
_W7AV_RESULT_DIGEST = (
    "cc123faadefb32e0cc9d0d35db8512b6ecbb74ff62376ead23475382364f2acd"
)
_MODELS = ("leak", "sat", "norm")
_DIRECTIONS = ("ab", "ba")
_PROFILE_MAPPING = (
    (
        "ab",
        "ab_old_a_under_b",
        "ab_old_a_after_gap",
        "ab_new_b_after_a",
        "ab_new_b_after_neutral",
    ),
    (
        "ba",
        "ba_old_b_under_a",
        "ba_old_b_after_gap",
        "ba_new_a_after_b",
        "ba_new_a_after_neutral",
    ),
)
_OUTCOMES = (
    "NOT_RESOLVED",
    "PROFILE_NOT_MATCHED",
    "PROFILE_EXPLAINED_BY_LEAK",
    "PROFILE_EXPLAINED_BY_SAT",
    "PROFILE_EXPLAINED_BY_NORM",
)
_EXPLANATION_LIMIT = 0.05


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
        "required_w7av_result_digest": _W7AV_RESULT_DIGEST,
        "measurement_surface": "observer",
        "measurement_role": "observer_output_trace_linf",
        "model_precedence": _MODELS,
        "required_directions": _DIRECTIONS,
        "profile_mapping": _PROFILE_MAPPING,
        "checkpoint_count": 5,
        "identity_repeat_control_count": 105,
        "observer_epsilon_source": (
            "maximum-same-input-repeat-observer-output-trace-linf"
        ),
        "observer_effect_floor_factor": 10.0,
        "zero_identity_policy": "exact-zero-floor-remains-zero",
        "denominator_rule": "initial-old-effect-strictly-above-observer-floor",
        "unresolved_policy": "no-epsilon-rescue",
        "normalization_rule": "each-profile-by-own-initial-old-effect",
        "profile_distance_metric": "linf-over-three-curves-and-five-checkpoints",
        "explanation_limit": _EXPLANATION_LIMIT,
        "model_match_rule": "both-ab-and-ba-profile-distances-at-most-limit",
        "neutral_contrast_role": "required-audit-control-not-profile-coordinate",
        "outcomes": _OUTCOMES,
        "accept_result_values": False,
        "field_floor_applied_to_observer": False,
        "profile_decision_allowed": False,
        "field_function_decision_allowed": False,
        "memory_claim_allowed": False,
    }


@dataclass(frozen=True, slots=True)
class W7AWObserverProfileEvaluationContract:
    """Immutable rules for a later observer profile evaluator."""

    contract_id: str
    required_w7av_result_digest: str
    measurement_surface: str
    measurement_role: str
    model_precedence: tuple[str, ...]
    required_directions: tuple[str, ...]
    profile_mapping: tuple[tuple[str, ...], ...]
    checkpoint_count: int
    identity_repeat_control_count: int
    observer_epsilon_source: str
    observer_effect_floor_factor: float
    zero_identity_policy: str
    denominator_rule: str
    unresolved_policy: str
    normalization_rule: str
    profile_distance_metric: str
    explanation_limit: float
    model_match_rule: str
    neutral_contrast_role: str
    outcomes: tuple[str, ...]
    accept_result_values: bool
    field_floor_applied_to_observer: bool
    profile_decision_allowed: bool
    field_function_decision_allowed: bool
    memory_claim_allowed: bool
    contract_digest: str

    def __post_init__(self) -> None:
        if (
            self.contract_id != _CONTRACT_ID
            or self.required_w7av_result_digest != _W7AV_RESULT_DIGEST
            or self.measurement_surface != "observer"
            or self.measurement_role != "observer_output_trace_linf"
            or tuple(self.model_precedence) != _MODELS
            or tuple(self.required_directions) != _DIRECTIONS
            or tuple(tuple(item) for item in self.profile_mapping)
            != _PROFILE_MAPPING
            or self.checkpoint_count != 5
            or self.identity_repeat_control_count != 105
            or self.observer_epsilon_source
            != "maximum-same-input-repeat-observer-output-trace-linf"
            or self.observer_effect_floor_factor != 10.0
            or self.zero_identity_policy != "exact-zero-floor-remains-zero"
            or self.denominator_rule
            != "initial-old-effect-strictly-above-observer-floor"
            or self.unresolved_policy != "no-epsilon-rescue"
            or self.normalization_rule
            != "each-profile-by-own-initial-old-effect"
            or self.profile_distance_metric
            != "linf-over-three-curves-and-five-checkpoints"
            or self.explanation_limit != _EXPLANATION_LIMIT
            or self.model_match_rule
            != "both-ab-and-ba-profile-distances-at-most-limit"
            or self.neutral_contrast_role
            != "required-audit-control-not-profile-coordinate"
            or tuple(self.outcomes) != _OUTCOMES
            or self.accept_result_values is not False
            or self.field_floor_applied_to_observer is not False
            or self.profile_decision_allowed is not False
            or self.field_function_decision_allowed is not False
            or self.memory_claim_allowed is not False
            or self.contract_digest != _digest(_payload())
        ):
            raise W7AWObserverProfileEvaluationContractError(
                "W7-AW observer profile contract differs"
            )


def build_w7aw_observer_profile_evaluation_contract(
) -> W7AWObserverProfileEvaluationContract:
    """Build the observer-only preregistration without accepting values."""

    payload = _payload()
    return W7AWObserverProfileEvaluationContract(
        _CONTRACT_ID,
        _W7AV_RESULT_DIGEST,
        "observer",
        "observer_output_trace_linf",
        _MODELS,
        _DIRECTIONS,
        _PROFILE_MAPPING,
        5,
        105,
        "maximum-same-input-repeat-observer-output-trace-linf",
        10.0,
        "exact-zero-floor-remains-zero",
        "initial-old-effect-strictly-above-observer-floor",
        "no-epsilon-rescue",
        "each-profile-by-own-initial-old-effect",
        "linf-over-three-curves-and-five-checkpoints",
        _EXPLANATION_LIMIT,
        "both-ab-and-ba-profile-distances-at-most-limit",
        "required-audit-control-not-profile-coordinate",
        _OUTCOMES,
        False,
        False,
        False,
        False,
        False,
        _digest(payload),
    )
