"""Static S1-IG finite fixture contract for the S1-IF attenuation audit."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json


class DTS1S1IGAttenuationAuditContractError(ValueError):
    """Raised when the finite S1-IG attenuation boundary is weakened."""


S1_IG_CONTRACT_ID = "dynamic-substrate.repeated-contact-attenuation-audit.s1ig.v1"
S1_IG_SOURCE_S1IF_CONTRACT_DIGEST = (
    "bfad62c3da8abf8a7cf6777adb401b33b35135360bd566093631de124cd47f56"
)
S1_IG_CANDIDATE_ID = "DTS1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER"
S1_IG_TARGET_MODULE = "mcm_field_organism.dynamic_substrate_dts1_attenuation_audit"
S1_IG_SYNTHETIC_FIXTURE = (
    ("geometry", "one-isolated-open-canonical-edge-node-a-node-b"),
    ("node_capacities", "(node-a=1.0,node-b=1.0)"),
    ("initial_conductive_bound", "0.4"),
    ("initial_refractory", "0.2"),
    ("initial_derived_free_per_node", "0.7"),
    ("contact_count", "3"),
    ("contact_participation", "1.0"),
    ("contact_elapsed_time", "0.5 synthetic-time-units"),
    ("dts1_rates", "(binding=0.4,turnover=0.3,recovery=0.2)"),
    ("common_probe_S", "(node-a=-1.0,node-b=1.0)"),
    ("common_probe_H", "(node-a=-0.2,node-b=0.2)"),
    ("matched_zero_H", "(node-a=0.0,node-b=0.0)"),
    ("common_probe_contact", "zero-at-both-nodes"),
    ("probe_elapsed_time", "0.5 synthetic-time-units"),
    ("field_response_time", "1.0 synthetic-time-units"),
    ("afterimage_time", "0.5 synthetic-time-units"),
    ("field_leak_rate", "0.0"),
)
S1_IG_ANALYTIC_RESOURCE_PREFLIGHT = (
    ("alpha_binding", "0.18126924692201812"),
    ("alpha_turnover", "0.1392920235749422"),
    ("alpha_recovery", "0.09516258196404043"),
    ("precontact_b", "(0.4,0.5980601362608484,0.725980129434404)"),
    ("precontact_refractory", "(0.2,0.23668429303716879,0.2974658112006975)"),
    ("precontact_free_per_node", "(0.7,0.5826277853509914,0.48827702968244924)"),
    ("engagement", "(0.2537769456908254,0.21122499977283485,0.17701921891971492)"),
    ("turnover", "(0.05571680942997688,0.08330500659927924,0.1011232413041166)"),
    ("recovery", "(0.019032516392808087,0.022523488435750538,0.02830761463988615)"),
    ("postcontact_b3", "0.8018761070500025"),
    ("postcontact_refractory3", "0.37028143786492795"),
    ("postcontact_free3_per_node", "0.4139212275425348"),
    ("minimum_engagement_drop", "0.034205780853119926"),
)
S1_IG_ANALYTIC_FIELD_PREFLIGHT = (
    ("applied_adapter_rates", "(1.2,1.299030068130424,1.362990064717202)"),
    ("common_probe_S_contrasts", "(0.3653670481054693,0.33091858932072243,0.3104157086599864)"),
    ("common_probe_H_half_amplitudes", "(0.3381414841181566,0.32690821524509184,0.32001161853570353)"),
    ("zero_H_probe_H_half_amplitudes", "(0.26456559588386813,0.2533323270108034,0.24643573030141508)"),
    ("first_contrast_drop", "0.034448458784746894"),
    ("second_contrast_drop", "0.020502880660736023"),
    ("complete_contrast_drop", "0.054951339445482916"),
    ("A0_neutral_contrast_each_checkpoint", "0.44626032029685964"),
    ("frozen_initial_adapter_contrast_each_checkpoint", "0.3653670481054693"),
    ("roundoff_floor", "1.1368683772161603e-13"),
)
S1_IG_AUDIT_CASES = (
    ("C01_ACTIVE_THREE_CONTACT_ATTENUATION", "three-carried-anatomy-contact-steps-and-three-common-H-probe-readouts", 3, 3),
    ("N01_VALUE_IDENTICAL_REPLAY", "two-identical-contact-proposals-and-two-identical-common-probe-readouts", 2, 2),
    ("N02_A0_DISABLED_CANDIDATE", "three-common-probe-readouts-with-backreaction-disabled", 0, 3),
    ("N03_FROZEN_PRESEQUENCE_ADAPTER", "three-common-probe-readouts-from-the-same-initial-anatomy", 0, 3),
    ("N04_MATCHED_ZERO_H", "three-active-readouts-from-the-same-carried-precontact-anatomies-with-H-zero", 0, 3),
    ("N05_ZERO_PARTICIPATION", "three-carried-anatomy-resource-steps-at-zero-participation", 3, 0),
)
S1_IG_MATCHING_CHECKS = (
    "all-three-positive-contacts-have-bit-exact-participation-duration-rates-geometry-and-event-boundaries",
    "only-the-complete-valid-postcontact-anatomy-carries-to-the-next-positive-contact",
    "all-main-readouts-start-from-one-bit-exact-common-S-H-field-and-zero-contact",
    "all-zero-H-readouts-start-from-one-bit-exact-common-S-and-zero-H-field",
    "every-readout-resource-poststate-is-discarded-and-never-enters-the-contact-train",
    "every-precontact-and-postcontact-anatomy-has-valid-local-and-global-ledgers",
    "all-fixture-values-are-synthetic-and-not-material-parameter-estimates",
)
S1_IG_NUMERIC_DECISION_RULES = (
    "all-three-observed-engagement-values-match-the-preregistered-resource-preflight-within-roundoff_floor",
    "engagement-contact-1-is-strictly-greater-than-contact-2-and-contact-2-than-contact-3",
    "both-consecutive-engagement-drops-exceed-roundoff_floor",
    "all-three-applied-adapter-rates-and-common-probe-S-contrasts-match-the-field-preflight-within-roundoff_floor",
    "common-probe-contrast-1-is-strictly-greater-than-contrast-2-and-contrast-2-than-contrast-3",
    "both-consecutive-common-probe-contrast-drops-exceed-roundoff_floor",
    "zero-H-probe-S-contrasts-match-the-main-probe-S-contrasts-within-roundoff_floor-and-keep-the-strict-direction",
    "all-local-global-ledger-residuals-and-analytic-vector-residuals-remain-within-roundoff_floor",
    "N01-complete-resource-and-field-payloads-are-bit-exact",
    "N02-produces-the-same-neutral-contrast-at-all-three-checkpoints",
    "N03-produces-the-same-initial-adapter-and-contrast-at-all-three-checkpoints",
    "N05-produces-exact-zero-engagement-at-all-three-contacts",
    "second-complete-audit-receipt-is-bit-exact-to-the-first",
)
S1_IG_BASELINE_RECORD_RULES = (
    "emit-one-static-record-for-each-of-the-five-S1IF-baseline-counterpredictions",
    "no-baseline-model-is-executed-or-fit-in-S1IG-or-the-S1IH-harness",
    "N02-N03-and-N04-are-technical-controls-and-not-baseline-model-fits",
    "dynamic-two-state-E1-remains-explicitly-not-separated-by-attenuation-alone",
    "any-contact-index-hidden-resource-coordinate-arm-label-or-per-checkpoint-fit-is-STOPP",
)
S1_IG_ACCEPTANCE_RULES = (
    "all-six-cases-complete-in-fixed-order-with-eight-direct-resource-and-fourteen-technical-field-calls",
    "all-matching-ledger-and-float64-preflight-checks-pass",
    "all-thirteen-numeric-decision-rules-pass",
    "all-five-static-baseline-records-remain-unaugmented-and-complete",
    "second-identical-twenty-two-call-audit-has-the-same-canonical-receipt",
    "one-failure-makes-the-whole-double-audit-STOPP-with-no-partial-PASS",
)
S1_IG_STOPP_CONDITIONS = (
    "fixture-case-contact-checkpoint-or-call-order-drift",
    "any-contact-common-probe-anatomy-carry-discard-or-ledger-check-fails",
    "either-engagement-or-field-contrast-trajectory-deviates-beyond-floor-or-lacks-the-strict-direction",
    "the-zero-H-readout-deviates-from-the-preregistered-S-contrast-trajectory",
    "any-value-identical-A0-frozen-adapter-or-zero-participation-control-fails",
    "any-output-resource-ledger-or-field-domain-residual-exceeds-floor",
    "baseline-state-is-augmented-executed-or-fit-separately-by-checkpoint",
    "receipt-nondeterminism-result-dependent-adjustment-retry-or-partial-output",
    "more-than-16-direct-resource-or-28-technical-field-calls-in-the-double-audit",
    "any-runtime-integration-research-execution-or-claim-expansion",
)
S1_IG_OUTPUT_SCHEMA = (
    "one-atomic-PASS-or-STOPP-decision",
    "fixed-fixture-source-contract-and-case-order-record",
    "three-complete-contact-transfer-and-pre-post-anatomy-records",
    "main-and-zero-H-common-probe-field-adapter-and-contrast-records",
    "five-complete-control-records-and-five-static-baseline-records",
    "all-direction-margin-floor-ledger-and-field-validity-booleans",
    "first-and-second-receipt-digests-and-repeat-identity-boolean",
    "direct-resource-technical-field-and-research-field-counts-plus-one-canonical-audit-SHA256-receipt",
)
S1_IG_FORBIDDEN_INTERPRETATIONS = (
    "interference-release-reuse-recovery-material-or-general-performance-evidence",
    "standalone-nonreducibility-to-dynamic-two-state-E1",
    "physical-rate-or-timescale-estimation",
    "runtime-readiness-or-research-probe-authorization",
    "memory-learning-semantics-organization-organism-or-artificial-intelligence",
    "new-natural-law-or-general-substrate-capability",
)
S1_IG_DECISION = "DTS1_FINITE_REPEATED_CONTACT_ATTENUATION_AUDIT_CONTRACT_BOUND"


def _digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1IGAttenuationAuditContract:
    contract_id: str
    source_s1if_contract_digest: str
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
    attenuation_proven: bool
    broader_function_proven: bool
    claims_permitted: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {field.name: getattr(self, field.name) for field in fields(self) if field.name != "contract_digest"}
        if (
            self.contract_id != S1_IG_CONTRACT_ID
            or self.source_s1if_contract_digest != S1_IG_SOURCE_S1IF_CONTRACT_DIGEST
            or self.candidate_id != S1_IG_CANDIDATE_ID
            or self.target_module != S1_IG_TARGET_MODULE
            or self.synthetic_fixture != S1_IG_SYNTHETIC_FIXTURE
            or self.analytic_resource_preflight != S1_IG_ANALYTIC_RESOURCE_PREFLIGHT
            or self.analytic_field_preflight != S1_IG_ANALYTIC_FIELD_PREFLIGHT
            or self.audit_cases != S1_IG_AUDIT_CASES
            or self.matching_checks != S1_IG_MATCHING_CHECKS
            or self.numeric_decision_rules != S1_IG_NUMERIC_DECISION_RULES
            or self.baseline_record_rules != S1_IG_BASELINE_RECORD_RULES
            or self.acceptance_rules != S1_IG_ACCEPTANCE_RULES
            or self.stopp_conditions != S1_IG_STOPP_CONDITIONS
            or self.output_schema != S1_IG_OUTPUT_SCHEMA
            or self.forbidden_interpretations != S1_IG_FORBIDDEN_INTERPRETATIONS
            or self.float64_epsilon_multiplier != 512
            or self.direct_resource_calls_per_audit != 8
            or self.technical_field_calls_per_audit != 14
            or self.maximum_double_audit_direct_resource_calls != 16
            or self.maximum_double_audit_technical_field_calls != 28
            or self.maximum_research_field_steps != 0
            or any(value is not True for value in (
                self.exact_repeat_required,
                self.exact_controls_required,
                self.synthetic_values_bound,
                self.atomic_decision_required,
                self.audit_implementation_and_execution_authorized_next_stage,
            ))
            or any(value is not False for value in (
                self.equation_added_or_changed,
                self.material_parameters_selected,
                self.audit_implemented,
                self.audit_executed,
                self.baseline_models_executed,
                self.runtime_integration_present,
                self.research_execution_permitted,
                self.attenuation_proven,
                self.broader_function_proven,
                self.claims_permitted,
            ))
            or self.direct_resource_calls_executed != 0
            or self.technical_field_calls_executed != 0
            or self.research_field_steps_executed != 0
            or self.decision != S1_IG_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1IGAttenuationAuditContractError("S1-IG weakened the finite attenuation audit boundary")


def build_dts1_s1ig_attenuation_audit_contract() -> DTS1S1IGAttenuationAuditContract:
    """Bind the finite attenuation double audit without implementing it."""

    values = {
        "contract_id": S1_IG_CONTRACT_ID,
        "source_s1if_contract_digest": S1_IG_SOURCE_S1IF_CONTRACT_DIGEST,
        "candidate_id": S1_IG_CANDIDATE_ID,
        "target_module": S1_IG_TARGET_MODULE,
        "synthetic_fixture": S1_IG_SYNTHETIC_FIXTURE,
        "analytic_resource_preflight": S1_IG_ANALYTIC_RESOURCE_PREFLIGHT,
        "analytic_field_preflight": S1_IG_ANALYTIC_FIELD_PREFLIGHT,
        "audit_cases": S1_IG_AUDIT_CASES,
        "matching_checks": S1_IG_MATCHING_CHECKS,
        "numeric_decision_rules": S1_IG_NUMERIC_DECISION_RULES,
        "baseline_record_rules": S1_IG_BASELINE_RECORD_RULES,
        "acceptance_rules": S1_IG_ACCEPTANCE_RULES,
        "stopp_conditions": S1_IG_STOPP_CONDITIONS,
        "output_schema": S1_IG_OUTPUT_SCHEMA,
        "forbidden_interpretations": S1_IG_FORBIDDEN_INTERPRETATIONS,
        "float64_epsilon_multiplier": 512,
        "direct_resource_calls_per_audit": 8,
        "technical_field_calls_per_audit": 14,
        "maximum_double_audit_direct_resource_calls": 16,
        "maximum_double_audit_technical_field_calls": 28,
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
        "attenuation_proven": False,
        "broader_function_proven": False,
        "claims_permitted": False,
        "decision": S1_IG_DECISION,
    }
    return DTS1S1IGAttenuationAuditContract(**values, contract_digest=_digest(values))
