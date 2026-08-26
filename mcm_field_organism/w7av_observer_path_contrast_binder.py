"""Bind raw seven-path observer contrasts without crossing measurement surfaces."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math

from .w7ac_observer_seven_path_consumer import W7ACObserverSevenPathResult


class W7AVObserverPathContrastBinderError(ValueError):
    """Raised when an observer contrast leaves the W7-O measurement contract."""


_BINDER_ID = "w7av.observer-path-contrast-binder.v1"
_W7AT_EVALUATION_DIGEST = (
    "b6ff73ac1b85344a5aa925506dba599bb9b3956abeb4eca0e6b0f9e63087b99c"
)
_W7AT_FIELD_EFFECT_FLOOR = 1.8915768951188738e-07
_MODELS = ("leak", "sat", "norm")
_CONTRASTS = (
    ("ab_old_a_under_b", "ab", "ub"),
    ("ab_old_a_after_gap", "ag", "ug"),
    ("ab_new_b_after_a", "ab", "ag"),
    ("ab_new_b_after_neutral", "ub", "ug"),
    ("ba_old_b_under_a", "ba", "ua"),
    ("ba_old_b_after_gap", "bg", "ug"),
    ("ba_new_a_after_b", "ba", "bg"),
    ("ba_new_a_after_neutral", "ua", "ug"),
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
        left.observer_ticks != right.observer_ticks
        or len(left_trace) != len(right_trace)
        or any(len(a) != len(b) for a, b in zip(left_trace, right_trace))
    ):
        raise W7AVObserverPathContrastBinderError(
            "observer probe traces are not temporally and geometrically aligned"
        )
    values = tuple(
        abs(a - b)
        for left_row, right_row in zip(left_trace, right_trace)
        for a, b in zip(left_row, right_row)
    )
    if not values or any(not math.isfinite(value) for value in values):
        raise W7AVObserverPathContrastBinderError(
            "observer probe contrast requires finite nonempty traces"
        )
    return max(values)


def _contrast_payload(
    model_id: str,
    contrast_role: str,
    left_path_id: str,
    right_path_id: str,
    checkpoint_linf: tuple[float, ...],
) -> dict[str, object]:
    return {
        "model_id": model_id,
        "contrast_role": contrast_role,
        "left_path_id": left_path_id,
        "right_path_id": right_path_id,
        "measurement_role": "observer_output_trace_linf",
        "checkpoint_linf": checkpoint_linf,
        "exact_segment_measurement": True,
        "normalized": False,
        "decision_allowed": False,
    }


@dataclass(frozen=True, slots=True)
class W7AVObserverPathContrast:
    """Five raw checkpoint distances for one model and path comparison."""

    model_id: str
    contrast_role: str
    left_path_id: str
    right_path_id: str
    measurement_role: str
    checkpoint_linf: tuple[float, ...]
    exact_segment_measurement: bool
    normalized: bool
    decision_allowed: bool
    contrast_digest: str

    def __post_init__(self) -> None:
        values = tuple(self.checkpoint_linf)
        row = (self.contrast_role, self.left_path_id, self.right_path_id)
        if (
            self.model_id not in _MODELS
            or row not in _CONTRASTS
            or self.measurement_role != "observer_output_trace_linf"
            or len(values) != 5
            or any(not math.isfinite(value) or value < 0.0 for value in values)
            or self.exact_segment_measurement is not True
            or self.normalized is not False
            or self.decision_allowed is not False
            or self.contrast_digest
            != _digest(
                _contrast_payload(
                    self.model_id,
                    self.contrast_role,
                    self.left_path_id,
                    self.right_path_id,
                    values,
                )
            )
        ):
            raise W7AVObserverPathContrastBinderError(
                "observer path contrast binding is invalid"
            )
        object.__setattr__(self, "checkpoint_linf", values)


def _result_payload(
    source_digest: str,
    contrasts: tuple[W7AVObserverPathContrast, ...],
) -> dict[str, object]:
    return {
        "binder_id": _BINDER_ID,
        "source_observer_seven_path_digest": source_digest,
        "w7at_evaluation_digest": _W7AT_EVALUATION_DIGEST,
        "w7at_field_effect_floor": _W7AT_FIELD_EFFECT_FLOOR,
        "field_floor_applied_to_observer": False,
        "contrast_digests": tuple(item.contrast_digest for item in contrasts),
        "profile_composition_allowed": False,
        "observer_explanation_allowed": False,
        "field_function_decision_allowed": False,
        "memory_claim_allowed": False,
    }


@dataclass(frozen=True, slots=True)
class W7AVObserverPathContrastResult:
    """Complete raw Observer binding with explicit field-floor separation."""

    binder_id: str
    source_observer_seven_path_digest: str
    w7at_evaluation_digest: str
    w7at_field_effect_floor: float
    field_floor_applied_to_observer: bool
    contrasts: tuple[W7AVObserverPathContrast, ...]
    profile_composition_allowed: bool
    observer_explanation_allowed: bool
    field_function_decision_allowed: bool
    memory_claim_allowed: bool
    result_digest: str

    def __post_init__(self) -> None:
        contrasts = tuple(self.contrasts)
        expected_roles = tuple(
            (model_id, role, left, right)
            for model_id in _MODELS
            for role, left, right in _CONTRASTS
        )
        if (
            self.binder_id != _BINDER_ID
            or not self.source_observer_seven_path_digest
            or self.w7at_evaluation_digest != _W7AT_EVALUATION_DIGEST
            or self.w7at_field_effect_floor != _W7AT_FIELD_EFFECT_FLOOR
            or self.field_floor_applied_to_observer is not False
            or tuple(
                (
                    item.model_id,
                    item.contrast_role,
                    item.left_path_id,
                    item.right_path_id,
                )
                for item in contrasts
            )
            != expected_roles
            or self.profile_composition_allowed is not False
            or self.observer_explanation_allowed is not False
            or self.field_function_decision_allowed is not False
            or self.memory_claim_allowed is not False
            or self.result_digest
            != _digest(
                _result_payload(
                    self.source_observer_seven_path_digest,
                    contrasts,
                )
            )
        ):
            raise W7AVObserverPathContrastBinderError(
                "observer contrast result binding is invalid"
            )
        object.__setattr__(self, "contrasts", contrasts)


def bind_w7av_observer_path_contrasts(
    source: W7ACObserverSevenPathResult,
) -> W7AVObserverPathContrastResult:
    """Compose all preregistered raw contrasts from one frozen W7-AC result."""

    if not isinstance(source, W7ACObserverSevenPathResult):
        raise W7AVObserverPathContrastBinderError(
            "W7-AV requires one complete W7-AC observer result"
        )
    paths = {
        (item.model_id, item.path_id): item for item in source.model_path_results
    }
    contrasts = []
    for model_id in _MODELS:
        for role, left_path, right_path in _CONTRASTS:
            left = paths[(model_id, left_path)]
            right = paths[(model_id, right_path)]
            values = tuple(
                _trace_linf(
                    left_checkpoint.probe_continuation.measurement,
                    right_checkpoint.probe_continuation.measurement,
                )
                for left_checkpoint, right_checkpoint in zip(
                    left.checkpoints,
                    right.checkpoints,
                )
            )
            payload = _contrast_payload(
                model_id,
                role,
                left_path,
                right_path,
                values,
            )
            contrasts.append(
                W7AVObserverPathContrast(
                    model_id,
                    role,
                    left_path,
                    right_path,
                    "observer_output_trace_linf",
                    values,
                    True,
                    False,
                    False,
                    _digest(payload),
                )
            )
    contrasts_out = tuple(contrasts)
    source_digest = source.observer_seven_path_consumption_digest
    payload = _result_payload(source_digest, contrasts_out)
    return W7AVObserverPathContrastResult(
        _BINDER_ID,
        source_digest,
        _W7AT_EVALUATION_DIGEST,
        _W7AT_FIELD_EFFECT_FLOOR,
        False,
        contrasts_out,
        False,
        False,
        False,
        False,
        _digest(payload),
    )
