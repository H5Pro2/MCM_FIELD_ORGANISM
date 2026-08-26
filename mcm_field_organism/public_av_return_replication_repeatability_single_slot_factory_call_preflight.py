"""Locked preflight for one future single-slot factory call."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_factory_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryAcceptance,
)


SINGLE_SLOT_FACTORY_CALL_PREFLIGHT_ID = (
    "public.av.nasa-earthrise.return-replication."
    "repeatability-single-slot-factory-call-preflight.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallPreflightError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallPreflight:
    preflight_id: str
    selected_repeat_index: int
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
    positive_factory_acceptance_bound: bool
    selected_factory_identities_bound: bool
    selected_constructor_identities_bound: bool
    selected_object_identities_bound: bool
    selected_slot_still_fresh: bool
    factory_call_preflight_complete: bool
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallPreflightError(
                "selected repeat index must be one of 1, 2, 3"
            )
        suffix = f".repeat-{self.selected_repeat_index}.v1"
        indexed_ids = (
            self.preflight_id,
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallPreflightError(
                "factory call preflight identities must match selected repeat index"
            )
        if self.future_callable_factory_id == self.future_gate_factory_id:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallPreflightError(
                "selected factory identities must remain unique"
            )
        expected = tuple(index for index in (1, 2, 3) if index != self.selected_repeat_index)
        if tuple(self.other_slots_unselected) != expected:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallPreflightError(
                "other slots must remain unselected"
            )
        required = (
            self.positive_factory_acceptance_bound,
            self.selected_factory_identities_bound,
            self.selected_constructor_identities_bound,
            self.selected_object_identities_bound,
            self.selected_slot_still_fresh,
            self.factory_call_preflight_complete,
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallPreflightError(
                "factory call preflight cannot store references, call factories, create objects, bind, decode, feed receptors, start runs, or release claims"
            )
        object.__setattr__(self, "other_slots_unselected", tuple(self.other_slots_unselected))


def preflight_public_av_return_replication_repeatability_single_slot_factory_call(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryAcceptance,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallPreflight:
    if not isinstance(acceptance, PublicAVReturnReplicationRepeatabilitySingleSlotFactoryAcceptance):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallPreflightError(
            "single-slot factory acceptance has the wrong type"
        )
    required = (
        acceptance.factory_binding_accepted,
        acceptance.constructor_identities_accepted,
        acceptance.factory_identities_accepted,
        acceptance.object_identities_accepted,
        acceptance.callable_gate_identities_accepted,
        acceptance.selected_slot_still_fresh,
        acceptance.factory_acceptance_complete,
    )
    forbidden = (
        acceptance.callable_factory_reference_stored,
        acceptance.gate_factory_reference_stored,
        acceptance.callable_reference_stored,
        acceptance.factory_function_called,
        acceptance.callable_factory_called,
        acceptance.gate_factory_called,
        acceptance.callable_object_created,
        acceptance.gate_object_created,
        acceptance.constructor_invoked,
        acceptance.binding_performed,
        acceptance.scheduler_available,
        acceptance.media_decode_allowed,
        acceptance.receptor_feed_allowed,
        acceptance.start_release_granted,
        acceptance.repeatability_run_allowed,
        acceptance.repeat_run_started,
    )
    if not all(required) or any(forbidden):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallPreflightError(
            "one complete fresh reference-free factory acceptance is required"
        )

    index = acceptance.selected_repeat_index
    suffix = f"repeat-{index}.v1"
    return PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallPreflight(
        preflight_id=f"{SINGLE_SLOT_FACTORY_CALL_PREFLIGHT_ID}.{suffix}",
        selected_repeat_index=index,
        factory_acceptance_id=acceptance.acceptance_id,
        factory_binding_id=acceptance.factory_binding_id,
        construction_acceptance_id=acceptance.construction_acceptance_id,
        construction_id=acceptance.construction_id,
        object_reservation_id=acceptance.object_reservation_id,
        candidate_id=acceptance.candidate_id,
        logical_callable_id=acceptance.logical_callable_id,
        logical_gate_id=acceptance.logical_gate_id,
        reserved_executor_id=acceptance.reserved_executor_id,
        future_callable_object_id=acceptance.future_callable_object_id,
        future_gate_object_id=acceptance.future_gate_object_id,
        callable_constructor_id=acceptance.callable_constructor_id,
        gate_constructor_id=acceptance.gate_constructor_id,
        future_callable_factory_id=acceptance.future_callable_factory_id,
        future_gate_factory_id=acceptance.future_gate_factory_id,
        source_id=acceptance.source_id,
        positive_factory_acceptance_bound=True,
        selected_factory_identities_bound=True,
        selected_constructor_identities_bound=True,
        selected_object_identities_bound=True,
        selected_slot_still_fresh=True,
        factory_call_preflight_complete=True,
        other_slots_unselected=acceptance.other_slots_unselected,
    )


def call_public_av_return_replication_repeatability_single_slot_preflighted_factories(
    preflight: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallPreflight,
) -> None:
    del preflight
    raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallPreflightError(
        "factory calls are not released by the locked single-slot factory call preflight"
    )


def public_av_return_replication_repeatability_single_slot_factory_call_preflight_to_jsonable(
    preflight: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallPreflight,
) -> dict[str, Any]:
    return asdict(preflight)
