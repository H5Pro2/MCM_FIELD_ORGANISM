"""Locked execution order for one callable-factory call."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_preflight_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionPreflightAcceptance,
)
from .public_av_return_replication_repeatability_single_slot_factory_execution_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep,
)


SINGLE_SLOT_CALLABLE_FACTORY_CALL_EXECUTION_ORDER_ID = (
    "public.av.nasa-earthrise.return-replication."
    "repeatability-single-slot-callable-factory-call-execution-order.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrderError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrder:
    execution_order_id: str
    selected_repeat_index: int
    call_execution_preflight_acceptance_id: str
    call_execution_preflight_id: str
    callable_factory_call_order_acceptance_id: str
    callable_factory_call_order_id: str
    future_callable_call_execution_step: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep
    untouched_gate_factory_step: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep
    future_callable_call_execution_step_id: str
    untouched_gate_factory_step_id: str
    future_callable_factory_order_id: str
    future_gate_factory_order_id: str
    callable_factory_identity_id: str
    callable_constructor_identity_id: str
    future_callable_object_id: str
    gate_factory_identity_id: str
    gate_constructor_identity_id: str
    future_gate_object_id: str
    logical_callable_id: str
    logical_gate_id: str
    reserved_executor_id: str
    source_id: str
    positive_call_execution_preflight_acceptance_bound: bool
    exactly_one_future_callable_call_execution_step: bool
    callable_call_execution_step_one_time: bool
    callable_call_execution_step_unexecuted: bool
    callable_factory_identity_bound: bool
    callable_constructor_identity_bound: bool
    future_callable_object_identity_bound: bool
    gate_factory_step_unselected: bool
    gate_factory_step_untouched: bool
    gate_factory_step_still_unexecuted: bool
    selected_slot_still_fresh: bool
    callable_factory_call_execution_order_complete: bool
    other_slots_unselected: tuple[int, ...]
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
        error = PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrderError
        if self.selected_repeat_index not in (1, 2, 3):
            raise error("selected repeat index must be one of 1, 2, 3")
        suffix = f".repeat-{self.selected_repeat_index}.v1"
        indexed_ids = (
            self.execution_order_id, self.call_execution_preflight_acceptance_id,
            self.call_execution_preflight_id, self.callable_factory_call_order_acceptance_id,
            self.callable_factory_call_order_id, self.future_callable_call_execution_step_id,
            self.untouched_gate_factory_step_id, self.future_callable_factory_order_id,
            self.future_gate_factory_order_id, self.callable_factory_identity_id,
            self.callable_constructor_identity_id, self.future_callable_object_id,
            self.gate_factory_identity_id, self.gate_constructor_identity_id,
            self.future_gate_object_id,
        )
        if not all(identifier.endswith(suffix) for identifier in indexed_ids):
            raise error("call execution order identities must match selected repeat index")
        step = self.future_callable_call_execution_step
        gate = self.untouched_gate_factory_step
        if not (
            step.step_index == 1 and step.role == "callable_factory"
            and step.step_id == self.future_callable_call_execution_step_id
            and step.factory_order_id == self.future_callable_factory_order_id
            and step.factory_identity_id == self.callable_factory_identity_id
            and step.constructor_identity_id == self.callable_constructor_identity_id
            and step.future_object_id == self.future_callable_object_id
            and step.one_time_future_step and not step.executed
        ):
            raise error("future callable factory call execution step must remain one-time and unexecuted")
        if not (
            gate.step_index == 2 and gate.role == "gate_factory"
            and gate.step_id == self.untouched_gate_factory_step_id
            and gate.factory_order_id == self.future_gate_factory_order_id
            and gate.factory_identity_id == self.gate_factory_identity_id
            and gate.constructor_identity_id == self.gate_constructor_identity_id
            and gate.future_object_id == self.future_gate_object_id
            and gate.one_time_future_step and not gate.executed
        ):
            raise error("gate factory step must remain unselected, untouched, and unexecuted")
        expected = tuple(index for index in (1, 2, 3) if index != self.selected_repeat_index)
        if tuple(self.other_slots_unselected) != expected:
            raise error("other slots must remain unselected")
        required = (
            self.positive_call_execution_preflight_acceptance_bound,
            self.exactly_one_future_callable_call_execution_step,
            self.callable_call_execution_step_one_time,
            self.callable_call_execution_step_unexecuted,
            self.callable_factory_identity_bound,
            self.callable_constructor_identity_bound,
            self.future_callable_object_identity_bound,
            self.gate_factory_step_unselected,
            self.gate_factory_step_untouched,
            self.gate_factory_step_still_unexecuted,
            self.selected_slot_still_fresh,
            self.callable_factory_call_execution_order_complete,
        )
        forbidden = (
            self.callable_factory_reference_stored, self.gate_factory_reference_stored,
            self.callable_reference_stored, self.factory_function_called,
            self.callable_factory_called, self.gate_factory_called,
            self.callable_object_created, self.gate_object_created,
            self.constructor_invoked, self.binding_performed, self.scheduler_available,
            self.media_decode_allowed, self.receptor_feed_allowed,
            self.start_release_granted, self.repeatability_run_allowed,
            self.repeat_run_started, self.stability_threshold_defined,
            self.memory_claim_allowed, self.meaning_claim_allowed,
            self.organization_claim_allowed, self.ai_claim_allowed,
        )
        if not all(required) or any(forbidden):
            raise error("callable factory call execution order remains fully non-executable")
        object.__setattr__(self, "other_slots_unselected", tuple(self.other_slots_unselected))


def order_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionPreflightAcceptance,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrder:
    error = PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrderError
    if not isinstance(
        acceptance,
        PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionPreflightAcceptance,
    ):
        raise error("single-slot callable factory call execution preflight acceptance has the wrong type")
    required = (
        acceptance.positive_call_execution_preflight_accepted,
        acceptance.exactly_one_call_execution_candidate_accepted,
        acceptance.callable_factory_call_candidate_unconsumed_accepted,
        acceptance.callable_identity_binding_accepted,
        acceptance.gate_factory_step_unselected_accepted,
        acceptance.gate_factory_step_untouched_accepted,
        acceptance.gate_factory_step_unexecuted_accepted,
        acceptance.selected_slot_still_fresh,
        acceptance.call_execution_preflight_acceptance_complete,
    )
    forbidden = (
        acceptance.callable_factory_reference_stored, acceptance.gate_factory_reference_stored,
        acceptance.callable_reference_stored, acceptance.factory_function_called,
        acceptance.callable_factory_called, acceptance.gate_factory_called,
        acceptance.callable_object_created, acceptance.gate_object_created,
        acceptance.constructor_invoked, acceptance.binding_performed,
        acceptance.scheduler_available, acceptance.media_decode_allowed,
        acceptance.receptor_feed_allowed, acceptance.start_release_granted,
        acceptance.repeatability_run_allowed, acceptance.repeat_run_started,
    )
    if not all(required) or any(forbidden):
        raise error("one complete fresh callable factory call execution preflight acceptance is required")
    fields = (
        "selected_repeat_index", "call_execution_preflight_id",
        "callable_factory_call_order_acceptance_id", "callable_factory_call_order_id",
        "untouched_gate_factory_step", "untouched_gate_factory_step_id",
        "future_callable_factory_order_id", "future_gate_factory_order_id",
        "callable_factory_identity_id", "callable_constructor_identity_id",
        "future_callable_object_id", "gate_factory_identity_id",
        "gate_constructor_identity_id", "future_gate_object_id",
        "logical_callable_id", "logical_gate_id", "reserved_executor_id",
        "source_id", "other_slots_unselected",
    )
    carried = {field: getattr(acceptance, field) for field in fields}
    index = acceptance.selected_repeat_index
    return PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrder(
        execution_order_id=f"{SINGLE_SLOT_CALLABLE_FACTORY_CALL_EXECUTION_ORDER_ID}.repeat-{index}.v1",
        call_execution_preflight_acceptance_id=acceptance.acceptance_id,
        future_callable_call_execution_step=acceptance.accepted_call_execution_candidate_step,
        future_callable_call_execution_step_id=acceptance.accepted_call_execution_candidate_step_id,
        positive_call_execution_preflight_acceptance_bound=True,
        exactly_one_future_callable_call_execution_step=True,
        callable_call_execution_step_one_time=True,
        callable_call_execution_step_unexecuted=True,
        callable_factory_identity_bound=True,
        callable_constructor_identity_bound=True,
        future_callable_object_identity_bound=True,
        gate_factory_step_unselected=True,
        gate_factory_step_untouched=True,
        gate_factory_step_still_unexecuted=True,
        selected_slot_still_fresh=True,
        callable_factory_call_execution_order_complete=True,
        **carried,
    )


def execute_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_order(
    order: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrder,
) -> None:
    del order
    raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrderError(
        "factory call execution is not released by the locked callable factory call execution order"
    )


def public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_order_to_jsonable(
    order: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrder,
) -> dict[str, Any]:
    return asdict(order)
