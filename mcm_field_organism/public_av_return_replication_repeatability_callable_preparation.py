"""Locked identity preparation for future repeatability executor callables."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_gate_instantiation import (
    PublicAVReturnReplicationRepeatabilityGateInstantiationContract,
)


CALLABLE_PREPARATION_ID = (
    "public.av.nasa-earthrise.return-replication.repeatability-callable-preparation.v1"
)


class PublicAVReturnReplicationRepeatabilityCallablePreparationError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatSlotCallablePreparation:
    repeat_index: int
    callable_preparation_id: str
    gate_instantiation_id: str
    slot_gate_instantiation_id: str
    reserved_gate_id: str
    reserved_executor_id: str
    future_callable_id: str
    slot_binding_id: str
    executor_binding_id: str
    source_id: str
    gate_reservation_bound: bool
    executor_identity_bound: bool
    callable_identity_reserved: bool
    fresh_callable_required: bool
    callable_object_created: bool = False
    callable_factory_created: bool = False
    gate_instance_created: bool = False
    callable_bound_to_gate: bool = False
    start_release_granted: bool = False
    repeat_run_started: bool = False
    reusable: bool = False

    def __post_init__(self) -> None:
        if self.repeat_index not in (1, 2, 3):
            raise PublicAVReturnReplicationRepeatabilityCallablePreparationError(
                "repeat_index must be one of 1, 2, 3"
            )
        suffix = f".repeat-{self.repeat_index}.v1"
        if not self.callable_preparation_id.endswith(suffix):
            raise PublicAVReturnReplicationRepeatabilityCallablePreparationError(
                "callable preparation identity does not match repeat_index"
            )
        if not self.future_callable_id.endswith(suffix):
            raise PublicAVReturnReplicationRepeatabilityCallablePreparationError(
                "future callable identity does not match repeat_index"
            )
        required = (
            self.gate_reservation_bound,
            self.executor_identity_bound,
            self.callable_identity_reserved,
            self.fresh_callable_required,
        )
        forbidden = (
            self.callable_object_created,
            self.callable_factory_created,
            self.gate_instance_created,
            self.callable_bound_to_gate,
            self.start_release_granted,
            self.repeat_run_started,
            self.reusable,
        )
        if not all(required) or any(forbidden):
            raise PublicAVReturnReplicationRepeatabilityCallablePreparationError(
                "slot callable preparation must remain identity-only and start-locked"
            )


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilityCallablePreparationContract:
    contract_id: str
    gate_instantiation_contract_id: str
    start_acceptance_id: str
    repeatability_preflight_id: str
    repeatability_runner_id: str
    source_id: str
    slot_callable_preparations: tuple[
        PublicAVReturnReplicationRepeatSlotCallablePreparation, ...
    ]
    all_three_gate_reservations_bound: bool
    all_future_callable_ids_unique: bool
    all_reserved_gate_ids_unique: bool
    all_reserved_executor_ids_unique: bool
    fresh_callable_per_slot_required: bool
    callable_preparation_contract_complete: bool
    callable_objects_created: bool = False
    callable_factories_created: bool = False
    gate_instances_created: bool = False
    callable_gate_binding_performed: bool = False
    start_release_granted: bool = False
    repeatability_run_allowed: bool = False
    automatic_repeat_loop_available: bool = False
    stability_threshold_defined: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        if self.contract_id != CALLABLE_PREPARATION_ID:
            raise PublicAVReturnReplicationRepeatabilityCallablePreparationError(
                "unexpected callable preparation contract identity"
            )
        if tuple(item.repeat_index for item in self.slot_callable_preparations) != (
            1,
            2,
            3,
        ):
            raise PublicAVReturnReplicationRepeatabilityCallablePreparationError(
                "callable preparation requires exactly the ordered slots 1, 2, 3"
            )
        required = (
            self.all_three_gate_reservations_bound,
            self.all_future_callable_ids_unique,
            self.all_reserved_gate_ids_unique,
            self.all_reserved_executor_ids_unique,
            self.fresh_callable_per_slot_required,
            self.callable_preparation_contract_complete,
        )
        forbidden = (
            self.callable_objects_created,
            self.callable_factories_created,
            self.gate_instances_created,
            self.callable_gate_binding_performed,
            self.start_release_granted,
            self.repeatability_run_allowed,
            self.automatic_repeat_loop_available,
            self.stability_threshold_defined,
            self.memory_claim_allowed,
            self.meaning_claim_allowed,
            self.organization_claim_allowed,
            self.ai_claim_allowed,
        )
        if not all(required) or any(forbidden):
            raise PublicAVReturnReplicationRepeatabilityCallablePreparationError(
                "callable preparation cannot create callables, bind gates, start runs, or release claims"
            )


def prepare_public_av_return_replication_repeatability_executor_callables(
    gate_contract: PublicAVReturnReplicationRepeatabilityGateInstantiationContract,
) -> PublicAVReturnReplicationRepeatabilityCallablePreparationContract:
    if not isinstance(
        gate_contract,
        PublicAVReturnReplicationRepeatabilityGateInstantiationContract,
    ):
        raise PublicAVReturnReplicationRepeatabilityCallablePreparationError(
            "gate instantiation contract has the wrong type"
        )
    if not gate_contract.gate_instantiation_contract_complete:
        raise PublicAVReturnReplicationRepeatabilityCallablePreparationError(
            "complete gate reservation contract is required"
        )
    if (
        gate_contract.gate_instances_created
        or gate_contract.executor_callables_created
        or gate_contract.executor_binding_performed
        or gate_contract.start_release_granted
        or gate_contract.repeatability_run_allowed
    ):
        raise PublicAVReturnReplicationRepeatabilityCallablePreparationError(
            "gate reservations must remain uninstantiated and run-locked"
        )

    slots = []
    for reserved in gate_contract.slot_gate_instantiations:
        if (
            reserved.gate_instance_created
            or reserved.executor_callable_created
            or reserved.executor_bound_to_gate
            or reserved.start_release_granted
            or reserved.repeat_run_started
        ):
            raise PublicAVReturnReplicationRepeatabilityCallablePreparationError(
                f"slot {reserved.repeat_index} is no longer fresh"
            )
        suffix = f"repeat-{reserved.repeat_index}.v1"
        slots.append(
            PublicAVReturnReplicationRepeatSlotCallablePreparation(
                repeat_index=reserved.repeat_index,
                callable_preparation_id=f"{CALLABLE_PREPARATION_ID}.{suffix}",
                gate_instantiation_id=gate_contract.contract_id,
                slot_gate_instantiation_id=reserved.gate_instantiation_id,
                reserved_gate_id=reserved.reserved_one_shot_gate_id,
                reserved_executor_id=reserved.reserved_executor_id,
                future_callable_id=(
                    "public.av.nasa-earthrise.return-replication."
                    f"executor-callable.{suffix}"
                ),
                slot_binding_id=reserved.slot_binding_id,
                executor_binding_id=reserved.executor_binding_id,
                source_id=reserved.source_id,
                gate_reservation_bound=True,
                executor_identity_bound=True,
                callable_identity_reserved=True,
                fresh_callable_required=True,
            )
        )

    callable_ids = tuple(item.future_callable_id for item in slots)
    gate_ids = tuple(item.reserved_gate_id for item in slots)
    executor_ids = tuple(item.reserved_executor_id for item in slots)
    return PublicAVReturnReplicationRepeatabilityCallablePreparationContract(
        contract_id=CALLABLE_PREPARATION_ID,
        gate_instantiation_contract_id=gate_contract.contract_id,
        start_acceptance_id=gate_contract.start_acceptance_id,
        repeatability_preflight_id=gate_contract.repeatability_preflight_id,
        repeatability_runner_id=gate_contract.repeatability_runner_id,
        source_id=gate_contract.source_id,
        slot_callable_preparations=tuple(slots),
        all_three_gate_reservations_bound=True,
        all_future_callable_ids_unique=len(set(callable_ids)) == 3,
        all_reserved_gate_ids_unique=len(set(gate_ids)) == 3,
        all_reserved_executor_ids_unique=len(set(executor_ids)) == 3,
        fresh_callable_per_slot_required=True,
        callable_preparation_contract_complete=True,
    )


def create_public_av_return_replication_repeatability_executor_callables(
    contract: PublicAVReturnReplicationRepeatabilityCallablePreparationContract,
) -> None:
    del contract
    raise PublicAVReturnReplicationRepeatabilityCallablePreparationError(
        "callable creation is not released by the locked preparation contract"
    )


def public_av_return_replication_repeatability_callable_preparation_to_jsonable(
    contract: PublicAVReturnReplicationRepeatabilityCallablePreparationContract,
) -> dict[str, Any]:
    return asdict(contract)
