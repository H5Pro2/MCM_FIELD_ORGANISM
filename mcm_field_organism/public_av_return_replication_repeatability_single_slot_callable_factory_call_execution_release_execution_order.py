"""Locked execution order for one callable-factory call release candidate."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any
from .public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_preflight_acceptance import PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflightAcceptance

ID = "public.av.nasa-earthrise.return-replication.repeatability-single-slot-callable-factory-call-execution-release-execution-order.v1"
class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrderError(ValueError): pass

@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrder:
    execution_order_id: str
    selected_repeat_index: int
    execution_preflight_acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflightAcceptance
    positive_execution_preflight_acceptance_bound: bool
    exactly_one_future_execution_step: bool
    execution_step_one_time: bool
    execution_step_unexecuted: bool
    callable_identity_bound: bool
    gate_step_unselected: bool
    gate_step_untouched: bool
    gate_step_still_unexecuted: bool
    selected_slot_still_fresh: bool
    actual_release_granted: bool
    execution_order_complete: bool
    callable_factory_reference_stored: bool = False
    gate_factory_reference_stored: bool = False
    callable_reference_stored: bool = False
    factory_function_called: bool = False
    callable_factory_called: bool = False
    gate_factory_called: bool = False
    callable_object_created: bool = False
    gate_object_created: bool = False
    constructor_invoked: bool = False
    binding_performed: bool = False
    scheduler_available: bool = False
    media_decode_allowed: bool = False
    receptor_feed_allowed: bool = False
    start_release_granted: bool = False
    repeatability_run_allowed: bool = False
    repeat_run_started: bool = False
    stability_threshold_defined: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False
    def __post_init__(self) -> None:
        error = PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrderError
        acceptance = self.execution_preflight_acceptance
        source = acceptance.release_execution_preflight.release_order_acceptance.release_order.release_preflight_acceptance.release_preflight
        if self.selected_repeat_index not in (1, 2, 3) or acceptance.selected_repeat_index != self.selected_repeat_index: raise error("selected repeat index mismatch")
        if not self.execution_order_id.endswith(f".repeat-{self.selected_repeat_index}.v1"): raise error("execution order identity mismatch")
        candidate, gate = source.release_candidate_step, source.untouched_gate_factory_step
        if candidate.role != "callable_factory" or candidate.executed or not candidate.one_time_future_step: raise error("execution step must remain unexecuted")
        if gate.role != "gate_factory" or gate.executed or not gate.one_time_future_step: raise error("gate step must remain untouched")
        required=(self.positive_execution_preflight_acceptance_bound,self.exactly_one_future_execution_step,self.execution_step_one_time,self.execution_step_unexecuted,self.callable_identity_bound,self.gate_step_unselected,self.gate_step_untouched,self.gate_step_still_unexecuted,self.selected_slot_still_fresh,self.execution_order_complete)
        forbidden=(self.actual_release_granted,self.callable_factory_reference_stored,self.gate_factory_reference_stored,self.callable_reference_stored,self.factory_function_called,self.callable_factory_called,self.gate_factory_called,self.callable_object_created,self.gate_object_created,self.constructor_invoked,self.binding_performed,self.scheduler_available,self.media_decode_allowed,self.receptor_feed_allowed,self.start_release_granted,self.repeatability_run_allowed,self.repeat_run_started,self.stability_threshold_defined,self.memory_claim_allowed,self.meaning_claim_allowed,self.organization_claim_allowed,self.ai_claim_allowed)
        if not all(required) or any(forbidden): raise error("release execution order remains fully non-executable")

def order_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution(acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflightAcceptance) -> PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrder:
    error=PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrderError
    if not isinstance(acceptance,PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflightAcceptance): raise error("wrong acceptance type")
    required=(acceptance.positive_execution_preflight_accepted,acceptance.exactly_one_execution_candidate_accepted,acceptance.execution_candidate_unconsumed_accepted,acceptance.actual_release_absence_accepted,acceptance.callable_identity_binding_accepted,acceptance.gate_step_untouched_accepted,acceptance.selected_slot_still_fresh,acceptance.acceptance_complete)
    forbidden=(acceptance.actual_release_granted,acceptance.callable_factory_reference_stored,acceptance.gate_factory_reference_stored,acceptance.callable_reference_stored,acceptance.factory_function_called,acceptance.callable_factory_called,acceptance.gate_factory_called,acceptance.callable_object_created,acceptance.gate_object_created,acceptance.constructor_invoked,acceptance.binding_performed,acceptance.scheduler_available,acceptance.media_decode_allowed,acceptance.receptor_feed_allowed,acceptance.start_release_granted,acceptance.repeatability_run_allowed,acceptance.repeat_run_started,acceptance.memory_claim_allowed,acceptance.meaning_claim_allowed,acceptance.organization_claim_allowed,acceptance.ai_claim_allowed)
    if not all(required) or any(forbidden): raise error("complete locked preflight acceptance required")
    i=acceptance.selected_repeat_index
    return PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrder(f"{ID}.repeat-{i}.v1",i,acceptance,True,True,True,True,True,True,True,True,True,False,True)

def execute_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_order(order: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrder) -> None:
    del order
    raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrderError("factory call execution release remains locked")

def public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_order_to_jsonable(order: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrder) -> dict[str,Any]: return asdict(order)
