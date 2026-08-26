"""Locked single-slot instantiation order derived from final repeatability preflight."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_final_execution_preflight import (
    PublicAVReturnReplicationRepeatabilityFinalExecutionPreflight,
)


SINGLE_SLOT_INSTANTIATION_ORDER_ID = (
    "public.av.nasa-earthrise.return-replication."
    "repeatability-single-slot-instantiation-order.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrderError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrder:
    order_id: str
    selected_repeat_index: int
    selected_slot_preflight_id: str
    candidate_id: str
    final_execution_preflight_id: str
    final_coordination_contract_id: str
    binding_acceptance_id: str
    repeatability_preflight_id: str
    repeatability_runner_id: str
    future_callable_id: str
    reserved_executor_id: str
    reserved_gate_id: str
    source_id: str
    selected_slot_is_fresh: bool
    selected_slot_identity_bound: bool
    candidate_identity_bound: bool
    callable_identity_bound: bool
    executor_identity_bound: bool
    gate_identity_bound: bool
    source_identity_bound: bool
    exactly_one_slot_selected: bool
    other_slots_unselected: tuple[int, ...]
    callable_object_created: bool = False
    gate_instance_created: bool = False
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
            raise PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrderError(
                "selected repeat index must be one of 1, 2, 3"
            )
        if self.order_id != f"{SINGLE_SLOT_INSTANTIATION_ORDER_ID}.repeat-{self.selected_repeat_index}.v1":
            raise PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrderError(
                "single-slot order identity does not match selected repeat index"
            )
        if tuple(self.other_slots_unselected) != tuple(
            index for index in (1, 2, 3) if index != self.selected_repeat_index
        ):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrderError(
                "unselected slots must be the remaining preregistered indices"
            )
        required = (
            self.selected_slot_is_fresh,
            self.selected_slot_identity_bound,
            self.candidate_identity_bound,
            self.callable_identity_bound,
            self.executor_identity_bound,
            self.gate_identity_bound,
            self.source_identity_bound,
            self.exactly_one_slot_selected,
        )
        forbidden = (
            self.callable_object_created,
            self.gate_instance_created,
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
        if not all(required):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrderError(
                "single-slot instantiation order requires one complete fresh identity chain"
            )
        if any(forbidden):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrderError(
                "single-slot instantiation order cannot create objects, decode media, feed receptors, start runs, or release claims"
            )
        object.__setattr__(self, "other_slots_unselected", tuple(self.other_slots_unselected))


def derive_public_av_return_replication_repeatability_single_slot_instantiation_order(
    final_preflight: PublicAVReturnReplicationRepeatabilityFinalExecutionPreflight,
    *,
    repeat_index: int,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrder:
    if not isinstance(final_preflight, PublicAVReturnReplicationRepeatabilityFinalExecutionPreflight):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrderError(
            "final execution preflight has the wrong contract type"
        )
    if repeat_index not in (1, 2, 3):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrderError(
            "repeat_index must be one of 1, 2, 3"
        )
    if not final_preflight.final_execution_preflight_complete:
        raise PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrderError(
            "complete final execution preflight is required"
        )
    if (
        final_preflight.callable_objects_created
        or final_preflight.gate_instances_created
        or final_preflight.bindings_performed
        or final_preflight.scheduler_available
        or final_preflight.start_release_granted
        or final_preflight.repeatability_run_allowed
        or final_preflight.media_decode_allowed
        or final_preflight.receptor_feed_allowed
    ):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrderError(
            "final preflight must remain object-free, receptor-locked, and run-locked"
        )

    matches = tuple(slot for slot in final_preflight.slot_preflights if slot.repeat_index == repeat_index)
    if len(matches) != 1:
        raise PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrderError(
            "selected repeat index must resolve to exactly one slot"
        )
    slot = matches[0]
    if (
        slot.callable_object_created
        or slot.gate_instance_created
        or slot.binding_performed
        or slot.scheduled
        or slot.start_release_granted
        or slot.repeat_run_started
    ):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrderError(
            "selected slot is no longer fresh"
        )

    return PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrder(
        order_id=f"{SINGLE_SLOT_INSTANTIATION_ORDER_ID}.repeat-{repeat_index}.v1",
        selected_repeat_index=repeat_index,
        selected_slot_preflight_id=slot.slot_preflight_id,
        candidate_id=slot.candidate_id,
        final_execution_preflight_id=final_preflight.preflight_id,
        final_coordination_contract_id=final_preflight.final_coordination_contract_id,
        binding_acceptance_id=final_preflight.binding_acceptance_id,
        repeatability_preflight_id=final_preflight.repeatability_preflight_id,
        repeatability_runner_id=final_preflight.repeatability_runner_id,
        future_callable_id=slot.future_callable_id,
        reserved_executor_id=slot.reserved_executor_id,
        reserved_gate_id=slot.reserved_gate_id,
        source_id=slot.source_id,
        selected_slot_is_fresh=True,
        selected_slot_identity_bound=True,
        candidate_identity_bound=True,
        callable_identity_bound=True,
        executor_identity_bound=True,
        gate_identity_bound=True,
        source_identity_bound=slot.source_id == final_preflight.source_id,
        exactly_one_slot_selected=True,
        other_slots_unselected=tuple(index for index in (1, 2, 3) if index != repeat_index),
    )


def instantiate_public_av_return_replication_repeatability_single_slot(
    order: PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrder,
) -> None:
    del order
    raise PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrderError(
        "single-slot instantiation is not released by the locked instantiation order"
    )


def public_av_return_replication_repeatability_single_slot_instantiation_order_to_jsonable(
    order: PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrder,
) -> dict[str, Any]:
    return asdict(order)
