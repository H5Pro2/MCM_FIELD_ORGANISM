"""Preregister locked repeatability checks for the public AV causal contrasts."""

from __future__ import annotations

from dataclasses import dataclass, fields

from .public_av_return_replication_preregistration import (
    PublicAVReturnReplicationPreregistration,
    public_av_return_replication_preregistration,
)


class PublicAVReturnReplicationRepeatabilityPreregistrationError(ValueError):
    """Raised when repeatability preregistration would release runs or claims."""


@dataclass(frozen=True, slots=True)
class PublicAVReturnTechnicalContrastRepeatabilityRole:
    contrast_id: str
    causal_question: str
    left_arm_id: str
    right_arm_id: str
    measured_roles: tuple[str, ...]

    def __post_init__(self) -> None:
        allowed = {
            "full_state_vs_fresh_stage_two": (
                "separate_full_state_from_fresh_stage_two_response",
                "return.continued.full_state",
                "return.fresh_stage_two",
            ),
            "activation_only_vs_afterimage_only": (
                "separate_linear_activation_residual_from_afterimage_trace",
                "control.activation_only_carry",
                "control.afterimage_only_carry",
            ),
            "full_state_vs_permuted_stage_two": (
                "separate_same_sequence_return_from_order_permuted_stage_two",
                "return.continued.full_state",
                "control.stage_two_order_permuted",
            ),
            "full_state_vs_withheld_stage_two": (
                "separate_stage_two_world_contact_from_contact_free_continuation",
                "return.continued.full_state",
                "control.stage_two_sequence_withheld",
            ),
        }
        expected = allowed.get(self.contrast_id)
        if expected is None:
            raise PublicAVReturnReplicationRepeatabilityPreregistrationError("invalid contrast id")
        if (self.causal_question, self.left_arm_id, self.right_arm_id) != expected:
            raise PublicAVReturnReplicationRepeatabilityPreregistrationError("contrast mapping changed")
        roles = tuple(self.measured_roles)
        required = {
            "activation_linf_values",
            "afterimage_linf_values",
            "layer_digest_equal_values",
            "snapshot_digest_equal_values",
            "stage_two_event_count_values",
        }
        forbidden = {
            "memory_score",
            "organization_score",
            "meaning",
            "label",
            "reward",
            "success_threshold",
            "target_topology",
        }
        if not required.issubset(roles) or forbidden.intersection(roles):
            raise PublicAVReturnReplicationRepeatabilityPreregistrationError("invalid repeatability measurement roles")
        object.__setattr__(self, "measured_roles", roles)


@dataclass(frozen=True, slots=True)
class PublicAVReturnReplicationRepeatabilityPreregistration:
    preregistration_id: str
    antecedent_analysis_doc: str
    source_id: str
    clock_id: str
    base_preregistration_id: str
    independent_repeat_count: int
    repeat_index_set: tuple[int, ...]
    contract_parameters_required_identical: tuple[str, ...]
    contrast_roles: tuple[PublicAVReturnTechnicalContrastRepeatabilityRole, ...]
    stability_measurements: tuple[str, ...]
    aggregation_roles: tuple[str, ...]
    required_invariants: tuple[str, ...]
    preregistration_complete: bool
    runner_implementation_allowed: bool = False
    repeatability_run_allowed: bool = False
    memory_threshold_defined: bool = False
    organization_threshold_defined: bool = False
    positive_effect_required: bool = False
    causal_mechanism_claim_allowed: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        if self.independent_repeat_count != 3 or tuple(self.repeat_index_set) != (1, 2, 3):
            raise PublicAVReturnReplicationRepeatabilityPreregistrationError("exactly three independent repeats are preregistered")
        if self.base_preregistration_id != "public.av.nasa-earthrise.return-replication.v1":
            raise PublicAVReturnReplicationRepeatabilityPreregistrationError("base preregistration changed")
        contrasts = tuple(self.contrast_roles)
        if len(contrasts) != 4 or len({item.contrast_id for item in contrasts}) != 4:
            raise PublicAVReturnReplicationRepeatabilityPreregistrationError("four unique contrast roles are required")
        required_parameters = {
            "same_source_contract",
            "same_local_file_integrity_gate",
            "same_permutation_contract_digest",
            "same_component_intervention_contract",
            "same_runner_wiring_contract",
            "same_preflight_gate",
            "same_stage_durations",
            "same_resolution_duration",
            "same_field_parameters",
            "same_public_media_clock",
        }
        if not required_parameters.issubset(self.contract_parameters_required_identical):
            raise PublicAVReturnReplicationRepeatabilityPreregistrationError("contract parameter identity is incomplete")
        required_stability = {
            "per_repeat_activation_linf",
            "per_repeat_afterimage_linf",
            "per_repeat_layer_digest_equality",
            "per_repeat_snapshot_digest_equality",
            "cross_repeat_activation_linf_min_max_range",
            "cross_repeat_afterimage_linf_min_max_range",
            "cross_repeat_digest_equality_pattern_consistency",
            "withheld_stage_two_event_count_consistency",
        }
        forbidden_roles = {
            "memory_score",
            "organization_score",
            "meaning",
            "label",
            "reward",
            "success_threshold",
            "target_topology",
        }
        role_pool = set(self.stability_measurements) | set(self.aggregation_roles) | set(self.required_invariants)
        if not required_stability.issubset(self.stability_measurements) or forbidden_roles.intersection(role_pool):
            raise PublicAVReturnReplicationRepeatabilityPreregistrationError("invalid stability roles")
        forbidden_flags = (
            self.runner_implementation_allowed,
            self.repeatability_run_allowed,
            self.memory_threshold_defined,
            self.organization_threshold_defined,
            self.positive_effect_required,
            self.causal_mechanism_claim_allowed,
            self.memory_claim_allowed,
            self.meaning_claim_allowed,
            self.organization_claim_allowed,
            self.ai_claim_allowed,
        )
        if not self.preregistration_complete or any(forbidden_flags):
            raise PublicAVReturnReplicationRepeatabilityPreregistrationError(
                "repeatability preregistration cannot release runs, thresholds, or claims"
            )
        object.__setattr__(self, "repeat_index_set", tuple(self.repeat_index_set))
        object.__setattr__(self, "contract_parameters_required_identical", tuple(self.contract_parameters_required_identical))
        object.__setattr__(self, "contrast_roles", contrasts)
        object.__setattr__(self, "stability_measurements", tuple(self.stability_measurements))
        object.__setattr__(self, "aggregation_roles", tuple(self.aggregation_roles))
        object.__setattr__(self, "required_invariants", tuple(self.required_invariants))


