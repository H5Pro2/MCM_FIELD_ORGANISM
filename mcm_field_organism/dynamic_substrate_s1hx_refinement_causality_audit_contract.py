"""S1-HX preregistration of one finite synthetic DTS-1 coupling audit."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json


class DTS1S1HXRefinementCausalityAuditContractError(ValueError):
    """Raised when the finite S1-HX audit boundary is weakened."""


S1_HX_CONTRACT_ID = "dynamic-substrate.refinement-causality-audit.s1hx.v1"
S1_HX_SOURCE_S1HW_RECEIPT_DIGEST = (
    "841ab118529a92d99ce84b41a77dcc0697b10c7ddfde4b879651c151767ec262"
)
S1_HX_CANDIDATE_ID = "DTS1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER"
S1_HX_TARGET_MODULE = (
    "mcm_field_organism.dynamic_substrate_dts1_refinement_causality_audit"
)
S1_HX_PARTITIONS = (2, 4, 8)
S1_HX_SYNTHETIC_FIXTURE = (
    ("geometry", "existing-three-node-open-line-with-two-canonical-edges"),
    ("physical_duration", "2.0 synthetic-time-units"),
    ("response_time", "1.0 synthetic-time-units"),
    ("afterimage_time", "0.5 synthetic-time-units"),
    ("dissipation_rate", "0.0 inverse-synthetic-time"),
    ("initial_S", "(-0.8,0.1,0.7)"),
    ("initial_H", "(0.2,-0.1,0.3)"),
    ("constant_contact", "(0.9,-0.2,0.4)"),
    ("node_capacities", "(1.0,1.0,1.0)"),
    ("dts1_rates", "(k_bind=0.4,k_turn=0.3,k_rec=0.2)"),
    ("active_resources", "((b=0.2,u=0.1),(b=0.4,u=0.2))"),
    ("zero_resources", "((b=0.0,u=0.0),(b=0.0,u=0.0))"),
)
S1_HX_SCENARIOS = (
    (
        "C01_P0_A0_EXACT_REFINEMENT_CONTROL",
        "P0-and-A0-field-output-must-be-bit-exact-at-every-substep-and-level",
    ),
    (
        "C02_ZERO_BINDING_CAUSAL_LATENCY",
        "first-A1-field-step-equals-A0-then-positive-binding-may-act-only-later",
    ),
    (
        "C03_ACTIVE_COMPLETE_PAIR_REFINEMENT",
        "active-A1-complete-field-anatomy-pair-must-refine-monotonically",
    ),
)
S1_HX_IDENTICAL_INPUT_RULES = (
    "all-levels-start-from-value-identical-field-and-anatomy-prestates",
    "all-levels-cover-the-same-closed-physical-interval-zero-to-two",
    "constant-contact-and-all-event-boundaries-are-identical-across-levels",
    "only-the-uniform-substep-count-changes-between-two-four-and-eight",
    "every-substep-recomputes-p_n-and-G_n-from-its-own-closed-prestate",
    "all-scenarios-use-one-fixed-config-and-one-fixed-positive-rate-triplet",
    "no-result-dependent-fixture-step-or-threshold-change-is-permitted",
)
S1_HX_PAIR_VECTOR = (
    "canonical-node-order-S-values",
    "canonical-node-order-H-values",
    "canonical-edge-order-b_e-divided-by-two-min-endpoint-capacity",
    "canonical-edge-order-u_e-divided-by-two-min-endpoint-capacity",
)
S1_HX_RESIDUAL_RULES = (
    "D(X,Y)=maximum-absolute-component-difference-of-complete-pair-vectors",
    "R_n_2n=D(X_n,X_2n)",
    "R_2n_4n=D(X_2n,X_4n)",
    "roundoff_floor=512*float64-epsilon*max(1,norm_inf(X_n),norm_inf(X_2n),norm_inf(X_4n))",
    "active-case-requires-R_n_2n-greater-than-roundoff_floor",
    "active-case-requires-R_2n_4n-strictly-less-than-R_n_2n",
    "no-observed-order-or-asymptotic-rate-is-claimed-from-three-levels",
)
S1_HX_CAUSALITY_RULES = (
    "C01-P0-A0-field-snapshots-are-bit-exact-at-every-corresponding-substep",
    "C02-first-A1-and-A0-field-proposals-are-bit-exact-from-zero-binding",
    "C02-first-A1-and-A0-resource-proposals-are-value-exact",
    "C02-first-A1-resource-proposal-contains-positive-new-binding",
    "C02-final-A1-A0-field-separation-must-exceed-its-roundoff-floor",
    "reader-latency-upper-bound-is-one-substep-duration",
    "latency-bounds-for-two-four-eight-substeps-are-1.0-0.5-0.25",
    "any-current-substep-use-of-new-binding-or-new-field-values-is-STOPP",
)
S1_HX_ACCEPTANCE_RULES = (
    "all-three-scenarios-complete-with-valid-finite-pair-states",
    "all-local-and-global-resource-ledger-residuals-remain-within-existing-bounds",
    "C01-all-exact-neutral-identities-pass",
    "C02-all-causal-latency-identities-and-positive-later-separation-pass",
    "C03-active-complete-pair-residual-is-nontrivial-and-strictly-decreases",
    "second-identical-audit-run-has-the-same-canonical-receipt-digest",
    "one-failure-makes-the-whole-audit-STOPP-with-no-partial-PASS",
)
S1_HX_STOPP_CONDITIONS = (
    "fixture-partition-physical-input-or-event-boundary-drift",
    "P0-A0-or-first-zero-binding-A1-exact-identity-failure",
    "same-substep-poststate-influence-or-reader-latency-not-halved",
    "nonfinite-out-of-domain-or-resource-ledger-invalid-pair-state",
    "active-coarse-fine-residual-at-or-below-floor-before-comparison",
    "active-fine-residual-not-strictly-smaller-than-coarse-residual",
    "nondeterministic-receipt-or-result-dependent-retry-tuning",
    "missing-scenario-partial-output-or-more-than-140-technical-field-steps",
)
S1_HX_OUTPUT_SCHEMA = (
    "one-atomic-PASS-or-STOPP-decision",
    "three-complete-scenario-records",
    "three-partition-counts-and-latency-bounds",
    "two-active-pair-residuals-and-one-roundoff-floor",
    "exact-identity-and-resource-validity-booleans",
    "technical-field-step-count-and-canonical-SHA256-receipt",
)
S1_HX_FORBIDDEN_INTERPRETATIONS = (
    "material-parameter-estimate-or-physical-timescale",
    "functional-baseline-separation-or-field-performance",
    "attenuation-interference-capacity-release-or-reuse-evidence",
    "memory-capability-or-any-broader-project-claim",
    "runtime-readiness-or-research-probe-authorization",
)
S1_HX_DECISION = "DTS1_FINITE_SYNTHETIC_REFINEMENT_CAUSALITY_AUDIT_CONTRACT_BOUND"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1HXRefinementCausalityAuditContract:
    contract_id: str
    source_s1hw_receipt_digest: str
    candidate_id: str
    target_module: str
    partitions: tuple[int, ...]
    synthetic_fixture: tuple[tuple[str, str], ...]
    scenarios: tuple[tuple[str, str], ...]
    identical_input_rules: tuple[str, ...]
    pair_vector: tuple[str, ...]
    residual_rules: tuple[str, ...]
    causality_rules: tuple[str, ...]
    acceptance_rules: tuple[str, ...]
    stopp_conditions: tuple[str, ...]
    output_schema: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    float64_epsilon_multiplier: int
    maximum_technical_field_steps: int
    exact_ablation_required: bool
    complete_pair_refinement_required: bool
    explicit_latency_halving_required: bool
    atomic_decision_required: bool
    synthetic_fixture_values_bound: bool
    audit_implementation_and_execution_authorized_next_stage: bool
    audit_implemented: bool
    audit_executed: bool
    material_rate_values_selected: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
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
            self.contract_id != S1_HX_CONTRACT_ID
            or self.source_s1hw_receipt_digest != S1_HX_SOURCE_S1HW_RECEIPT_DIGEST
            or self.candidate_id != S1_HX_CANDIDATE_ID
            or self.target_module != S1_HX_TARGET_MODULE
            or self.partitions != S1_HX_PARTITIONS
            or self.synthetic_fixture != S1_HX_SYNTHETIC_FIXTURE
            or self.scenarios != S1_HX_SCENARIOS
            or self.identical_input_rules != S1_HX_IDENTICAL_INPUT_RULES
            or self.pair_vector != S1_HX_PAIR_VECTOR
            or self.residual_rules != S1_HX_RESIDUAL_RULES
            or self.causality_rules != S1_HX_CAUSALITY_RULES
            or self.acceptance_rules != S1_HX_ACCEPTANCE_RULES
            or self.stopp_conditions != S1_HX_STOPP_CONDITIONS
            or self.output_schema != S1_HX_OUTPUT_SCHEMA
            or self.forbidden_interpretations != S1_HX_FORBIDDEN_INTERPRETATIONS
            or self.float64_epsilon_multiplier != 512
            or self.maximum_technical_field_steps != 140
            or any(
                value is not True
                for value in (
                    self.exact_ablation_required,
                    self.complete_pair_refinement_required,
                    self.explicit_latency_halving_required,
                    self.atomic_decision_required,
                    self.synthetic_fixture_values_bound,
                    self.audit_implementation_and_execution_authorized_next_stage,
                )
            )
            or any(
                value is not False
                for value in (
                    self.audit_implemented,
                    self.audit_executed,
                    self.material_rate_values_selected,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                    self.functional_effect_proven,
                    self.claims_permitted,
                )
            )
            or self.research_field_steps_executed != 0
            or self.decision != S1_HX_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1HXRefinementCausalityAuditContractError(
                "S1-HX weakened the finite refinement and causality audit boundary"
            )


def build_dts1_s1hx_refinement_causality_audit_contract(
) -> DTS1S1HXRefinementCausalityAuditContract:
    """Bind one finite synthetic audit without implementing or executing it."""

    values = {
        "contract_id": S1_HX_CONTRACT_ID,
        "source_s1hw_receipt_digest": S1_HX_SOURCE_S1HW_RECEIPT_DIGEST,
        "candidate_id": S1_HX_CANDIDATE_ID,
        "target_module": S1_HX_TARGET_MODULE,
        "partitions": S1_HX_PARTITIONS,
        "synthetic_fixture": S1_HX_SYNTHETIC_FIXTURE,
        "scenarios": S1_HX_SCENARIOS,
        "identical_input_rules": S1_HX_IDENTICAL_INPUT_RULES,
        "pair_vector": S1_HX_PAIR_VECTOR,
        "residual_rules": S1_HX_RESIDUAL_RULES,
        "causality_rules": S1_HX_CAUSALITY_RULES,
        "acceptance_rules": S1_HX_ACCEPTANCE_RULES,
        "stopp_conditions": S1_HX_STOPP_CONDITIONS,
        "output_schema": S1_HX_OUTPUT_SCHEMA,
        "forbidden_interpretations": S1_HX_FORBIDDEN_INTERPRETATIONS,
        "float64_epsilon_multiplier": 512,
        "maximum_technical_field_steps": 140,
        "exact_ablation_required": True,
        "complete_pair_refinement_required": True,
        "explicit_latency_halving_required": True,
        "atomic_decision_required": True,
        "synthetic_fixture_values_bound": True,
        "audit_implementation_and_execution_authorized_next_stage": True,
        "audit_implemented": False,
        "audit_executed": False,
        "material_rate_values_selected": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "research_field_steps_executed": 0,
        "functional_effect_proven": False,
        "claims_permitted": False,
        "decision": S1_HX_DECISION,
    }
    return DTS1S1HXRefinementCausalityAuditContract(
        **values,
        contract_digest=_digest(values),
    )
