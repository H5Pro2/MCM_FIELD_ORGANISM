"""Static S1-IM finite fixture contract for the S1-IL release/reuse audit."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json


class DTS1S1IMReleaseReuseAuditContractError(ValueError):
    """Raised when the finite S1-IM audit boundary is weakened."""


S1_IM_CONTRACT_ID = "dynamic-substrate.local-capacity-release-reuse-audit.s1im.v1"
S1_IM_SOURCE_S1IL_CONTRACT_DIGEST = (
    "05582932f13789dab3ff612ea2035ffbfb3180154203ee1574e67b6a86e2c550"
)
S1_IM_CANDIDATE_ID = "DTS1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER"
S1_IM_TARGET_MODULE = "mcm_field_organism.dynamic_substrate_dts1_release_reuse_audit"
S1_IM_SYNTHETIC_FIXTURE = (
    ("geometry", "open-line-node-a-node-b-node-c-with-A=(a,b)-and-B=(b,c)"),
    ("node_capacities", "(node-a=1.0,node-b=1.0,node-c=1.0)"),
    ("initial_conductive_bound", "(A=0.2,B=0.2)"),
    ("initial_refractory", "(A=0.1,B=0.1)"),
    ("initial_derived_free", "(node-a=0.85,node-b=0.7,node-c=0.85)"),
    ("A_load_participation", "(A=1.0,B=0.0)"),
    ("release_window_participation", "(A=0.0,B=0.0)"),
    ("B_probe_participation", "(A=0.0,B=1.0)"),
    ("zero_B_probe_participation", "(A=0.0,B=0.0)"),
    ("interval_duration", "0.5 synthetic-time-units"),
    ("recovery_on_rates", "(binding=0.4,turnover=0.3,recovery=0.2)"),
    ("recovery_off_rates", "(binding=0.4,turnover=0.3,recovery=0.0)"),
    ("common_probe_S", "(node-a=-1.0,node-b=0.0,node-c=1.0)"),
    ("common_probe_H", "(node-a=-0.2,node-b=0.0,node-c=0.2)"),
    ("matched_zero_H", "(node-a=0.0,node-b=0.0,node-c=0.0)"),
    ("common_probe_contact", "zero-at-all-three-nodes"),
    ("probe_duration", "0.5 synthetic-time-units"),
    ("field_response_time", "1.0 synthetic-time-units"),
    ("afterimage_time", "0.5 synthetic-time-units"),
    ("field_leak_rate", "0.0"),
)
S1_IM_ANALYTIC_RESOURCE_PREFLIGHT = (
    ("alpha_binding", "0.18126924692201812"),
    ("alpha_turnover", "0.1392920235749422"),
    ("alpha_recovery_on", "0.09516258196404043"),
    ("alpha_recovery_off", "0.0"),
    ("common_A_load_engagement", "0.2537769456908254"),
    ("common_postload_state_bA_uA_bB_uB", "(0.4259185409758369,0.11834214651858439,0.17214159528501158,0.11834214651858439)"),
    ("recovery_on_window_A_recovery", "0.011261744217875269"),
    ("recovery_on_window_B_recovery", "0.011261744217875269"),
    ("recovery_off_window_A_recovery", "0.0"),
    ("recovery_off_window_B_recovery", "0.0"),
    ("recovery_on_preprobe_state_bA_uA_bB_uB", "(0.3665914855252257,0.1664074577513204,0.1481636441363436,0.13105835344937714)"),
    ("recovery_off_preprobe_state_bA_uA_bB_uB", "(0.3665914855252257,0.17766920196919567,0.1481636441363436,0.1423200976672524)"),
    ("recovery_on_preprobe_shared_free", "0.5938895295688665"),
    ("recovery_off_preprobe_shared_free", "0.5826277853509914"),
    ("shared_free_release_margin", "0.01126174421787518"),
    ("recovery_on_B_engagement", "0.2153078155596401"),
    ("recovery_off_B_engagement", "0.21122499977283485"),
    ("additional_B_engagement_margin", "0.0040828157868052495"),
    ("recovery_on_postprobe_state_bA_uA_bB_uB", "(0.31552821568107287,0.2016349642577856,0.3428334458839948,0.13922451595916752)"),
    ("recovery_off_postprobe_state_bA_uA_bB_uB", "(0.31552821568107287,0.21182501181846924,0.33875063009718953,0.1494145635198512)"),
    ("B_probe_node_admissions_both_arms", "(1.0,1.0,1.0)"),
)
S1_IM_ANALYTIC_FIELD_PREFLIGHT = (
    ("postprobe_recovery_on_adapter_A_B", "(1.1577641078405365,1.1714167229419974)"),
    ("postprobe_recovery_off_adapter_A_B", "(1.1577641078405365,1.1693753150485948)"),
    ("recovery_on_main_S", "(-0.33950427416406204,0.0013662710624220717,0.3381380031016397)"),
    ("recovery_off_main_S", "(-0.33957447535575846,0.001163051483276697,0.3384114238724816)"),
    ("recovery_on_main_H", "(-0.4271451758519227,0.0008376410940565081,0.42630753475786604)"),
    ("recovery_off_main_H", "(-0.42717123310618593,0.0007128200861448213,0.4264584130200409)"),
    ("recovery_on_zero_H_output_H", "(-0.3535692876176341,0.000837641094056506,0.3527316465235776)"),
    ("recovery_off_zero_H_output_H", "(-0.3535953448718974,0.0007128200861448334,0.3528825247857523)"),
    ("B_edge_contrast_recovery_on", "0.3367717320392176"),
    ("B_edge_contrast_recovery_off", "0.33724837238920485"),
    ("B_edge_contrast_off_minus_on", "0.00047664034998723404"),
    ("complete_main_SH_separation", "0.000273420770841859"),
    ("complete_zero_H_SH_separation", "0.000273420770841859"),
    ("roundoff_floor", "1.1368683772161603e-13"),
)
S1_IM_AUDIT_CASES = (
    ("C01_RECOVERY_ON_VERSUS_OFF_THEN_B", "two-complete-three-interval-resource-arms-and-two-main-readouts", 6, 2),
    ("N01_VALUE_IDENTICAL_SEQUENCE_REPLAY", "two-complete-identical-recovery-on-sequences-and-readouts", 6, 2),
    ("N02_RECOVERY_ZERO_EQUALS_OFF", "two-release-window-proposals-from-the-common-postload-state", 2, 0),
    ("N03_ZERO_REFRACTORY_SOURCE", "two-zero-source-release-window-proposals", 2, 0),
    ("N04_ZERO_B_PROBE_PARTICIPATION", "two-zero-B-proposals-from-the-active-preprobe-anatomies", 2, 0),
    ("N05_A0_DISABLED_FIELD_READOUT", "two-postprobe-common-readouts-with-backreaction-disabled", 0, 2),
    ("N06_FROZEN_PRERELEASE_ADAPTER", "two-postprobe-readouts-with-one-common-fixed-adapter", 0, 2),
    ("N07_MATCHED_ZERO_H", "two-active-postprobe-readouts-with-H-zero", 0, 2),
)
S1_IM_MATCHING_CHECKS = (
    "both-active-arms-have-bit-exact-initial-anatomy-A-load-participation-duration-rates-and-boundaries",
    "release-windows-have-bit-exact-zero-participation-duration-turnover-rate-and-boundaries-with-only-recovery-channel-different",
    "both-B-probes-have-bit-exact-positive-participation-duration-rates-and-boundaries",
    "all-node-admissions-remain-one-so-no-direction-is-created-by-saturation-or-clipping",
    "only-complete-valid-resource-poststates-carry-between-sequence-intervals",
    "all-main-and-zero-H-readouts-use-respective-bit-exact-common-field-prestates-and-discard-resource-poststates",
    "every-anatomy-has-valid-local-and-global-ledgers-and-all-values-are-synthetic",
)
S1_IM_NUMERIC_DECISION_RULES = (
    "all-resource-state-transfer-free-admission-and-field-values-match-preflight-within-roundoff-floor",
    "recovery-on-window-has-positive-A-and-B-recovery-while-recovery-off-is-exactly-zero",
    "postwindow-conductive-bound-values-are-bit-exact-between-active-arms",
    "preprobe-shared-free-is-higher-after-recovery-on-by-more-than-roundoff-floor",
    "B-engagement-is-higher-after-recovery-on-by-more-than-roundoff-floor",
    "release-margin-and-additional-B-engagement-margin-pass-separately",
    "postprobe-adapter-and-complete-main-S-H-values-match-field-preflight",
    "B-edge-contrast-has-the-preregistered-direction-and-complete-separation-exceeds-floor",
    "zero-H-S-vectors-match-main-S-vectors-and-complete-separation-exceeds-floor",
    "all-local-global-ledger-and-field-domain-residuals-remain-within-roundoff-floor",
    "N01-complete-sequence-and-readout-payloads-are-bit-exact",
    "N02-recovery-zero-and-explicit-recovery-off-results-are-bit-exact",
    "N03-zero-source-recovery-is-exactly-zero-and-results-are-bit-exact",
    "N04-zero-B-engagement-is-exactly-zero-in-both-arms",
    "N05-A0-common-field-outputs-are-bit-exact-between-postprobe-anatomies",
    "N06-one-fixed-prerelease-adapter-produces-bit-exact-complete-field-outputs",
    "second-complete-audit-receipt-is-bit-exact-to-the-first",
)
S1_IM_BASELINE_RECORD_RULES = (
    "emit-one-static-record-for-each-of-the-five-S1IL-baseline-counterpredictions",
    "no-baseline-model-is-executed-or-fit-in-S1IM-or-the-S1IN-harness",
    "N05-N06-and-N07-are-technical-controls-and-not-baseline-model-fits",
    "dynamic-two-state-E1-remains-explicitly-not-separated-by-release-and-reuse-alone",
    "any-arm-label-hidden-resource-coordinate-or-per-arm-fit-is-STOPP",
)
S1_IM_ACCEPTANCE_RULES = (
    "all-eight-cases-complete-in-fixed-order-with-eighteen-direct-resource-and-ten-technical-field-calls",
    "all-matching-ledger-field-and-float64-preflight-checks-pass",
    "all-seventeen-numeric-decision-rules-pass",
    "all-five-static-baseline-records-remain-unaugmented-and-complete",
    "second-identical-twenty-eight-call-audit-has-the-same-canonical-receipt",
    "one-failure-makes-the-whole-double-audit-STOPP-with-no-partial-PASS",
)
S1_IM_STOPP_CONDITIONS = (
    "fixture-case-arm-sequence-checkpoint-or-call-order-drift",
    "any-geometry-matching-anatomy-carry-readout-discard-or-ledger-check-fails",
    "direct-recovery-shared-free-or-B-engagement-deviates-beyond-floor-or-lacks-direction",
    "conductive-bound-postwindow-values-are-not-bit-exact-between-active-arms",
    "any-value-identical-recovery-zero-source-zero-B-A0-frozen-adapter-or-H-control-fails",
    "any-output-resource-ledger-or-field-domain-residual-exceeds-floor",
    "baseline-state-is-augmented-executed-or-fit-separately-by-arm",
    "receipt-nondeterminism-result-dependent-adjustment-retry-or-partial-output",
    "more-than-36-direct-resource-or-20-technical-field-calls-in-the-double-audit",
    "any-runtime-integration-research-execution-or-claim-expansion",
)
S1_IM_OUTPUT_SCHEMA = (
    "one-atomic-PASS-or-STOPP-decision",
    "fixed-fixture-source-contract-case-and-arm-order-record",
    "complete-load-release-window-B-probe-transfer-and-anatomy-records",
    "direct-recovery-shared-free-B-engagement-admission-and-margin-records",
    "main-and-zero-H-common-readout-field-adapter-contrast-and-separation-records",
    "seven-complete-control-records-and-five-static-baseline-records",
    "all-direction-margin-floor-ledger-and-field-validity-booleans",
    "first-and-second-receipt-digests-and-repeat-identity-boolean",
    "direct-resource-technical-field-and-research-field-counts-plus-one-canonical-audit-SHA256-receipt",
)
S1_IM_FORBIDDEN_INTERPRETATIONS = (
    "standalone-nonreducibility-to-dynamic-two-state-E1",
    "physical-rate-timescale-material-or-general-performance-evidence",
    "runtime-readiness-or-research-probe-authorization",
    "memory-learning-forgetting-semantics-organization-organism-or-artificial-intelligence",
    "new-natural-law-or-general-substrate-capability",
)
S1_IM_DECISION = "DTS1_FINITE_LOCAL_CAPACITY_RELEASE_REUSE_AUDIT_CONTRACT_BOUND"


def _digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1IMReleaseReuseAuditContract:
    contract_id: str
    source_s1il_contract_digest: str
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
    release_proven: bool
    reuse_proven: bool
    e1_nonreducibility_proven: bool
    claims_permitted: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {field.name: getattr(self, field.name) for field in fields(self) if field.name != "contract_digest"}
        constants = (
            self.contract_id == S1_IM_CONTRACT_ID,
            self.source_s1il_contract_digest == S1_IM_SOURCE_S1IL_CONTRACT_DIGEST,
            self.candidate_id == S1_IM_CANDIDATE_ID,
            self.target_module == S1_IM_TARGET_MODULE,
            self.synthetic_fixture == S1_IM_SYNTHETIC_FIXTURE,
            self.analytic_resource_preflight == S1_IM_ANALYTIC_RESOURCE_PREFLIGHT,
            self.analytic_field_preflight == S1_IM_ANALYTIC_FIELD_PREFLIGHT,
            self.audit_cases == S1_IM_AUDIT_CASES,
            self.matching_checks == S1_IM_MATCHING_CHECKS,
            self.numeric_decision_rules == S1_IM_NUMERIC_DECISION_RULES,
            self.baseline_record_rules == S1_IM_BASELINE_RECORD_RULES,
            self.acceptance_rules == S1_IM_ACCEPTANCE_RULES,
            self.stopp_conditions == S1_IM_STOPP_CONDITIONS,
            self.output_schema == S1_IM_OUTPUT_SCHEMA,
            self.forbidden_interpretations == S1_IM_FORBIDDEN_INTERPRETATIONS,
        )
        required_true = (
            self.exact_repeat_required,
            self.exact_controls_required,
            self.synthetic_values_bound,
            self.atomic_decision_required,
            self.audit_implementation_and_execution_authorized_next_stage,
        )
        required_false = (
            self.equation_added_or_changed,
            self.material_parameters_selected,
            self.audit_implemented,
            self.audit_executed,
            self.baseline_models_executed,
            self.runtime_integration_present,
            self.research_execution_permitted,
            self.release_proven,
            self.reuse_proven,
            self.e1_nonreducibility_proven,
            self.claims_permitted,
        )
        if (
            not all(constants)
            or self.float64_epsilon_multiplier != 512
            or self.direct_resource_calls_per_audit != 18
            or self.technical_field_calls_per_audit != 10
            or self.maximum_double_audit_direct_resource_calls != 36
            or self.maximum_double_audit_technical_field_calls != 20
            or self.maximum_research_field_steps != 0
            or not all(required_true)
            or any(required_false)
            or self.direct_resource_calls_executed != 0
            or self.technical_field_calls_executed != 0
            or self.research_field_steps_executed != 0
            or self.decision != S1_IM_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1IMReleaseReuseAuditContractError("S1-IM weakened the finite release/reuse audit boundary")


def build_dts1_s1im_release_reuse_audit_contract() -> DTS1S1IMReleaseReuseAuditContract:
    """Bind the finite release/reuse double audit without implementing it."""

    values = {
        "contract_id": S1_IM_CONTRACT_ID,
        "source_s1il_contract_digest": S1_IM_SOURCE_S1IL_CONTRACT_DIGEST,
        "candidate_id": S1_IM_CANDIDATE_ID,
        "target_module": S1_IM_TARGET_MODULE,
        "synthetic_fixture": S1_IM_SYNTHETIC_FIXTURE,
        "analytic_resource_preflight": S1_IM_ANALYTIC_RESOURCE_PREFLIGHT,
        "analytic_field_preflight": S1_IM_ANALYTIC_FIELD_PREFLIGHT,
        "audit_cases": S1_IM_AUDIT_CASES,
        "matching_checks": S1_IM_MATCHING_CHECKS,
        "numeric_decision_rules": S1_IM_NUMERIC_DECISION_RULES,
        "baseline_record_rules": S1_IM_BASELINE_RECORD_RULES,
        "acceptance_rules": S1_IM_ACCEPTANCE_RULES,
        "stopp_conditions": S1_IM_STOPP_CONDITIONS,
        "output_schema": S1_IM_OUTPUT_SCHEMA,
        "forbidden_interpretations": S1_IM_FORBIDDEN_INTERPRETATIONS,
        "float64_epsilon_multiplier": 512,
        "direct_resource_calls_per_audit": 18,
        "technical_field_calls_per_audit": 10,
        "maximum_double_audit_direct_resource_calls": 36,
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
        "release_proven": False,
        "reuse_proven": False,
        "e1_nonreducibility_proven": False,
        "claims_permitted": False,
        "decision": S1_IM_DECISION,
    }
    return DTS1S1IMReleaseReuseAuditContract(**values, contract_digest=_digest(values))
