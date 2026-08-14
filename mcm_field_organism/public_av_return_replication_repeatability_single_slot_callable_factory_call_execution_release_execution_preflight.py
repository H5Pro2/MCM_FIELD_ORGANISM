"""Locked execution preflight for one callable-factory call release order acceptance."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_order_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseOrderAcceptance,
)


ID = (
    "public.av.nasa-earthrise.return-replication.repeatability-single-slot-"
    "callable-factory-call-execution-release-execution-preflight.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflightError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflight:
    preflight_id: str
    selected_repeat_index: int
    release_order_acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseOrderAcceptance
    positive_release_order_acceptance_bound: bool
    exactly_one_execution_candidate_bound: bool
    execution_candidate_unconsumed: bool
    callable_identity_binding_accepted: bool
    gate_factory_step_unselected: bool
    gate_factory_step_untouched: bool
    gate_factory_step_still_unexecuted: bool
    selected_slot_still_fresh: bool
    actual_release_granted: bool
    execution_preflight_complete: bool
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
        error = PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflightError
        acceptance = self.release_order_acceptance
        order = acceptance.release_order
        source = order.release_preflight_acceptance.release_preflight
        if self.selected_repeat_index not in (1, 2, 3) or acceptance.selected_repeat_index != self.selected_repeat_index:
            raise error("selected repeat index mismatch")
        if not self.preflight_id.endswith(f".repeat-{self.selected_repeat_index}.v1"):
            raise error("execution preflight identity mismatch")
        candidate = source.release_candidate_step
        gate = source.untouched_gate_factory_step
        if candidate.role != "callable_factory" or candidate.executed or not candidate.one_time_future_step:
            raise error("execution candidate must remain the unconsumed callable release step")
        if gate.role != "gate_factory" or gate.executed or not gate.one_time_future_step:
            raise error("gate factory step must remain untouched")
        required = (
            self.positive_release_order_acceptance_bound,
            self.exactly_one_execution_candidate_bound,
            self.execution_candidate_unconsumed,
            self.callable_identity_binding_accepted,
            self.gate_factory_step_unselected,
            self.gate_factory_step_untouched,
            self.gate_factory_step_still_unexecuted,
            self.selected_slot_still_fresh,
            self.execution_preflight_complete,
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
            raise error("release execution preflight remains fully non-executable")


def preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseOrderAcceptance,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflight:
    error = PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflightError
    if not isinstance(acceptance, PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseOrderAcceptance):
        raise error("wrong release order acceptance type")
    required = (
        acceptance.positive_release_order_accepted,
        acceptance.exactly_one_future_release_step_accepted,
        acceptance.release_step_unconsumed_accepted,
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
        raise error("one complete locked release order acceptance is required")
    index = acceptance.selected_repeat_index
    return PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflight(
        preflight_id=f"{ID}.repeat-{index}.v1",
        selected_repeat_index=index,
        release_order_acceptance=acceptance,
        positive_release_order_acceptance_bound=True,
        exactly_one_execution_candidate_bound=True,
        execution_candidate_unconsumed=True,
        callable_identity_binding_accepted=True,
        gate_factory_step_unselected=True,
        gate_factory_step_untouched=True,
        gate_factory_step_still_unexecuted=True,
        selected_slot_still_fresh=True,
        actual_release_granted=False,
        execution_preflight_complete=True,
    )


def execute_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_preflight(
    preflight: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflight,
) -> None:
    del preflight
    raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflightError(
        "factory call execution release remains locked"
    )


def public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_preflight_to_jsonable(
    preflight: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflight,
) -> dict[str, Any]:
    return asdict(preflight)
