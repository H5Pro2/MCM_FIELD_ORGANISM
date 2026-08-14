"""Locked final orchestration identities for three repeatability candidates."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_callable_gate_binding_acceptance import (
    PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptance,
)


FINAL_ORCHESTRATION_ID = (
    "public.av.nasa-earthrise.return-replication.repeatability-final-orchestration.v1"
)


class PublicAVReturnReplicationRepeatabilityFinalOrchestrationError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilityStartCandidate:
    repeat_index: int
    order_position: int
    candidate_id: str
    binding_acceptance_id: str
    callable_preparation_id: str
    future_callable_id: str
    reserved_executor_id: str
    reserved_gate_id: str
    slot_binding_id: str
    executor_binding_id: str
    source_id: str
    identity_chain_complete: bool
    order_identity_matches: bool
    fresh_objects_required: bool
    technical_start_candidate: bool
    callable_object_created: bool = False
    gate_instance_created: bool = False
    binding_performed: bool = False
    scheduled: bool = False
    start_release_granted: bool = False
    repeat_run_started: bool = False
    reusable: bool = False

    def __post_init__(self) -> None:
        if self.repeat_index not in (1, 2, 3) or self.order_position != self.repeat_index:
            raise PublicAVReturnReplicationRepeatabilityFinalOrchestrationError(
                "candidate order must match repeat_index 1, 2, 3"
            )
        if not self.candidate_id.endswith(f".repeat-{self.repeat_index}.v1"):
            raise PublicAVReturnReplicationRepeatabilityFinalOrchestrationError(
                "candidate identity does not match repeat_index"
            )
        required = (
            self.identity_chain_complete,
            self.order_identity_matches,
            self.fresh_objects_required,
            self.technical_start_candidate,
        )
        forbidden = (
            self.callable_object_created,
            self.gate_instance_created,
            self.binding_performed,
            self.scheduled,
            self.start_release_granted,
            self.repeat_run_started,
            self.reusable,
        )
        if not all(required) or any(forbidden):
            raise PublicAVReturnReplicationRepeatabilityFinalOrchestrationError(
                "start candidate must remain identity-only, unscheduled, and locked"
            )


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilityFinalOrchestrationContract:
    contract_id: str
    binding_acceptance_id: str
    callable_preparation_contract_id: str
    gate_instantiation_contract_id: str
    start_acceptance_id: str
    repeatability_preflight_id: str
    repeatability_runner_id: str
    source_id: str
    ordered_start_candidates: tuple[
        PublicAVReturnReplicationRepeatabilityStartCandidate, ...
    ]
    candidate_order: tuple[int, int, int]
    all_three_binding_acceptances_carried: bool
    all_candidate_ids_unique: bool
    all_callable_ids_unique: bool
    all_gate_ids_unique: bool
    all_executor_ids_unique: bool
    no_cross_candidate_state_carry: bool
    final_orchestration_contract_complete: bool
    callable_objects_created: bool = False
    gate_instances_created: bool = False
    bindings_performed: bool = False
    scheduler_created: bool = False
    automatic_transition_available: bool = False
    start_release_granted: bool = False
    repeatability_run_allowed: bool = False
    stability_threshold_defined: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        if self.contract_id != FINAL_ORCHESTRATION_ID:
            raise PublicAVReturnReplicationRepeatabilityFinalOrchestrationError(
                "unexpected final orchestration identity"
            )
        indices = tuple(item.repeat_index for item in self.ordered_start_candidates)
        if indices != (1, 2, 3) or self.candidate_order != (1, 2, 3):
            raise PublicAVReturnReplicationRepeatabilityFinalOrchestrationError(
                "final orchestration requires exactly the order 1, 2, 3"
            )
        required = (
            self.all_three_binding_acceptances_carried,
            self.all_candidate_ids_unique,
            self.all_callable_ids_unique,
            self.all_gate_ids_unique,
            self.all_executor_ids_unique,
            self.no_cross_candidate_state_carry,
            self.final_orchestration_contract_complete,
        )
        forbidden = (
            self.callable_objects_created,
            self.gate_instances_created,
            self.bindings_performed,
            self.scheduler_created,
            self.automatic_transition_available,
            self.start_release_granted,
            self.repeatability_run_allowed,
            self.stability_threshold_defined,
            self.memory_claim_allowed,
            self.meaning_claim_allowed,
            self.organization_claim_allowed,
            self.ai_claim_allowed,
        )
        if not all(required) or any(forbidden):
            raise PublicAVReturnReplicationRepeatabilityFinalOrchestrationError(
                "final orchestration cannot create objects, schedule, start runs, or release claims"
            )


def orchestrate_public_av_return_replication_repeatability_candidates(
    acceptance: PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptance,
) -> PublicAVReturnReplicationRepeatabilityFinalOrchestrationContract:
    if not isinstance(
        acceptance,
        PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptance,
    ):
        raise PublicAVReturnReplicationRepeatabilityFinalOrchestrationError(
            "callable-gate binding acceptance has the wrong type"
        )
    if not acceptance.binding_acceptance_complete:
        raise PublicAVReturnReplicationRepeatabilityFinalOrchestrationError(
            "complete callable-gate binding acceptance is required"
        )
    if (
        acceptance.callable_objects_created
        or acceptance.gate_instances_created
        or acceptance.callable_gate_binding_performed
        or acceptance.executor_binding_performed
        or acceptance.start_release_granted
        or acceptance.repeatability_run_allowed
    ):
        raise PublicAVReturnReplicationRepeatabilityFinalOrchestrationError(
            "binding acceptance must remain object-free and run-locked"
        )

    candidates = []
    for slot in acceptance.slot_binding_acceptances:
        if (
            slot.callable_object_created
            or slot.gate_instance_created
            or slot.callable_bound_to_gate
            or slot.executor_bound_to_gate
            or slot.start_release_granted
            or slot.repeat_run_started
        ):
            raise PublicAVReturnReplicationRepeatabilityFinalOrchestrationError(
                f"slot {slot.repeat_index} is no longer a fresh candidate"
            )
        candidates.append(
            PublicAVReturnReplicationRepeatabilityStartCandidate(
                repeat_index=slot.repeat_index,
                order_position=slot.repeat_index,
                candidate_id=f"{FINAL_ORCHESTRATION_ID}.repeat-{slot.repeat_index}.v1",
                binding_acceptance_id=slot.binding_acceptance_id,
                callable_preparation_id=slot.callable_preparation_id,
                future_callable_id=slot.future_callable_id,
                reserved_executor_id=slot.reserved_executor_id,
                reserved_gate_id=slot.reserved_gate_id,
                slot_binding_id=slot.slot_binding_id,
                executor_binding_id=slot.executor_binding_id,
                source_id=slot.source_id,
                identity_chain_complete=True,
                order_identity_matches=True,
                fresh_objects_required=True,
                technical_start_candidate=True,
            )
        )

    candidate_ids = tuple(item.candidate_id for item in candidates)
    callable_ids = tuple(item.future_callable_id for item in candidates)
    gate_ids = tuple(item.reserved_gate_id for item in candidates)
    executor_ids = tuple(item.reserved_executor_id for item in candidates)
    return PublicAVReturnReplicationRepeatabilityFinalOrchestrationContract(
        contract_id=FINAL_ORCHESTRATION_ID,
        binding_acceptance_id=acceptance.acceptance_id,
        callable_preparation_contract_id=acceptance.callable_preparation_contract_id,
        gate_instantiation_contract_id=acceptance.gate_instantiation_contract_id,
        start_acceptance_id=acceptance.start_acceptance_id,
        repeatability_preflight_id=acceptance.repeatability_preflight_id,
        repeatability_runner_id=acceptance.repeatability_runner_id,
        source_id=acceptance.source_id,
        ordered_start_candidates=tuple(candidates),
        candidate_order=(1, 2, 3),
        all_three_binding_acceptances_carried=True,
        all_candidate_ids_unique=len(set(candidate_ids)) == 3,
        all_callable_ids_unique=len(set(callable_ids)) == 3,
        all_gate_ids_unique=len(set(gate_ids)) == 3,
        all_executor_ids_unique=len(set(executor_ids)) == 3,
        no_cross_candidate_state_carry=True,
        final_orchestration_contract_complete=True,
    )


def start_public_av_return_replication_repeatability_orchestration(
    contract: PublicAVReturnReplicationRepeatabilityFinalOrchestrationContract,
) -> None:
    del contract
    raise PublicAVReturnReplicationRepeatabilityFinalOrchestrationError(
        "repeatability start is not released by the locked final orchestration contract"
    )


def public_av_return_replication_repeatability_final_orchestration_to_jsonable(
    contract: PublicAVReturnReplicationRepeatabilityFinalOrchestrationContract,
) -> dict[str, Any]:
    return asdict(contract)
