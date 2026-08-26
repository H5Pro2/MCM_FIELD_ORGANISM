"""Static S1-IT contracts for six private DTS-1 baseline adapters."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1is_baseline_surface_compatibility import (
    build_dts1_s1is_baseline_surface_compatibility,
)


class DTS1S1ITPrivateAdapterContractError(ValueError):
    """Raised when the closed S1-IT adapter boundary is weakened."""


S1_IT_CONTRACT_ID = "dynamic-substrate.private-baseline-adapters.s1it.v1"
S1_IT_SOURCE_S1IS_DIGEST = (
    "abbced8b76c1fd03259ef01f671db94d03e12896efcfa4c531c7135b8bedf2d7"
)
S1_IT_COMMON_INPUT_SCHEMA = (
    "canonical-node-ids-and-symmetric-edge-inventory-for-one-bound-two-or-three-node-fixture",
    "complete-finite-S-H-prestate-in-canonical-node-order",
    "ordered-receptor-contact-values-event-boundaries-durations-and-checkpoint-boundaries",
    "existing-neutral-substrate-afterimage-and-optional-dissipation-configuration-source-identities",
    "one-baseline-role-and-one-preregistered-baseline-configuration-source-identity",
)
S1_IT_COMMON_OUTPUT_SCHEMA = (
    "complete-finite-S-H-checkpoint-vectors-in-canonical-node-order",
    "one-adapter-input-digest-one-configuration-digest-and-one-output-digest",
    "model-owned-invariant-and-numerical-diagnostic-records-without-hidden-state-export-to-other-baselines",
    "atomic-success-or-one-fail-closed-error-with-no-partial-profile",
)
S1_IT_ADAPTER_CONTRACTS = (
    (
        "B1_FIXED_PRERELEASE_ADAPTER",
        "sanitized-common-predivergence-conductive-edge-ledger-plus-common-input",
        "no-evolving-baseline-state-after-one-fixed-edge-rate-ledger-is-created",
        "compute_dts1_edge_rates-on-canonical-sanitized-anatomy-then-_advance_active_field-with-one-reused-adapter",
        "fixed-edge-rate-ledger-digest-plus-common-output",
        "reject-original-DTS1-anatomy-free-refractory-transfer-or-any-postdivergence-conductive-state",
    ),
    (
        "B2_S2_LINEAR_INTEGRATOR",
        "common-input-translated-to-matching-symmetric-generator-and-boundary-vector",
        "S-and-H-from-common-prestate-plus-baseline-owned-neutral-zero-L",
        "advance_s2_reference_model-with-model-id-b2-and-one-immutable-config-source",
        "S-and-H-checkpoints-plus-L-invariant-diagnostics-and-common-output",
        "reject-nonsymmetric-or-shape-mismatched-generator-boundary-and-any-DTS1-derived-L",
    ),
    (
        "B3_F3_LOCAL_LEAKY",
        "common-input-plus-uniform-baseline-owned-M-state-matching-the-complete-geometry",
        "S-and-H-from-common-prestate-plus-uniform-M-from-one-immutable-arm-config-source",
        "advance_mcm_f3_shared_field-with-compute_mcm_f3_local_leaky_baseline-in-private-calculator-slot",
        "S-and-H-checkpoints-plus-M-balance-diagnostics-and-common-output",
        "reject-nonuniform-or-DTS1-derived-M-and-any-calculator-substitution",
    ),
    (
        "B4_F3_LINEAR_COUPLED",
        "common-input-plus-uniform-baseline-owned-M-state-matching-the-complete-geometry",
        "S-and-H-from-common-prestate-plus-uniform-M-from-one-immutable-arm-config-source",
        "advance_mcm_f3_shared_field-with-compute_mcm_f3_linear_coupled_baseline-in-private-calculator-slot",
        "S-and-H-checkpoints-plus-M-balance-diagnostics-and-common-output",
        "reject-nonuniform-or-DTS1-derived-M-and-any-calculator-substitution",
    ),
    (
        "B5_F3_FULL",
        "common-input-plus-uniform-baseline-owned-M-state-matching-the-complete-geometry",
        "S-and-H-from-common-prestate-plus-uniform-M-from-one-immutable-arm-config-source",
        "advance_mcm_f3_shared_field-with-unchanged-default-compute_mcm_f3_coupling",
        "S-and-H-checkpoints-plus-M-balance-diagnostics-and-common-output",
        "reject-nonuniform-or-DTS1-derived-M-and-any-default-calculator-replacement",
    ),
    (
        "B6_CONST_V",
        "common-input-plus-one-frozen-W7M-const-v-spec-and-uniform-baseline-owned-M-state",
        "S-and-H-from-common-prestate-plus-uniform-M-from-the-same-frozen-spec-for-both-geometries",
        "advance_mcm_f3_shared_field-with-compute_w7n_coupling_baseline-const-v-bound-in-private-calculator-slot",
        "S-and-H-checkpoints-plus-M-balance-spec-identity-diagnostics-and-common-output",
        "reject-non-const-v-spec-geometry-specific-spec-values-DTS1-derived-M-or-calculator-substitution",
    ),
)
S1_IT_SCHEDULE_RULES = (
    "preserve-every-contact-value-order-start-end-duration-and-checkpoint-boundary-from-the-source-fixture",
    "map-one-source-event-interval-to-exactly-one-baseline-interval-without-merge-split-delay-replay-or-lookahead",
    "derive-generators-boundaries-and-distributions-only-from-the-common-geometry-contact-and-existing-field-config-sources",
    "emit-only-the-S-H-checkpoints-bound-by-the-corrected-28-component-profile-in-canonical-order",
    "zero-contact-intervals-remain-explicit-and-may-not-be-removed-as-no-ops",
)
S1_IT_CONFIGURATION_RULES = (
    "B1-binds-one-fixed-adapter-per-source-fixture-from-the-common-predivergence-conductive-ledger",
    "B2-through-B6-bind-one-existing-configuration-source-identity-and-later-one-digest-across-all-four-profile-blocks",
    "B2-neutral-zero-L-and-B3-through-B6-uniform-M-are-state-initialization-rules-not-fit-parameters",
    "B6-uses-one-existing-frozen-W7M-const-v-spec-for-two-and-three-node-geometries",
    "numeric-values-configuration-digests-refinement-and-comparison-thresholds-remain-unselected-in-S1-IT",
)
S1_IT_FORBIDDEN_INPUTS = (
    "DTS1-free-refractory-transfer-ledger-or-original-anatomy-object",
    "arm-case-profile-block-checkpoint-target-direction-reference-output-or-future-state",
    "result-dependent-parameter-gain-scale-reset-retry-or-oracle-state",
    "hidden-replay-phase-detector-label-reward-target-topology-or-resource-transport",
)
S1_IT_FAIL_CLOSED_RULES = (
    "reject-any-node-edge-digest-shape-order-time-or-checkpoint-mismatch-before-kernel-entry",
    "reject-any-configuration-source-or-calculator-identity-drift-before-kernel-entry",
    "reject-any-forbidden-input-presence-even-when-the-current-kernel-source-would-not-read-it",
    "reject-any-nonfinite-out-of-domain-invariant-breaking-partial-or-nondeterministic-output",
    "one-adapter-failure-invalidates-the-complete-later-joint-audit-without-omission-or-substitution",
)
S1_IT_FORBIDDEN_INTERPRETATIONS = (
    "implemented-executable-validated-or-numerically-admissible-adapter",
    "parameter-selection-baseline-fit-baseline-closure-or-candidate-superiority",
    "memory-learning-semantics-inner-context-organization-self-regulation-organism-or-artificial-intelligence",
)
S1_IT_DECISION = "SIX_PRIVATE_BASELINE_ADAPTER_CONTRACTS_BOUND_NO_IMPLEMENTATION_OR_VALUES"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1ITPrivateAdapterContract:
    contract_id: str
    source_s1is_digest: str
    common_input_schema: tuple[str, ...]
    common_output_schema: tuple[str, ...]
    adapter_contracts: tuple[tuple[str, str, str, str, str, str], ...]
    schedule_rules: tuple[str, ...]
    configuration_rules: tuple[str, ...]
    forbidden_inputs: tuple[str, ...]
    fail_closed_rules: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    adapter_role_count: int
    parameter_source_identities_named: bool
    parameter_values_selected: bool
    configuration_digests_bound: bool
    comparison_threshold_selected: bool
    adapters_implemented: bool
    profile_container_implemented: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    finite_binding_contract_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_IT_CONTRACT_ID
            or self.source_s1is_digest != S1_IT_SOURCE_S1IS_DIGEST
            or self.common_input_schema != S1_IT_COMMON_INPUT_SCHEMA
            or self.common_output_schema != S1_IT_COMMON_OUTPUT_SCHEMA
            or self.adapter_contracts != S1_IT_ADAPTER_CONTRACTS
            or self.schedule_rules != S1_IT_SCHEDULE_RULES
            or self.configuration_rules != S1_IT_CONFIGURATION_RULES
            or self.forbidden_inputs != S1_IT_FORBIDDEN_INPUTS
            or self.fail_closed_rules != S1_IT_FAIL_CLOSED_RULES
            or self.forbidden_interpretations != S1_IT_FORBIDDEN_INTERPRETATIONS
            or self.adapter_role_count != 6
            or self.parameter_source_identities_named is not True
            or any(
                value is not False
                for value in (
                    self.parameter_values_selected,
                    self.configuration_digests_bound,
                    self.comparison_threshold_selected,
                    self.adapters_implemented,
                    self.profile_container_implemented,
                    self.baseline_models_executed,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                )
            )
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.finite_binding_contract_authorized_next_stage is not True
            or self.decision != S1_IT_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1ITPrivateAdapterContractError(
                "S1-IT weakened the private adapter boundary"
            )


def build_dts1_s1it_private_adapter_contract() -> DTS1S1ITPrivateAdapterContract:
    """Bind six adapter interfaces without values, implementation, or execution."""

    source = build_dts1_s1is_baseline_surface_compatibility()
    values = {
        "contract_id": S1_IT_CONTRACT_ID,
        "source_s1is_digest": source.audit_digest,
        "common_input_schema": S1_IT_COMMON_INPUT_SCHEMA,
        "common_output_schema": S1_IT_COMMON_OUTPUT_SCHEMA,
        "adapter_contracts": S1_IT_ADAPTER_CONTRACTS,
        "schedule_rules": S1_IT_SCHEDULE_RULES,
        "configuration_rules": S1_IT_CONFIGURATION_RULES,
        "forbidden_inputs": S1_IT_FORBIDDEN_INPUTS,
        "fail_closed_rules": S1_IT_FAIL_CLOSED_RULES,
        "forbidden_interpretations": S1_IT_FORBIDDEN_INTERPRETATIONS,
        "adapter_role_count": len(S1_IT_ADAPTER_CONTRACTS),
        "parameter_source_identities_named": True,
        "parameter_values_selected": False,
        "configuration_digests_bound": False,
        "comparison_threshold_selected": False,
        "adapters_implemented": False,
        "profile_container_implemented": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "finite_binding_contract_authorized_next_stage": True,
        "decision": S1_IT_DECISION,
    }
    return DTS1S1ITPrivateAdapterContract(
        **values, contract_digest=_digest(values)
    )
