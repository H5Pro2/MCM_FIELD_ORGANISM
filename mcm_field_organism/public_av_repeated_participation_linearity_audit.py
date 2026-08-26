"""Preregistered repeated-participation boundedness and affine-linearity audit."""

from __future__ import annotations

from dataclasses import replace
import math
from pathlib import Path

from .neutral_asynchronous_field_runtime import run_neutral_asynchronous_field
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .public_av_continuous_dissipation_viability import _continuous_gap, _field_components
from .public_av_return_resolution_curve import _shift_sequences
from .public_av_return_resolution_dissipation_intervention import DISSIPATION_LEAK_RATES_PER_SECOND
from .public_av_return_resolution_mode_audit import _mode_metrics
from .public_av_six_arm_field_execution import _sequences
from .public_av_two_stage_return_execution import _fresh_field, _steps
from .public_media_source_contract import PublicMediaSourceContract


REPEATED_PARTICIPATION_CYCLE_COUNTS = (1, 2, 4, 8)
REPEATED_PARTICIPATION_HISTORY_CYCLE_COUNTS = tuple(range(1, 9))
REPEATED_PARTICIPATION_GAP_TICKS = 2_000_000_000
REPEATED_PARTICIPATION_CONTACT_TICKS = 500_000_000
REPEATED_PARTICIPATION_ARM_IDS = (
    "continued_repeated_participation",
    "fresh_same_cycle",
    "zero_input_homogeneous_transition",
)


class PublicAVRepeatedParticipationLinearityError(ValueError):
    pass


def _zero_value_sequences(sequences):
    output = []
    for sequence in sequences:
        frames = tuple(
            replace(item, frame=replace(item.frame, values=(0.0,) * len(item.frame.values)))
            for item in sequence.frames
        )
        output.append(replace(sequence, frames=frames))
    return tuple(output)


def _affine_residual(measured, fresh, homogeneous):
    if not measured or len(measured) != len(fresh) or len(measured) != len(homogeneous):
        raise PublicAVRepeatedParticipationLinearityError("affine vectors must align")
    residual = tuple(
        value - (boundary + carried)
        for value, boundary, carried in zip(measured, fresh, homogeneous, strict=True)
    )
    return {
        "l1": math.fsum(abs(value) for value in residual),
        "l2": math.sqrt(math.fsum(value * value for value in residual)),
        "linf": max(abs(value) for value in residual),
    }


def _component_record(measured, fresh, homogeneous):
    carry = _mode_metrics(measured, fresh)
    return {
        "mean": math.fsum(measured) / len(measured),
        "l2": math.sqrt(math.fsum(value * value for value in measured)),
        "linf": max(abs(value) for value in measured),
        "carry_mean_delta_to_fresh": carry[0],
        "carry_centered_linf_to_fresh": carry[1],
        "carry_constant_energy_fraction": carry[2],
        "affine_residual": _affine_residual(measured, fresh, homogeneous),
    }


def _vector_metrics(values):
    if not values:
        raise PublicAVRepeatedParticipationLinearityError("field component is required")
    return {
        "l1": math.fsum(abs(value) for value in values),
        "l2": math.sqrt(math.fsum(value * value for value in values)),
        "linf": max(abs(value) for value in values),
        "mean": math.fsum(values) / len(values),
    }


def _state_record(field):
    activation, afterimage = _field_components(field)
    snapshot_digest = (
        field.snapshot().digest() if field.last_distribution is not None else None
    )
    return {
        "activation": _vector_metrics(activation),
        "afterimage": _vector_metrics(afterimage),
        "layer_digest": field.layer.digest(),
        "snapshot_digest": snapshot_digest,
        "snapshot_available": snapshot_digest is not None,
    }


def _cycle_delta(current, previous):
    if len(current) != len(previous) or not current:
        raise PublicAVRepeatedParticipationLinearityError("cycle vectors must align")
    return _vector_metrics(
        tuple(value - prior for value, prior in zip(current, previous, strict=True))
    )


def _rate_history(rate, cycles):
    if tuple(item["cycle"] for item in cycles) != REPEATED_PARTICIPATION_HISTORY_CYCLE_COUNTS:
        raise PublicAVRepeatedParticipationLinearityError("complete cycle history is required")
    return {
        "leak_rate_per_second": rate,
        "cycles": cycles,
        "boundedness_series": [
            {
                "cycle": item["cycle"],
                "activation_maximum_amplitude": item["maximum_amplitude"]["activation"],
                "afterimage_maximum_amplitude": item["maximum_amplitude"]["afterimage"],
            }
            for item in cycles
        ],
    }


