"""Non-executable wiring contract for the six-arm public AV return replication."""

from __future__ import annotations

from dataclasses import dataclass, fields

from .public_av_return_permutation_contract import (
    PublicAVReturnPermutationContract,
    public_av_return_permutation_contract,
)
from .public_av_return_replication_compatibility import (
    PublicAVReturnReplicationCompatibilityAudit,
    audit_public_av_return_replication_compatibility,
)
from .public_av_return_replication_preregistration import (
    PublicAVReturnReplicationPreregistration,
    public_av_return_replication_preregistration,
)


class PublicAVReturnReplicationRunnerError(ValueError):
    """Raised when replication wiring violates its preregistered boundary."""


@dataclass(frozen=True, slots=True)
class PublicAVReturnReplicationArmWiring:
    arm_id: str
    stage_one_sequence_id: str
    stage_two_sequence_id: str
    stage_one_interval_ticks: tuple[int, int]
    resolution_interval_ticks: tuple[int, int]
    stage_two_interval_ticks: tuple[int, int]
    stage_two_state_mode: str
    causal_contrast_role: str
    runtime_path: str
    component_intervention_mode: str | None
    permutation_contract_id: str | None
    permutation_contract_digest: str | None
    stage_two_sequence_digest: tuple[str, str] | None
    stage_two_contact_mode: str
    measured_roles: tuple[str, ...]
    executable: bool = False

    def __post_init__(self) -> None:
        if self.stage_one_interval_ticks != (0, 500_000_000):
            raise PublicAVReturnReplicationRunnerError("stage-one interval changed")
        if self.resolution_interval_ticks != (500_000_000, 600_000_000):
            raise PublicAVReturnReplicationRunnerError("resolution interval changed")
        if self.stage_two_interval_ticks != (600_000_000, 1_100_000_000):
            raise PublicAVReturnReplicationRunnerError("stage-two interval changed")
        if not self.runtime_path or not self.measured_roles:
            raise PublicAVReturnReplicationRunnerError("arm requires runtime and measurement contracts")
        if self.executable:
            raise PublicAVReturnReplicationRunnerError("arm wiring cannot be executable")
        object.__setattr__(self, "measured_roles", tuple(self.measured_roles))
        if self.stage_two_sequence_digest is not None:
            object.__setattr__(self, "stage_two_sequence_digest", tuple(self.stage_two_sequence_digest))


@dataclass(frozen=True, slots=True)
class PublicAVReturnReplicationRunnerWiring:
    runner_id: str
    preregistration_id: str
    compatibility_audit_id: str
    source_id: str
    clock_id: str
    permutation_contract_id: str
    permutation_contract_digest: str
    arms: tuple[PublicAVReturnReplicationArmWiring, ...]
    fixed_field_parameters: tuple[str, ...]
    required_invariants: tuple[str, ...]
    wiring_complete: bool
    all_arms_structurally_supported: bool
    implementation_allowed_for_wiring_only: bool
    executable: bool = False
    replication_run_allowed: bool = False
    media_decode_allowed: bool = False
    receptor_feed_allowed: bool = False
    memory_threshold_defined: bool = False
    organization_threshold_defined: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        arms = tuple(self.arms)
        if len(arms) != 6 or len({arm.arm_id for arm in arms}) != 6:
            raise PublicAVReturnReplicationRunnerError("runner requires six unique arms")
        if not self.wiring_complete or not self.all_arms_structurally_supported:
            raise PublicAVReturnReplicationRunnerError("runner requires complete structural support")
        if not self.implementation_allowed_for_wiring_only:
            raise PublicAVReturnReplicationRunnerError("wiring-only implementation must be explicit")
        forbidden = (
            self.executable, self.replication_run_allowed, self.media_decode_allowed,
            self.receptor_feed_allowed, self.memory_threshold_defined,
            self.organization_threshold_defined, self.memory_claim_allowed,
            self.meaning_claim_allowed, self.organization_claim_allowed, self.ai_claim_allowed,
        )
        if any(forbidden):
            raise PublicAVReturnReplicationRunnerError("runner wiring cannot release execution or claims")
        object.__setattr__(self, "arms", arms)
        object.__setattr__(self, "fixed_field_parameters", tuple(self.fixed_field_parameters))
        object.__setattr__(self, "required_invariants", tuple(self.required_invariants))


