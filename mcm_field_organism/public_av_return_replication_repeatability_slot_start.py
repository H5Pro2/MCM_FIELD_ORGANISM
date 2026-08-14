"""Locked per-slot bindings for repeatability one-shot entrypoints."""

from __future__ import annotations

from dataclasses import dataclass, fields

from .public_av_return_replication_repeatability_preflight import (
    PublicAVReturnReplicationRepeatabilityPreflight,
)
from .public_av_return_replication_repeatability_runner import (
    PublicAVReturnReplicationRepeatabilityRunnerWiring,
)


class PublicAVReturnReplicationRepeatabilitySlotStartError(ValueError):
    """Raised when a repeat slot binding could start or reuse a release."""


@dataclass(frozen=True, slots=True)
class PublicAVReturnReplicationRepeatSlotStartBinding:
    repeat_index: int
    binding_id: str
    one_shot_entrypoint_id: str
    repeatability_preflight_id: str
    base_preflight_id: str
    base_runner_id: str
    source_id: str
    positive_preflight_bound: bool
    one_shot_release_unconsumed: bool
    fresh_entrypoint_required: bool
    entrypoint_instance_created: bool
    executor_bound: bool
    start_allowed: bool
    repeat_run_started: bool
    prior_binding_reusable: bool

    def __post_init__(self) -> None:
        if self.repeat_index not in {1, 2, 3}:
            raise PublicAVReturnReplicationRepeatabilitySlotStartError("repeat index must be preregistered")
        expected_suffix = f"repeat-{self.repeat_index}.v1"
        if not self.binding_id.endswith(expected_suffix) or not self.one_shot_entrypoint_id.endswith(expected_suffix):
            raise PublicAVReturnReplicationRepeatabilitySlotStartError("slot identities must be index-bound")
        required = (
            self.positive_preflight_bound,
            self.one_shot_release_unconsumed,
            self.fresh_entrypoint_required,
        )
        forbidden = (
            self.entrypoint_instance_created,
            self.executor_bound,
            self.start_allowed,
            self.repeat_run_started,
            self.prior_binding_reusable,
        )
        if not all(required) or any(forbidden):
            raise PublicAVReturnReplicationRepeatabilitySlotStartError("slot binding must remain fresh and start-locked")


@dataclass(frozen=True, slots=True)
class PublicAVReturnReplicationRepeatabilitySlotStartContract:
    contract_id: str
    repeatability_preflight_id: str
    repeatability_runner_id: str
    source_id: str
    slot_bindings: tuple[PublicAVReturnReplicationRepeatSlotStartBinding, ...]
    all_positive_preflights_bound_once: bool
    entrypoint_ids_unique: bool
    binding_ids_unique: bool
    fresh_entrypoint_per_slot_required: bool
    contract_complete: bool
    executable: bool
    repeatability_run_allowed: bool
    automatic_repeat_loop_available: bool
    executor_binding_allowed: bool
    stability_threshold_defined: bool
    memory_claim_allowed: bool
    meaning_claim_allowed: bool
    organization_claim_allowed: bool
    ai_claim_allowed: bool

    def __post_init__(self) -> None:
        bindings = tuple(self.slot_bindings)
        if len(bindings) != 3 or tuple(item.repeat_index for item in bindings) != (1, 2, 3):
            raise PublicAVReturnReplicationRepeatabilitySlotStartError("three ordered slot bindings are required")
        computed_entrypoints_unique = len({item.one_shot_entrypoint_id for item in bindings}) == 3
        computed_bindings_unique = len({item.binding_id for item in bindings}) == 3
        if self.entrypoint_ids_unique != computed_entrypoints_unique or not computed_entrypoints_unique:
            raise PublicAVReturnReplicationRepeatabilitySlotStartError("entrypoint identities must be unique")
        if self.binding_ids_unique != computed_bindings_unique or not computed_bindings_unique:
            raise PublicAVReturnReplicationRepeatabilitySlotStartError("binding identities must be unique")
        required = (
            self.all_positive_preflights_bound_once,
            self.fresh_entrypoint_per_slot_required,
            self.contract_complete,
        )
        forbidden = (
            self.executable,
            self.repeatability_run_allowed,
            self.automatic_repeat_loop_available,
            self.executor_binding_allowed,
            self.stability_threshold_defined,
            self.memory_claim_allowed,
            self.meaning_claim_allowed,
            self.organization_claim_allowed,
            self.ai_claim_allowed,
        )
        if not all(required) or any(forbidden):
            raise PublicAVReturnReplicationRepeatabilitySlotStartError("slot start contract cannot release execution or claims")
        object.__setattr__(self, "slot_bindings", bindings)


