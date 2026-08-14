"""Preregistered amplitude and shape audit for continuous field dissipation."""

from __future__ import annotations

import math
from pathlib import Path

from .neutral_asynchronous_field_runtime import run_neutral_asynchronous_field
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .public_av_continuous_dissipation_viability import _continuous_gap, _field_components
from .public_av_return_resolution_curve import ARM_IDS, _independent_arm_start_field, _shift_sequences
from .public_av_return_resolution_dissipation_intervention import DISSIPATION_LEAK_RATES_PER_SECOND
from .public_av_return_resolution_mode_audit import _mode_metrics
from .public_av_return_resolution_tail import TAIL_RESOLUTION_DURATION_TICKS
from .public_av_six_arm_field_execution import _sequences
from .public_av_two_stage_return_execution import _fresh_field, _steps
from .public_media_source_contract import PublicMediaSourceContract
from .shared_field_component_intervention import intervene_shared_field_component


class PublicAVContinuousDissipationAttenuationError(ValueError):
    pass


def _vector_stats(values: tuple[float, ...]) -> dict[str, float]:
    if not values:
        raise PublicAVContinuousDissipationAttenuationError("vector metrics require values")
    mean = math.fsum(values) / len(values)
    return {
        "l1": math.fsum(abs(value) for value in values),
        "l2": math.sqrt(math.fsum(value * value for value in values)),
        "linf": max(abs(value) for value in values),
        "mean": mean,
        "standard_deviation": math.sqrt(
            math.fsum((value - mean) ** 2 for value in values) / len(values)
        ),
    }


def _norm_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0.0:
        if numerator == 0.0:
            return 1.0
        raise PublicAVContinuousDissipationAttenuationError(
            "nonzero norm cannot be normalized by a zero reference norm"
        )
    return numerator / denominator


def _centered_form_correlation(
    values: tuple[float, ...], reference: tuple[float, ...]
) -> float:
    if not values or len(values) != len(reference):
        raise PublicAVContinuousDissipationAttenuationError("shape vectors must align")
    left_mean = math.fsum(values) / len(values)
    right_mean = math.fsum(reference) / len(reference)
    left = tuple(value - left_mean for value in values)
    right = tuple(value - right_mean for value in reference)
    left_norm = math.sqrt(math.fsum(value * value for value in left))
    right_norm = math.sqrt(math.fsum(value * value for value in right))
    if left_norm == 0.0 and right_norm == 0.0:
        return 1.0
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    value = math.fsum(a * b for a, b in zip(left, right, strict=True)) / (
        left_norm * right_norm
    )
    return min(1.0, max(-1.0, value))


def _absolute_metrics(values, zero_values):
    stats = _vector_stats(values)
    zero_stats = _vector_stats(zero_values)
    return {
        **stats,
        "l1_ratio_to_zero_rate": _norm_ratio(stats["l1"], zero_stats["l1"]),
        "l2_ratio_to_zero_rate": _norm_ratio(stats["l2"], zero_stats["l2"]),
        "linf_ratio_to_zero_rate": _norm_ratio(stats["linf"], zero_stats["linf"]),
        "centered_form_correlation_to_zero_rate": _centered_form_correlation(
            values, zero_values
        ),
    }


def _difference(left, right):
    return tuple(a - b for a, b in zip(left, right, strict=True))


def _carry_metrics(values, fresh, zero_values, zero_fresh):
    delta = _difference(values, fresh)
    zero_delta = _difference(zero_values, zero_fresh)
    stats = _vector_stats(delta)
    zero_stats = _vector_stats(zero_delta)
    fresh_stats = _vector_stats(fresh)
    constant_fraction = _mode_metrics(values, fresh)[2]
    zero_constant_fraction = _mode_metrics(zero_values, zero_fresh)[2]
    return {
        **stats,
        "l1_ratio_to_zero_rate_carry": _norm_ratio(stats["l1"], zero_stats["l1"]),
        "l2_ratio_to_zero_rate_carry": _norm_ratio(stats["l2"], zero_stats["l2"]),
        "linf_ratio_to_zero_rate_carry": _norm_ratio(stats["linf"], zero_stats["linf"]),
        "l1_ratio_to_rate_fresh_field": _norm_ratio(stats["l1"], fresh_stats["l1"]),
        "l2_ratio_to_rate_fresh_field": _norm_ratio(stats["l2"], fresh_stats["l2"]),
        "linf_ratio_to_rate_fresh_field": _norm_ratio(stats["linf"], fresh_stats["linf"]),
        "constant_energy_fraction": constant_fraction,
        "constant_energy_fraction_change_from_zero_rate": (
            constant_fraction - zero_constant_fraction
        ),
    }