def wire_public_av_return_replication_runner(
    compatibility_audit: PublicAVReturnReplicationCompatibilityAudit | None = None,
    preregistration: PublicAVReturnReplicationPreregistration | None = None,
    permutation_contract: PublicAVReturnPermutationContract | None = None,
) -> PublicAVReturnReplicationRunnerWiring:
    plan = preregistration or public_av_return_replication_preregistration()
    contract = permutation_contract or public_av_return_permutation_contract(plan)
    audit = compatibility_audit or audit_public_av_return_replication_compatibility(plan, contract)
    if not isinstance(plan, PublicAVReturnReplicationPreregistration):
        raise PublicAVReturnReplicationRunnerError("preregistration is required")
    if not isinstance(contract, PublicAVReturnPermutationContract):
        raise PublicAVReturnReplicationRunnerError("permutation contract is required")
    if not isinstance(audit, PublicAVReturnReplicationCompatibilityAudit):
        raise PublicAVReturnReplicationRunnerError("compatibility audit is required")
    if audit.preregistration_id != plan.preregistration_id or contract.preregistration_id != plan.preregistration_id:
        raise PublicAVReturnReplicationRunnerError("contract identity mismatch")
    if audit.source_id != plan.source_id or audit.clock_id != plan.clock_id:
        raise PublicAVReturnReplicationRunnerError("source or clock mismatch")
    if not audit.all_preregistered_arms_supported or not audit.runner_implementation_allowed:
        raise PublicAVReturnReplicationRunnerError("all arms require implementation release")
    if audit.replication_run_allowed:
        raise PublicAVReturnReplicationRunnerError("compatibility audit cannot release a run")

    compatibility = {item.arm_id: item for item in audit.arms}
    interventions = {
        "control.activation_only_carry": "reset_afterimage_preserve_activation",
        "control.afterimage_only_carry": "reset_activation_preserve_afterimage",
    }
    wired = []
    for arm in plan.arms:
        support = compatibility[arm.arm_id]
        if not support.existing_runtime_supports_arm or support.runtime_path is None:
            raise PublicAVReturnReplicationRunnerError(f"unsupported arm: {arm.arm_id}")
        permuted = arm.arm_id == contract.arm_id
        withheld = arm.arm_id == "control.stage_two_sequence_withheld"
        digest = None if withheld else (
            (contract.auditory_permuted_sequence_digest, contract.visual_permuted_sequence_digest)
            if permuted else plan.stage_sequence_digest
        )
        wired.append(PublicAVReturnReplicationArmWiring(
            arm_id=arm.arm_id,
            stage_one_sequence_id=arm.stage_one_sequence_id,
            stage_two_sequence_id=arm.stage_two_sequence_id,
            stage_one_interval_ticks=(0, 500_000_000),
            resolution_interval_ticks=(500_000_000, 600_000_000),
            stage_two_interval_ticks=(600_000_000, 1_100_000_000),
            stage_two_state_mode=arm.stage_two_state_mode,
            causal_contrast_role=arm.causal_contrast_role,
            runtime_path=support.runtime_path,
            component_intervention_mode=interventions.get(arm.arm_id),
            permutation_contract_id=contract.contract_id if permuted else None,
            permutation_contract_digest=contract.contract_digest if permuted else None,
            stage_two_sequence_digest=digest,
            stage_two_contact_mode=(
                "withheld_contact_free" if withheld else
                "permuted_reduced_sequence" if permuted else "audited_reduced_sequence"
            ),
            measured_roles=plan.measured_roles,
        ))
    return PublicAVReturnReplicationRunnerWiring(
        runner_id="public.av.nasa-earthrise.return-replication.runner.wiring.v1",
        preregistration_id=plan.preregistration_id,
        compatibility_audit_id=audit.audit_id,
        source_id=plan.source_id,
        clock_id=plan.clock_id,
        permutation_contract_id=contract.contract_id,
        permutation_contract_digest=contract.contract_digest,
        arms=tuple(wired),
        fixed_field_parameters=plan.fixed_field_parameters,
        required_invariants=plan.required_invariants,
        wiring_complete=True,
        all_arms_structurally_supported=True,
        implementation_allowed_for_wiring_only=True,
    )


def execute_public_av_return_replication_runner(wiring: PublicAVReturnReplicationRunnerWiring) -> None:
    if not isinstance(wiring, PublicAVReturnReplicationRunnerWiring):
        raise PublicAVReturnReplicationRunnerError("runner wiring is required")
    raise PublicAVReturnReplicationRunnerError("replication execution is not released")


def public_av_return_replication_runner_json_value(
    wiring: PublicAVReturnReplicationRunnerWiring,
) -> dict[str, object]:
    if not isinstance(wiring, PublicAVReturnReplicationRunnerWiring):
        raise PublicAVReturnReplicationRunnerError("runner wiring is required")

    def convert(value):
        if hasattr(value, "__dataclass_fields__"):
            return {role: convert(getattr(value, role)) for role in value.__dataclass_fields__}
        if isinstance(value, tuple):
            return [convert(item) for item in value]
        return value

    return convert(wiring)


def public_av_return_replication_runner_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (PublicAVReturnReplicationArmWiring, PublicAVReturnReplicationRunnerWiring)
        for item in fields(cls)
    )
