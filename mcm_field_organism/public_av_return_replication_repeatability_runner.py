"""Locked structural runner wiring for three independent AV replication repeats."""

from __future__ import annotations

from dataclasses import dataclass, fields

from .public_av_return_replication_repeatability_preregistration import (
    PublicAVReturnReplicationRepeatabilityPreregistration,
    public_av_return_replication_repeatability_preregistration,
)
from .public_av_return_replication_runner import (
    PublicAVReturnReplicationRunnerWiring,
    wire_public_av_return_replication_runner,
)


class PublicAVReturnReplicationRepeatabilityRunnerError(ValueError):
    """Raised when repeatability wiring could execute or share state."""


@dataclass(frozen=True, slots=True)
class PublicAVReturnReplicationRepeatSlotWiring:
    repeat_index: int
    base_runner_id: str
    base_preregistration_id: str
    source_id: str
    clock_id: str
    arm_ids: tuple[str, ...]
    permutation_contract_digest: str
    fixed_field_parameters: tuple[str, ...]
    fresh_runner_instance_required: bool
    fresh_field_at_repeat_start: bool
    separate_start_preflight_required: bool
    cross_repeat_state_carry_allowed: bool
    prior_execution_receipt_reusable: bool
    executable: bool = False

    def __post_init__(self) -> None:
        if self.repeat_index not in {1, 2, 3}:
            raise PublicAVReturnReplicationRepeatabilityRunnerError("repeat index must be preregistered")
        if len(self.arm_ids) != 6 or len(set(self.arm_ids)) != 6:
            raise PublicAVReturnReplicationRepeatabilityRunnerError("each repeat requires six unique arms")
        required = (
            self.fresh_runner_instance_required,
            self.fresh_field_at_repeat_start,
            self.separate_start_preflight_required,
        )
        forbidden = (
            self.cross_repeat_state_carry_allowed,
            self.prior_execution_receipt_reusable,
            self.executable,
        )
        if not all(required) or any(forbidden):
            raise PublicAVReturnReplicationRepeatabilityRunnerError("repeat slot must remain fresh and non-executable")
        object.__setattr__(self, "arm_ids", tuple(self.arm_ids))
        object.__setattr__(self, "fixed_field_parameters", tuple(self.fixed_field_parameters))


@dataclass(frozen=True, slots=True)
class PublicAVReturnReplicationRepeatabilityRunnerWiring:
    runner_id: str
    repeatability_preregistration_id: str
    base_runner_id: str
    source_id: str
    clock_id: str
    repeat_slots: tuple[PublicAVReturnReplicationRepeatSlotWiring, ...]
    stability_measurements: tuple[str, ...]
    contract_parameters_required_identical: tuple[str, ...]
    all_repeat_slots_structurally_wired: bool
    runner_wiring_implementation_allowed: bool
    automatic_repeat_loop_available: bool
    executable: bool
    repeatability_run_allowed: bool
    media_decode_allowed: bool
    receptor_feed_allowed: bool
    stability_threshold_defined: bool
    memory_threshold_defined: bool
    organization_threshold_defined: bool
    causal_mechanism_claim_allowed: bool
    memory_claim_allowed: bool
    meaning_claim_allowed: bool
    organization_claim_allowed: bool
    ai_claim_allowed: bool

    def __post_init__(self) -> None:
        slots = tuple(self.repeat_slots)
        if len(slots) != 3 or tuple(item.repeat_index for item in slots) != (1, 2, 3):
            raise PublicAVReturnReplicationRepeatabilityRunnerError("three ordered repeat slots are required")
        if not self.all_repeat_slots_structurally_wired or not self.runner_wiring_implementation_allowed:
            raise PublicAVReturnReplicationRepeatabilityRunnerError("structural wiring must be explicit")
        forbidden = (
            self.automatic_repeat_loop_available,
            self.executable,
            self.repeatability_run_allowed,
            self.media_decode_allowed,
            self.receptor_feed_allowed,
            self.stability_threshold_defined,
            self.memory_threshold_defined,
            self.organization_threshold_defined,
            self.causal_mechanism_claim_allowed,
            self.memory_claim_allowed,
            self.meaning_claim_allowed,
            self.organization_claim_allowed,
            self.ai_claim_allowed,
        )
        if any(forbidden):
            raise PublicAVReturnReplicationRepeatabilityRunnerError("repeatability wiring cannot release loops, runs, or claims")
        object.__setattr__(self, "repeat_slots", slots)
        object.__setattr__(self, "stability_measurements", tuple(self.stability_measurements))
        object.__setattr__(self, "contract_parameters_required_identical", tuple(self.contract_parameters_required_identical))


