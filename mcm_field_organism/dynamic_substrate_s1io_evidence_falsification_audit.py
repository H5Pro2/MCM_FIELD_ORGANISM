"""Static S1-IO evidence and falsification audit for DTS-1."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json


class DTS1S1IOEvidenceAuditError(ValueError):
    """Raised when the closed S1-IO evidence classification is weakened."""


S1_IO_AUDIT_ID = "dynamic-substrate.synthetic-evidence-falsification.s1io.v1"
S1_IO_SOURCE_S1HH_CONTRACT_DIGEST = (
    "5eae6462ed7019f3e2f09b0f1ba0ae3859781c7be852d7d4cdf011b4ae602388"
)
S1_IO_SOURCE_AUDIT_RECEIPTS = (
    ("S1-IB", "55159311a95b555900632014d68b3534aeb958787e0e6bcfba4d3e32dfedb217"),
    ("S1-IE", "dbaa141450f1a00defb71824feb4e61bbef727c0023ea1d1e19cc979581ebcea"),
    ("S1-IH", "2fd24fd7ccdee690ea5610440e2d76f85e6a5ca0b8bc4b9045ff7c12a34d0c36"),
    ("S1-IK", "7d0a5bffd19cc7f212392b1d4a9c4d8ea8c79ffb1414d6a9fbc9a936ff9dedfe"),
    ("S1-IN", "521dcb2750b87315550552979c4d1fe4ab7cd045fef4f3218265c3a32959a245"),
)
S1_IO_MEASUREMENT_CLASSIFICATIONS = (
    ("M01_LOCAL_GLOBAL_THREE_ROLE_LEDGER", "SUPPORTED_FINITE_SYNTHETIC", ("S1-IB", "S1-IE", "S1-IH", "S1-IK", "S1-IN")),
    ("M02_REPEATED_EQUAL_CONTACT_ATTENUATION", "SUPPORTED_FINITE_SYNTHETIC", ("S1-IH",)),
    ("M03_ABA_MATCHED_GAP_INTERFERENCE", "SUPPORTED_FINITE_SYNTHETIC", ("S1-IK",)),
    ("M04_FREE_RECOVERY_AND_ADJACENT_REUSE", "SUPPORTED_FINITE_SYNTHETIC", ("S1-IN",)),
    ("M05_WITHIN_PROBE_SUBSTRATE_AND_FIELD_CHECKPOINTS", "SUPPORTED_FINITE_SYNTHETIC", ("S1-IE",)),
    ("M06_SH_MATCHED_FREE_REFRACTORY_INTERVENTION", "SUPPORTED_JOINT_FINITE_SYNTHETIC", ("S1-IB", "S1-IE")),
    ("M07_CANDIDATE_DISABLED_NULL_PATH", "SUPPORTED_FINITE_SYNTHETIC", ("S1-IE", "S1-IH", "S1-IK", "S1-IN")),
)
S1_IO_BASELINE_CLASSIFICATIONS = (
    ("fixed-adapter-and-frozen-e1", "TECHNICAL_COUNTERCONTROLS_SUPPORTED_GLOBAL_FIT_OPEN", ("S1-IE", "S1-IH", "S1-IK", "S1-IN")),
    ("leaky-trace-and-integrator", "MATCHED_STATE_EFFECTS_SUPPORTED_BASELINE_NOT_EXECUTED", ("S1-IK",)),
    ("dynamic-two-state-e1", "REGISTERED_STATE_SPACE_COUNTERPREDICTION_SUPPORTED", ("S1-IB", "S1-IE")),
    ("f3-and-const-v", "DIRECT_PARTITION_INTERVENTION_SUPPORTED_BASELINE_NOT_EXECUTED", ("S1-IB", "S1-IE")),
    ("fast-afterimage", "ZERO_H_COUNTERCONTROLS_SUPPORTED", ("S1-IE", "S1-IH", "S1-IK", "S1-IN")),
)
S1_IO_FALSIFICATION_CLASSIFICATIONS = (
    ("F01_RESOURCE_CREATION_LOSS_OR_INVALID_STATE", "NOT_TRIGGERED_IN_REGISTERED_FINITE_FIXTURES", ("S1-IB", "S1-IE", "S1-IH", "S1-IK", "S1-IN")),
    ("F02_LABEL_REWARD_COUNTER_PHASE_RESET_OR_TARGET_REQUIRED", "NOT_USED_BY_PRIVATE_AUDIT_PATHS", ("S1-IB", "S1-IE", "S1-IH", "S1-IK", "S1-IN")),
    ("F03_NO_MEASURABLE_ATTENUATION", "CONTRADICTED_BY_REGISTERED_RESULT", ("S1-IH",)),
    ("F04_NO_MATCHED_GAP_COMPETITOR_EFFECT", "CONTRADICTED_BY_REGISTERED_RESULT", ("S1-IK",)),
    ("F05_NO_RELEASE_OR_CAPACITY_REUSE", "CONTRADICTED_BY_REGISTERED_RESULT", ("S1-IN",)),
    ("F06_ONE_FIXED_ADAPTER_REPRODUCES_COMPLETE_TRAJECTORY", "OPEN_GLOBAL_BASELINE_CLOSURE", ("S1-IE", "S1-IH", "S1-IK", "S1-IN")),
    ("F07_ONE_LEAKY_OR_INTEGRATOR_BASELINE_REPRODUCES_ALL_PROFILES", "OPEN_BASELINE_NOT_EXECUTED", ()),
    ("F08_F3_OR_CONSTV_REPRODUCES_ALL_PROFILES_AND_INTERVENTIONS", "OPEN_BASELINE_NOT_EXECUTED", ("S1-IB", "S1-IE")),
    ("F09_EFFECT_VANISHES_WITH_H_MATCHED_OR_ZERO", "CONTRADICTED_BY_REGISTERED_ZERO_H_CONTROLS", ("S1-IE", "S1-IH", "S1-IK", "S1-IN")),
    ("F10_FREE_REFRACTORY_INTERVENTION_HAS_NO_CAPACITY_EFFECT", "CONTRADICTED_BY_REGISTERED_RESULT", ("S1-IB", "S1-IE")),
)
S1_IO_SCOPE_CONCLUSIONS = (
    "all-seven-S1HH-required-measurement-roles-have-finite-synthetic-support",
    "no-direct-registered-functional-falsification-condition-was-triggered",
    "dynamic-two-state-E1-lacks-the-registered-free-versus-refractory-state-pair-by-its-bound-state-space",
    "fixed-adapter-leaky-integrator-and-F3-CONSTV-global-baseline-closure-remains-incomplete",
    "the-current-result-is-a-constructed-synthetic-substrate-function-set-not-a-material-or-runtime-finding",
    "no-further-same-fixture-variant-is-authorized-before-joint-baseline-closure-is-bound",
)
S1_IO_FORBIDDEN_INTERPRETATIONS = (
    "complete-baseline-rejection-or-universal-model-nonreducibility",
    "material-validity-physical-timescale-runtime-readiness-or-research-field-authorization",
    "memory-learning-forgetting-semantics-inner-context-organization-or-self-regulation",
    "organism-artificial-intelligence-new-natural-law-or-general-capability",
)
S1_IO_DECISION = "DTS1_SYNTHETIC_MINIMUM_FUNCTION_SET_SUPPORTED_BASELINE_CLOSURE_OPEN"


def _digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1IOEvidenceFalsificationAudit:
    audit_id: str
    source_s1hh_contract_digest: str
    source_audit_receipts: tuple[tuple[str, str], ...]
    measurement_classifications: tuple[tuple[str, str, tuple[str, ...]], ...]
    baseline_classifications: tuple[tuple[str, str, tuple[str, ...]], ...]
    falsification_classifications: tuple[tuple[str, str, tuple[str, ...]], ...]
    scope_conclusions: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    all_required_measurement_roles_supported: bool
    direct_function_falsification_triggered: bool
    baseline_closure_complete: bool
    candidate_globally_validated: bool
    equation_added_or_changed: bool
    fixture_added_or_changed: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_resource_calls_executed: int
    technical_field_calls_executed: int
    research_field_steps_executed: int
    claims_permitted: bool
    joint_baseline_contract_authorized_next_stage: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = {field.name: getattr(self, field.name) for field in fields(self) if field.name != "audit_digest"}
        if (
            self.audit_id != S1_IO_AUDIT_ID
            or self.source_s1hh_contract_digest != S1_IO_SOURCE_S1HH_CONTRACT_DIGEST
            or self.source_audit_receipts != S1_IO_SOURCE_AUDIT_RECEIPTS
            or self.measurement_classifications != S1_IO_MEASUREMENT_CLASSIFICATIONS
            or self.baseline_classifications != S1_IO_BASELINE_CLASSIFICATIONS
            or self.falsification_classifications != S1_IO_FALSIFICATION_CLASSIFICATIONS
            or self.scope_conclusions != S1_IO_SCOPE_CONCLUSIONS
            or self.forbidden_interpretations != S1_IO_FORBIDDEN_INTERPRETATIONS
            or self.all_required_measurement_roles_supported is not True
            or self.joint_baseline_contract_authorized_next_stage is not True
            or any(
                value is not False
                for value in (
                    self.direct_function_falsification_triggered,
                    self.baseline_closure_complete,
                    self.candidate_globally_validated,
                    self.equation_added_or_changed,
                    self.fixture_added_or_changed,
                    self.baseline_models_executed,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                    self.claims_permitted,
                )
            )
            or self.technical_resource_calls_executed != 0
            or self.technical_field_calls_executed != 0
            or self.research_field_steps_executed != 0
            or self.decision != S1_IO_DECISION
            or self.audit_digest != _digest(payload)
        ):
            raise DTS1S1IOEvidenceAuditError("S1-IO weakened the evidence or baseline boundary")


def build_dts1_s1io_evidence_falsification_audit() -> DTS1S1IOEvidenceFalsificationAudit:
    """Classify immutable receipts without executing a model or field."""

    values = {
        "audit_id": S1_IO_AUDIT_ID,
        "source_s1hh_contract_digest": S1_IO_SOURCE_S1HH_CONTRACT_DIGEST,
        "source_audit_receipts": S1_IO_SOURCE_AUDIT_RECEIPTS,
        "measurement_classifications": S1_IO_MEASUREMENT_CLASSIFICATIONS,
        "baseline_classifications": S1_IO_BASELINE_CLASSIFICATIONS,
        "falsification_classifications": S1_IO_FALSIFICATION_CLASSIFICATIONS,
        "scope_conclusions": S1_IO_SCOPE_CONCLUSIONS,
        "forbidden_interpretations": S1_IO_FORBIDDEN_INTERPRETATIONS,
        "all_required_measurement_roles_supported": True,
        "direct_function_falsification_triggered": False,
        "baseline_closure_complete": False,
        "candidate_globally_validated": False,
        "equation_added_or_changed": False,
        "fixture_added_or_changed": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_resource_calls_executed": 0,
        "technical_field_calls_executed": 0,
        "research_field_steps_executed": 0,
        "claims_permitted": False,
        "joint_baseline_contract_authorized_next_stage": True,
        "decision": S1_IO_DECISION,
    }
    return DTS1S1IOEvidenceFalsificationAudit(**values, audit_digest=_digest(values))
