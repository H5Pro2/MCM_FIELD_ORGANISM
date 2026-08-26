"""Locked release preflight for one callable-factory call execution order acceptance."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_order_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrderAcceptance,
)
from .public_av_return_replication_repeatability_single_slot_factory_execution_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep,
)


SINGLE_SLOT_CALLABLE_FACTORY_CALL_EXECUTION_RELEASE_PREFLIGHT_ID = (
    "public.av.nasa-earthrise.return-replication."
    "repeatability-single-slot-callable-factory-call-execution-release-preflight.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleasePreflightError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleasePreflight:
    preflight_id: str
    selected_repeat_index: int
    callable_factory_call_execution_order_acceptance_id: str
    callable_factory_call_execution_order_id: str
    release_candidate_step: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep
    untouched_gate_factory_step: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep
    release_candidate_step_id: str
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
    positive_execution_order_acceptance_bound: bool
    exactly_one_release_candidate_bound: bool
    release_candidate_unconsumed: bool
    callable_identity_binding_accepted: bool
    gate_factory_step_unselected: bool
    gate_factory_step_untouched: bool
    gate_factory_step_still_unexecuted: bool
    selected_slot_still_fresh: bool
    actual_release_granted: bool
    release_preflight_complete: bool
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
        error = PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleasePreflightError
        if self.selected_repeat_index not in (1, 2, 3):
            raise error("selected repeat index must be one of 1, 2, 3")
        suffix = f".repeat-{self.selected_repeat_index}.v1"
        indexed_ids = (
            self.preflight_id, self.callable_factory_call_execution_order_acceptance_id,
            self.callable_factory_call_execution_order_id, self.release_candidate_step_id,
            self.untouched_gate_factory_step_id, self.future_callable_factory_order_id,
            self.future_gate_factory_order_id, self.callable_factory_identity_id,
            self.callable_constructor_identity_id, self.future_callable_object_id,
            self.gate_factory_identity_id, self.gate_constructor_identity_id,
            self.future_gate_object_id,
        )
        if not all(identifier.endswith(suffix) for identifier in indexed_ids):
            raise error("release preflight identities must match selected repeat index")
        candidate = self.release_candidate_step
        gate = self.untouched_gate_factory_step
        if not (
            candidate.step_index == 1 and candidate.role == "callable_factory"
            and candidate.step_id == self.release_candidate_step_id
            and candidate.factory_order_id == self.future_callable_factory_order_id
            and candidate.factory_identity_id == self.callable_factory_identity_id
            and candidate.constructor_identity_id == self.callable_constructor_identity_id
            and candidate.future_object_id == self.future_callable_object_id
            and candidate.one_time_future_step and not candidate.executed
        ):
            raise error("release candidate must remain the unconsumed callable factory execution step")
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
            self.positive_execution_order_acceptance_bound,
            self.exactly_one_release_candidate_bound,
            self.release_candidate_unconsumed,
            self.callable_identity_binding_accepted,
            self.gate_factory_step_unselected,
            self.gate_factory_step_untouched,
            self.gate_factory_step_still_unexecuted,
            self.selected_slot_still_fresh,
            self.release_preflight_complete,
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
            raise error("release preflight remains fully non-executable")
        object.__setattr__(self, "other_slots_unselected", tuple(self.other_slots_unselected))


def preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrderAcceptance,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleasePreflight:
    error = PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleasePreflightError
    if not isinstance(acceptance, PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrderAcceptance):
        raise error("single-slot callable factory call execution order acceptance has the wrong type")
    order = acceptance.execution_order
    required = (
        acceptance.positive_execution_order_accepted,
        acceptance.exactly_one_future_execution_step_accepted,
        acceptance.execution_step_unconsumed_accepted,
        acceptance.gate_step_untouched_accepted,
        acceptance.acceptance_complete,
        order.callable_factory_call_execution_order_complete,
    )
    forbidden = (
        acceptance.callable_factory_reference_stored, acceptance.callable_reference_stored,
        acceptance.factory_function_called, acceptance.callable_factory_called,
        acceptance.callable_object_created, acceptance.constructor_invoked,
        acceptance.binding_performed, acceptance.media_decode_allowed,
        acceptance.receptor_feed_allowed, acceptance.repeat_run_started,
        order.callable_factory_reference_stored, order.gate_factory_reference_stored,
        order.callable_reference_stored, order.factory_function_called,
        order.callable_factory_called, order.gate_factory_called,
        order.callable_object_created, order.gate_object_created,
        order.constructor_invoked, order.binding_performed,
        order.scheduler_available, order.media_decode_allowed,
        order.receptor_feed_allowed, order.start_release_granted,
        order.repeatability_run_allowed, order.repeat_run_started,
    )
    if not all(required) or any(forbidden):
        raise error("one complete fresh callable factory call execution order acceptance is required")
    index = acceptance.selected_repeat_index
    return PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleasePreflight(
        preflight_id=f"{SINGLE_SLOT_CALLABLE_FACTORY_CALL_EXECUTION_RELEASE_PREFLIGHT_ID}.repeat-{index}.v1",
        selected_repeat_index=index,
        callable_factory_call_execution_order_acceptance_id=acceptance.acceptance_id,
        callable_factory_call_execution_order_id=order.execution_order_id,
        release_candidate_step=order.future_callable_call_execution_step,
        untouched_gate_factory_step=order.untouched_gate_factory_step,
        release_candidate_step_id=order.future_callable_call_execution_step_id,
        untouched_gate_factory_step_id=order.untouched_gate_factory_step_id,
        future_callable_factory_order_id=order.future_callable_factory_order_id,
        future_gate_factory_order_id=order.future_gate_factory_order_id,
        callable_factory_identity_id=order.callable_factory_identity_id,
        callable_constructor_identity_id=order.callable_constructor_identity_id,
        future_callable_object_id=order.future_callable_object_id,
        gate_factory_identity_id=order.gate_factory_identity_id,
        gate_constructor_identity_id=order.gate_constructor_identity_id,
        future_gate_object_id=order.future_gate_object_id,
        logical_callable_id=order.logical_callable_id,
        logical_gate_id=order.logical_gate_id,
        reserved_executor_id=order.reserved_executor_id,
        source_id=order.source_id,
        positive_execution_order_acceptance_bound=True,
        exactly_one_release_candidate_bound=True,
        release_candidate_unconsumed=True,
        callable_identity_binding_accepted=True,
        gate_factory_step_unselected=True,
        gate_factory_step_untouched=True,
        gate_factory_step_still_unexecuted=True,
        selected_slot_still_fresh=True,
        actual_release_granted=False,
        release_preflight_complete=True,
        other_slots_unselected=order.other_slots_unselected,
    )


def execute_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_preflight(
    preflight: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleasePreflight,
) -> None:
    del preflight
    raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleasePreflightError(
        "factory call execution release is not granted by the locked release preflight"
    )


def public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_preflight_to_jsonable(
    preflight: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleasePreflight,
) -> dict[str, Any]:
    return asdict(preflight)
