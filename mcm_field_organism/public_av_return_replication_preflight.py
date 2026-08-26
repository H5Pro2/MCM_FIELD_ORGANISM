"""Execution preflight for one bounded six-arm public AV return replication."""

from __future__ import annotations

from dataclasses import dataclass, fields
from pathlib import Path

from .public_av_container_source import PUBLIC_MEDIA_CLOCK_ID
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
from .public_av_return_replication_runner import (
    PublicAVReturnReplicationRunnerWiring,
    wire_public_av_return_replication_runner,
)
from .public_media_source_contract import (
    PublicMediaSourceAudit,
    PublicMediaSourceContract,
    audit_public_media_source,
    nasa_earthrise_av_source_contract,
)


class PublicAVReturnReplicationPreflightError(ValueError):
    """Raised when the six-arm replication preflight exceeds its boundary."""


@dataclass(frozen=True, slots=True)
class PublicAVReturnReplicationPreflight:
    preflight_id: str
    source_id: str
    media_path: str
    source_audit_accepted: bool
    source_size_matches: bool
    source_sha1_matches: bool
    preregistration_id_matches: bool
    compatibility_audit_id_matches: bool
    permutation_contract_id_matches: bool
    permutation_contract_digest_matches: bool
    source_id_matches_contracts: bool
    clock_id_matches: bool
    arm_count: int
    arm_ids_complete: bool
    all_arms_wired: bool
    all_arms_structurally_supported: bool
    stage_one_interval_ticks: tuple[int, int]
    resolution_interval_ticks: tuple[int, int]
    stage_two_interval_ticks: tuple[int, int]
    intervals_fixed: bool
    fixed_field_parameters_match_preregistration: bool
    field_parameter_roles: tuple[str, ...]
    runner_wiring_non_executable: bool
    runner_run_lock_engaged: bool
    compatibility_run_lock_engaged: bool
    media_decode_allowed: bool
    receptor_feed_allowed: bool
    single_bounded_replication_run_release_granted: bool
    repeat_count_authorized: int
    release_scope: str
    field_run_started: bool = False
    raw_payload_retained: bool = False
    metadata_used_by_field: bool = False
    memory_threshold_defined: bool = False
    organization_threshold_defined: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        expected_intervals = (
            self.stage_one_interval_ticks == (0, 500_000_000)
            and self.resolution_interval_ticks == (500_000_000, 600_000_000)
            and self.stage_two_interval_ticks == (600_000_000, 1_100_000_000)
        )
        if self.intervals_fixed != expected_intervals or not expected_intervals:
            raise PublicAVReturnReplicationPreflightError("fixed replication intervals are required")
        if self.arm_count != 6 or not self.arm_ids_complete or not self.all_arms_wired:
            raise PublicAVReturnReplicationPreflightError("six complete replication arms are required")
        required = (
            self.source_audit_accepted,
            self.source_size_matches,
            self.source_sha1_matches,
            self.preregistration_id_matches,
            self.compatibility_audit_id_matches,
            self.permutation_contract_id_matches,
            self.permutation_contract_digest_matches,
            self.source_id_matches_contracts,
            self.clock_id_matches,
            self.all_arms_structurally_supported,
            self.fixed_field_parameters_match_preregistration,
            self.runner_wiring_non_executable,
            self.runner_run_lock_engaged,
            self.compatibility_run_lock_engaged,
            not self.media_decode_allowed,
            not self.receptor_feed_allowed,
        )
        if self.single_bounded_replication_run_release_granted != all(required):
            raise PublicAVReturnReplicationPreflightError(
                "single replication release must exactly follow the preflight gate"
            )
        if self.repeat_count_authorized != 1:
            raise PublicAVReturnReplicationPreflightError("exactly one replication run can be authorized")
        if self.release_scope != "one_public_av_six_arm_return_replication_0p5s_plus_0p1s_gap":
            raise PublicAVReturnReplicationPreflightError("release scope changed")
        forbidden = (
            self.field_run_started,
            self.raw_payload_retained,
            self.metadata_used_by_field,
            self.memory_threshold_defined,
            self.organization_threshold_defined,
            self.memory_claim_allowed,
            self.meaning_claim_allowed,
            self.organization_claim_allowed,
            self.ai_claim_allowed,
        )
        if any(forbidden):
            raise PublicAVReturnReplicationPreflightError(
                "preflight cannot start a run, retain payloads, define thresholds, or release claims"
            )
        object.__setattr__(self, "stage_one_interval_ticks", tuple(self.stage_one_interval_ticks))
        object.__setattr__(self, "resolution_interval_ticks", tuple(self.resolution_interval_ticks))
        object.__setattr__(self, "stage_two_interval_ticks", tuple(self.stage_two_interval_ticks))
        object.__setattr__(self, "field_parameter_roles", tuple(self.field_parameter_roles))


