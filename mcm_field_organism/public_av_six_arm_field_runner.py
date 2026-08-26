"""Non-executable wiring contract for the corrected six-arm public AV field run."""

from __future__ import annotations

from dataclasses import dataclass, fields

from .public_av_field_path_compatibility import (
    PublicAVFieldPathCompatibilityAudit,
)
from .public_av_field_preregistration import (
    PublicAVFieldArmPlan,
    PublicAVFieldPreregistration,
    public_av_passive_field_preregistration,
)


class PublicAVSixArmFieldRunnerError(ValueError):
    """Raised when field-run wiring would become executable or biased."""


@dataclass(frozen=True, slots=True)
class PublicAVSixArmFieldArmWiring:
    arm_id: str
    included_modalities: tuple[str, ...]
    partition_id: str
    reverse_sequence_declaration: bool
    fresh_field_required: bool
    dock_geometry_digest: tuple[tuple[str, str, int], ...]
    field_parameter_contract: tuple[str, ...]
    measured_roles: tuple[str, ...]
    executable: bool = False

    def __post_init__(self) -> None:
        if not self.arm_id:
            raise PublicAVSixArmFieldRunnerError("arm_id must be non-empty")
        modalities = tuple(self.included_modalities)
        if not modalities or any(item not in {"auditory", "visual"} for item in modalities):
            raise PublicAVSixArmFieldRunnerError("arm requires source modalities")
        if self.partition_id not in {"coarse", "completion_fine"}:
            raise PublicAVSixArmFieldRunnerError("invalid partition_id")
        if not isinstance(self.reverse_sequence_declaration, bool) or not isinstance(
            self.fresh_field_required,
            bool,
        ):
            raise PublicAVSixArmFieldRunnerError("arm flags must be boolean")
        if not self.fresh_field_required:
            raise PublicAVSixArmFieldRunnerError("every arm requires a fresh field")
        if not self.dock_geometry_digest or not self.field_parameter_contract:
            raise PublicAVSixArmFieldRunnerError("wiring requires field contracts")
        if not self.measured_roles:
            raise PublicAVSixArmFieldRunnerError("wiring requires measured roles")
        if self.executable:
            raise PublicAVSixArmFieldRunnerError("arm wiring cannot be executable")
        object.__setattr__(self, "included_modalities", modalities)
        object.__setattr__(
            self,
            "dock_geometry_digest",
            tuple(tuple(item) for item in self.dock_geometry_digest),
        )
        object.__setattr__(
            self,
            "field_parameter_contract",
            tuple(self.field_parameter_contract),
        )
        object.__setattr__(self, "measured_roles", tuple(self.measured_roles))


@dataclass(frozen=True, slots=True)
class PublicAVSixArmFieldRunnerWiring:
    runner_id: str
    preregistration_id: str
    source_id: str
    clock_id: str
    duration_limit_ticks: int
    auditory_input_digest: str
    visual_input_digest: str
    arms: tuple[PublicAVSixArmFieldArmWiring, ...]
    wiring_complete: bool
    all_arms_structurally_supported: bool
    implementation_allowed_for_wiring_only: bool
    executable: bool = False
    field_run_allowed: bool = False
    raw_payload_retained: bool = False
    metadata_used_by_field: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        if not self.runner_id or not self.preregistration_id or not self.source_id:
            raise PublicAVSixArmFieldRunnerError("technical identities are required")
        if self.duration_limit_ticks != 500_000_000:
            raise PublicAVSixArmFieldRunnerError("duration must remain fixed")
        arms = tuple(self.arms)
        if len(arms) != 6 or len({arm.arm_id for arm in arms}) != 6:
            raise PublicAVSixArmFieldRunnerError("runner wiring requires six unique arms")
        if not self.wiring_complete or not self.all_arms_structurally_supported:
            raise PublicAVSixArmFieldRunnerError("runner wiring requires supported arms")
        if not self.implementation_allowed_for_wiring_only:
            raise PublicAVSixArmFieldRunnerError("wiring implementation must be explicit")
        forbidden_flags = (
            "executable",
            "field_run_allowed",
            "raw_payload_retained",
            "metadata_used_by_field",
            "memory_claim_allowed",
            "meaning_claim_allowed",
            "organization_claim_allowed",
            "ai_claim_allowed",
        )
        if any(getattr(self, role) for role in forbidden_flags):
            raise PublicAVSixArmFieldRunnerError(
                "runner wiring cannot release execution, payloads, metadata, or claims"
            )
        object.__setattr__(self, "arms", arms)


