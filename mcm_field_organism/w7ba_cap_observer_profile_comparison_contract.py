"""Static W7-BA contract for dimensionless CAP-to-observer profile matching."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json


class W7BACAPObserverProfileComparisonContractError(ValueError):
    """Raised when the W7-BA profile comparison preregistration changes."""


_CONTRACT_ID = "w7ba.cap-observer-profile-comparison-contract.v1"
_W7AX_EVALUATION_DIGEST = (
    "7729f162d5702bf9008eac107148bbb9f85f58dce244e5bf726657b4535cd9ba"
)
_W7AZ_COMPOSITION_DIGEST = (
    "ecb14d76ab49a05010c4d988308f729415d7583570d0908f2588df0964254d9f"
)
_MODELS = ("leak", "sat", "norm")
_DIRECTIONS = ("ab", "ba")
_CURVES = ("old_b_retention", "old_g_retention", "new_b_gain")
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
        "required_w7ax_evaluation_digest": _W7AX_EVALUATION_DIGEST,
        "required_w7az_composition_digest": _W7AZ_COMPOSITION_DIGEST,
        "candidate_model_id": "cap",
        "observer_model_precedence": _MODELS,
        "required_directions": _DIRECTIONS,
        "profile_curves": _CURVES,
        "checkpoint_count": 5,
        "required_cap_profile_count": 2,
        "required_observer_profile_count": 6,
        "resolution_rule": "all-compared-profiles-must-be-resolved",
        "direction_distance_metric": (
            "linf-over-three-dimensionless-curves-and-five-checkpoints"
        ),
        "model_distance_metric": "maximum-of-ab-and-ba-direction-distances",
        "explanation_limit": _EXPLANATION_LIMIT,
        "model_match_rule": "model-distance-at-most-explanation-limit",
        "selection_rule": "first-matched-model-in-leak-sat-norm-precedence",
        "outcomes": _OUTCOMES,
        "absolute_amplitude_comparison_allowed": False,
        "neutral_control_is_profile_coordinate": False,
        "accept_result_values": False,
        "profile_explanation_decision_allowed": False,
        "field_function_decision_allowed": False,
        "memory_claim_allowed": False,
    }


@dataclass(frozen=True, slots=True)
class W7BACAPObserverProfileComparisonContract:
    """Immutable rules for a later dimensionless profile evaluator."""

    contract_id: str
    required_w7ax_evaluation_digest: str
    required_w7az_composition_digest: str
    candidate_model_id: str
    observer_model_precedence: tuple[str, ...]
    required_directions: tuple[str, ...]
    profile_curves: tuple[str, ...]
    checkpoint_count: int
    required_cap_profile_count: int
    required_observer_profile_count: int
    resolution_rule: str
    direction_distance_metric: str
    model_distance_metric: str
    explanation_limit: float
    model_match_rule: str
    selection_rule: str
    outcomes: tuple[str, ...]
    absolute_amplitude_comparison_allowed: bool
    neutral_control_is_profile_coordinate: bool
    accept_result_values: bool
    profile_explanation_decision_allowed: bool
    field_function_decision_allowed: bool
    memory_claim_allowed: bool
    contract_digest: str

    def __post_init__(self) -> None:
        if (
            self.contract_id != _CONTRACT_ID
            or self.required_w7ax_evaluation_digest != _W7AX_EVALUATION_DIGEST
            or self.required_w7az_composition_digest
            != _W7AZ_COMPOSITION_DIGEST
            or self.candidate_model_id != "cap"
            or tuple(self.observer_model_precedence) != _MODELS
            or tuple(self.required_directions) != _DIRECTIONS
            or tuple(self.profile_curves) != _CURVES
            or self.checkpoint_count != 5
            or self.required_cap_profile_count != 2
            or self.required_observer_profile_count != 6
            or self.resolution_rule
            != "all-compared-profiles-must-be-resolved"
            or self.direction_distance_metric
            != "linf-over-three-dimensionless-curves-and-five-checkpoints"
            or self.model_distance_metric
            != "maximum-of-ab-and-ba-direction-distances"
            or self.explanation_limit != _EXPLANATION_LIMIT
            or self.model_match_rule
            != "model-distance-at-most-explanation-limit"
            or self.selection_rule
            != "first-matched-model-in-leak-sat-norm-precedence"
            or tuple(self.outcomes) != _OUTCOMES
            or self.absolute_amplitude_comparison_allowed is not False
            or self.neutral_control_is_profile_coordinate is not False
            or self.accept_result_values is not False
            or self.profile_explanation_decision_allowed is not False
            or self.field_function_decision_allowed is not False
            or self.memory_claim_allowed is not False
            or self.contract_digest != _digest(_payload())
        ):
            raise W7BACAPObserverProfileComparisonContractError(
                "W7-BA CAP-to-observer profile comparison contract differs"
            )


def build_w7ba_cap_observer_profile_comparison_contract(
) -> W7BACAPObserverProfileComparisonContract:
    """Build the comparison preregistration without accepting profiles."""

    payload = _payload()
    return W7BACAPObserverProfileComparisonContract(
        _CONTRACT_ID,
        _W7AX_EVALUATION_DIGEST,
        _W7AZ_COMPOSITION_DIGEST,
        "cap",
        _MODELS,
        _DIRECTIONS,
        _CURVES,
        5,
        2,
        6,
        "all-compared-profiles-must-be-resolved",
        "linf-over-three-dimensionless-curves-and-five-checkpoints",
        "maximum-of-ab-and-ba-direction-distances",
        _EXPLANATION_LIMIT,
        "model-distance-at-most-explanation-limit",
        "first-matched-model-in-leak-sat-norm-precedence",
        _OUTCOMES,
        False,
        False,
        False,
        False,
        False,
        False,
        _digest(payload),
    )
