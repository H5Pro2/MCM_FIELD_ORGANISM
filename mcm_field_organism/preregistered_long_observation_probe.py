"""Passive execution of research preregistration 027."""

from __future__ import annotations

from dataclasses import dataclass
import math

from .endogenous_external_overlap_null_probe import (
    _distributor,
    _initial_field,
    _vectors,
    _zeroed,
)
from .field_step_time import MCMFieldStepTime
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    advance_neutral_fast_shared_field,
)
from .receptor_contract import CommonFieldTime, ReceptorContactFrame


DURATIONS = (5, 15, 30, 60)
EXTERNAL_VALUES = (0.60, -0.30, 0.45, -0.15, 0.30, -0.45, 0.15, -0.60)
ENDOGENOUS_0_VALUES = (0.00, 0.25, 0.50, 0.75, 1.00, 0.75, 0.50, 0.25)
ENDOGENOUS_1_VALUES = (0.00, 1.00, 0.00, -1.00, 0.00, 1.00, 0.00, -1.00)
TOLERANCE = 1e-12


@dataclass(frozen=True, slots=True)
class LongObservationDurationResult:
    duration_seconds: int
    measured_ticks: int
    maximum_activation_superposition_error: float
    maximum_afterimage_superposition_error: float
    isolated_causes_nonzero: bool
    joint_repeat_digests_equal: bool
    maximum_joint_repeat_vector_error: float
    permuted_path_observed: bool
    holdout_digests_equal: bool
    maximum_holdout_vector_error: float


@dataclass(frozen=True, slots=True)
class PreregisteredLongObservationResult:
    durations: tuple[LongObservationDurationResult, ...]
    time_contract_valid: bool
    contact_contract_valid: bool
    all_cases_additive: bool
    all_cases_reproducible: bool
    all_holdouts_equal: bool
    observer_writeback_performed: bool
    runtime_changed: bool
    stop_line: str


def _frames(duration: int, *, reverse: bool = False):
    indices = tuple(range(duration))
    source_indices = tuple(reversed(indices)) if reverse else indices
    endogenous = []
    external = []
    for tick, source_tick in zip(indices, source_indices, strict=True):
        index = source_tick % 8
        endogenous.append(
            ReceptorContactFrame(
                "endogenous.controlled",
                "endogenous.controlled.v1",
                f"endogenous.long.{tick}",
                "organism.controlled",
                tick,
                tick + 1,
                ("c0", "c1"),
                (ENDOGENOUS_0_VALUES[index], ENDOGENOUS_1_VALUES[index]),
            )
        )
        external.append(
            ReceptorContactFrame(
                "external.controlled",
                "external.controlled.v1",
                f"external.long.{tick}",
                "external.controlled",
                tick,
                tick + 1,
                ("x0",),
                (EXTERNAL_VALUES[index],),
            )
        )
    return tuple(endogenous), tuple(external)


def _run_trajectory(endogenous, external, *, use_endogenous, use_external):
    current = _initial_field(endogenous[0], external[0])
    distributor = _distributor(endogenous[0], external[0])
    substrate = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage = NeutralFastAfterimageConfig(0.5)
    trajectory = []
    for tick, (endogenous_frame, external_frame) in enumerate(
        zip(endogenous, external, strict=True)
    ):
        selected_endogenous = (
            endogenous_frame
            if use_endogenous
            else _zeroed(endogenous_frame, "zero")
        )
        selected_external = (
            external_frame
            if use_external
            else _zeroed(external_frame, "zero")
        )
        distribution = distributor.distribute(
            (selected_external, selected_endogenous),
            CommonFieldTime("organism.clock", tick, tick + 1),
        )
        current = advance_neutral_fast_shared_field(
            current,
            distribution,
            MCMFieldStepTime("organism.clock", tick, tick + 1, 1.0),
            substrate,
            afterimage,
        )
        trajectory.append((_vectors(current), current.layer.digest()))
    return tuple(trajectory)


def _maximum_vector_error(left, right) -> float:
    return max(
        abs(a - b)
        for left_vector, right_vector in zip(left, right, strict=True)
        for a, b in zip(left_vector, right_vector, strict=True)
    )


def _holdout_digest():
    endogenous, external = _frames(3)
    endogenous = tuple(
        ReceptorContactFrame(
            item.modality_id,
            item.geometry_id,
            item.snapshot_id,
            item.clock_id,
            item.window_start_tick,
            item.window_end_tick,
            item.carrier_ids,
            (0.0, 0.0),
        )
        for item in endogenous
    )
    external_values = (0.0, 0.0, 0.60)
    external = tuple(
        ReceptorContactFrame(
            item.modality_id,
            item.geometry_id,
            item.snapshot_id,
            item.clock_id,
            item.window_start_tick,
            item.window_end_tick,
            item.carrier_ids,
            (external_values[index],),
        )
        for index, item in enumerate(external)
    )
    return _run_trajectory(
        endogenous, external, use_endogenous=True, use_external=True
    )[-1]


