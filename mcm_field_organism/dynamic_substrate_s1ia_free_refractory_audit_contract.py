"""Static S1-IA fixture and execution contract for the S1-HZ intervention."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json


class DTS1S1IAFreeRefractoryAuditContractError(ValueError):
    """Raised when the finite S1-IA audit boundary is weakened."""


S1_IA_CONTRACT_ID = "dynamic-substrate.free-refractory-audit.s1ia.v1"
S1_IA_SOURCE_S1HZ_CONTRACT_DIGEST = (
    "968a0ed6e033da839fae767cbf2a5ed2129440a6ab9c68c386fe206c606cff57"
)
S1_IA_CANDIDATE_ID = "DTS1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER"
S1_IA_TARGET_MODULE = (
    "mcm_field_organism.dynamic_substrate_dts1_free_refractory_audit"
)
S1_IA_SYNTHETIC_FIXTURE = (
    ("geometry", "one-isolated-existing-canonical-edge-node-a-node-b"),
    ("node_capacities", "(node-a=1.0,node-b=1.0)"),
    ("reference_S", "(node-a=-1.0,node-b=1.0)"),
    ("reference_H", "(node-a=0.2,node-b=-0.2)"),
    ("target_edge_participation", "1.0"),
    ("elapsed_time", "0.5 synthetic-time-units"),
    ("dts1_rates", "(binding=0.4,turnover=0.3,recovery=0.2)"),
    ("conductive_bound_both_arms", "0.4"),
    ("F_HIGH_refractory", "0.2"),
    ("R_HIGH_refractory", "0.8"),
    ("F_HIGH_derived_free_per_node", "0.7"),
    ("R_HIGH_derived_free_per_node", "0.3999999999999999"),
)
S1_IA_ANALYTIC_PREFLIGHT = (
    ("alpha_bind", "0.18126924692201812"),
    ("F_HIGH_engagement_offer", "0.2537769456908254"),
    ("R_HIGH_engagement_offer", "0.14501539753761447"),
    ("F_HIGH_node_demand", "0.1268884728454127"),
    ("R_HIGH_node_demand", "0.07250769876880724"),
    ("F_HIGH_node_admission", "1.0"),
    ("R_HIGH_node_admission", "1.0"),
    ("expected_engagement_difference", "0.1087615481532109"),
    ("roundoff_floor", "1.1368683772161603e-13"),
)
S1_IA_AUDIT_CASES = (
    (
        "C01_DIRECT_INTERVENTION_PAIR",
        "F_HIGH-and-R_HIGH-at-positive-participation-and-positive-binding-rate",
        2,
    ),
    (
        "N01_EQUAL_PARTITION_REPEAT",
        "two-value-identical-F_HIGH-proposals-require-bit-exact-complete-results",
        2,
    ),
    (
        "N02_ZERO_PARTICIPATION",
        "F_HIGH-and-R_HIGH-with-participation-zero-require-exact-zero-engagement",
        2,
    ),
    (
        "N03_ZERO_BINDING_RATE",
        "F_HIGH-and-R_HIGH-with-binding-rate-zero-require-exact-zero-engagement",
        2,
    ),
)
S1_IA_MATCHING_CHECKS = (
    "canonical-node-and-edge-identities-are-bit-exact-between-intervention-arms",
    "capacities-conductive-binding-reference-S-reference-H-participation-time-and-rates-match",
    "global-capacity-and-global-accounted-resource-are-exactly-2.0-in-both-arms",
    "only-refractory-and-ledger-derived-free-resource-differ-between-arms",
    "both-input-anatomies-have-zero-local-and-global-ledger-residuals",
    "both-engagement-demands-are-strictly-below-their-derived-node-free-resource",
    "no-baseline-receives-arm-id-or-free-refractory-state-coordinate",
)
S1_IA_NUMERIC_DECISION_RULES = (
    "read-only-the-target-edge-engagement-field-from-the-S1HP-transfer-ledger",
    "observed-F_HIGH-engagement-must-match-0.2537769456908254-within-roundoff_floor",
    "observed-R_HIGH-engagement-must-match-0.14501539753761447-within-roundoff_floor",
    "observed-engagement-difference-must-exceed-roundoff_floor",
    "observed-F_HIGH-engagement-must-be-strictly-greater-than-observed-R_HIGH",
    "all-output-local-and-global-ledger-residuals-must-remain-within-roundoff_floor",
    "N01-complete-result-payloads-and-digests-must-be-bit-exact",
    "N02-and-N03-engagement-values-must-be-exactly-zero-in-both-arms",
    "second-complete-audit-receipt-must-be-bit-exact-to-the-first",
)
S1_IA_BASELINE_RECORD_RULES = (
    "emit-one-record-for-each-of-the-five-S1HZ-baseline-counterpredictions",
    "records-are-static-state-space-checks-and-do-not-execute-baseline-models",
    "fixed-adapter-leaky-integrator-two-state-E1-F3-CONST-V-and-H-receive-only-their-bound-state",
    "any-hidden-free-refractory-coordinate-arm-label-or-per-arm-fit-is-STOPP",
)
S1_IA_ACCEPTANCE_RULES = (
    "all-four-cases-complete-in-the-fixed-order-with-eight-pure-step-calls",
    "all-matching-preflight-and-ledger-checks-pass",
    "all-nine-numeric-decision-rules-pass",
    "all-five-static-baseline-records-remain-unaugmented-and-complete",
    "second-identical-eight-call-audit-has-the-same-canonical-receipt",
    "one-failure-makes-the-whole-double-audit-STOPP-with-no-partial-PASS",
)
S1_IA_STOPP_CONDITIONS = (
    "fixture-arm-order-case-order-or-call-count-drift",
    "any-input-matching-ledger-interior-or-nonsaturation-check-fails",
    "primary-observable-is-replaced-by-net-binding-field-output-or-proxy",
    "either-positive-arm-deviates-from-its-preregistered-engagement-beyond-floor",
    "engagement-difference-is-not-positive-or-does-not-exceed-floor",
    "any-null-control-exact-identity-fails",
    "any-output-resource-ledger-residual-exceeds-floor",
    "baseline-state-is-augmented-or-fit-separately-by-arm",
    "receipt-nondeterminism-result-dependent-adjustment-retry-or-partial-output",
    "more-than-16-pure-resource-step-calls-any-field-step-runtime-or-research-execution",
)
S1_IA_OUTPUT_SCHEMA = (
    "one-atomic-PASS-or-STOPP-decision",
    "fixed-fixture-and-two-input-anatomy-digests",
    "four-complete-case-records-in-fixed-order",
    "both-positive-engagements-difference-and-roundoff-floor",
    "all-null-exactness-and-resource-ledger-validity-booleans",
    "five-static-baseline-state-space-records",
    "first-and-second-receipt-digests-and-repeat-identity-boolean",
    "pure-resource-step-count-field-step-count-and-canonical-audit-SHA256-receipt",
)
S1_IA_FORBIDDEN_INTERPRETATIONS = (
    "field-function-attenuation-interference-release-or-reuse-evidence",
    "material-parameter-estimate-or-physical-timescale",
    "baseline-performance-comparison-or-general-model-superiority",
    "runtime-readiness-or-research-probe-authorization",
    "memory-learning-semantics-organization-organism-or-artificial-intelligence",
    "new-natural-law-or-general-substrate-capability",
)
S1_IA_DECISION = "DTS1_FINITE_FREE_REFRACTORY_AUDIT_CONTRACT_BOUND"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1IAFreeRefractoryAuditContract:
    contract_id: str
    source_s1hz_contract_digest: str
    candidate_id: str
    target_module: str
    synthetic_fixture: tuple[tuple[str, str], ...]
    analytic_preflight: tuple[tuple[str, str], ...]
    audit_cases: tuple[tuple[str, str, int], ...]
    matching_checks: tuple[str, ...]
    numeric_decision_rules: tuple[str, ...]
    baseline_record_rules: tuple[str, ...]
    acceptance_rules: tuple[str, ...]
    stopp_conditions: tuple[str, ...]
    output_schema: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    float64_epsilon_multiplier: int
    pure_step_calls_per_audit: int
    maximum_double_audit_pure_step_calls: int
    maximum_field_steps: int
    exact_repeat_required: bool
    exact_null_controls_required: bool
    direct_engagement_measurement_required: bool
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
    pure_resource_steps_executed: int
    field_steps_executed: int
    research_field_steps_executed: int
    functional_effect_proven: bool
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
            self.contract_id != S1_IA_CONTRACT_ID
            or self.source_s1hz_contract_digest != S1_IA_SOURCE_S1HZ_CONTRACT_DIGEST
            or self.candidate_id != S1_IA_CANDIDATE_ID
            or self.target_module != S1_IA_TARGET_MODULE
            or self.synthetic_fixture != S1_IA_SYNTHETIC_FIXTURE
            or self.analytic_preflight != S1_IA_ANALYTIC_PREFLIGHT
            or self.audit_cases != S1_IA_AUDIT_CASES
            or self.matching_checks != S1_IA_MATCHING_CHECKS
            or self.numeric_decision_rules != S1_IA_NUMERIC_DECISION_RULES
            or self.baseline_record_rules != S1_IA_BASELINE_RECORD_RULES
            or self.acceptance_rules != S1_IA_ACCEPTANCE_RULES
            or self.stopp_conditions != S1_IA_STOPP_CONDITIONS
            or self.output_schema != S1_IA_OUTPUT_SCHEMA
            or self.forbidden_interpretations != S1_IA_FORBIDDEN_INTERPRETATIONS
            or self.float64_epsilon_multiplier != 512
            or self.pure_step_calls_per_audit != 8
            or self.maximum_double_audit_pure_step_calls != 16
            or self.maximum_field_steps != 0
            or any(
                value is not True
                for value in (
                    self.exact_repeat_required,
                    self.exact_null_controls_required,
                    self.direct_engagement_measurement_required,
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
                    self.functional_effect_proven,
                    self.claims_permitted,
                )
            )
            or self.pure_resource_steps_executed != 0
            or self.field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.decision != S1_IA_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1IAFreeRefractoryAuditContractError(
                "S1-IA weakened the finite free-versus-refractory audit boundary"
            )


def build_dts1_s1ia_free_refractory_audit_contract(
) -> DTS1S1IAFreeRefractoryAuditContract:
    """Bind one finite double audit without implementing or executing it."""

    values = {
        "contract_id": S1_IA_CONTRACT_ID,
        "source_s1hz_contract_digest": S1_IA_SOURCE_S1HZ_CONTRACT_DIGEST,
        "candidate_id": S1_IA_CANDIDATE_ID,
        "target_module": S1_IA_TARGET_MODULE,
        "synthetic_fixture": S1_IA_SYNTHETIC_FIXTURE,
        "analytic_preflight": S1_IA_ANALYTIC_PREFLIGHT,
        "audit_cases": S1_IA_AUDIT_CASES,
        "matching_checks": S1_IA_MATCHING_CHECKS,
        "numeric_decision_rules": S1_IA_NUMERIC_DECISION_RULES,
        "baseline_record_rules": S1_IA_BASELINE_RECORD_RULES,
        "acceptance_rules": S1_IA_ACCEPTANCE_RULES,
        "stopp_conditions": S1_IA_STOPP_CONDITIONS,
        "output_schema": S1_IA_OUTPUT_SCHEMA,
        "forbidden_interpretations": S1_IA_FORBIDDEN_INTERPRETATIONS,
        "float64_epsilon_multiplier": 512,
        "pure_step_calls_per_audit": 8,
        "maximum_double_audit_pure_step_calls": 16,
        "maximum_field_steps": 0,
        "exact_repeat_required": True,
        "exact_null_controls_required": True,
        "direct_engagement_measurement_required": True,
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
        "pure_resource_steps_executed": 0,
        "field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "functional_effect_proven": False,
        "claims_permitted": False,
        "decision": S1_IA_DECISION,
    }
    return DTS1S1IAFreeRefractoryAuditContract(
        **values,
        contract_digest=_digest(values),
    )
