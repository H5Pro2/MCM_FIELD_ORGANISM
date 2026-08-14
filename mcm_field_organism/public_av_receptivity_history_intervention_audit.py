"""Controlled receptor-history intervention for a repeated world contact."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .local_adaptive_receptivity import (
    LocalAdaptiveReceptivityConfig,
    LocalReceptivityState,
    run_adaptive_receptivity_field,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .public_av_local_adaptive_receptivity_cauchy_convergence_audit import (
    CAUCHY_AUDIT_CONTACT_TICKS,
    CAUCHY_AUDIT_DURATION_TICKS,
    CAUCHY_AUDIT_LEAK_RATE_PER_SECOND,
    CAUCHY_AUDIT_VECTOR_ROLES,
)
from .public_av_local_adaptive_receptivity_coupling_scheme_audit import (
    COUPLING_AUDIT_SCHEMES,
    _run_coupled_gap,
)
from .public_av_local_adaptive_receptivity_partition_audit import (
    _component_vectors,
    _linf,
    _partition_ticks,
    _state_record,
)
from .public_av_return_resolution_curve import _shift_sequences
from .public_av_six_arm_field_execution import _sequences
from .public_av_two_stage_return_execution import _fresh_field, _steps
from .public_media_source_contract import PublicMediaSourceContract
from .asynchronous_receptor_events import audit_asynchronous_receptor_events


HISTORY_INTERVENTION_ALPHA_AXIS = (0.5, 1.0)
HISTORY_INTERVENTION_PARTITION_COUNT = 320
HISTORY_INTERVENTION_ARM_IDS = (
    "carried_receptivity",
    "reset_receptivity",
    "identical_carried_control",
)
HISTORY_INTERVENTION_ROLES = tuple(CAUCHY_AUDIT_VECTOR_ROLES)
HISTORY_INTERVENTION_CONTACT_TICKS = CAUCHY_AUDIT_CONTACT_TICKS


class PublicAVReceptivityHistoryInterventionError(ValueError):
    pass


def _validated_axes(alpha: float, scheme: str) -> tuple[float, str]:
    alpha = float(alpha)
    if alpha not in HISTORY_INTERVENTION_ALPHA_AXIS:
        raise PublicAVReceptivityHistoryInterventionError(
            "alpha must belong to the preregistered history-intervention axis"
        )
    if scheme not in COUPLING_AUDIT_SCHEMES:
        raise PublicAVReceptivityHistoryInterventionError(
            "scheme must belong to the preregistered coupling axis"
        )
    return alpha, scheme


def _vector_differences(left, right) -> dict[str, float]:
    return {
        role: _linf(left[role], right[role])
        for role in HISTORY_INTERVENTION_ROLES
    }


def _require_identical_control(differences: dict[str, float]) -> None:
    if set(differences) != set(HISTORY_INTERVENTION_ROLES):
        raise PublicAVReceptivityHistoryInterventionError(
            "identical control must contain every measurement role"
        )
    if any(value != 0.0 for value in differences.values()):
        raise PublicAVReceptivityHistoryInterventionError(
            "identical carried control diverged"
        )


def _second_contact_event_timeline(
    shifted_sequences, contact_start: int
) -> tuple[list[dict[str, object]], str]:
    audit = audit_asynchronous_receptor_events(shifted_sequences)
    ordered = sorted(
        (
            event
            for group in audit.completion_groups
            for event in group.events
            if contact_start < event.completion_tick
            <= contact_start + CAUCHY_AUDIT_CONTACT_TICKS
        ),
        key=lambda event: (
            event.completion_tick,
            event.modality_id,
            event.snapshot_id,
        ),
    )
    timeline = [
        {
            "sequence_index": index,
            "sensor_path": event.modality_id,
            "elapsed_ticks": event.completion_tick - contact_start,
        }
        for index, event in enumerate(ordered)
    ]
    digest = hashlib.sha256(
        json.dumps(
            timeline, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()
    return timeline, digest


def _require_event_timeline_digest(
    sequences,
    expected_digest: str | None,
) -> str:
    _, actual_digest = _second_contact_event_timeline(sequences, 0)
    if expected_digest is not None and actual_digest != expected_digest:
        raise PublicAVReceptivityHistoryInterventionError(
            "receptor event timeline digest differs from preregistration"
        )
    return actual_digest


def _exact_trace_onset_interval(
    trace_differences: list[dict[str, object]], role: str,
    event_timeline: list[dict[str, object]],
) -> dict[str, object] | None:
    interval_start = 0
    for trace_index, point in enumerate(trace_differences):
        interval_end = point["elapsed_ticks"]
        value = point["carried_to_reset_linf"][role]
        if value != 0.0:
            return {
                "trace_index": trace_index,
                "interval_start_elapsed_ticks": interval_start,
                "interval_end_elapsed_ticks": interval_end,
                "event_sequence_indices": [
                    event["sequence_index"]
                    for event in event_timeline
                    if interval_start < event["elapsed_ticks"] <= interval_end
                ],
            }
        interval_start = interval_end
    return None


def _run_contact_trace(
    start_field,
    start_receptivity,
    shifted_sequences,
    contact_start,
    substrate,
    afterimage,
    receptivity_config,
    dissipation,
):
    _, event_timeline_digest = _second_contact_event_timeline(
        shifted_sequences, contact_start
    )
    field = start_field
    receptivity = start_receptivity
    trace = []
    vector_trace = []
    source_support_count = None
    for interval_start, interval_end in _partition_ticks(
        contact_start, CAUCHY_AUDIT_CONTACT_TICKS,
        HISTORY_INTERVENTION_PARTITION_COUNT,
    ):
        run = run_adaptive_receptivity_field(
            field,
            receptivity,
            shifted_sequences,
            _steps(shifted_sequences, interval_start, interval_end),
            substrate,
            afterimage,
            receptivity_config,
            dissipation,
        )
        field = run.field
        receptivity = run.receptivity
        source_support_count = run.source_support_count
        trace.append(_state_record(
            field, receptivity, interval_end - contact_start
        ))
        vector_trace.append(_component_vectors(field, receptivity))
    return (
        field,
        receptivity,
        source_support_count,
        trace,
        vector_trace,
        event_timeline_digest,
    )


def execute_public_av_receptivity_history_intervention_shard(
    path: Path,
    contract: PublicMediaSourceContract,
    alpha: float,
    scheme: str,
    *,
    start_tick: int = 0,
    expected_event_timeline_digest: str | None = None,
) -> dict[str, object]:
    alpha, scheme = _validated_axes(alpha, scheme)
    if not isinstance(path, Path) or not path.is_file():
        raise PublicAVReceptivityHistoryInterventionError(
            "audited media file is required"
        )
    if not isinstance(contract, PublicMediaSourceContract):
        raise PublicAVReceptivityHistoryInterventionError(
            "source contract is required"
        )

    sequences = _sequences(path, contract, start_tick=start_tick)
    source_event_timeline_digest = _require_event_timeline_digest(
        sequences, expected_event_timeline_digest
    )
    substrate = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage = NeutralFastAfterimageConfig(0.5)
    dissipation = NeutralFieldDissipationConfig(CAUCHY_AUDIT_LEAK_RATE_PER_SECOND)
    config = LocalAdaptiveReceptivityConfig(alpha)
    initial_field = _fresh_field(sequences)
    first_contact = run_adaptive_receptivity_field(
        initial_field,
        LocalReceptivityState.fresh(initial_field),
        sequences,
        _steps(sequences, 0, CAUCHY_AUDIT_CONTACT_TICKS),
        substrate,
        afterimage,
        config,
        dissipation,
    )

    groups = []
    for gap_ticks in CAUCHY_AUDIT_DURATION_TICKS:
        gap_field, carried_receptivity, gap_trace = _run_coupled_gap(
            first_contact.field,
            first_contact.receptivity,
            CAUCHY_AUDIT_CONTACT_TICKS,
            gap_ticks,
            HISTORY_INTERVENTION_PARTITION_COUNT,
            scheme,
            substrate,
            afterimage,
            config,
            dissipation,
        )
        reset_receptivity = LocalReceptivityState.fresh(gap_field)
        contact_start = CAUCHY_AUDIT_CONTACT_TICKS + gap_ticks
        shifted = _shift_sequences(sequences, contact_start)
        event_timeline, expected_event_timeline_digest = (
            _second_contact_event_timeline(shifted, contact_start)
        )
        starts = (
            carried_receptivity,
            reset_receptivity,
            carried_receptivity,
        )
        runs = []
        for arm_id, start_receptivity in zip(
            HISTORY_INTERVENTION_ARM_IDS, starts, strict=True
        ):
            (
                field,
                receptivity,
                event_count,
                trace,
                vector_trace,
                arm_event_timeline_digest,
            ) = _run_contact_trace(
                gap_field,
                start_receptivity,
                shifted,
                contact_start,
                substrate,
                afterimage,
                config,
                dissipation,
            )
            runs.append({
                "arm_id": arm_id,
                "event_count": event_count,
                "second_contact_event_timeline_digest": (
                    arm_event_timeline_digest
                ),
                "start_layer_digest": gap_field.layer.digest(),
                "start_snapshot_digest": gap_field.snapshot().digest(),
                "start_receptivity": _state_record(
                    gap_field, start_receptivity, 0
                )["receptivity"],
                "trace": trace,
                "vector_trace": vector_trace,
                "final": _state_record(
                    field, receptivity, CAUCHY_AUDIT_CONTACT_TICKS
                ),
                "vectors": _component_vectors(field, receptivity),
            })

        carried, reset, identical = runs
        start_vectors = {
            "carried": _component_vectors(gap_field, carried_receptivity),
            "reset": _component_vectors(gap_field, reset_receptivity),
        }
        start_differences = _vector_differences(
            start_vectors["carried"], start_vectors["reset"]
        )
        trace_differences = []
        for carried_point, carried_vectors, reset_vectors in zip(
            carried["trace"], carried["vector_trace"], reset["vector_trace"],
            strict=True,
        ):
            trace_differences.append({
                "elapsed_ticks": carried_point["elapsed_ticks"],
                "carried_to_reset_linf": _vector_differences(
                    carried_vectors, reset_vectors
                ),
            })
        identical_differences = _vector_differences(
            carried["vectors"], identical["vectors"]
        )
        _require_identical_control(identical_differences)
        arm_event_timeline_digests = [
            arm["second_contact_event_timeline_digest"] for arm in runs
        ]
        if any(
            digest != expected_event_timeline_digest
            for digest in arm_event_timeline_digests
        ):
            raise PublicAVReceptivityHistoryInterventionError(
                "second-contact event timeline diverged between arms"
            )
        trace_onset_intervals = {
            role: _exact_trace_onset_interval(
                trace_differences, role, event_timeline
            )
            for role in ("activation", "afterimage", "local_energy")
        }
        for arm in runs:
            del arm["vectors"]
            del arm["vector_trace"]
        groups.append({
            "alpha_per_amplitude_second": alpha,
            "scheme": scheme,
            "gap_ticks": gap_ticks,
            "partition_count": HISTORY_INTERVENTION_PARTITION_COUNT,
            "gap_trace": gap_trace,
            "intervention": "reset_receptivity_only_before_second_contact",
            "field_start_shared_between_arms": True,
            "active_update_rule_shared_between_arms": True,
            "sensor_events_and_time_axis_shared_between_arms": True,
            "second_contact_event_timeline": event_timeline,
            "second_contact_event_timeline_digest": (
                expected_event_timeline_digest
            ),
            "arm_event_timeline_digests_identical": True,
            "trace_onset_intervals": trace_onset_intervals,
            "carried_to_reset_start_linf": start_differences,
            "carried_to_reset_trace": trace_differences,
            "arms": runs,
            "identical_control_final_linf": identical_differences,
            "identical_control_passed": True,
        })

    return {
        "audit_id": (
            "public.av.nasa-earthrise.receptivity-history-intervention-"
            "alpha-scheme-shard.v1"
        ),
        "source_id": contract.source_id,
        "source_start_tick": start_tick,
        "source_end_tick": start_tick + HISTORY_INTERVENTION_CONTACT_TICKS,
        "source_event_timeline_digest": source_event_timeline_digest,
        "alpha_axis": [alpha],
        "schemes": [scheme],
        "gap_duration_ticks": list(CAUCHY_AUDIT_DURATION_TICKS),
        "contact_ticks": CAUCHY_AUDIT_CONTACT_TICKS,
        "partition_count": HISTORY_INTERVENTION_PARTITION_COUNT,
        "arm_ids": list(HISTORY_INTERVENTION_ARM_IDS),
        "measurement_roles": list(HISTORY_INTERVENTION_ROLES),
        "intervention_changes_receptivity_initialization_only": True,
        "groups": groups,
        "shard_axes": ["alpha", "scheme"],
        "shard_values": {"alpha": alpha, "scheme": scheme},
        "threshold_defined": False,
        "preferred_alpha_selected": False,
        "preferred_scheme_selected": False,
        "memory_claim_allowed": False,
        "meaning_claim_allowed": False,
        "organization_claim_allowed": False,
        "consciousness_claim_allowed": False,
        "ai_claim_allowed": False,
    }
