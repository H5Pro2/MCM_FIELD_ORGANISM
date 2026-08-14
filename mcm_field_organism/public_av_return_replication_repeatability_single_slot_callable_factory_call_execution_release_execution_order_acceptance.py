"""Locked acceptance of one callable-factory call execution release execution order."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrder,
)


ID = (
    "public.av.nasa-earthrise.return-replication.repeatability-single-slot-"
    "callable-factory-call-execution-release-execution-order-acceptance.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrderAcceptanceError(
    ValueError
):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrderAcceptance:
    acceptance_id: str
    selected_repeat_index: int
    execution_order: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrder
    positive_execution_order_accepted: bool
    exactly_one_future_execution_step_accepted: bool
    execution_step_one_time_accepted: bool
    execution_step_unexecuted_accepted: bool
    actual_release_absence_accepted: bool
    callable_identity_accepted: bool
    gate_step_untouched_accepted: bool
    selected_slot_still_fresh: bool
    acceptance_complete: bool
    actual_release_granted: bool = False
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
        error = PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrderAcceptanceError
        order = self.execution_order
        source = (
            order.execution_preflight_acceptance.release_execution_preflight.release_order_acceptance.release_order
            .release_preflight_acceptance.release_preflight
        )
        if self.selected_repeat_index not in (1, 2, 3) or order.selected_repeat_index != self.selected_repeat_index:
            raise error("selected repeat index mismatch")
        if not self.acceptance_id.endswith(f".repeat-{self.selected_repeat_index}.v1"):
            raise error("acceptance identity mismatch")
        candidate = source.release_candidate_step
        gate = source.untouched_gate_factory_step
        if candidate.role != "callable_factory" or candidate.executed or not candidate.one_time_future_step:
            raise error("execution step must remain unexecuted")
        if gate.role != "gate_factory" or gate.executed or not gate.one_time_future_step:
            raise error("gate step must remain untouched")
        required = (
            self.positive_execution_order_accepted,
            self.exactly_one_future_execution_step_accepted,
            self.execution_step_one_time_accepted,
            self.execution_step_unexecuted_accepted,
            self.actual_release_absence_accepted,
            self.callable_identity_accepted,
            self.gate_step_untouched_accepted,
            self.selected_slot_still_fresh,
            self.acceptance_complete,
        )
        forbidden = (
            self.actual_release_granted,
            self.callable_factory_reference_stored,
            self.gate_factory_reference_stored,
            self.callable_reference_stored,
            self.factory_function_called,
            self.callable_factory_called,
            self.gate_factory_called,
            self.callable_object_created,
            self.gate_object_created,
            self.constructor_invoked,
            self.binding_performed,
            self.scheduler_available,
            self.media_decode_allowed,
            self.receptor_feed_allowed,
            self.start_release_granted,
            self.repeatability_run_allowed,
            self.repeat_run_started,
            self.stability_threshold_defined,
            self.memory_claim_allowed,
            self.meaning_claim_allowed,
            self.organization_claim_allowed,
            self.ai_claim_allowed,
        )
        if not all(required) or any(forbidden):
            raise error("release execution order acceptance remains fully non-executable")


def accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_order(
    order: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrder,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrderAcceptance:
    error = PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrderAcceptanceError
    if not isinstance(order, PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrder):
        raise error("wrong execution order type")
    required = (
        order.positive_execution_preflight_acceptance_bound,
        order.exactly_one_future_execution_step,
        order.execution_step_one_time,
        order.execution_step_unexecuted,
        order.callable_identity_bound,
        order.gate_step_unselected,
        order.gate_step_untouched,
        order.gate_step_still_unexecuted,
        order.selected_slot_still_fresh,
        order.execution_order_complete,
    )
    forbidden = (
        order.actual_release_granted,
        order.callable_factory_reference_stored,
        order.gate_factory_reference_stored,
        order.callable_reference_stored,
        order.factory_function_called,
        order.callable_factory_called,
        order.gate_factory_called,
        order.callable_object_created,
        order.gate_object_created,
        order.constructor_invoked,
        order.binding_performed,
        order.scheduler_available,
        order.media_decode_allowed,
        order.receptor_feed_allowed,
        order.start_release_granted,
        order.repeatability_run_allowed,
        order.repeat_run_started,
        order.memory_claim_allowed,
        order.meaning_claim_allowed,
        order.organization_claim_allowed,
        order.ai_claim_allowed,
    )
    if not all(required) or any(forbidden):
        raise error("one complete locked execution order is required")
    index = order.selected_repeat_index
    return PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrderAcceptance(
        acceptance_id=f"{ID}.repeat-{index}.v1",
        selected_repeat_index=index,
        execution_order=order,
        positive_execution_order_accepted=True,
        exactly_one_future_execution_step_accepted=True,
        execution_step_one_time_accepted=True,
        execution_step_unexecuted_accepted=True,
        actual_release_absence_accepted=True,
        callable_identity_accepted=True,
        gate_step_untouched_accepted=True,
        selected_slot_still_fresh=True,
        acceptance_complete=True,
    )


def execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_call_execution_release_execution_order(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrderAcceptance,
) -> None:
    del acceptance
    raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrderAcceptanceError(
        "factory call execution release remains locked"
    )


def public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_order_acceptance_to_jsonable(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrderAcceptance,
) -> dict[str, Any]:
    return asdict(acceptance)
