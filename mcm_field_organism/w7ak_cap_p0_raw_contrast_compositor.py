"""W7-AK sample-aligned CAP/P0 raw contrasts without evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math

from .w7ag_passive_cap_measurement_handoff import (
    W7AGCAPMeasurementResult,
    W7AGPassiveCAPMeasurementHandoff,
)
from .w7ai_p0_zero_start_measurement_reference import (
    W7AIP0MeasurementReferenceResult,
    W7AIP0ZeroStartMeasurementReferences,
)


class W7AKRawContrastError(ValueError):
    """Raised when CAP/P0 pairing leaves the W7-AJ contract."""


_COMPOSITOR_ID = "w7ak.cap-p0-raw-contrast-compositor.v1"
_CAP_HANDOFF_DIGEST = (
    "898e94bdbc2b5b0f893c5c512a684fd15544845d25de1a97febc83ffc8bcccd8"
)
_P0_REFERENCE_DIGEST = (
    "8b194514f4ac4074039891d6ba0e0db0ffdd9f28c157ce8a2bac66b238d771f5"
)
_PATH_IDS = ("ab", "ag", "ba", "bg", "ua", "ub", "ug")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _finite_vector(values, role: str) -> tuple[float, ...]:
    result = tuple(float(item) for item in values)
    if not result or any(not math.isfinite(item) for item in result):
        raise W7AKRawContrastError(f"{role} must be finite")
    return result


def _nonnegative(value: float, role: str) -> float:
    if isinstance(value, bool):
        raise W7AKRawContrastError(f"{role} must be numeric")
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise W7AKRawContrastError(f"{role} must be finite and nonnegative")
    return result


def _residual_payload(
    tick: int,
    s_residuals: tuple[float, ...],
    h_residuals: tuple[float, ...],
) -> dict[str, object]:
    return {
        "tick": tick,
        "s_residuals": s_residuals,
        "h_residuals": h_residuals,
    }


@dataclass(frozen=True, slots=True)
class W7AKResidualSample:
    """Directed CAP-minus-P0 S/H residual at one shared boundary."""

    tick: int
    s_residuals: tuple[float, ...]
    h_residuals: tuple[float, ...]
    residual_digest: str

    def __post_init__(self) -> None:
        if isinstance(self.tick, bool) or not isinstance(self.tick, int):
            raise W7AKRawContrastError("residual tick must be an integer")
        s_values = _finite_vector(self.s_residuals, "S residual")
        h_values = _finite_vector(self.h_residuals, "H residual")
        if len(s_values) != len(h_values):
            raise W7AKRawContrastError("S/H residual geometry differs")
        if self.residual_digest != _digest(
            _residual_payload(self.tick, s_values, h_values)
        ):
            raise W7AKRawContrastError(
                "residual digest does not match its content"
            )
        object.__setattr__(self, "s_residuals", s_values)
        object.__setattr__(self, "h_residuals", h_values)


def _raw_distances(
    left_samples,
    right_samples,
) -> tuple[float, float, float]:
    s_values = []
    h_values = []
    for left, right in zip(left_samples, right_samples, strict=True):
        if left.tick != right.tick:
            raise W7AKRawContrastError("raw distance sample ticks differ")
        left_s = _finite_vector(left.s_values, "left S")
        right_s = _finite_vector(right.s_values, "right S")
        left_h = _finite_vector(left.h_values, "left H")
        right_h = _finite_vector(right.h_values, "right H")
        if len({len(left_s), len(right_s), len(left_h), len(right_h)}) != 1:
            raise W7AKRawContrastError("raw distance sample geometry differs")
        s_values.extend(a - b for a, b in zip(left_s, right_s, strict=True))
        h_values.extend(a - b for a, b in zip(left_h, right_h, strict=True))
    if not s_values or not h_values:
        raise W7AKRawContrastError("raw distance requires samples")
    return (
        max(abs(item) for item in s_values),
        max(abs(item) for item in h_values),
        math.sqrt(
            math.fsum(item * item for item in s_values)
            + math.fsum(item * item for item in h_values)
        ),
    )


def _measurement_scalars(samples) -> tuple[float, float, float]:
    samples = tuple(samples)
    if not samples:
        raise W7AKRawContrastError("measurement reconstruction needs samples")
    s_linf = max(abs(value) for sample in samples for value in sample.s_values)
    h_linf = max(abs(value) for sample in samples for value in sample.h_values)
    trajectory_l2 = math.sqrt(
        math.fsum(
            value * value
            for sample in samples
            for values in (sample.s_values, sample.h_values)
            for value in values
        )
    )
    return s_linf, h_linf, trajectory_l2


def _pair_payload(
    path_id: str,
    checkpoint: int,
    plan_checkpoint_digest: str,
    cap_measurement_digest: str,
    p0_reference_digest: str,
    observation_ticks: tuple[int, ...],
    residual_digests: tuple[str, ...],
    cap_p0_s_linf: float,
    cap_p0_h_linf: float,
    cap_p0_sh_trajectory_l2: float,
    abs_probe_s_linf_gap: float,
    abs_probe_h_linf_gap: float,
    abs_probe_sh_trajectory_l2_gap: float,
) -> dict[str, object]:
    return {
        "path_id": path_id,
        "checkpoint": checkpoint,
        "plan_checkpoint_digest": plan_checkpoint_digest,
        "cap_measurement_digest": cap_measurement_digest,
        "p0_reference_digest": p0_reference_digest,
        "observation_ticks": observation_ticks,
        "residual_digests": residual_digests,
        "cap_p0_S_linf": cap_p0_s_linf,
        "cap_p0_H_linf": cap_p0_h_linf,
        "cap_p0_SH_trajectory_l2": cap_p0_sh_trajectory_l2,
        "abs_probe_S_linf_gap": abs_probe_s_linf_gap,
        "abs_probe_H_linf_gap": abs_probe_h_linf_gap,
        "abs_probe_SH_trajectory_l2_gap": abs_probe_sh_trajectory_l2_gap,
        "same_zero_fast_start": True,
        "p0_has_substrate": False,
        "evaluated": False,
    }


@dataclass(frozen=True, slots=True)
class W7AKRawContrastPair:
    """One bound CAP/P0 raw pair without threshold or path decision."""

    path_id: str
    checkpoint: int
    plan_checkpoint_digest: str
    cap_measurement: W7AGCAPMeasurementResult = field(repr=False)
    p0_reference: W7AIP0MeasurementReferenceResult = field(repr=False)
    observation_ticks: tuple[int, ...]
    residual_samples: tuple[W7AKResidualSample, ...] = field(repr=False)
    cap_p0_S_linf: float
    cap_p0_H_linf: float
    cap_p0_SH_trajectory_l2: float
    abs_probe_S_linf_gap: float
    abs_probe_H_linf_gap: float
    abs_probe_SH_trajectory_l2_gap: float
    same_zero_fast_start: bool
    p0_has_substrate: bool
    evaluated: bool
    raw_contrast_pair_digest: str

    def __post_init__(self) -> None:
        ticks = tuple(self.observation_ticks)
        residuals = tuple(self.residual_samples)
        if (
            self.path_id not in _PATH_IDS
            or self.checkpoint not in range(5)
            or not self.plan_checkpoint_digest
            or self.cap_measurement.path_id != self.path_id
            or self.p0_reference.path_id != self.path_id
            or self.cap_measurement.checkpoint != self.checkpoint
            or self.p0_reference.checkpoint != self.checkpoint
            or self.cap_measurement.plan_checkpoint_digest
            != self.plan_checkpoint_digest
            or self.p0_reference.plan_checkpoint_digest
            != self.plan_checkpoint_digest
            or ticks != tuple(item.tick for item in residuals)
            or ticks
            != self.cap_measurement.field_measurement.probe_observation_ticks
            or ticks
            != self.p0_reference.field_measurement.probe_observation_ticks
            or self.same_zero_fast_start is not True
            or self.p0_has_substrate is not False
            or self.evaluated is not False
        ):
            raise W7AKRawContrastError("raw contrast pair binding is invalid")
        for role in (
            "cap_p0_S_linf",
            "cap_p0_H_linf",
            "cap_p0_SH_trajectory_l2",
            "abs_probe_S_linf_gap",
            "abs_probe_H_linf_gap",
            "abs_probe_SH_trajectory_l2_gap",
        ):
            object.__setattr__(self, role, _nonnegative(getattr(self, role), role))
        payload = _pair_payload(
            self.path_id,
            self.checkpoint,
            self.plan_checkpoint_digest,
            self.cap_measurement.measurement_result_digest,
            self.p0_reference.measurement_reference_digest,
            ticks,
            tuple(item.residual_digest for item in residuals),
            self.cap_p0_S_linf,
            self.cap_p0_H_linf,
            self.cap_p0_SH_trajectory_l2,
            self.abs_probe_S_linf_gap,
            self.abs_probe_H_linf_gap,
            self.abs_probe_SH_trajectory_l2_gap,
        )
        if self.raw_contrast_pair_digest != _digest(payload):
            raise W7AKRawContrastError(
                "raw contrast pair digest does not match its content"
            )
        object.__setattr__(self, "observation_ticks", ticks)
        object.__setattr__(self, "residual_samples", residuals)


def _build_pair(
    cap: W7AGCAPMeasurementResult,
    p0: W7AIP0MeasurementReferenceResult,
) -> W7AKRawContrastPair:
    if (
        cap.path_id != p0.path_id
        or cap.checkpoint != p0.checkpoint
        or cap.plan_checkpoint_digest != p0.plan_checkpoint_digest
        or cap.field_measurement.probe_observation_ticks
        != p0.field_measurement.probe_observation_ticks
        or len(cap.samples) != len(p0.samples)
    ):
        raise W7AKRawContrastError("CAP/P0 measurement roles do not pair")
    cap_ids = tuple(item.neuron_id for item in cap.aligned_state.field.layer.neurons)
    if cap_ids != p0.initial_state.neuron_ids:
        raise W7AKRawContrastError("CAP/P0 neuron order differs")
    if (
        any(
            item.activation != 0.0 or item.afterimage != 0.0
            for item in cap.aligned_state.field.layer.neurons
        )
        or any(p0.initial_state.s_values)
        or any(p0.initial_state.h_values)
        or p0.initial_state.p0_field.substrate is not None
        or p0.initial_state.p0_field.development is not None
    ):
        raise W7AKRawContrastError("CAP/P0 pair does not share a zero fast start")
    residuals = []
    for cap_sample, p0_sample in zip(cap.samples, p0.samples, strict=True):
        if cap_sample.tick != p0_sample.tick:
            raise W7AKRawContrastError("CAP/P0 sample ticks differ")
        if len(
            {
                len(cap_sample.s_values),
                len(p0_sample.s_values),
                len(cap_sample.h_values),
                len(p0_sample.h_values),
                len(cap_ids),
            }
        ) != 1:
            raise W7AKRawContrastError("CAP/P0 sample geometry differs")
        s_residuals = tuple(
            a - b
            for a, b in zip(
                cap_sample.s_values,
                p0_sample.s_values,
                strict=True,
            )
        )
        h_residuals = tuple(
            a - b
            for a, b in zip(
                cap_sample.h_values,
                p0_sample.h_values,
                strict=True,
            )
        )
        residuals.append(
            W7AKResidualSample(
                cap_sample.tick,
                s_residuals,
                h_residuals,
                _digest(
                    _residual_payload(
                        cap_sample.tick,
                        s_residuals,
                        h_residuals,
                    )
                ),
            )
        )
    residuals = tuple(residuals)
    distances = _raw_distances(cap.samples, p0.samples)
    cap_scalars = _measurement_scalars(cap.samples)
    p0_scalars = _measurement_scalars(p0.samples)
    expected_cap = cap.field_measurement
    expected_p0 = p0.field_measurement
    if cap_scalars != (
        expected_cap.probe_S_linf,
        expected_cap.probe_H_linf,
        expected_cap.probe_SH_trajectory_l2,
    ) or p0_scalars != (
        expected_p0.probe_S_linf,
        expected_p0.probe_H_linf,
        expected_p0.probe_SH_trajectory_l2,
    ):
        raise W7AKRawContrastError("W7-P aggregate reconstruction differs")
    gaps = tuple(abs(a - b) for a, b in zip(cap_scalars, p0_scalars, strict=True))
    ticks = tuple(item.tick for item in residuals)
    payload = _pair_payload(
        cap.path_id,
        cap.checkpoint,
        cap.plan_checkpoint_digest,
        cap.measurement_result_digest,
        p0.measurement_reference_digest,
        ticks,
        tuple(item.residual_digest for item in residuals),
        distances[0],
        distances[1],
        distances[2],
        gaps[0],
        gaps[1],
        gaps[2],
    )
    return W7AKRawContrastPair(
        cap.path_id,
        cap.checkpoint,
        cap.plan_checkpoint_digest,
        cap,
        p0,
        ticks,
        residuals,
        distances[0],
        distances[1],
        distances[2],
        gaps[0],
        gaps[1],
        gaps[2],
        True,
        False,
        False,
        _digest(payload),
    )


def _result_payload(
    plan_digest: str,
    cap_handoff_digest: str,
    p0_reference_digest: str,
    pairs: tuple[W7AKRawContrastPair, ...],
    identity_countercontrol_digest: str,
    symmetry_countercontrol_digest: str,
    order_countercontrol_digest: str,
) -> dict[str, object]:
    return {
        "compositor_id": _COMPOSITOR_ID,
        "plan_digest": plan_digest,
        "cap_handoff_digest": cap_handoff_digest,
        "p0_reference_digest": p0_reference_digest,
        "pair_digests": tuple(item.raw_contrast_pair_digest for item in pairs),
        "identity_countercontrol_digest": identity_countercontrol_digest,
        "symmetry_countercontrol_digest": symmetry_countercontrol_digest,
        "order_countercontrol_digest": order_countercontrol_digest,
        "evaluated": False,
    }


@dataclass(frozen=True, slots=True)
class W7AKRawContrastComposition:
    """All 35 raw CAP/P0 pairs, still without an effect decision."""

    compositor_id: str
    plan_digest: str
    cap_handoff_digest: str
    p0_reference_digest: str
    pairs: tuple[W7AKRawContrastPair, ...] = field(repr=False)
    identity_countercontrol_digest: str
    symmetry_countercontrol_digest: str
    order_countercontrol_digest: str
    evaluated: bool
    raw_contrast_composition_digest: str

    def __post_init__(self) -> None:
        pairs = tuple(self.pairs)
        expected_roles = tuple(
            (path_id, checkpoint)
            for path_id in _PATH_IDS
            for checkpoint in range(5)
        )
        if (
            self.compositor_id != _COMPOSITOR_ID
            or not self.plan_digest
            or self.cap_handoff_digest != _CAP_HANDOFF_DIGEST
            or self.p0_reference_digest != _P0_REFERENCE_DIGEST
            or tuple((item.path_id, item.checkpoint) for item in pairs)
            != expected_roles
            or not self.identity_countercontrol_digest
            or not self.symmetry_countercontrol_digest
            or not self.order_countercontrol_digest
            or self.evaluated is not False
        ):
            raise W7AKRawContrastError("raw contrast composition binding is invalid")
        payload = _result_payload(
            self.plan_digest,
            self.cap_handoff_digest,
            self.p0_reference_digest,
            pairs,
            self.identity_countercontrol_digest,
            self.symmetry_countercontrol_digest,
            self.order_countercontrol_digest,
        )
        if self.raw_contrast_composition_digest != _digest(payload):
            raise W7AKRawContrastError(
                "raw contrast composition digest does not match its content"
            )
        object.__setattr__(self, "pairs", pairs)


def compose_w7ak_cap_p0_raw_contrasts(
    cap_handoff: W7AGPassiveCAPMeasurementHandoff,
    p0_references: W7AIP0ZeroStartMeasurementReferences,
) -> W7AKRawContrastComposition:
    """Pair existing W7-AG/W7-AI samples without rerunning either model."""

    if not isinstance(cap_handoff, W7AGPassiveCAPMeasurementHandoff) or not isinstance(
        p0_references,
        W7AIP0ZeroStartMeasurementReferences,
    ):
        raise W7AKRawContrastError("raw contrasts require W7-AG and W7-AI results")
    if (
        cap_handoff.measurement_handoff_digest != _CAP_HANDOFF_DIGEST
        or p0_references.p0_zero_start_measurement_reference_digest
        != _P0_REFERENCE_DIGEST
        or cap_handoff.plan_digest != p0_references.plan_digest
        or cap_handoff.p0_absolute_comparison_ready is not False
        or p0_references.p0_absolute_comparison_ready is not True
    ):
        raise W7AKRawContrastError("raw contrast input digests differ")
    input_digests = (
        cap_handoff.measurement_handoff_digest,
        p0_references.p0_zero_start_measurement_reference_digest,
    )
    cap_by_role = {
        (item.path_id, item.checkpoint): item
        for item in cap_handoff.measurements
    }
    p0_by_role = {
        (item.path_id, item.checkpoint): item
        for item in p0_references.references
    }
    expected_roles = tuple(
        (path_id, checkpoint)
        for path_id in _PATH_IDS
        for checkpoint in range(5)
    )
    if tuple(cap_by_role) != expected_roles or tuple(p0_by_role) != expected_roles:
        raise W7AKRawContrastError("raw contrast role inventory differs")
    pairs = tuple(
        _build_pair(cap_by_role[role], p0_by_role[role])
        for role in expected_roles
    )
    reversed_pairs = tuple(
        _build_pair(cap_by_role[role], p0_by_role[role])
        for role in reversed(expected_roles)
    )
    actual = {
        (item.path_id, item.checkpoint): item.raw_contrast_pair_digest
        for item in pairs
    }
    if any(
        actual[(item.path_id, item.checkpoint)]
        != item.raw_contrast_pair_digest
        for item in reversed_pairs
    ):
        raise W7AKRawContrastError("raw contrast processing order changed a pair")
    identity_payload = []
    symmetry_payload = []
    for cap, p0 in zip(
        cap_handoff.measurements,
        p0_references.references,
        strict=True,
    ):
        role = (cap.path_id, cap.checkpoint)
        pair = pairs[expected_roles.index(role)]
        cap_identity = _raw_distances(cap.samples, cap.samples)
        p0_identity = _raw_distances(p0.samples, p0.samples)
        forward = _raw_distances(cap.samples, p0.samples)
        reverse = _raw_distances(p0.samples, cap.samples)
        residuals_negated = True
        for residual, cap_sample, p0_sample in zip(
            pair.residual_samples,
            cap.samples,
            p0.samples,
            strict=True,
        ):
            reverse_s = tuple(
                p0_value - cap_value
                for p0_value, cap_value in zip(
                    p0_sample.s_values,
                    cap_sample.s_values,
                    strict=True,
                )
            )
            reverse_h = tuple(
                p0_value - cap_value
                for p0_value, cap_value in zip(
                    p0_sample.h_values,
                    cap_sample.h_values,
                    strict=True,
                )
            )
            if any(
                value != -reverse_value
                for value, reverse_value in zip(
                    residual.s_residuals,
                    reverse_s,
                    strict=True,
                )
            ) or any(
                value != -reverse_value
                for value, reverse_value in zip(
                    residual.h_residuals,
                    reverse_h,
                    strict=True,
                )
            ):
                residuals_negated = False
                break
        if cap_identity != (0.0, 0.0, 0.0) or p0_identity != (0.0, 0.0, 0.0):
            raise W7AKRawContrastError("identity countercontrol is nonzero")
        if forward != reverse or not residuals_negated:
            raise W7AKRawContrastError("operand symmetry countercontrol failed")
        identity_payload.append(
            {
                "path_id": cap.path_id,
                "checkpoint": cap.checkpoint,
                "cap_identity": cap_identity,
                "p0_identity": p0_identity,
            }
        )
        symmetry_payload.append(
            {
                "path_id": cap.path_id,
                "checkpoint": cap.checkpoint,
                "forward": forward,
                "reverse": reverse,
                "residuals_negated": residuals_negated,
            }
        )
    identity_digest = _digest(identity_payload)
    symmetry_digest = _digest(symmetry_payload)
    order_digest = _digest(
        {
            "canonical_pair_digests": tuple(
                item.raw_contrast_pair_digest for item in pairs
            ),
            "reverse_role_digests": tuple(
                actual[(item.path_id, item.checkpoint)]
                for item in reversed(pairs)
            ),
        }
    )
    if input_digests != (
        cap_handoff.measurement_handoff_digest,
        p0_references.p0_zero_start_measurement_reference_digest,
    ):
        raise W7AKRawContrastError("raw contrast composition mutated an input")
    payload = _result_payload(
        cap_handoff.plan_digest,
        input_digests[0],
        input_digests[1],
        pairs,
        identity_digest,
        symmetry_digest,
        order_digest,
    )
    return W7AKRawContrastComposition(
        _COMPOSITOR_ID,
        cap_handoff.plan_digest,
        input_digests[0],
        input_digests[1],
        pairs,
        identity_digest,
        symmetry_digest,
        order_digest,
        False,
        _digest(payload),
    )