def execute_public_av_repeated_participation_linearity_audit(
    path: Path, contract: PublicMediaSourceContract
) -> dict[str, object]:
    if not isinstance(path, Path) or not path.is_file():
        raise PublicAVRepeatedParticipationLinearityError("audited media file is required")
    if not isinstance(contract, PublicMediaSourceContract):
        raise PublicAVRepeatedParticipationLinearityError("source contract is required")
    base_sequences = _sequences(path, contract)
    substrate = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage = NeutralFastAfterimageConfig(0.5)
    points = []
    rate_histories = []
    for rate in DISSIPATION_LEAK_RATES_PER_SECOND:
        dissipation = NeutralFieldDissipationConfig(rate)
        current = _fresh_field(base_sequences)
        observations = {}
        cycle_history = []
        total_events = 0
        previous_post_contact_components = None
        for cycle in REPEATED_PARTICIPATION_HISTORY_CYCLE_COUNTS:
            start_tick = (cycle - 1) * (
                REPEATED_PARTICIPATION_CONTACT_TICKS + REPEATED_PARTICIPATION_GAP_TICKS
            )
            pre_contact = current
            sequences = _shift_sequences(base_sequences, start_tick)
            steps = _steps(
                sequences, start_tick, start_tick + REPEATED_PARTICIPATION_CONTACT_TICKS
            )
            continued = run_neutral_asynchronous_field(
                pre_contact, sequences, steps, substrate, afterimage_config=afterimage,
                dissipation_config=dissipation,
            )
            total_events += continued.source_support_count
            post_contact = continued.field
            post_contact_components = _field_components(post_contact)
            gap_end_tick = start_tick + REPEATED_PARTICIPATION_CONTACT_TICKS + REPEATED_PARTICIPATION_GAP_TICKS
            post_gap = _continuous_gap(
                post_contact,
                start_tick + REPEATED_PARTICIPATION_CONTACT_TICKS,
                gap_end_tick,
                substrate,
                afterimage,
                dissipation,
            )
            state_records = {
                "before_contact": _state_record(pre_contact),
                "after_contact": _state_record(post_contact),
                "after_contact_free_interval": _state_record(post_gap),
            }
            cycle_delta = None
            if previous_post_contact_components is not None:
                cycle_delta = {
                    "activation": _cycle_delta(
                        post_contact_components[0], previous_post_contact_components[0]
                    ),
                    "afterimage": _cycle_delta(
                        post_contact_components[1], previous_post_contact_components[1]
                    ),
                }
            maximum_amplitude = {
                component: max(
                    state_records[state][component]["linf"]
                    for state in (
                        "before_contact", "after_contact", "after_contact_free_interval"
                    )
                )
                for component in ("activation", "afterimage")
            }
            cycle_history.append({
                "cycle": cycle,
                "states": state_records,
                "cycle_to_cycle_post_contact_delta": cycle_delta,
                "maximum_amplitude": maximum_amplitude,
                "events_in_world_contact": continued.source_support_count,
                "cumulative_world_event_count": total_events,
            })
            previous_post_contact_components = post_contact_components
            current = post_gap
            if cycle not in REPEATED_PARTICIPATION_CYCLE_COUNTS:
                continue
            fresh = run_neutral_asynchronous_field(
                _fresh_field(base_sequences), sequences, steps, substrate,
                afterimage_config=afterimage, dissipation_config=dissipation,
            )
            homogeneous = run_neutral_asynchronous_field(
                pre_contact, _zero_value_sequences(sequences), steps, substrate,
                afterimage_config=afterimage, dissipation_config=dissipation,
            )
            measured_activation, measured_afterimage = _field_components(continued.field)
            fresh_activation, fresh_afterimage = _field_components(fresh.field)
            homogeneous_activation, homogeneous_afterimage = _field_components(homogeneous.field)
            observations[cycle] = {
                "leak_rate_per_second": rate,
                "cycle_count": cycle,
                "events_per_world_contact": continued.source_support_count,
                "cumulative_world_event_count": total_events,
                "arm_ids": list(REPEATED_PARTICIPATION_ARM_IDS),
                "activation": _component_record(
                    measured_activation, fresh_activation, homogeneous_activation
                ),
                "afterimage": _component_record(
                    measured_afterimage, fresh_afterimage, homogeneous_afterimage
                ),
                "layer_digests": [
                    continued.field.layer.digest(), fresh.field.layer.digest(),
                    homogeneous.field.layer.digest(),
                ],
                "snapshot_digests": [
                    continued.field.snapshot().digest(), fresh.field.snapshot().digest(),
                    homogeneous.field.snapshot().digest(),
                ],
            }
        points.extend(observations[count] for count in REPEATED_PARTICIPATION_CYCLE_COUNTS)
        rate_histories.append(_rate_history(rate, cycle_history))
    return {
        "audit_id": "public.av.nasa-earthrise.repeated-participation-linearity-audit.v1",
        "source_id": contract.source_id,
        "clock_id": base_sequences[0].clock_id,
        "leak_rates_per_second": list(DISSIPATION_LEAK_RATES_PER_SECOND),
        "cycle_counts": list(REPEATED_PARTICIPATION_CYCLE_COUNTS),
        "history_cycle_counts": list(REPEATED_PARTICIPATION_HISTORY_CYCLE_COUNTS),
        "contact_free_gap_ticks": REPEATED_PARTICIPATION_GAP_TICKS,
        "world_sequence_identical_each_cycle": True,
        "affine_prediction": "F(x,u)=F(0,u)+F(x,0)",
        "initial_pre_contact_snapshot_policy": (
            "null_until_first_completed_receptor_distribution"
        ),
        "per_rate_cycle_histories": rate_histories,
        "points": points,
        "threshold_defined": False,
        "preferred_rate_selected": False,
        "memory_claim_allowed": False,
        "meaning_claim_allowed": False,
        "organization_claim_allowed": False,
        "ai_claim_allowed": False,
    }
