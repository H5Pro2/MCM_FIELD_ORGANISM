"""Terminal W7-BB evaluator for dimensionless CAP-to-observer profiles."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math

from .w7ax_observer_profile_evaluator import W7AXObserverProfileEvaluationResult
from .w7az_cap_field_profile_compositor import W7AZCAPFieldProfileComposition
from .w7ba_cap_observer_profile_comparison_contract import (
    W7BACAPObserverProfileComparisonContract,
)


class W7BBTerminalProfileEvaluatorError(RuntimeError):
    """Raised when the terminal profile comparison cannot complete."""


_EVALUATOR_ID = "w7bb.terminal-cap-observer-profile-evaluator.v1"
_W7BA_CONTRACT_DIGEST = (
    "131e18bb4ab7fa862ea8886ee338353b2fcffc6055e6bd15e2419b29ab36dccc"
)
_MODELS = ("leak", "sat", "norm")
_DIRECTIONS = ("ab", "ba")
_OUTCOMES = {
    "NOT_RESOLVED",
    "PROFILE_NOT_MATCHED",
    "PROFILE_EXPLAINED_BY_LEAK",
    "PROFILE_EXPLAINED_BY_SAT",
    "PROFILE_EXPLAINED_BY_NORM",
}


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _profile_values(profile) -> tuple[float, ...]:
    values = tuple(
        value
        for curve in (
            profile.old_b_retention,
            profile.old_g_retention,
            profile.new_b_gain,
        )
        for value in curve
    )
    if len(values) != 15 or any(not math.isfinite(value) for value in values):
        raise W7BBTerminalProfileEvaluatorError(
            "resolved profile does not contain 15 finite coordinates"
        )
    return values


def _direction_payload(
    model_id: str,
    direction: str,
    profile_linf: float,
) -> dict[str, object]:
    return {
        "model_id": model_id,
        "direction": direction,
        "profile_linf": profile_linf,
    }


@dataclass(frozen=True, slots=True)
class W7BBProfileDirectionDistance:
    model_id: str
    direction: str
    profile_linf: float
    distance_digest: str

    def __post_init__(self) -> None:
        if (
            self.model_id not in _MODELS
            or self.direction not in _DIRECTIONS
            or not math.isfinite(self.profile_linf)
            or self.profile_linf < 0.0
            or self.distance_digest
            != _digest(
                _direction_payload(
                    self.model_id,
                    self.direction,
                    self.profile_linf,
                )
            )
        ):
            raise W7BBTerminalProfileEvaluatorError(
                "profile direction distance binding is invalid"
            )


def _model_payload(
    model_id: str,
    direction_digests: tuple[str, ...],
    model_linf: float,
    matched: bool,
) -> dict[str, object]:
    return {
        "model_id": model_id,
        "direction_digests": direction_digests,
        "model_linf": model_linf,
        "matched": matched,
    }


@dataclass(frozen=True, slots=True)
class W7BBObserverModelProfileComparison:
    model_id: str
    direction_distances: tuple[W7BBProfileDirectionDistance, ...]
    model_linf: float
    matched: bool
    comparison_digest: str

    def __post_init__(self) -> None:
        distances = tuple(self.direction_distances)
        if (
            self.model_id not in _MODELS
            or tuple((item.model_id, item.direction) for item in distances)
            != tuple((self.model_id, direction) for direction in _DIRECTIONS)
            or self.model_linf != max(item.profile_linf for item in distances)
            or self.matched != (self.model_linf <= 0.05)
            or self.comparison_digest
            != _digest(
                _model_payload(
                    self.model_id,
                    tuple(item.distance_digest for item in distances),
                    self.model_linf,
                    self.matched,
                )
            )
        ):
            raise W7BBTerminalProfileEvaluatorError(
                "observer model profile comparison binding is invalid"
            )
        object.__setattr__(self, "direction_distances", distances)


def _result_payload(
    w7ax_digest: str,
    w7az_digest: str,
    comparisons: tuple[W7BBObserverModelProfileComparison, ...],
    outcome: str,
) -> dict[str, object]:
    return {
        "evaluator_id": _EVALUATOR_ID,
        "w7ba_contract_digest": _W7BA_CONTRACT_DIGEST,
        "w7ax_evaluation_digest": w7ax_digest,
        "w7az_composition_digest": w7az_digest,
        "comparison_digests": tuple(
            item.comparison_digest for item in comparisons
        ),
        "outcome": outcome,
        "persisted": False,
        "writes_back": False,
        "field_function_decision_allowed": False,
        "memory_claim_allowed": False,
    }


@dataclass(frozen=True, slots=True)
class W7BBTerminalProfileEvaluation:
    evaluator_id: str
    w7ba_contract_digest: str
    w7ax_evaluation_digest: str
    w7az_composition_digest: str
    model_comparisons: tuple[W7BBObserverModelProfileComparison, ...]
    outcome: str
    persisted: bool
    writes_back: bool
    field_function_decision_allowed: bool
    memory_claim_allowed: bool
    evaluation_digest: str

    def __post_init__(self) -> None:
        comparisons = tuple(self.model_comparisons)
        expected_count = 0 if self.outcome == "NOT_RESOLVED" else 3
        if (
            self.evaluator_id != _EVALUATOR_ID
            or self.w7ba_contract_digest != _W7BA_CONTRACT_DIGEST
            or not self.w7ax_evaluation_digest
            or not self.w7az_composition_digest
            or len(comparisons) != expected_count
            or (
                comparisons
                and tuple(item.model_id for item in comparisons) != _MODELS
            )
            or self.outcome not in _OUTCOMES
            or self.persisted is not False
            or self.writes_back is not False
            or self.field_function_decision_allowed is not False
            or self.memory_claim_allowed is not False
            or self.evaluation_digest
            != _digest(
                _result_payload(
                    self.w7ax_evaluation_digest,
                    self.w7az_composition_digest,
                    comparisons,
                    self.outcome,
                )
            )
        ):
            raise W7BBTerminalProfileEvaluatorError(
                "terminal profile evaluation binding is invalid"
            )
        object.__setattr__(self, "model_comparisons", comparisons)


class _W7BBTerminalEvaluatorState:
    """Single-use state that locks after either success or failure."""

    __slots__ = ("result", "error")

    def __init__(self) -> None:
        self.result: W7BBTerminalProfileEvaluation | None = None
        self.error: str | None = None


def _start_w7bb_terminal_profile_evaluator() -> _W7BBTerminalEvaluatorState:
    return _W7BBTerminalEvaluatorState()


def _evaluate_w7bb_terminal_profiles(
    state: _W7BBTerminalEvaluatorState,
    contract: W7BACAPObserverProfileComparisonContract,
    observer_result: W7AXObserverProfileEvaluationResult,
    cap_result: W7AZCAPFieldProfileComposition,
) -> W7BBTerminalProfileEvaluation:
    """Compare canonical profiles once and lock the evaluator terminally."""

    if not isinstance(state, _W7BBTerminalEvaluatorState):
        raise W7BBTerminalProfileEvaluatorError(
            "terminal profile evaluation requires its private state"
        )
    if state.result is not None or state.error is not None:
        raise W7BBTerminalProfileEvaluatorError(
            "terminal profile evaluation was already attempted"
        )
    try:
        if (
            not isinstance(contract, W7BACAPObserverProfileComparisonContract)
            or contract.contract_digest != _W7BA_CONTRACT_DIGEST
            or not isinstance(observer_result, W7AXObserverProfileEvaluationResult)
            or observer_result.evaluation_digest
            != contract.required_w7ax_evaluation_digest
            or not isinstance(cap_result, W7AZCAPFieldProfileComposition)
            or cap_result.composition_digest
            != contract.required_w7az_composition_digest
        ):
            raise W7BBTerminalProfileEvaluatorError(
                "terminal profile source provenance differs"
            )
        cap_profiles = {
            item.profile.direction: item.profile for item in cap_result.profiles
        }
        observer_profiles = {
            (item.profile.model_id, item.profile.direction): item.profile
            for item in observer_result.profiles
        }
        all_profiles = tuple(cap_profiles.values()) + tuple(
            observer_profiles.values()
        )
        if any(profile.resolution != "RESOLVED" for profile in all_profiles):
            comparisons = ()
            outcome = "NOT_RESOLVED"
        else:
            model_comparisons = []
            for model_id in contract.observer_model_precedence:
                direction_distances = []
                for direction in contract.required_directions:
                    cap_values = _profile_values(cap_profiles[direction])
                    observer_values = _profile_values(
                        observer_profiles[(model_id, direction)]
                    )
                    distance = max(
                        abs(a - b)
                        for a, b in zip(
                            cap_values,
                            observer_values,
                            strict=True,
                        )
                    )
                    payload = _direction_payload(model_id, direction, distance)
                    direction_distances.append(
                        W7BBProfileDirectionDistance(
                            model_id,
                            direction,
                            distance,
                            _digest(payload),
                        )
                    )
                distances_out = tuple(direction_distances)
                model_linf = max(item.profile_linf for item in distances_out)
                matched = model_linf <= contract.explanation_limit
                payload = _model_payload(
                    model_id,
                    tuple(item.distance_digest for item in distances_out),
                    model_linf,
                    matched,
                )
                model_comparisons.append(
                    W7BBObserverModelProfileComparison(
                        model_id,
                        distances_out,
                        model_linf,
                        matched,
                        _digest(payload),
                    )
                )
            comparisons = tuple(model_comparisons)
            matched_models = tuple(
                item.model_id for item in comparisons if item.matched
            )
            outcome = (
                "PROFILE_EXPLAINED_BY_" + matched_models[0].upper()
                if matched_models
                else "PROFILE_NOT_MATCHED"
            )
        w7ax_digest = observer_result.evaluation_digest
        w7az_digest = cap_result.composition_digest
        payload = _result_payload(
            w7ax_digest,
            w7az_digest,
            comparisons,
            outcome,
        )
        result = W7BBTerminalProfileEvaluation(
            _EVALUATOR_ID,
            contract.contract_digest,
            w7ax_digest,
            w7az_digest,
            comparisons,
            outcome,
            False,
            False,
            False,
            False,
            _digest(payload),
        )
    except Exception as error:
        state.error = f"{type(error).__name__}: {error}"
        if isinstance(error, W7BBTerminalProfileEvaluatorError):
            raise
        raise W7BBTerminalProfileEvaluatorError(state.error) from error
    state.result = result
    return result
