"""Locked execution preflight for one callable-factory step order."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_callable_factory_step_order_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderAcceptance,
)
from .public_av_return_replication_repeatability_single_slot_factory_execution_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep,
)


SINGLE_SLOT_CALLABLE_FACTORY_STEP_EXECUTION_PREFLIGHT_ID = (
    "public.av.nasa-earthrise.return-replication."
    "repeatability-single-slot-callable-factory-step-execution-preflight.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflight:
    preflight_id: str
    selected_repeat_index: int
    callable_factory_step_order_acceptance_id: str
    callable_factory_step_order_id: str
    first_factory_step_acceptance_id: str
    first_factory_step_preflight_id: str
    factory_execution_order_acceptance_id: str
    factory_execution_order_id: str
    execution_candidate_step: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep
    untouched_gate_factory_step: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep
    execution_candidate_step_id: str
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
    positive_order_acceptance_bound: bool
    exactly_one_execution_candidate_bound: bool
    callable_factory_candidate_bound: bool
    callable_factory_candidate_unconsumed: bool
    callable_identity_binding_accepted: bool
    gate_factory_step_unselected: bool
    gate_factory_step_untouched: bool
    gate_factory_step_still_unexecuted: bool
    selected_slot_still_fresh: bool
    execution_preflight_complete: bool
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightError(
                "selected repeat index must be one of 1, 2, 3"
            )
        suffix = f".repeat-{self.selected_repeat_index}.v1"
        indexed_ids = (
            self.preflight_id, self.callable_factory_step_order_acceptance_id,
            self.callable_factory_step_order_id, self.first_factory_step_acceptance_id,
            self.first_factory_step_preflight_id, self.factory_execution_order_acceptance_id,
            self.factory_execution_order_id, self.execution_candidate_step_id,
            self.untouched_gate_factory_step_id, self.future_callable_factory_order_id,
            self.future_gate_factory_order_id, self.callable_factory_identity_id,
            self.callable_constructor_identity_id, self.future_callable_object_id,
            self.gate_factory_identity_id, self.gate_constructor_identity_id,
            self.future_gate_object_id,
        )
        if not all(identifier.endswith(suffix) for identifier in indexed_ids):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightError(
                "callable factory step execution preflight identities must match selected repeat index"
            )
        candidate = self.execution_candidate_step
        gate_step = self.untouched_gate_factory_step
        if not (
            candidate.step_index == 1
            and candidate.role == "callable_factory"
            and candidate.step_id == self.execution_candidate_step_id
            and candidate.factory_order_id == self.future_callable_factory_order_id
            and candidate.factory_identity_id == self.callable_factory_identity_id
            and candidate.constructor_identity_id == self.callable_constructor_identity_id
            and candidate.future_object_id == self.future_callable_object_id
            and candidate.one_time_future_step
            and not candidate.executed
        ):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightError(
                "execution candidate must be the single unconsumed callable factory step"
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightError(
                "gate factory step must remain untouched and unexecuted"
            )
        expected = tuple(index for index in (1, 2, 3) if index != self.selected_repeat_index)
        if tuple(self.other_slots_unselected) != expected:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightError(
                "other slots must remain unselected"
            )
        required = (
            self.positive_order_acceptance_bound,
            self.exactly_one_execution_candidate_bound,
            self.callable_factory_candidate_bound,
            self.callable_factory_candidate_unconsumed,
            self.callable_identity_binding_accepted,
            self.gate_factory_step_unselected,
            self.gate_factory_step_untouched,
            self.gate_factory_step_still_unexecuted,
            self.selected_slot_still_fresh,
            self.execution_preflight_complete,
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightError(
                "callable factory step execution preflight remains fully non-executable"
            )
        object.__setattr__(self, "other_slots_unselected", tuple(self.other_slots_unselected))


def preflight_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderAcceptance,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflight:
    if not isinstance(acceptance, PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderAcceptance):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightError(
            "single-slot callable factory step order acceptance has the wrong type"
        )
    required = (
        acceptance.positive_callable_factory_step_order_accepted,
        acceptance.exactly_one_callable_factory_order_accepted,
        acceptance.callable_factory_order_one_time_accepted,
        acceptance.callable_factory_order_unexecuted_accepted,
        acceptance.callable_identity_binding_accepted,
        acceptance.gate_factory_step_unselected_accepted,
        acceptance.gate_factory_step_untouched_accepted,
        acceptance.gate_factory_step_unexecuted_accepted,
        acceptance.selected_slot_still_fresh,
        acceptance.callable_factory_step_order_acceptance_complete,
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
        raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightError(
            "one complete fresh callable factory step order acceptance is required"
        )
    index = acceptance.selected_repeat_index
    identity_fields = (
        "selected_repeat_index", "callable_factory_step_order_id",
        "first_factory_step_acceptance_id", "first_factory_step_preflight_id",
        "factory_execution_order_acceptance_id", "factory_execution_order_id",
        "future_callable_factory_order_id", "future_gate_factory_order_id",
        "callable_factory_identity_id", "callable_constructor_identity_id",
        "future_callable_object_id", "gate_factory_identity_id",
        "gate_constructor_identity_id", "future_gate_object_id",
        "logical_callable_id", "logical_gate_id", "reserved_executor_id",
        "source_id", "other_slots_unselected",
    )
    carried = {field: getattr(acceptance, field) for field in identity_fields}
    return PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflight(
        preflight_id=f"{SINGLE_SLOT_CALLABLE_FACTORY_STEP_EXECUTION_PREFLIGHT_ID}.repeat-{index}.v1",
        callable_factory_step_order_acceptance_id=acceptance.acceptance_id,
        execution_candidate_step=acceptance.selected_factory_step,
        untouched_gate_factory_step=acceptance.untouched_gate_factory_step,
        execution_candidate_step_id=acceptance.selected_callable_factory_step_id,
        untouched_gate_factory_step_id=acceptance.untouched_gate_factory_step_id,
        positive_order_acceptance_bound=True,
        exactly_one_execution_candidate_bound=True,
        callable_factory_candidate_bound=True,
        callable_factory_candidate_unconsumed=True,
        callable_identity_binding_accepted=True,
        gate_factory_step_unselected=True,
        gate_factory_step_untouched=True,
        gate_factory_step_still_unexecuted=True,
        selected_slot_still_fresh=True,
        execution_preflight_complete=True,
        **carried,
    )


def execute_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight(
    preflight: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflight,
) -> None:
    del preflight
    raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightError(
        "factory execution is not released by the locked callable factory step execution preflight"
    )


def public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight_to_jsonable(
    preflight: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflight,
) -> dict[str, Any]:
    return asdict(preflight)
