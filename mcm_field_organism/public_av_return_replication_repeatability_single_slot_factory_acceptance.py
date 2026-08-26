"""Locked acceptance of one single-slot factory identity binding."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_factory_binding import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryBinding,
)


SINGLE_SLOT_FACTORY_ACCEPTANCE_ID = (
    "public.av.nasa-earthrise.return-replication."
    "repeatability-single-slot-factory-acceptance.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryAcceptanceError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryAcceptance:
    acceptance_id: str
    selected_repeat_index: int
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
    factory_binding_accepted: bool
    constructor_identities_accepted: bool
    factory_identities_accepted: bool
    object_identities_accepted: bool
    callable_gate_identities_accepted: bool
    selected_slot_still_fresh: bool
    factory_acceptance_complete: bool
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryAcceptanceError(
                "selected repeat index must be one of 1, 2, 3"
            )
        if not self.acceptance_id.endswith(f".repeat-{self.selected_repeat_index}.v1"):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryAcceptanceError(
                "factory acceptance identity does not match selected repeat index"
            )
        if self.future_callable_factory_id == self.future_gate_factory_id:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryAcceptanceError(
                "accepted factory identities must remain unique"
            )
        expected = tuple(index for index in (1, 2, 3) if index != self.selected_repeat_index)
        if tuple(self.other_slots_unselected) != expected:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryAcceptanceError(
                "other slots must remain unselected"
            )
        required = (
            self.factory_binding_accepted,
            self.constructor_identities_accepted,
            self.factory_identities_accepted,
            self.object_identities_accepted,
            self.callable_gate_identities_accepted,
            self.selected_slot_still_fresh,
            self.factory_acceptance_complete,
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryAcceptanceError(
                "factory acceptance cannot store references, call factories, create objects, decode, feed receptors, start runs, or release claims"
            )
        object.__setattr__(self, "other_slots_unselected", tuple(self.other_slots_unselected))


def accept_public_av_return_replication_repeatability_single_slot_factory_binding(
    binding: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryBinding,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotFactoryAcceptance:
    if not isinstance(binding, PublicAVReturnReplicationRepeatabilitySingleSlotFactoryBinding):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryAcceptanceError(
            "single-slot factory binding has the wrong type"
        )
    required = (
        binding.construction_acceptance_bound,
        binding.constructor_identities_bound,
        binding.callable_factory_identity_bound,
        binding.gate_factory_identity_bound,
        binding.factory_identities_unique,
        binding.selected_slot_still_fresh,
    )
    forbidden = (
        binding.callable_factory_reference_stored,
        binding.gate_factory_reference_stored,
        binding.callable_reference_stored,
        binding.factory_function_called,
        binding.callable_factory_called,
        binding.gate_factory_called,
        binding.callable_object_created,
        binding.gate_object_created,
        binding.constructor_invoked,
        binding.binding_performed,
        binding.scheduler_available,
        binding.media_decode_allowed,
        binding.receptor_feed_allowed,
        binding.start_release_granted,
        binding.repeatability_run_allowed,
        binding.repeat_run_started,
    )
    if not all(required) or any(forbidden):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryAcceptanceError(
            "one complete fresh reference-free factory binding is required"
        )

    index = binding.selected_repeat_index
    return PublicAVReturnReplicationRepeatabilitySingleSlotFactoryAcceptance(
        acceptance_id=f"{SINGLE_SLOT_FACTORY_ACCEPTANCE_ID}.repeat-{index}.v1",
        selected_repeat_index=index,
        factory_binding_id=binding.binding_id,
        construction_acceptance_id=binding.construction_acceptance_id,
        construction_id=binding.construction_id,
        object_reservation_id=binding.object_reservation_id,
        candidate_id=binding.candidate_id,
        logical_callable_id=binding.logical_callable_id,
        logical_gate_id=binding.logical_gate_id,
        reserved_executor_id=binding.reserved_executor_id,
        future_callable_object_id=binding.future_callable_object_id,
        future_gate_object_id=binding.future_gate_object_id,
        callable_constructor_id=binding.callable_constructor_id,
        gate_constructor_id=binding.gate_constructor_id,
        future_callable_factory_id=binding.future_callable_factory_id,
        future_gate_factory_id=binding.future_gate_factory_id,
        source_id=binding.source_id,
        factory_binding_accepted=True,
        constructor_identities_accepted=True,
        factory_identities_accepted=True,
        object_identities_accepted=True,
        callable_gate_identities_accepted=True,
        selected_slot_still_fresh=True,
        factory_acceptance_complete=True,
        other_slots_unselected=binding.other_slots_unselected,
    )


def call_public_av_return_replication_repeatability_single_slot_accepted_factories(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryAcceptance,
) -> None:
    del acceptance
    raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryAcceptanceError(
        "factory calls are not released by the locked factory acceptance"
    )


def public_av_return_replication_repeatability_single_slot_factory_acceptance_to_jsonable(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryAcceptance,
) -> dict[str, Any]:
    return asdict(acceptance)
