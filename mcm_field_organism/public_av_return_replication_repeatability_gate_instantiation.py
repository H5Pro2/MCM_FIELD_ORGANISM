"""Locked reservation contract for repeatability one-shot gate instances."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_start_acceptance import (
    PublicAVReturnReplicationRepeatabilityStartAcceptance,
)


GATE_INSTANTIATION_ID = (
    "public.av.nasa-earthrise.return-replication.repeatability-gate-instantiation.v1"
)


class PublicAVReturnReplicationRepeatabilityGateInstantiationError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatSlotGateInstantiation:
    repeat_index: int
    gate_instantiation_id: str
    start_acceptance_id: str
    slot_acceptance_id: str
    reserved_one_shot_gate_id: str
    reserved_executor_id: str
    slot_binding_id: str
    executor_binding_id: str
    source_id: str
    start_acceptance_bound: bool
    one_shot_gate_identity_reserved: bool
    executor_identity_carried: bool
    fresh_gate_required: bool
    gate_instance_created: bool = False
    executor_callable_created: bool = False
    executor_bound_to_gate: bool = False
    start_release_granted: bool = False
    repeat_run_started: bool = False
    reusable: bool = False

    def __post_init__(self) -> None:
        if self.repeat_index not in (1, 2, 3):
            raise PublicAVReturnReplicationRepeatabilityGateInstantiationError(
                "repeat_index must be one of 1, 2, 3"
            )
        if not self.gate_instantiation_id.endswith(f".repeat-{self.repeat_index}.v1"):
            raise PublicAVReturnReplicationRepeatabilityGateInstantiationError(
                "gate instantiation identity does not match repeat_index"
            )
        required = (
            self.start_acceptance_bound,
            self.one_shot_gate_identity_reserved,
            self.executor_identity_carried,
            self.fresh_gate_required,
        )
        forbidden = (
            self.gate_instance_created,
            self.executor_callable_created,
            self.executor_bound_to_gate,
            self.start_release_granted,
            self.repeat_run_started,
            self.reusable,
        )
        if not all(required):
            raise PublicAVReturnReplicationRepeatabilityGateInstantiationError(
                "slot gate instantiation requires a complete reserved identity chain"
            )
        if any(forbidden):
            raise PublicAVReturnReplicationRepeatabilityGateInstantiationError(
                "slot gate instantiation must remain uncreated and start-locked"
            )


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilityGateInstantiationContract:
    contract_id: str
    start_acceptance_id: str
    repeatability_preflight_id: str
    repeatability_runner_id: str
    slot_start_contract_id: str
    executor_binding_contract_id: str
    source_id: str
    slot_gate_instantiations: tuple[PublicAVReturnReplicationRepeatSlotGateInstantiation, ...]
    all_three_start_acceptances_bound: bool
    all_reserved_gate_ids_unique: bool
    all_reserved_executor_ids_unique: bool
    fresh_gate_per_slot_required: bool
    gate_instantiation_contract_complete: bool
    gate_instances_created: bool = False
    executor_callables_created: bool = False
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
        if self.contract_id != GATE_INSTANTIATION_ID:
            raise PublicAVReturnReplicationRepeatabilityGateInstantiationError(
                "unexpected gate instantiation contract identity"
            )
        if tuple(item.repeat_index for item in self.slot_gate_instantiations) != (1, 2, 3):
            raise PublicAVReturnReplicationRepeatabilityGateInstantiationError(
                "gate instantiation must contain exactly the ordered slots 1, 2, 3"
            )
        required = (
            self.all_three_start_acceptances_bound,
            self.all_reserved_gate_ids_unique,
            self.all_reserved_executor_ids_unique,
            self.fresh_gate_per_slot_required,
            self.gate_instantiation_contract_complete,
        )
        forbidden = (
            self.gate_instances_created,
            self.executor_callables_created,
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
            raise PublicAVReturnReplicationRepeatabilityGateInstantiationError(
                "gate instantiation contract is incomplete"
            )
        if any(forbidden):
            raise PublicAVReturnReplicationRepeatabilityGateInstantiationError(
                "gate instantiation contract cannot create gates, bind executors, start runs, or release claims"
            )


def reserve_public_av_return_replication_repeatability_gate_instances(
    acceptance: PublicAVReturnReplicationRepeatabilityStartAcceptance,
) -> PublicAVReturnReplicationRepeatabilityGateInstantiationContract:
    if not isinstance(acceptance, PublicAVReturnReplicationRepeatabilityStartAcceptance):
        raise PublicAVReturnReplicationRepeatabilityGateInstantiationError(
            "start acceptance has the wrong contract type"
        )
    if not acceptance.start_acceptance_complete:
        raise PublicAVReturnReplicationRepeatabilityGateInstantiationError(
            "complete start acceptance is required"
        )
    if (
        acceptance.gate_instances_created
        or acceptance.executor_callables_created
        or acceptance.start_release_granted
        or acceptance.repeatability_run_allowed
    ):
        raise PublicAVReturnReplicationRepeatabilityGateInstantiationError(
            "start acceptance must remain uninstantiated and run-locked"
        )

    slots = []
    for slot in acceptance.slot_acceptances:
        if (
            slot.gate_instance_created
            or slot.executor_callable_created
            or slot.executor_bound
            or slot.start_release_granted
            or slot.repeat_run_started
        ):
            raise PublicAVReturnReplicationRepeatabilityGateInstantiationError(
                f"slot {slot.repeat_index} is no longer fresh"
            )
        slots.append(
            PublicAVReturnReplicationRepeatSlotGateInstantiation(
                repeat_index=slot.repeat_index,
                gate_instantiation_id=(
                    f"{GATE_INSTANTIATION_ID}.repeat-{slot.repeat_index}.v1"
                ),
                start_acceptance_id=acceptance.acceptance_id,
                slot_acceptance_id=slot.acceptance_id,
                reserved_one_shot_gate_id=slot.future_one_shot_entrypoint_id,
                reserved_executor_id=slot.future_executor_id,
                slot_binding_id=slot.slot_binding_id,
                executor_binding_id=slot.executor_binding_id,
                source_id=slot.source_id,
                start_acceptance_bound=True,
                one_shot_gate_identity_reserved=True,
                executor_identity_carried=True,
                fresh_gate_required=True,
            )
        )

    gate_ids = tuple(item.reserved_one_shot_gate_id for item in slots)
    executor_ids = tuple(item.reserved_executor_id for item in slots)
    return PublicAVReturnReplicationRepeatabilityGateInstantiationContract(
        contract_id=GATE_INSTANTIATION_ID,
        start_acceptance_id=acceptance.acceptance_id,
        repeatability_preflight_id=acceptance.repeatability_preflight_id,
        repeatability_runner_id=acceptance.repeatability_runner_id,
        slot_start_contract_id=acceptance.slot_start_contract_id,
        executor_binding_contract_id=acceptance.executor_binding_contract_id,
        source_id=acceptance.source_id,
        slot_gate_instantiations=tuple(slots),
        all_three_start_acceptances_bound=True,
        all_reserved_gate_ids_unique=len(set(gate_ids)) == 3,
        all_reserved_executor_ids_unique=len(set(executor_ids)) == 3,
        fresh_gate_per_slot_required=True,
        gate_instantiation_contract_complete=True,
    )


def instantiate_public_av_return_replication_repeatability_gates(
    contract: PublicAVReturnReplicationRepeatabilityGateInstantiationContract,
) -> None:
    del contract
    raise PublicAVReturnReplicationRepeatabilityGateInstantiationError(
        "gate instantiation is not released by the locked repeatability gate contract"
    )


def public_av_return_replication_repeatability_gate_instantiation_to_jsonable(
    contract: PublicAVReturnReplicationRepeatabilityGateInstantiationContract,
) -> dict[str, Any]:
    return asdict(contract)
