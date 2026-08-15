"""Static S1-HZ contract for the smallest DTS-1 state intervention."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json


class DTS1S1HZFreeRefractoryInterventionContractError(ValueError):
    """Raised when the closed S1-HZ intervention boundary is weakened."""


S1_HZ_CONTRACT_ID = "dynamic-substrate.free-refractory-intervention.s1hz.v1"
S1_HZ_SOURCE_S1HH_CONTRACT_DIGEST = (
    "5eae6462ed7019f3e2f09b0f1ba0ae3859781c7be852d7d4cdf011b4ae602388"
)
S1_HZ_SOURCE_S1HY_AUDIT_RECEIPT_DIGEST = (
    "c6f75a0a1009c51dd03ad546ae04c4aded34ecf7ccd0b687bcbac4d715f24de2"
)
S1_HZ_CANDIDATE_ID = "DTS1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER"
S1_HZ_INTERVENTION_ID = "DTS1_FREE_VERSUS_REFRACTORY_NEXT_ENGAGEMENT"
S1_HZ_ARM_IDS = (
    "F_HIGH_MORE_FREE_LESS_REFRACTORY",
    "R_HIGH_LESS_FREE_MORE_REFRACTORY",
)
S1_HZ_MATCHED_PRESTATE_RULES = (
    "one-identical-existing-canonical-edge-and-identical-endpoint-identities",
    "identical-finite-positive-endpoint-capacities-and-total-resource",
    "identical-S-and-H-at-both-endpoints",
    "identical-conductive-bound-resource-on-the-target-edge",
    "identical-positive-current-participation-on-the-target-edge",
    "identical-positive-step-duration-and-identical-existing-DTS1-rates",
    "identical-field-contact-config-and-event-boundary-if-a-field-wrapper-is-later-used",
    "only-free-versus-refractory-partition-may-differ-between-arms",
    "F_HIGH-has-strictly-more-free-and-strictly-less-refractory-than-R_HIGH-at-both-endpoints",
    "both-arms-are-strict-interior-states-without-clipping-or-admission-saturation",
)
S1_HZ_INTERVENTION_CONSTRUCTION = (
    "use-one-isolated-existing-edge-so-no-adjacent-edge-can-consume-the-matched-pool",
    "hold-capacity-and-conductive-bound-resource-fixed",
    "move-one-positive-matched-resource-amount-from-free-to-refractory-in-R_HIGH",
    "derive-free-resource-only-from-the-existing-S1HI-half-share-ledger",
    "do-not-write-store-or-normalize-free-resource-independently",
    "validate-both-complete-anatomies-before-either-proposal-is-evaluated",
)
S1_HZ_MEASUREMENT_RULES = (
    "read-the-existing-S1HP-passive-edge-transfer-ledger-before-atomic-commit",
    "primary-observable-is-accepted-engagement-on-the-target-edge",
    "F_HIGH-accepted-engagement-must-be-strictly-greater-than-R_HIGH",
    "turnover-recovery-net-binding-and-field-output-are-not-primary-observables",
    "compare-one-step-proposals-from-the-two-closed-matched-prestates",
    "record-local-and-global-resource-ledger-residuals-for-both-complete-results",
    "use-no-post-hoc-threshold-fit-normalization-or-result-dependent-retry",
)
S1_HZ_NULL_CONTROLS = (
    (
        "N01_EQUAL_PARTITION_REPEAT",
        "value-identical-prestates-must-produce-bit-exact-complete-transfer-ledgers",
    ),
    (
        "N02_ZERO_PARTICIPATION",
        "both-partitions-must-produce-exactly-zero-accepted-engagement",
    ),
    (
        "N03_ZERO_BINDING_RATE",
        "both-partitions-must-produce-exactly-zero-accepted-engagement",
    ),
)
S1_HZ_BASELINE_COUNTERPREDICTIONS = (
    (
        "fixed-adapter-and-frozen-e1",
        "matched-S-H-and-conductive-binding-give-the-same-current-adapter-and-no-partition-dependent-engagement-state",
    ),
    (
        "leaky-trace-and-integrator",
        "matched-S-H-and-identical-step-input-give-no-free-versus-refractory-state-coordinate",
    ),
    (
        "dynamic-two-state-e1",
        "matched-conductive-binding-and-total-resource-collapse-both-arms-to-one-two-state-prestate",
    ),
    (
        "f3-and-const-v",
        "unchanged-spatial-total-and-no-resource-transport-give-no-local-partition-dependent-engagement-ledger",
    ),
    (
        "fast-afterimage",
        "exactly-matched-H-cannot-distinguish-the-two-resource-partitions",
    ),
)
S1_HZ_ACCEPTANCE_RULES = (
    "both-intervention-arms-and-all-three-null-controls-are-complete",
    "all-matched-prestate-rules-hold-before-any-proposal-call",
    "both-input-and-output-anatomies-pass-existing-S1HI-conservation-validation",
    "F_HIGH-accepted-engagement-is-strictly-greater-than-R_HIGH",
    "all-null-control-exact-identities-pass",
    "all-five-baseline-counterpredictions-remain-state-space-distinct-without-hidden-state-augmentation",
    "one-failure-makes-the-whole-intervention-audit-STOPP-with-no-partial-PASS",
)
S1_HZ_STOPP_CONDITIONS = (
    "any-unmatched-S-H-binding-capacity-total-participation-time-rate-or-input",
    "any-independent-free-resource-store-or-resource-ledger-violation",
    "any-nonfinite-negative-clipped-normalized-or-saturated-intervention-state",
    "F_HIGH-engagement-not-strictly-greater-than-R_HIGH-engagement",
    "any-null-control-is-not-exact",
    "measurement-uses-net-binding-field-amplitude-or-a-fitted-proxy-instead-of-accepted-engagement",
    "a-baseline-receives-the-hidden-free-refractory-coordinate-or-arm-label",
    "result-dependent-fixture-threshold-rate-or-step-adjustment",
    "missing-arm-partial-output-runtime-coupling-or-unregistered-execution",
)
S1_HZ_OUTPUT_SCHEMA = (
    "one-atomic-PASS-or-STOPP-decision",
    "two-complete-matched-prestate-manifests-and-their-canonical-digests",
    "accepted-target-edge-engagement-for-both-intervention-arms",
    "three-complete-null-control-records-with-exact-identity-booleans",
    "local-and-global-resource-ledger-residuals",
    "five-baseline-state-space-counterprediction-records",
    "technical-step-count-and-one-canonical-SHA256-receipt",
)
S1_HZ_FORBIDDEN_INTERPRETATIONS = (
    "field-function-attenuation-interference-release-or-reuse-evidence",
    "material-parameter-estimate-or-physical-timescale",
    "runtime-readiness-or-research-probe-authorization",
    "memory-learning-engram-semantics-or-inner-context",
    "organization-self-regulation-organism-or-artificial-intelligence",
    "new-natural-law-or-general-substrate-capability",
)
S1_HZ_DECISION = "DTS1_FREE_REFRACTORY_INTERVENTION_CONTRACT_BOUND"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1HZFreeRefractoryInterventionContract:
    contract_id: str
    source_s1hh_contract_digest: str
    source_s1hy_audit_receipt_digest: str
    candidate_id: str
    intervention_id: str
    arm_ids: tuple[str, ...]
    matched_prestate_rules: tuple[str, ...]
    intervention_construction: tuple[str, ...]
    measurement_rules: tuple[str, ...]
    null_controls: tuple[tuple[str, str], ...]
    baseline_counterpredictions: tuple[tuple[str, str], ...]
    acceptance_rules: tuple[str, ...]
    stopp_conditions: tuple[str, ...]
    output_schema: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    existing_s1hp_transfer_law_reused: bool
    direct_resource_measurement_required: bool
    isolated_single_edge_required: bool
    complete_baseline_set_required: bool
    atomic_decision_required: bool
    finite_fixture_audit_contract_authorized_next_stage: bool
    equation_added_or_changed: bool
    parameter_values_selected: bool
    intervention_implemented: bool
    intervention_executed: bool
    field_response_measured: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
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
            self.contract_id != S1_HZ_CONTRACT_ID
            or self.source_s1hh_contract_digest != S1_HZ_SOURCE_S1HH_CONTRACT_DIGEST
            or self.source_s1hy_audit_receipt_digest
            != S1_HZ_SOURCE_S1HY_AUDIT_RECEIPT_DIGEST
            or self.candidate_id != S1_HZ_CANDIDATE_ID
            or self.intervention_id != S1_HZ_INTERVENTION_ID
            or self.arm_ids != S1_HZ_ARM_IDS
            or self.matched_prestate_rules != S1_HZ_MATCHED_PRESTATE_RULES
            or self.intervention_construction != S1_HZ_INTERVENTION_CONSTRUCTION
            or self.measurement_rules != S1_HZ_MEASUREMENT_RULES
            or self.null_controls != S1_HZ_NULL_CONTROLS
            or self.baseline_counterpredictions != S1_HZ_BASELINE_COUNTERPREDICTIONS
            or self.acceptance_rules != S1_HZ_ACCEPTANCE_RULES
            or self.stopp_conditions != S1_HZ_STOPP_CONDITIONS
            or self.output_schema != S1_HZ_OUTPUT_SCHEMA
            or self.forbidden_interpretations != S1_HZ_FORBIDDEN_INTERPRETATIONS
            or any(
                value is not True
                for value in (
                    self.existing_s1hp_transfer_law_reused,
                    self.direct_resource_measurement_required,
                    self.isolated_single_edge_required,
                    self.complete_baseline_set_required,
                    self.atomic_decision_required,
                    self.finite_fixture_audit_contract_authorized_next_stage,
                )
            )
            or any(
                value is not False
                for value in (
                    self.equation_added_or_changed,
                    self.parameter_values_selected,
                    self.intervention_implemented,
                    self.intervention_executed,
                    self.field_response_measured,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                    self.functional_effect_proven,
                    self.claims_permitted,
                )
            )
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.decision != S1_HZ_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1HZFreeRefractoryInterventionContractError(
                "S1-HZ weakened the free-versus-refractory intervention boundary"
            )


def build_dts1_s1hz_free_refractory_intervention_contract(
) -> DTS1S1HZFreeRefractoryInterventionContract:
    """Bind the direct state intervention without implementing or executing it."""

    values = {
        "contract_id": S1_HZ_CONTRACT_ID,
        "source_s1hh_contract_digest": S1_HZ_SOURCE_S1HH_CONTRACT_DIGEST,
        "source_s1hy_audit_receipt_digest": S1_HZ_SOURCE_S1HY_AUDIT_RECEIPT_DIGEST,
        "candidate_id": S1_HZ_CANDIDATE_ID,
        "intervention_id": S1_HZ_INTERVENTION_ID,
        "arm_ids": S1_HZ_ARM_IDS,
        "matched_prestate_rules": S1_HZ_MATCHED_PRESTATE_RULES,
        "intervention_construction": S1_HZ_INTERVENTION_CONSTRUCTION,
        "measurement_rules": S1_HZ_MEASUREMENT_RULES,
        "null_controls": S1_HZ_NULL_CONTROLS,
        "baseline_counterpredictions": S1_HZ_BASELINE_COUNTERPREDICTIONS,
        "acceptance_rules": S1_HZ_ACCEPTANCE_RULES,
        "stopp_conditions": S1_HZ_STOPP_CONDITIONS,
        "output_schema": S1_HZ_OUTPUT_SCHEMA,
        "forbidden_interpretations": S1_HZ_FORBIDDEN_INTERPRETATIONS,
        "existing_s1hp_transfer_law_reused": True,
        "direct_resource_measurement_required": True,
        "isolated_single_edge_required": True,
        "complete_baseline_set_required": True,
        "atomic_decision_required": True,
        "finite_fixture_audit_contract_authorized_next_stage": True,
        "equation_added_or_changed": False,
        "parameter_values_selected": False,
        "intervention_implemented": False,
        "intervention_executed": False,
        "field_response_measured": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "functional_effect_proven": False,
        "claims_permitted": False,
        "decision": S1_HZ_DECISION,
    }
    return DTS1S1HZFreeRefractoryInterventionContract(
        **values,
        contract_digest=_digest(values),
    )
