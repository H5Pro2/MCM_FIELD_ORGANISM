"""Locked acceptance of one callable-factory step order."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_callable_factory_step_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrder,
)
from .public_av_return_replication_repeatability_single_slot_factory_execution_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep,
)


SINGLE_SLOT_CALLABLE_FACTORY_STEP_ORDER_ACCEPTANCE_ID = (
    "public.av.nasa-earthrise.return-replication."
    "repeatability-single-slot-callable-factory-step-order-acceptance.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderAcceptanceError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderAcceptance:
    acceptance_id: str
    selected_repeat_index: int
    callable_factory_step_order_id: str
    first_factory_step_acceptance_id: str
    first_factory_step_preflight_id: str
    factory_execution_order_acceptance_id: str
    factory_execution_order_id: str
    selected_factory_step: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep
    untouched_gate_factory_step: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep
    selected_callable_factory_step_id: str
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
    positive_callable_factory_step_order_accepted: bool
    exactly_one_callable_factory_order_accepted: bool
    callable_factory_order_one_time_accepted: bool
    callable_factory_order_unexecuted_accepted: bool
    callable_identity_binding_accepted: bool
    gate_factory_step_unselected_accepted: bool
    gate_factory_step_untouched_accepted: bool
    gate_factory_step_unexecuted_accepted: bool
    selected_slot_still_fresh: bool
    callable_factory_step_order_acceptance_complete: bool
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderAcceptanceError(
                "selected repeat index must be one of 1, 2, 3"
            )
        suffix = f".repeat-{self.selected_repeat_index}.v1"
        indexed_ids = (
            self.acceptance_id, self.callable_factory_step_order_id,
            self.first_factory_step_acceptance_id, self.first_factory_step_preflight_id,
            self.factory_execution_order_acceptance_id, self.factory_execution_order_id,
            self.selected_callable_factory_step_id, self.untouched_gate_factory_step_id,
            self.future_callable_factory_order_id, self.future_gate_factory_order_id,
            self.callable_factory_identity_id, self.callable_constructor_identity_id,
            self.future_callable_object_id, self.gate_factory_identity_id,
            self.gate_constructor_identity_id, self.future_gate_object_id,
        )
        if not all(identifier.endswith(suffix) for identifier in indexed_ids):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderAcceptanceError(
                "callable factory order acceptance identities must match selected repeat index"
            )
        callable_step = self.selected_factory_step
        gate_step = self.untouched_gate_factory_step
        if not (
            callable_step.step_index == 1 and callable_step.role == "callable_factory"
            and callable_step.step_id == self.selected_callable_factory_step_id
            and callable_step.factory_order_id == self.future_callable_factory_order_id
            and callable_step.factory_identity_id == self.callable_factory_identity_id
            and callable_step.constructor_identity_id == self.callable_constructor_identity_id
            and callable_step.future_object_id == self.future_callable_object_id
            and callable_step.one_time_future_step and not callable_step.executed
        ):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderAcceptanceError(
                "accepted callable factory order must remain one-time and unexecuted"
            )
        if not (
            gate_step.step_index == 2 and gate_step.role == "gate_factory"
            and gate_step.step_id == self.untouched_gate_factory_step_id
            and gate_step.factory_order_id == self.future_gate_factory_order_id
            and gate_step.factory_identity_id == self.gate_factory_identity_id
            and gate_step.constructor_identity_id == self.gate_constructor_identity_id
            and gate_step.future_object_id == self.future_gate_object_id
            and gate_step.one_time_future_step and not gate_step.executed
        ):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderAcceptanceError(
                "gate factory step must remain untouched and unexecuted"
            )
        expected = tuple(index for index in (1, 2, 3) if index != self.selected_repeat_index)
        if tuple(self.other_slots_unselected) != expected:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderAcceptanceError(
                "other slots must remain unselected"
            )
        required = (
            self.positive_callable_factory_step_order_accepted,
            self.exactly_one_callable_factory_order_accepted,
            self.callable_factory_order_one_time_accepted,
            self.callable_factory_order_unexecuted_accepted,
            self.callable_identity_binding_accepted,
            self.gate_factory_step_unselected_accepted,
            self.gate_factory_step_untouched_accepted,
            self.gate_factory_step_unexecuted_accepted,
            self.selected_slot_still_fresh,
            self.callable_factory_step_order_acceptance_complete,
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderAcceptanceError(
                "callable factory order acceptance remains fully non-executable"
            )
        object.__setattr__(self, "other_slots_unselected", tuple(self.other_slots_unselected))


def accept_public_av_return_replication_repeatability_single_slot_callable_factory_step_order(
    order: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrder,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderAcceptance:
    if not isinstance(order, PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrder):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderAcceptanceError(
            "single-slot callable factory step order has the wrong type"
        )
    required = (
        order.positive_first_step_acceptance_bound,
        order.exactly_one_callable_factory_order_derived,
        order.callable_factory_order_one_time,
        order.callable_factory_order_unexecuted,
        order.callable_factory_identity_bound,
        order.callable_constructor_identity_bound,
        order.future_callable_object_identity_bound,
        order.gate_factory_step_unselected,
        order.gate_factory_step_untouched,
        order.gate_factory_step_still_unexecuted,
        order.selected_slot_still_fresh,
        order.callable_factory_step_order_complete,
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
        raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderAcceptanceError(
            "one complete fresh non-executable callable factory order is required"
        )
    index = order.selected_repeat_index
    identity_fields = (
        "selected_repeat_index", "first_factory_step_acceptance_id",
        "first_factory_step_preflight_id", "factory_execution_order_acceptance_id",
        "factory_execution_order_id", "selected_factory_step", "untouched_gate_factory_step",
        "selected_callable_factory_step_id", "untouched_gate_factory_step_id",
        "future_callable_factory_order_id", "future_gate_factory_order_id",
        "callable_factory_identity_id", "callable_constructor_identity_id",
        "future_callable_object_id", "gate_factory_identity_id",
        "gate_constructor_identity_id", "future_gate_object_id", "logical_callable_id",
        "logical_gate_id", "reserved_executor_id", "source_id", "other_slots_unselected",
    )
    carried = {field: getattr(order, field) for field in identity_fields}
    return PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderAcceptance(
        acceptance_id=f"{SINGLE_SLOT_CALLABLE_FACTORY_STEP_ORDER_ACCEPTANCE_ID}.repeat-{index}.v1",
        callable_factory_step_order_id=order.order_id,
        positive_callable_factory_step_order_accepted=True,
        exactly_one_callable_factory_order_accepted=True,
        callable_factory_order_one_time_accepted=True,
        callable_factory_order_unexecuted_accepted=True,
        callable_identity_binding_accepted=True,
        gate_factory_step_unselected_accepted=True,
        gate_factory_step_untouched_accepted=True,
        gate_factory_step_unexecuted_accepted=True,
        selected_slot_still_fresh=True,
        callable_factory_step_order_acceptance_complete=True,
        **carried,
    )


def execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_step_order(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderAcceptance,
) -> None:
    del acceptance
    raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderAcceptanceError(
        "factory execution is not released by the locked callable factory order acceptance"
    )


def public_av_return_replication_repeatability_single_slot_callable_factory_step_order_acceptance_to_jsonable(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderAcceptance,
) -> dict[str, Any]:
    return asdict(acceptance)
