"""Locked acceptance of the first callable-factory step preflight."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_factory_execution_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep,
)
from .public_av_return_replication_repeatability_single_slot_first_factory_step_preflight import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepPreflight,
)


SINGLE_SLOT_FIRST_FACTORY_STEP_ACCEPTANCE_ID = (
    "public.av.nasa-earthrise.return-replication."
    "repeatability-single-slot-first-factory-step-acceptance.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepAcceptanceError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepAcceptance:
    acceptance_id: str
    selected_repeat_index: int
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
    gate_factory_identity_id: str
    callable_constructor_identity_id: str
    gate_constructor_identity_id: str
    future_callable_object_id: str
    future_gate_object_id: str
    logical_callable_id: str
    logical_gate_id: str
    reserved_executor_id: str
    source_id: str
    positive_first_step_preflight_accepted: bool
    callable_factory_step_selection_accepted: bool
    callable_factory_step_unconsumed_accepted: bool
    callable_identity_binding_accepted: bool
    gate_factory_step_unselected_accepted: bool
    gate_factory_step_untouched_accepted: bool
    gate_factory_step_unexecuted_accepted: bool
    selected_slot_still_fresh: bool
    first_factory_step_acceptance_complete: bool
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepAcceptanceError(
                "selected repeat index must be one of 1, 2, 3"
            )
        suffix = f".repeat-{self.selected_repeat_index}.v1"
        indexed_ids = (
            self.acceptance_id, self.first_factory_step_preflight_id,
            self.factory_execution_order_acceptance_id, self.factory_execution_order_id,
            self.selected_callable_factory_step_id, self.untouched_gate_factory_step_id,
            self.future_callable_factory_order_id, self.future_gate_factory_order_id,
            self.callable_factory_identity_id, self.gate_factory_identity_id,
            self.callable_constructor_identity_id, self.gate_constructor_identity_id,
            self.future_callable_object_id, self.future_gate_object_id,
        )
        if not all(identifier.endswith(suffix) for identifier in indexed_ids):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepAcceptanceError(
                "first step acceptance identities must match selected repeat index"
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepAcceptanceError(
                "accepted callable factory step must remain selected and unconsumed"
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepAcceptanceError(
                "gate factory step must remain untouched and unexecuted"
            )
        expected = tuple(index for index in (1, 2, 3) if index != self.selected_repeat_index)
        if tuple(self.other_slots_unselected) != expected:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepAcceptanceError(
                "other slots must remain unselected"
            )
        required = (
            self.positive_first_step_preflight_accepted,
            self.callable_factory_step_selection_accepted,
            self.callable_factory_step_unconsumed_accepted,
            self.callable_identity_binding_accepted,
            self.gate_factory_step_unselected_accepted,
            self.gate_factory_step_untouched_accepted,
            self.gate_factory_step_unexecuted_accepted,
            self.selected_slot_still_fresh,
            self.first_factory_step_acceptance_complete,
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepAcceptanceError(
                "first factory step acceptance remains fully non-executable"
            )
        object.__setattr__(self, "other_slots_unselected", tuple(self.other_slots_unselected))


def accept_public_av_return_replication_repeatability_single_slot_first_factory_step_preflight(
    preflight: PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepPreflight,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepAcceptance:
    if not isinstance(preflight, PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepPreflight):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepAcceptanceError(
            "single-slot first factory step preflight has the wrong type"
        )
    required = (
        preflight.positive_execution_order_acceptance_bound,
        preflight.exactly_one_callable_factory_step_selected,
        preflight.callable_factory_step_unconsumed,
        preflight.callable_factory_identity_bound,
        preflight.callable_constructor_identity_bound,
        preflight.future_callable_object_identity_bound,
        preflight.gate_factory_step_unselected,
        preflight.gate_factory_step_untouched,
        preflight.gate_factory_step_still_unexecuted,
        preflight.selected_slot_still_fresh,
        preflight.first_factory_step_preflight_complete,
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
        raise PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepAcceptanceError(
            "one complete fresh non-executable first step preflight is required"
        )
    index = preflight.selected_repeat_index
    return PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepAcceptance(
        acceptance_id=f"{SINGLE_SLOT_FIRST_FACTORY_STEP_ACCEPTANCE_ID}.repeat-{index}.v1",
        selected_repeat_index=index,
        first_factory_step_preflight_id=preflight.preflight_id,
        factory_execution_order_acceptance_id=preflight.factory_execution_order_acceptance_id,
        factory_execution_order_id=preflight.factory_execution_order_id,
        selected_factory_step=preflight.selected_factory_step,
        untouched_gate_factory_step=preflight.untouched_gate_factory_step,
        selected_callable_factory_step_id=preflight.selected_callable_factory_step_id,
        untouched_gate_factory_step_id=preflight.untouched_gate_factory_step_id,
        future_callable_factory_order_id=preflight.future_callable_factory_order_id,
        future_gate_factory_order_id=preflight.future_gate_factory_order_id,
        callable_factory_identity_id=preflight.callable_factory_identity_id,
        gate_factory_identity_id=preflight.gate_factory_identity_id,
        callable_constructor_identity_id=preflight.callable_constructor_identity_id,
        gate_constructor_identity_id=preflight.gate_constructor_identity_id,
        future_callable_object_id=preflight.future_callable_object_id,
        future_gate_object_id=preflight.future_gate_object_id,
        logical_callable_id=preflight.logical_callable_id,
        logical_gate_id=preflight.logical_gate_id,
        reserved_executor_id=preflight.reserved_executor_id,
        source_id=preflight.source_id,
        positive_first_step_preflight_accepted=True,
        callable_factory_step_selection_accepted=True,
        callable_factory_step_unconsumed_accepted=True,
        callable_identity_binding_accepted=True,
        gate_factory_step_unselected_accepted=True,
        gate_factory_step_untouched_accepted=True,
        gate_factory_step_unexecuted_accepted=True,
        selected_slot_still_fresh=True,
        first_factory_step_acceptance_complete=True,
        other_slots_unselected=preflight.other_slots_unselected,
    )


def execute_public_av_return_replication_repeatability_single_slot_accepted_first_factory_step(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepAcceptance,
) -> None:
    del acceptance
    raise PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepAcceptanceError(
        "factory execution is not released by the locked first step acceptance"
    )


def public_av_return_replication_repeatability_single_slot_first_factory_step_acceptance_to_jsonable(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepAcceptance,
) -> dict[str, Any]:
    return asdict(acceptance)
