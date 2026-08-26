"""Static S1-JP bridge contract for six private baseline adapters."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_dts1_common_interval_materializer import (
    build_dts1_s1jo_implementation_receipt,
)
from .dynamic_substrate_s1it_private_adapter_contract import (
    build_dts1_s1it_private_adapter_contract,
)
from .dynamic_substrate_s1ja_finite_configuration_matrix_contract import (
    build_dts1_s1ja_finite_configuration_matrix_contract,
)


class DTS1S1JPBaselineAdapterBridgeContractError(ValueError):
    """Raised when the static S1-JP adapter bridge is weakened."""


S1_JP_CONTRACT_ID = "dynamic-substrate.baseline-adapter-bridge.s1jp.v1"
S1_JP_SOURCE_S1JO_DIGEST = (
    "6c4bd17ae11f9e6cc1e71f7d88a089df982b0acefc1a9800f7f80b3386de0806"
)
S1_JP_SOURCE_S1IT_DIGEST = (
    "942373dd7605c8b8054c1b188d99fce47145d7894e7521bad81c2b9065facac4"
)
S1_JP_SOURCE_S1JA_DIGEST = (
    "331168f2a6f937b454742d2be57de3f022f75ca5ca521fbff31f101bd4ea1fbc"
)
S1_JP_COMMON_INVOCATION_SCHEMA = (
    "materialized_field",
    "receptor_distribution",
    "step_time",
    "geometry_digest",
)
S1_JP_PRIVATE_CONTEXT_SCHEMA = (
    "one-exact-baseline-role-B1-through-B6-bound-before-the-sequence",
    "one-complete-role-owned-private-state-matching-the-S1-JN-schema",
    "one-exact-S1-JA-configuration-record-and-digest-for-that-role",
    "one-preregistered-refinement-level-from-two-four-or-eight",
    "no-envelope-sequence-arm-case-checkpoint-target-reference-future-or-result-data",
)
S1_JP_ADAPTER_BRIDGES = (
    (
        "B1",
        ("fixed_adapter_payload", "fixed_adapter_configuration_digest"),
        "dynamic_substrate_dts1_coupled_step._advance_active_field",
        "validate-and-reconstruct-only-the-preregistered-fixed-edge-rate-adapter-from-private-context",
        "partition-the-one-physical-window-deterministically-at-the-bound-refinement-and-advance-with-one-unchanged-fixed-adapter",
        "return-complete-field-and-the-bit-identical-fixed-adapter-private-state",
    ),
    (
        "B2",
        ("complete_L_state_payload", "B2_configuration_digest"),
        "s2_reference_baselines.advance_s2_reference_model:model-b2",
        "map-canonical-field-S-H-private-L-geometry-and-contact-to-S2-state-generator-and-boundary",
        "advance-each-deterministic-subwindow-with-the-one-bound-model-b2-configuration",
        "map-S-H-back-to-the-complete-field-and-return-the-complete-resulting-L-private-state",
    ),
    (
        "B3",
        ("embedded_M_state_digest", "B3_configuration_digest"),
        "mcm_f3_runtime.advance_mcm_f3_shared_field:compute_mcm_f3_local_leaky_baseline",
        "validate-the-embedded-M-state-and-bind-only-the-local-leaky-calculator",
        "use-the-existing-F3-runtime-native-refinement-with-the-exact-common-distribution-and-time",
        "return-the-complete-F3-field-and-private-state-with-the-resulting-embedded-M-digest",
    ),
    (
        "B4",
        ("embedded_M_state_digest", "B4_configuration_digest"),
        "mcm_f3_runtime.advance_mcm_f3_shared_field:compute_mcm_f3_linear_coupled_baseline",
        "validate-the-embedded-M-state-and-bind-only-the-linear-coupled-calculator",
        "use-the-existing-F3-runtime-native-refinement-with-the-exact-common-distribution-and-time",
        "return-the-complete-F3-field-and-private-state-with-the-resulting-embedded-M-digest",
    ),
    (
        "B5",
        ("embedded_M_state_digest", "B5_configuration_digest"),
        "mcm_f3_runtime.advance_mcm_f3_shared_field:compute_mcm_f3_coupling",
        "validate-the-embedded-M-state-and-preserve-the-unchanged-default-F3-calculator",
        "use-the-existing-F3-runtime-native-refinement-with-the-exact-common-distribution-and-time",
        "return-the-complete-F3-field-and-private-state-with-the-resulting-embedded-M-digest",
    ),
    (
        "B6",
        (
            "embedded_M_state_digest",
            "frozen_CONST_V_spec_digest",
            "B6_configuration_digest",
        ),
        "mcm_f3_runtime.advance_mcm_f3_shared_field:w7n_capacity_function_baselines.compute_w7n_coupling_baseline:const-v",
        "validate-embedded-M-and-the-one-frozen-const-v-spec-before-binding-the-private-calculator",
        "use-the-existing-F3-runtime-native-refinement-with-the-exact-common-distribution-and-time",
        "return-the-complete-F3-field-resulting-M-digest-and-unchanged-spec-and-configuration-digests",
    ),
)
S1_JP_OUTPUT_SCHEMA = (
    "one-complete-SharedMCMField-with-the-exact-finished-distribution-layer-tick-perceptions-and-role-owned-state",
    "one-complete-next-private-state-matching-the-same-S1-JN-role-schema",
    "one-role-owned-finite-invariant-and-numerical-diagnostic-record",
    "one-canonical-output-digest-over-the-complete-field-next-private-state-and-diagnostics",
    "atomic-success-or-one-S1-JP-error-with-no-field-state-diagnostic-or-digest-partial-output",
)
S1_JP_INFORMATION_BARRIER_RULES = (
    "the-adapter-interval-call-receives-exactly-the-four-S1-JO-model-invocation-values-plus-its-prebound-private-context",
    "common-exposure-private-prestate-materialized-input-and-orchestration-control-digests-never-enter-a-baseline-kernel",
    "the-integrity-record-envelope-sequence-ordinal-checkpoint-and-candidate-sidecar-never-enter-the-private-adapter-context",
    "one-baseline-private-context-is-inaccessible-to-every-other-baseline-and-to-DTS1",
    "private-context-state-may-change-only-through-the-bound-role-kernel-and-must-be-returned-explicitly",
    "no-global-closure-cache-replay-retry-result-reader-or-hidden-mutable-state-is-permitted",
)
S1_JP_TIME_AND_REFINEMENT_RULES = (
    "derive-physical-elapsed-time-only-from-the-S1-JO-step-time",
    "levels-two-four-eight-partition-the-same-physical-window-into-equal-contiguous-subwindows",
    "the-registered-S-H-boundary-is-already-materialized-and-is-never-reapplied-inside-a-subwindow",
    "contact-values-remain-constant-and-the-distribution-is-neither-merged-dropped-delayed-nor-replayed",
    "the-final-field-time-and-last-distribution-equal-the-complete-original-S1-JO-window",
    "one-refinement-failure-invalidates-the-complete-adapter-result-without-fallback-to-another-level",
)
S1_JP_VALIDATION_ORDER = (
    "exact-adapter-role-private-schema-configuration-digest-and-refinement",
    "four-field-model-invocation-type-geometry-node-order-distribution-and-time",
    "role-owned-state-provenance-and-kernel-calculator-or-fixed-adapter-identity",
    "deterministic-input-conversion-and-complete-subwindow-plan",
    "kernel-output-shape-finiteness-role-invariants-time-and-state-return",
    "canonical-complete-output-digest-and-atomic-publication",
)
S1_JP_NEUTRAL_AND_FAILURE_RULES = (
    "zero-contact-intervals-remain-explicit-model-intervals-and-are-never-short-circuited-as-no-ops",
    "where-an-existing-kernel-has-a-neutral-or-null-arm-path-the-adapter-must-delegate-to-that-path-without-reimplementation",
    "an-ablation-control-may-remove-only-the-bound-model-specific-contribution-and-may-not-change-exposure-time-or-field-identity",
    "no-exception-may-trigger-clipping-renormalization-parameter-change-state-reset-retry-or-partial-carry",
    "any-adapter-error-blocks-that-complete-later-joint-comparison-case",
)
S1_JP_TECHNICAL_TEST_MATRIX = (
    ("T01", "source-digests-and-exact-four-value-S1-JO-schema"),
    ("T02", "six-distinct-role-context-schemas-and-kernel-identities"),
    ("T03", "B1-fixed-adapter-information-barrier-and-unchanged-return"),
    ("T04", "B2-complete-L-roundtrip-and-field-S-H-mapping"),
    ("T05", "B3-through-B5-embedded-M-roundtrip-and-calculator-identity"),
    ("T06", "B6-frozen-const-v-spec-and-M-roundtrip"),
    ("T07", "configuration-and-refinement-prebinding-without-fit"),
    ("T08", "integrity-orchestration-and-candidate-data-inaccessibility"),
    ("T09", "contiguous-subwindow-time-contact-and-boundary-rules"),
    ("T10", "complete-field-private-state-diagnostic-and-output-digest-schema"),
    ("T11", "neutral-delegation-and-zero-contact-not-short-circuited"),
    ("T12", "validation-order-and-atomic-fail-closed-output"),
    ("T13", "deterministic-tamper-evident-and-no-kernel-call"),
    ("T14", "no-adapter-runtime-profile-or-research-execution"),
)
S1_JP_FORBIDDEN_INTERPRETATIONS = (
    "implemented-executable-numerically-admissible-or-validated-baseline-adapter",
    "baseline-fit-closure-rejection-or-candidate-superiority",
    "runtime-readiness-or-completed-twenty-four-case-matrix",
    "memory-learning-semantics-consciousness-experience-understanding-organic-property-or-artificial-intelligence",
)
S1_JP_DECISION = (
    "SIX_PRIVATE_BASELINE_ADAPTER_BRIDGES_BOUND_NO_IMPLEMENTATION_OR_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1JPBaselineAdapterBridgeContract:
    contract_id: str
    source_s1jo_digest: str
    source_s1it_digest: str
    source_s1ja_digest: str
    common_invocation_schema: tuple[str, ...]
    private_context_schema: tuple[str, ...]
    adapter_bridges: tuple[tuple[str, tuple[str, ...], str, str, str, str], ...]
    output_schema: tuple[str, ...]
    information_barrier_rules: tuple[str, ...]
    time_and_refinement_rules: tuple[str, ...]
    validation_order: tuple[str, ...]
    neutral_and_failure_rules: tuple[str, ...]
    technical_test_matrix: tuple[tuple[str, str], ...]
    forbidden_interpretations: tuple[str, ...]
    adapter_role_count: int
    technical_test_count: int
    complete_bridge_contract_bound: bool
    adapter_context_implemented: bool
    adapters_implemented: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    private_adapter_implementation_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_JP_CONTRACT_ID
            or self.source_s1jo_digest != S1_JP_SOURCE_S1JO_DIGEST
            or self.source_s1it_digest != S1_JP_SOURCE_S1IT_DIGEST
            or self.source_s1ja_digest != S1_JP_SOURCE_S1JA_DIGEST
            or self.common_invocation_schema != S1_JP_COMMON_INVOCATION_SCHEMA
            or self.private_context_schema != S1_JP_PRIVATE_CONTEXT_SCHEMA
            or self.adapter_bridges != S1_JP_ADAPTER_BRIDGES
            or self.output_schema != S1_JP_OUTPUT_SCHEMA
            or self.information_barrier_rules != S1_JP_INFORMATION_BARRIER_RULES
            or self.time_and_refinement_rules != S1_JP_TIME_AND_REFINEMENT_RULES
            or self.validation_order != S1_JP_VALIDATION_ORDER
            or self.neutral_and_failure_rules != S1_JP_NEUTRAL_AND_FAILURE_RULES
            or self.technical_test_matrix != S1_JP_TECHNICAL_TEST_MATRIX
            or self.forbidden_interpretations != S1_JP_FORBIDDEN_INTERPRETATIONS
            or self.adapter_role_count != 6
            or self.technical_test_count != 14
            or self.complete_bridge_contract_bound is not True
            or any(
                value is not False
                for value in (
                    self.adapter_context_implemented,
                    self.adapters_implemented,
                    self.baseline_models_executed,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                )
            )
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.private_adapter_implementation_authorized_next_stage is not True
            or self.decision != S1_JP_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1JPBaselineAdapterBridgeContractError(
                "S1-JP weakened the private baseline adapter bridge"
            )


def build_dts1_s1jp_baseline_adapter_bridge_contract(
) -> DTS1S1JPBaselineAdapterBridgeContract:
    """Bind six private adapter bridges without constructing or running them."""

    source = build_dts1_s1jo_implementation_receipt()
    prior = build_dts1_s1it_private_adapter_contract()
    configuration = build_dts1_s1ja_finite_configuration_matrix_contract()
    values = {
        "contract_id": S1_JP_CONTRACT_ID,
        "source_s1jo_digest": source.receipt_digest,
        "source_s1it_digest": prior.contract_digest,
        "source_s1ja_digest": configuration.contract_digest,
        "common_invocation_schema": S1_JP_COMMON_INVOCATION_SCHEMA,
        "private_context_schema": S1_JP_PRIVATE_CONTEXT_SCHEMA,
        "adapter_bridges": S1_JP_ADAPTER_BRIDGES,
        "output_schema": S1_JP_OUTPUT_SCHEMA,
        "information_barrier_rules": S1_JP_INFORMATION_BARRIER_RULES,
        "time_and_refinement_rules": S1_JP_TIME_AND_REFINEMENT_RULES,
        "validation_order": S1_JP_VALIDATION_ORDER,
        "neutral_and_failure_rules": S1_JP_NEUTRAL_AND_FAILURE_RULES,
        "technical_test_matrix": S1_JP_TECHNICAL_TEST_MATRIX,
        "forbidden_interpretations": S1_JP_FORBIDDEN_INTERPRETATIONS,
        "adapter_role_count": len(S1_JP_ADAPTER_BRIDGES),
        "technical_test_count": len(S1_JP_TECHNICAL_TEST_MATRIX),
        "complete_bridge_contract_bound": True,
        "adapter_context_implemented": False,
        "adapters_implemented": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "private_adapter_implementation_authorized_next_stage": True,
        "decision": S1_JP_DECISION,
    }
    return DTS1S1JPBaselineAdapterBridgeContract(
        **values, contract_digest=_digest(values)
    )