def _arm_wiring(
    arm: PublicAVFieldArmPlan,
    audit: PublicAVFieldPathCompatibilityAudit,
    plan: PublicAVFieldPreregistration,
) -> PublicAVSixArmFieldArmWiring:
    compatible = next(item for item in audit.arms if item.arm_id == arm.arm_id)
    if not compatible.existing_runtime_accepts_arm:
        raise PublicAVSixArmFieldRunnerError(f"arm is not structurally supported: {arm.arm_id}")
    return PublicAVSixArmFieldArmWiring(
        arm_id=arm.arm_id,
        included_modalities=arm.included_modalities,
        partition_id=arm.partition_id,
        reverse_sequence_declaration=arm.reverse_sequence_declaration,
        fresh_field_required=arm.fresh_field_required,
        dock_geometry_digest=audit.dock_geometry_digest,
        field_parameter_contract=audit.field_parameter_contract,
        measured_roles=plan.measured_roles,
    )


def wire_public_av_six_arm_field_runner(
    compatibility_audit: PublicAVFieldPathCompatibilityAudit,
    preregistration: PublicAVFieldPreregistration | None = None,
) -> PublicAVSixArmFieldRunnerWiring:
    """Wire the corrected arms and keep the field run constructively blocked."""

    if not isinstance(compatibility_audit, PublicAVFieldPathCompatibilityAudit):
        raise PublicAVSixArmFieldRunnerError("compatibility audit is required")
    plan = preregistration or public_av_passive_field_preregistration()
    if not isinstance(plan, PublicAVFieldPreregistration):
        raise PublicAVSixArmFieldRunnerError("preregistration is required")
    if not compatibility_audit.all_preregistered_arms_representable_by_existing_runtime:
        raise PublicAVSixArmFieldRunnerError("all six arms must be structurally supported")
    if compatibility_audit.field_run_allowed or compatibility_audit.field_runner_implementation_allowed:
        raise PublicAVSixArmFieldRunnerError("compatibility audit cannot carry release flags")
    if plan.preregistration_id != compatibility_audit.preregistration_id:
        raise PublicAVSixArmFieldRunnerError("preregistration mismatch")
    if plan.source_id != compatibility_audit.source_id or plan.clock_id != compatibility_audit.clock_id:
        raise PublicAVSixArmFieldRunnerError("source or clock mismatch")
    arms = tuple(_arm_wiring(arm, compatibility_audit, plan) for arm in plan.arms)
    return PublicAVSixArmFieldRunnerWiring(
        runner_id="public.av.nasa-earthrise.passive-field.runner.wiring.v1",
        preregistration_id=plan.preregistration_id,
        source_id=plan.source_id,
        clock_id=plan.clock_id,
        duration_limit_ticks=plan.duration_limit_ticks,
        auditory_input_digest=plan.auditory_input_digest,
        visual_input_digest=plan.visual_input_digest,
        arms=arms,
        wiring_complete=True,
        all_arms_structurally_supported=True,
        implementation_allowed_for_wiring_only=True,
    )


def execute_public_av_six_arm_field_runner(
    wiring: PublicAVSixArmFieldRunnerWiring,
) -> None:
    """Deliberately blocked execution point for later explicit field-run release."""

    if not isinstance(wiring, PublicAVSixArmFieldRunnerWiring):
        raise PublicAVSixArmFieldRunnerError("runner wiring is required")
    raise PublicAVSixArmFieldRunnerError(
        "field execution is not released for the six-arm public AV runner"
    )


def public_av_six_arm_field_runner_json_value(
    wiring: PublicAVSixArmFieldRunnerWiring,
) -> dict:
    if not isinstance(wiring, PublicAVSixArmFieldRunnerWiring):
        raise PublicAVSixArmFieldRunnerError("runner wiring is required")

    def convert(value):
        if hasattr(value, "__dataclass_fields__"):
            return {
                role: convert(getattr(value, role))
                for role in value.__dataclass_fields__
            }
        if isinstance(value, tuple):
            return [convert(item) for item in value]
        return value

    return convert(wiring)


def public_av_six_arm_field_runner_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (PublicAVSixArmFieldArmWiring, PublicAVSixArmFieldRunnerWiring)
        for item in fields(cls)
    )