def bind_public_av_return_replication_repeatability_slots(
    repeatability_wiring: PublicAVReturnReplicationRepeatabilityRunnerWiring,
    preflight: PublicAVReturnReplicationRepeatabilityPreflight,
) -> PublicAVReturnReplicationRepeatabilitySlotStartContract:
    if not isinstance(repeatability_wiring, PublicAVReturnReplicationRepeatabilityRunnerWiring):
        raise PublicAVReturnReplicationRepeatabilitySlotStartError("repeatability runner wiring is required")
    if not isinstance(preflight, PublicAVReturnReplicationRepeatabilityPreflight):
        raise PublicAVReturnReplicationRepeatabilitySlotStartError("repeatability preflight is required")
    if preflight.repeatability_runner_id != repeatability_wiring.runner_id:
        raise PublicAVReturnReplicationRepeatabilitySlotStartError("repeatability runner identity differs")
    if preflight.source_id != repeatability_wiring.source_id:
        raise PublicAVReturnReplicationRepeatabilitySlotStartError("source identity differs")
    if not preflight.repeatability_preflight_complete or preflight.repeatability_run_allowed:
        raise PublicAVReturnReplicationRepeatabilitySlotStartError("completed locked preflight is required")
    if any((repeatability_wiring.executable, repeatability_wiring.repeatability_run_allowed)):
        raise PublicAVReturnReplicationRepeatabilitySlotStartError("runner locks must remain engaged")
    bindings = []
    for runner_slot, slot_preflight in zip(
        repeatability_wiring.repeat_slots,
        preflight.repeat_slot_preflights,
        strict=True,
    ):
        if runner_slot.repeat_index != slot_preflight.repeat_index:
            raise PublicAVReturnReplicationRepeatabilitySlotStartError("repeat slot order differs")
        if not slot_preflight.positive_one_shot_release_available or not slot_preflight.one_shot_release_unconsumed:
            raise PublicAVReturnReplicationRepeatabilitySlotStartError("slot requires an unused positive one-shot release")
        suffix = f"repeat-{runner_slot.repeat_index}.v1"
        bindings.append(PublicAVReturnReplicationRepeatSlotStartBinding(
            repeat_index=runner_slot.repeat_index,
            binding_id=f"public.av.nasa-earthrise.return-replication.slot-binding.{suffix}",
            one_shot_entrypoint_id=f"public.av.nasa-earthrise.return-replication.one-shot-entrypoint.{suffix}",
            repeatability_preflight_id=preflight.preflight_id,
            base_preflight_id=slot_preflight.base_preflight_id,
            base_runner_id=runner_slot.base_runner_id,
            source_id=runner_slot.source_id,
            positive_preflight_bound=True,
            one_shot_release_unconsumed=True,
            fresh_entrypoint_required=True,
            entrypoint_instance_created=False,
            executor_bound=False,
            start_allowed=False,
            repeat_run_started=False,
            prior_binding_reusable=False,
        ))
    return PublicAVReturnReplicationRepeatabilitySlotStartContract(
        contract_id="public.av.nasa-earthrise.return-replication.repeatability-slot-start.v1",
        repeatability_preflight_id=preflight.preflight_id,
        repeatability_runner_id=repeatability_wiring.runner_id,
        source_id=preflight.source_id,
        slot_bindings=tuple(bindings),
        all_positive_preflights_bound_once=True,
        entrypoint_ids_unique=True,
        binding_ids_unique=True,
        fresh_entrypoint_per_slot_required=True,
        contract_complete=True,
        executable=False,
        repeatability_run_allowed=False,
        automatic_repeat_loop_available=False,
        executor_binding_allowed=False,
        stability_threshold_defined=False,
        memory_claim_allowed=False,
        meaning_claim_allowed=False,
        organization_claim_allowed=False,
        ai_claim_allowed=False,
    )


def public_av_return_replication_repeatability_slot_start_json_value(
    contract: PublicAVReturnReplicationRepeatabilitySlotStartContract,
) -> dict[str, object]:
    if not isinstance(contract, PublicAVReturnReplicationRepeatabilitySlotStartContract):
        raise PublicAVReturnReplicationRepeatabilitySlotStartError("slot start contract is required")

    def convert(value):
        if hasattr(value, "__dataclass_fields__"):
            return {role: convert(getattr(value, role)) for role in value.__dataclass_fields__}
        if isinstance(value, tuple):
            return [convert(item) for item in value]
        return value

    return convert(contract)


def public_av_return_replication_repeatability_slot_start_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (PublicAVReturnReplicationRepeatSlotStartBinding, PublicAVReturnReplicationRepeatabilitySlotStartContract)
        for item in fields(cls)
    )
