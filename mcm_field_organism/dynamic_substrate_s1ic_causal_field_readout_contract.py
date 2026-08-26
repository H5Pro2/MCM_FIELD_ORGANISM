"""Static S1-IC contract for a two-substep causal DTS-1 field readout."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json


class DTS1S1ICCausalFieldReadoutContractError(ValueError):
    """Raised when the closed S1-IC field-readout boundary is weakened."""


S1_IC_CONTRACT_ID = "dynamic-substrate.causal-field-readout.s1ic.v1"
S1_IC_SOURCE_S1IB_AUDIT_RECEIPT_DIGEST = (
    "55159311a95b555900632014d68b3534aeb958787e0e6bcfba4d3e32dfedb217"
)
S1_IC_CANDIDATE_ID = "DTS1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER"
S1_IC_READOUT_ID = "DTS1_TWO_SUBSTEP_FREE_REFRACTORY_CAUSAL_FIELD_READOUT"
S1_IC_ARM_IDS = (
    "F_HIGH_MORE_FREE_LESS_REFRACTORY",
    "R_HIGH_LESS_FREE_MORE_REFRACTORY",
)
S1_IC_CLOSED_PAIR_RULES = (
    "both-arms-start-from-value-identical-complete-field-S-and-H-prestates",
    "both-arms-start-with-identical-geometry-capacities-total-resource-and-conductive-binding",
    "only-the-valid-ledger-derived-free-versus-refractory-partition-differs",
    "both-arms-use-identical-contact-event-boundaries-field-configs-step-times-and-DTS1-rates",
    "each-substep-reads-one-complete-closed-field-anatomy-prestate-and-commits-atomically",
    "no-arm-label-result-value-or-poststate-may-enter-a-proposal",
)
S1_IC_TWO_SUBSTEP_CAUSAL_CHAIN = (
    "substep-1-participation-is-identical-because-S0-is-identical",
    "substep-1-applied-adapter-is-bit-exact-because-conductive-binding-b0-is-identical",
    "substep-1-complete-field-proposal-S1-H1-is-bit-exact-between-arms",
    "substep-1-engagement-F_HIGH-is-strictly-greater-than-R_HIGH-as-established-by-S1IB",
    "substep-1-committed-conductive-binding-b1-F_HIGH-is-strictly-greater-than-b1-R_HIGH",
    "substep-2-complete-field-prestate-S1-H1-remains-bit-exact-between-arms",
    "substep-2-applied-adapter-rate-F_HIGH-is-strictly-greater-than-R_HIGH-from-b1-only",
    "substep-2-field-proposals-may-first-diverge-through-their-prestate-b1-adapters",
    "substep-2-resource-proposals-cannot-affect-the-concurrent-substep-2-field-proposals",
    "no-third-substep-is-part-of-the-minimal-readout",
)
S1_IC_FIELD_OBSERVABLES = (
    "canonical-complete-S-and-H-vectors-after-each-substep",
    "canonical-applied-edge-rate-vector-in-each-substep",
    "canonical-target-edge-contrast-C=S_second_endpoint-minus-S_first_endpoint",
    "maximum-absolute-component-separation-of-the-two-complete-substep-2-S-H-vectors",
    "all-substep-resource-transfers-and-local-global-ledger-residuals-as-causal-diagnostics",
)
S1_IC_DIRECTION_RULES = (
    "the-next-fixture-must-bind-a-positive-target-edge-contrast-before-substep-2",
    "the-next-fixture-must-analytically-preregister-the-sign-and-nonzero-margin-before-execution",
    "with-the-bound-positive-contrast-the-higher-F_HIGH-adapter-must-produce-strictly-smaller-substep-2-contrast-than-R_HIGH",
    "complete-substep-2-S-H-separation-must-exceed-a-preregistered-float64-floor",
    "no-observed-direction-threshold-or-fixture-value-may-be-selected-after-execution",
)
S1_IC_CONTROL_CASES = (
    (
        "N01_EQUAL_PARTITION_TWO_SUBSTEP_REPEAT",
        "value-identical-anatomies-require-bit-exact-complete-pairs-through-both-substeps",
    ),
    (
        "N02_A0_TWO_SUBSTEP_CONTROL",
        "backreaction-disabled-arms-require-bit-exact-neutral-field-output-in-both-substeps",
    ),
    (
        "N03_FROZEN_INITIAL_ADAPTER_CONTROL",
        "one-preprobe-fixed-b0-adapter-requires-bit-exact-field-output-between-arms-in-both-substeps",
    ),
    (
        "N04_MATCHED_ZERO_H_CONTROL",
        "the-directed-readout-must-remain-preregistered-with-H0-exactly-zero-in-both-arms",
    ),
)
S1_IC_BASELINE_COUNTERPREDICTIONS = (
    (
        "fixed-adapter-and-frozen-e1",
        "one-b0-adapter-cannot-diverge-after-the-arm-identical-first-field-state",
    ),
    (
        "leaky-trace-and-integrator",
        "identical-field-history-through-substep-1-and-identical-substep-2-input-cannot-create-an-arm-difference",
    ),
    (
        "dynamic-two-state-e1",
        "identical-b0-and-total-resource-collapse-the-initial-arms-and-therefore-predict-identical-b1-and-field-readout",
    ),
    (
        "f3-and-const-v",
        "unchanged-spatial-total-without-the-local-partition-coordinate-predicts-no-arm-specific-b1-adapter",
    ),
    (
        "fast-afterimage",
        "bit-exact-H-through-substep-1-and-the-zero-H-control-cannot-explain-the-substep-2-arm-separation",
    ),
)
S1_IC_ACCEPTANCE_RULES = (
    "active-pair-and-all-four-controls-are-complete-for-exactly-two-substeps",
    "all-closed-pair-and-first-substep-exact-identities-pass",
    "b1-and-substep-2-applied-adapter-have-the-preregistered-strict-direction",
    "substep-2-field-separation-exceeds-its-preregistered-floor-and-has-the-preregistered-contrast-direction",
    "all-input-output-field-domains-and-resource-ledgers-remain-valid",
    "all-five-baseline-counterpredictions-remain-unaugmented-and-distinct",
    "one-failure-makes-the-whole-readout-audit-STOPP-with-no-partial-PASS",
)
S1_IC_STOPP_CONDITIONS = (
    "any-unmatched-field-binding-capacity-total-contact-time-config-rate-or-event-boundary",
    "substep-1-adapter-or-complete-field-output-is-not-bit-exact-between-active-arms",
    "substep-1-b1-or-substep-2-applied-adapter-lacks-the-preregistered-direction",
    "substep-2-field-separation-is-at-or-below-floor-or-has-the-wrong-contrast-direction",
    "substep-2-resource-poststate-or-any-third-substep-is-used-to-explain-the-readout",
    "any-equal-partition-A0-frozen-adapter-or-zero-H-control-fails",
    "any-field-domain-resource-ledger-atomicity-or-determinism-failure",
    "any-baseline-receives-arm-label-free-refractory-coordinate-or-per-arm-fit",
    "result-dependent-fixture-threshold-step-rate-retry-or-partial-output",
    "runtime-coupling-unregistered-execution-or-research-field-use",
)
S1_IC_OUTPUT_SCHEMA = (
    "one-atomic-PASS-or-STOPP-decision",
    "complete-two-substep-field-anatomy-records-for-both-active-arms",
    "first-substep-field-and-adapter-exact-identity-booleans",
    "b1-and-second-substep-adapter-direction-records",
    "second-substep-complete-S-H-separation-contrast-direction-and-roundoff-floor",
    "four-complete-control-records-and-five-static-baseline-records",
    "field-resource-step-counts-and-one-canonical-SHA256-receipt",
)
S1_IC_FORBIDDEN_INTERPRETATIONS = (
    "attenuation-interference-release-reuse-or-material-evidence",
    "general-field-performance-or-baseline-superiority",
    "runtime-readiness-or-research-probe-authorization",
    "memory-learning-semantics-inner-context-organization-or-self-regulation",
    "organism-artificial-intelligence-new-natural-law-or-general-capability",
)
S1_IC_DECISION = "DTS1_TWO_SUBSTEP_CAUSAL_FIELD_READOUT_CONTRACT_BOUND"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1ICCausalFieldReadoutContract:
    contract_id: str
    source_s1ib_audit_receipt_digest: str
    candidate_id: str
    readout_id: str
    arm_ids: tuple[str, ...]
    closed_pair_rules: tuple[str, ...]
    two_substep_causal_chain: tuple[str, ...]
    field_observables: tuple[str, ...]
    direction_rules: tuple[str, ...]
    control_cases: tuple[tuple[str, str], ...]
    baseline_counterpredictions: tuple[tuple[str, str], ...]
    acceptance_rules: tuple[str, ...]
    stopp_conditions: tuple[str, ...]
    output_schema: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    exact_two_substeps_required: bool
    first_substep_field_identity_required: bool
    second_substep_causal_readout_required: bool
    complete_baseline_set_required: bool
    atomic_decision_required: bool
    finite_fixture_audit_contract_authorized_next_stage: bool
    fixture_values_selected: bool
    equation_added_or_changed: bool
    readout_implemented: bool
    readout_executed: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    field_effect_proven: bool
    broader_function_proven: bool
    claims_permitted: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_IC_CONTRACT_ID
            or self.source_s1ib_audit_receipt_digest
            != S1_IC_SOURCE_S1IB_AUDIT_RECEIPT_DIGEST
            or self.candidate_id != S1_IC_CANDIDATE_ID
            or self.readout_id != S1_IC_READOUT_ID
            or self.arm_ids != S1_IC_ARM_IDS
            or self.closed_pair_rules != S1_IC_CLOSED_PAIR_RULES
            or self.two_substep_causal_chain != S1_IC_TWO_SUBSTEP_CAUSAL_CHAIN
            or self.field_observables != S1_IC_FIELD_OBSERVABLES
            or self.direction_rules != S1_IC_DIRECTION_RULES
            or self.control_cases != S1_IC_CONTROL_CASES
            or self.baseline_counterpredictions != S1_IC_BASELINE_COUNTERPREDICTIONS
            or self.acceptance_rules != S1_IC_ACCEPTANCE_RULES
            or self.stopp_conditions != S1_IC_STOPP_CONDITIONS
            or self.output_schema != S1_IC_OUTPUT_SCHEMA
            or self.forbidden_interpretations != S1_IC_FORBIDDEN_INTERPRETATIONS
            or any(
                value is not True
                for value in (
                    self.exact_two_substeps_required,
                    self.first_substep_field_identity_required,
                    self.second_substep_causal_readout_required,
                    self.complete_baseline_set_required,
                    self.atomic_decision_required,
                    self.finite_fixture_audit_contract_authorized_next_stage,
                )
            )
            or any(
                value is not False
                for value in (
                    self.fixture_values_selected,
                    self.equation_added_or_changed,
                    self.readout_implemented,
                    self.readout_executed,
                    self.baseline_models_executed,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                    self.field_effect_proven,
                    self.broader_function_proven,
                    self.claims_permitted,
                )
            )
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.decision != S1_IC_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1ICCausalFieldReadoutContractError(
                "S1-IC weakened the two-substep causal field-readout boundary"
            )


def build_dts1_s1ic_causal_field_readout_contract(
) -> DTS1S1ICCausalFieldReadoutContract:
    """Bind the causal readout without selecting values or executing fields."""

    values = {
        "contract_id": S1_IC_CONTRACT_ID,
        "source_s1ib_audit_receipt_digest": S1_IC_SOURCE_S1IB_AUDIT_RECEIPT_DIGEST,
        "candidate_id": S1_IC_CANDIDATE_ID,
        "readout_id": S1_IC_READOUT_ID,
        "arm_ids": S1_IC_ARM_IDS,
        "closed_pair_rules": S1_IC_CLOSED_PAIR_RULES,
        "two_substep_causal_chain": S1_IC_TWO_SUBSTEP_CAUSAL_CHAIN,
        "field_observables": S1_IC_FIELD_OBSERVABLES,
        "direction_rules": S1_IC_DIRECTION_RULES,
        "control_cases": S1_IC_CONTROL_CASES,
        "baseline_counterpredictions": S1_IC_BASELINE_COUNTERPREDICTIONS,
        "acceptance_rules": S1_IC_ACCEPTANCE_RULES,
        "stopp_conditions": S1_IC_STOPP_CONDITIONS,
        "output_schema": S1_IC_OUTPUT_SCHEMA,
        "forbidden_interpretations": S1_IC_FORBIDDEN_INTERPRETATIONS,
        "exact_two_substeps_required": True,
        "first_substep_field_identity_required": True,
        "second_substep_causal_readout_required": True,
        "complete_baseline_set_required": True,
        "atomic_decision_required": True,
        "finite_fixture_audit_contract_authorized_next_stage": True,
        "fixture_values_selected": False,
        "equation_added_or_changed": False,
        "readout_implemented": False,
        "readout_executed": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "field_effect_proven": False,
        "broader_function_proven": False,
        "claims_permitted": False,
        "decision": S1_IC_DECISION,
    }
    return DTS1S1ICCausalFieldReadoutContract(
        **values,
        contract_digest=_digest(values),
    )
