"""Locked acceptance of one callable-factory call execution release execution preflight."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_preflight import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflight,
)


ID = (
    "public.av.nasa-earthrise.return-replication.repeatability-single-slot-"
    "callable-factory-call-execution-release-execution-preflight-acceptance.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflightAcceptanceError(
    ValueError
):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflightAcceptance:
    acceptance_id: str
    selected_repeat_index: int
    release_execution_preflight: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflight
    positive_execution_preflight_accepted: bool
    exactly_one_execution_candidate_accepted: bool
    execution_candidate_unconsumed_accepted: bool
    actual_release_absence_accepted: bool
    callable_identity_binding_accepted: bool
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
        error = PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflightAcceptanceError
        preflight = self.release_execution_preflight
        source = preflight.release_order_acceptance.release_order.release_preflight_acceptance.release_preflight
        if self.selected_repeat_index not in (1, 2, 3) or preflight.selected_repeat_index != self.selected_repeat_index:
            raise error("selected repeat index mismatch")
        if not self.acceptance_id.endswith(f".repeat-{self.selected_repeat_index}.v1"):
            raise error("acceptance identity mismatch")
        candidate = source.release_candidate_step
        gate = source.untouched_gate_factory_step
        if candidate.role != "callable_factory" or candidate.executed or not candidate.one_time_future_step:
            raise error("execution candidate must remain unconsumed")
        if gate.role != "gate_factory" or gate.executed or not gate.one_time_future_step:
            raise error("gate step must remain untouched")
        required = (
            self.positive_execution_preflight_accepted,
            self.exactly_one_execution_candidate_accepted,
            self.execution_candidate_unconsumed_accepted,
            self.actual_release_absence_accepted,
            self.callable_identity_binding_accepted,
            self.gate_step_untouched_accepted,
            self.selected_slot_still_fresh,
            self.acceptance_complete,
        )
        forbidden = (
            self.actual_release_granted,
            self.callable_factory_reference_stored,
            self.gate_factory_reference_stored,
            self.callable_reference_stored,
            self.factory_function_called,
            self.callable_factory_called,
            self.gate_factory_called,
            self.callable_object_created,
            self.gate_object_created,
            self.constructor_invoked,
            self.binding_performed,
            self.scheduler_available,
            self.media_decode_allowed,
            self.receptor_feed_allowed,
            self.start_release_granted,
            self.repeatability_run_allowed,
            self.repeat_run_started,
            self.stability_threshold_defined,
            self.memory_claim_allowed,
            self.meaning_claim_allowed,
            self.organization_claim_allowed,
            self.ai_claim_allowed,
        )
        if not all(required) or any(forbidden):
            raise error("release execution preflight acceptance remains fully non-executable")


def accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_preflight(
    preflight: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflight,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflightAcceptance:
    error = PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflightAcceptanceError
    if not isinstance(preflight, PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflight):
        raise error("wrong release execution preflight type")
    required = (
        preflight.positive_release_order_acceptance_bound,
        preflight.exactly_one_execution_candidate_bound,
        preflight.execution_candidate_unconsumed,
        preflight.callable_identity_binding_accepted,
        preflight.gate_factory_step_unselected,
        preflight.gate_factory_step_untouched,
        preflight.gate_factory_step_still_unexecuted,
        preflight.selected_slot_still_fresh,
        preflight.execution_preflight_complete,
    )
    forbidden = (
        preflight.actual_release_granted,
        preflight.callable_factory_reference_stored,
        preflight.gate_factory_reference_stored,
        preflight.callable_reference_stored,
        preflight.factory_function_called,
        preflight.callable_factory_called,
        preflight.gate_factory_called,
        preflight.callable_object_created,
        preflight.gate_object_created,
        preflight.constructor_invoked,
        preflight.binding_performed,
        preflight.scheduler_available,
        preflight.media_decode_allowed,
        preflight.receptor_feed_allowed,
        preflight.start_release_granted,
        preflight.repeatability_run_allowed,
        preflight.repeat_run_started,
        preflight.stability_threshold_defined,
        preflight.memory_claim_allowed,
        preflight.meaning_claim_allowed,
        preflight.organization_claim_allowed,
        preflight.ai_claim_allowed,
    )
    if not all(required) or any(forbidden):
        raise error("one complete locked release execution preflight is required")
    index = preflight.selected_repeat_index
    return PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflightAcceptance(
        acceptance_id=f"{ID}.repeat-{index}.v1",
        selected_repeat_index=index,
        release_execution_preflight=preflight,
        positive_execution_preflight_accepted=True,
        exactly_one_execution_candidate_accepted=True,
        execution_candidate_unconsumed_accepted=True,
        actual_release_absence_accepted=True,
        callable_identity_binding_accepted=True,
        gate_step_untouched_accepted=True,
        selected_slot_still_fresh=True,
        acceptance_complete=True,
    )


def execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_call_execution_release_execution_preflight(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflightAcceptance,
) -> None:
    del acceptance
    raise PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflightAcceptanceError(
        "factory call execution release remains locked"
    )


def public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_preflight_acceptance_to_jsonable(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflightAcceptance,
) -> dict[str, Any]:
    return asdict(acceptance)
