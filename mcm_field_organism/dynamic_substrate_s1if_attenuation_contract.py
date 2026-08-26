"""Static S1-IF contract for DTS-1 attenuation under repeated equal contact."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json


class DTS1S1IFAttenuationContractError(ValueError):
    """Raised when the closed S1-IF attenuation boundary is weakened."""


S1_IF_CONTRACT_ID = "dynamic-substrate.repeated-contact-attenuation.s1if.v1"
S1_IF_SOURCE_S1HH_CONTRACT_DIGEST = (
    "5eae6462ed7019f3e2f09b0f1ba0ae3859781c7be852d7d4cdf011b4ae602388"
)
S1_IF_SOURCE_S1IE_AUDIT_RECEIPT_DIGEST = (
    "dbaa141450f1a00defb71824feb4e61bbef727c0023ea1d1e19cc979581ebcea"
)
S1_IF_CANDIDATE_ID = "DTS1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER"
S1_IF_FUNCTION_ID = "DTS1_EQUAL_LOCAL_CONTACT_CONDUCTIVE_ATTENUATION"
S1_IF_SEQUENCE_RULES = (
    "one-existing-isolated-undirected-target-edge-is-used-throughout",
    "at-least-three-consecutive-A-contacts-are-required-and-the-next-stage-must-bind-the-exact-finite-count",
    "every-A-contact-has-the-same-positive-local-participation-duration-contact-shape-and-event-boundaries",
    "the-complete-DTS1-anatomy-carries-continuously-between-A-contacts-with-no-resource-reset",
    "each-field-readout-uses-one-value-identical-registered-S-H-probe-prestate-so-field-integration-does-not-accumulate-between-readouts",
    "readout-probes-do-not-commit-resource-poststates-or-enter-the-contact-train",
    "no-arm-label-contact-index-observed-result-or-future-state-may-control-a-transfer-or-field-proposal",
)
S1_IF_REQUIRED_RECORDS = (
    "complete-pre-and-post-contact-anatomy-at-every-A-contact",
    "accepted-target-edge-engagement-turnover-and-recovery-ledger-at-every-A-contact",
    "local-and-global-free-conductive-bound-refractory-ledger-residuals-at-every-checkpoint",
    "one-common-probe-applied-adapter-and-complete-S-H-field-output-from-every-precontact-anatomy",
    "oriented-target-edge-S-contrast-for-every-common-probe-readout",
    "complete-H-matched-or-H-ablated-common-probe-readout-series",
    "bit-exact-disabled-candidate-and-value-identical-replay-records",
)
S1_IF_DIRECTION_RULES = (
    "the-next-stage-must-preregister-a-strict-decrease-in-accepted-engagement-across-the-selected-equal-contact-checkpoints",
    "the-next-stage-must-preregister-the-corresponding-strict-directed-attenuation-of-the-common-probe-target-edge-contrast",
    "engagement-and-field-contrast-directions-must-both-pass-and-neither-may-substitute-for-the-other",
    "the-directed-common-probe-attenuation-must-remain-above-a-preregistered-float64-floor-after-H-is-matched-or-ablated",
    "all-directions-margins-floors-and-checkpoints-must-be-analytic-and-fixed-before-execution",
)
S1_IF_CONTROL_CASES = (
    (
        "N01_VALUE_IDENTICAL_REPLAY",
        "two-value-identical-complete-inputs-require-bit-exact-ledgers-adapters-and-complete-field-outputs",
    ),
    (
        "N02_A0_DISABLED_CANDIDATE",
        "candidate-disabled-common-probe-readouts-require-the-bit-exact-neutral-field-path-at-every-checkpoint",
    ),
    (
        "N03_FROZEN_PRESEQUENCE_ADAPTER",
        "one-adapter-fixed-from-the-presequence-binding-cannot-receive-contact-index-or-changing-DTS1-anatomy",
    ),
    (
        "N04_MATCHED_OR_ABLATED_H",
        "the-preregistered-directed-attenuation-must-remain-when-every-common-probe-H-prestate-is-value-identical-or-zero",
    ),
    (
        "N05_ZERO_PARTICIPATION",
        "zero-local-participation-requires-exactly-zero-engagement-with-no-contact-conditioned-field-claim",
    ),
)
S1_IF_BASELINE_COUNTERPREDICTIONS = (
    (
        "fixed-adapter-and-frozen-e1",
        "one-presequence-fixed-adapter-predicts-the-same-applied-coupling-for-every-value-identical-common-probe",
    ),
    (
        "leaky-trace-and-integrator",
        "value-identical-common-probe-S-H-prestates-remove-carried-field-state-and-provide-no-free-bound-refractory-ledger",
    ),
    (
        "dynamic-two-state-e1",
        "attenuation-alone-is-not-distinctive-so-S1IB-free-versus-refractory-intervention-and-S1IE-causal-readout-remain-jointly-required",
    ),
    (
        "f3-and-const-v",
        "without-local-three-role-turnover-the-baseline-has-no-direct-engagement-and-refractory-ledger-for-the-equal-contact-series",
    ),
    (
        "fast-afterimage",
        "matched-or-ablated-common-probe-H-removes-fast-afterimage-as-the-source-of-the-directed-readout-series",
    ),
)
S1_IF_ACCEPTANCE_RULES = (
    "the-active-series-and-all-five-controls-are-complete-for-the-preregistered-finite-contact-count",
    "every-contact-input-is-equal-except-for-the-continuously-carried-valid-DTS1-anatomy",
    "accepted-engagement-and-common-probe-field-contrast-both-have-the-preregistered-strict-attenuation-directions",
    "the-H-matched-or-ablated-directed-readout-remains-above-its-preregistered-floor",
    "all-anatomies-ledgers-field-domains-and-atomic-proposals-remain-valid",
    "all-five-baseline-counterpredictions-remain-unaugmented-and-recorded-without-model-execution-at-this-stage",
    "one-failure-makes-the-whole-attenuation-audit-STOPP-with-no-partial-PASS",
)
S1_IF_STOPP_CONDITIONS = (
    "any-unequal-A-participation-duration-contact-shape-event-boundary-or-common-probe-S-H-prestate",
    "any-resource-reset-contact-counter-phase-detector-label-reward-target-or-result-dependent-transfer",
    "accepted-engagement-does-not-have-the-preregistered-strict-decrease",
    "common-probe-field-contrast-does-not-have-the-preregistered-strict-directed-attenuation",
    "the-directed-readout-vanishes-at-or-below-floor-after-H-matching-or-ablation",
    "any-value-identical-A0-frozen-adapter-or-zero-participation-control-fails",
    "any-resource-creation-loss-negativity-clipping-normalization-or-invalid-field-domain",
    "any-baseline-receives-contact-index-hidden-resource-coordinate-arm-label-or-per-checkpoint-fit",
    "attenuation-alone-is-used-to-claim-separation-from-dynamic-two-state-E1",
    "result-dependent-fixture-count-checkpoint-direction-threshold-rate-retry-or-partial-output",
    "runtime-coupling-unregistered-execution-or-research-field-use",
)
S1_IF_FORBIDDEN_INTERPRETATIONS = (
    "interference-release-reuse-recovery-performance-or-material-evidence",
    "standalone-nonreducibility-to-dynamic-two-state-E1",
    "runtime-readiness-or-research-probe-authorization",
    "memory-learning-semantics-inner-context-organization-or-self-regulation",
    "organism-artificial-intelligence-new-natural-law-or-general-capability",
)
S1_IF_DECISION = "DTS1_REPEATED_EQUAL_CONTACT_ATTENUATION_CONTRACT_BOUND"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1IFAttenuationContract:
    contract_id: str
    source_s1hh_contract_digest: str
    source_s1ie_audit_receipt_digest: str
    candidate_id: str
    function_id: str
    sequence_rules: tuple[str, ...]
    required_records: tuple[str, ...]
    direction_rules: tuple[str, ...]
    control_cases: tuple[tuple[str, str], ...]
    baseline_counterpredictions: tuple[tuple[str, str], ...]
    acceptance_rules: tuple[str, ...]
    stopp_conditions: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    exact_contact_count_selected: bool
    fixture_values_selected: bool
    equation_added_or_changed: bool
    attenuation_harness_implemented: bool
    attenuation_executed: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    attenuation_proven: bool
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
            self.contract_id != S1_IF_CONTRACT_ID
            or self.source_s1hh_contract_digest != S1_IF_SOURCE_S1HH_CONTRACT_DIGEST
            or self.source_s1ie_audit_receipt_digest
            != S1_IF_SOURCE_S1IE_AUDIT_RECEIPT_DIGEST
            or self.candidate_id != S1_IF_CANDIDATE_ID
            or self.function_id != S1_IF_FUNCTION_ID
            or self.sequence_rules != S1_IF_SEQUENCE_RULES
            or self.required_records != S1_IF_REQUIRED_RECORDS
            or self.direction_rules != S1_IF_DIRECTION_RULES
            or self.control_cases != S1_IF_CONTROL_CASES
            or self.baseline_counterpredictions != S1_IF_BASELINE_COUNTERPREDICTIONS
            or self.acceptance_rules != S1_IF_ACCEPTANCE_RULES
            or self.stopp_conditions != S1_IF_STOPP_CONDITIONS
            or self.forbidden_interpretations != S1_IF_FORBIDDEN_INTERPRETATIONS
            or any(
                value is not False
                for value in (
                    self.exact_contact_count_selected,
                    self.fixture_values_selected,
                    self.equation_added_or_changed,
                    self.attenuation_harness_implemented,
                    self.attenuation_executed,
                    self.baseline_models_executed,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                    self.attenuation_proven,
                    self.broader_function_proven,
                    self.claims_permitted,
                )
            )
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.finite_fixture_contract_authorized_next_stage is not True
            or self.atomic_decision_required is not True
            or self.decision != S1_IF_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1IFAttenuationContractError(
                "S1-IF weakened the repeated-contact attenuation boundary"
            )


def build_dts1_s1if_attenuation_contract() -> DTS1S1IFAttenuationContract:
    """Bind attenuation measurements and falsification without execution."""

    values = {
        "contract_id": S1_IF_CONTRACT_ID,
        "source_s1hh_contract_digest": S1_IF_SOURCE_S1HH_CONTRACT_DIGEST,
        "source_s1ie_audit_receipt_digest": S1_IF_SOURCE_S1IE_AUDIT_RECEIPT_DIGEST,
        "candidate_id": S1_IF_CANDIDATE_ID,
        "function_id": S1_IF_FUNCTION_ID,
        "sequence_rules": S1_IF_SEQUENCE_RULES,
        "required_records": S1_IF_REQUIRED_RECORDS,
        "direction_rules": S1_IF_DIRECTION_RULES,
        "control_cases": S1_IF_CONTROL_CASES,
        "baseline_counterpredictions": S1_IF_BASELINE_COUNTERPREDICTIONS,
        "acceptance_rules": S1_IF_ACCEPTANCE_RULES,
        "stopp_conditions": S1_IF_STOPP_CONDITIONS,
        "forbidden_interpretations": S1_IF_FORBIDDEN_INTERPRETATIONS,
        "exact_contact_count_selected": False,
        "fixture_values_selected": False,
        "equation_added_or_changed": False,
        "attenuation_harness_implemented": False,
        "attenuation_executed": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "attenuation_proven": False,
        "broader_function_proven": False,
        "claims_permitted": False,
        "finite_fixture_contract_authorized_next_stage": True,
        "atomic_decision_required": True,
        "decision": S1_IF_DECISION,
    }
    return DTS1S1IFAttenuationContract(**values, contract_digest=_digest(values))
