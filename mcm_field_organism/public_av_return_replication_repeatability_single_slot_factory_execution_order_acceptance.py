"""Locked acceptance of one two-step single-slot factory execution order."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_factory_execution_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrder,
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep,
)


SINGLE_SLOT_FACTORY_EXECUTION_ORDER_ACCEPTANCE_ID = (
    "public.av.nasa-earthrise.return-replication."
    "repeatability-single-slot-factory-execution-order-acceptance.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderAcceptanceError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderAcceptance:
    acceptance_id: str
    selected_repeat_index: int
    factory_execution_order_id: str
    execution_acceptance_id: str
    execution_preflight_id: str
    factory_order_acceptance_id: str
    factory_order_id: str
    factory_call_acceptance_id: str
    factory_call_preflight_id: str
    factory_acceptance_id: str
    factory_binding_id: str
    construction_acceptance_id: str
    construction_id: str
    object_reservation_id: str
    candidate_id: str
    logical_callable_id: str
    logical_gate_id: str
    reserved_executor_id: str
    future_callable_object_id: str
    future_gate_object_id: str
    callable_constructor_id: str
    gate_constructor_id: str
    future_callable_factory_id: str
    future_gate_factory_id: str
    future_callable_factory_order_id: str
    future_gate_factory_order_id: str
    ordered_factory_execution_candidate_ids: tuple[str, str]
    accepted_future_execution_steps: tuple[PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep, ...]
    source_id: str
    positive_factory_execution_order_accepted: bool
    exactly_two_future_steps_accepted: bool
    callable_factory_step_first_accepted: bool
    gate_factory_step_second_accepted: bool
    execution_steps_one_time_accepted: bool
    execution_steps_unexecuted_accepted: bool
    identity_chain_accepted: bool
    selected_slot_still_fresh: bool
    factory_execution_order_acceptance_complete: bool
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
        if self.selected_repeat_index not in (1, 2, 3):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderAcceptanceError(
                "selected repeat index must be one of 1, 2, 3"
            )
        suffix = f".repeat-{self.selected_repeat_index}.v1"
        indexed_ids = (
            self.acceptance_id, self.factory_execution_order_id,
            self.execution_acceptance_id, self.execution_preflight_id,
            self.factory_order_acceptance_id, self.factory_order_id,
            self.factory_call_acceptance_id, self.factory_call_preflight_id,
            self.factory_acceptance_id, self.factory_binding_id,
            self.callable_constructor_id, self.gate_constructor_id,
            self.future_callable_factory_id, self.future_gate_factory_id,
            self.future_callable_object_id, self.future_gate_object_id,
            self.future_callable_factory_order_id, self.future_gate_factory_order_id,
        )
        if not all(identifier.endswith(suffix) for identifier in indexed_ids):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderAcceptanceError(
                "factory execution order acceptance identities must match selected repeat index"
            )
        if tuple(self.ordered_factory_execution_candidate_ids) != (
            self.future_callable_factory_order_id, self.future_gate_factory_order_id,
        ):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderAcceptanceError(
                "accepted candidates must remain callable then gate factory orders"
            )
        steps = tuple(self.accepted_future_execution_steps)
        if len(steps) != 2 or not (
            steps[0].step_index == 1
            and steps[0].role == "callable_factory"
            and steps[0].factory_order_id == self.future_callable_factory_order_id
            and steps[1].step_index == 2
            and steps[1].role == "gate_factory"
            and steps[1].factory_order_id == self.future_gate_factory_order_id
            and all(step.one_time_future_step and not step.executed for step in steps)
        ):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderAcceptanceError(
                "exactly two ordered unexecuted one-time steps are required"
            )
        expected = tuple(index for index in (1, 2, 3) if index != self.selected_repeat_index)
        if tuple(self.other_slots_unselected) != expected:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderAcceptanceError(
                "other slots must remain unselected"
            )
        required = (
            self.positive_factory_execution_order_accepted,
            self.exactly_two_future_steps_accepted,
            self.callable_factory_step_first_accepted,
            self.gate_factory_step_second_accepted,
            self.execution_steps_one_time_accepted,
            self.execution_steps_unexecuted_accepted,
            self.identity_chain_accepted,
            self.selected_slot_still_fresh,
            self.factory_execution_order_acceptance_complete,
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderAcceptanceError(
                "factory execution order acceptance remains fully non-executable"
            )
        object.__setattr__(self, "accepted_future_execution_steps", steps)
        object.__setattr__(self, "ordered_factory_execution_candidate_ids", tuple(self.ordered_factory_execution_candidate_ids))
        object.__setattr__(self, "other_slots_unselected", tuple(self.other_slots_unselected))


def accept_public_av_return_replication_repeatability_single_slot_factory_execution_order(
    order: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrder,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderAcceptance:
    if not isinstance(order, PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrder):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderAcceptanceError(
            "single-slot factory execution order has the wrong type"
        )
    required = (
        order.positive_execution_acceptance_bound,
        order.exactly_two_future_execution_steps_derived,
        order.callable_factory_step_first, order.gate_factory_step_second,
        order.execution_steps_one_time, order.execution_steps_unexecuted,
        order.selected_slot_still_fresh, order.factory_execution_order_complete,
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
        raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderAcceptanceError(
            "one complete fresh unexecuted factory execution order is required"
        )

    index = order.selected_repeat_index
    identity_fields = (
        "selected_repeat_index", "execution_acceptance_id", "execution_preflight_id",
        "factory_order_acceptance_id", "factory_order_id", "factory_call_acceptance_id",
        "factory_call_preflight_id", "factory_acceptance_id", "factory_binding_id",
        "construction_acceptance_id", "construction_id", "object_reservation_id",
        "candidate_id", "logical_callable_id", "logical_gate_id", "reserved_executor_id",
        "future_callable_object_id", "future_gate_object_id", "callable_constructor_id",
        "gate_constructor_id", "future_callable_factory_id", "future_gate_factory_id",
        "future_callable_factory_order_id", "future_gate_factory_order_id",
        "ordered_factory_execution_candidate_ids", "source_id", "other_slots_unselected",
    )
    carried = {field: getattr(order, field) for field in identity_fields}
    return PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderAcceptance(
        acceptance_id=f"{SINGLE_SLOT_FACTORY_EXECUTION_ORDER_ACCEPTANCE_ID}.repeat-{index}.v1",
        factory_execution_order_id=order.execution_order_id,
        accepted_future_execution_steps=order.future_execution_steps,
        positive_factory_execution_order_accepted=True,
        exactly_two_future_steps_accepted=True,
        callable_factory_step_first_accepted=True,
        gate_factory_step_second_accepted=True,
        execution_steps_one_time_accepted=True,
        execution_steps_unexecuted_accepted=True,
        identity_chain_accepted=True,
        selected_slot_still_fresh=True,
        factory_execution_order_acceptance_complete=True,
        **carried,
    )


def execute_public_av_return_replication_repeatability_single_slot_accepted_factory_execution_order(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderAcceptance,
) -> None:
    del acceptance
    raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderAcceptanceError(
        "factory execution is not released by the locked execution order acceptance"
    )


def public_av_return_replication_repeatability_single_slot_factory_execution_order_acceptance_to_jsonable(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderAcceptance,
) -> dict[str, Any]:
    return asdict(acceptance)
