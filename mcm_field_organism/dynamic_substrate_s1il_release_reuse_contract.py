"""Static S1-IL contract for local DTS-1 capacity release and reuse."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json


class DTS1S1ILReleaseReuseContractError(ValueError):
    """Raised when the closed S1-IL release/reuse boundary is weakened."""


S1_IL_CONTRACT_ID = "dynamic-substrate.local-capacity-release-reuse.s1il.v1"
S1_IL_SOURCE_S1HH_CONTRACT_DIGEST = (
    "5eae6462ed7019f3e2f09b0f1ba0ae3859781c7be852d7d4cdf011b4ae602388"
)
S1_IL_SOURCE_S1IK_AUDIT_RECEIPT_DIGEST = (
    "7d0a5bffd19cc7f212392b1d4a9c4d8ea8c79ffb1414d6a9fbc9a936ff9dedfe"
)
S1_IL_CANDIDATE_ID = "DTS1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER"
S1_IL_FUNCTION_ID = "DTS1_LOCAL_REFRACTORY_RELEASE_AND_ADJACENT_EDGE_REUSE"

S1_IL_ARM_IDS = (
    "RECOVERY_ON_THEN_ADJACENT_B_PROBE",
    "RECOVERY_OFF_THEN_ADJACENT_B_PROBE",
)
S1_IL_GEOMETRY_RULES = (
    "one-open-three-node-line-with-existing-adjacent-edges-A-and-B",
    "A-and-B-share-exactly-one-middle-endpoint-with-one-finite-local-ledger",
    "both-arms-start-from-one-bit-exact-post-A-load-anatomy-with-positive-refractory-resource",
    "outer-capacities-edge-identities-total-resource-and-complete-initial-anatomy-are-arm-identical",
    "no-new-edge-resource-transport-global-allocator-reset-or-hidden-state-is-permitted",
)
S1_IL_SEQUENCE_RULES = (
    "first-form-one-common-positive-A-load-state-before-the-two-arms-diverge",
    "the-release-window-has-zero-edge-participation-and-identical-positive-duration-turnover-rate-and-event-boundaries",
    "only-the-refractory-to-free-recovery-channel-is-active-in-recovery-on-and-ablated-in-recovery-off",
    "the-recovery-intervention-must-not-change-conductive-turnover-or-any-field-state",
    "after-the-release-window-both-arms-receive-one-value-identical-positive-B-probe-on-the-adjacent-edge",
    "the-B-probe-reads-the-complete-carried-anatomy-and-is-committed-before-any-separate-field-readout",
    "separate-common-S-H-readouts-may-read-preprobe-and-postprobe-anatomies-but-their-resource-poststates-are-discarded",
    "no-arm-label-time-index-result-value-future-state-or-target-direction-may-control-a-resource-or-field-proposal",
)
S1_IL_REQUIRED_RECORDS = (
    "complete-pre-and-post-anatomy-and-transfer-ledger-for-load-release-window-and-B-probe",
    "recovery-channel-transfer-on-every-edge-and-free-resource-at-every-node-during-the-release-window",
    "shared-endpoint-free-resource-immediately-before-the-identical-B-probe",
    "accepted-B-engagement-turnover-recovery-and-node-admission-diagnostics-in-both-arms",
    "local-and-global-free-conductive-bound-refractory-ledger-residuals-at-every-checkpoint",
    "cumulative-shared-endpoint-recovery-margin-and-additional-B-engagement-kept-as-separate-measures",
    "common-S-H-field-readouts-with-applied-adapters-and-complete-output-vectors-if-field-readout-is-retained",
    "bit-exact-value-identical-replay-recovery-zero-B-zero-A0-frozen-adapter-and-H-controls",
)
S1_IL_DIRECTION_RULES = (
    "recovery-on-must-transfer-a-strictly-positive-amount-from-refractory-to-free-during-the-zero-contact-window",
    "conductive-bound-poststates-after-the-release-window-must-be-bit-exact-between-recovery-on-and-recovery-off",
    "refractory-resource-must-be-strictly-lower-and-shared-free-resource-strictly-higher-with-recovery-on",
    "accepted-B-engagement-must-be-strictly-higher-after-recovery-on-than-after-recovery-off",
    "the-next-stage-must-preregister-a-nonsaturating-fixture-and-all-ledger-margins-before-execution",
    "release-and-reuse-directions-must-both-pass-and-neither-a-field-output-nor-one-direction-may-substitute-for-the-other",
    "any-field-direction-floor-and-H-control-must-be-fixed-analytically-before-execution",
)
S1_IL_CONTROL_CASES = (
    (
        "N01_VALUE_IDENTICAL_SEQUENCE_REPLAY",
        "two-value-identical-complete-sequences-require-bit-exact-ledgers-anatomies-and-readouts",
    ),
    (
        "N02_RECOVERY_ZERO_EQUALS_RECOVERY_OFF",
        "recovery-rate-zero-must-be-bit-exact-to-the-explicitly-ablated-recovery-window",
    ),
    (
        "N03_ZERO_REFRACTORY_SOURCE",
        "with-zero-refractory-and-zero-turnover-source-the-release-window-must-transfer-exactly-zero-recovery",
    ),
    (
        "N04_ZERO_B_PROBE_PARTICIPATION",
        "zero-B-participation-requires-exactly-zero-B-engagement-in-both-arms",
    ),
    (
        "N05_A0_DISABLED_FIELD_READOUT",
        "candidate-disabled-common-readouts-require-the-bit-exact-neutral-field-path",
    ),
    (
        "N06_FROZEN_PRERELEASE_ADAPTER",
        "one-adapter-fixed-before-release-cannot-turn-a-ledger-margin-into-an-arm-specific-readout",
    ),
    (
        "N07_MATCHED_OR_ABLATED_H",
        "any-preregistered-field-separation-must-remain-with-H-value-identical-or-zero",
    ),
)
S1_IL_BASELINE_COUNTERPREDICTIONS = (
    (
        "fixed-adapter-and-frozen-e1",
        "one-prerelease-fixed-adapter-has-no-refractory-to-free-ledger-transfer-or-subsequent-shared-capacity-admission",
    ),
    (
        "leaky-trace-and-integrator",
        "matched-fresh-S-H-readouts-remove-carried-field-state-while-direct-release-and-B-admission-ledgers-remain",
    ),
    (
        "dynamic-two-state-e1",
        "release-and-reuse-alone-are-not-distinctive-so-the-S1IB-free-refractory-intervention-remains-jointly-required",
    ),
    (
        "f3-and-const-v",
        "without-one-conserved-local-three-role-ledger-the-baseline-has-no-direct-refractory-release-and-adjacent-rebinding-record",
    ),
    (
        "fast-afterimage",
        "matched-or-ablated-H-cannot-create-a-refractory-to-free-ledger-transfer-or-positive-B-engagement-margin",
    ),
)
S1_IL_ACCEPTANCE_RULES = (
    "both-active-arms-and-all-seven-controls-are-complete-for-one-preregistered-finite-sequence",
    "all-arm-matching-causality-anatomy-ledger-and-atomicity-rules-pass",
    "positive-direct-release-higher-shared-free-resource-and-higher-B-engagement-have-all-preregistered-directions",
    "all-five-baseline-counterpredictions-remain-unaugmented-and-recorded-without-model-execution-at-this-stage",
    "one-failure-makes-the-whole-release-reuse-audit-STOPP-with-no-partial-PASS",
)
S1_IL_STOPP_CONDITIONS = (
    "any-unmatched-load-state-release-duration-turnover-rate-event-boundary-B-probe-or-common-readout",
    "A-and-B-do-not-share-exactly-one-finite-endpoint-ledger",
    "recovery-on-is-not-positive-or-does-not-produce-more-shared-free-resource-than-recovery-off",
    "B-engagement-after-recovery-on-is-not-strictly-higher-than-after-recovery-off",
    "release-is-inferred-only-from-field-amplitude-or-reuse-is-inferred-without-direct-B-engagement",
    "any-value-identical-recovery-zero-source-zero-B-zero-A0-frozen-adapter-or-H-control-fails",
    "any-resource-creation-loss-negativity-clipping-normalization-invalid-field-domain-or-partial-commit",
    "any-baseline-receives-arm-label-hidden-resource-coordinate-or-per-arm-fit",
    "release-and-reuse-alone-are-used-to-claim-separation-from-dynamic-two-state-E1",
    "result-dependent-fixture-threshold-direction-rate-retry-or-partial-output",
    "runtime-coupling-unregistered-execution-or-research-field-use",
)
S1_IL_FORBIDDEN_INTERPRETATIONS = (
    "material-general-performance-or-runtime-readiness-evidence",
    "standalone-nonreducibility-to-dynamic-two-state-E1",
    "memory-learning-forgetting-semantics-inner-context-organization-or-self-regulation",
    "organism-artificial-intelligence-new-natural-law-or-general-capability",
)
S1_IL_DECISION = "DTS1_LOCAL_CAPACITY_RELEASE_AND_ADJACENT_REUSE_CONTRACT_BOUND"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1ILReleaseReuseContract:
    contract_id: str
    source_s1hh_contract_digest: str
    source_s1ik_audit_receipt_digest: str
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
    harness_implemented: bool
    release_reuse_executed: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    release_proven: bool
    reuse_proven: bool
    e1_nonreducibility_proven: bool
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
            self.contract_id != S1_IL_CONTRACT_ID
            or self.source_s1hh_contract_digest != S1_IL_SOURCE_S1HH_CONTRACT_DIGEST
            or self.source_s1ik_audit_receipt_digest != S1_IL_SOURCE_S1IK_AUDIT_RECEIPT_DIGEST
            or self.candidate_id != S1_IL_CANDIDATE_ID
            or self.function_id != S1_IL_FUNCTION_ID
            or self.arm_ids != S1_IL_ARM_IDS
            or self.geometry_rules != S1_IL_GEOMETRY_RULES
            or self.sequence_rules != S1_IL_SEQUENCE_RULES
            or self.required_records != S1_IL_REQUIRED_RECORDS
            or self.direction_rules != S1_IL_DIRECTION_RULES
            or self.control_cases != S1_IL_CONTROL_CASES
            or self.baseline_counterpredictions != S1_IL_BASELINE_COUNTERPREDICTIONS
            or self.acceptance_rules != S1_IL_ACCEPTANCE_RULES
            or self.stopp_conditions != S1_IL_STOPP_CONDITIONS
            or self.forbidden_interpretations != S1_IL_FORBIDDEN_INTERPRETATIONS
            or any(
                value is not False
                for value in (
                    self.fixture_values_selected,
                    self.equation_added_or_changed,
                    self.harness_implemented,
                    self.release_reuse_executed,
                    self.baseline_models_executed,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                    self.release_proven,
                    self.reuse_proven,
                    self.e1_nonreducibility_proven,
                    self.claims_permitted,
                )
            )
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.finite_fixture_contract_authorized_next_stage is not True
            or self.atomic_decision_required is not True
            or self.decision != S1_IL_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1ILReleaseReuseContractError(
                "S1-IL weakened the local release/reuse boundary"
            )


def build_dts1_s1il_release_reuse_contract() -> DTS1S1ILReleaseReuseContract:
    """Bind local capacity release and adjacent reuse without values or execution."""

    values = {
        "contract_id": S1_IL_CONTRACT_ID,
        "source_s1hh_contract_digest": S1_IL_SOURCE_S1HH_CONTRACT_DIGEST,
        "source_s1ik_audit_receipt_digest": S1_IL_SOURCE_S1IK_AUDIT_RECEIPT_DIGEST,
        "candidate_id": S1_IL_CANDIDATE_ID,
        "function_id": S1_IL_FUNCTION_ID,
        "arm_ids": S1_IL_ARM_IDS,
        "geometry_rules": S1_IL_GEOMETRY_RULES,
        "sequence_rules": S1_IL_SEQUENCE_RULES,
        "required_records": S1_IL_REQUIRED_RECORDS,
        "direction_rules": S1_IL_DIRECTION_RULES,
        "control_cases": S1_IL_CONTROL_CASES,
        "baseline_counterpredictions": S1_IL_BASELINE_COUNTERPREDICTIONS,
        "acceptance_rules": S1_IL_ACCEPTANCE_RULES,
        "stopp_conditions": S1_IL_STOPP_CONDITIONS,
        "forbidden_interpretations": S1_IL_FORBIDDEN_INTERPRETATIONS,
        "fixture_values_selected": False,
        "equation_added_or_changed": False,
        "harness_implemented": False,
        "release_reuse_executed": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "release_proven": False,
        "reuse_proven": False,
        "e1_nonreducibility_proven": False,
        "claims_permitted": False,
        "finite_fixture_contract_authorized_next_stage": True,
        "atomic_decision_required": True,
        "decision": S1_IL_DECISION,
    }
    return DTS1S1ILReleaseReuseContract(**values, contract_digest=_digest(values))
