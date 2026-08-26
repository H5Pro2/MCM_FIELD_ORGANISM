"""Locked acceptance of one callable-factory execution order."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_callable_factory_execution_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrder,
)
from .public_av_return_replication_repeatability_single_slot_factory_execution_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep,
)


SINGLE_SLOT_CALLABLE_FACTORY_EXECUTION_ORDER_ACCEPTANCE_ID = (
    "public.av.nasa-earthrise.return-replication."
    "repeatability-single-slot-callable-factory-execution-order-acceptance.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrderAcceptanceError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrderAcceptance:
    acceptance_id: str
    selected_repeat_index: int
    callable_factory_execution_order_id: str
    execution_preflight_acceptance_id: str
    execution_preflight_id: str
    callable_factory_step_order_acceptance_id: str
    callable_factory_step_order_id: str
    first_factory_step_acceptance_id: str
    first_factory_step_preflight_id: str
    factory_execution_order_acceptance_id: str
    factory_execution_order_id: str
    accepted_callable_execution_step: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep
    untouched_gate_factory_step: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep
    accepted_callable_execution_step_id: str
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
    positive_callable_factory_execution_order_accepted: bool
    exactly_one_future_callable_execution_step_accepted: bool
    callable_execution_step_one_time_accepted: bool
    callable_execution_step_unexecuted_accepted: bool
    callable_identity_binding_accepted: bool
    gate_factory_step_unselected_accepted: bool
    gate_factory_step_untouched_accepted: bool
    gate_factory_step_unexecuted_accepted: bool
    selected_slot_still_fresh: bool
    callable_factory_execution_order_acceptance_complete: bool
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
        error = PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrderAcceptanceError
        if self.selected_repeat_index not in (1, 2, 3):
            raise error("selected repeat index must be one of 1, 2, 3")
        suffix = f".repeat-{self.selected_repeat_index}.v1"
        indexed_ids = (
            self.acceptance_id, self.callable_factory_execution_order_id,
            self.execution_preflight_acceptance_id, self.execution_preflight_id,
            self.callable_factory_step_order_acceptance_id, self.callable_factory_step_order_id,
            self.first_factory_step_acceptance_id, self.first_factory_step_preflight_id,
            self.factory_execution_order_acceptance_id, self.factory_execution_order_id,
            self.accepted_callable_execution_step_id, self.untouched_gate_factory_step_id,
            self.future_callable_factory_order_id, self.future_gate_factory_order_id,
            self.callable_factory_identity_id, self.callable_constructor_identity_id,
            self.future_callable_object_id, self.gate_factory_identity_id,
            self.gate_constructor_identity_id, self.future_gate_object_id,
        )
        if not all(identifier.endswith(suffix) for identifier in indexed_ids):
            raise error("callable factory execution acceptance identities must match selected repeat index")
        step = self.accepted_callable_execution_step
        gate_step = self.untouched_gate_factory_step
        if not (
            step.step_index == 1 and step.role == "callable_factory"
            and step.step_id == self.accepted_callable_execution_step_id
            and step.factory_order_id == self.future_callable_factory_order_id
            and step.factory_identity_id == self.callable_factory_identity_id
            and step.constructor_identity_id == self.callable_constructor_identity_id
            and step.future_object_id == self.future_callable_object_id
            and step.one_time_future_step and not step.executed
        ):
            raise error("accepted callable factory execution step must remain one-time and unexecuted")
        if not (
            gate_step.step_index == 2 and gate_step.role == "gate_factory"
            and gate_step.step_id == self.untouched_gate_factory_step_id
            and gate_step.factory_order_id == self.future_gate_factory_order_id
            and gate_step.factory_identity_id == self.gate_factory_identity_id
            and gate_step.constructor_identity_id == self.gate_constructor_identity_id
            and gate_step.future_object_id == self.future_gate_object_id
            and gate_step.one_time_future_step and not gate_step.executed
        ):
            raise error("gate factory step must remain unselected, untouched, and unexecuted")
        expected = tuple(index for index in (1, 2, 3) if index != self.selected_repeat_index)
        if tuple(self.other_slots_unselected) != expected:
            raise error("other slots must remain unselected")
        required = (
            self.positive_callable_factory_execution_order_accepted,
            self.exactly_one_future_callable_execution_step_accepted,
            self.callable_execution_step_one_time_accepted,
            self.callable_execution_step_unexecuted_accepted,
            self.callable_identity_binding_accepted,
            self.gate_factory_step_unselected_accepted,
            self.gate_factory_step_untouched_accepted,
            self.gate_factory_step_unexecuted_accepted,
            self.selected_slot_still_fresh,
            self.callable_factory_execution_order_acceptance_complete,
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
            raise error("callable factory execution order acceptance remains fully non-executable")
        object.__setattr__(self, "other_slots_unselected", tuple(self.other_slots_unselected))


def accept_public_av_return_replication_repeatability_single_slot_callable_factory_execution_order(
    order: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrder,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrderAcceptance:
    error = PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrderAcceptanceError
    if not isinstance(order, PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrder):
        raise error("single-slot callable factory execution order has the wrong type")
    required = (
        order.positive_execution_preflight_acceptance_bound,
        order.exactly_one_future_callable_execution_step,
        order.callable_execution_step_one_time,
        order.callable_execution_step_unexecuted,
        order.callable_factory_identity_bound,
        order.callable_constructor_identity_bound,
        order.future_callable_object_identity_bound,
        order.gate_factory_step_unselected,
        order.gate_factory_step_untouched,
        order.gate_factory_step_still_unexecuted,
        order.selected_slot_still_fresh,
        order.callable_factory_execution_order_complete,
    )
    forbidden = (
        order.callable_factory_reference_stored, order.gate_factory_reference_stored,
        order.callable_reference_stored, order.factory_function_called,
        order.callable_factory_called, order.gate_factory_called,
        order.callable_object_created, order.gate_object_created,
        order.constructor_invoked, order.binding_performed, order.scheduler_available,
        order.media_decode_allowed, order.receptor_feed_allowed,
        order.start_release_granted, order.repeatability_run_allowed, order.repeat_run_started,
    )
    if not all(required) or any(forbidden):
        raise error("one complete fresh callable factory execution order is required")
    carried_fields = (
        "selected_repeat_index", "execution_preflight_acceptance_id", "execution_preflight_id",
        "callable_factory_step_order_acceptance_id", "callable_factory_step_order_id",
        "first_factory_step_acceptance_id", "first_factory_step_preflight_id",
        "factory_execution_order_acceptance_id", "factory_execution_order_id",
        "untouched_gate_factory_step", "untouched_gate_factory_step_id",
        "future_callable_factory_order_id", "future_gate_factory_order_id",
        "callable_factory_identity_id", "callable_constructor_identity_id",
        "future_callable_object_id", "gate_factory_identity_id",
        "gate_constructor_identity_id", "future_gate_object_id", "logical_callable_id",
        "logical_gate_id", "reserved_executor_id", "source_id", "other_slots_unselected",
    )
    carried = {field: getattr(order, field) for field in carried_fields}
    index = order.selected_repeat_index
    return PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrderAcceptance(
        acceptance_id=f"{SINGLE_SLOT_CALLABLE_FACTORY_EXECUTION_ORDER_ACCEPTANCE_ID}.repeat-{index}.v1",
        callable_factory_execution_order_id=order.execution_order_id,
        accepted_callable_execution_step=order.future_callable_execution_step,
        accepted_callable_execution_step_id=order.future_callable_execution_step_id,
        positive_callable_factory_execution_order_accepted=True,
        exactly_one_future_callable_execution_step_accepted=True,
        callable_execution_step_one_time_accepted=True,
        callable_execution_step_unexecuted_accepted=True,
        callable_identity_binding_accepted=True,
        gate_factory_step_unselected_accepted=True,
        gate_factory_step_untouched_accepted=True,
        gate_factory_step_unexecuted_accepted=True,
        selected_slot_still_fresh=True,
        callable_factory_execution_order_acceptance_complete=True,
        **carried,
    )


def execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_execution_order(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrderAcceptance,
) -> None:
    del acceptance
    raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrderAcceptanceError(
        "factory execution is not released by the locked callable factory execution order acceptance"
    )


def public_av_return_replication_repeatability_single_slot_callable_factory_execution_order_acceptance_to_jsonable(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrderAcceptance,
) -> dict[str, Any]:
    return asdict(acceptance)
