"""Locked factory order contract for one repeatability slot."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_factory_call_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallAcceptance,
)


SINGLE_SLOT_FACTORY_ORDER_ID = (
    "public.av.nasa-earthrise.return-replication."
    "repeatability-single-slot-factory-order.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrder:
    order_id: str
    selected_repeat_index: int
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
    positive_factory_call_acceptance_bound: bool
    exactly_one_callable_factory_order_derived: bool
    exactly_one_gate_factory_order_derived: bool
    factory_order_identities_unique: bool
    factory_identities_bound: bool
    constructor_identities_bound: bool
    object_identities_bound: bool
    selected_slot_still_fresh: bool
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderError(
                "selected repeat index must be one of 1, 2, 3"
            )
        suffix = f".repeat-{self.selected_repeat_index}.v1"
        indexed_ids = (
            self.order_id,
            self.factory_call_acceptance_id,
            self.factory_call_preflight_id,
            self.factory_acceptance_id,
            self.factory_binding_id,
            self.callable_constructor_id,
            self.gate_constructor_id,
            self.future_callable_factory_id,
            self.future_gate_factory_id,
            self.future_callable_object_id,
            self.future_gate_object_id,
            self.future_callable_factory_order_id,
            self.future_gate_factory_order_id,
        )
        if not all(identifier.endswith(suffix) for identifier in indexed_ids):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderError(
                "factory order identities must match selected repeat index"
            )
        if self.future_callable_factory_order_id == self.future_gate_factory_order_id:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderError(
                "callable and gate factory order identities must be unique"
            )
        if self.future_callable_factory_id == self.future_gate_factory_id:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderError(
                "factory identities must remain unique"
            )
        expected = tuple(index for index in (1, 2, 3) if index != self.selected_repeat_index)
        if tuple(self.other_slots_unselected) != expected:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderError(
                "other slots must remain unselected"
            )
        required = (
            self.positive_factory_call_acceptance_bound,
            self.exactly_one_callable_factory_order_derived,
            self.exactly_one_gate_factory_order_derived,
            self.factory_order_identities_unique,
            self.factory_identities_bound,
            self.constructor_identities_bound,
            self.object_identities_bound,
            self.selected_slot_still_fresh,
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderError(
                "factory order cannot store references, call factories, create objects, bind, decode, feed receptors, start runs, or release claims"
            )
        object.__setattr__(self, "other_slots_unselected", tuple(self.other_slots_unselected))


def order_public_av_return_replication_repeatability_single_slot_factories(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallAcceptance,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrder:
    if not isinstance(acceptance, PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallAcceptance):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderError(
            "single-slot factory call acceptance has the wrong type"
        )
    required = (
        acceptance.positive_factory_call_preflight_accepted,
        acceptance.factory_identities_accepted,
        acceptance.constructor_identities_accepted,
        acceptance.object_identities_accepted,
        acceptance.callable_gate_executor_identities_accepted,
        acceptance.source_identity_accepted,
        acceptance.selected_slot_still_fresh,
        acceptance.factory_call_acceptance_complete,
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
        raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderError(
            "one complete fresh reference-free factory call acceptance is required"
        )

    index = acceptance.selected_repeat_index
    suffix = f"repeat-{index}.v1"
    return PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrder(
        order_id=f"{SINGLE_SLOT_FACTORY_ORDER_ID}.{suffix}",
        selected_repeat_index=index,
        factory_call_acceptance_id=acceptance.acceptance_id,
        factory_call_preflight_id=acceptance.factory_call_preflight_id,
        factory_acceptance_id=acceptance.factory_acceptance_id,
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
        future_callable_factory_order_id=(
            "public.av.nasa-earthrise.return-replication."
            f"single-slot-callable-factory-order.{suffix}"
        ),
        future_gate_factory_order_id=(
            "public.av.nasa-earthrise.return-replication."
            f"single-slot-gate-factory-order.{suffix}"
        ),
        source_id=acceptance.source_id,
        positive_factory_call_acceptance_bound=True,
        exactly_one_callable_factory_order_derived=True,
        exactly_one_gate_factory_order_derived=True,
        factory_order_identities_unique=True,
        factory_identities_bound=True,
        constructor_identities_bound=True,
        object_identities_bound=True,
        selected_slot_still_fresh=True,
        other_slots_unselected=acceptance.other_slots_unselected,
    )


def execute_public_av_return_replication_repeatability_single_slot_factory_order(
    order: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrder,
) -> None:
    del order
    raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderError(
        "factory orders are not executable in the locked single-slot factory order contract"
    )


def public_av_return_replication_repeatability_single_slot_factory_order_to_jsonable(
    order: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrder,
) -> dict[str, Any]:
    return asdict(order)
