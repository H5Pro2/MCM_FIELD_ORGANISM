"""Execution preflight for one bounded public AV two-stage return run."""

from __future__ import annotations

from dataclasses import dataclass, fields
from pathlib import Path

from .public_av_container_source import PUBLIC_MEDIA_CLOCK_ID
from .public_av_no_input_gap_audit import (
    PublicAVNoInputGapAudit,
    audit_public_av_no_input_gap_step_time,
)
from .public_av_two_stage_return_preregistration import (
    public_av_two_stage_return_preregistration,
)
from .public_av_two_stage_return_runner import (
    PublicAVTwoStageReturnRunnerWiring,
    wire_public_av_two_stage_return_runner,
)
from .public_media_source_contract import (
    PublicMediaSourceAudit,
    PublicMediaSourceContract,
    audit_public_media_source,
    nasa_earthrise_av_source_contract,
)


class PublicAVTwoStageReturnPreflightError(ValueError):
    """Raised when the two-stage run preflight would exceed its release boundary."""


@dataclass(frozen=True, slots=True)
class PublicAVTwoStageReturnPreflight:
    preflight_id: str
    source_id: str
    media_path: str
    source_audit_accepted: bool
    source_size_matches: bool
    source_sha1_matches: bool
    runner_id_matches_gap_audit: bool
    preregistration_id_matches: bool
    source_id_matches_contracts: bool
    clock_id_matches: bool
    stage_one_interval_ticks: tuple[int, int]
    resolution_interval_ticks: tuple[int, int]
    stage_two_interval_ticks: tuple[int, int]
    intervals_fixed: bool
    gap_audit_complete: bool
    no_input_gap_contact_free: bool
    fixed_field_parameters_match_preregistration: bool
    field_parameter_roles: tuple[str, ...]
    single_bounded_run_release_granted: bool
    release_scope: str
    field_run_started: bool = False
    raw_payload_retained: bool = False
    metadata_used_by_field: bool = False
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
            raise PublicAVTwoStageReturnPreflightError("fixed run intervals are required")
        required = (
            self.source_audit_accepted,
            self.source_size_matches,
            self.source_sha1_matches,
            self.runner_id_matches_gap_audit,
            self.preregistration_id_matches,
            self.source_id_matches_contracts,
            self.clock_id_matches,
            self.gap_audit_complete,
            self.no_input_gap_contact_free,
            self.fixed_field_parameters_match_preregistration,
        )
        if self.single_bounded_run_release_granted != all(required):
            raise PublicAVTwoStageReturnPreflightError(
                "single-run release must exactly follow the preflight gate"
            )
        if self.release_scope != "one_public_av_two_stage_return_run_0p5s_plus_0p1s_gap":
            raise PublicAVTwoStageReturnPreflightError("release scope changed")
        forbidden = (
            self.field_run_started,
            self.raw_payload_retained,
            self.metadata_used_by_field,
            self.memory_claim_allowed,
            self.meaning_claim_allowed,
            self.organization_claim_allowed,
            self.ai_claim_allowed,
        )
        if any(forbidden):
            raise PublicAVTwoStageReturnPreflightError(
                "preflight cannot start a run, retain payloads, or release claims"
            )
        object.__setattr__(self, "stage_one_interval_ticks", tuple(self.stage_one_interval_ticks))
        object.__setattr__(self, "resolution_interval_ticks", tuple(self.resolution_interval_ticks))
        object.__setattr__(self, "stage_two_interval_ticks", tuple(self.stage_two_interval_ticks))
        object.__setattr__(self, "field_parameter_roles", tuple(self.field_parameter_roles))


