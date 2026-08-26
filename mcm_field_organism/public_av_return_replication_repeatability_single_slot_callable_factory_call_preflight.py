"""Locked call preflight for one callable-factory execution order acceptance."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_callable_factory_execution_order_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrderAcceptance,
)
from .public_av_return_replication_repeatability_single_slot_factory_execution_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep,
)


SINGLE_SLOT_CALLABLE_FACTORY_CALL_PREFLIGHT_ID = (
    "public.av.nasa-earthrise.return-replication."
    "repeatability-single-slot-callable-factory-call-preflight.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallPreflightError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallPreflight:
    preflight_id: str
    selected_repeat_index: int
    callable_factory_execution_order_acceptance_id: str
    callable_factory_execution_order_id: str
    execution_preflight_acceptance_id: str
    execution_preflight_id: str
    callable_factory_step_order_acceptance_id: str
    callable_factory_step_order_id: str
    first_factory_step_acceptance_id: str
    first_factory_step_preflight_id: str
    factory_execution_order_acceptance_id: str
    factory_execution_order_id: str
    call_candidate_step: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep
    untouched_gate_factory_step: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep
    call_candidate_step_id: str
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
    exactly_one_callable_call_candidate_bound: bool
    callable_factory_call_candidate_unconsumed: bool
    callable_factory_identity_bound: bool
    callable_constructor_identity_bound: bool
    future_callable_object_identity_bound: bool
    gate_factory_step_unselected: bool
    gate_factory_step_untouched: bool
    gate_factory_step_still_unexecuted: bool
    selected_slot_still_fresh: bool
    callable_factory_call_preflight_complete: bool
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallPreflightError(
                "selected repeat index must be one of 1, 2, 3"
            )
        suffix = f".repeat-{self.selected_repeat_index}.v1"
        indexed_ids = (
            self.preflight_id, self.callable_factory_execution_order_acceptance_id,
            self.callable_factory_execution_order_id, self.execution_preflight_acceptance_id,
            self.execution_preflight_id, self.callable_factory_step_order_acceptance_id,
            self.callable_factory_step_order_id, self.first_factory_step_acceptance_id,
            self.first_factory_step_preflight_id, self.factory_execution_order_acceptance_id,
            self.factory_execution_order_id, self.call_candidate_step_id,
            self.untouched_gate_factory_step_id, self.future_callable_factory_order_id,
            self.future_gate_factory_order_id, self.callable_factory_identity_id,
            self.callable_constructor_identity_id, self.future_callable_object_id,
            self.gate_factory_identity_id, self.gate_constructor_identity_id,
            self.future_gate_object_id,
        )
        if not all(identifier.endswith(suffix) for identifier in indexed_ids):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallPreflightError(
                "call preflight identities must match selected repeat index"
            )
        candidate = self.call_candidate_step
        gate_step = self.untouched_gate_factory_step
        if not (
            candidate.step_index == 1
            and candidate.role == "callable_factory"
            and candidate.step_id == self.call_candidate_step_id
            and candidate.factory_order_id == self.future_callable_factory_order_id
            and candidate.factory_identity_id == self.callable_factory_identity_id
            and candidate.constructor_identity_id == self.callable_constructor_identity_id
            and candidate.future_object_id == self.future_callable_object_id
            and candidate.one_time_future_step
            and not candidate.executed
        ):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallPreflightError(
                "call candidate must be the single unconsumed callable factory step"
            )
        if not (
            gate_step.step_index == 2
            and gate_step.role == "gate_factory"
            and gate_step.step_id == self.untouched_gate_factory_step_id
            and gate_step.factory_order_id == self.future_gate_factory_order_id
            and gate_step.factory_identity_id == self.gate_factory_identity_id
            and gate_step.constructor_identity_id == self.gate_constructor_identity_id
            and gate_step.future_object_id == self.future_gate_object_id
            and gate_step.one_time_future_step
            and not gate_step.executed
        ):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallPreflightError(
                "gate factory step must remain untouched and unexecuted"
            )
        expected = tuple(index for index in (1, 2, 3) if index != self.selected_repeat_index)
        if tuple(self.other_slots_unselected) != expected:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallPreflightError(
                "other slots must remain unselected"
            )
        required = (
            self.positive_execution_order_acceptance_bound,
            self.exactly_one_callable_call_candidate_bound,
            self.callable_factory_call_candidate_unconsumed,
            self.callable_factory_identity_bound,
            self.callable_constructor_identity_bound,
            self.future_callable_object_identity_bound,
            self.gate_factory_step_unselected,
            self.gate_factory_step_untouched,
            self.gate_factory_step_still_unexecuted,
            self.selected_slot_still_fresh,
            self.callable_factory_call_preflight_complete,
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallPreflightError(
                "callable factory call preflight remains fully non-executable"
            )
        object.__setattr__(self, "other_slots_unselected", tuple(self.other_slots_unselected))


def preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrderAcceptance,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallPreflight:
    if not isinstance(acceptance, PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrderAcceptance):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallPreflightError(
            "single-slot callable factory execution order acceptance has the wrong type"
        )
    required = (
        acceptance.positive_callable_factory_execution_order_accepted,
        acceptance.exactly_one_future_callable_execution_step_accepted,
        acceptance.callable_execution_step_one_time_accepted,
        acceptance.callable_execution_step_unexecuted_accepted,
        acceptance.callable_identity_binding_accepted,
        acceptance.gate_factory_step_unselected_accepted,
        acceptance.gate_factory_step_untouched_accepted,
        acceptance.gate_factory_step_unexecuted_accepted,
        acceptance.selected_slot_still_fresh,
        acceptance.callable_factory_execution_order_acceptance_complete,
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
        raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallPreflightError(
            "one complete fresh callable factory execution order acceptance is required"
        )
    index = acceptance.selected_repeat_index
    carried_fields = (
        "selected_repeat_index", "callable_factory_execution_order_id",
        "execution_preflight_acceptance_id", "execution_preflight_id",
        "callable_factory_step_order_acceptance_id", "callable_factory_step_order_id",
        "first_factory_step_acceptance_id", "first_factory_step_preflight_id",
        "factory_execution_order_acceptance_id", "factory_execution_order_id",
        "untouched_gate_factory_step", "untouched_gate_factory_step_id",
        "future_callable_factory_order_id", "future_gate_factory_order_id",
        "callable_factory_identity_id", "callable_constructor_identity_id",
        "future_callable_object_id", "gate_factory_identity_id",
        "gate_constructor_identity_id", "future_gate_object_id",
        "logical_callable_id", "logical_gate_id", "reserved_executor_id",
        "source_id", "other_slots_unselected",
    )
    carried = {field: getattr(acceptance, field) for field in carried_fields}
    return PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallPreflight(
        preflight_id=f"{SINGLE_SLOT_CALLABLE_FACTORY_CALL_PREFLIGHT_ID}.repeat-{index}.v1",
        callable_factory_execution_order_acceptance_id=acceptance.acceptance_id,
        call_candidate_step=acceptance.accepted_callable_execution_step,
        call_candidate_step_id=acceptance.accepted_callable_execution_step_id,
        positive_execution_order_acceptance_bound=True,
        exactly_one_callable_call_candidate_bound=True,
        callable_factory_call_candidate_unconsumed=True,
        callable_factory_identity_bound=True,
        callable_constructor_identity_bound=True,
        future_callable_object_identity_bound=True,
        gate_factory_step_unselected=True,
        gate_factory_step_untouched=True,
        gate_factory_step_still_unexecuted=True,
        selected_slot_still_fresh=True,
        callable_factory_call_preflight_complete=True,
        **carried,
    )


def execute_public_av_return_replication_repeatability_single_slot_callable_factory_call_preflight(
    preflight: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallPreflight,
) -> None:
    del preflight
    raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallPreflightError(
        "factory call is not released by the locked callable factory call preflight"
    )


def public_av_return_replication_repeatability_single_slot_callable_factory_call_preflight_to_jsonable(
    preflight: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallPreflight,
) -> dict[str, Any]:
    return asdict(preflight)
