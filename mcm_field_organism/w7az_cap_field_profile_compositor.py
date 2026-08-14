"""Pure W7-AZ compositor for CAP path contrasts and field profiles."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math

from .w7ag_passive_cap_measurement_handoff import (
    W7AGCAPMeasurementResult,
    W7AGPassiveCAPMeasurementHandoff,
)
from .w7ak_cap_p0_raw_contrast_compositor import W7AKRawContrastComposition
from .w7ay_cap_field_profile_contract import W7AYCAPFieldProfileContract
from .w7p_measurement_compositor import (
    W7PLifecycleProfile,
    compose_w7p_lifecycle_profile,
)


class W7AZCAPFieldProfileCompositorError(ValueError):
    """Raised when CAP path contrast composition leaves the W7-AY contract."""


_COMPOSITOR_ID = "w7az.cap-field-profile-compositor.v1"
_W7AY_CONTRACT_DIGEST = (
    "08f229d21891bdf55f7274439303fdae312c2ddec03883b6a04db4f5949a89f9"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _trajectory_distances(
    left: W7AGCAPMeasurementResult,
    right: W7AGCAPMeasurementResult,
) -> tuple[float, float, float]:
    left_samples = tuple(left.samples)
    right_samples = tuple(right.samples)
    if (
        left.checkpoint != right.checkpoint
        or len(left_samples) != len(right_samples)
        or left.field_measurement.probe_observation_ticks
        != right.field_measurement.probe_observation_ticks
    ):
        raise W7AZCAPFieldProfileCompositorError(
            "CAP path trajectories are not checkpoint and tick aligned"
        )
    s_differences = []
    h_differences = []
    for left_sample, right_sample in zip(
        left_samples,
        right_samples,
        strict=True,
    ):
        if (
            left_sample.tick != right_sample.tick
            or len(left_sample.s_values) != len(right_sample.s_values)
            or len(left_sample.h_values) != len(right_sample.h_values)
            or len(left_sample.s_values) != len(left_sample.h_values)
        ):
            raise W7AZCAPFieldProfileCompositorError(
                "CAP path trajectory sample geometry differs"
            )
        s_differences.extend(
            abs(a - b)
            for a, b in zip(
                left_sample.s_values,
                right_sample.s_values,
                strict=True,
            )
        )
        h_differences.extend(
            abs(a - b)
            for a, b in zip(
                left_sample.h_values,
                right_sample.h_values,
                strict=True,
            )
        )
    if (
        not s_differences
        or not h_differences
        or any(not math.isfinite(value) for value in s_differences)
        or any(not math.isfinite(value) for value in h_differences)
    ):
        raise W7AZCAPFieldProfileCompositorError(
            "CAP path contrast requires finite nonempty trajectories"
        )
    s_linf = max(s_differences)
    h_linf = max(h_differences)
    return s_linf, h_linf, max(s_linf, h_linf)


def _contrast_payload(
    role: str,
    left_path_id: str,
    right_path_id: str,
    s_linf: tuple[float, ...],
    h_linf: tuple[float, ...],
    effect_linf: tuple[float, ...],
) -> dict[str, object]:
    return {
        "contrast_role": role,
        "left_path_id": left_path_id,
        "right_path_id": right_path_id,
        "checkpoint_S_linf": s_linf,
        "checkpoint_H_linf": h_linf,
        "checkpoint_effect_linf": effect_linf,
        "effect_metric": "max-of-samplewise-S-linf-and-H-linf",
        "normalized": False,
        "evaluated": False,
    }


@dataclass(frozen=True, slots=True)
class W7AZCAPPathContrast:
    """Five raw CAP S/H path distances and their joint effect metric."""

    contrast_role: str
    left_path_id: str
    right_path_id: str
    checkpoint_S_linf: tuple[float, ...]
    checkpoint_H_linf: tuple[float, ...]
    checkpoint_effect_linf: tuple[float, ...]
    effect_metric: str
    normalized: bool
    evaluated: bool
    contrast_digest: str

    def __post_init__(self) -> None:
        s_values = tuple(self.checkpoint_S_linf)
        h_values = tuple(self.checkpoint_H_linf)
        effects = tuple(self.checkpoint_effect_linf)
        if (
            len(s_values) != 5
            or len(h_values) != 5
            or len(effects) != 5
            or any(
                not math.isfinite(value) or value < 0.0
                for values in (s_values, h_values, effects)
                for value in values
            )
            or effects != tuple(max(s, h) for s, h in zip(s_values, h_values))
            or self.effect_metric
            != "max-of-samplewise-S-linf-and-H-linf"
            or self.normalized is not False
            or self.evaluated is not False
            or self.contrast_digest
            != _digest(
                _contrast_payload(
                    self.contrast_role,
                    self.left_path_id,
                    self.right_path_id,
                    s_values,
                    h_values,
                    effects,
                )
            )
        ):
            raise W7AZCAPFieldProfileCompositorError(
                "CAP path contrast binding is invalid"
            )
        object.__setattr__(self, "checkpoint_S_linf", s_values)
        object.__setattr__(self, "checkpoint_H_linf", h_values)
        object.__setattr__(self, "checkpoint_effect_linf", effects)


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
class W7AZCAPProfileRecord:
    profile: W7PLifecycleProfile = field(repr=False)
    profile_digest: str

    def __post_init__(self) -> None:
        if (
            not isinstance(self.profile, W7PLifecycleProfile)
            or self.profile.measurement_surface != "field"
            or self.profile.model_id != "cap"
            or self.profile.direction not in {"ab", "ba"}
            or self.profile_digest != _digest(_profile_payload(self.profile))
        ):
            raise W7AZCAPFieldProfileCompositorError(
                "CAP profile record binding is invalid"
            )


def _result_payload(
    cap_handoff_digest: str,
    cap_p0_digest: str,
    contrasts: tuple[W7AZCAPPathContrast, ...],
    profiles: tuple[W7AZCAPProfileRecord, ...],
) -> dict[str, object]:
    return {
        "compositor_id": _COMPOSITOR_ID,
        "w7ay_contract_digest": _W7AY_CONTRACT_DIGEST,
        "cap_handoff_digest": cap_handoff_digest,
        "cap_p0_control_digest": cap_p0_digest,
        "contrast_digests": tuple(item.contrast_digest for item in contrasts),
        "profile_digests": tuple(item.profile_digest for item in profiles),
        "cap_p0_values_used_as_path_effects": False,
        "observer_comparison_performed": False,
        "writes_back": False,
        "field_function_decision_allowed": False,
        "memory_claim_allowed": False,
    }


@dataclass(frozen=True, slots=True)
class W7AZCAPFieldProfileComposition:
    """Eight raw CAP path contrasts and two profiles without interpretation."""

    compositor_id: str
    w7ay_contract_digest: str
    cap_handoff_digest: str
    cap_p0_control_digest: str
    contrasts: tuple[W7AZCAPPathContrast, ...]
    profiles: tuple[W7AZCAPProfileRecord, ...]
    cap_p0_values_used_as_path_effects: bool
    observer_comparison_performed: bool
    writes_back: bool
    field_function_decision_allowed: bool
    memory_claim_allowed: bool
    composition_digest: str

    def __post_init__(self) -> None:
        contrasts = tuple(self.contrasts)
        profiles = tuple(self.profiles)
        if (
            self.compositor_id != _COMPOSITOR_ID
            or self.w7ay_contract_digest != _W7AY_CONTRACT_DIGEST
            or not self.cap_handoff_digest
            or not self.cap_p0_control_digest
            or len(contrasts) != 8
            or tuple(item.profile.direction for item in profiles) != ("ab", "ba")
            or self.cap_p0_values_used_as_path_effects is not False
            or self.observer_comparison_performed is not False
            or self.writes_back is not False
            or self.field_function_decision_allowed is not False
            or self.memory_claim_allowed is not False
            or self.composition_digest
            != _digest(
                _result_payload(
                    self.cap_handoff_digest,
                    self.cap_p0_control_digest,
                    contrasts,
                    profiles,
                )
            )
        ):
            raise W7AZCAPFieldProfileCompositorError(
                "CAP field profile composition binding is invalid"
            )
        object.__setattr__(self, "contrasts", contrasts)
        object.__setattr__(self, "profiles", profiles)


def compose_w7az_cap_field_profiles(
    contract: W7AYCAPFieldProfileContract,
    cap_handoff: W7AGPassiveCAPMeasurementHandoff,
    cap_p0_control: W7AKRawContrastComposition,
) -> W7AZCAPFieldProfileComposition:
    """Compose CAP path contrasts and profiles from existing objects only."""

    if (
        not isinstance(contract, W7AYCAPFieldProfileContract)
        or contract.contract_digest != _W7AY_CONTRACT_DIGEST
        or not isinstance(cap_handoff, W7AGPassiveCAPMeasurementHandoff)
        or cap_handoff.measurement_handoff_digest
        != contract.required_w7ag_handoff_digest
        or not isinstance(cap_p0_control, W7AKRawContrastComposition)
        or cap_p0_control.raw_contrast_composition_digest
        != contract.required_w7ak_composition_digest
        or cap_p0_control.cap_handoff_digest
        != cap_handoff.measurement_handoff_digest
        or cap_p0_control.plan_digest != cap_handoff.plan_digest
    ):
        raise W7AZCAPFieldProfileCompositorError(
            "W7-AZ input provenance differs"
        )
    measurements = {
        (item.path_id, item.checkpoint): item for item in cap_handoff.measurements
    }
    for pair in cap_p0_control.pairs:
        if pair.cap_measurement is not measurements[(pair.path_id, pair.checkpoint)]:
            raise W7AZCAPFieldProfileCompositorError(
                "W7-AK CAP control does not retain the W7-AG measurement object"
            )
    contrasts = []
    for role, left_path, right_path in contract.contrast_inventory:
        distances = tuple(
            _trajectory_distances(
                measurements[(left_path, checkpoint)],
                measurements[(right_path, checkpoint)],
            )
            for checkpoint in range(contract.checkpoint_count)
        )
        s_values = tuple(item[0] for item in distances)
        h_values = tuple(item[1] for item in distances)
        effects = tuple(item[2] for item in distances)
        payload = _contrast_payload(
            role,
            left_path,
            right_path,
            s_values,
            h_values,
            effects,
        )
        contrasts.append(
            W7AZCAPPathContrast(
                role,
                left_path,
                right_path,
                s_values,
                h_values,
                effects,
                contract.effect_metric,
                False,
                False,
                _digest(payload),
            )
        )
    contrasts_out = tuple(contrasts)
    effect_curves = {
        item.contrast_role: item.checkpoint_effect_linf for item in contrasts_out
    }
    profiles = []
    for direction, old_b, old_g, new_b, _neutral in contract.profile_mapping:
        profile = compose_w7p_lifecycle_profile(
            "field",
            "cap",
            direction,
            effect_curves[old_b],
            effect_curves[old_g],
            effect_curves[new_b],
            contract.w7at_effect_floor,
        )
        profiles.append(
            W7AZCAPProfileRecord(
                profile,
                _digest(_profile_payload(profile)),
            )
        )
    profiles_out = tuple(profiles)
    handoff_digest = cap_handoff.measurement_handoff_digest
    control_digest = cap_p0_control.raw_contrast_composition_digest
    payload = _result_payload(
        handoff_digest,
        control_digest,
        contrasts_out,
        profiles_out,
    )
    return W7AZCAPFieldProfileComposition(
        _COMPOSITOR_ID,
        contract.contract_digest,
        handoff_digest,
        control_digest,
        contrasts_out,
        profiles_out,
        False,
        False,
        False,
        False,
        False,
        _digest(payload),
    )
