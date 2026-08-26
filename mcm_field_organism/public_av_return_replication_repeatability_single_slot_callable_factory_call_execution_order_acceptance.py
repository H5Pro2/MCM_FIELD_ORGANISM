"""Locked acceptance of one callable-factory call execution order."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any
from .public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_order import PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrder

ID = "public.av.nasa-earthrise.return-replication.repeatability-single-slot-callable-factory-call-execution-order-acceptance.v1"
class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrderAcceptanceError(ValueError): pass

@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrderAcceptance:
    acceptance_id: str
    selected_repeat_index: int
    execution_order: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrder
    positive_execution_order_accepted: bool
    exactly_one_future_execution_step_accepted: bool
    execution_step_unconsumed_accepted: bool
    gate_step_untouched_accepted: bool
    acceptance_complete: bool
    callable_factory_reference_stored: bool = False
    callable_reference_stored: bool = False
    factory_function_called: bool = False
    callable_factory_called: bool = False
    callable_object_created: bool = False
    constructor_invoked: bool = False
    binding_performed: bool = False
    media_decode_allowed: bool = False
    receptor_feed_allowed: bool = False
    repeat_run_started: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False
    def __post_init__(self) -> None:
        error = PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrderAcceptanceError
        order = self.execution_order
        if self.selected_repeat_index not in (1, 2, 3) or order.selected_repeat_index != self.selected_repeat_index:
            raise error("selected repeat index mismatch")
        if not self.acceptance_id.endswith(f".repeat-{self.selected_repeat_index}.v1"):
            raise error("acceptance identity mismatch")
        step, gate = order.future_callable_call_execution_step, order.untouched_gate_factory_step
        if step.role != "callable_factory" or step.executed or not step.one_time_future_step:
            raise error("callable execution step must remain unconsumed")
        if gate.role != "gate_factory" or gate.executed or not gate.one_time_future_step:
            raise error("gate step must remain untouched")
        required = (self.positive_execution_order_accepted, self.exactly_one_future_execution_step_accepted, self.execution_step_unconsumed_accepted, self.gate_step_untouched_accepted, self.acceptance_complete)
        forbidden = (self.callable_factory_reference_stored, self.callable_reference_stored, self.factory_function_called, self.callable_factory_called, self.callable_object_created, self.constructor_invoked, self.binding_performed, self.media_decode_allowed, self.receptor_feed_allowed, self.repeat_run_started, self.memory_claim_allowed, self.meaning_claim_allowed, self.organization_claim_allowed, self.ai_claim_allowed)
        if not all(required) or any(forbidden): raise error("execution order acceptance remains non-executable")

def accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_order(order: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrder) -> PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrderAcceptance:
    if not isinstance(order, PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrder):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrderAcceptanceError("wrong order type")
    required=(order.positive_call_execution_preflight_acceptance_bound, order.exactly_one_future_callable_call_execution_step, order.callable_call_execution_step_one_time, order.callable_call_execution_step_unexecuted, order.gate_factory_step_unselected, order.gate_factory_step_untouched, order.gate_factory_step_still_unexecuted, order.callable_factory_call_execution_order_complete)
    forbidden=(order.callable_factory_reference_stored, order.callable_reference_stored, order.factory_function_called, order.callable_factory_called, order.callable_object_created, order.binding_performed, order.media_decode_allowed, order.receptor_feed_allowed, order.repeat_run_started)
    if not all(required) or any(forbidden): raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrderAcceptanceError("fresh locked order required")
    i=order.selected_repeat_index
    return PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrderAcceptance(f"{ID}.repeat-{i}.v1", i, order, True, True, True, True, True)

def execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_call_execution_order(acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrderAcceptance) -> None:
    raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrderAcceptanceError("factory call remains locked")

def public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_order_acceptance_to_jsonable(acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrderAcceptance) -> dict[str, Any]: return asdict(acceptance)
