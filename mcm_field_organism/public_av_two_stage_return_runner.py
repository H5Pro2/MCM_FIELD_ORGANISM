"""Non-executable wiring for the preregistered public AV world return."""

from __future__ import annotations

from dataclasses import dataclass, fields

from .public_av_two_stage_return_preregistration import (
    PublicAVTwoStageReturnPreregistration,
    public_av_two_stage_return_preregistration,
)


class PublicAVTwoStageReturnRunnerError(ValueError):
    """Raised when return-run wiring would authorize execution or claims."""


@dataclass(frozen=True, slots=True)
class PublicAVTwoStageReturnArmWiring:
    arm_id: str
    stage_one_sequence_id: str
    stage_two_sequence_id: str
    stage_one_interval_ticks: tuple[int, int]
    resolution_interval_ticks: tuple[int, int]
    stage_two_interval_ticks: tuple[int, int]
    stage_two_tick_offset: int
    carry_field_state_to_stage_two: bool
    fresh_field_before_stage_two: bool
    resolution_phase: str
    measured_roles: tuple[str, ...]
    executable: bool = False

    def __post_init__(self) -> None:
        if self.arm_id not in {"continued_field", "fresh_stage_two_baseline"}:
            raise PublicAVTwoStageReturnRunnerError("invalid return arm")
        expected_sequence = "public.av.nasa-earthrise.0p5s.reduced.v1"
        if self.stage_one_sequence_id != expected_sequence or self.stage_two_sequence_id != expected_sequence:
            raise PublicAVTwoStageReturnRunnerError("both stages require the audited sequence")
        if self.stage_one_interval_ticks != (0, 500_000_000):
            raise PublicAVTwoStageReturnRunnerError("stage-one interval must remain fixed")
        if self.resolution_interval_ticks != (500_000_000, 600_000_000):
            raise PublicAVTwoStageReturnRunnerError("resolution interval must remain fixed")
        if self.stage_two_interval_ticks != (600_000_000, 1_100_000_000):
            raise PublicAVTwoStageReturnRunnerError("stage-two interval must remain fixed")
        if self.stage_two_tick_offset != 600_000_000:
            raise PublicAVTwoStageReturnRunnerError("stage-two time shift must remain fixed")
        if self.carry_field_state_to_stage_two == self.fresh_field_before_stage_two:
            raise PublicAVTwoStageReturnRunnerError("exactly one stage-two state mode is required")
        if self.arm_id == "continued_field" and not self.carry_field_state_to_stage_two:
            raise PublicAVTwoStageReturnRunnerError("continued arm must carry field state")
        if self.arm_id == "fresh_stage_two_baseline" and not self.fresh_field_before_stage_two:
            raise PublicAVTwoStageReturnRunnerError("baseline arm must start stage two fresh")
        if self.resolution_phase != "no_input_gap.step_time_only":
            raise PublicAVTwoStageReturnRunnerError("resolution phase must remain fixed")
        if not self.measured_roles or self.executable:
            raise PublicAVTwoStageReturnRunnerError("arm wiring cannot be executable or unmeasured")
        object.__setattr__(self, "measured_roles", tuple(self.measured_roles))


@dataclass(frozen=True, slots=True)
class PublicAVTwoStageReturnRunnerWiring:
    runner_id: str
    preregistration_id: str
    source_id: str
    clock_id: str
    stage_sequence_digest: tuple[str, str]
    arms: tuple[PublicAVTwoStageReturnArmWiring, ...]
    fixed_field_parameters: tuple[str, ...]
    required_invariants: tuple[str, ...]
    wiring_complete: bool
    stage_two_time_shift_fixed: bool
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
        if not self.runner_id or not self.preregistration_id or not self.source_id or not self.clock_id:
            raise PublicAVTwoStageReturnRunnerError("technical identities are required")
        arms = tuple(self.arms)
        if {arm.arm_id for arm in arms} != {"continued_field", "fresh_stage_two_baseline"}:
            raise PublicAVTwoStageReturnRunnerError("exactly two return arms are required")
        if not self.wiring_complete or not self.stage_two_time_shift_fixed:
            raise PublicAVTwoStageReturnRunnerError("complete fixed-time wiring is required")
        if not self.implementation_allowed_for_wiring_only:
            raise PublicAVTwoStageReturnRunnerError("wiring-only authorization is required")
        forbidden = (
            "executable", "field_run_allowed", "raw_payload_retained", "metadata_used_by_field",
            "memory_claim_allowed", "meaning_claim_allowed", "organization_claim_allowed", "ai_claim_allowed",
        )
        if any(getattr(self, role) for role in forbidden):
            raise PublicAVTwoStageReturnRunnerError("runner wiring cannot release execution, data, or claims")
        object.__setattr__(self, "arms", arms)
        object.__setattr__(self, "stage_sequence_digest", tuple(self.stage_sequence_digest))
        object.__setattr__(self, "fixed_field_parameters", tuple(self.fixed_field_parameters))
        object.__setattr__(self, "required_invariants", tuple(self.required_invariants))


