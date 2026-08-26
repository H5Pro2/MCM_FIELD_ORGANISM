"""Locked final order for one callable-factory call execution release."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any
from .public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_preflight_acceptance import PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalPreflightAcceptance
ID="public.av.nasa-earthrise.return-replication.repeatability-single-slot-callable-factory-call-execution-release-final-order.v1"
class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrderError(ValueError): pass
@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrder:
    final_order_id:str; selected_repeat_index:int; final_preflight_acceptance:PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalPreflightAcceptance
    positive_final_preflight_acceptance_bound:bool; exactly_one_final_lock_step_derived:bool; final_lock_step_one_time:bool; final_lock_step_unconsumed:bool
    callable_identity_bound:bool; gate_step_unselected:bool; gate_step_untouched:bool; gate_step_still_unexecuted:bool; selected_slot_still_fresh:bool; actual_release_granted:bool; final_order_complete:bool
    callable_factory_reference_stored:bool=False; gate_factory_reference_stored:bool=False; callable_reference_stored:bool=False; factory_function_called:bool=False; callable_factory_called:bool=False; gate_factory_called:bool=False
    callable_object_created:bool=False; gate_object_created:bool=False; constructor_invoked:bool=False; binding_performed:bool=False; scheduler_available:bool=False; media_decode_allowed:bool=False; receptor_feed_allowed:bool=False
    start_release_granted:bool=False; repeatability_run_allowed:bool=False; repeat_run_started:bool=False; stability_threshold_defined:bool=False; memory_claim_allowed:bool=False; meaning_claim_allowed:bool=False; organization_claim_allowed:bool=False; ai_claim_allowed:bool=False
    def __post_init__(self):
        error=PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrderError; a=self.final_preflight_acceptance; source=a.final_preflight.execution_order_acceptance.execution_order.execution_preflight_acceptance.release_execution_preflight.release_order_acceptance.release_order.release_preflight_acceptance.release_preflight
        if self.selected_repeat_index not in (1,2,3) or a.selected_repeat_index!=self.selected_repeat_index: raise error("selected repeat index mismatch")
        if not self.final_order_id.endswith(f".repeat-{self.selected_repeat_index}.v1"): raise error("final order identity mismatch")
        c,g=source.release_candidate_step,source.untouched_gate_factory_step
        if c.role!="callable_factory" or c.executed or not c.one_time_future_step: raise error("final lock step must remain unconsumed")
        if g.role!="gate_factory" or g.executed or not g.one_time_future_step: raise error("gate step must remain untouched")
        required=(self.positive_final_preflight_acceptance_bound,self.exactly_one_final_lock_step_derived,self.final_lock_step_one_time,self.final_lock_step_unconsumed,self.callable_identity_bound,self.gate_step_unselected,self.gate_step_untouched,self.gate_step_still_unexecuted,self.selected_slot_still_fresh,self.final_order_complete)
        forbidden=tuple(getattr(self,n) for n in ("actual_release_granted","callable_factory_reference_stored","gate_factory_reference_stored","callable_reference_stored","factory_function_called","callable_factory_called","gate_factory_called","callable_object_created","gate_object_created","constructor_invoked","binding_performed","scheduler_available","media_decode_allowed","receptor_feed_allowed","start_release_granted","repeatability_run_allowed","repeat_run_started","stability_threshold_defined","memory_claim_allowed","meaning_claim_allowed","organization_claim_allowed","ai_claim_allowed"))
        if not all(required) or any(forbidden): raise error("final order remains fully non-executable")
def order_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final(a:PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalPreflightAcceptance)->PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrder:
    error=PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrderError
    if not isinstance(a,PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalPreflightAcceptance): raise error("wrong acceptance type")
    required=(a.positive_final_preflight_accepted,a.exactly_one_final_lock_candidate_accepted,a.final_lock_candidate_unconsumed_accepted,a.actual_release_absence_accepted,a.callable_identity_binding_accepted,a.gate_step_untouched_accepted,a.selected_slot_still_fresh,a.acceptance_complete)
    forbidden=tuple(getattr(a,n) for n in ("actual_release_granted","callable_factory_reference_stored","gate_factory_reference_stored","callable_reference_stored","factory_function_called","callable_factory_called","gate_factory_called","callable_object_created","gate_object_created","constructor_invoked","binding_performed","scheduler_available","media_decode_allowed","receptor_feed_allowed","start_release_granted","repeatability_run_allowed","repeat_run_started","memory_claim_allowed","meaning_claim_allowed","organization_claim_allowed","ai_claim_allowed"))
    if not all(required) or any(forbidden): raise error("complete locked final preflight acceptance required")
    i=a.selected_repeat_index; return PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrder(f"{ID}.repeat-{i}.v1",i,a,True,True,True,True,True,True,True,True,True,False,True)
def execute_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_order(o:PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrder)->None:
    del o; raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrderError("factory call execution release remains locked")
def public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_order_to_jsonable(o:PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrder)->dict[str,Any]: return asdict(o)
