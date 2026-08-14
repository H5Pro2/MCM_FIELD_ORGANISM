"""Locked acceptance of one single-slot factory order execution preflight."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_factory_order_execution_preflight import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionPreflight,
)


SINGLE_SLOT_FACTORY_ORDER_EXECUTION_ACCEPTANCE_ID = (
    "public.av.nasa-earthrise.return-replication."
    "repeatability-single-slot-factory-order-execution-acceptance.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionAcceptanceError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionAcceptance:
    acceptance_id: str
    selected_repeat_index: int
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
    future_callable_object_id: str
    future_gate_object_id: str
    callable_constructor_id: str
    gate_constructor_id: str
    future_callable_factory_id: str
    future_gate_factory_id: str
    future_callable_factory_order_id: str
    future_gate_factory_order_id: str
    ordered_factory_execution_candidate_ids: tuple[str, str]
    source_id: str
    positive_execution_preflight_accepted: bool
    two_ordered_execution_candidates_accepted: bool
    callable_factory_candidate_first_accepted: bool
    gate_factory_candidate_second_accepted: bool
    fixed_candidate_order_accepted: bool
    factory_order_identities_accepted: bool
    selected_slot_still_fresh: bool
    factory_order_execution_acceptance_complete: bool
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionAcceptanceError(
                "selected repeat index must be one of 1, 2, 3"
            )
        suffix = f".repeat-{self.selected_repeat_index}.v1"
        indexed_ids = (
            self.acceptance_id, self.execution_preflight_id, self.factory_order_acceptance_id,
            self.factory_order_id, self.factory_call_acceptance_id,
            self.factory_call_preflight_id, self.factory_acceptance_id, self.factory_binding_id,
            self.callable_constructor_id, self.gate_constructor_id,
            self.future_callable_factory_id, self.future_gate_factory_id,
            self.future_callable_object_id, self.future_gate_object_id,
            self.future_callable_factory_order_id, self.future_gate_factory_order_id,
        )
        if not all(identifier.endswith(suffix) for identifier in indexed_ids):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionAcceptanceError(
                "execution acceptance identities must match selected repeat index"
            )
        expected_candidates = (
            self.future_callable_factory_order_id,
            self.future_gate_factory_order_id,
        )
        if tuple(self.ordered_factory_execution_candidate_ids) != expected_candidates:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionAcceptanceError(
                "accepted execution candidates must remain callable then gate factory orders"
            )
        if self.future_callable_factory_order_id == self.future_gate_factory_order_id:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionAcceptanceError(
                "accepted factory order identities must remain unique"
            )
        expected = tuple(index for index in (1, 2, 3) if index != self.selected_repeat_index)
        if tuple(self.other_slots_unselected) != expected:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionAcceptanceError(
                "other slots must remain unselected"
            )
        required = (
            self.positive_execution_preflight_accepted,
            self.two_ordered_execution_candidates_accepted,
            self.callable_factory_candidate_first_accepted,
            self.gate_factory_candidate_second_accepted,
            self.fixed_candidate_order_accepted,
            self.factory_order_identities_accepted,
            self.selected_slot_still_fresh,
            self.factory_order_execution_acceptance_complete,
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionAcceptanceError(
                "execution acceptance cannot store references, call factories, create objects, bind, decode, feed receptors, start runs, or release claims"
            )
        object.__setattr__(
            self, "ordered_factory_execution_candidate_ids",
            tuple(self.ordered_factory_execution_candidate_ids),
        )
        object.__setattr__(self, "other_slots_unselected", tuple(self.other_slots_unselected))


def accept_public_av_return_replication_repeatability_single_slot_factory_order_execution_preflight(
    preflight: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionPreflight,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionAcceptance:
    if not isinstance(preflight, PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionPreflight):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionAcceptanceError(
            "single-slot factory order execution preflight has the wrong type"
        )
    required = (
        preflight.positive_factory_order_acceptance_bound,
        preflight.two_ordered_execution_candidates_bound,
        preflight.callable_factory_execution_candidate_first,
        preflight.gate_factory_execution_candidate_second,
        preflight.execution_candidate_order_fixed,
        preflight.factory_order_identities_bound,
        preflight.selected_slot_still_fresh,
        preflight.factory_order_execution_preflight_complete,
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
        raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionAcceptanceError(
            "one complete fresh reference-free execution preflight is required"
        )

    values = asdict(preflight)
    carried_fields = {
        key: value for key, value in values.items()
        if key not in {
            "preflight_id", "positive_factory_order_acceptance_bound",
            "two_ordered_execution_candidates_bound",
            "callable_factory_execution_candidate_first",
            "gate_factory_execution_candidate_second", "execution_candidate_order_fixed",
            "factory_order_identities_bound", "factory_order_execution_preflight_complete",
        }
    }
    index = preflight.selected_repeat_index
    return PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionAcceptance(
        acceptance_id=f"{SINGLE_SLOT_FACTORY_ORDER_EXECUTION_ACCEPTANCE_ID}.repeat-{index}.v1",
        execution_preflight_id=preflight.preflight_id,
        positive_execution_preflight_accepted=True,
        two_ordered_execution_candidates_accepted=True,
        callable_factory_candidate_first_accepted=True,
        gate_factory_candidate_second_accepted=True,
        fixed_candidate_order_accepted=True,
        factory_order_identities_accepted=True,
        factory_order_execution_acceptance_complete=True,
        **carried_fields,
    )


def execute_public_av_return_replication_repeatability_single_slot_accepted_factory_order_execution(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionAcceptance,
) -> None:
    del acceptance
    raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionAcceptanceError(
        "factory order execution is not released by the locked execution acceptance"
    )


def public_av_return_replication_repeatability_single_slot_factory_order_execution_acceptance_to_jsonable(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionAcceptance,
) -> dict[str, Any]:
    return asdict(acceptance)
