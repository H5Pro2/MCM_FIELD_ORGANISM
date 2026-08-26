"""Locked acceptance of one single-slot construction identity contract."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_object_construction import (
    PublicAVReturnReplicationRepeatabilitySingleSlotObjectConstruction,
)


SINGLE_SLOT_CONSTRUCTION_ACCEPTANCE_ID = (
    "public.av.nasa-earthrise.return-replication."
    "repeatability-single-slot-construction-acceptance.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotConstructionAcceptanceError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotConstructionAcceptance:
    acceptance_id: str
    selected_repeat_index: int
    construction_id: str
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
    reservation_identity_accepted: bool
    object_identities_accepted: bool
    constructor_identities_accepted: bool
    callable_identity_accepted: bool
    gate_identity_accepted: bool
    selected_slot_still_fresh: bool
    construction_acceptance_complete: bool
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotConstructionAcceptanceError(
                "selected repeat index must be one of 1, 2, 3"
            )
        if not self.acceptance_id.endswith(f".repeat-{self.selected_repeat_index}.v1"):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotConstructionAcceptanceError(
                "acceptance identity does not match selected repeat index"
            )
        expected_unselected = tuple(
            index for index in (1, 2, 3) if index != self.selected_repeat_index
        )
        if tuple(self.other_slots_unselected) != expected_unselected:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotConstructionAcceptanceError(
                "other slots must remain unselected"
            )
        required = (
            self.reservation_identity_accepted,
            self.object_identities_accepted,
            self.constructor_identities_accepted,
            self.callable_identity_accepted,
            self.gate_identity_accepted,
            self.selected_slot_still_fresh,
            self.construction_acceptance_complete,
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotConstructionAcceptanceError(
                "construction acceptance cannot call factories, create objects, bind, decode, feed receptors, start runs, or release claims"
            )
        object.__setattr__(self, "other_slots_unselected", tuple(self.other_slots_unselected))


def accept_public_av_return_replication_repeatability_single_slot_construction(
    construction: PublicAVReturnReplicationRepeatabilitySingleSlotObjectConstruction,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotConstructionAcceptance:
    if not isinstance(
        construction,
        PublicAVReturnReplicationRepeatabilitySingleSlotObjectConstruction,
    ):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotConstructionAcceptanceError(
            "single-slot construction has the wrong type"
        )
    if not (
        construction.exactly_one_reservation_bound
        and construction.reserved_object_identities_bound
        and construction.constructor_identities_declared
        and construction.selected_slot_still_fresh
    ):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotConstructionAcceptanceError(
            "one complete fresh construction contract is required"
        )
    if any(
        (
            construction.callable_factory_called,
            construction.gate_factory_called,
            construction.callable_object_created,
            construction.gate_object_created,
            construction.constructor_invoked,
            construction.binding_performed,
            construction.scheduler_available,
            construction.media_decode_allowed,
            construction.receptor_feed_allowed,
            construction.start_release_granted,
            construction.repeatability_run_allowed,
            construction.repeat_run_started,
        )
    ):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotConstructionAcceptanceError(
            "construction must remain factory-free, object-free, and run-locked"
        )

    index = construction.selected_repeat_index
    return PublicAVReturnReplicationRepeatabilitySingleSlotConstructionAcceptance(
        acceptance_id=f"{SINGLE_SLOT_CONSTRUCTION_ACCEPTANCE_ID}.repeat-{index}.v1",
        selected_repeat_index=index,
        construction_id=construction.construction_id,
        object_reservation_id=construction.object_reservation_id,
        instantiation_order_id=construction.instantiation_order_id,
        candidate_id=construction.candidate_id,
        logical_callable_id=construction.logical_callable_id,
        logical_gate_id=construction.logical_gate_id,
        reserved_executor_id=construction.reserved_executor_id,
        future_callable_object_id=construction.future_callable_object_id,
        future_gate_object_id=construction.future_gate_object_id,
        callable_constructor_id=construction.callable_constructor_id,
        gate_constructor_id=construction.gate_constructor_id,
        source_id=construction.source_id,
        reservation_identity_accepted=True,
        object_identities_accepted=True,
        constructor_identities_accepted=True,
        callable_identity_accepted=True,
        gate_identity_accepted=True,
        selected_slot_still_fresh=True,
        construction_acceptance_complete=True,
        other_slots_unselected=construction.other_slots_unselected,
    )


def construct_from_public_av_return_replication_repeatability_single_slot_acceptance(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotConstructionAcceptance,
) -> None:
    del acceptance
    raise PublicAVReturnReplicationRepeatabilitySingleSlotConstructionAcceptanceError(
        "construction is not released by the locked single-slot acceptance"
    )


def public_av_return_replication_repeatability_single_slot_construction_acceptance_to_jsonable(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotConstructionAcceptance,
) -> dict[str, Any]:
    return asdict(acceptance)
