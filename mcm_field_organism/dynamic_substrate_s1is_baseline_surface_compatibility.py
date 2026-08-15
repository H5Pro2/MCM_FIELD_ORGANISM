"""Static S1-IS compatibility audit for DTS-1 joint baseline surfaces."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1ir_corrected_profile_contract import (
    build_dts1_s1ir_corrected_profile_contract,
)


class DTS1S1ISBaselineSurfaceCompatibilityError(ValueError):
    """Raised when the static S1-IS compatibility boundary is weakened."""


S1_IS_AUDIT_ID = "dynamic-substrate.baseline-surface-compatibility.s1is.v1"
S1_IS_SOURCE_S1IR_DIGEST = (
    "350de2e0abbd05d03544567b3e7aae81ef387c75c739b924deea5f726410123e"
)
S1_IS_GEOMETRY_REQUIREMENTS = (
    ("P_IE_CAUSAL_TWO_SUBSTEP", 2, 4, 8),
    ("P_IH_ATTENUATION", 2, 4, 8),
    ("P_IK_INTERFERENCE", 3, 6, 6),
    ("P_IN_RELEASE_REUSE", 3, 6, 6),
)
S1_IS_SURFACE_RECORDS = (
    (
        "B1_FIXED_PRERELEASE_ADAPTER",
        "compute_dts1_edge_rates-plus-_advance_active_field",
        "arbitrary-nonempty-symmetric-edge-inventory-including-open-two-and-three-node-lines",
        "complete-SharedMCMField-SH-output",
        "sanitize-to-common-predivergence-conductive-ledger-derive-once-then-reuse-fixed-edge-rates",
        "COMPATIBLE_REQUIRES_PRIVATE_INFORMATION_BARRIER_AND_SCHEDULE_ADAPTER",
    ),
    (
        "B2_S2_LINEAR_INTEGRATOR",
        "advance_s2_reference_model-model-b2",
        "nonempty-equal-length-S-H-L-with-matching-symmetric-n-by-n-generator-and-n-boundary",
        "complete-S2ReferenceState-SH-output",
        "map-field-SH-and-geometry-boundary-while-initializing-baseline-owned-L-without-DTS1-state",
        "COMPATIBLE_REQUIRES_PRIVATE_STATE_GEOMETRY_AND_SCHEDULE_ADAPTER",
    ),
    (
        "B3_F3_LOCAL_LEAKY",
        "compute_mcm_f3_local_leaky_baseline-via-advance_mcm_f3_shared_field",
        "complete-layer-and-one-M-mass-per-node-with-matching-edge-digest-for-two-or-three-nodes",
        "complete-SharedMCMField-SH-output-via-existing-generic-F3-runtime",
        "bind-uniform-baseline-owned-M-and-inject-fixed-calculator-through-private-runtime-slot",
        "COMPATIBLE_REQUIRES_PRIVATE_F3_STATE_AND_SCHEDULE_ADAPTER",
    ),
    (
        "B4_F3_LINEAR_COUPLED",
        "compute_mcm_f3_linear_coupled_baseline-via-advance_mcm_f3_shared_field",
        "complete-layer-and-one-M-mass-per-node-with-matching-edge-digest-for-two-or-three-nodes",
        "complete-SharedMCMField-SH-output-via-existing-generic-F3-runtime",
        "bind-uniform-baseline-owned-M-and-inject-fixed-calculator-through-private-runtime-slot",
        "COMPATIBLE_REQUIRES_PRIVATE_F3_STATE_AND_SCHEDULE_ADAPTER",
    ),
    (
        "B5_F3_FULL",
        "compute_mcm_f3_coupling-via-advance_mcm_f3_shared_field",
        "complete-layer-and-one-M-mass-per-node-with-matching-edge-digest-for-two-or-three-nodes",
        "complete-SharedMCMField-SH-output-via-existing-generic-F3-runtime",
        "bind-uniform-baseline-owned-M-and-use-the-unchanged-default-F3-calculator",
        "COMPATIBLE_REQUIRES_PRIVATE_F3_STATE_AND_SCHEDULE_ADAPTER",
    ),
    (
        "B6_CONST_V",
        "compute_w7n_coupling_baseline-const-v-via-advance_mcm_f3_shared_field",
        "generic-kernel-supports-matching-two-or-three-node-M-state-but-existing-E1-E4-handoff-is-three-node-only",
        "complete-SharedMCMField-SH-output-via-existing-generic-F3-runtime",
        "bind-one-frozen-W7M-const-v-spec-and-add-private-two-node-geometry-handoff-with-uniform-baseline-owned-M",
        "COMPATIBLE_REQUIRES_PRIVATE_CONST_V_GEOMETRY_STATE_AND_SCHEDULE_ADAPTER",
    ),
)
S1_IS_COMMON_ADAPTER_RULES = (
    "adapters-may-only-map-node-identities-canonical-order-shapes-event-boundaries-and-existing-baseline-owned-state",
    "adapters-may-not-read-DTS1-free-refractory-transfer-arm-case-checkpoint-target-reference-future-or-result-data",
    "B1-sanitizer-must-not-pass-the-original-DTS1-anatomy-object-to-the-fixed-adapter-reader",
    "B2-L-and-B3-through-B6-M-initialization-must-be-one-preregistered-baseline-owned-rule-per-model-across-all-blocks",
    "B3-through-B6-must-use-the-existing-generic-F3-runtime-with-their-unchanged-coupling-calculator",
    "B6-must-use-one-existing-frozen-W7M-const-v-spec-for-both-geometries",
    "no-adapter-may-change-an-equation-parameter-state-role-checkpoint-count-profile-sign-or-control-gate",
)
S1_IS_NOT_YET_PROVEN = (
    "adapter-construction-and-fail-closed-validation",
    "one-configuration-digest-per-baseline",
    "numerical-admissibility-over-every-bound-event-interval",
    "28-component-profile-reconstruction",
    "deterministic-repeat-and-refinement-controls",
    "baseline-closure-or-residual",
)
S1_IS_FORBIDDEN_INTERPRETATIONS = (
    "implemented-ready-or-executed-baseline-composition",
    "baseline-fit-baseline-rejection-baseline-closure-or-candidate-superiority",
    "memory-learning-semantics-inner-context-organization-self-regulation-organism-or-artificial-intelligence",
)
S1_IS_DECISION = (
    "ALL_SIX_BASELINE_KERNEL_SURFACES_STATICALLY_COMPATIBLE_PRIVATE_ADAPTERS_REQUIRED"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1ISBaselineSurfaceCompatibility:
    audit_id: str
    source_s1ir_digest: str
    geometry_requirements: tuple[tuple[str, int, int, int], ...]
    surface_records: tuple[tuple[str, str, str, str, str, str], ...]
    common_adapter_rules: tuple[str, ...]
    not_yet_proven: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    baseline_role_count: int
    two_node_surface_count: int
    three_node_surface_count: int
    kernel_surface_compatibility_complete: bool
    executable_composition_ready: bool
    geometry_adapters_implemented: bool
    configuration_digests_bound: bool
    parameter_values_selected: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    adapter_contract_authorized_next_stage: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "audit_digest"
        }
        if (
            self.audit_id != S1_IS_AUDIT_ID
            or self.source_s1ir_digest != S1_IS_SOURCE_S1IR_DIGEST
            or self.geometry_requirements != S1_IS_GEOMETRY_REQUIREMENTS
            or self.surface_records != S1_IS_SURFACE_RECORDS
            or self.common_adapter_rules != S1_IS_COMMON_ADAPTER_RULES
            or self.not_yet_proven != S1_IS_NOT_YET_PROVEN
            or self.forbidden_interpretations != S1_IS_FORBIDDEN_INTERPRETATIONS
            or self.baseline_role_count != 6
            or self.two_node_surface_count != 6
            or self.three_node_surface_count != 6
            or self.kernel_surface_compatibility_complete is not True
            or any(
                value is not False
                for value in (
                    self.executable_composition_ready,
                    self.geometry_adapters_implemented,
                    self.configuration_digests_bound,
                    self.parameter_values_selected,
                    self.baseline_models_executed,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                )
            )
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.adapter_contract_authorized_next_stage is not True
            or self.decision != S1_IS_DECISION
            or self.audit_digest != _digest(payload)
        ):
            raise DTS1S1ISBaselineSurfaceCompatibilityError(
                "S1-IS weakened the static compatibility boundary"
            )


def build_dts1_s1is_baseline_surface_compatibility() -> DTS1S1ISBaselineSurfaceCompatibility:
    """Bind surface compatibility without constructing or running adapters."""

    source = build_dts1_s1ir_corrected_profile_contract()
    values = {
        "audit_id": S1_IS_AUDIT_ID,
        "source_s1ir_digest": source.contract_digest,
        "geometry_requirements": S1_IS_GEOMETRY_REQUIREMENTS,
        "surface_records": S1_IS_SURFACE_RECORDS,
        "common_adapter_rules": S1_IS_COMMON_ADAPTER_RULES,
        "not_yet_proven": S1_IS_NOT_YET_PROVEN,
        "forbidden_interpretations": S1_IS_FORBIDDEN_INTERPRETATIONS,
        "baseline_role_count": len(S1_IS_SURFACE_RECORDS),
        "two_node_surface_count": len(S1_IS_SURFACE_RECORDS),
        "three_node_surface_count": len(S1_IS_SURFACE_RECORDS),
        "kernel_surface_compatibility_complete": True,
        "executable_composition_ready": False,
        "geometry_adapters_implemented": False,
        "configuration_digests_bound": False,
        "parameter_values_selected": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "adapter_contract_authorized_next_stage": True,
        "decision": S1_IS_DECISION,
    }
    return DTS1S1ISBaselineSurfaceCompatibility(
        **values, audit_digest=_digest(values)
    )
