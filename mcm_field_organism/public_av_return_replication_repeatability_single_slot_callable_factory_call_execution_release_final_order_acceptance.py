"""Locked acceptance of one callable-factory call execution release final order."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrder,
)


ID = (
    "public.av.nasa-earthrise.return-replication.repeatability-single-slot-"
    "callable-factory-call-execution-release-final-order-acceptance.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrderAcceptanceError(
    ValueError
):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrderAcceptance:
    acceptance_id: str
    selected_repeat_index: int
    final_order: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrder
    positive_final_order_accepted: bool
    exactly_one_final_lock_step_accepted: bool
    final_lock_step_one_time_accepted: bool
    final_lock_step_unconsumed_accepted: bool
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
        error = PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrderAcceptanceError
        order = self.final_order
        source = (
            order.final_preflight_acceptance.final_preflight.execution_order_acceptance.execution_order
            .execution_preflight_acceptance.release_execution_preflight.release_order_acceptance.release_order
            .release_preflight_acceptance.release_preflight
        )
        if self.selected_repeat_index not in (1, 2, 3) or order.selected_repeat_index != self.selected_repeat_index:
            raise error("selected repeat index mismatch")
        if not self.acceptance_id.endswith(f".repeat-{self.selected_repeat_index}.v1"):
            raise error("acceptance identity mismatch")
        candidate = source.release_candidate_step
        gate = source.untouched_gate_factory_step
        if candidate.role != "callable_factory" or candidate.executed or not candidate.one_time_future_step:
            raise error("final lock step must remain unconsumed")
        if gate.role != "gate_factory" or gate.executed or not gate.one_time_future_step:
            raise error("gate step must remain untouched")
        required = (
            self.positive_final_order_accepted,
            self.exactly_one_final_lock_step_accepted,
            self.final_lock_step_one_time_accepted,
            self.final_lock_step_unconsumed_accepted,
            self.actual_release_absence_accepted,
            self.callable_identity_accepted,
            self.gate_step_untouched_accepted,
            self.selected_slot_still_fresh,
            self.acceptance_complete,
        )
        forbidden = tuple(
            getattr(self, name)
            for name in (
                "actual_release_granted", "callable_factory_reference_stored", "gate_factory_reference_stored",
                "callable_reference_stored", "factory_function_called", "callable_factory_called",
                "gate_factory_called", "callable_object_created", "gate_object_created", "constructor_invoked",
                "binding_performed", "scheduler_available", "media_decode_allowed", "receptor_feed_allowed",
                "start_release_granted", "repeatability_run_allowed", "repeat_run_started",
                "stability_threshold_defined", "memory_claim_allowed", "meaning_claim_allowed",
                "organization_claim_allowed", "ai_claim_allowed",
            )
        )
        if not all(required) or any(forbidden):
            raise error("final order acceptance remains fully non-executable")


def accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_order(
    order: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrder,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrderAcceptance:
    error = PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrderAcceptanceError
    if not isinstance(order, PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrder):
        raise error("wrong final order type")
    required = (
        order.positive_final_preflight_acceptance_bound,
        order.exactly_one_final_lock_step_derived,
        order.final_lock_step_one_time,
        order.final_lock_step_unconsumed,
        order.callable_identity_bound,
        order.gate_step_unselected,
        order.gate_step_untouched,
        order.gate_step_still_unexecuted,
        order.selected_slot_still_fresh,
        order.final_order_complete,
    )
    forbidden = tuple(
        getattr(order, name)
        for name in (
            "actual_release_granted", "callable_factory_reference_stored", "gate_factory_reference_stored",
            "callable_reference_stored", "factory_function_called", "callable_factory_called",
            "gate_factory_called", "callable_object_created", "gate_object_created", "constructor_invoked",
            "binding_performed", "scheduler_available", "media_decode_allowed", "receptor_feed_allowed",
            "start_release_granted", "repeatability_run_allowed", "repeat_run_started",
            "stability_threshold_defined", "memory_claim_allowed", "meaning_claim_allowed",
            "organization_claim_allowed", "ai_claim_allowed",
        )
    )
    if not all(required) or any(forbidden):
        raise error("one complete locked final order is required")
    index = order.selected_repeat_index
    return PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrderAcceptance(
        acceptance_id=f"{ID}.repeat-{index}.v1",
        selected_repeat_index=index,
        final_order=order,
        positive_final_order_accepted=True,
        exactly_one_final_lock_step_accepted=True,
        final_lock_step_one_time_accepted=True,
        final_lock_step_unconsumed_accepted=True,
        actual_release_absence_accepted=True,
        callable_identity_accepted=True,
        gate_step_untouched_accepted=True,
        selected_slot_still_fresh=True,
        acceptance_complete=True,
    )


def execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_call_execution_release_final_order(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrderAcceptance,
) -> None:
    del acceptance
    raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrderAcceptanceError(
        "factory call execution release remains locked"
    )


def public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_order_acceptance_to_jsonable(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrderAcceptance,
) -> dict[str, Any]:
    return asdict(acceptance)
