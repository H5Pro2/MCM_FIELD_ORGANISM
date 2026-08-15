"""Static S1-ID fixture and audit contract for the S1-IC field readout."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json


class DTS1S1IDCausalFieldReadoutAuditContractError(ValueError):
    """Raised when the finite S1-ID readout boundary is weakened."""


S1_ID_CONTRACT_ID = "dynamic-substrate.causal-field-readout-audit.s1id.v1"
S1_ID_SOURCE_S1IC_CONTRACT_DIGEST = (
    "98a376eee3bb141d4a058202cd8759bd34324b80ecaa19a333491148a18ca5e9"
)
S1_ID_CANDIDATE_ID = "DTS1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER"
S1_ID_TARGET_MODULE = (
    "mcm_field_organism.dynamic_substrate_dts1_causal_field_readout_audit"
)
S1_ID_SYNTHETIC_FIXTURE = (
    ("geometry", "two-node-open-line-with-one-canonical-edge"),
    ("node_capacities", "(1.0,1.0)"),
    ("initial_S", "(-1.0,1.0)"),
    ("initial_H_main", "(-0.2,0.2)"),
    ("initial_H_zero_control", "(0.0,0.0)"),
    ("constant_receptor_contact", "(0.0,0.0)"),
    ("response_time", "1.0 synthetic-time-units"),
    ("afterimage_time", "0.5 synthetic-time-units"),
    ("dissipation_rate", "0.0 inverse-synthetic-time"),
    ("substep_duration", "0.5 synthetic-time-units"),
    ("substep_count", "2"),
    ("dts1_rates", "(binding=0.4,turnover=0.3,recovery=0.2)"),
    ("conductive_bound_both_arms", "0.4"),
    ("F_HIGH_refractory", "0.2"),
    ("R_HIGH_refractory", "0.8"),
    ("F_HIGH_derived_free_per_node", "0.7"),
    ("R_HIGH_derived_free_per_node", "0.3999999999999999"),
)
S1_ID_ANALYTIC_PREFLIGHT = (
    ("substep_1_participation", "1.0"),
    ("substep_1_adapter_rate_both_arms", "1.2"),
    ("substep_1_F_HIGH_engagement", "0.2537769456908254"),
    ("substep_1_R_HIGH_engagement", "0.14501539753761447"),
    ("substep_1_turnover_both_arms", "0.05571680942997688"),
    ("substep_1_b1_F_HIGH", "0.5980601362608484"),
    ("substep_1_b1_R_HIGH", "0.48929858810763766"),
    ("substep_1_field_contrast_both_arms", "0.3653670481054693"),
    ("substep_1_H_contrast_main_both_arms", "0.6762829682363132"),
    ("substep_1_H_contrast_zero_control", "0.5291311917677363"),
    ("substep_2_adapter_rate_F_HIGH", "1.299030068130424"),
    ("substep_2_adapter_rate_R_HIGH", "1.2446492940538187"),
    ("substep_2_field_contrast_F_HIGH", "0.06045337407166922"),
    ("substep_2_field_contrast_R_HIGH", "0.06383190638930979"),
    ("substep_2_contrast_margin_R_minus_F", "0.0033785323176405632"),
    ("substep_2_complete_SH_separation_main", "0.0016892661588202816"),
    ("substep_2_complete_SH_separation_zero_H", "0.0016892661588202816"),
    ("roundoff_floor", "1.1368683772161603e-13"),
)
S1_ID_AUDIT_CASES = (
    (
        "C01_ACTIVE_TWO_SUBSTEP_READOUT",
        "F_HIGH-versus-R_HIGH-with-main-H-and-active-backreaction",
        4,
    ),
    (
        "N01_EQUAL_PARTITION_TWO_SUBSTEP_REPEAT",
        "two-F_HIGH-arms-require-bit-exact-complete-pairs-through-both-substeps",
        4,
    ),
    (
        "N02_A0_TWO_SUBSTEP_CONTROL",
        "F_HIGH-versus-R_HIGH-with-backreaction-disabled-in-both-substeps",
        4,
    ),
    (
        "N03_FROZEN_INITIAL_ADAPTER_CONTROL",
        "F_HIGH-versus-R_HIGH-reuse-their-original-b0-anatomies-for-substep-2",
        4,
    ),
    (
        "N04_MATCHED_ZERO_H_CONTROL",
        "F_HIGH-versus-R_HIGH-with-H0-exactly-zero-and-active-backreaction",
        4,
    ),
)
S1_ID_CAUSAL_DECISION_RULES = (
    "C01-substep-1-applied-adapter-rates-are-bit-exact-1.2",
    "C01-substep-1-complete-S-H-field-vectors-are-bit-exact-between-arms",
    "C01-substep-1-b1-values-match-preregistration-within-roundoff-floor-and-F_HIGH-is-greater",
    "C01-substep-2-field-prestates-remain-bit-exact-between-arms",
    "C01-substep-2-adapter-rates-match-preregistration-within-floor-and-F_HIGH-is-greater",
    "C01-substep-2-contrasts-match-preregistration-within-floor-and-C_F_HIGH-is-strictly-less-than-C_R_HIGH",
    "C01-substep-2-complete-S-H-separation-matches-preregistration-within-floor-and-exceeds-floor",
    "N01-complete-field-anatomy-and-passive-ledger-results-are-bit-exact-at-both-substeps",
    "N02-complete-field-vectors-are-bit-exact-between-arms-at-both-substeps",
    "N03-complete-field-vectors-and-applied-b0-adapters-are-bit-exact-at-both-substeps",
    "N04-repeats-the-preregistered-C01-adapter-contrast-direction-and-complete-separation-with-H0-zero",
    "all-field-values-remain-in-domain-and-all-resource-ledger-residuals-remain-within-floor",
    "second-complete-audit-receipt-is-bit-exact-to-the-first",
)
S1_ID_FROZEN_CONTROL_RULES = (
    "N03-substep-1-runs-the-normal-matched-b0-active-proposal-in-both-arms",
    "N03-substep-2-uses-the-bit-exact-substep-1-field-output-but-the-original-valid-arm-anatomy",
    "both-original-anatomies-have-identical-b0-so-the-substep-2-applied-adapters-are-bit-exact",
    "N03-resource-results-are-diagnostic-only-and-are-not-carried-across-the-frozen-control-boundary",
    "the-frozen-control-is-not-a-runtime-mode-and-cannot-enter-the-active-pair",
)
S1_ID_BASELINE_RECORD_RULES = (
    "emit-five-static-state-space-records-from-S1IC-without-executing-baseline-models",
    "A0-and-frozen-b0-are-the-only-executed-field-countercontrols",
    "no-baseline-receives-arm-id-free-refractory-coordinate-or-per-arm-fit",
)
S1_ID_ACCEPTANCE_RULES = (
    "all-five-cases-complete-in-fixed-order-with-20-technical-field-calls",
    "all-thirteen-causal-decision-rules-pass",
    "all-static-baseline-records-remain-unaugmented-and-complete",
    "second-identical-20-call-audit-has-the-same-canonical-receipt",
    "one-failure-makes-the-whole-double-audit-STOPP-with-no-partial-PASS",
)
S1_ID_STOPP_CONDITIONS = (
    "fixture-arm-case-substep-event-boundary-or-call-count-drift",
    "any-first-substep-adapter-or-complete-field-identity-failure",
    "any-b1-second-adapter-contrast-or-complete-separation-direction-or-margin-failure",
    "any-equal-partition-A0-frozen-b0-or-zero-H-control-failure",
    "any-current-substep-resource-poststate-or-third-substep-used-for-field-attribution",
    "any-field-domain-resource-ledger-atomicity-or-determinism-failure",
    "baseline-state-augmentation-or-baseline-model-execution-beyond-A0-and-frozen-b0",
    "result-dependent-fixture-threshold-rate-step-retry-or-partial-output",
    "more-than-40-technical-field-calls-runtime-integration-or-research-execution",
)
S1_ID_OUTPUT_SCHEMA = (
    "one-atomic-PASS-or-STOPP-decision",
    "five-complete-two-arm-two-substep-case-records",
    "canonical-S-H-vectors-anatomy-digests-adapter-rates-and-resource-ledgers",
    "first-substep-exact-identities-b1-values-and-second-substep-prestate-identities",
    "second-substep-contrasts-complete-S-H-separations-and-roundoff-floor",
    "five-static-baseline-records-and-all-control-exactness-booleans",
    "first-repeat-and-audit-receipts-with-field-and-research-step-counts",
)
S1_ID_FORBIDDEN_INTERPRETATIONS = (
    "attenuation-interference-release-reuse-or-material-evidence",
    "general-field-performance-baseline-superiority-or-runtime-readiness",
    "memory-learning-semantics-inner-context-organization-or-self-regulation",
    "organism-artificial-intelligence-new-natural-law-or-general-capability",
)
S1_ID_DECISION = "DTS1_FINITE_CAUSAL_FIELD_READOUT_AUDIT_CONTRACT_BOUND"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1IDCausalFieldReadoutAuditContract:
    contract_id: str
    source_s1ic_contract_digest: str
    candidate_id: str
    target_module: str
    synthetic_fixture: tuple[tuple[str, str], ...]
    analytic_preflight: tuple[tuple[str, str], ...]
    audit_cases: tuple[tuple[str, str, int], ...]
    causal_decision_rules: tuple[str, ...]
    frozen_control_rules: tuple[str, ...]
    baseline_record_rules: tuple[str, ...]
    acceptance_rules: tuple[str, ...]
    stopp_conditions: tuple[str, ...]
    output_schema: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    float64_epsilon_multiplier: int
    field_calls_per_audit: int
    maximum_double_audit_field_calls: int
    exact_two_substeps_per_arm: bool
    analytic_direction_and_margin_bound: bool
    exact_controls_required: bool
    atomic_decision_required: bool
    audit_implementation_and_execution_authorized_next_stage: bool
    synthetic_values_bound: bool
    equation_added_or_changed: bool
    audit_implemented: bool
    audit_executed: bool
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
            self.contract_id != S1_ID_CONTRACT_ID
            or self.source_s1ic_contract_digest != S1_ID_SOURCE_S1IC_CONTRACT_DIGEST
            or self.candidate_id != S1_ID_CANDIDATE_ID
            or self.target_module != S1_ID_TARGET_MODULE
            or self.synthetic_fixture != S1_ID_SYNTHETIC_FIXTURE
            or self.analytic_preflight != S1_ID_ANALYTIC_PREFLIGHT
            or self.audit_cases != S1_ID_AUDIT_CASES
            or self.causal_decision_rules != S1_ID_CAUSAL_DECISION_RULES
            or self.frozen_control_rules != S1_ID_FROZEN_CONTROL_RULES
            or self.baseline_record_rules != S1_ID_BASELINE_RECORD_RULES
            or self.acceptance_rules != S1_ID_ACCEPTANCE_RULES
            or self.stopp_conditions != S1_ID_STOPP_CONDITIONS
            or self.output_schema != S1_ID_OUTPUT_SCHEMA
            or self.forbidden_interpretations != S1_ID_FORBIDDEN_INTERPRETATIONS
            or self.float64_epsilon_multiplier != 512
            or self.field_calls_per_audit != 20
            or self.maximum_double_audit_field_calls != 40
            or any(
                value is not True
                for value in (
                    self.exact_two_substeps_per_arm,
                    self.analytic_direction_and_margin_bound,
                    self.exact_controls_required,
                    self.atomic_decision_required,
                    self.audit_implementation_and_execution_authorized_next_stage,
                    self.synthetic_values_bound,
                )
            )
            or any(
                value is not False
                for value in (
                    self.equation_added_or_changed,
                    self.audit_implemented,
                    self.audit_executed,
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
            or self.decision != S1_ID_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1IDCausalFieldReadoutAuditContractError(
                "S1-ID weakened the finite causal field-readout audit boundary"
            )


def build_dts1_s1id_causal_field_readout_audit_contract(
) -> DTS1S1IDCausalFieldReadoutAuditContract:
    """Bind one finite double audit without implementing or executing fields."""

    values = {
        "contract_id": S1_ID_CONTRACT_ID,
        "source_s1ic_contract_digest": S1_ID_SOURCE_S1IC_CONTRACT_DIGEST,
        "candidate_id": S1_ID_CANDIDATE_ID,
        "target_module": S1_ID_TARGET_MODULE,
        "synthetic_fixture": S1_ID_SYNTHETIC_FIXTURE,
        "analytic_preflight": S1_ID_ANALYTIC_PREFLIGHT,
        "audit_cases": S1_ID_AUDIT_CASES,
        "causal_decision_rules": S1_ID_CAUSAL_DECISION_RULES,
        "frozen_control_rules": S1_ID_FROZEN_CONTROL_RULES,
        "baseline_record_rules": S1_ID_BASELINE_RECORD_RULES,
        "acceptance_rules": S1_ID_ACCEPTANCE_RULES,
        "stopp_conditions": S1_ID_STOPP_CONDITIONS,
        "output_schema": S1_ID_OUTPUT_SCHEMA,
        "forbidden_interpretations": S1_ID_FORBIDDEN_INTERPRETATIONS,
        "float64_epsilon_multiplier": 512,
        "field_calls_per_audit": 20,
        "maximum_double_audit_field_calls": 40,
        "exact_two_substeps_per_arm": True,
        "analytic_direction_and_margin_bound": True,
        "exact_controls_required": True,
        "atomic_decision_required": True,
        "audit_implementation_and_execution_authorized_next_stage": True,
        "synthetic_values_bound": True,
        "equation_added_or_changed": False,
        "audit_implemented": False,
        "audit_executed": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "field_effect_proven": False,
        "broader_function_proven": False,
        "claims_permitted": False,
        "decision": S1_ID_DECISION,
    }
    return DTS1S1IDCausalFieldReadoutAuditContract(
        **values,
        contract_digest=_digest(values),
    )
