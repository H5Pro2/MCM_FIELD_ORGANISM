"""Preregistration for a two-stage public AV world-return comparison."""

from __future__ import annotations

from dataclasses import dataclass, fields


class PublicAVTwoStageReturnPreregistrationError(ValueError):
    """Raised when a preregistration would authorize a run or claim memory."""


@dataclass(frozen=True, slots=True)
class PublicAVTwoStageReturnArm:
    arm_id: str
    stage_one_sequence_id: str
    stage_two_sequence_id: str
    carry_field_state_to_stage_two: bool
    fresh_field_before_stage_two: bool
    resolution_phase: str
    intermediate_interval_ticks: int

    def __post_init__(self) -> None:
        if self.arm_id not in {"continued_field", "fresh_stage_two_baseline"}:
            raise PublicAVTwoStageReturnPreregistrationError("invalid arm_id")
        expected_sequence = "public.av.nasa-earthrise.0p5s.reduced.v1"
        if self.stage_one_sequence_id != expected_sequence or self.stage_two_sequence_id != expected_sequence:
            raise PublicAVTwoStageReturnPreregistrationError("both stages require the same audited sequence")
        if not isinstance(self.carry_field_state_to_stage_two, bool) or not isinstance(
            self.fresh_field_before_stage_two,
            bool,
        ):
            raise PublicAVTwoStageReturnPreregistrationError("state flags must be boolean")
        if self.carry_field_state_to_stage_two == self.fresh_field_before_stage_two:
            raise PublicAVTwoStageReturnPreregistrationError("arms require exactly one stage-two state mode")
        if self.arm_id == "continued_field" and not self.carry_field_state_to_stage_two:
            raise PublicAVTwoStageReturnPreregistrationError("continued arm must carry field state")
        if self.arm_id == "fresh_stage_two_baseline" and not self.fresh_field_before_stage_two:
            raise PublicAVTwoStageReturnPreregistrationError("baseline arm must refresh stage two")
        if self.resolution_phase != "no_input_gap.step_time_only":
            raise PublicAVTwoStageReturnPreregistrationError("resolution phase must remain fixed")
        if (
            isinstance(self.intermediate_interval_ticks, bool)
            or not isinstance(self.intermediate_interval_ticks, int)
            or self.intermediate_interval_ticks != 100_000_000
        ):
            raise PublicAVTwoStageReturnPreregistrationError("intermediate interval must be 0.1 seconds")


@dataclass(frozen=True, slots=True)
class PublicAVTwoStageReturnPreregistration:
    preregistration_id: str
    source_id: str
    clock_id: str
    stage_duration_ticks: int
    stage_sequence_digest: tuple[str, str]
    arms: tuple[PublicAVTwoStageReturnArm, ...]
    fixed_field_parameters: tuple[str, ...]
    measured_roles: tuple[str, ...]
    required_invariants: tuple[str, ...]
    preregistration_complete: bool
    runner_implementation_allowed: bool = False
    field_run_allowed: bool = False
    memory_threshold_defined: bool = False
    organization_threshold_defined: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        if not self.preregistration_id or not self.source_id or not self.clock_id:
            raise PublicAVTwoStageReturnPreregistrationError("technical identities are required")
        if self.stage_duration_ticks != 500_000_000:
            raise PublicAVTwoStageReturnPreregistrationError("stage duration must remain 0.5 seconds")
        digests = tuple(self.stage_sequence_digest)
        if len(digests) != 2:
            raise PublicAVTwoStageReturnPreregistrationError("auditory and visual sequence digests are required")
        for digest in digests:
            if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
                raise PublicAVTwoStageReturnPreregistrationError("stage digests must be SHA-256")
        arms = tuple(self.arms)
        if {arm.arm_id for arm in arms} != {"continued_field", "fresh_stage_two_baseline"}:
            raise PublicAVTwoStageReturnPreregistrationError("exactly two return arms are required")
        forbidden_measurements = {
            "label",
            "meaning",
            "reward",
            "target_topology",
            "desired_response",
            "memory_score",
            "organization_score",
        }
        if forbidden_measurements.intersection(self.measured_roles):
            raise PublicAVTwoStageReturnPreregistrationError("content or claim measurements are forbidden")
        if not self.fixed_field_parameters or not self.measured_roles or not self.required_invariants:
            raise PublicAVTwoStageReturnPreregistrationError("parameters, measurements, and invariants are required")
        release_flags = (
            "runner_implementation_allowed",
            "field_run_allowed",
            "memory_threshold_defined",
            "organization_threshold_defined",
            "memory_claim_allowed",
            "meaning_claim_allowed",
            "organization_claim_allowed",
            "ai_claim_allowed",
        )
        if not self.preregistration_complete or any(getattr(self, role) for role in release_flags):
            raise PublicAVTwoStageReturnPreregistrationError(
                "two-stage preregistration cannot release runs, thresholds, or claims"
            )
        object.__setattr__(self, "stage_sequence_digest", digests)
        object.__setattr__(self, "arms", arms)
        object.__setattr__(self, "fixed_field_parameters", tuple(self.fixed_field_parameters))
        object.__setattr__(self, "measured_roles", tuple(self.measured_roles))
        object.__setattr__(self, "required_invariants", tuple(self.required_invariants))


