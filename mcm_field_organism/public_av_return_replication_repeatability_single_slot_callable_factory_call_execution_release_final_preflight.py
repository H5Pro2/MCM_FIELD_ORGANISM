"""Final locked preflight for one callable-factory call release execution step."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any
from .public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_order_acceptance import PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrderAcceptance
ID="public.av.nasa-earthrise.return-replication.repeatability-single-slot-callable-factory-call-execution-release-final-preflight.v1"
class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalPreflightError(ValueError): pass

@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalPreflight:
    preflight_id:str; selected_repeat_index:int
    execution_order_acceptance:PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrderAcceptance
    positive_execution_order_acceptance_bound:bool; exactly_one_final_lock_candidate_bound:bool
    final_lock_candidate_unconsumed:bool; callable_identity_binding_accepted:bool
    gate_step_unselected:bool; gate_step_untouched:bool; gate_step_still_unexecuted:bool
    selected_slot_still_fresh:bool; actual_release_granted:bool; final_preflight_complete:bool
    callable_factory_reference_stored:bool=False; gate_factory_reference_stored:bool=False; callable_reference_stored:bool=False
    factory_function_called:bool=False; callable_factory_called:bool=False; gate_factory_called:bool=False
    callable_object_created:bool=False; gate_object_created:bool=False; constructor_invoked:bool=False; binding_performed:bool=False
    scheduler_available:bool=False; media_decode_allowed:bool=False; receptor_feed_allowed:bool=False; start_release_granted:bool=False
    repeatability_run_allowed:bool=False; repeat_run_started:bool=False; stability_threshold_defined:bool=False
    memory_claim_allowed:bool=False; meaning_claim_allowed:bool=False; organization_claim_allowed:bool=False; ai_claim_allowed:bool=False
    def __post_init__(self):
        error=PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalPreflightError; a=self.execution_order_acceptance; source=a.execution_order.execution_preflight_acceptance.release_execution_preflight.release_order_acceptance.release_order.release_preflight_acceptance.release_preflight
        if self.selected_repeat_index not in (1,2,3) or a.selected_repeat_index!=self.selected_repeat_index: raise error("selected repeat index mismatch")
        if not self.preflight_id.endswith(f".repeat-{self.selected_repeat_index}.v1"): raise error("final preflight identity mismatch")
        candidate,gate=source.release_candidate_step,source.untouched_gate_factory_step
        if candidate.role!="callable_factory" or candidate.executed or not candidate.one_time_future_step: raise error("final lock candidate must remain unconsumed")
        if gate.role!="gate_factory" or gate.executed or not gate.one_time_future_step: raise error("gate step must remain untouched")
        required=(self.positive_execution_order_acceptance_bound,self.exactly_one_final_lock_candidate_bound,self.final_lock_candidate_unconsumed,self.callable_identity_binding_accepted,self.gate_step_unselected,self.gate_step_untouched,self.gate_step_still_unexecuted,self.selected_slot_still_fresh,self.final_preflight_complete)
        forbidden=(self.actual_release_granted,self.callable_factory_reference_stored,self.gate_factory_reference_stored,self.callable_reference_stored,self.factory_function_called,self.callable_factory_called,self.gate_factory_called,self.callable_object_created,self.gate_object_created,self.constructor_invoked,self.binding_performed,self.scheduler_available,self.media_decode_allowed,self.receptor_feed_allowed,self.start_release_granted,self.repeatability_run_allowed,self.repeat_run_started,self.stability_threshold_defined,self.memory_claim_allowed,self.meaning_claim_allowed,self.organization_claim_allowed,self.ai_claim_allowed)
        if not all(required) or any(forbidden): raise error("final preflight remains fully non-executable")

def preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final(a:PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrderAcceptance)->PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalPreflight:
    error=PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalPreflightError
    if not isinstance(a,PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrderAcceptance): raise error("wrong acceptance type")
    required=(a.positive_execution_order_accepted,a.exactly_one_future_execution_step_accepted,a.execution_step_one_time_accepted,a.execution_step_unexecuted_accepted,a.actual_release_absence_accepted,a.callable_identity_accepted,a.gate_step_untouched_accepted,a.selected_slot_still_fresh,a.acceptance_complete)
    forbidden=(a.actual_release_granted,a.callable_factory_reference_stored,a.gate_factory_reference_stored,a.callable_reference_stored,a.factory_function_called,a.callable_factory_called,a.gate_factory_called,a.callable_object_created,a.gate_object_created,a.constructor_invoked,a.binding_performed,a.scheduler_available,a.media_decode_allowed,a.receptor_feed_allowed,a.start_release_granted,a.repeatability_run_allowed,a.repeat_run_started,a.memory_claim_allowed,a.meaning_claim_allowed,a.organization_claim_allowed,a.ai_claim_allowed)
    if not all(required) or any(forbidden): raise error("complete locked execution order acceptance required")
    i=a.selected_repeat_index
    return PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalPreflight(f"{ID}.repeat-{i}.v1",i,a,True,True,True,True,True,True,True,True,False,True)
def execute_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_preflight(p:PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalPreflight)->None:
    del p; raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalPreflightError("factory call execution release remains locked")
def public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_preflight_to_jsonable(p:PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalPreflight)->dict[str,Any]: return asdict(p)
