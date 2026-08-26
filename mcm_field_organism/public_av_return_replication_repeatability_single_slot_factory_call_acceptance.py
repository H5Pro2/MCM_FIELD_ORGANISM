"""Locked acceptance of one single-slot factory call preflight."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_factory_call_preflight import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallPreflight,
)


SINGLE_SLOT_FACTORY_CALL_ACCEPTANCE_ID = (
    "public.av.nasa-earthrise.return-replication."
    "repeatability-single-slot-factory-call-acceptance.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallAcceptanceError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallAcceptance:
    acceptance_id: str
    selected_repeat_index: int
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
    source_id: str
    positive_factory_call_preflight_accepted: bool
    factory_identities_accepted: bool
    constructor_identities_accepted: bool
    object_identities_accepted: bool
    callable_gate_executor_identities_accepted: bool
    source_identity_accepted: bool
    selected_slot_still_fresh: bool
    factory_call_acceptance_complete: bool
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallAcceptanceError(
                "selected repeat index must be one of 1, 2, 3"
            )
        suffix = f".repeat-{self.selected_repeat_index}.v1"
        indexed_ids = (
            self.acceptance_id,
            self.factory_call_preflight_id,
            self.factory_acceptance_id,
            self.factory_binding_id,
            self.callable_constructor_id,
            self.gate_constructor_id,
            self.future_callable_factory_id,
            self.future_gate_factory_id,
            self.future_callable_object_id,
            self.future_gate_object_id,
        )
        if not all(identifier.endswith(suffix) for identifier in indexed_ids):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallAcceptanceError(
                "factory call acceptance identities must match selected repeat index"
            )
        if self.future_callable_factory_id == self.future_gate_factory_id:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallAcceptanceError(
                "accepted factory identities must remain unique"
            )
        expected = tuple(index for index in (1, 2, 3) if index != self.selected_repeat_index)
        if tuple(self.other_slots_unselected) != expected:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallAcceptanceError(
                "other slots must remain unselected"
            )
        required = (
            self.positive_factory_call_preflight_accepted,
            self.factory_identities_accepted,
            self.constructor_identities_accepted,
            self.object_identities_accepted,
            self.callable_gate_executor_identities_accepted,
            self.source_identity_accepted,
            self.selected_slot_still_fresh,
            self.factory_call_acceptance_complete,
        )
        forbidden = (
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallAcceptanceError(
                "factory call acceptance cannot store references, call factories, create objects, bind, decode, feed receptors, start runs, or release claims"
            )
        object.__setattr__(self, "other_slots_unselected", tuple(self.other_slots_unselected))


def accept_public_av_return_replication_repeatability_single_slot_factory_call_preflight(
    preflight: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallPreflight,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallAcceptance:
    if not isinstance(preflight, PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallPreflight):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallAcceptanceError(
            "single-slot factory call preflight has the wrong type"
        )
    required = (
        preflight.positive_factory_acceptance_bound,
        preflight.selected_factory_identities_bound,
        preflight.selected_constructor_identities_bound,
        preflight.selected_object_identities_bound,
        preflight.selected_slot_still_fresh,
        preflight.factory_call_preflight_complete,
    )
    forbidden = (
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
    )
    if not all(required) or any(forbidden):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallAcceptanceError(
            "one complete fresh reference-free factory call preflight is required"
        )

    index = preflight.selected_repeat_index
    return PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallAcceptance(
        acceptance_id=f"{SINGLE_SLOT_FACTORY_CALL_ACCEPTANCE_ID}.repeat-{index}.v1",
        selected_repeat_index=index,
        factory_call_preflight_id=preflight.preflight_id,
        factory_acceptance_id=preflight.factory_acceptance_id,
        factory_binding_id=preflight.factory_binding_id,
        construction_acceptance_id=preflight.construction_acceptance_id,
        construction_id=preflight.construction_id,
        object_reservation_id=preflight.object_reservation_id,
        candidate_id=preflight.candidate_id,
        logical_callable_id=preflight.logical_callable_id,
        logical_gate_id=preflight.logical_gate_id,
        reserved_executor_id=preflight.reserved_executor_id,
        future_callable_object_id=preflight.future_callable_object_id,
        future_gate_object_id=preflight.future_gate_object_id,
        callable_constructor_id=preflight.callable_constructor_id,
        gate_constructor_id=preflight.gate_constructor_id,
        future_callable_factory_id=preflight.future_callable_factory_id,
        future_gate_factory_id=preflight.future_gate_factory_id,
        source_id=preflight.source_id,
        positive_factory_call_preflight_accepted=True,
        factory_identities_accepted=True,
        constructor_identities_accepted=True,
        object_identities_accepted=True,
        callable_gate_executor_identities_accepted=True,
        source_identity_accepted=True,
        selected_slot_still_fresh=True,
        factory_call_acceptance_complete=True,
        other_slots_unselected=preflight.other_slots_unselected,
    )


def call_public_av_return_replication_repeatability_single_slot_accepted_factory_call(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallAcceptance,
) -> None:
    del acceptance
    raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallAcceptanceError(
        "factory calls are not released by the locked single-slot factory call acceptance"
    )


def public_av_return_replication_repeatability_single_slot_factory_call_acceptance_to_jsonable(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallAcceptance,
) -> dict[str, Any]:
    return asdict(acceptance)