def public_av_two_stage_return_preregistration() -> PublicAVTwoStageReturnPreregistration:
    sequence_id = "public.av.nasa-earthrise.0p5s.reduced.v1"
    return PublicAVTwoStageReturnPreregistration(
        preregistration_id="public.av.nasa-earthrise.two-stage-return.v1",
        source_id="public.audiovisual.nasa-earthrise-realtime.svs.2013-12-20",
        clock_id="public.media.pts_ns",
        stage_duration_ticks=500_000_000,
        stage_sequence_digest=(
            "501476111cdd3d17e9b5249b3774dc7918c8ffb8123264c16ce775ba5f6a175f",
            "86e9d1a2b1c01959f52d2446f855078dc313341f638bc8e23f43fcf79ea48d93",
        ),
        arms=(
            PublicAVTwoStageReturnArm(
                "continued_field",
                sequence_id,
                sequence_id,
                True,
                False,
                "no_input_gap.step_time_only",
                100_000_000,
            ),
            PublicAVTwoStageReturnArm(
                "fresh_stage_two_baseline",
                sequence_id,
                sequence_id,
                False,
                True,
                "no_input_gap.step_time_only",
                100_000_000,
            ),
        ),
        fixed_field_parameters=(
            "fresh_shared_field_at_stage_one_start",
            "neutral_local_field_substrate_config_1.0",
            "neutral_fast_afterimage_config_0.5",
            "orthogonal_field_sample_offsets",
            "identical_audio_video_dock_geometry",
            "stage_two_uses_identical_reduced_sequence",
        ),
        measured_roles=(
            "stage_one_snapshot_digest",
            "post_resolution_snapshot_digest",
            "stage_two_snapshot_digest",
            "stage_two_layer_digest",
            "stage_two_activation_vector",
            "stage_two_afterimage_vector",
            "stage_two_activation_linf_between_arms",
            "stage_two_afterimage_linf_between_arms",
            "stage_two_layer_digest_equal",
            "stage_two_snapshot_digest_equal",
        ),
        required_invariants=(
            "same_audited_source_in_both_stages",
            "same_reduced_sequence_in_both_stages",
            "same_intermediate_interval_in_all_arms",
            "same_resolution_phase_in_all_arms",
            "no_receptor_feedback",
            "no_field_to_media_feedback",
            "no_metadata_input",
            "no_raw_payload_output",
            "no_memory_or_organization_threshold",
        ),
        preregistration_complete=True,
    )


def public_av_two_stage_return_preregistration_json_value(
    plan: PublicAVTwoStageReturnPreregistration,
) -> dict:
    if not isinstance(plan, PublicAVTwoStageReturnPreregistration):
        raise PublicAVTwoStageReturnPreregistrationError("two-stage preregistration is required")

    def convert(value):
        if hasattr(value, "__dataclass_fields__"):
            return {
                role: convert(getattr(value, role))
                for role in value.__dataclass_fields__
            }
        if isinstance(value, tuple):
            return [convert(item) for item in value]
        return value

    return convert(plan)


def public_av_two_stage_return_preregistration_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (PublicAVTwoStageReturnArm, PublicAVTwoStageReturnPreregistration)
        for item in fields(cls)
    )