def audit_public_av_return_replication_preflight(
    path: Path,
    contract: PublicMediaSourceContract | None = None,
    *,
    source_audit: PublicMediaSourceAudit | None = None,
    preregistration: PublicAVReturnReplicationPreregistration | None = None,
    compatibility_audit: PublicAVReturnReplicationCompatibilityAudit | None = None,
    permutation_contract: PublicAVReturnPermutationContract | None = None,
    wiring: PublicAVReturnReplicationRunnerWiring | None = None,
) -> PublicAVReturnReplicationPreflight:
    """Audit source and contracts before exactly one six-arm replication run."""

    if not isinstance(path, Path):
        raise PublicAVReturnReplicationPreflightError("path must be a pathlib.Path")
    plan = preregistration or public_av_return_replication_preregistration()
    if not isinstance(plan, PublicAVReturnReplicationPreregistration):
        raise PublicAVReturnReplicationPreflightError("replication preregistration is required")
    source_contract = contract or nasa_earthrise_av_source_contract()
    if not isinstance(source_contract, PublicMediaSourceContract):
        raise PublicAVReturnReplicationPreflightError("source contract is required")
    observed_source = source_audit or audit_public_media_source(path, source_contract)
    if not isinstance(observed_source, PublicMediaSourceAudit):
        raise PublicAVReturnReplicationPreflightError("source audit is required")
    perm_contract = permutation_contract or public_av_return_permutation_contract(plan)
    if not isinstance(perm_contract, PublicAVReturnPermutationContract):
        raise PublicAVReturnReplicationPreflightError("permutation contract is required")
    compatibility = compatibility_audit or audit_public_av_return_replication_compatibility(
        plan,
        perm_contract,
    )
    if not isinstance(compatibility, PublicAVReturnReplicationCompatibilityAudit):
        raise PublicAVReturnReplicationPreflightError("compatibility audit is required")
    runner = wiring or wire_public_av_return_replication_runner(
        compatibility,
        plan,
        perm_contract,
    )
    if not isinstance(runner, PublicAVReturnReplicationRunnerWiring):
        raise PublicAVReturnReplicationPreflightError("runner wiring is required")

    expected_arm_ids = {arm.arm_id for arm in plan.arms}
    wired_arm_ids = {arm.arm_id for arm in runner.arms}
    arm_intervals = {
        (
            arm.stage_one_interval_ticks,
            arm.resolution_interval_ticks,
            arm.stage_two_interval_ticks,
        )
        for arm in runner.arms
    }
    intervals = next(iter(arm_intervals)) if len(arm_intervals) == 1 else ((), (), ())
    stage_one, resolution, stage_two = intervals
    fixed_parameters = (
        runner.fixed_field_parameters == plan.fixed_field_parameters
        and "neutral_local_field_substrate_config_1.0" in runner.fixed_field_parameters
        and "neutral_fast_afterimage_config_0.5" in runner.fixed_field_parameters
        and "orthogonal_field_sample_offsets" in runner.fixed_field_parameters
        and "identical_audio_video_dock_geometry" in runner.fixed_field_parameters
    )
    return PublicAVReturnReplicationPreflight(
        preflight_id="public.av.nasa-earthrise.return-replication.preflight.v1",
        source_id=plan.source_id,
        media_path=str(path),
        source_audit_accepted=observed_source.accepted,
        source_size_matches=observed_source.size_matches,
        source_sha1_matches=observed_source.sha1_matches,
        preregistration_id_matches=(
            runner.preregistration_id == plan.preregistration_id
            and compatibility.preregistration_id == plan.preregistration_id
            and perm_contract.preregistration_id == plan.preregistration_id
        ),
        compatibility_audit_id_matches=runner.compatibility_audit_id == compatibility.audit_id,
        permutation_contract_id_matches=runner.permutation_contract_id == perm_contract.contract_id,
        permutation_contract_digest_matches=runner.permutation_contract_digest == perm_contract.contract_digest,
        source_id_matches_contracts=(
            source_contract.source_id == plan.source_id
            and observed_source.source_id == plan.source_id
            and compatibility.source_id == plan.source_id
            and runner.source_id == plan.source_id
        ),
        clock_id_matches=(
            plan.clock_id == PUBLIC_MEDIA_CLOCK_ID
            and compatibility.clock_id == plan.clock_id
            and runner.clock_id == plan.clock_id
        ),
        arm_count=len(runner.arms),
        arm_ids_complete=wired_arm_ids == expected_arm_ids,
        all_arms_wired=len(runner.arms) == 6 and len(wired_arm_ids) == 6,
        all_arms_structurally_supported=(
            compatibility.all_preregistered_arms_supported
            and runner.all_arms_structurally_supported
        ),
        stage_one_interval_ticks=stage_one,
        resolution_interval_ticks=resolution,
        stage_two_interval_ticks=stage_two,
        intervals_fixed=True,
        fixed_field_parameters_match_preregistration=fixed_parameters,
        field_parameter_roles=runner.fixed_field_parameters,
        runner_wiring_non_executable=not runner.executable,
        runner_run_lock_engaged=(
            not runner.replication_run_allowed
            and not runner.media_decode_allowed
            and not runner.receptor_feed_allowed
        ),
        compatibility_run_lock_engaged=not compatibility.replication_run_allowed,
        media_decode_allowed=False,
        receptor_feed_allowed=False,
        single_bounded_replication_run_release_granted=(
            observed_source.accepted
            and observed_source.size_matches
            and observed_source.sha1_matches
            and runner.preregistration_id == plan.preregistration_id
            and compatibility.preregistration_id == plan.preregistration_id
            and perm_contract.preregistration_id == plan.preregistration_id
            and runner.compatibility_audit_id == compatibility.audit_id
            and runner.permutation_contract_id == perm_contract.contract_id
            and runner.permutation_contract_digest == perm_contract.contract_digest
            and source_contract.source_id == plan.source_id
            and observed_source.source_id == plan.source_id
            and compatibility.source_id == plan.source_id
            and runner.source_id == plan.source_id
            and plan.clock_id == PUBLIC_MEDIA_CLOCK_ID
            and compatibility.clock_id == plan.clock_id
            and runner.clock_id == plan.clock_id
            and wired_arm_ids == expected_arm_ids
            and len(runner.arms) == 6
            and len(wired_arm_ids) == 6
            and compatibility.all_preregistered_arms_supported
            and runner.all_arms_structurally_supported
            and fixed_parameters
            and not runner.executable
            and not runner.replication_run_allowed
            and not runner.media_decode_allowed
            and not runner.receptor_feed_allowed
            and not compatibility.replication_run_allowed
        ),
        repeat_count_authorized=1,
        release_scope="one_public_av_six_arm_return_replication_0p5s_plus_0p1s_gap",
    )


def public_av_return_replication_preflight_json_value(
    preflight: PublicAVReturnReplicationPreflight,
) -> dict[str, object]:
    if not isinstance(preflight, PublicAVReturnReplicationPreflight):
        raise PublicAVReturnReplicationPreflightError("replication preflight is required")
    return {
        role: list(value) if isinstance(value, tuple) else value
        for role, value in (
            (item.name, getattr(preflight, item.name))
            for item in fields(preflight)
        )
    }


def public_av_return_replication_preflight_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(PublicAVReturnReplicationPreflight))
