"""Structural compatibility audit for the preregistered public AV field arms."""

from __future__ import annotations

from dataclasses import dataclass, fields

from .finite_audio_video_field_run import audio_video_dock_anatomies
from .log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from .public_av_field_preregistration import (
    PublicAVFieldArmPlan,
    PublicAVFieldPreregistration,
    public_av_passive_field_preregistration,
)
from .public_av_receptor_run import PublicAVReceptorRun
from .shared_mcm_field import ReceptorDockAnatomy


class PublicAVFieldPathCompatibilityError(ValueError):
    """Raised when a structural audit would cross into a field run."""


@dataclass(frozen=True, slots=True)
class PublicAVFieldArmCompatibility:
    arm_id: str
    included_modalities: tuple[str, ...]
    partition_id: str
    uses_identical_dock_geometry: bool
    uses_identical_field_parameters: bool
    can_supply_receptor_sequences: bool
    can_supply_proposal_steps: bool
    existing_runtime_accepts_arm: bool
    requires_synthetic_media: bool
    requires_special_rule: bool
    blocker: str

    def __post_init__(self) -> None:
        if not self.arm_id:
            raise PublicAVFieldPathCompatibilityError("arm_id must be non-empty")
        modalities = tuple(self.included_modalities)
        if any(item not in {"auditory", "visual"} for item in modalities):
            raise PublicAVFieldPathCompatibilityError("invalid modality")
        if self.partition_id not in {"coarse", "completion_fine"}:
            raise PublicAVFieldPathCompatibilityError("invalid partition_id")
        bool_roles = (
            "uses_identical_dock_geometry",
            "uses_identical_field_parameters",
            "can_supply_receptor_sequences",
            "can_supply_proposal_steps",
            "existing_runtime_accepts_arm",
            "requires_synthetic_media",
            "requires_special_rule",
        )
        if any(not isinstance(getattr(self, role), bool) for role in bool_roles):
            raise PublicAVFieldPathCompatibilityError("compatibility flags must be boolean")
        if self.existing_runtime_accepts_arm and (
            self.requires_synthetic_media or self.requires_special_rule or self.blocker
        ):
            raise PublicAVFieldPathCompatibilityError(
                "accepted arms cannot require synthetic media, special rules, or blockers"
            )
        if not self.existing_runtime_accepts_arm and not self.blocker:
            raise PublicAVFieldPathCompatibilityError("blocked arms require a blocker")
        object.__setattr__(self, "included_modalities", modalities)


@dataclass(frozen=True, slots=True)
class PublicAVFieldPathCompatibilityAudit:
    preregistration_id: str
    source_id: str
    clock_id: str
    duration_limit_ticks: int
    auditory_geometry_id: str
    visual_geometry_id: str
    dock_geometry_digest: tuple[tuple[str, str, int], ...]
    field_parameter_contract: tuple[str, ...]
    arms: tuple[PublicAVFieldArmCompatibility, ...]
    all_preregistered_arms_representable_by_existing_runtime: bool
    single_modality_arms_supported: bool
    field_runner_implementation_allowed: bool = False
    field_run_allowed: bool = False
    synthetic_media_introduced: bool = False
    special_rules_introduced: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        if not self.preregistration_id or not self.source_id or not self.clock_id:
            raise PublicAVFieldPathCompatibilityError("technical identities are required")
        if self.duration_limit_ticks != 500_000_000:
            raise PublicAVFieldPathCompatibilityError("duration must remain fixed")
        arms = tuple(self.arms)
        if len(arms) != 6 or len({arm.arm_id for arm in arms}) != 6:
            raise PublicAVFieldPathCompatibilityError("exactly six arm audits are required")
        release_flags = (
            "field_runner_implementation_allowed",
            "field_run_allowed",
            "synthetic_media_introduced",
            "special_rules_introduced",
            "memory_claim_allowed",
            "meaning_claim_allowed",
            "organization_claim_allowed",
            "ai_claim_allowed",
        )
        if any(getattr(self, role) for role in release_flags):
            raise PublicAVFieldPathCompatibilityError(
                "compatibility audit cannot release runs, claims, or special inputs"
            )
        expected_all = all(arm.existing_runtime_accepts_arm for arm in arms)
        if self.all_preregistered_arms_representable_by_existing_runtime != expected_all:
            raise PublicAVFieldPathCompatibilityError("aggregate arm compatibility mismatch")
        single = all(
            arm.existing_runtime_accepts_arm
            for arm in arms
            if arm.arm_id in {"auditory_only.fine", "visual_only.fine"}
        )
        if self.single_modality_arms_supported != single:
            raise PublicAVFieldPathCompatibilityError("single modality aggregate mismatch")
        object.__setattr__(self, "arms", arms)
        object.__setattr__(self, "dock_geometry_digest", tuple(self.dock_geometry_digest))
        object.__setattr__(
            self,
            "field_parameter_contract",
            tuple(self.field_parameter_contract),
        )


def _dock_geometry_digest(
    anatomies: dict[str, ReceptorDockAnatomy],
) -> tuple[tuple[str, str, int], ...]:
    return tuple(
        sorted(
            (
                modality_id,
                anatomy.dock_id,
                len(anatomy.positions),
            )
            for modality_id, anatomy in anatomies.items()
        )
    )


