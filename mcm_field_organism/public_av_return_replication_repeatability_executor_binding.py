"""Locked per-slot executor identity bindings for repeatability starts."""

from __future__ import annotations

from dataclasses import dataclass, fields

from .public_av_return_permutation_contract import PublicAVReturnPermutationContract
from .public_av_return_replication_repeatability_slot_start import (
    PublicAVReturnReplicationRepeatabilitySlotStartContract,
)
from .public_av_return_replication_runner import PublicAVReturnReplicationRunnerWiring


class PublicAVReturnReplicationRepeatabilityExecutorBindingError(ValueError):
    """Raised when a repeat slot executor binding could instantiate execution."""


@dataclass(frozen=True, slots=True)
class PublicAVReturnReplicationRepeatSlotExecutorBinding:
    repeat_index: int
    executor_binding_id: str
    future_executor_id: str
    slot_binding_id: str
    one_shot_entrypoint_id: str
    repeatability_preflight_id: str
    base_preflight_id: str
    base_runner_id: str
    permutation_contract_id: str
    permutation_contract_digest: str
    source_id: str
    positive_slot_start_bound: bool
    preflight_identity_bound: bool
    runner_identity_bound: bool
    permutation_identity_bound: bool
    executor_identity_bound: bool
    executor_callable_created: bool
    entrypoint_instance_created: bool
    executor_bound_to_entrypoint: bool
    start_allowed: bool
    repeat_run_started: bool
    prior_executor_binding_reusable: bool

    def __post_init__(self) -> None:
        if self.repeat_index not in {1, 2, 3}:
            raise PublicAVReturnReplicationRepeatabilityExecutorBindingError("repeat index must be preregistered")
        expected_suffix = f"repeat-{self.repeat_index}.v1"
        if not self.executor_binding_id.endswith(expected_suffix) or not self.future_executor_id.endswith(expected_suffix):
            raise PublicAVReturnReplicationRepeatabilityExecutorBindingError("executor identities must be index-bound")
        required = (
            self.positive_slot_start_bound,
            self.preflight_identity_bound,
            self.runner_identity_bound,
            self.permutation_identity_bound,
            self.executor_identity_bound,
        )
        forbidden = (
            self.executor_callable_created,
            self.entrypoint_instance_created,
            self.executor_bound_to_entrypoint,
            self.start_allowed,
            self.repeat_run_started,
            self.prior_executor_binding_reusable,
        )
        if not all(required) or any(forbidden):
            raise PublicAVReturnReplicationRepeatabilityExecutorBindingError(
                "executor binding must remain identity-only and start-locked"
            )


@dataclass(frozen=True, slots=True)
class PublicAVReturnReplicationRepeatabilityExecutorBindingContract:
    contract_id: str
    slot_start_contract_id: str
    repeatability_preflight_id: str
    repeatability_runner_id: str
    permutation_contract_id: str
    permutation_contract_digest: str
    source_id: str
    slot_executor_bindings: tuple[PublicAVReturnReplicationRepeatSlotExecutorBinding, ...]
    all_slots_have_executor_identity: bool
    executor_binding_ids_unique: bool
    future_executor_ids_unique: bool
    preflight_runner_permutation_bound_per_slot: bool
    entrypoint_instances_created: bool
    executor_callables_created: bool
    executor_binding_allowed: bool
    start_allowed: bool
    repeatability_run_allowed: bool
    automatic_repeat_loop_available: bool
    stability_threshold_defined: bool
    memory_claim_allowed: bool
    meaning_claim_allowed: bool
    organization_claim_allowed: bool
    ai_claim_allowed: bool

    def __post_init__(self) -> None:
        bindings = tuple(self.slot_executor_bindings)
        if len(bindings) != 3 or tuple(item.repeat_index for item in bindings) != (1, 2, 3):
            raise PublicAVReturnReplicationRepeatabilityExecutorBindingError(
                "three ordered slot executor bindings are required"
            )
        binding_ids_unique = len({item.executor_binding_id for item in bindings}) == 3
        executor_ids_unique = len({item.future_executor_id for item in bindings}) == 3
        if self.executor_binding_ids_unique != binding_ids_unique or not binding_ids_unique:
            raise PublicAVReturnReplicationRepeatabilityExecutorBindingError("executor binding identities must be unique")
        if self.future_executor_ids_unique != executor_ids_unique or not executor_ids_unique:
            raise PublicAVReturnReplicationRepeatabilityExecutorBindingError("future executor identities must be unique")
        required = (
            self.all_slots_have_executor_identity,
            self.preflight_runner_permutation_bound_per_slot,
        )
        forbidden = (
            self.entrypoint_instances_created,
            self.executor_callables_created,
            self.executor_binding_allowed,
            self.start_allowed,
            self.repeatability_run_allowed,
            self.automatic_repeat_loop_available,
            self.stability_threshold_defined,
            self.memory_claim_allowed,
            self.meaning_claim_allowed,
            self.organization_claim_allowed,
            self.ai_claim_allowed,
        )
        if not all(required) or any(forbidden):
            raise PublicAVReturnReplicationRepeatabilityExecutorBindingError(
                "executor binding contract cannot create executors, start runs, or release claims"
            )
        object.__setattr__(self, "slot_executor_bindings", bindings)


