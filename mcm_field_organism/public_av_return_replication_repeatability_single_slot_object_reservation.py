"""Locked object identity reservation for one repeatability slot."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_instantiation_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrder,
)


SINGLE_SLOT_OBJECT_RESERVATION_ID = (
    "public.av.nasa-earthrise.return-replication."
    "repeatability-single-slot-object-reservation.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotObjectReservationError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotObjectReservation:
    reservation_id: str
    selected_repeat_index: int
    instantiation_order_id: str
    selected_slot_preflight_id: str
    candidate_id: str
    logical_callable_id: str
    logical_gate_id: str
    reserved_executor_id: str
    future_callable_object_id: str
    future_gate_object_id: str
    source_id: str
    exactly_one_order_bound: bool
    callable_object_identity_reserved: bool
    gate_object_identity_reserved: bool
    logical_identities_unchanged: bool
    selected_slot_still_fresh: bool
    other_slots_unselected: tuple[int, ...]
    callable_object_created: bool = False
    gate_object_created: bool = False
    object_factory_created: bool = False
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotObjectReservationError(
                "selected repeat index must be one of 1, 2, 3"
            )
        suffix = f".repeat-{self.selected_repeat_index}.v1"
        if not self.reservation_id.endswith(suffix):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotObjectReservationError(
                "reservation identity does not match selected repeat index"
            )
        if not self.future_callable_object_id.endswith(suffix):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotObjectReservationError(
                "future callable object identity does not match selected repeat index"
            )
        if not self.future_gate_object_id.endswith(suffix):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotObjectReservationError(
                "future gate object identity does not match selected repeat index"
            )
        expected_unselected = tuple(
            index for index in (1, 2, 3) if index != self.selected_repeat_index
        )
        if tuple(self.other_slots_unselected) != expected_unselected:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotObjectReservationError(
                "other slots must remain unselected"
            )
        required = (
            self.exactly_one_order_bound,
            self.callable_object_identity_reserved,
            self.gate_object_identity_reserved,
            self.logical_identities_unchanged,
            self.selected_slot_still_fresh,
        )
        forbidden = (
            self.callable_object_created,
            self.gate_object_created,
            self.object_factory_created,
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotObjectReservationError(
                "object reservation must remain identity-only, receptor-locked, and run-locked"
            )
        object.__setattr__(self, "other_slots_unselected", tuple(self.other_slots_unselected))


def reserve_public_av_return_replication_repeatability_single_slot_objects(
    order: PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrder,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotObjectReservation:
    if not isinstance(
        order,
        PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrder,
    ):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotObjectReservationError(
            "single-slot instantiation order has the wrong type"
        )
    if not (
        order.exactly_one_slot_selected
        and order.selected_slot_is_fresh
        and order.callable_identity_bound
        and order.gate_identity_bound
    ):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotObjectReservationError(
            "one complete fresh single-slot order is required"
        )
    if (
        order.callable_object_created
        or order.gate_instance_created
        or order.binding_performed
        or order.scheduler_available
        or order.media_decode_allowed
        or order.receptor_feed_allowed
        or order.start_release_granted
        or order.repeatability_run_allowed
        or order.repeat_run_started
    ):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotObjectReservationError(
            "single-slot order must remain object-free and run-locked"
        )

    index = order.selected_repeat_index
    suffix = f"repeat-{index}.v1"
    return PublicAVReturnReplicationRepeatabilitySingleSlotObjectReservation(
        reservation_id=f"{SINGLE_SLOT_OBJECT_RESERVATION_ID}.{suffix}",
        selected_repeat_index=index,
        instantiation_order_id=order.order_id,
        selected_slot_preflight_id=order.selected_slot_preflight_id,
        candidate_id=order.candidate_id,
        logical_callable_id=order.future_callable_id,
        logical_gate_id=order.reserved_gate_id,
        reserved_executor_id=order.reserved_executor_id,
        future_callable_object_id=(
            "public.av.nasa-earthrise.return-replication."
            f"single-slot-callable-object.{suffix}"
        ),
        future_gate_object_id=(
            "public.av.nasa-earthrise.return-replication."
            f"single-slot-gate-object.{suffix}"
        ),
        source_id=order.source_id,
        exactly_one_order_bound=True,
        callable_object_identity_reserved=True,
        gate_object_identity_reserved=True,
        logical_identities_unchanged=True,
        selected_slot_still_fresh=True,
        other_slots_unselected=order.other_slots_unselected,
    )


def create_public_av_return_replication_repeatability_single_slot_objects(
    reservation: PublicAVReturnReplicationRepeatabilitySingleSlotObjectReservation,
) -> None:
    del reservation
    raise PublicAVReturnReplicationRepeatabilitySingleSlotObjectReservationError(
        "object creation is not released by the locked single-slot reservation"
    )


def public_av_return_replication_repeatability_single_slot_object_reservation_to_jsonable(
    reservation: PublicAVReturnReplicationRepeatabilitySingleSlotObjectReservation,
) -> dict[str, Any]:
    return asdict(reservation)
