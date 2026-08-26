"""Locked constructor identity contract for one repeatability slot."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_object_reservation import (
    PublicAVReturnReplicationRepeatabilitySingleSlotObjectReservation,
)


SINGLE_SLOT_OBJECT_CONSTRUCTION_ID = (
    "public.av.nasa-earthrise.return-replication."
    "repeatability-single-slot-object-construction.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotObjectConstructionError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotObjectConstruction:
    construction_id: str
    selected_repeat_index: int
    object_reservation_id: str
    instantiation_order_id: str
    candidate_id: str
    logical_callable_id: str
    logical_gate_id: str
    reserved_executor_id: str
    future_callable_object_id: str
    future_gate_object_id: str
    callable_constructor_id: str
    gate_constructor_id: str
    source_id: str
    exactly_one_reservation_bound: bool
    reserved_object_identities_bound: bool
    constructor_identities_declared: bool
    callable_constructor_allowed_later: bool
    gate_constructor_allowed_later: bool
    selected_slot_still_fresh: bool
    other_slots_unselected: tuple[int, ...]
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotObjectConstructionError(
                "selected repeat index must be one of 1, 2, 3"
            )
        suffix = f".repeat-{self.selected_repeat_index}.v1"
        if not self.construction_id.endswith(suffix):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotObjectConstructionError(
                "construction identity does not match selected repeat index"
            )
        if not self.callable_constructor_id.endswith(suffix):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotObjectConstructionError(
                "callable constructor identity does not match selected repeat index"
            )
        if not self.gate_constructor_id.endswith(suffix):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotObjectConstructionError(
                "gate constructor identity does not match selected repeat index"
            )
        expected_unselected = tuple(
            index for index in (1, 2, 3) if index != self.selected_repeat_index
        )
        if tuple(self.other_slots_unselected) != expected_unselected:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotObjectConstructionError(
                "other slots must remain unselected"
            )
        required = (
            self.exactly_one_reservation_bound,
            self.reserved_object_identities_bound,
            self.constructor_identities_declared,
            self.callable_constructor_allowed_later,
            self.gate_constructor_allowed_later,
            self.selected_slot_still_fresh,
        )
        forbidden = (
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotObjectConstructionError(
                "object construction contract cannot call factories, create instances, bind, decode, feed receptors, start runs, or release claims"
            )
        object.__setattr__(self, "other_slots_unselected", tuple(self.other_slots_unselected))


def prepare_public_av_return_replication_repeatability_single_slot_object_construction(
    reservation: PublicAVReturnReplicationRepeatabilitySingleSlotObjectReservation,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotObjectConstruction:
    if not isinstance(
        reservation,
        PublicAVReturnReplicationRepeatabilitySingleSlotObjectReservation,
    ):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotObjectConstructionError(
            "single-slot object reservation has the wrong type"
        )
    if not (
        reservation.exactly_one_order_bound
        and reservation.callable_object_identity_reserved
        and reservation.gate_object_identity_reserved
        and reservation.selected_slot_still_fresh
    ):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotObjectConstructionError(
            "one complete fresh object reservation is required"
        )
    if (
        reservation.callable_object_created
        or reservation.gate_object_created
        or reservation.object_factory_created
        or reservation.binding_performed
        or reservation.scheduler_available
        or reservation.media_decode_allowed
        or reservation.receptor_feed_allowed
        or reservation.start_release_granted
        or reservation.repeatability_run_allowed
        or reservation.repeat_run_started
    ):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotObjectConstructionError(
            "object reservation must remain factory-free, object-free, and run-locked"
        )

    index = reservation.selected_repeat_index
    suffix = f"repeat-{index}.v1"
    return PublicAVReturnReplicationRepeatabilitySingleSlotObjectConstruction(
        construction_id=f"{SINGLE_SLOT_OBJECT_CONSTRUCTION_ID}.{suffix}",
        selected_repeat_index=index,
        object_reservation_id=reservation.reservation_id,
        instantiation_order_id=reservation.instantiation_order_id,
        candidate_id=reservation.candidate_id,
        logical_callable_id=reservation.logical_callable_id,
        logical_gate_id=reservation.logical_gate_id,
        reserved_executor_id=reservation.reserved_executor_id,
        future_callable_object_id=reservation.future_callable_object_id,
        future_gate_object_id=reservation.future_gate_object_id,
        callable_constructor_id=(
            "public.av.nasa-earthrise.return-replication."
            f"single-slot-callable-constructor.{suffix}"
        ),
        gate_constructor_id=(
            "public.av.nasa-earthrise.return-replication."
            f"single-slot-gate-constructor.{suffix}"
        ),
        source_id=reservation.source_id,
        exactly_one_reservation_bound=True,
        reserved_object_identities_bound=True,
        constructor_identities_declared=True,
        callable_constructor_allowed_later=True,
        gate_constructor_allowed_later=True,
        selected_slot_still_fresh=True,
        other_slots_unselected=reservation.other_slots_unselected,
    )


def construct_public_av_return_replication_repeatability_single_slot_objects(
    construction: PublicAVReturnReplicationRepeatabilitySingleSlotObjectConstruction,
) -> None:
    del construction
    raise PublicAVReturnReplicationRepeatabilitySingleSlotObjectConstructionError(
        "object construction is not released by the locked single-slot construction contract"
    )


def public_av_return_replication_repeatability_single_slot_object_construction_to_jsonable(
    construction: PublicAVReturnReplicationRepeatabilitySingleSlotObjectConstruction,
) -> dict[str, Any]:
    return asdict(construction)