def bind_public_av_return_replication_repeatability_slot_executors(
    slot_start_contract: PublicAVReturnReplicationRepeatabilitySlotStartContract,
    base_wiring: PublicAVReturnReplicationRunnerWiring,
    permutation_contract: PublicAVReturnPermutationContract,
) -> PublicAVReturnReplicationRepeatabilityExecutorBindingContract:
    if not isinstance(slot_start_contract, PublicAVReturnReplicationRepeatabilitySlotStartContract):
        raise PublicAVReturnReplicationRepeatabilityExecutorBindingError("slot start contract is required")
    if not isinstance(base_wiring, PublicAVReturnReplicationRunnerWiring):
        raise PublicAVReturnReplicationRepeatabilityExecutorBindingError("base runner wiring is required")
    if not isinstance(permutation_contract, PublicAVReturnPermutationContract):
        raise PublicAVReturnReplicationRepeatabilityExecutorBindingError("permutation contract is required")
    if not slot_start_contract.contract_complete or slot_start_contract.executor_binding_allowed:
        raise PublicAVReturnReplicationRepeatabilityExecutorBindingError("locked slot start contract is required")
    if base_wiring.executable or base_wiring.replication_run_allowed:
        raise PublicAVReturnReplicationRepeatabilityExecutorBindingError("base runner must remain non-executable")
    if permutation_contract.replication_run_allowed or not permutation_contract.fully_specified:
        raise PublicAVReturnReplicationRepeatabilityExecutorBindingError("locked complete permutation contract is required")
    if slot_start_contract.repeatability_runner_id == "" or slot_start_contract.source_id != base_wiring.source_id:
        raise PublicAVReturnReplicationRepeatabilityExecutorBindingError("runner or source identity differs")
    if base_wiring.permutation_contract_id != permutation_contract.contract_id:
        raise PublicAVReturnReplicationRepeatabilityExecutorBindingError("permutation contract identity differs")
    if base_wiring.permutation_contract_digest != permutation_contract.contract_digest:
        raise PublicAVReturnReplicationRepeatabilityExecutorBindingError("permutation contract digest differs")

    bindings = []
    for slot in slot_start_contract.slot_bindings:
        if slot.base_runner_id != base_wiring.runner_id:
            raise PublicAVReturnReplicationRepeatabilityExecutorBindingError("slot runner identity differs")
        if slot.entrypoint_instance_created or slot.executor_bound or slot.start_allowed or slot.repeat_run_started:
            raise PublicAVReturnReplicationRepeatabilityExecutorBindingError("slot start must remain uninstantiated")
        suffix = f"repeat-{slot.repeat_index}.v1"
        bindings.append(PublicAVReturnReplicationRepeatSlotExecutorBinding(
            repeat_index=slot.repeat_index,
            executor_binding_id=f"public.av.nasa-earthrise.return-replication.executor-binding.{suffix}",
            future_executor_id=f"public.av.nasa-earthrise.return-replication.executor.{suffix}",
            slot_binding_id=slot.binding_id,
            one_shot_entrypoint_id=slot.one_shot_entrypoint_id,
            repeatability_preflight_id=slot.repeatability_preflight_id,
            base_preflight_id=slot.base_preflight_id,
            base_runner_id=slot.base_runner_id,
            permutation_contract_id=permutation_contract.contract_id,
            permutation_contract_digest=permutation_contract.contract_digest,
            source_id=slot.source_id,
            positive_slot_start_bound=True,
            preflight_identity_bound=True,
            runner_identity_bound=True,
            permutation_identity_bound=True,
            executor_identity_bound=True,
            executor_callable_created=False,
            entrypoint_instance_created=False,
            executor_bound_to_entrypoint=False,
            start_allowed=False,
            repeat_run_started=False,
            prior_executor_binding_reusable=False,
        ))

    return PublicAVReturnReplicationRepeatabilityExecutorBindingContract(
        contract_id="public.av.nasa-earthrise.return-replication.repeatability-executor-binding.v1",
        slot_start_contract_id=slot_start_contract.contract_id,
        repeatability_preflight_id=slot_start_contract.repeatability_preflight_id,
        repeatability_runner_id=slot_start_contract.repeatability_runner_id,
        permutation_contract_id=permutation_contract.contract_id,
        permutation_contract_digest=permutation_contract.contract_digest,
        source_id=slot_start_contract.source_id,
        slot_executor_bindings=tuple(bindings),
        all_slots_have_executor_identity=True,
        executor_binding_ids_unique=True,
        future_executor_ids_unique=True,
        preflight_runner_permutation_bound_per_slot=True,
        entrypoint_instances_created=False,
        executor_callables_created=False,
        executor_binding_allowed=False,
        start_allowed=False,
        repeatability_run_allowed=False,
        automatic_repeat_loop_available=False,
        stability_threshold_defined=False,
        memory_claim_allowed=False,
        meaning_claim_allowed=False,
        organization_claim_allowed=False,
        ai_claim_allowed=False,
    )


def public_av_return_replication_repeatability_executor_binding_json_value(
    contract: PublicAVReturnReplicationRepeatabilityExecutorBindingContract,
) -> dict[str, object]:
    if not isinstance(contract, PublicAVReturnReplicationRepeatabilityExecutorBindingContract):
        raise PublicAVReturnReplicationRepeatabilityExecutorBindingError("executor binding contract is required")

    def convert(value):
        if hasattr(value, "__dataclass_fields__"):
            return {role: convert(getattr(value, role)) for role in value.__dataclass_fields__}
        if isinstance(value, tuple):
            return [convert(item) for item in value]
        return value

    return convert(contract)


def public_av_return_replication_repeatability_executor_binding_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            PublicAVReturnReplicationRepeatSlotExecutorBinding,
            PublicAVReturnReplicationRepeatabilityExecutorBindingContract,
        )
        for item in fields(cls)
    )
