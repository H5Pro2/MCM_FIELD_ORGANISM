"""Static S1-KJ selection contract for the finite B2/P_IE case."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1jz_finite_orchestrator_api_contract import (
    S1_JZ_FRESH_STATE_RECORDS,
)
from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    S1_JX_CASE_RECORDS,
    S1_JX_REPLICA_RECORDS,
)
from .dynamic_substrate_s1ke_dual_refinement_digest_contract import (
    S1_KE_COMPARISON_DIGEST_ROLE,
    S1_KE_COMPLETE_PROVENANCE_DIGEST_ROLE,
    S1_KE_CORRECTED_OUTPUT_SCHEMA,
)
from .dynamic_substrate_s1ki_b1_pie_case_output_contract import (
    build_dts1_s1ki_b1_pie_case_output_contract,
)


class DTS1S1KJB2PIECaseSelectionContractError(ValueError):
    """Raised when the finite S1-KJ case selection is weakened."""


S1_KJ_CONTRACT_ID = "dynamic-substrate.b2-pie-case-selection.s1kj.v1"
S1_KJ_SOURCE_S1KI_DIGEST = (
    "1797308317415797115ad4a0e6e44ded67b73f088cd4fb11d5b578b339b8b5f1"
)
S1_KJ_CASE_ID = "C05"
S1_KJ_TARGET_REPLICA_IDS = (
    "B2:P_IE_CAUSAL_TWO_SUBSTEP:r2",
    "B2:P_IE_CAUSAL_TWO_SUBSTEP:r4",
    "B2:P_IE_CAUSAL_TWO_SUBSTEP:r8",
)
S1_KJ_TARGET_CASE_RECORD = next(
    row for row in S1_JX_CASE_RECORDS if row[0] == S1_KJ_CASE_ID
)
S1_KJ_TARGET_REPLICA_RECORDS = tuple(
    row for row in S1_JX_REPLICA_RECORDS if row[0] in S1_KJ_TARGET_REPLICA_IDS
)
S1_KJ_FRESH_STATE_RECORD = next(
    row
    for row in S1_JZ_FRESH_STATE_RECORDS
    if row[0] == "B2" and row[1] == "TWO_NODE_OPEN_LINE"
)
S1_KJ_FRESH_FIELD_DIGEST = (
    "389f731c42f91164332fcfda65cc5130d5090db7f03e211736ae0bb6c1ca2f61"
)
S1_KJ_FRESH_PRIVATE_STATE_DIGEST = (
    "06f8e90d235e9676cbdca36863d63c4b1b8f4bda1f508c4110c0bcd5916d3b9d"
)
S1_KJ_FRESH_START_RULES = (
    "r2-r4-and-r8-each-start-from-an-independent-corrected-B2-fresh-state",
    "P_IE_F_HIGH-and-P_IE_R_HIGH-each-start-from-that-sequences-own-fresh-state",
    "complete-L-state-carries-only-between-the-two-ordered-intervals-of-one-sequence",
    "no-field-L-state-output-or-provenance-carries-between-sequences-or-refinements",
)
S1_KJ_EXECUTION_BUDGET = (
    ("target_replica_count", 3),
    ("interval_calls_per_replica", 4),
    ("maximum_new_interval_calls", 12),
    ("retry_or_repeat_calls", 0),
)
S1_KJ_OUTPUT_ACCEPTANCE_RULES = (
    "each-replica-publishes-one-atomic-mcm.s1jz.complete-replica-output.v2-or-one-error",
    "each-output-carries-one-complete-provenance-digest-and-one-refinement-comparison-digest",
    "B2-refinement-comparison-digests-must-be-bit-identical-across-r2-r4-r8",
    "complete-output-digests-remain-identity-bearing-and-must-not-be-used-for-refinement-equality",
    "all-three-replicas-must-pass-before-C05-may-be-composed-in-a-later-stage",
)
S1_KJ_SELECTION_RATIONALE = (
    "B2-is-the-registered-stateful-S2-linear-integrator-counterbaseline",
    "B2-receives-the-same-P_IE-profile-and-two-node-geometry-as-completed-B1-C01",
    "same-profile-progression-is-a-controlled-next-case-selection-not-a-baseline-judgment",
)
S1_KJ_FORBIDDEN_SCOPE = (
    "no-runner-initializer-adapter-or-output-implementation",
    "no-replica-interval-retry-or-repeat-execution",
    "no-C05-output-or-24-case-matrix-publication",
    "no-baseline-closure-ranking-candidate-comparison-runtime-or-research-run",
    "no-memory-learning-intelligence-or-organism-property-claim",
)
S1_KJ_DECISION = (
    "B2_PIE_C05_SELECTED_THREE_REFINEMENT_DUAL_DIGEST_TWELVE_CALL_CONTRACT_BOUND_NO_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1KJB2PIECaseSelectionContract:
    contract_id: str
    source_s1ki_digest: str
    target_case_record: tuple[object, ...]
    target_replica_ids: tuple[str, ...]
    target_replica_records: tuple[tuple[object, ...], ...]
    corrected_fresh_state_record: tuple[object, ...]
    fresh_field_digest: str
    fresh_private_state_digest: str
    complete_provenance_digest_role: tuple[tuple[str, object], ...]
    comparison_digest_role: tuple[tuple[str, object], ...]
    corrected_output_schema: tuple[tuple[str, object], ...]
    fresh_start_rules: tuple[str, ...]
    execution_budget: tuple[tuple[str, int], ...]
    output_acceptance_rules: tuple[str, ...]
    selection_rationale: tuple[str, ...]
    forbidden_scope: tuple[str, ...]
    target_replica_count: int
    intervals_per_target_replica: int
    maximum_new_interval_calls: int
    case_selected: bool
    runner_extension_implemented: bool
    target_replicas_executed: int
    interval_calls_executed: int
    case_output_composed: bool
    matrix_24_case_output_published: bool
    baseline_judgment_present: bool
    runtime_integration_present: bool
    exact_implementation_execution_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_KJ_CONTRACT_ID
            or self.source_s1ki_digest != S1_KJ_SOURCE_S1KI_DIGEST
            or self.target_case_record != S1_KJ_TARGET_CASE_RECORD
            or self.target_replica_ids != S1_KJ_TARGET_REPLICA_IDS
            or self.target_replica_records != S1_KJ_TARGET_REPLICA_RECORDS
            or self.corrected_fresh_state_record != S1_KJ_FRESH_STATE_RECORD
            or self.fresh_field_digest != S1_KJ_FRESH_FIELD_DIGEST
            or self.fresh_private_state_digest != S1_KJ_FRESH_PRIVATE_STATE_DIGEST
            or self.complete_provenance_digest_role != S1_KE_COMPLETE_PROVENANCE_DIGEST_ROLE
            or self.comparison_digest_role != S1_KE_COMPARISON_DIGEST_ROLE
            or self.corrected_output_schema != S1_KE_CORRECTED_OUTPUT_SCHEMA
            or self.fresh_start_rules != S1_KJ_FRESH_START_RULES
            or self.execution_budget != S1_KJ_EXECUTION_BUDGET
            or self.output_acceptance_rules != S1_KJ_OUTPUT_ACCEPTANCE_RULES
            or self.selection_rationale != S1_KJ_SELECTION_RATIONALE
            or self.forbidden_scope != S1_KJ_FORBIDDEN_SCOPE
            or self.target_replica_count != 3
            or self.intervals_per_target_replica != 4
            or self.maximum_new_interval_calls != 12
            or self.case_selected is not True
            or self.runner_extension_implemented is not False
            or self.target_replicas_executed != 0
            or self.interval_calls_executed != 0
            or self.case_output_composed is not False
            or self.matrix_24_case_output_published is not False
            or self.baseline_judgment_present is not False
            or self.runtime_integration_present is not False
            or self.exact_implementation_execution_authorized_next_stage is not True
            or self.decision != S1_KJ_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1KJB2PIECaseSelectionContractError(
                "S1-KJ weakened the finite B2/P_IE case selection"
            )


def build_dts1_s1kj_b2_pie_case_selection_contract(
) -> DTS1S1KJB2PIECaseSelectionContract:
    """Select and bind C05 without implementing or executing its replicas."""

    source = build_dts1_s1ki_b1_pie_case_output_contract()
    if source.contract_digest != S1_KJ_SOURCE_S1KI_DIGEST:
        raise DTS1S1KJB2PIECaseSelectionContractError("S1-KI source differs")
    if (
        len(S1_KJ_TARGET_REPLICA_RECORDS) != 3
        or tuple(row[0] for row in S1_KJ_TARGET_REPLICA_RECORDS)
        != S1_KJ_TARGET_REPLICA_IDS
        or S1_KJ_FRESH_STATE_RECORD[6] != S1_KJ_FRESH_FIELD_DIGEST
        or S1_KJ_FRESH_STATE_RECORD[8] != S1_KJ_FRESH_PRIVATE_STATE_DIGEST
    ):
        raise DTS1S1KJB2PIECaseSelectionContractError(
            "registered C05 replicas or corrected B2 fresh state differ"
        )
    values = {
        "contract_id": S1_KJ_CONTRACT_ID,
        "source_s1ki_digest": source.contract_digest,
        "target_case_record": S1_KJ_TARGET_CASE_RECORD,
        "target_replica_ids": S1_KJ_TARGET_REPLICA_IDS,
        "target_replica_records": S1_KJ_TARGET_REPLICA_RECORDS,
        "corrected_fresh_state_record": S1_KJ_FRESH_STATE_RECORD,
        "fresh_field_digest": S1_KJ_FRESH_FIELD_DIGEST,
        "fresh_private_state_digest": S1_KJ_FRESH_PRIVATE_STATE_DIGEST,
        "complete_provenance_digest_role": S1_KE_COMPLETE_PROVENANCE_DIGEST_ROLE,
        "comparison_digest_role": S1_KE_COMPARISON_DIGEST_ROLE,
        "corrected_output_schema": S1_KE_CORRECTED_OUTPUT_SCHEMA,
        "fresh_start_rules": S1_KJ_FRESH_START_RULES,
        "execution_budget": S1_KJ_EXECUTION_BUDGET,
        "output_acceptance_rules": S1_KJ_OUTPUT_ACCEPTANCE_RULES,
        "selection_rationale": S1_KJ_SELECTION_RATIONALE,
        "forbidden_scope": S1_KJ_FORBIDDEN_SCOPE,
        "target_replica_count": 3,
        "intervals_per_target_replica": 4,
        "maximum_new_interval_calls": 12,
        "case_selected": True,
        "runner_extension_implemented": False,
        "target_replicas_executed": 0,
        "interval_calls_executed": 0,
        "case_output_composed": False,
        "matrix_24_case_output_published": False,
        "baseline_judgment_present": False,
        "runtime_integration_present": False,
        "exact_implementation_execution_authorized_next_stage": True,
        "decision": S1_KJ_DECISION,
    }
    return DTS1S1KJB2PIECaseSelectionContract(
        **values, contract_digest=_digest(values)
    )
