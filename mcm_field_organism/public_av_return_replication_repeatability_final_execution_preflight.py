"""Locked final execution preflight for repeatability start candidates."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_final_orchestration import (
    PublicAVReturnReplicationRepeatabilityFinalOrchestrationContract,
)
from .public_media_source_contract import PublicMediaSourceAudit


FINAL_EXECUTION_PREFLIGHT_ID = (
    "public.av.nasa-earthrise.return-replication."
    "repeatability-final-execution-preflight.v1"
)


class PublicAVReturnReplicationRepeatabilityFinalExecutionPreflightError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilityFinalExecutionSlotPreflight:
    repeat_index: int
    order_position: int
    slot_preflight_id: str
    candidate_id: str
    future_callable_id: str
    reserved_executor_id: str
    reserved_gate_id: str
    source_id: str
    candidate_identity_matches: bool
    source_identity_matches: bool
    one_shot_state_fresh: bool
    object_state_fresh: bool
    ordered_candidate_accepted: bool
    callable_object_created: bool = False
    gate_instance_created: bool = False
    binding_performed: bool = False
    scheduled: bool = False
    start_release_granted: bool = False
    repeat_run_started: bool = False

    def __post_init__(self) -> None:
        if self.repeat_index not in (1, 2, 3) or self.order_position != self.repeat_index:
            raise PublicAVReturnReplicationRepeatabilityFinalExecutionPreflightError(
                "slot preflight order must match repeat_index"
            )
        if not self.slot_preflight_id.endswith(f".repeat-{self.repeat_index}.v1"):
            raise PublicAVReturnReplicationRepeatabilityFinalExecutionPreflightError(
                "slot preflight identity does not match repeat_index"
            )
        required = (
            self.candidate_identity_matches,
            self.source_identity_matches,
            self.one_shot_state_fresh,
            self.object_state_fresh,
            self.ordered_candidate_accepted,
        )
        forbidden = (
            self.callable_object_created,
            self.gate_instance_created,
            self.binding_performed,
            self.scheduled,
            self.start_release_granted,
            self.repeat_run_started,
        )
        if not all(required) or any(forbidden):
            raise PublicAVReturnReplicationRepeatabilityFinalExecutionPreflightError(
                "slot execution preflight must remain fresh and start-locked"
            )


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilityFinalExecutionPreflight:
    preflight_id: str
    final_orchestration_contract_id: str
    binding_acceptance_id: str
    repeatability_preflight_id: str
    repeatability_runner_id: str
    source_id: str
    observed_source_size_bytes: int
    observed_source_sha1: str
    slot_preflights: tuple[
        PublicAVReturnReplicationRepeatabilityFinalExecutionSlotPreflight, ...
    ]
    source_audit_accepted: bool
    source_file_present: bool
    source_size_matches: bool
    source_sha1_matches: bool
    receptor_release_still_locked: bool
    orchestration_identity_unchanged: bool
    all_three_candidates_ordered: bool
    all_three_one_shot_states_fresh: bool
    final_execution_preflight_complete: bool
    callable_objects_created: bool = False
    gate_instances_created: bool = False
    bindings_performed: bool = False
    scheduler_available: bool = False
    start_release_granted: bool = False
    repeatability_run_allowed: bool = False
    media_decode_allowed: bool = False
    receptor_feed_allowed: bool = False
    stability_threshold_defined: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        if self.preflight_id != FINAL_EXECUTION_PREFLIGHT_ID:
            raise PublicAVReturnReplicationRepeatabilityFinalExecutionPreflightError(
                "unexpected final execution preflight identity"
            )
        if tuple(item.repeat_index for item in self.slot_preflights) != (1, 2, 3):
            raise PublicAVReturnReplicationRepeatabilityFinalExecutionPreflightError(
                "final execution preflight requires slots 1, 2, 3"
            )
        required = (
            self.source_audit_accepted,
            self.source_file_present,
            self.source_size_matches,
            self.source_sha1_matches,
            self.receptor_release_still_locked,
            self.orchestration_identity_unchanged,
            self.all_three_candidates_ordered,
            self.all_three_one_shot_states_fresh,
            self.final_execution_preflight_complete,
        )
        forbidden = (
            self.callable_objects_created,
            self.gate_instances_created,
            self.bindings_performed,
            self.scheduler_available,
            self.start_release_granted,
            self.repeatability_run_allowed,
            self.media_decode_allowed,
            self.receptor_feed_allowed,
            self.stability_threshold_defined,
            self.memory_claim_allowed,
            self.meaning_claim_allowed,
            self.organization_claim_allowed,
            self.ai_claim_allowed,
        )
        if not all(required) or any(forbidden):
            raise PublicAVReturnReplicationRepeatabilityFinalExecutionPreflightError(
                "final execution preflight cannot release objects, scheduling, runs, receptors, or claims"
            )


def audit_public_av_return_replication_repeatability_final_execution_preflight(
    orchestration: PublicAVReturnReplicationRepeatabilityFinalOrchestrationContract,
    source_audit: PublicMediaSourceAudit,
) -> PublicAVReturnReplicationRepeatabilityFinalExecutionPreflight:
    if not isinstance(
        orchestration,
        PublicAVReturnReplicationRepeatabilityFinalOrchestrationContract,
    ):
        raise PublicAVReturnReplicationRepeatabilityFinalExecutionPreflightError(
            "final orchestration has the wrong type"
        )
    if not isinstance(source_audit, PublicMediaSourceAudit):
        raise PublicAVReturnReplicationRepeatabilityFinalExecutionPreflightError(
            "source audit has the wrong type"
        )
    if not orchestration.final_orchestration_contract_complete:
        raise PublicAVReturnReplicationRepeatabilityFinalExecutionPreflightError(
            "complete final orchestration is required"
        )
    if not (
        source_audit.accepted
        and source_audit.file_present
        and source_audit.size_matches
        and source_audit.sha1_matches
        and not source_audit.receptor_release_granted
    ):
        raise PublicAVReturnReplicationRepeatabilityFinalExecutionPreflightError(
            "accepted integrity-only source audit is required"
        )
    if source_audit.source_id != orchestration.source_id:
        raise PublicAVReturnReplicationRepeatabilityFinalExecutionPreflightError(
            "source identity differs from final orchestration"
        )
    if (
        orchestration.callable_objects_created
        or orchestration.gate_instances_created
        or orchestration.bindings_performed
        or orchestration.scheduler_created
        or orchestration.start_release_granted
        or orchestration.repeatability_run_allowed
    ):
        raise PublicAVReturnReplicationRepeatabilityFinalExecutionPreflightError(
            "orchestration must remain object-free and run-locked"
        )

    slots = []
    for candidate in orchestration.ordered_start_candidates:
        if (
            candidate.callable_object_created
            or candidate.gate_instance_created
            or candidate.binding_performed
            or candidate.scheduled
            or candidate.start_release_granted
            or candidate.repeat_run_started
        ):
            raise PublicAVReturnReplicationRepeatabilityFinalExecutionPreflightError(
                f"candidate {candidate.repeat_index} is no longer fresh"
            )
        slots.append(
            PublicAVReturnReplicationRepeatabilityFinalExecutionSlotPreflight(
                repeat_index=candidate.repeat_index,
                order_position=candidate.order_position,
                slot_preflight_id=(
                    f"{FINAL_EXECUTION_PREFLIGHT_ID}.repeat-{candidate.repeat_index}.v1"
                ),
                candidate_id=candidate.candidate_id,
                future_callable_id=candidate.future_callable_id,
                reserved_executor_id=candidate.reserved_executor_id,
                reserved_gate_id=candidate.reserved_gate_id,
                source_id=candidate.source_id,
                candidate_identity_matches=True,
                source_identity_matches=candidate.source_id == source_audit.source_id,
                one_shot_state_fresh=True,
                object_state_fresh=True,
                ordered_candidate_accepted=True,
            )
        )

    return PublicAVReturnReplicationRepeatabilityFinalExecutionPreflight(
        preflight_id=FINAL_EXECUTION_PREFLIGHT_ID,
        final_orchestration_contract_id=orchestration.contract_id,
        binding_acceptance_id=orchestration.binding_acceptance_id,
        repeatability_preflight_id=orchestration.repeatability_preflight_id,
        repeatability_runner_id=orchestration.repeatability_runner_id,
        source_id=orchestration.source_id,
        observed_source_size_bytes=source_audit.observed_size_bytes or 0,
        observed_source_sha1=source_audit.observed_sha1 or "",
        slot_preflights=tuple(slots),
        source_audit_accepted=True,
        source_file_present=True,
        source_size_matches=True,
        source_sha1_matches=True,
        receptor_release_still_locked=True,
        orchestration_identity_unchanged=True,
        all_three_candidates_ordered=True,
        all_three_one_shot_states_fresh=True,
        final_execution_preflight_complete=True,
    )


def start_public_av_return_replication_repeatability_from_final_preflight(
    preflight: PublicAVReturnReplicationRepeatabilityFinalExecutionPreflight,
) -> None:
    del preflight
    raise PublicAVReturnReplicationRepeatabilityFinalExecutionPreflightError(
        "repeatability run is not released by the locked final execution preflight"
    )


def public_av_return_replication_repeatability_final_execution_preflight_to_jsonable(
    preflight: PublicAVReturnReplicationRepeatabilityFinalExecutionPreflight,
) -> dict[str, Any]:
    return asdict(preflight)
