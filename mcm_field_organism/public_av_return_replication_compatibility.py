"""Structural compatibility audit for the six-arm public AV replication."""

from __future__ import annotations

from dataclasses import dataclass, fields

from .public_av_return_replication_preregistration import (
    PublicAVReturnReplicationPreregistration,
    public_av_return_replication_preregistration,
)
from .public_av_return_permutation_contract import (
    PublicAVReturnPermutationContract,
    public_av_return_permutation_contract,
)
from .shared_field_component_intervention import shared_field_component_intervention_public_roles


class PublicAVReturnReplicationCompatibilityError(ValueError):
    """Raised when compatibility would authorize unsupported interventions."""


@dataclass(frozen=True, slots=True)
class PublicAVReturnReplicationArmCompatibility:
    arm_id: str
    existing_runtime_supports_arm: bool
    runtime_path: str | None
    blocker: str | None
    artificial_receptor_events_required: bool
    special_state_rule_required: bool
    sequence_transform_fully_specified: bool

    def __post_init__(self) -> None:
        if self.existing_runtime_supports_arm:
            if self.runtime_path is None or self.blocker is not None:
                raise PublicAVReturnReplicationCompatibilityError("supported arm requires one existing path")
            if self.artificial_receptor_events_required or self.special_state_rule_required:
                raise PublicAVReturnReplicationCompatibilityError("supported arm cannot require artificial input or rules")
        elif self.blocker is None:
            raise PublicAVReturnReplicationCompatibilityError("unsupported arm requires one blocker")


@dataclass(frozen=True, slots=True)
class PublicAVReturnReplicationCompatibilityAudit:
    audit_id: str
    preregistration_id: str
    source_id: str
    clock_id: str
    arms: tuple[PublicAVReturnReplicationArmCompatibility, ...]
    full_state_and_fresh_arms_supported: bool
    withheld_stage_two_supported_contact_free: bool
    component_state_interventions_supported: bool
    permuted_stage_two_contract_complete: bool
    all_preregistered_arms_supported: bool
    runner_implementation_allowed: bool
    replication_run_allowed: bool
    artificial_media_events_introduced: bool
    special_rules_introduced: bool
    field_parameters_changed: bool
    audit_complete: bool
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        arms = tuple(self.arms)
        if len(arms) != 6 or len({arm.arm_id for arm in arms}) != 6:
            raise PublicAVReturnReplicationCompatibilityError("audit requires six unique arms")
        computed_all = all(arm.existing_runtime_supports_arm for arm in arms)
        if self.all_preregistered_arms_supported != computed_all:
            raise PublicAVReturnReplicationCompatibilityError("aggregate compatibility differs from arms")
        if not self.full_state_and_fresh_arms_supported or not self.withheld_stage_two_supported_contact_free:
            raise PublicAVReturnReplicationCompatibilityError("known existing paths must remain represented")
        if self.runner_implementation_allowed != computed_all:
            raise PublicAVReturnReplicationCompatibilityError("runner implementation must follow structural support")
        forbidden = (
            self.replication_run_allowed,
            self.artificial_media_events_introduced,
            self.special_rules_introduced,
            self.field_parameters_changed,
            self.memory_claim_allowed,
            self.meaning_claim_allowed,
            self.organization_claim_allowed,
            self.ai_claim_allowed,
        )
        if any(forbidden):
            raise PublicAVReturnReplicationCompatibilityError("compatibility audit cannot release run, rules, or claims")
        if not self.audit_complete:
            raise PublicAVReturnReplicationCompatibilityError("audit must be complete")
        object.__setattr__(self, "arms", arms)


