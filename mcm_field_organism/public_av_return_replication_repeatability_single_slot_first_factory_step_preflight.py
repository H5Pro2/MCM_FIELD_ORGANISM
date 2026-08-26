"""Locked preflight for the first callable-factory execution step."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_factory_execution_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep,
)
from .public_av_return_replication_repeatability_single_slot_factory_execution_order_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderAcceptance,
)


SINGLE_SLOT_FIRST_FACTORY_STEP_PREFLIGHT_ID = (
    "public.av.nasa-earthrise.return-replication."
    "repeatability-single-slot-first-factory-step-preflight.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepPreflightError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepPreflight:
    preflight_id: str
    selected_repeat_index: int
    factory_execution_order_acceptance_id: str
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
    selected_factory_step: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep
    untouched_gate_factory_step: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep
    selected_callable_factory_step_id: str
    untouched_gate_factory_step_id: str
    future_callable_factory_order_id: str
    future_gate_factory_order_id: str
    callable_factory_identity_id: str
    gate_factory_identity_id: str
    callable_constructor_identity_id: str
    gate_constructor_identity_id: str
    future_callable_object_id: str
    future_gate_object_id: str
    source_id: str
    positive_execution_order_acceptance_bound: bool
    exactly_one_callable_factory_step_selected: bool
    callable_factory_step_unconsumed: bool
    callable_factory_identity_bound: bool
    callable_constructor_identity_bound: bool
    future_callable_object_identity_bound: bool
    gate_factory_step_unselected: bool
    gate_factory_step_untouched: bool
    gate_factory_step_still_unexecuted: bool
    selected_slot_still_fresh: bool
    first_factory_step_preflight_complete: bool
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepPreflightError(
                "selected repeat index must be one of 1, 2, 3"
            )
        suffix = f".repeat-{self.selected_repeat_index}.v1"
        indexed_ids = (
            self.preflight_id, self.factory_execution_order_acceptance_id,
            self.factory_execution_order_id, self.execution_acceptance_id,
            self.execution_preflight_id, self.factory_order_acceptance_id,
            self.factory_order_id, self.factory_call_acceptance_id,
            self.factory_call_preflight_id, self.factory_acceptance_id,
            self.factory_binding_id, self.callable_factory_identity_id,
            self.gate_factory_identity_id, self.callable_constructor_identity_id,
            self.gate_constructor_identity_id, self.future_callable_object_id,
            self.future_gate_object_id, self.future_callable_factory_order_id,
            self.future_gate_factory_order_id, self.selected_callable_factory_step_id,
            self.untouched_gate_factory_step_id,
        )
        if not all(identifier.endswith(suffix) for identifier in indexed_ids):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepPreflightError(
                "first factory step preflight identities must match selected repeat index"
            )
        if not (
            self.selected_factory_step.step_index == 1
            and self.selected_factory_step.role == "callable_factory"
            and self.selected_factory_step.step_id == self.selected_callable_factory_step_id
            and self.selected_factory_step.factory_order_id == self.future_callable_factory_order_id
            and self.selected_factory_step.factory_identity_id == self.callable_factory_identity_id
            and self.selected_factory_step.constructor_identity_id == self.callable_constructor_identity_id
            and self.selected_factory_step.future_object_id == self.future_callable_object_id
            and self.selected_factory_step.one_time_future_step
            and not self.selected_factory_step.executed
        ):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepPreflightError(
                "only the first unconsumed callable factory step can be selected"
            )
        if not (
            self.untouched_gate_factory_step.step_index == 2
            and self.untouched_gate_factory_step.role == "gate_factory"
            and self.untouched_gate_factory_step.step_id == self.untouched_gate_factory_step_id
            and self.untouched_gate_factory_step.factory_order_id == self.future_gate_factory_order_id
            and self.untouched_gate_factory_step.factory_identity_id == self.gate_factory_identity_id
            and self.untouched_gate_factory_step.constructor_identity_id == self.gate_constructor_identity_id
            and self.untouched_gate_factory_step.future_object_id == self.future_gate_object_id
            and self.untouched_gate_factory_step.one_time_future_step
            and not self.untouched_gate_factory_step.executed
        ):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepPreflightError(
                "the gate factory step must remain untouched and unexecuted"
            )
        expected = tuple(index for index in (1, 2, 3) if index != self.selected_repeat_index)
        if tuple(self.other_slots_unselected) != expected:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepPreflightError(
                "other slots must remain unselected"
            )
        required = (
            self.positive_execution_order_acceptance_bound,
            self.exactly_one_callable_factory_step_selected,
            self.callable_factory_step_unconsumed,
            self.callable_factory_identity_bound,
            self.callable_constructor_identity_bound,
            self.future_callable_object_identity_bound,
            self.gate_factory_step_unselected,
            self.gate_factory_step_untouched,
            self.gate_factory_step_still_unexecuted,
            self.selected_slot_still_fresh,
            self.first_factory_step_preflight_complete,
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepPreflightError(
                "first factory step preflight remains fully non-executable"
            )
        object.__setattr__(self, "other_slots_unselected", tuple(self.other_slots_unselected))


def preflight_public_av_return_replication_repeatability_single_slot_first_factory_step(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderAcceptance,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepPreflight:
    if not isinstance(acceptance, PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderAcceptance):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepPreflightError(
            "single-slot factory execution order acceptance has the wrong type"
        )
    required = (
        acceptance.positive_factory_execution_order_accepted,
        acceptance.exactly_two_future_steps_accepted,
        acceptance.callable_factory_step_first_accepted,
        acceptance.gate_factory_step_second_accepted,
        acceptance.execution_steps_one_time_accepted,
        acceptance.execution_steps_unexecuted_accepted,
        acceptance.identity_chain_accepted,
        acceptance.selected_slot_still_fresh,
        acceptance.factory_execution_order_acceptance_complete,
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
        raise PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepPreflightError(
            "one complete fresh execution order acceptance is required"
        )
    steps = tuple(acceptance.accepted_future_execution_steps)
    if len(steps) != 2:
        raise PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepPreflightError(
            "exactly two accepted future steps are required"
        )
    callable_step, gate_step = steps
    index = acceptance.selected_repeat_index
    identity_fields = (
        "selected_repeat_index", "factory_execution_order_id", "execution_acceptance_id",
        "execution_preflight_id", "factory_order_acceptance_id", "factory_order_id",
        "factory_call_acceptance_id", "factory_call_preflight_id", "factory_acceptance_id",
        "factory_binding_id", "construction_acceptance_id", "construction_id",
        "object_reservation_id", "candidate_id", "logical_callable_id", "logical_gate_id",
        "reserved_executor_id", "future_callable_object_id", "future_gate_object_id",
        "future_callable_factory_order_id", "future_gate_factory_order_id",
        "source_id", "other_slots_unselected",
    )
    carried = {field: getattr(acceptance, field) for field in identity_fields}
    return PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepPreflight(
        preflight_id=f"{SINGLE_SLOT_FIRST_FACTORY_STEP_PREFLIGHT_ID}.repeat-{index}.v1",
        factory_execution_order_acceptance_id=acceptance.acceptance_id,
        selected_factory_step=callable_step,
        untouched_gate_factory_step=gate_step,
        selected_callable_factory_step_id=callable_step.step_id,
        untouched_gate_factory_step_id=gate_step.step_id,
        callable_factory_identity_id=acceptance.future_callable_factory_id,
        gate_factory_identity_id=acceptance.future_gate_factory_id,
        callable_constructor_identity_id=acceptance.callable_constructor_id,
        gate_constructor_identity_id=acceptance.gate_constructor_id,
        positive_execution_order_acceptance_bound=True,
        exactly_one_callable_factory_step_selected=True,
        callable_factory_step_unconsumed=True,
        callable_factory_identity_bound=True,
        callable_constructor_identity_bound=True,
        future_callable_object_identity_bound=True,
        gate_factory_step_unselected=True,
        gate_factory_step_untouched=True,
        gate_factory_step_still_unexecuted=True,
        selected_slot_still_fresh=True,
        first_factory_step_preflight_complete=True,
        **carried,
    )


def execute_public_av_return_replication_repeatability_single_slot_first_factory_step_preflight(
    preflight: PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepPreflight,
) -> None:
    del preflight
    raise PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepPreflightError(
        "factory execution is not released by the locked first step preflight"
    )


def public_av_return_replication_repeatability_single_slot_first_factory_step_preflight_to_jsonable(
    preflight: PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepPreflight,
) -> dict[str, Any]:
    return asdict(preflight)
