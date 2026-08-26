"""Static S1-IJ finite fixture contract for the S1-II interference audit."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json


class DTS1S1IJInterferenceAuditContractError(ValueError):
    """Raised when the finite S1-IJ interference boundary is weakened."""


S1_IJ_CONTRACT_ID = "dynamic-substrate.local-aba-interference-audit.s1ij.v1"
S1_IJ_SOURCE_S1II_CONTRACT_DIGEST = (
    "888c5bfcb525f44439f85f6e9b4664616013552c72ed86e8cd3bb141ddd8a60f"
)
S1_IJ_CANDIDATE_ID = "DTS1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER"
S1_IJ_TARGET_MODULE = "mcm_field_organism.dynamic_substrate_dts1_interference_audit"
S1_IJ_SYNTHETIC_FIXTURE = (
    ("geometry", "open-line-node-a-node-b-node-c-with-A=(a,b)-and-B=(b,c)"),
    ("node_capacities", "(node-a=1.0,node-b=1.0,node-c=1.0)"),
    ("initial_conductive_bound", "(A=0.2,B=0.2)"),
    ("initial_refractory", "(A=0.1,B=0.1)"),
    ("initial_derived_free", "(node-a=0.85,node-b=0.7,node-c=0.85)"),
    ("A_participation", "(A=1.0,B=0.0)"),
    ("B_participation", "(A=0.0,B=1.0)"),
    ("gap_participation", "(A=0.0,B=0.0)"),
    ("interval_duration", "0.5 synthetic-time-units"),
    ("dts1_rates", "(binding=0.4,turnover=0.3,recovery=0.2)"),
    ("common_probe_S", "(node-a=-1.0,node-b=0.0,node-c=1.0)"),
    ("common_probe_H", "(node-a=-0.2,node-b=0.0,node-c=0.2)"),
    ("matched_zero_H", "(node-a=0.0,node-b=0.0,node-c=0.0)"),
    ("common_probe_contact", "zero-at-all-three-nodes"),
    ("probe_duration", "0.5 synthetic-time-units"),
    ("field_response_time", "1.0 synthetic-time-units"),
    ("afterimage_time", "0.5 synthetic-time-units"),
    ("field_leak_rate", "0.0"),
)
S1_IJ_ANALYTIC_RESOURCE_PREFLIGHT = (
    ("alpha_binding", "0.18126924692201812"),
    ("alpha_turnover", "0.1392920235749422"),
    ("alpha_recovery", "0.09516258196404043"),
    ("common_after_first_A_state_bA_uA_bB_uB", "(0.4259185409758369,0.11834214651858439,0.17214159528501158,0.11834214651858439)"),
    ("first_A_engagement", "0.2537769456908254"),
    ("middle_B_engagement_ABA", "0.21122499977283485"),
    ("middle_B_engagement_gap", "0.0"),
    ("prefinal_ABA_state_bA_uA_bB_uB", "(0.3665914855252257,0.1664074577513204,0.35938864390917846,0.13105835344937714)"),
    ("prefinal_gap_state_bA_uA_bB_uB", "(0.3665914855252257,0.1664074577513204,0.1481636441363436,0.13105835344937714)"),
    ("prefinal_shared_free_ABA", "0.4882770296824491"),
    ("prefinal_shared_free_gap", "0.5938895295688666"),
    ("shared_free_deficit", "0.10561249988641752"),
    ("final_A_engagement_ABA", "0.1770192189197149"),
    ("final_A_engagement_gap", "0.21530781555964015"),
    ("final_A_engagement_margin", "0.03828859663992526"),
    ("final_A_node_admissions_ABA", "(1.0,1.0,1.0)"),
    ("final_A_node_admissions_gap", "(1.0,1.0,1.0)"),
    ("postsequence_ABA_state_bA_uA_bB_uB", "(0.4925474346007877,0.2016349642577856,0.3093286724492147,0.1686464736071424)"),
    ("postsequence_gap_state_bA_uA_bB_uB", "(0.5308360312407131,0.2016349642577856,0.12752563032435466,0.13922451595916752)"),
)
S1_IJ_ANALYTIC_FIELD_PREFLIGHT = (
    ("postsequence_ABA_adapter_rates_A_B", "(1.246273717300394,1.1546643362246074)"),
    ("postsequence_gap_adapter_rates_A_B", "(1.2654180156203565,1.0637628151621774)"),
    ("ABA_main_S", "(-0.3285365618910417,-0.008877459964944538,0.3374140218559861)"),
    ("gap_main_S", "(-0.3296226851650033,-0.020205409157527568,0.34982809432253065)"),
    ("ABA_main_H", "(-0.42093511597049654,-0.005504159798256638,0.4264392757687532)"),
    ("gap_main_H", "(-0.4208720331765879,-0.012379420410438664,0.4332514535870263)"),
    ("ABA_zero_H_output_H", "(-0.3473592277362081,-0.0055041597982566325,0.3528633875344647)"),
    ("gap_zero_H_output_H", "(-0.3472961449422995,-0.01237942041043865,0.3596755653527379)"),
    ("A_edge_contrast_ABA", "0.31965910192609714"),
    ("A_edge_contrast_gap", "0.30941727600747576"),
    ("A_edge_contrast_margin_ABA_minus_gap", "0.010241825918621383"),
    ("complete_main_SH_separation", "0.012414072466544523"),
    ("complete_zero_H_SH_separation", "0.012414072466544523"),
    ("roundoff_floor", "1.1368683772161603e-13"),
)
S1_IJ_AUDIT_CASES = (
    ("C01_ACTIVE_ABA_VERSUS_A_GAP_A", "two-complete-three-interval-resource-arms-and-two-main-readouts", 6, 2),
    ("N01_VALUE_IDENTICAL_ABA_REPLAY", "two-complete-identical-ABA-sequences-and-readouts", 6, 2),
    ("N02_B_ZERO_EQUALS_MATCHED_GAP", "two-complete-zero-B-and-gap-resource-sequences", 6, 0),
    ("N03_A0_DISABLED_FIELD_READOUT", "two-postsequence-common-readouts-with-backreaction-disabled", 0, 2),
    ("N04_FROZEN_PRESEQUENCE_ADAPTER", "two-common-readouts-from-the-same-initial-anatomy", 0, 2),
    ("N05_MATCHED_ZERO_H", "two-active-postsequence-readouts-with-H-zero", 0, 2),
    ("N06_ZERO_A_PROBE_PARTICIPATION", "two-three-interval-arms-with-final-A-participation-zero", 6, 0),
)
S1_IJ_MATCHING_CHECKS = (
    "both-active-arms-have-bit-exact-initial-anatomy-first-A-contact-duration-rates-and-event-boundaries",
    "middle-B-and-gap-intervals-have-bit-exact-duration-rates-and-boundaries-with-only-participation-different",
    "both-final-A-probes-have-bit-exact-positive-participation-duration-rates-and-boundaries",
    "only-complete-valid-resource-poststates-carry-between-sequence-intervals",
    "all-main-and-zero-H-readouts-use-their-respective-bit-exact-common-field-prestates",
    "every-readout-resource-poststate-is-discarded-and-never-enters-a-sequence",
    "every-anatomy-has-valid-local-and-global-ledgers-and-all-values-are-synthetic",
)
S1_IJ_NUMERIC_DECISION_RULES = (
    "all-resource-state-transfer-shared-free-and-admission-values-match-the-preregistered-preflight-within-roundoff_floor",
    "middle-B-engagement-in-ABA-is-strictly-positive-and-gap-B-engagement-is-exactly-zero",
    "prefinal-shared-free-ABA-is-strictly-lower-than-gap-by-more-than-roundoff_floor",
    "final-A-engagement-ABA-is-strictly-lower-than-gap-by-more-than-roundoff_floor",
    "all-postsequence-adapter-and-complete-main-S-H-values-match-the-field-preflight-within-roundoff_floor",
    "A-edge-contrast-ABA-is-strictly-greater-than-gap-by-more-than-roundoff_floor",
    "complete-main-S-H-separation-matches-preflight-and-exceeds-roundoff_floor",
    "zero-H-S-vectors-match-main-S-vectors-within-roundoff_floor-and-complete-separation-exceeds-floor",
    "all-local-global-ledger-residuals-and-field-domain-residuals-remain-within-roundoff_floor",
    "N01-complete-sequence-and-readout-payloads-are-bit-exact",
    "N02-zero-B-and-gap-complete-resource-results-are-bit-exact",
    "N03-A0-common-field-outputs-are-bit-exact-between-postsequence-anatomies",
    "N04-frozen-initial-adapter-and-complete-field-outputs-are-bit-exact",
    "N06-final-A-engagement-is-exactly-zero-in-both-arms",
    "second-complete-audit-receipt-is-bit-exact-to-the-first",
)
S1_IJ_BASELINE_RECORD_RULES = (
    "emit-one-static-record-for-each-of-the-five-S1II-baseline-counterpredictions",
    "no-baseline-model-is-executed-or-fit-in-S1IJ-or-the-S1IK-harness",
    "N03-N04-and-N05-are-technical-controls-and-not-baseline-model-fits",
    "dynamic-two-state-E1-remains-explicitly-not-separated-by-interference-alone",
    "any-sequence-index-hidden-resource-coordinate-arm-label-or-per-arm-fit-is-STOPP",
)
S1_IJ_ACCEPTANCE_RULES = (
    "all-seven-cases-complete-in-fixed-order-with-twenty-four-direct-resource-and-ten-technical-field-calls",
    "all-matching-ledger-field-and-float64-preflight-checks-pass",
    "all-fifteen-numeric-decision-rules-pass",
    "all-five-static-baseline-records-remain-unaugmented-and-complete",
    "second-identical-thirty-four-call-audit-has-the-same-canonical-receipt",
    "one-failure-makes-the-whole-double-audit-STOPP-with-no-partial-PASS",
)
S1_IJ_STOPP_CONDITIONS = (
    "fixture-case-arm-sequence-checkpoint-or-call-order-drift",
    "any-geometry-matching-anatomy-carry-readout-discard-or-ledger-check-fails",
    "middle-B-shared-free-final-A-engagement-or-field-readout-deviates-beyond-floor-or-lacks-direction",
    "zero-H-readout-does-not-retain-the-preregistered-S-separation",
    "any-value-identical-B-zero-A0-frozen-adapter-or-zero-A-probe-control-fails",
    "any-output-resource-ledger-or-field-domain-residual-exceeds-floor",
    "baseline-state-is-augmented-executed-or-fit-separately-by-arm",
    "receipt-nondeterminism-result-dependent-adjustment-retry-or-partial-output",
    "more-than-48-direct-resource-or-20-technical-field-calls-in-the-double-audit",
    "any-runtime-integration-research-execution-or-claim-expansion",
)
S1_IJ_OUTPUT_SCHEMA = (
    "one-atomic-PASS-or-STOPP-decision",
    "fixed-fixture-source-contract-case-and-arm-order-record",
    "complete-three-interval-resource-transfer-and-anatomy-records-for-both-active-arms",
    "shared-free-final-A-engagement-admission-and-margin-records",
    "main-and-zero-H-common-readout-field-adapter-contrast-and-separation-records",
    "six-complete-control-records-and-five-static-baseline-records",
    "all-direction-margin-floor-ledger-and-field-validity-booleans",
    "first-and-second-receipt-digests-and-repeat-identity-boolean",
    "direct-resource-technical-field-and-research-field-counts-plus-one-canonical-audit-SHA256-receipt",
)
S1_IJ_FORBIDDEN_INTERPRETATIONS = (
    "release-reuse-recovery-material-or-general-performance-evidence",
    "standalone-nonreducibility-to-dynamic-two-state-E1",
    "physical-rate-or-timescale-estimation",
    "runtime-readiness-or-research-probe-authorization",
    "memory-learning-semantics-organization-organism-or-artificial-intelligence",
    "new-natural-law-or-general-substrate-capability",
)
S1_IJ_DECISION = "DTS1_FINITE_LOCAL_ABA_INTERFERENCE_AUDIT_CONTRACT_BOUND"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1IJInterferenceAuditContract:
    contract_id: str
    source_s1ii_contract_digest: str
    candidate_id: str
    target_module: str
    synthetic_fixture: tuple[tuple[str, str], ...]
    analytic_resource_preflight: tuple[tuple[str, str], ...]
    analytic_field_preflight: tuple[tuple[str, str], ...]
    audit_cases: tuple[tuple[str, str, int, int], ...]
    matching_checks: tuple[str, ...]
    numeric_decision_rules: tuple[str, ...]
    baseline_record_rules: tuple[str, ...]
    acceptance_rules: tuple[str, ...]
    stopp_conditions: tuple[str, ...]
    output_schema: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    float64_epsilon_multiplier: int
    direct_resource_calls_per_audit: int
    technical_field_calls_per_audit: int
    maximum_double_audit_direct_resource_calls: int
    maximum_double_audit_technical_field_calls: int
    maximum_research_field_steps: int
    exact_repeat_required: bool
    exact_controls_required: bool
    synthetic_values_bound: bool
    atomic_decision_required: bool
    audit_implementation_and_execution_authorized_next_stage: bool
    equation_added_or_changed: bool
    material_parameters_selected: bool
    audit_implemented: bool
    audit_executed: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    direct_resource_calls_executed: int
    technical_field_calls_executed: int
    research_field_steps_executed: int
    interference_proven: bool
    release_or_reuse_proven: bool
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
            self.contract_id != S1_IJ_CONTRACT_ID
            or self.source_s1ii_contract_digest != S1_IJ_SOURCE_S1II_CONTRACT_DIGEST
            or self.candidate_id != S1_IJ_CANDIDATE_ID
            or self.target_module != S1_IJ_TARGET_MODULE
            or self.synthetic_fixture != S1_IJ_SYNTHETIC_FIXTURE
            or self.analytic_resource_preflight != S1_IJ_ANALYTIC_RESOURCE_PREFLIGHT
            or self.analytic_field_preflight != S1_IJ_ANALYTIC_FIELD_PREFLIGHT
            or self.audit_cases != S1_IJ_AUDIT_CASES
            or self.matching_checks != S1_IJ_MATCHING_CHECKS
            or self.numeric_decision_rules != S1_IJ_NUMERIC_DECISION_RULES
            or self.baseline_record_rules != S1_IJ_BASELINE_RECORD_RULES
            or self.acceptance_rules != S1_IJ_ACCEPTANCE_RULES
            or self.stopp_conditions != S1_IJ_STOPP_CONDITIONS
            or self.output_schema != S1_IJ_OUTPUT_SCHEMA
            or self.forbidden_interpretations != S1_IJ_FORBIDDEN_INTERPRETATIONS
            or self.float64_epsilon_multiplier != 512
            or self.direct_resource_calls_per_audit != 24
            or self.technical_field_calls_per_audit != 10
            or self.maximum_double_audit_direct_resource_calls != 48
            or self.maximum_double_audit_technical_field_calls != 20
            or self.maximum_research_field_steps != 0
            or any(
                value is not True
                for value in (
                    self.exact_repeat_required,
                    self.exact_controls_required,
                    self.synthetic_values_bound,
                    self.atomic_decision_required,
                    self.audit_implementation_and_execution_authorized_next_stage,
                )
            )
            or any(
                value is not False
                for value in (
                    self.equation_added_or_changed,
                    self.material_parameters_selected,
                    self.audit_implemented,
                    self.audit_executed,
                    self.baseline_models_executed,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                    self.interference_proven,
                    self.release_or_reuse_proven,
                    self.broader_function_proven,
                    self.claims_permitted,
                )
            )
            or self.direct_resource_calls_executed != 0
            or self.technical_field_calls_executed != 0
            or self.research_field_steps_executed != 0
            or self.decision != S1_IJ_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1IJInterferenceAuditContractError(
                "S1-IJ weakened the finite local interference audit boundary"
            )


def build_dts1_s1ij_interference_audit_contract() -> DTS1S1IJInterferenceAuditContract:
    """Bind the finite interference double audit without implementing it."""

    values = {
        "contract_id": S1_IJ_CONTRACT_ID,
        "source_s1ii_contract_digest": S1_IJ_SOURCE_S1II_CONTRACT_DIGEST,
        "candidate_id": S1_IJ_CANDIDATE_ID,
        "target_module": S1_IJ_TARGET_MODULE,
        "synthetic_fixture": S1_IJ_SYNTHETIC_FIXTURE,
        "analytic_resource_preflight": S1_IJ_ANALYTIC_RESOURCE_PREFLIGHT,
        "analytic_field_preflight": S1_IJ_ANALYTIC_FIELD_PREFLIGHT,
        "audit_cases": S1_IJ_AUDIT_CASES,
        "matching_checks": S1_IJ_MATCHING_CHECKS,
        "numeric_decision_rules": S1_IJ_NUMERIC_DECISION_RULES,
        "baseline_record_rules": S1_IJ_BASELINE_RECORD_RULES,
        "acceptance_rules": S1_IJ_ACCEPTANCE_RULES,
        "stopp_conditions": S1_IJ_STOPP_CONDITIONS,
        "output_schema": S1_IJ_OUTPUT_SCHEMA,
        "forbidden_interpretations": S1_IJ_FORBIDDEN_INTERPRETATIONS,
        "float64_epsilon_multiplier": 512,
        "direct_resource_calls_per_audit": 24,
        "technical_field_calls_per_audit": 10,
        "maximum_double_audit_direct_resource_calls": 48,
        "maximum_double_audit_technical_field_calls": 20,
        "maximum_research_field_steps": 0,
        "exact_repeat_required": True,
        "exact_controls_required": True,
        "synthetic_values_bound": True,
        "atomic_decision_required": True,
        "audit_implementation_and_execution_authorized_next_stage": True,
        "equation_added_or_changed": False,
        "material_parameters_selected": False,
        "audit_implemented": False,
        "audit_executed": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "direct_resource_calls_executed": 0,
        "technical_field_calls_executed": 0,
        "research_field_steps_executed": 0,
        "interference_proven": False,
        "release_or_reuse_proven": False,
        "broader_function_proven": False,
        "claims_permitted": False,
        "decision": S1_IJ_DECISION,
    }
    return DTS1S1IJInterferenceAuditContract(
        **values,
        contract_digest=_digest(values),
    )
