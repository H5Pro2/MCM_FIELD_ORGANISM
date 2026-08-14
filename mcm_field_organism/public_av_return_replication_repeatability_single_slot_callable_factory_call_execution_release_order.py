"""Locked release order for one callable-factory call execution candidate."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_preflight_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleasePreflightAcceptance,
)


ID = (
    "public.av.nasa-earthrise.return-replication.repeatability-single-slot-"
    "callable-factory-call-execution-release-order.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseOrderError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseOrder:
    release_order_id: str
    selected_repeat_index: int
    release_preflight_acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleasePreflightAcceptance
    positive_release_preflight_acceptance_bound: bool
    exactly_one_future_release_step_derived: bool
    release_step_one_time: bool
    release_step_unconsumed: bool
    callable_factory_identity_bound: bool
    callable_constructor_identity_bound: bool
    future_callable_object_identity_bound: bool
    gate_factory_step_unselected: bool
    gate_factory_step_untouched: bool
    gate_factory_step_still_unexecuted: bool
    selected_slot_still_fresh: bool
    actual_release_granted: bool
    release_order_complete: bool
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
        error = PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseOrderError
        acceptance = self.release_preflight_acceptance
        preflight = acceptance.release_preflight
        if self.selected_repeat_index not in (1, 2, 3) or acceptance.selected_repeat_index != self.selected_repeat_index:
            raise error("selected repeat index mismatch")
        if not self.release_order_id.endswith(f".repeat-{self.selected_repeat_index}.v1"):
            raise error("release order identity mismatch")
        candidate = preflight.release_candidate_step
        gate = preflight.untouched_gate_factory_step
        if candidate.role != "callable_factory" or candidate.executed or not candidate.one_time_future_step:
            raise error("future release step must remain the unconsumed callable candidate")
        if gate.role != "gate_factory" or gate.executed or not gate.one_time_future_step:
            raise error("gate factory step must remain untouched")
        required = (
            self.positive_release_preflight_acceptance_bound,
            self.exactly_one_future_release_step_derived,
            self.release_step_one_time,
            self.release_step_unconsumed,
            self.callable_factory_identity_bound,
            self.callable_constructor_identity_bound,
            self.future_callable_object_identity_bound,
            self.gate_factory_step_unselected,
            self.gate_factory_step_untouched,
            self.gate_factory_step_still_unexecuted,
            self.selected_slot_still_fresh,
            self.release_order_complete,
        )
        forbidden = (
            self.actual_release_granted, self.callable_factory_reference_stored,
            self.gate_factory_reference_stored, self.callable_reference_stored,
            self.factory_function_called, self.callable_factory_called,
            self.gate_factory_called, self.callable_object_created,
            self.gate_object_created, self.constructor_invoked,
            self.binding_performed, self.scheduler_available,
            self.media_decode_allowed, self.receptor_feed_allowed,
            self.start_release_granted, self.repeatability_run_allowed,
            self.repeat_run_started, self.stability_threshold_defined,
            self.memory_claim_allowed, self.meaning_claim_allowed,
            self.organization_claim_allowed, self.ai_claim_allowed,
        )
        if not all(required) or any(forbidden):
            raise error("release order remains fully non-executable")


def order_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleasePreflightAcceptance,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseOrder:
    error = PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseOrderError
    if not isinstance(acceptance, PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleasePreflightAcceptance):
        raise error("wrong release preflight acceptance type")
    required = (
        acceptance.positive_release_preflight_accepted,
        acceptance.exactly_one_release_candidate_accepted,
        acceptance.release_candidate_unconsumed_accepted,
        acceptance.actual_release_absence_accepted,
        acceptance.gate_step_untouched_accepted,
        acceptance.acceptance_complete,
    )
    forbidden = (
        acceptance.actual_release_granted, acceptance.callable_factory_reference_stored,
        acceptance.gate_factory_reference_stored, acceptance.callable_reference_stored,
        acceptance.factory_function_called, acceptance.callable_factory_called,
        acceptance.gate_factory_called, acceptance.callable_object_created,
        acceptance.gate_object_created, acceptance.constructor_invoked,
        acceptance.binding_performed, acceptance.scheduler_available,
        acceptance.media_decode_allowed, acceptance.receptor_feed_allowed,
        acceptance.start_release_granted, acceptance.repeatability_run_allowed,
        acceptance.repeat_run_started, acceptance.stability_threshold_defined,
        acceptance.memory_claim_allowed, acceptance.meaning_claim_allowed,
        acceptance.organization_claim_allowed, acceptance.ai_claim_allowed,
    )
    if not all(required) or any(forbidden):
        raise error("one complete locked release preflight acceptance is required")
    index = acceptance.selected_repeat_index
    return PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseOrder(
        release_order_id=f"{ID}.repeat-{index}.v1",
        selected_repeat_index=index,
        release_preflight_acceptance=acceptance,
        positive_release_preflight_acceptance_bound=True,
        exactly_one_future_release_step_derived=True,
        release_step_one_time=True,
        release_step_unconsumed=True,
        callable_factory_identity_bound=True,
        callable_constructor_identity_bound=True,
        future_callable_object_identity_bound=True,
        gate_factory_step_unselected=True,
        gate_factory_step_untouched=True,
        gate_factory_step_still_unexecuted=True,
        selected_slot_still_fresh=True,
        actual_release_granted=False,
        release_order_complete=True,
    )


def execute_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_order(
    order: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseOrder,
) -> None:
    del order
    raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseOrderError(
        "factory call execution release is not granted by the locked release order"
    )


def public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_order_to_jsonable(
    order: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseOrder,
) -> dict[str, Any]:
    return asdict(order)
