"""Preregister a bounded causal replication of the public AV return result."""

from __future__ import annotations

from dataclasses import dataclass, fields


class PublicAVReturnReplicationPreregistrationError(ValueError):
    """Raised when the replication plan would predefine claims or outcomes."""


@dataclass(frozen=True, slots=True)
class PublicAVReturnReplicationArm:
    arm_id: str
    stage_one_sequence_id: str
    stage_two_sequence_id: str
    stage_one_state_mode: str
    resolution_phase: str
    stage_two_state_mode: str
    causal_contrast_role: str
    intermediate_interval_ticks: int

    def __post_init__(self) -> None:
        allowed_arms = {
            "return.continued.full_state",
            "return.fresh_stage_two",
            "control.activation_only_carry",
            "control.afterimage_only_carry",
            "control.stage_two_order_permuted",
            "control.stage_two_sequence_withheld",
        }
        if self.arm_id not in allowed_arms:
            raise PublicAVReturnReplicationPreregistrationError("invalid replication arm")
        sequence_id = "public.av.nasa-earthrise.0p5s.reduced.v1"
        if self.stage_one_sequence_id != sequence_id:
            raise PublicAVReturnReplicationPreregistrationError("stage one must use the audited sequence")
        stage_two_ids = {
            sequence_id,
            "public.av.nasa-earthrise.0p5s.reduced.permuted-order.v1",
            "none.no-stage-two-receptor-sequence",
        }
        if self.stage_two_sequence_id not in stage_two_ids:
            raise PublicAVReturnReplicationPreregistrationError("invalid stage two sequence")
        if self.stage_one_state_mode != "fresh_shared_field":
            raise PublicAVReturnReplicationPreregistrationError("stage one must start fresh")
        if self.resolution_phase != "no_input_gap.step_time_only":
            raise PublicAVReturnReplicationPreregistrationError("resolution phase must remain fixed")
        state_modes = {
            "carry_activation_and_afterimage",
            "fresh_before_stage_two",
            "carry_activation_reset_afterimage",
            "reset_activation_carry_afterimage",
            "carry_full_state_with_permuted_stage_two",
            "carry_full_state_without_stage_two_receptors",
        }
        if self.stage_two_state_mode not in state_modes:
            raise PublicAVReturnReplicationPreregistrationError("invalid state mode")
        contrast_roles = {
            "observed_return_state_continuation",
            "fresh_field_counterbaseline",
            "linear_residual_counterbaseline",
            "afterimage_counterbaseline",
            "sequence_order_counterbaseline",
            "no_world_return_counterbaseline",
        }
        if self.causal_contrast_role not in contrast_roles:
            raise PublicAVReturnReplicationPreregistrationError("invalid contrast role")
        if self.intermediate_interval_ticks != 100_000_000:
            raise PublicAVReturnReplicationPreregistrationError("intermediate interval must remain 0.1 seconds")


@dataclass(frozen=True, slots=True)
class PublicAVReturnReplicationPreregistration:
    preregistration_id: str
    antecedent_result_doc: str
    source_id: str
    clock_id: str
    stage_duration_ticks: int
    resolution_duration_ticks: int
    stage_sequence_digest: tuple[str, str]
    arms: tuple[PublicAVReturnReplicationArm, ...]
    fixed_field_parameters: tuple[str, ...]
    measured_roles: tuple[str, ...]
    required_invariants: tuple[str, ...]
    causal_questions: tuple[str, ...]
    preregistration_complete: bool
    replication_run_allowed: bool = False
    runner_implementation_allowed: bool = False
    memory_threshold_defined: bool = False
    organization_threshold_defined: bool = False
    positive_effect_required: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        if not self.preregistration_id or not self.source_id or not self.clock_id:
            raise PublicAVReturnReplicationPreregistrationError("technical identities are required")
        if self.stage_duration_ticks != 500_000_000 or self.resolution_duration_ticks != 100_000_000:
            raise PublicAVReturnReplicationPreregistrationError("durations must remain fixed")
        digests = tuple(self.stage_sequence_digest)
        if len(digests) != 2:
            raise PublicAVReturnReplicationPreregistrationError("auditory and visual digests are required")
        for digest in digests:
            if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
                raise PublicAVReturnReplicationPreregistrationError("stage digests must be SHA-256")
        arms = tuple(self.arms)
        expected = {
            "return.continued.full_state",
            "return.fresh_stage_two",
            "control.activation_only_carry",
            "control.afterimage_only_carry",
            "control.stage_two_order_permuted",
            "control.stage_two_sequence_withheld",
        }
        if {arm.arm_id for arm in arms} != expected:
            raise PublicAVReturnReplicationPreregistrationError("all six replication arms are required")
        forbidden_measurements = {
            "label",
            "meaning",
            "reward",
            "target_topology",
            "desired_response",
            "memory_score",
            "organization_score",
            "success_threshold",
        }
        if forbidden_measurements.intersection(self.measured_roles):
            raise PublicAVReturnReplicationPreregistrationError("claim or content measurements are forbidden")
        release_flags = (
            self.replication_run_allowed,
            self.runner_implementation_allowed,
            self.memory_threshold_defined,
            self.organization_threshold_defined,
            self.positive_effect_required,
            self.memory_claim_allowed,
            self.meaning_claim_allowed,
            self.organization_claim_allowed,
            self.ai_claim_allowed,
        )
        if not self.preregistration_complete or any(release_flags):
            raise PublicAVReturnReplicationPreregistrationError(
                "replication preregistration cannot release runs, thresholds, or claims"
            )
        object.__setattr__(self, "stage_sequence_digest", digests)
        object.__setattr__(self, "arms", arms)
        object.__setattr__(self, "fixed_field_parameters", tuple(self.fixed_field_parameters))
        object.__setattr__(self, "measured_roles", tuple(self.measured_roles))
        object.__setattr__(self, "required_invariants", tuple(self.required_invariants))
        object.__setattr__(self, "causal_questions", tuple(self.causal_questions))


