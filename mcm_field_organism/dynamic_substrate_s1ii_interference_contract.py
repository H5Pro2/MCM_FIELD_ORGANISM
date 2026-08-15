"""Static S1-II contract for local DTS-1 A-B-A interference."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json


class DTS1S1IIInterferenceContractError(ValueError):
    """Raised when the closed S1-II interference boundary is weakened."""


S1_II_CONTRACT_ID = "dynamic-substrate.local-aba-interference.s1ii.v1"
S1_II_SOURCE_S1HH_CONTRACT_DIGEST = (
    "5eae6462ed7019f3e2f09b0f1ba0ae3859781c7be852d7d4cdf011b4ae602388"
)
S1_II_SOURCE_S1IH_AUDIT_RECEIPT_DIGEST = (
    "2fd24fd7ccdee690ea5610440e2d76f85e6a5ca0b8bc4b9045ff7c12a34d0c36"
)
S1_II_CANDIDATE_ID = "DTS1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER"
S1_II_FUNCTION_ID = "DTS1_SHARED_ENDPOINT_ABA_COMPETITOR_INTERFERENCE"
S1_II_ARM_IDS = (
    "ABA_SHARED_ENDPOINT_COMPETITOR",
    "A_GAP_A_MATCHED_PASSIVE_INTERVAL",
)
S1_II_GEOMETRY_RULES = (
    "one-open-three-node-line-with-two-existing-canonical-edges-A-and-B",
    "A-and-B-share-exactly-one-middle-endpoint-and-no-other-endpoint",
    "the-middle-endpoint-has-one-finite-capacity-ledger-shared-by-both-incident-edges",
    "outer-endpoint-capacities-edge-identities-and-the-complete-initial-anatomy-are-arm-identical",
    "no-new-edge-resource-transport-global-allocator-or-hidden-shared-state-is-permitted",
)
S1_II_SEQUENCE_RULES = (
    "both-arms-begin-with-the-same-positive-A-contact-from-one-bit-exact-closed-anatomy",
    "the-middle-interval-has-the-same-positive-duration-rates-and-event-boundaries-in-both-arms",
    "the-ABA-arm-applies-positive-participation-only-to-B-during-the-middle-interval",
    "the-A-gap-A-arm-applies-zero-participation-to-both-edges-during-the-middle-interval",
    "both-arms-end-with-the-same-positive-A-probe-from-their-complete-carried-preprobe-anatomies",
    "the-final-A-resource-proposal-is-committed-before-any-separate-field-readout",
    "each-field-readout-uses-one-value-identical-registered-S-H-probe-and-discards-its-resource-poststate",
    "no-arm-label-sequence-index-result-value-or-future-state-may-control-transfer-or-field-proposals",
)
S1_II_REQUIRED_RECORDS = (
    "complete-pre-and-post-anatomy-and-transfer-ledger-for-every-sequence-interval",
    "middle-B-accepted-engagement-and-the-shared-endpoint-free-resource-before-the-final-A-probe",
    "final-A-accepted-engagement-turnover-recovery-and-node-admission-diagnostics-in-both-arms",
    "local-and-global-free-conductive-bound-refractory-ledger-residuals-at-every-checkpoint",
    "one-common-postsequence-probe-applied-adapter-and-complete-S-H-field-output-for-both-arms",
    "oriented-A-edge-S-contrast-and-complete-S-H-arm-separation-in-the-common-readout",
    "the-same-common-readout-with-value-identical-or-ablated-H",
    "bit-exact-value-identical-replay-B-zero-A0-and-frozen-adapter-control-records",
)
S1_II_DIRECTION_RULES = (
    "middle-B-engagement-in-the-ABA-arm-must-be-strictly-positive",
    "shared-endpoint-free-resource-before-final-A-must-be-strictly-lower-in-ABA-than-A-gap-A",
    "final-A-accepted-engagement-must-be-strictly-lower-in-ABA-than-A-gap-A",
    "the-next-stage-must-analytically-preregister-the-postsequence-common-field-readout-direction-and-nonzero-margin",
    "the-directed-field-separation-must-remain-above-a-preregistered-float64-floor-after-H-is-matched-or-ablated",
    "shared-free-final-A-engagement-and-field-readout-directions-must-all-pass-and-none-may-substitute-for-another",
    "all-directions-margins-floors-checkpoints-and-admission-limits-must-be-fixed-before-execution",
)
S1_II_CONTROL_CASES = (
    (
        "N01_VALUE_IDENTICAL_ABA_REPLAY",
        "two-value-identical-complete-ABA-sequences-require-bit-exact-ledgers-anatomies-and-readouts",
    ),
    (
        "N02_B_ZERO_EQUALS_MATCHED_GAP",
        "zero-B-participation-with-the-same-middle-duration-requires-bit-exact-A-gap-A-resource-results",
    ),
    (
        "N03_A0_DISABLED_FIELD_READOUT",
        "candidate-disabled-postsequence-common-readouts-require-the-bit-exact-neutral-field-path",
    ),
    (
        "N04_FROZEN_PRESEQUENCE_ADAPTER",
        "one-adapter-fixed-before-the-sequence-requires-bit-exact-common-field-output-between-arms",
    ),
    (
        "N05_MATCHED_OR_ABLATED_H",
        "the-preregistered-directed-postsequence-field-separation-must-remain-with-H-value-identical-or-zero",
    ),
    (
        "N06_ZERO_A_PROBE_PARTICIPATION",
        "zero-final-A-participation-requires-exactly-zero-final-A-engagement-in-both-arms",
    ),
)
S1_II_BASELINE_COUNTERPREDICTIONS = (
    (
        "fixed-adapter-and-frozen-e1",
        "one-presequence-fixed-adapter-cannot-express-shared-free-displacement-and-predicts-one-common-readout-coupling",
    ),
    (
        "leaky-trace-and-integrator",
        "value-identical-postsequence-S-H-probes-remove-carried-field-state-while-the-direct-shared-resource-ledger-remains",
    ),
    (
        "dynamic-two-state-e1",
        "shared-pool-competition-alone-is-not-distinctive-so-S1IB-free-refractory-intervention-and-S1IE-readout-remain-jointly-required",
    ),
    (
        "f3-and-const-v",
        "without-one-finite-shared-endpoint-ledger-the-baseline-has-no-direct-B-displacement-of-final-A-admission",
    ),
    (
        "fast-afterimage",
        "matched-or-ablated-common-probe-H-removes-fast-afterimage-as-the-source-of-postsequence-field-separation",
    ),
)
S1_II_ACCEPTANCE_RULES = (
    "both-active-arms-and-all-six-controls-are-complete-for-the-preregistered-finite-sequence",
    "all-arm-matching-sequence-causality-anatomy-ledger-and-atomicity-rules-pass",
    "middle-B-engagement-shared-free-deficit-and-final-A-engagement-have-all-preregistered-strict-directions",
    "the-postsequence-common-field-readout-has-its-preregistered-direction-and-remains-above-floor-with-H-controlled",
    "all-five-baseline-counterpredictions-remain-unaugmented-and-recorded-without-model-execution-at-this-stage",
    "one-failure-makes-the-whole-interference-audit-STOPP-with-no-partial-PASS",
)
S1_II_STOPP_CONDITIONS = (
    "any-unmatched-initial-anatomy-A-contact-middle-duration-rate-event-boundary-final-A-probe-or-common-readout",
    "A-and-B-do-not-share-exactly-one-finite-endpoint-ledger",
    "middle-B-engagement-is-not-positive-or-shared-free-resource-is-not-lower-before-final-A",
    "final-A-engagement-in-ABA-is-not-strictly-lower-than-in-A-gap-A",
    "postsequence-field-separation-is-at-or-below-floor-has-the-wrong-direction-or-vanishes-with-H-controlled",
    "any-value-identical-B-zero-A0-frozen-adapter-H-or-zero-A-probe-control-fails",
    "any-resource-creation-loss-negativity-clipping-normalization-invalid-field-domain-or-partial-commit",
    "any-baseline-receives-sequence-label-hidden-resource-coordinate-arm-id-or-per-arm-fit",
    "interference-alone-is-used-to-claim-separation-from-dynamic-two-state-E1",
    "result-dependent-fixture-threshold-direction-rate-retry-or-partial-output",
    "runtime-coupling-unregistered-execution-or-research-field-use",
)
S1_II_FORBIDDEN_INTERPRETATIONS = (
    "capacity-release-reuse-recovery-material-or-general-performance-evidence",
    "standalone-nonreducibility-to-dynamic-two-state-E1",
    "runtime-readiness-or-research-probe-authorization",
    "memory-learning-semantics-inner-context-organization-or-self-regulation",
    "organism-artificial-intelligence-new-natural-law-or-general-capability",
)
S1_II_DECISION = "DTS1_LOCAL_ABA_VERSUS_A_GAP_A_INTERFERENCE_CONTRACT_BOUND"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1IIInterferenceContract:
    contract_id: str
    source_s1hh_contract_digest: str
    source_s1ih_audit_receipt_digest: str
    candidate_id: str
    function_id: str
    arm_ids: tuple[str, ...]
    geometry_rules: tuple[str, ...]
    sequence_rules: tuple[str, ...]
    required_records: tuple[str, ...]
    direction_rules: tuple[str, ...]
    control_cases: tuple[tuple[str, str], ...]
    baseline_counterpredictions: tuple[tuple[str, str], ...]
    acceptance_rules: tuple[str, ...]
    stopp_conditions: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    fixture_values_selected: bool
    equation_added_or_changed: bool
    interference_harness_implemented: bool
    interference_executed: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    interference_proven: bool
    release_or_reuse_proven: bool
    broader_function_proven: bool
    claims_permitted: bool
    finite_fixture_contract_authorized_next_stage: bool
    atomic_decision_required: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_II_CONTRACT_ID
            or self.source_s1hh_contract_digest != S1_II_SOURCE_S1HH_CONTRACT_DIGEST
            or self.source_s1ih_audit_receipt_digest
            != S1_II_SOURCE_S1IH_AUDIT_RECEIPT_DIGEST
            or self.candidate_id != S1_II_CANDIDATE_ID
            or self.function_id != S1_II_FUNCTION_ID
            or self.arm_ids != S1_II_ARM_IDS
            or self.geometry_rules != S1_II_GEOMETRY_RULES
            or self.sequence_rules != S1_II_SEQUENCE_RULES
            or self.required_records != S1_II_REQUIRED_RECORDS
            or self.direction_rules != S1_II_DIRECTION_RULES
            or self.control_cases != S1_II_CONTROL_CASES
            or self.baseline_counterpredictions != S1_II_BASELINE_COUNTERPREDICTIONS
            or self.acceptance_rules != S1_II_ACCEPTANCE_RULES
            or self.stopp_conditions != S1_II_STOPP_CONDITIONS
            or self.forbidden_interpretations != S1_II_FORBIDDEN_INTERPRETATIONS
            or any(
                value is not False
                for value in (
                    self.fixture_values_selected,
                    self.equation_added_or_changed,
                    self.interference_harness_implemented,
                    self.interference_executed,
                    self.baseline_models_executed,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                    self.interference_proven,
                    self.release_or_reuse_proven,
                    self.broader_function_proven,
                    self.claims_permitted,
                )
            )
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.finite_fixture_contract_authorized_next_stage is not True
            or self.atomic_decision_required is not True
            or self.decision != S1_II_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1IIInterferenceContractError(
                "S1-II weakened the local A-B-A interference boundary"
            )


def build_dts1_s1ii_interference_contract() -> DTS1S1IIInterferenceContract:
    """Bind local competitor interference without values or execution."""

    values = {
        "contract_id": S1_II_CONTRACT_ID,
        "source_s1hh_contract_digest": S1_II_SOURCE_S1HH_CONTRACT_DIGEST,
        "source_s1ih_audit_receipt_digest": S1_II_SOURCE_S1IH_AUDIT_RECEIPT_DIGEST,
        "candidate_id": S1_II_CANDIDATE_ID,
        "function_id": S1_II_FUNCTION_ID,
        "arm_ids": S1_II_ARM_IDS,
        "geometry_rules": S1_II_GEOMETRY_RULES,
        "sequence_rules": S1_II_SEQUENCE_RULES,
        "required_records": S1_II_REQUIRED_RECORDS,
        "direction_rules": S1_II_DIRECTION_RULES,
        "control_cases": S1_II_CONTROL_CASES,
        "baseline_counterpredictions": S1_II_BASELINE_COUNTERPREDICTIONS,
        "acceptance_rules": S1_II_ACCEPTANCE_RULES,
        "stopp_conditions": S1_II_STOPP_CONDITIONS,
        "forbidden_interpretations": S1_II_FORBIDDEN_INTERPRETATIONS,
        "fixture_values_selected": False,
        "equation_added_or_changed": False,
        "interference_harness_implemented": False,
        "interference_executed": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "interference_proven": False,
        "release_or_reuse_proven": False,
        "broader_function_proven": False,
        "claims_permitted": False,
        "finite_fixture_contract_authorized_next_stage": True,
        "atomic_decision_required": True,
        "decision": S1_II_DECISION,
    }
    return DTS1S1IIInterferenceContract(**values, contract_digest=_digest(values))
