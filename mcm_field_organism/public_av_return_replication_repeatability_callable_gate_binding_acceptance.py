"""Locked acceptance for future repeatability callable-to-gate bindings."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_callable_preparation import (
    PublicAVReturnReplicationRepeatabilityCallablePreparationContract,
)


CALLABLE_GATE_BINDING_ACCEPTANCE_ID = (
    "public.av.nasa-earthrise.return-replication."
    "repeatability-callable-gate-binding-acceptance.v1"
)


class PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptanceError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatSlotCallableGateBindingAcceptance:
    repeat_index: int
    binding_acceptance_id: str
    callable_preparation_id: str
    gate_instantiation_id: str
    future_callable_id: str
    reserved_executor_id: str
    reserved_gate_id: str
    slot_binding_id: str
    executor_binding_id: str
    source_id: str
    callable_identity_matches: bool
    executor_identity_matches: bool
    gate_identity_matches: bool
    callable_gate_pairing_unique: bool
    fresh_callable_required: bool
    fresh_gate_required: bool
    callable_object_created: bool = False
    gate_instance_created: bool = False
    callable_bound_to_gate: bool = False
    executor_bound_to_gate: bool = False
    start_release_granted: bool = False
    repeat_run_started: bool = False
    reusable: bool = False

    def __post_init__(self) -> None:
        if self.repeat_index not in (1, 2, 3):
            raise PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptanceError(
                "repeat_index must be one of 1, 2, 3"
            )
        suffix = f".repeat-{self.repeat_index}.v1"
        if not self.binding_acceptance_id.endswith(suffix):
            raise PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptanceError(
                "binding acceptance identity does not match repeat_index"
            )
        required = (
            self.callable_identity_matches,
            self.executor_identity_matches,
            self.gate_identity_matches,
            self.callable_gate_pairing_unique,
            self.fresh_callable_required,
            self.fresh_gate_required,
        )
        forbidden = (
            self.callable_object_created,
            self.gate_instance_created,
            self.callable_bound_to_gate,
            self.executor_bound_to_gate,
            self.start_release_granted,
            self.repeat_run_started,
            self.reusable,
        )
        if not all(required):
            raise PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptanceError(
                "slot binding acceptance requires complete callable, executor, and gate identities"
            )
        if any(forbidden):
            raise PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptanceError(
                "slot binding acceptance must remain unbound and start-locked"
            )


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptance:
    acceptance_id: str
    callable_preparation_contract_id: str
    gate_instantiation_contract_id: str
    start_acceptance_id: str
    repeatability_preflight_id: str
    repeatability_runner_id: str
    source_id: str
    slot_binding_acceptances: tuple[
        PublicAVReturnReplicationRepeatSlotCallableGateBindingAcceptance, ...
    ]
    all_three_callable_preparations_bound: bool
    all_callable_gate_pairings_unique: bool
    all_callable_ids_unique: bool
    all_gate_ids_unique: bool
    all_executor_ids_unique: bool
    binding_acceptance_complete: bool
    callable_objects_created: bool = False
    gate_instances_created: bool = False
    callable_gate_binding_performed: bool = False
    executor_binding_performed: bool = False
    start_release_granted: bool = False
    repeatability_run_allowed: bool = False
    automatic_repeat_loop_available: bool = False
    stability_threshold_defined: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        if self.acceptance_id != CALLABLE_GATE_BINDING_ACCEPTANCE_ID:
            raise PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptanceError(
                "unexpected callable-gate binding acceptance identity"
            )
        if tuple(item.repeat_index for item in self.slot_binding_acceptances) != (1, 2, 3):
            raise PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptanceError(
                "binding acceptance must contain exactly the ordered slots 1, 2, 3"
            )
        required = (
            self.all_three_callable_preparations_bound,
            self.all_callable_gate_pairings_unique,
            self.all_callable_ids_unique,
            self.all_gate_ids_unique,
            self.all_executor_ids_unique,
            self.binding_acceptance_complete,
        )
        forbidden = (
            self.callable_objects_created,
            self.gate_instances_created,
            self.callable_gate_binding_performed,
            self.executor_binding_performed,
            self.start_release_granted,
            self.repeatability_run_allowed,
            self.automatic_repeat_loop_available,
            self.stability_threshold_defined,
            self.memory_claim_allowed,
            self.meaning_claim_allowed,
            self.organization_claim_allowed,
            self.ai_claim_allowed,
        )
        if not all(required):
            raise PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptanceError(
                "callable-gate binding acceptance is incomplete"
            )
        if any(forbidden):
            raise PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptanceError(
                "callable-gate binding acceptance cannot create objects, bind gates, start runs, or release claims"
            )


def accept_public_av_return_replication_repeatability_callable_gate_bindings(
    callable_preparation: PublicAVReturnReplicationRepeatabilityCallablePreparationContract,
) -> PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptance:
    if not isinstance(
        callable_preparation,
        PublicAVReturnReplicationRepeatabilityCallablePreparationContract,
    ):
        raise PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptanceError(
            "callable preparation has the wrong contract type"
        )
    if not callable_preparation.callable_preparation_contract_complete:
        raise PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptanceError(
            "complete callable preparation is required"
        )
    if (
        callable_preparation.callable_objects_created
        or callable_preparation.callable_factories_created
        or callable_preparation.gate_instances_created
        or callable_preparation.callable_gate_binding_performed
        or callable_preparation.start_release_granted
        or callable_preparation.repeatability_run_allowed
    ):
        raise PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptanceError(
            "callable preparation must remain object-free and run-locked"
        )

    slots = []
    seen_pairings: set[tuple[str, str]] = set()
    for prepared in callable_preparation.slot_callable_preparations:
        if (
            prepared.callable_object_created
            or prepared.callable_factory_created
            or prepared.gate_instance_created
            or prepared.callable_bound_to_gate
            or prepared.start_release_granted
            or prepared.repeat_run_started
        ):
            raise PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptanceError(
                f"slot {prepared.repeat_index} is no longer fresh"
            )
        pairing = (prepared.future_callable_id, prepared.reserved_gate_id)
        if pairing in seen_pairings:
            raise PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptanceError(
                f"slot {prepared.repeat_index} repeats a callable-gate pairing"
            )
        seen_pairings.add(pairing)
        suffix = f"repeat-{prepared.repeat_index}.v1"
        slots.append(
            PublicAVReturnReplicationRepeatSlotCallableGateBindingAcceptance(
                repeat_index=prepared.repeat_index,
                binding_acceptance_id=(
                    f"{CALLABLE_GATE_BINDING_ACCEPTANCE_ID}.{suffix}"
                ),
                callable_preparation_id=prepared.callable_preparation_id,
                gate_instantiation_id=prepared.gate_instantiation_id,
                future_callable_id=prepared.future_callable_id,
                reserved_executor_id=prepared.reserved_executor_id,
                reserved_gate_id=prepared.reserved_gate_id,
                slot_binding_id=prepared.slot_binding_id,
                executor_binding_id=prepared.executor_binding_id,
                source_id=prepared.source_id,
                callable_identity_matches=True,
                executor_identity_matches=True,
                gate_identity_matches=True,
                callable_gate_pairing_unique=True,
                fresh_callable_required=True,
                fresh_gate_required=True,
            )
        )

    callable_ids = tuple(item.future_callable_id for item in slots)
    gate_ids = tuple(item.reserved_gate_id for item in slots)
    executor_ids = tuple(item.reserved_executor_id for item in slots)
    pairings = tuple((item.future_callable_id, item.reserved_gate_id) for item in slots)
    return PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptance(
        acceptance_id=CALLABLE_GATE_BINDING_ACCEPTANCE_ID,
        callable_preparation_contract_id=callable_preparation.contract_id,
        gate_instantiation_contract_id=callable_preparation.gate_instantiation_contract_id,
        start_acceptance_id=callable_preparation.start_acceptance_id,
        repeatability_preflight_id=callable_preparation.repeatability_preflight_id,
        repeatability_runner_id=callable_preparation.repeatability_runner_id,
        source_id=callable_preparation.source_id,
        slot_binding_acceptances=tuple(slots),
        all_three_callable_preparations_bound=True,
        all_callable_gate_pairings_unique=len(set(pairings)) == 3,
        all_callable_ids_unique=len(set(callable_ids)) == 3,
        all_gate_ids_unique=len(set(gate_ids)) == 3,
        all_executor_ids_unique=len(set(executor_ids)) == 3,
        binding_acceptance_complete=True,
    )


def bind_public_av_return_replication_repeatability_callables_to_gates(
    acceptance: PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptance,
) -> None:
    del acceptance
    raise PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptanceError(
        "callable-gate binding is not released by the locked acceptance contract"
    )


def public_av_return_replication_repeatability_callable_gate_binding_acceptance_to_jsonable(
    acceptance: PublicAVReturnReplicationRepeatabilityCallableGateBindingAcceptance,
) -> dict[str, Any]:
    return asdict(acceptance)
