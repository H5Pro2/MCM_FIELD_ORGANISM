"""Locked acceptance of one callable-factory call execution preflight."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_preflight import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionPreflight,
)
from .public_av_return_replication_repeatability_single_slot_factory_execution_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep,
)

ACCEPTANCE_ID = (
    "public.av.nasa-earthrise.return-replication."
    "repeatability-single-slot-callable-factory-call-execution-preflight-acceptance.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionPreflightAcceptanceError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionPreflightAcceptance:
    acceptance_id: str
    selected_repeat_index: int
    call_execution_preflight_id: str
    callable_factory_call_order_acceptance_id: str
    callable_factory_call_order_id: str
    accepted_call_execution_candidate_step: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep
    untouched_gate_factory_step: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep
    accepted_call_execution_candidate_step_id: str
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
    positive_call_execution_preflight_accepted: bool
    exactly_one_call_execution_candidate_accepted: bool
    callable_factory_call_candidate_unconsumed_accepted: bool
    callable_identity_binding_accepted: bool
    gate_factory_step_unselected_accepted: bool
    gate_factory_step_untouched_accepted: bool
    gate_factory_step_unexecuted_accepted: bool
    selected_slot_still_fresh: bool
    call_execution_preflight_acceptance_complete: bool
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
        error = PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionPreflightAcceptanceError
        if self.selected_repeat_index not in (1, 2, 3):
            raise error("selected repeat index must be one of 1, 2, 3")
        suffix = f".repeat-{self.selected_repeat_index}.v1"
        indexed = (
            self.acceptance_id, self.call_execution_preflight_id,
            self.callable_factory_call_order_acceptance_id, self.callable_factory_call_order_id,
            self.accepted_call_execution_candidate_step_id, self.untouched_gate_factory_step_id,
            self.future_callable_factory_order_id, self.future_gate_factory_order_id,
            self.callable_factory_identity_id, self.callable_constructor_identity_id,
            self.future_callable_object_id, self.gate_factory_identity_id,
            self.gate_constructor_identity_id, self.future_gate_object_id,
        )
        if not all(value.endswith(suffix) for value in indexed):
            raise error("call execution acceptance identities must match selected repeat index")
        candidate = self.accepted_call_execution_candidate_step
        gate = self.untouched_gate_factory_step
        if not (
            candidate.step_index == 1 and candidate.role == "callable_factory"
            and candidate.step_id == self.accepted_call_execution_candidate_step_id
            and candidate.factory_order_id == self.future_callable_factory_order_id
            and candidate.factory_identity_id == self.callable_factory_identity_id
            and candidate.constructor_identity_id == self.callable_constructor_identity_id
            and candidate.future_object_id == self.future_callable_object_id
            and candidate.one_time_future_step and not candidate.executed
        ):
            raise error("accepted call execution candidate must remain unconsumed")
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
        expected = tuple(i for i in (1, 2, 3) if i != self.selected_repeat_index)
        if tuple(self.other_slots_unselected) != expected:
            raise error("other slots must remain unselected")
        required = (
            self.positive_call_execution_preflight_accepted,
            self.exactly_one_call_execution_candidate_accepted,
            self.callable_factory_call_candidate_unconsumed_accepted,
            self.callable_identity_binding_accepted,
            self.gate_factory_step_unselected_accepted,
            self.gate_factory_step_untouched_accepted,
            self.gate_factory_step_unexecuted_accepted,
            self.selected_slot_still_fresh,
            self.call_execution_preflight_acceptance_complete,
        )
        forbidden = (
            self.callable_factory_reference_stored, self.gate_factory_reference_stored,
            self.callable_reference_stored, self.factory_function_called,
            self.callable_factory_called, self.gate_factory_called,
            self.callable_object_created, self.gate_object_created,
            self.constructor_invoked, self.binding_performed, self.scheduler_available,
            self.media_decode_allowed, self.receptor_feed_allowed, self.start_release_granted,
            self.repeatability_run_allowed, self.repeat_run_started,
            self.stability_threshold_defined, self.memory_claim_allowed,
            self.meaning_claim_allowed, self.organization_claim_allowed, self.ai_claim_allowed,
        )
        if not all(required) or any(forbidden):
            raise error("call execution preflight acceptance remains fully non-executable")
        object.__setattr__(self, "other_slots_unselected", tuple(self.other_slots_unselected))


def accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_preflight(
    preflight: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionPreflight,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionPreflightAcceptance:
    error = PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionPreflightAcceptanceError
    if not isinstance(preflight, PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionPreflight):
        raise error("single-slot callable factory call execution preflight has the wrong type")
    required = (
        preflight.positive_call_order_acceptance_bound,
        preflight.exactly_one_call_execution_candidate_bound,
        preflight.callable_factory_call_candidate_unconsumed,
        preflight.callable_factory_identity_bound, preflight.callable_constructor_identity_bound,
        preflight.future_callable_object_identity_bound, preflight.gate_factory_step_unselected,
        preflight.gate_factory_step_untouched, preflight.gate_factory_step_still_unexecuted,
        preflight.selected_slot_still_fresh,
        preflight.callable_factory_call_execution_preflight_complete,
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
        raise error("one complete fresh call execution preflight is required")
    fields = (
        "selected_repeat_index", "callable_factory_call_order_id",
        "untouched_gate_factory_step", "untouched_gate_factory_step_id",
        "future_callable_factory_order_id", "future_gate_factory_order_id",
        "callable_factory_identity_id", "callable_constructor_identity_id",
        "future_callable_object_id", "gate_factory_identity_id",
        "gate_constructor_identity_id", "future_gate_object_id", "logical_callable_id",
        "logical_gate_id", "reserved_executor_id", "source_id", "other_slots_unselected",
    )
    carried = {field: getattr(preflight, field) for field in fields}
    index = preflight.selected_repeat_index
    return PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionPreflightAcceptance(
        acceptance_id=f"{ACCEPTANCE_ID}.repeat-{index}.v1",
        call_execution_preflight_id=preflight.preflight_id,
        callable_factory_call_order_acceptance_id=preflight.callable_factory_call_order_acceptance_id,
        accepted_call_execution_candidate_step=preflight.call_execution_candidate_step,
        accepted_call_execution_candidate_step_id=preflight.call_execution_candidate_step_id,
        positive_call_execution_preflight_accepted=True,
        exactly_one_call_execution_candidate_accepted=True,
        callable_factory_call_candidate_unconsumed_accepted=True,
        callable_identity_binding_accepted=True,
        gate_factory_step_unselected_accepted=True,
        gate_factory_step_untouched_accepted=True,
        gate_factory_step_unexecuted_accepted=True,
        selected_slot_still_fresh=True,
        call_execution_preflight_acceptance_complete=True,
        **carried,
    )


def execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_call_execution_preflight(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionPreflightAcceptance,
) -> None:
    del acceptance
    raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionPreflightAcceptanceError(
        "factory call is not released by the locked execution preflight acceptance"
    )


def public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_preflight_acceptance_to_jsonable(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionPreflightAcceptance,
) -> dict[str, Any]:
    return asdict(acceptance)