def public_av_return_replication_repeatability_preregistration(
    base: PublicAVReturnReplicationPreregistration | None = None,
) -> PublicAVReturnReplicationRepeatabilityPreregistration:
    plan = base or public_av_return_replication_preregistration()
    if not isinstance(plan, PublicAVReturnReplicationPreregistration):
        raise PublicAVReturnReplicationRepeatabilityPreregistrationError("base replication preregistration is required")
    roles = (
        "activation_linf_values",
        "afterimage_linf_values",
        "layer_digest_equal_values",
        "snapshot_digest_equal_values",
        "stage_two_event_count_values",
    )
    return PublicAVReturnReplicationRepeatabilityPreregistration(
        preregistration_id="public.av.nasa-earthrise.return-replication.repeatability-preregistration.v1",
        antecedent_analysis_doc="docs/forschung/117_NASA_WELTWIEDERKEHR_REPLIKATION_KAUSALKONTRAST_ANALYSE.md",
        source_id=plan.source_id,
        clock_id=plan.clock_id,
        base_preregistration_id=plan.preregistration_id,
        independent_repeat_count=3,
        repeat_index_set=(1, 2, 3),
        contract_parameters_required_identical=(
            "same_source_contract",
            "same_local_file_integrity_gate",
            "same_permutation_contract_digest",
            "same_component_intervention_contract",
            "same_runner_wiring_contract",
            "same_preflight_gate",
            "same_stage_durations",
            "same_resolution_duration",
            "same_field_parameters",
            "same_public_media_clock",
        ),
        contrast_roles=(
            PublicAVReturnTechnicalContrastRepeatabilityRole(
                "full_state_vs_fresh_stage_two",
                plan.causal_questions[0],
                "return.continued.full_state",
                "return.fresh_stage_two",
                roles,
            ),
            PublicAVReturnTechnicalContrastRepeatabilityRole(
                "activation_only_vs_afterimage_only",
                plan.causal_questions[1],
                "control.activation_only_carry",
                "control.afterimage_only_carry",
                roles,
            ),
            PublicAVReturnTechnicalContrastRepeatabilityRole(
                "full_state_vs_permuted_stage_two",
                plan.causal_questions[2],
                "return.continued.full_state",
                "control.stage_two_order_permuted",
                roles,
            ),
            PublicAVReturnTechnicalContrastRepeatabilityRole(
                "full_state_vs_withheld_stage_two",
                plan.causal_questions[3],
                "return.continued.full_state",
                "control.stage_two_sequence_withheld",
                roles,
            ),
        ),
        stability_measurements=(
            "per_repeat_activation_linf",
            "per_repeat_afterimage_linf",
            "per_repeat_layer_digest_equality",
            "per_repeat_snapshot_digest_equality",
            "cross_repeat_activation_linf_min_max_range",
            "cross_repeat_afterimage_linf_min_max_range",
            "cross_repeat_digest_equality_pattern_consistency",
            "withheld_stage_two_event_count_consistency",
        ),
        aggregation_roles=(
            "technical_min",
            "technical_max",
            "technical_range",
            "exact_digest_pattern_match_count",
            "repeat_index_only",
        ),
        required_invariants=(
            "no_repetition_without_separate_start_preflight",
            "no_adaptive_parameter_update_between_repeats",
            "no_cross_repeat_state_carry",
            "fresh_field_at_every_repeat_start",
            "no_metadata_input",
            "no_raw_payload_output",
            "no_memory_or_organization_threshold",
            "no_positive_minimum_difference",
        ),
        preregistration_complete=True,
    )


def public_av_return_replication_repeatability_preregistration_json_value(
    plan: PublicAVReturnReplicationRepeatabilityPreregistration,
) -> dict[str, object]:
    if not isinstance(plan, PublicAVReturnReplicationRepeatabilityPreregistration):
        raise PublicAVReturnReplicationRepeatabilityPreregistrationError("repeatability preregistration is required")

    def convert(value):
        if hasattr(value, "__dataclass_fields__"):
            return {role: convert(getattr(value, role)) for role in value.__dataclass_fields__}
        if isinstance(value, tuple):
            return [convert(item) for item in value]
        return value

    return convert(plan)


def public_av_return_replication_repeatability_preregistration_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            PublicAVReturnTechnicalContrastRepeatabilityRole,
            PublicAVReturnReplicationRepeatabilityPreregistration,
        )
        for item in fields(cls)
    )