def audit_public_av_return_replication_compatibility(
    preregistration: PublicAVReturnReplicationPreregistration | None = None,
    permutation_contract: PublicAVReturnPermutationContract | None = None,
) -> PublicAVReturnReplicationCompatibilityAudit:
    plan = preregistration or public_av_return_replication_preregistration()
    if not isinstance(plan, PublicAVReturnReplicationPreregistration):
        raise PublicAVReturnReplicationCompatibilityError("replication preregistration is required")
    contract = permutation_contract or public_av_return_permutation_contract(plan)
    if not isinstance(contract, PublicAVReturnPermutationContract):
        raise PublicAVReturnReplicationCompatibilityError("permutation contract is required")

    permutation_complete = (
        contract.preregistration_id == plan.preregistration_id
        and contract.arm_id == "control.stage_two_order_permuted"
        and contract.source_stage_sequence_digest == plan.stage_sequence_digest
        and contract.event_time_contract.clock_id == plan.clock_id
        and contract.fully_specified
    )
    component_roles = set(shared_field_component_intervention_public_roles())
    component_supported = {
        "mode",
        "neutral_value",
        "activation_preserved_exactly",
        "afterimage_preserved_exactly",
        "activation_reset_globally",
        "afterimage_reset_globally",
        "observer_side_only",
        "organism_function_added",
        "field_time_advanced",
        "receptor_events_introduced",
        "field_parameters_changed",
    }.issubset(component_roles)

    support = {
        "return.continued.full_state": (
            True, "two_stage_return.full_state_carry", None, True,
        ),
        "return.fresh_stage_two": (
            True, "two_stage_return.fresh_stage_two", None, True,
        ),
        "control.activation_only_carry": (
            component_supported, "component_intervention.reset_afterimage_preserve_activation",
            None if component_supported else "component intervention contract is incomplete",
            True,
        ),
        "control.afterimage_only_carry": (
            component_supported, "component_intervention.reset_activation_preserve_afterimage",
            None if component_supported else "component intervention contract is incomplete",
            True,
        ),
        "control.stage_two_order_permuted": (
            permutation_complete, "permutation_contract.reverse_rank_stage_two",
            None if permutation_complete else "permutation contract is incomplete",
            permutation_complete,
        ),
        "control.stage_two_sequence_withheld": (
            True, "contact_free_field_step.stage_two_horizon", None, True,
        ),
    }
    arms = tuple(
        PublicAVReturnReplicationArmCompatibility(
            arm_id=arm.arm_id,
            existing_runtime_supports_arm=support[arm.arm_id][0],
            runtime_path=support[arm.arm_id][1],
            blocker=support[arm.arm_id][2],
            artificial_receptor_events_required=False,
            special_state_rule_required=False,
            sequence_transform_fully_specified=support[arm.arm_id][3],
        )
        for arm in plan.arms
    )
    all_supported = all(arm.existing_runtime_supports_arm for arm in arms)
    return PublicAVReturnReplicationCompatibilityAudit(
        audit_id="public.av.nasa-earthrise.return-replication.compatibility.v2",
        preregistration_id=plan.preregistration_id,
        source_id=plan.source_id,
        clock_id=plan.clock_id,
        arms=arms,
        full_state_and_fresh_arms_supported=True,
        withheld_stage_two_supported_contact_free=True,
        component_state_interventions_supported=component_supported,
        permuted_stage_two_contract_complete=permutation_complete,
        all_preregistered_arms_supported=all_supported,
        runner_implementation_allowed=all_supported,
        replication_run_allowed=False,
        artificial_media_events_introduced=False,
        special_rules_introduced=False,
        field_parameters_changed=False,
        audit_complete=True,
    )


def public_av_return_replication_compatibility_json_value(
    audit: PublicAVReturnReplicationCompatibilityAudit,
) -> dict[str, object]:
    if not isinstance(audit, PublicAVReturnReplicationCompatibilityAudit):
        raise PublicAVReturnReplicationCompatibilityError("compatibility audit is required")

    def convert(value):
        if hasattr(value, "__dataclass_fields__"):
            return {name: convert(getattr(value, name)) for name in value.__dataclass_fields__}
        if isinstance(value, tuple):
            return [convert(item) for item in value]
        return value

    return convert(audit)


def public_av_return_replication_compatibility_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (PublicAVReturnReplicationArmCompatibility, PublicAVReturnReplicationCompatibilityAudit)
        for item in fields(cls)
    )
