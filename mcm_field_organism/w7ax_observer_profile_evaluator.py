"""Pure W7-AX evaluator for observer repeat controls and profiles."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math

from .w7ac_observer_seven_path_consumer import W7ACObserverSevenPathResult
from .w7av_observer_path_contrast_binder import (
    W7AVObserverPathContrastResult,
)
from .w7aw_observer_profile_evaluation_contract import (
    W7AWObserverProfileEvaluationContract,
)
from .w7p_measurement_compositor import (
    W7PLifecycleProfile,
    compose_w7p_lifecycle_profile,
)


class W7AXObserverProfileEvaluatorError(ValueError):
    """Raised when W7-AX inputs cross observer evaluation roles."""


_EVALUATOR_ID = "w7ax.observer-profile-evaluator.v1"
_MODELS = ("leak", "sat", "norm")
_PATHS = ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
_DIRECTIONS = ("ab", "ba")
_W7AW_CONTRACT_DIGEST = (
    "37ae530d3a776db2b7b29f593efcb66482ff6b89a920c5d90b9b9085f4ffa7ff"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _trace_linf(left, right) -> float:
    left_trace = tuple(tuple(row) for row in left.observer_output_trace)
    right_trace = tuple(tuple(row) for row in right.observer_output_trace)
    if (
        left.model_id != right.model_id
        or left.observer_ticks != right.observer_ticks
        or len(left_trace) != len(right_trace)
        or any(len(a) != len(b) for a, b in zip(left_trace, right_trace))
    ):
        raise W7AXObserverProfileEvaluatorError(
            "observer repeat measurements are not aligned"
        )
    values = tuple(
        abs(a - b)
        for left_row, right_row in zip(left_trace, right_trace)
        for a, b in zip(left_row, right_row)
    )
    if not values or any(not math.isfinite(value) for value in values):
        raise W7AXObserverProfileEvaluatorError(
            "observer repeat control requires finite nonempty traces"
        )
    return max(values)


def _control_payload(
    path_id: str,
    model_id: str,
    checkpoint: int,
    trace_linf: float,
) -> dict[str, object]:
    return {
        "path_id": path_id,
        "model_id": model_id,
        "checkpoint": checkpoint,
        "measurement_role": "observer_output_trace_linf",
        "trace_linf": trace_linf,
    }


@dataclass(frozen=True, slots=True)
class W7AXObserverRepeatControl:
    """One same-input repeat distance on the observer surface."""

    path_id: str
    model_id: str
    checkpoint: int
    measurement_role: str
    trace_linf: float
    control_digest: str

    def __post_init__(self) -> None:
        if (
            self.path_id not in _PATHS
            or self.model_id not in _MODELS
            or self.checkpoint not in range(5)
            or self.measurement_role != "observer_output_trace_linf"
            or not math.isfinite(self.trace_linf)
            or self.trace_linf < 0.0
            or self.control_digest
            != _digest(
                _control_payload(
                    self.path_id,
                    self.model_id,
                    self.checkpoint,
                    self.trace_linf,
                )
            )
        ):
            raise W7AXObserverProfileEvaluatorError(
                "observer repeat control binding is invalid"
            )


def _profile_payload(profile: W7PLifecycleProfile) -> dict[str, object]:
    return {
        "measurement_surface": profile.measurement_surface,
        "model_id": profile.model_id,
        "direction": profile.direction,
        "resolution": profile.resolution,
        "old_b_retention": profile.old_b_retention,
        "old_g_retention": profile.old_g_retention,
        "new_b_gain": profile.new_b_gain,
    }


@dataclass(frozen=True, slots=True)
class W7AXObserverProfileRecord:
    """One W7-P profile retained with a content digest."""

    profile: W7PLifecycleProfile = field(repr=False)
    profile_digest: str

    def __post_init__(self) -> None:
        if (
            not isinstance(self.profile, W7PLifecycleProfile)
            or self.profile.measurement_surface != "observer"
            or self.profile.model_id not in _MODELS
            or self.profile.direction not in _DIRECTIONS
            or self.profile_digest != _digest(_profile_payload(self.profile))
        ):
            raise W7AXObserverProfileEvaluatorError(
                "observer profile record binding is invalid"
            )


def _result_payload(
    primary_digest: str,
    repeated_digest: str,
    w7av_digest: str,
    controls: tuple[W7AXObserverRepeatControl, ...],
    observer_epsilon: float,
    observer_effect_floor: float,
    profiles: tuple[W7AXObserverProfileRecord, ...],
) -> dict[str, object]:
    return {
        "evaluator_id": _EVALUATOR_ID,
        "w7aw_contract_digest": _W7AW_CONTRACT_DIGEST,
        "primary_w7ac_digest": primary_digest,
        "repeated_w7ac_digest": repeated_digest,
        "w7av_result_digest": w7av_digest,
        "control_digests": tuple(item.control_digest for item in controls),
        "observer_epsilon": observer_epsilon,
        "observer_effect_floor": observer_effect_floor,
        "profile_digests": tuple(item.profile_digest for item in profiles),
        "observer_explanation": "NOT_EVALUATED_NO_FIELD_PROFILES",
        "field_floor_applied_to_observer": False,
        "writes_back": False,
        "field_function_decision_allowed": False,
        "memory_claim_allowed": False,
    }


@dataclass(frozen=True, slots=True)
class W7AXObserverProfileEvaluationResult:
    """Observer resolution and profiles without cross-surface explanation."""

    evaluator_id: str
    w7aw_contract_digest: str
    primary_w7ac_digest: str
    repeated_w7ac_digest: str
    w7av_result_digest: str
    repeat_controls: tuple[W7AXObserverRepeatControl, ...]
    observer_epsilon: float
    observer_effect_floor: float
    profiles: tuple[W7AXObserverProfileRecord, ...]
    observer_explanation: str
    field_floor_applied_to_observer: bool
    writes_back: bool
    field_function_decision_allowed: bool
    memory_claim_allowed: bool
    evaluation_digest: str

    def __post_init__(self) -> None:
        controls = tuple(self.repeat_controls)
        profiles = tuple(self.profiles)
        expected_controls = tuple(
            (path, model, checkpoint)
            for path in _PATHS
            for model in _MODELS
            for checkpoint in range(5)
        )
        if (
            self.evaluator_id != _EVALUATOR_ID
            or self.w7aw_contract_digest != _W7AW_CONTRACT_DIGEST
            or not self.primary_w7ac_digest
            or self.repeated_w7ac_digest != self.primary_w7ac_digest
            or not self.w7av_result_digest
            or tuple(
                (item.path_id, item.model_id, item.checkpoint)
                for item in controls
            )
            != expected_controls
            or self.observer_epsilon
            != max(item.trace_linf for item in controls)
            or self.observer_effect_floor != 10.0 * self.observer_epsilon
            or tuple(
                (item.profile.model_id, item.profile.direction)
                for item in profiles
            )
            != tuple((model, direction) for model in _MODELS for direction in _DIRECTIONS)
            or self.observer_explanation != "NOT_EVALUATED_NO_FIELD_PROFILES"
            or self.field_floor_applied_to_observer is not False
            or self.writes_back is not False
            or self.field_function_decision_allowed is not False
            or self.memory_claim_allowed is not False
            or self.evaluation_digest
            != _digest(
                _result_payload(
                    self.primary_w7ac_digest,
                    self.repeated_w7ac_digest,
                    self.w7av_result_digest,
                    controls,
                    self.observer_epsilon,
                    self.observer_effect_floor,
                    profiles,
                )
            )
        ):
            raise W7AXObserverProfileEvaluatorError(
                "observer profile evaluation result binding is invalid"
            )
        object.__setattr__(self, "repeat_controls", controls)
        object.__setattr__(self, "profiles", profiles)


def evaluate_w7ax_observer_profiles(
    contract: W7AWObserverProfileEvaluationContract,
    raw_contrasts: W7AVObserverPathContrastResult,
    primary: W7ACObserverSevenPathResult,
    repeated: W7ACObserverSevenPathResult,
) -> W7AXObserverProfileEvaluationResult:
    """Evaluate independent repeat controls and observer profiles in memory."""

    if (
        not isinstance(contract, W7AWObserverProfileEvaluationContract)
        or contract.contract_digest != _W7AW_CONTRACT_DIGEST
        or not isinstance(raw_contrasts, W7AVObserverPathContrastResult)
        or raw_contrasts.result_digest != contract.required_w7av_result_digest
        or not isinstance(primary, W7ACObserverSevenPathResult)
        or not isinstance(repeated, W7ACObserverSevenPathResult)
        or primary is repeated
        or primary.observer_seven_path_consumption_digest
        != raw_contrasts.source_observer_seven_path_digest
        or repeated.observer_seven_path_consumption_digest
        != primary.observer_seven_path_consumption_digest
    ):
        raise W7AXObserverProfileEvaluatorError(
            "W7-AX input provenance or independent repeat binding differs"
        )
    primary_paths = {
        (item.path_id, item.model_id): item for item in primary.model_path_results
    }
    repeated_paths = {
        (item.path_id, item.model_id): item for item in repeated.model_path_results
    }
    controls = []
    for path in _PATHS:
        for model in _MODELS:
            left = primary_paths[(path, model)]
            right = repeated_paths[(path, model)]
            for checkpoint, (left_item, right_item) in enumerate(
                zip(left.checkpoints, right.checkpoints)
            ):
                distance = _trace_linf(
                    left_item.probe_continuation.measurement,
                    right_item.probe_continuation.measurement,
                )
                payload = _control_payload(path, model, checkpoint, distance)
                controls.append(
                    W7AXObserverRepeatControl(
                        path,
                        model,
                        checkpoint,
                        "observer_output_trace_linf",
                        distance,
                        _digest(payload),
                    )
                )
    controls_out = tuple(controls)
    observer_epsilon = max(item.trace_linf for item in controls_out)
    observer_effect_floor = contract.observer_effect_floor_factor * observer_epsilon
    curves = {
        (item.model_id, item.contrast_role): item.checkpoint_linf
        for item in raw_contrasts.contrasts
    }
    profiles = []
    for model in _MODELS:
        for direction, old_b, old_g, new_b, _neutral in contract.profile_mapping:
            profile = compose_w7p_lifecycle_profile(
                "observer",
                model,
                direction,
                curves[(model, old_b)],
                curves[(model, old_g)],
                curves[(model, new_b)],
                observer_effect_floor,
            )
            profiles.append(
                W7AXObserverProfileRecord(
                    profile,
                    _digest(_profile_payload(profile)),
                )
            )
    profiles_out = tuple(profiles)
    primary_digest = primary.observer_seven_path_consumption_digest
    repeated_digest = repeated.observer_seven_path_consumption_digest
    payload = _result_payload(
        primary_digest,
        repeated_digest,
        raw_contrasts.result_digest,
        controls_out,
        observer_epsilon,
        observer_effect_floor,
        profiles_out,
    )
    return W7AXObserverProfileEvaluationResult(
        _EVALUATOR_ID,
        contract.contract_digest,
        primary_digest,
        repeated_digest,
        raw_contrasts.result_digest,
        controls_out,
        observer_epsilon,
        observer_effect_floor,
        profiles_out,
        "NOT_EVALUATED_NO_FIELD_PROFILES",
        False,
        False,
        False,
        False,
        _digest(payload),
    )