def wire_public_av_return_replication_repeatability_runner(
    preregistration: PublicAVReturnReplicationRepeatabilityPreregistration | None = None,
    base_wiring: PublicAVReturnReplicationRunnerWiring | None = None,
) -> PublicAVReturnReplicationRepeatabilityRunnerWiring:
    plan = preregistration or public_av_return_replication_repeatability_preregistration()
    runner = base_wiring or wire_public_av_return_replication_runner()
    if not isinstance(plan, PublicAVReturnReplicationRepeatabilityPreregistration):
        raise PublicAVReturnReplicationRepeatabilityRunnerError("repeatability preregistration is required")
    if not isinstance(runner, PublicAVReturnReplicationRunnerWiring):
        raise PublicAVReturnReplicationRepeatabilityRunnerError("base runner wiring is required")
    if plan.base_preregistration_id != runner.preregistration_id:
        raise PublicAVReturnReplicationRepeatabilityRunnerError("base preregistration differs")
    if plan.source_id != runner.source_id or plan.clock_id != runner.clock_id:
        raise PublicAVReturnReplicationRepeatabilityRunnerError("source or clock differs")
    if not runner.wiring_complete or not runner.all_arms_structurally_supported:
        raise PublicAVReturnReplicationRepeatabilityRunnerError("base runner is incomplete")
    if any((runner.executable, runner.replication_run_allowed, runner.media_decode_allowed, runner.receptor_feed_allowed)):
        raise PublicAVReturnReplicationRepeatabilityRunnerError("base runner locks must remain engaged")
    arm_ids = tuple(arm.arm_id for arm in runner.arms)
    slots = tuple(
        PublicAVReturnReplicationRepeatSlotWiring(
            repeat_index=index,
            base_runner_id=runner.runner_id,
            base_preregistration_id=runner.preregistration_id,
            source_id=runner.source_id,
            clock_id=runner.clock_id,
            arm_ids=arm_ids,
            permutation_contract_digest=runner.permutation_contract_digest,
            fixed_field_parameters=runner.fixed_field_parameters,
            fresh_runner_instance_required=True,
            fresh_field_at_repeat_start=True,
            separate_start_preflight_required=True,
            cross_repeat_state_carry_allowed=False,
            prior_execution_receipt_reusable=False,
        )
        for index in plan.repeat_index_set
    )
    return PublicAVReturnReplicationRepeatabilityRunnerWiring(
        runner_id="public.av.nasa-earthrise.return-replication.repeatability-runner.wiring.v1",
        repeatability_preregistration_id=plan.preregistration_id,
        base_runner_id=runner.runner_id,
        source_id=runner.source_id,
        clock_id=runner.clock_id,
        repeat_slots=slots,
        stability_measurements=plan.stability_measurements,
        contract_parameters_required_identical=plan.contract_parameters_required_identical,
        all_repeat_slots_structurally_wired=True,
        runner_wiring_implementation_allowed=True,
        automatic_repeat_loop_available=False,
        executable=False,
        repeatability_run_allowed=False,
        media_decode_allowed=False,
        receptor_feed_allowed=False,
        stability_threshold_defined=False,
        memory_threshold_defined=False,
        organization_threshold_defined=False,
        causal_mechanism_claim_allowed=False,
        memory_claim_allowed=False,
        meaning_claim_allowed=False,
        organization_claim_allowed=False,
        ai_claim_allowed=False,
    )


def execute_public_av_return_replication_repeatability_runner(
    wiring: PublicAVReturnReplicationRepeatabilityRunnerWiring,
) -> None:
    if not isinstance(wiring, PublicAVReturnReplicationRepeatabilityRunnerWiring):
        raise PublicAVReturnReplicationRepeatabilityRunnerError("repeatability runner wiring is required")
    raise PublicAVReturnReplicationRepeatabilityRunnerError("repeatability execution is not released")


def public_av_return_replication_repeatability_runner_json_value(
    wiring: PublicAVReturnReplicationRepeatabilityRunnerWiring,
) -> dict[str, object]:
    if not isinstance(wiring, PublicAVReturnReplicationRepeatabilityRunnerWiring):
        raise PublicAVReturnReplicationRepeatabilityRunnerError("repeatability runner wiring is required")

    def convert(value):
        if hasattr(value, "__dataclass_fields__"):
            return {role: convert(getattr(value, role)) for role in value.__dataclass_fields__}
        if isinstance(value, tuple):
            return [convert(item) for item in value]
        return value

    return convert(wiring)


def public_av_return_replication_repeatability_runner_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (PublicAVReturnReplicationRepeatSlotWiring, PublicAVReturnReplicationRepeatabilityRunnerWiring)
        for item in fields(cls)
    )
