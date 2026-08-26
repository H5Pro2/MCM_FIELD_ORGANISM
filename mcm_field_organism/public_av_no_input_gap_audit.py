"""Structural audit for the public AV no-input resolution gap."""

from __future__ import annotations

from dataclasses import dataclass, fields

from .field_step_time import MCMFieldStepTime
from .receptor_contract import CommonFieldTime
from .receptor_distributor import ReceptorDistribution
from .public_av_two_stage_return_runner import (
    PublicAVTwoStageReturnRunnerWiring,
    wire_public_av_two_stage_return_runner,
)


class PublicAVNoInputGapAuditError(ValueError):
    """Raised when the no-input gap would need events, content, or a release."""


@dataclass(frozen=True, slots=True)
class PublicAVNoInputGapAudit:
    audit_id: str
    runner_id: str
    preregistration_id: str
    clock_id: str
    resolution_phase: str
    resolution_interval_ticks: tuple[int, int]
    resolution_duration_ticks: int
    contact_free_distribution_contact_count: int
    step_time_only_interval_matches: bool
    high_level_asynchronous_runtime_accepts_empty_sequence: bool
    lower_contact_free_field_step_available: bool
    uses_existing_neutral_fast_field_step: bool
    artificial_receptor_events_introduced: bool
    special_content_introduced: bool
    field_parameters_changed: bool
    runner_execution_allowed: bool
    field_run_allowed: bool
    audit_complete: bool
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        if self.resolution_phase != "no_input_gap.step_time_only":
            raise PublicAVNoInputGapAuditError("resolution phase must remain fixed")
        if self.resolution_interval_ticks != (500_000_000, 600_000_000):
            raise PublicAVNoInputGapAuditError("resolution interval must remain fixed")
        if self.resolution_duration_ticks != 100_000_000:
            raise PublicAVNoInputGapAuditError("resolution duration must remain fixed")
        if self.contact_free_distribution_contact_count != 0:
            raise PublicAVNoInputGapAuditError("no-input gap cannot contain contacts")
        if not self.step_time_only_interval_matches:
            raise PublicAVNoInputGapAuditError("gap step time must match distribution time")
        if self.high_level_asynchronous_runtime_accepts_empty_sequence:
            raise PublicAVNoInputGapAuditError(
                "high-level asynchronous runtime must not be treated as the gap path"
            )
        if not self.lower_contact_free_field_step_available:
            raise PublicAVNoInputGapAuditError("contact-free field step is not available")
        if not self.uses_existing_neutral_fast_field_step:
            raise PublicAVNoInputGapAuditError("audit requires the existing neutral fast field step")
        forbidden = (
            "artificial_receptor_events_introduced",
            "special_content_introduced",
            "field_parameters_changed",
            "runner_execution_allowed",
            "field_run_allowed",
            "memory_claim_allowed",
            "meaning_claim_allowed",
            "organization_claim_allowed",
            "ai_claim_allowed",
        )
        if any(getattr(self, role) for role in forbidden):
            raise PublicAVNoInputGapAuditError(
                "no-input gap audit cannot release execution, content, or claims"
            )
        if not self.audit_complete:
            raise PublicAVNoInputGapAuditError("audit must be complete")
        object.__setattr__(
            self,
            "resolution_interval_ticks",
            tuple(self.resolution_interval_ticks),
        )


def audit_public_av_no_input_gap_step_time(
    wiring: PublicAVTwoStageReturnRunnerWiring | None = None,
) -> PublicAVNoInputGapAudit:
    """Audit whether the two-stage resolution gap is structurally representable."""

    runner = wiring or wire_public_av_two_stage_return_runner()
    if not isinstance(runner, PublicAVTwoStageReturnRunnerWiring):
        raise PublicAVNoInputGapAuditError("two-stage runner wiring is required")
    if runner.executable or runner.field_run_allowed:
        raise PublicAVNoInputGapAuditError("runner must remain non-executable")

    intervals = {arm.resolution_interval_ticks for arm in runner.arms}
    phases = {arm.resolution_phase for arm in runner.arms}
    if intervals != {(500_000_000, 600_000_000)}:
        raise PublicAVNoInputGapAuditError("all arms must share the fixed gap interval")
    if phases != {"no_input_gap.step_time_only"}:
        raise PublicAVNoInputGapAuditError("all arms must share the fixed gap phase")

    start_tick, end_tick = (500_000_000, 600_000_000)
    field_time = CommonFieldTime(runner.clock_id, start_tick, end_tick)
    distribution = ReceptorDistribution(field_time, ())
    step_time = MCMFieldStepTime(runner.clock_id, start_tick, end_tick, 1_000_000_000)
    step_time_matches = (
        distribution.field_time.clock_id == step_time.clock_id
        and distribution.field_time.window_start_tick == step_time.start_tick
        and distribution.field_time.window_end_tick == step_time.end_tick
    )

    return PublicAVNoInputGapAudit(
        audit_id="public.av.nasa-earthrise.no-input-gap.audit.v1",
        runner_id=runner.runner_id,
        preregistration_id=runner.preregistration_id,
        clock_id=runner.clock_id,
        resolution_phase="no_input_gap.step_time_only",
        resolution_interval_ticks=(start_tick, end_tick),
        resolution_duration_ticks=end_tick - start_tick,
        contact_free_distribution_contact_count=len(distribution.contacts),
        step_time_only_interval_matches=step_time_matches,
        high_level_asynchronous_runtime_accepts_empty_sequence=False,
        lower_contact_free_field_step_available=True,
        uses_existing_neutral_fast_field_step=True,
        artificial_receptor_events_introduced=False,
        special_content_introduced=False,
        field_parameters_changed=False,
        runner_execution_allowed=False,
        field_run_allowed=False,
        audit_complete=True,
    )


def public_av_no_input_gap_audit_json_value(
    audit: PublicAVNoInputGapAudit,
) -> dict[str, object]:
    if not isinstance(audit, PublicAVNoInputGapAudit):
        raise PublicAVNoInputGapAuditError("no-input gap audit is required")
    return {
        role: list(value) if isinstance(value, tuple) else value
        for role, value in ((item.name, getattr(audit, item.name)) for item in fields(audit))
    }


def public_av_no_input_gap_audit_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(PublicAVNoInputGapAudit))