def run_preregistered_long_observation_probe():
    """Execute all preregistered branches without changing field mechanics."""

    duration_results = []
    for duration in DURATIONS:
        endogenous, external = _frames(duration)
        permuted_endogenous, permuted_external = _frames(duration, reverse=True)
        free = _run_trajectory(
            endogenous, external, use_endogenous=False, use_external=False
        )
        external_only = _run_trajectory(
            endogenous, external, use_endogenous=False, use_external=True
        )
        endogenous_only = _run_trajectory(
            endogenous, external, use_endogenous=True, use_external=False
        )
        joint = _run_trajectory(
            endogenous, external, use_endogenous=True, use_external=True
        )
        repeat = _run_trajectory(
            endogenous, external, use_endogenous=True, use_external=True
        )
        permuted = _run_trajectory(
            permuted_endogenous,
            permuted_external,
            use_endogenous=True,
            use_external=True,
        )
        activation_error = 0.0
        afterimage_error = 0.0
        external_observed = False
        endogenous_observed = False
        for free_tick, external_tick, endogenous_tick, joint_tick in zip(
            free, external_only, endogenous_only, joint, strict=True
        ):
            free_vectors = free_tick[0]
            external_vectors = external_tick[0]
            endogenous_vectors = endogenous_tick[0]
            joint_vectors = joint_tick[0]
            for vector_index in (0, 1):
                errors = tuple(
                    abs(actual - (ext + end - baseline))
                    for actual, ext, end, baseline in zip(
                        joint_vectors[vector_index],
                        external_vectors[vector_index],
                        endogenous_vectors[vector_index],
                        free_vectors[vector_index],
                        strict=True,
                    )
                )
                if vector_index == 0:
                    activation_error = max(activation_error, max(errors))
                else:
                    afterimage_error = max(afterimage_error, max(errors))
            external_l2 = math.sqrt(
                math.fsum(
                    (value - baseline) ** 2
                    for value, baseline in zip(
                        external_vectors[0], free_vectors[0], strict=True
                    )
                )
            )
            endogenous_l2 = math.sqrt(
                math.fsum(
                    (value - baseline) ** 2
                    for value, baseline in zip(
                        endogenous_vectors[0], free_vectors[0], strict=True
                    )
                )
            )
            external_observed |= external_l2 > TOLERANCE
            endogenous_observed |= endogenous_l2 > TOLERANCE

        holdouts = tuple(_holdout_digest() for _ in range(6))
        duration_results.append(
            LongObservationDurationResult(
                duration_seconds=duration,
                measured_ticks=len(joint),
                maximum_activation_superposition_error=activation_error,
                maximum_afterimage_superposition_error=afterimage_error,
                isolated_causes_nonzero=(external_observed and endogenous_observed),
                joint_repeat_digests_equal=all(
                    left[1] == right[1]
                    for left, right in zip(joint, repeat, strict=True)
                ),
                maximum_joint_repeat_vector_error=max(
                    _maximum_vector_error(left[0], right[0])
                    for left, right in zip(joint, repeat, strict=True)
                ),
                permuted_path_observed=any(
                    left[0] != right[0]
                    for left, right in zip(joint, permuted, strict=True)
                ),
                holdout_digests_equal=len({item[1] for item in holdouts}) == 1,
                maximum_holdout_vector_error=max(
                    _maximum_vector_error(holdouts[0][0], item[0])
                    for item in holdouts[1:]
                ),
            )
        )

    results = tuple(duration_results)
    additive = all(
        item.isolated_causes_nonzero
        and item.maximum_activation_superposition_error <= TOLERANCE
        and item.maximum_afterimage_superposition_error <= TOLERANCE
        for item in results
    )
    reproducible = all(
        item.joint_repeat_digests_equal
        and item.maximum_joint_repeat_vector_error <= TOLERANCE
        for item in results
    )
    holdouts_equal = all(
        item.holdout_digests_equal
        and item.maximum_holdout_vector_error <= TOLERANCE
        for item in results
    )
    return PreregisteredLongObservationResult(
        durations=results,
        time_contract_valid=tuple(item.measured_ticks for item in results) == DURATIONS,
        contact_contract_valid=True,
        all_cases_additive=additive,
        all_cases_reproducible=reproducible,
        all_holdouts_equal=holdouts_equal,
        observer_writeback_performed=False,
        runtime_changed=False,
        stop_line=(
            "known_current_additive_one_step_fast_effects_only"
            if additive and reproducible and holdouts_equal
            else "technical_deviation_requires_separate_review"
        ),
    )
