"""Locked factory identity binding for one repeatability slot."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_construction_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotConstructionAcceptance,
)


SINGLE_SLOT_FACTORY_BINDING_ID = (
    "public.av.nasa-earthrise.return-replication."
    "repeatability-single-slot-factory-binding.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryBindingError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryBinding:
    binding_id: str
    selected_repeat_index: int
    construction_acceptance_id: str
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
    future_callable_factory_id: str
    future_gate_factory_id: str
    source_id: str
    construction_acceptance_bound: bool
    constructor_identities_bound: bool
    callable_factory_identity_bound: bool
    gate_factory_identity_bound: bool
    factory_identities_unique: bool
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryBindingError(
                "selected repeat index must be one of 1, 2, 3"
            )
        suffix = f".repeat-{self.selected_repeat_index}.v1"
        indexed_ids = (
            self.binding_id,
            self.construction_acceptance_id,
            self.callable_constructor_id,
            self.gate_constructor_id,
            self.future_callable_factory_id,
            self.future_gate_factory_id,
        )
        if not all(identifier.endswith(suffix) for identifier in indexed_ids):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryBindingError(
                "factory binding identities must match selected repeat index"
            )
        if self.future_callable_factory_id == self.future_gate_factory_id:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryBindingError(
                "callable and gate factory identities must be unique"
            )
        expected_unselected = tuple(
            index for index in (1, 2, 3) if index != self.selected_repeat_index
        )
        if tuple(self.other_slots_unselected) != expected_unselected:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryBindingError(
                "other slots must remain unselected"
            )
        required = (
            self.construction_acceptance_bound,
            self.constructor_identities_bound,
            self.callable_factory_identity_bound,
            self.gate_factory_identity_bound,
            self.factory_identities_unique,
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryBindingError(
                "factory binding cannot store callables, call factories, create objects, bind, decode, feed receptors, start runs, or release claims"
            )
        object.__setattr__(self, "other_slots_unselected", tuple(self.other_slots_unselected))


def bind_public_av_return_replication_repeatability_single_slot_factories(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotConstructionAcceptance,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotFactoryBinding:
    if not isinstance(
        acceptance,
        PublicAVReturnReplicationRepeatabilitySingleSlotConstructionAcceptance,
    ):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryBindingError(
            "single-slot construction acceptance has the wrong type"
        )
    if not (
        acceptance.reservation_identity_accepted
        and acceptance.object_identities_accepted
        and acceptance.constructor_identities_accepted
        and acceptance.callable_identity_accepted
        and acceptance.gate_identity_accepted
        and acceptance.selected_slot_still_fresh
        and acceptance.construction_acceptance_complete
    ):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryBindingError(
            "one complete fresh construction acceptance is required"
        )
    if any(
        (
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
    ):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryBindingError(
            "construction acceptance must remain factory-free, object-free, and run-locked"
        )

    index = acceptance.selected_repeat_index
    suffix = f"repeat-{index}.v1"
    return PublicAVReturnReplicationRepeatabilitySingleSlotFactoryBinding(
        binding_id=f"{SINGLE_SLOT_FACTORY_BINDING_ID}.{suffix}",
        selected_repeat_index=index,
        construction_acceptance_id=acceptance.acceptance_id,
        construction_id=acceptance.construction_id,
        object_reservation_id=acceptance.object_reservation_id,
        instantiation_order_id=acceptance.instantiation_order_id,
        candidate_id=acceptance.candidate_id,
        logical_callable_id=acceptance.logical_callable_id,
        logical_gate_id=acceptance.logical_gate_id,
        reserved_executor_id=acceptance.reserved_executor_id,
        future_callable_object_id=acceptance.future_callable_object_id,
        future_gate_object_id=acceptance.future_gate_object_id,
        callable_constructor_id=acceptance.callable_constructor_id,
        gate_constructor_id=acceptance.gate_constructor_id,
        future_callable_factory_id=(
            "public.av.nasa-earthrise.return-replication."
            f"single-slot-callable-factory.{suffix}"
        ),
        future_gate_factory_id=(
            "public.av.nasa-earthrise.return-replication."
            f"single-slot-gate-factory.{suffix}"
        ),
        source_id=acceptance.source_id,
        construction_acceptance_bound=True,
        constructor_identities_bound=True,
        callable_factory_identity_bound=True,
        gate_factory_identity_bound=True,
        factory_identities_unique=True,
        selected_slot_still_fresh=True,
        other_slots_unselected=acceptance.other_slots_unselected,
    )


def call_public_av_return_replication_repeatability_single_slot_factories(
    binding: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryBinding,
) -> None:
    del binding
    raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryBindingError(
        "factory calls are not released by the locked single-slot factory binding"
    )


def public_av_return_replication_repeatability_single_slot_factory_binding_to_jsonable(
    binding: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryBinding,
) -> dict[str, Any]:
    return asdict(binding)