def execute_public_av_continuous_dissipation_attenuation_audit(
    path: Path, contract: PublicMediaSourceContract
) -> dict[str, object]:
    if not isinstance(path, Path) or not path.is_file():
        raise PublicAVContinuousDissipationAttenuationError("audited media file is required")
    if not isinstance(contract, PublicMediaSourceContract):
        raise PublicAVContinuousDissipationAttenuationError("source contract is required")
    sequences = _sequences(path, contract)
    substrate = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage = NeutralFastAfterimageConfig(0.5)
    stage_ones = {}
    for rate in DISSIPATION_LEAK_RATES_PER_SECOND:
        stage_ones[rate] = run_neutral_asynchronous_field(
            _fresh_field(sequences), sequences, _steps(sequences, 0, 500_000_000), substrate,
            afterimage_config=afterimage,
            dissipation_config=NeutralFieldDissipationConfig(rate),
        )
    zero_stage_activation, zero_stage_afterimage = _field_components(stage_ones[0.0].field)
    stage_one = []
    for rate in DISSIPATION_LEAK_RATES_PER_SECOND:
        activation, trace = _field_components(stage_ones[rate].field)
        stage_one.append({
            "leak_rate_per_second": rate,
            "event_count": stage_ones[rate].source_support_count,
            "activation": _absolute_metrics(activation, zero_stage_activation),
            "afterimage": _absolute_metrics(trace, zero_stage_afterimage),
            "layer_digest": stage_ones[rate].field.layer.digest(),
            "snapshot_digest": stage_ones[rate].field.snapshot().digest(),
        })

    points = []
    for duration in TAIL_RESOLUTION_DURATION_TICKS:
        start_tick = 500_000_000 + duration
        shifted = _shift_sequences(sequences, start_tick)
        steps = _steps(shifted, start_tick, start_tick + 500_000_000)
        fields_by_rate = {}
        counts = {}
        for rate in DISSIPATION_LEAK_RATES_PER_SECOND:
            config = NeutralFieldDissipationConfig(rate)
            arm_fields = []
            for arm_id in ARM_IDS:
                start = _independent_arm_start_field(
                    stage_ones[rate].field, arm_id, lambda: _fresh_field(sequences)
                )
                if arm_id != "return.fresh_stage_two":
                    start = _continuous_gap(
                        start, 500_000_000, start_tick, substrate, afterimage, config
                    )
                    if arm_id == "control.activation_only_carry":
                        start = intervene_shared_field_component(
                            start, "reset_afterimage_preserve_activation"
                        ).field
                    elif arm_id == "control.afterimage_only_carry":
                        start = intervene_shared_field_component(
                            start, "reset_activation_preserve_afterimage"
                        ).field
                run = run_neutral_asynchronous_field(
                    start, shifted, steps, substrate, afterimage_config=afterimage,
                    dissipation_config=config,
                )
                counts[rate] = run.source_support_count
                arm_fields.append(run.field)
            fields_by_rate[rate] = tuple(arm_fields)

        zero_fields = fields_by_rate[0.0]
        zero_fresh_activation, zero_fresh_afterimage = _field_components(zero_fields[-1])
        for rate in DISSIPATION_LEAK_RATES_PER_SECOND:
            fields = fields_by_rate[rate]
            fresh_activation, fresh_afterimage = _field_components(fields[-1])
            arms = []
            for index, field in enumerate(fields):
                activation, trace = _field_components(field)
                zero_activation, zero_trace = _field_components(zero_fields[index])
                arms.append({
                    "arm_id": ARM_IDS[index],
                    "activation": _carry_metrics(
                        activation, fresh_activation, zero_activation, zero_fresh_activation
                    ),
                    "afterimage": _carry_metrics(
                        trace, fresh_afterimage, zero_trace, zero_fresh_afterimage
                    ),
                    "layer_digest": field.layer.digest(),
                    "snapshot_digest": field.snapshot().digest(),
                })
            points.append({
                "leak_rate_per_second": rate,
                "resolution_duration_ticks": duration,
                "stage_two_event_count": counts[rate],
                "fresh_activation": _absolute_metrics(
                    fresh_activation, zero_fresh_activation
                ),
                "fresh_afterimage": _absolute_metrics(
                    fresh_afterimage, zero_fresh_afterimage
                ),
                "arms": arms,
            })
    return {
        "audit_id": "public.av.nasa-earthrise.continuous-dissipation-attenuation-audit.v1",
        "source_id": contract.source_id,
        "clock_id": sequences[0].clock_id,
        "leak_rates_per_second": list(DISSIPATION_LEAK_RATES_PER_SECOND),
        "resolution_duration_ticks": list(TAIL_RESOLUTION_DURATION_TICKS),
        "zero_norm_ratio_rule": "zero_over_zero_is_one_nonzero_over_zero_is_error",
        "centered_zero_shape_rule": "both_zero_is_one_one_zero_is_zero",
        "stage_one": stage_one,
        "points": points,
        "threshold_defined": False,
        "preferred_rate_selected": False,
        "memory_claim_allowed": False,
        "meaning_claim_allowed": False,
        "organization_claim_allowed": False,
        "ai_claim_allowed": False,
    }