def audit_public_av_two_stage_return_preflight(
    path: Path,
    contract: PublicMediaSourceContract | None = None,
    *,
    source_audit: PublicMediaSourceAudit | None = None,
    wiring: PublicAVTwoStageReturnRunnerWiring | None = None,
    gap_audit: PublicAVNoInputGapAudit | None = None,
) -> PublicAVTwoStageReturnPreflight:
    """Audit source and contracts before exactly one bounded two-stage run."""

    if not isinstance(path, Path):
        raise PublicAVTwoStageReturnPreflightError("path must be a pathlib.Path")
    plan = public_av_two_stage_return_preregistration()
    source_contract = contract or nasa_earthrise_av_source_contract()
    if not isinstance(source_contract, PublicMediaSourceContract):
        raise PublicAVTwoStageReturnPreflightError("source contract is required")
    observed_source = source_audit or audit_public_media_source(path, source_contract)
    if not isinstance(observed_source, PublicMediaSourceAudit):
        raise PublicAVTwoStageReturnPreflightError("source audit is required")

    runner = wiring or wire_public_av_two_stage_return_runner(plan)
    if not isinstance(runner, PublicAVTwoStageReturnRunnerWiring):
        raise PublicAVTwoStageReturnPreflightError("runner wiring is required")
    gap = gap_audit or audit_public_av_no_input_gap_step_time(runner)
    if not isinstance(gap, PublicAVNoInputGapAudit):
        raise PublicAVTwoStageReturnPreflightError("gap audit is required")

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
    gate_conditions = (
        observed_source.accepted,
        observed_source.size_matches,
        observed_source.sha1_matches,
        gap.runner_id == runner.runner_id,
        runner.preregistration_id == plan.preregistration_id
        and gap.preregistration_id == plan.preregistration_id,
        source_contract.source_id == plan.source_id
        and observed_source.source_id == plan.source_id
        and runner.source_id == plan.source_id,
        plan.clock_id == PUBLIC_MEDIA_CLOCK_ID
        and runner.clock_id == plan.clock_id
        and gap.clock_id == plan.clock_id,
        gap.audit_complete,
        gap.contact_free_distribution_contact_count == 0
        and gap.lower_contact_free_field_step_available
        and not gap.artificial_receptor_events_introduced,
        fixed_parameters,
    )
    release_granted = all(gate_conditions)
    return PublicAVTwoStageReturnPreflight(
        preflight_id="public.av.nasa-earthrise.two-stage-return.preflight.v1",
        source_id=plan.source_id,
        media_path=str(path),
        source_audit_accepted=observed_source.accepted,
        source_size_matches=observed_source.size_matches,
        source_sha1_matches=observed_source.sha1_matches,
        runner_id_matches_gap_audit=gap.runner_id == runner.runner_id,
        preregistration_id_matches=(
            runner.preregistration_id == plan.preregistration_id
            and gap.preregistration_id == plan.preregistration_id
        ),
        source_id_matches_contracts=(
            source_contract.source_id == plan.source_id
            and observed_source.source_id == plan.source_id
            and runner.source_id == plan.source_id
        ),
        clock_id_matches=(
            plan.clock_id == PUBLIC_MEDIA_CLOCK_ID
            and runner.clock_id == plan.clock_id
            and gap.clock_id == plan.clock_id
        ),
        stage_one_interval_ticks=stage_one,
        resolution_interval_ticks=resolution,
        stage_two_interval_ticks=stage_two,
        intervals_fixed=True,
        gap_audit_complete=gap.audit_complete,
        no_input_gap_contact_free=(
            gap.contact_free_distribution_contact_count == 0
            and gap.lower_contact_free_field_step_available
            and not gap.artificial_receptor_events_introduced
        ),
        fixed_field_parameters_match_preregistration=fixed_parameters,
        field_parameter_roles=runner.fixed_field_parameters,
        single_bounded_run_release_granted=release_granted,
        release_scope="one_public_av_two_stage_return_run_0p5s_plus_0p1s_gap",
    )


def public_av_two_stage_return_preflight_json_value(
    preflight: PublicAVTwoStageReturnPreflight,
) -> dict[str, object]:
    if not isinstance(preflight, PublicAVTwoStageReturnPreflight):
        raise PublicAVTwoStageReturnPreflightError("two-stage return preflight is required")
    return {
        role: list(value) if isinstance(value, tuple) else value
        for role, value in (
            (item.name, getattr(preflight, item.name))
            for item in fields(preflight)
        )
    }


def public_av_two_stage_return_preflight_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(PublicAVTwoStageReturnPreflight))
