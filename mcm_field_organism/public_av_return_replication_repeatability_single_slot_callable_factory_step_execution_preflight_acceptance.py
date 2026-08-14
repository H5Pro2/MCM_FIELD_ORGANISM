"""Locked acceptance of one callable-factory step execution preflight."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflight,
)
from .public_av_return_replication_repeatability_single_slot_factory_execution_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep,
)


SINGLE_SLOT_CALLABLE_FACTORY_STEP_EXECUTION_PREFLIGHT_ACCEPTANCE_ID = (
    "public.av.nasa-earthrise.return-replication."
    "repeatability-single-slot-callable-factory-step-execution-preflight-acceptance.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightAcceptanceError(
    ValueError
):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightAcceptance:
    acceptance_id: str
    selected_repeat_index: int
    execution_preflight_id: str
    callable_factory_step_order_acceptance_id: str
    callable_factory_step_order_id: str
    first_factory_step_acceptance_id: str
    first_factory_step_preflight_id: str
    factory_execution_order_acceptance_id: str
    factory_execution_order_id: str
    accepted_execution_candidate_step: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep
    untouched_gate_factory_step: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep
    accepted_execution_candidate_step_id: str
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
    positive_execution_preflight_accepted: bool
    exactly_one_execution_candidate_accepted: bool
    callable_factory_candidate_accepted: bool
    callable_factory_candidate_unconsumed_accepted: bool
    callable_identity_binding_accepted: bool
    gate_factory_step_unselected_accepted: bool
    gate_factory_step_untouched_accepted: bool
    gate_factory_step_unexecuted_accepted: bool
    selected_slot_still_fresh: bool
    execution_preflight_acceptance_complete: bool
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
        error = PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightAcceptanceError
        if self.selected_repeat_index not in (1, 2, 3):
            raise error("selected repeat index must be one of 1, 2, 3")
        suffix = f".repeat-{self.selected_repeat_index}.v1"
        indexed_ids = (
            self.acceptance_id, self.execution_preflight_id,
            self.callable_factory_step_order_acceptance_id, self.callable_factory_step_order_id,
            self.first_factory_step_acceptance_id, self.first_factory_step_preflight_id,
            self.factory_execution_order_acceptance_id, self.factory_execution_order_id,
            self.accepted_execution_candidate_step_id, self.untouched_gate_factory_step_id,
            self.future_callable_factory_order_id, self.future_gate_factory_order_id,
            self.callable_factory_identity_id, self.callable_constructor_identity_id,
            self.future_callable_object_id, self.gate_factory_identity_id,
            self.gate_constructor_identity_id, self.future_gate_object_id,
        )
        if not all(identifier.endswith(suffix) for identifier in indexed_ids):
            raise error("execution preflight acceptance identities must match selected repeat index")
        candidate = self.accepted_execution_candidate_step
        gate_step = self.untouched_gate_factory_step
        if not (
            candidate.step_index == 1 and candidate.role == "callable_factory"
            and candidate.step_id == self.accepted_execution_candidate_step_id
            and candidate.factory_order_id == self.future_callable_factory_order_id
            and candidate.factory_identity_id == self.callable_factory_identity_id
            and candidate.constructor_identity_id == self.callable_constructor_identity_id
            and candidate.future_object_id == self.future_callable_object_id
            and candidate.one_time_future_step and not candidate.executed
        ):
            raise error("accepted execution candidate must remain the unconsumed callable factory step")
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
            self.positive_execution_preflight_accepted,
            self.exactly_one_execution_candidate_accepted,
            self.callable_factory_candidate_accepted,
            self.callable_factory_candidate_unconsumed_accepted,
            self.callable_identity_binding_accepted,
            self.gate_factory_step_unselected_accepted,
            self.gate_factory_step_untouched_accepted,
            self.gate_factory_step_unexecuted_accepted,
            self.selected_slot_still_fresh,
            self.execution_preflight_acceptance_complete,
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
            raise error("execution preflight acceptance remains fully non-executable")
        object.__setattr__(self, "other_slots_unselected", tuple(self.other_slots_unselected))


def accept_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight(
    preflight: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflight,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightAcceptance:
    error = PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightAcceptanceError
    if not isinstance(
        preflight,
        PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflight,
    ):
        raise error("single-slot callable factory step execution preflight has the wrong type")
    required = (
        preflight.positive_order_acceptance_bound,
        preflight.exactly_one_execution_candidate_bound,
        preflight.callable_factory_candidate_bound,
        preflight.callable_factory_candidate_unconsumed,
        preflight.callable_identity_binding_accepted,
        preflight.gate_factory_step_unselected,
        preflight.gate_factory_step_untouched,
        preflight.gate_factory_step_still_unexecuted,
        preflight.selected_slot_still_fresh,
        preflight.execution_preflight_complete,
    )
    forbidden = (
        preflight.callable_factory_reference_stored, preflight.gate_factory_reference_stored,
        preflight.callable_reference_stored, preflight.factory_function_called,
        preflight.callable_factory_called, preflight.gate_factory_called,
        preflight.callable_object_created, preflight.gate_object_created,
        preflight.constructor_invoked, preflight.binding_performed,
        preflight.scheduler_available, preflight.media_decode_allowed,
        preflight.receptor_feed_allowed, preflight.start_release_granted,
        preflight.repeatability_run_allowed, preflight.repeat_run_started,
    )
    if not all(required) or any(forbidden):
        raise error("one complete fresh callable factory execution preflight is required")
    carried_fields = (
        "selected_repeat_index", "callable_factory_step_order_acceptance_id",
        "callable_factory_step_order_id", "first_factory_step_acceptance_id",
        "first_factory_step_preflight_id", "factory_execution_order_acceptance_id",
        "factory_execution_order_id", "untouched_gate_factory_step",
        "untouched_gate_factory_step_id", "future_callable_factory_order_id",
        "future_gate_factory_order_id", "callable_factory_identity_id",
        "callable_constructor_identity_id", "future_callable_object_id",
        "gate_factory_identity_id", "gate_constructor_identity_id",
        "future_gate_object_id", "logical_callable_id", "logical_gate_id",
        "reserved_executor_id", "source_id", "other_slots_unselected",
    )
    carried = {field: getattr(preflight, field) for field in carried_fields}
    index = preflight.selected_repeat_index
    return PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightAcceptance(
        acceptance_id=(
            f"{SINGLE_SLOT_CALLABLE_FACTORY_STEP_EXECUTION_PREFLIGHT_ACCEPTANCE_ID}"
            f".repeat-{index}.v1"
        ),
        execution_preflight_id=preflight.preflight_id,
        accepted_execution_candidate_step=preflight.execution_candidate_step,
        accepted_execution_candidate_step_id=preflight.execution_candidate_step_id,
        positive_execution_preflight_accepted=True,
        exactly_one_execution_candidate_accepted=True,
        callable_factory_candidate_accepted=True,
        callable_factory_candidate_unconsumed_accepted=True,
        callable_identity_binding_accepted=True,
        gate_factory_step_unselected_accepted=True,
        gate_factory_step_untouched_accepted=True,
        gate_factory_step_unexecuted_accepted=True,
        selected_slot_still_fresh=True,
        execution_preflight_acceptance_complete=True,
        **carried,
    )


def execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_step_preflight(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightAcceptance,
) -> None:
    del acceptance
    raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightAcceptanceError(
        "factory execution is not released by the locked execution preflight acceptance"
    )


def public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight_acceptance_to_jsonable(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightAcceptance,
) -> dict[str, Any]:
    return asdict(acceptance)