def _arm_compatibility(
    arm: PublicAVFieldArmPlan,
    *,
    shared_dock_modalities: set[str],
) -> PublicAVFieldArmCompatibility:
    modalities = tuple(arm.included_modalities)
    uses_identical_dock_geometry = shared_dock_modalities == {"auditory", "visual"}
    uses_identical_field_parameters = arm.fresh_field_required
    can_supply_receptor_sequences = bool(modalities)
    can_supply_proposal_steps = arm.partition_id in {"coarse", "completion_fine"}
    requires_synthetic_media = False
    if not modalities:
        existing_runtime_accepts_arm = False
        requires_special_rule = True
        blocker = (
            "existing neutral asynchronous runtime requires at least one receptor "
            "sequence and positive source support"
        )
    else:
        existing_runtime_accepts_arm = (
            uses_identical_dock_geometry
            and uses_identical_field_parameters
            and can_supply_receptor_sequences
            and can_supply_proposal_steps
        )
        requires_special_rule = False
        blocker = "" if existing_runtime_accepts_arm else "arm contract mismatch"
    return PublicAVFieldArmCompatibility(
        arm_id=arm.arm_id,
        included_modalities=modalities,
        partition_id=arm.partition_id,
        uses_identical_dock_geometry=uses_identical_dock_geometry,
        uses_identical_field_parameters=uses_identical_field_parameters,
        can_supply_receptor_sequences=can_supply_receptor_sequences,
        can_supply_proposal_steps=can_supply_proposal_steps,
        existing_runtime_accepts_arm=existing_runtime_accepts_arm,
        requires_synthetic_media=requires_synthetic_media,
        requires_special_rule=requires_special_rule,
        blocker=blocker,
    )


def audit_public_av_field_path_compatibility(
    receptor_run: PublicAVReceptorRun,
    preregistration: PublicAVFieldPreregistration | None = None,
    auditory_config: LogSpectralConfig = LogSpectralConfig(),
) -> PublicAVFieldPathCompatibilityAudit:
    """Audit only structural compatibility; never build or advance a field."""

    if not isinstance(receptor_run, PublicAVReceptorRun):
        raise PublicAVFieldPathCompatibilityError("receptor run result is required")
    plan = preregistration or public_av_passive_field_preregistration()
    if not isinstance(plan, PublicAVFieldPreregistration):
        raise PublicAVFieldPathCompatibilityError("preregistration is required")
    if receptor_run.source_id != plan.source_id:
        raise PublicAVFieldPathCompatibilityError("source_id mismatch")
    if receptor_run.clock_id != plan.clock_id:
        raise PublicAVFieldPathCompatibilityError("clock_id mismatch")
    if receptor_run.duration_limit_ticks != plan.duration_limit_ticks:
        raise PublicAVFieldPathCompatibilityError("duration mismatch")
    if receptor_run.auditory_sequence_digest != plan.auditory_input_digest:
        raise PublicAVFieldPathCompatibilityError("auditory input digest mismatch")
    if receptor_run.visual_sequence_digest != plan.visual_input_digest:
        raise PublicAVFieldPathCompatibilityError("visual input digest mismatch")

    auditory_carrier_count = len(LogSpectralReceptor(auditory_config).channel_ids)
    anatomies = audio_video_dock_anatomies(
        auditory_carrier_count=auditory_carrier_count,
        visual_grid_columns=10,
        visual_grid_rows=8,
    )
    dock_digest = _dock_geometry_digest(anatomies)
    shared_modalities = set(anatomies)
    arm_audits = tuple(
        _arm_compatibility(arm, shared_dock_modalities=shared_modalities)
        for arm in plan.arms
    )
    return PublicAVFieldPathCompatibilityAudit(
        preregistration_id=plan.preregistration_id,
        source_id=plan.source_id,
        clock_id=plan.clock_id,
        duration_limit_ticks=plan.duration_limit_ticks,
        auditory_geometry_id=receptor_run.auditory_geometry_id,
        visual_geometry_id=receptor_run.visual_geometry_id,
        dock_geometry_digest=dock_digest,
        field_parameter_contract=(
            "fresh_shared_field_per_arm",
            "neutral_local_field_substrate_config_1.0",
            "neutral_fast_afterimage_config_0.5",
            "orthogonal_field_sample_offsets",
        ),
        arms=arm_audits,
        all_preregistered_arms_representable_by_existing_runtime=all(
            arm.existing_runtime_accepts_arm for arm in arm_audits
        ),
        single_modality_arms_supported=all(
            arm.existing_runtime_accepts_arm
            for arm in arm_audits
            if arm.arm_id in {"auditory_only.fine", "visual_only.fine"}
        ),
    )


def public_av_field_path_compatibility_json_value(
    audit: PublicAVFieldPathCompatibilityAudit,
) -> dict:
    if not isinstance(audit, PublicAVFieldPathCompatibilityAudit):
        raise PublicAVFieldPathCompatibilityError("compatibility audit is required")

    def convert(value):
        if hasattr(value, "__dataclass_fields__"):
            return {
                role: convert(getattr(value, role))
                for role in value.__dataclass_fields__
            }
        if isinstance(value, tuple):
            return [convert(item) for item in value]
        return value

    return convert(audit)


def public_av_field_path_compatibility_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (PublicAVFieldArmCompatibility, PublicAVFieldPathCompatibilityAudit)
        for item in fields(cls)
    )