def wire_public_av_two_stage_return_runner(
    preregistration: PublicAVTwoStageReturnPreregistration | None = None,
) -> PublicAVTwoStageReturnRunnerWiring:
    plan = preregistration or public_av_two_stage_return_preregistration()
    if not isinstance(plan, PublicAVTwoStageReturnPreregistration):
        raise PublicAVTwoStageReturnRunnerError("two-stage preregistration is required")
    arms = tuple(
        PublicAVTwoStageReturnArmWiring(
            arm_id=arm.arm_id,
            stage_one_sequence_id=arm.stage_one_sequence_id,
            stage_two_sequence_id=arm.stage_two_sequence_id,
            stage_one_interval_ticks=(0, plan.stage_duration_ticks),
            resolution_interval_ticks=(plan.stage_duration_ticks, plan.stage_duration_ticks + arm.intermediate_interval_ticks),
            stage_two_interval_ticks=(
                plan.stage_duration_ticks + arm.intermediate_interval_ticks,
                2 * plan.stage_duration_ticks + arm.intermediate_interval_ticks,
            ),
            stage_two_tick_offset=plan.stage_duration_ticks + arm.intermediate_interval_ticks,
            carry_field_state_to_stage_two=arm.carry_field_state_to_stage_two,
            fresh_field_before_stage_two=arm.fresh_field_before_stage_two,
            resolution_phase=arm.resolution_phase,
            measured_roles=plan.measured_roles,
        )
        for arm in plan.arms
    )
    return PublicAVTwoStageReturnRunnerWiring(
        runner_id="public.av.nasa-earthrise.two-stage-return.runner.wiring.v1",
        preregistration_id=plan.preregistration_id,
        source_id=plan.source_id,
        clock_id=plan.clock_id,
        stage_sequence_digest=plan.stage_sequence_digest,
        arms=arms,
        fixed_field_parameters=plan.fixed_field_parameters,
        required_invariants=plan.required_invariants,
        wiring_complete=True,
        stage_two_time_shift_fixed=True,
        implementation_allowed_for_wiring_only=True,
    )


def execute_public_av_two_stage_return_runner(wiring: PublicAVTwoStageReturnRunnerWiring) -> None:
    if not isinstance(wiring, PublicAVTwoStageReturnRunnerWiring):
        raise PublicAVTwoStageReturnRunnerError("runner wiring is required")
    raise PublicAVTwoStageReturnRunnerError("field execution is not released for the two-stage return runner")


def public_av_two_stage_return_runner_json_value(wiring: PublicAVTwoStageReturnRunnerWiring) -> dict:
    if not isinstance(wiring, PublicAVTwoStageReturnRunnerWiring):
        raise PublicAVTwoStageReturnRunnerError("runner wiring is required")

    def convert(value):
        if hasattr(value, "__dataclass_fields__"):
            return {role: convert(getattr(value, role)) for role in value.__dataclass_fields__}
        if isinstance(value, tuple):
            return [convert(item) for item in value]
        return value

    return convert(wiring)


def public_av_two_stage_return_runner_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (PublicAVTwoStageReturnArmWiring, PublicAVTwoStageReturnRunnerWiring)
        for item in fields(cls)
    )
