"""Locked acceptance of one single-slot factory order contract."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_factory_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrder,
)


SINGLE_SLOT_FACTORY_ORDER_ACCEPTANCE_ID = (
    "public.av.nasa-earthrise.return-replication."
    "repeatability-single-slot-factory-order-acceptance.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderAcceptanceError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderAcceptance:
    acceptance_id: str
    selected_repeat_index: int
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
    source_id: str
    positive_factory_order_accepted: bool
    two_factory_order_identities_accepted: bool
    factory_order_identities_unique: bool
    factory_identities_accepted: bool
    constructor_identities_accepted: bool
    object_identities_accepted: bool
    callable_gate_executor_identities_accepted: bool
    source_identity_accepted: bool
    selected_slot_still_fresh: bool
    factory_order_acceptance_complete: bool
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderAcceptanceError(
                "selected repeat index must be one of 1, 2, 3"
            )
        suffix = f".repeat-{self.selected_repeat_index}.v1"
        indexed_ids = (
            self.acceptance_id, self.factory_order_id, self.factory_call_acceptance_id,
            self.factory_call_preflight_id, self.factory_acceptance_id, self.factory_binding_id,
            self.callable_constructor_id, self.gate_constructor_id,
            self.future_callable_factory_id, self.future_gate_factory_id,
            self.future_callable_object_id, self.future_gate_object_id,
            self.future_callable_factory_order_id, self.future_gate_factory_order_id,
        )
        if not all(identifier.endswith(suffix) for identifier in indexed_ids):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderAcceptanceError(
                "factory order acceptance identities must match selected repeat index"
            )
        if self.future_callable_factory_order_id == self.future_gate_factory_order_id:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderAcceptanceError(
                "accepted factory order identities must remain unique"
            )
        if self.future_callable_factory_id == self.future_gate_factory_id:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderAcceptanceError(
                "accepted factory identities must remain unique"
            )
        expected = tuple(index for index in (1, 2, 3) if index != self.selected_repeat_index)
        if tuple(self.other_slots_unselected) != expected:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderAcceptanceError(
                "other slots must remain unselected"
            )
        required = (
            self.positive_factory_order_accepted,
            self.two_factory_order_identities_accepted,
            self.factory_order_identities_unique,
            self.factory_identities_accepted,
            self.constructor_identities_accepted,
            self.object_identities_accepted,
            self.callable_gate_executor_identities_accepted,
            self.source_identity_accepted,
            self.selected_slot_still_fresh,
            self.factory_order_acceptance_complete,
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderAcceptanceError(
                "factory order acceptance cannot store references, call factories, create objects, bind, decode, feed receptors, start runs, or release claims"
            )
        object.__setattr__(self, "other_slots_unselected", tuple(self.other_slots_unselected))


def accept_public_av_return_replication_repeatability_single_slot_factory_order(
    order: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrder,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderAcceptance:
    if not isinstance(order, PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrder):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderAcceptanceError(
            "single-slot factory order has the wrong type"
        )
    required = (
        order.positive_factory_call_acceptance_bound,
        order.exactly_one_callable_factory_order_derived,
        order.exactly_one_gate_factory_order_derived,
        order.factory_order_identities_unique,
        order.factory_identities_bound,
        order.constructor_identities_bound,
        order.object_identities_bound,
        order.selected_slot_still_fresh,
    )
    forbidden = (
        order.callable_factory_reference_stored, order.gate_factory_reference_stored,
        order.callable_reference_stored, order.factory_function_called,
        order.callable_factory_called, order.gate_factory_called,
        order.callable_object_created, order.gate_object_created,
        order.constructor_invoked, order.binding_performed, order.scheduler_available,
        order.media_decode_allowed, order.receptor_feed_allowed,
        order.start_release_granted, order.repeatability_run_allowed, order.repeat_run_started,
    )
    if not all(required) or any(forbidden):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderAcceptanceError(
            "one complete fresh reference-free factory order is required"
        )

    index = order.selected_repeat_index
    return PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderAcceptance(
        acceptance_id=f"{SINGLE_SLOT_FACTORY_ORDER_ACCEPTANCE_ID}.repeat-{index}.v1",
        selected_repeat_index=index,
        factory_order_id=order.order_id,
        factory_call_acceptance_id=order.factory_call_acceptance_id,
        factory_call_preflight_id=order.factory_call_preflight_id,
        factory_acceptance_id=order.factory_acceptance_id,
        factory_binding_id=order.factory_binding_id,
        construction_acceptance_id=order.construction_acceptance_id,
        construction_id=order.construction_id,
        object_reservation_id=order.object_reservation_id,
        candidate_id=order.candidate_id,
        logical_callable_id=order.logical_callable_id,
        logical_gate_id=order.logical_gate_id,
        reserved_executor_id=order.reserved_executor_id,
        future_callable_object_id=order.future_callable_object_id,
        future_gate_object_id=order.future_gate_object_id,
        callable_constructor_id=order.callable_constructor_id,
        gate_constructor_id=order.gate_constructor_id,
        future_callable_factory_id=order.future_callable_factory_id,
        future_gate_factory_id=order.future_gate_factory_id,
        future_callable_factory_order_id=order.future_callable_factory_order_id,
        future_gate_factory_order_id=order.future_gate_factory_order_id,
        source_id=order.source_id,
        positive_factory_order_accepted=True,
        two_factory_order_identities_accepted=True,
        factory_order_identities_unique=True,
        factory_identities_accepted=True,
        constructor_identities_accepted=True,
        object_identities_accepted=True,
        callable_gate_executor_identities_accepted=True,
        source_identity_accepted=True,
        selected_slot_still_fresh=True,
        factory_order_acceptance_complete=True,
        other_slots_unselected=order.other_slots_unselected,
    )


def execute_public_av_return_replication_repeatability_single_slot_accepted_factory_order(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderAcceptance,
) -> None:
    del acceptance
    raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderAcceptanceError(
        "factory orders are not executable in the locked factory order acceptance"
    )


def public_av_return_replication_repeatability_single_slot_factory_order_acceptance_to_jsonable(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderAcceptance,
) -> dict[str, Any]:
    return asdict(acceptance)