def public_av_return_replication_preregistration() -> PublicAVReturnReplicationPreregistration:
    sequence_id = "public.av.nasa-earthrise.0p5s.reduced.v1"
    return PublicAVReturnReplicationPreregistration(
        preregistration_id="public.av.nasa-earthrise.return-replication.v1",
        antecedent_result_doc="docs/forschung/106_NASA_ZWEISTUFIGER_WELTWIEDERKEHR_VOLLSTAENDIGER_LAUF.md",
        source_id="public.audiovisual.nasa-earthrise-realtime.svs.2013-12-20",
        clock_id="public.media.pts_ns",
        stage_duration_ticks=500_000_000,
        resolution_duration_ticks=100_000_000,
        stage_sequence_digest=(
            "501476111cdd3d17e9b5249b3774dc7918c8ffb8123264c16ce775ba5f6a175f",
            "86e9d1a2b1c01959f52d2446f855078dc313341f638bc8e23f43fcf79ea48d93",
        ),
        arms=(
            PublicAVReturnReplicationArm(
                "return.continued.full_state",
                sequence_id,
                sequence_id,
                "fresh_shared_field",
                "no_input_gap.step_time_only",
                "carry_activation_and_afterimage",
                "observed_return_state_continuation",
                100_000_000,
            ),
            PublicAVReturnReplicationArm(
                "return.fresh_stage_two",
                sequence_id,
                sequence_id,
                "fresh_shared_field",
                "no_input_gap.step_time_only",
                "fresh_before_stage_two",
                "fresh_field_counterbaseline",
                100_000_000,
            ),
            PublicAVReturnReplicationArm(
                "control.activation_only_carry",
                sequence_id,
                sequence_id,
                "fresh_shared_field",
                "no_input_gap.step_time_only",
                "carry_activation_reset_afterimage",
                "linear_residual_counterbaseline",
                100_000_000,
            ),
            PublicAVReturnReplicationArm(
                "control.afterimage_only_carry",
                sequence_id,
                sequence_id,
                "fresh_shared_field",
                "no_input_gap.step_time_only",
                "reset_activation_carry_afterimage",
                "afterimage_counterbaseline",
                100_000_000,
            ),
            PublicAVReturnReplicationArm(
                "control.stage_two_order_permuted",
                sequence_id,
                "public.av.nasa-earthrise.0p5s.reduced.permuted-order.v1",
                "fresh_shared_field",
                "no_input_gap.step_time_only",
                "carry_full_state_with_permuted_stage_two",
                "sequence_order_counterbaseline",
                100_000_000,
            ),
            PublicAVReturnReplicationArm(
                "control.stage_two_sequence_withheld",
                sequence_id,
                "none.no-stage-two-receptor-sequence",
                "fresh_shared_field",
                "no_input_gap.step_time_only",
                "carry_full_state_without_stage_two_receptors",
                "no_world_return_counterbaseline",
                100_000_000,
            ),
        ),
        fixed_field_parameters=(
            "neutral_local_field_substrate_config_1.0",
            "neutral_fast_afterimage_config_0.5",
            "orthogonal_field_sample_offsets",
            "identical_audio_video_dock_geometry",
            "same_stage_one_reduced_sequence",
            "same_resolution_duration",
            "same_public_media_clock",
        ),
        measured_roles=(
            "stage_one_snapshot_digest",
            "post_resolution_snapshot_digest_nullable",
            "stage_two_snapshot_digest_nullable",
            "stage_two_layer_digest_nullable",
            "stage_two_activation_vector_nullable",
            "stage_two_afterimage_vector_nullable",
            "pairwise_activation_linf_matrix",
            "pairwise_afterimage_linf_matrix",
            "layer_digest_equality_matrix",
            "snapshot_digest_equality_matrix",
            "withheld_stage_two_contact_count",
        ),
        required_invariants=(
            "same_audited_source_contract",
            "same_local_file_integrity_gate",
            "fresh_field_at_every_arm_start",
            "no_receptor_feedback",
            "no_field_to_media_feedback",
            "no_metadata_input",
            "no_raw_payload_output",
            "no_memory_or_organization_threshold",
            "no_positive_minimum_difference",
        ),
        causal_questions=(
            "separate_full_state_from_fresh_stage_two_response",
            "separate_linear_activation_residual_from_afterimage_trace",
            "separate_same_sequence_return_from_order_permuted_stage_two",
            "separate_stage_two_world_contact_from_contact_free_continuation",
        ),
        preregistration_complete=True,
    )


def public_av_return_replication_preregistration_json_value(
    plan: PublicAVReturnReplicationPreregistration,
) -> dict[str, object]:
    if not isinstance(plan, PublicAVReturnReplicationPreregistration):
        raise PublicAVReturnReplicationPreregistrationError("replication preregistration is required")

    def convert(value):
        if hasattr(value, "__dataclass_fields__"):
            return {role: convert(getattr(value, role)) for role in value.__dataclass_fields__}
        if isinstance(value, tuple):
            return [convert(item) for item in value]
        return value

    return convert(plan)


def public_av_return_replication_preregistration_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (PublicAVReturnReplicationArm, PublicAVReturnReplicationPreregistration)
        for item in fields(cls)
    )
