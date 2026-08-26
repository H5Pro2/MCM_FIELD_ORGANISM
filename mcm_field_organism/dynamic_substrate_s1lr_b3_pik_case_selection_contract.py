"""Static S1-LR selection contract for the finite B3/P_IK case."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1jz_finite_orchestrator_api_contract import S1_JZ_FRESH_STATE_RECORDS
from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    S1_JX_CASE_RECORDS,
    S1_JX_REPLICA_RECORDS,
    S1_JX_SEQUENCE_RECORDS,
)
from .dynamic_substrate_s1ke_dual_refinement_digest_contract import (
    S1_KE_COMPARISON_DIGEST_ROLE,
    S1_KE_COMPLETE_PROVENANCE_DIGEST_ROLE,
    S1_KE_CORRECTED_OUTPUT_SCHEMA,
)
from .dynamic_substrate_s1lp_b3_pih_case_output_contract import (
    S1_LP_CASE_ID,
    build_dts1_s1lp_b3_pih_case_output_contract,
)


class DTS1S1LRB3PIKCaseSelectionContractError(ValueError):
    """Raised when the static S1-LR case selection is weakened."""


S1_LR_CONTRACT_ID = "dynamic-substrate.b3-pik-case-selection.s1lr.v1"
S1_LR_SOURCE_S1LP_DIGEST = (
    "ae1ec48d4e8dd36a022c4b6434651deff8f65890315658d5121e716f0d149f90"
)
S1_LR_SOURCE_S1LP_DECISION = (
    "C10_B3_PIH_THREE_REFINEMENT_CASE_OUTPUT_BOUND_FROM_S1LO_RECEIPT_NO_NEW_EXECUTION"
)
S1_LR_CASE_ID = "C11"
S1_LR_SEQUENCE_KEYS = ("P_IK_A_B_A", "P_IK_A_GAP_A")
S1_LR_TARGET_REPLICA_IDS = (
    "B3:P_IK_INTERFERENCE:r2",
    "B3:P_IK_INTERFERENCE:r4",
    "B3:P_IK_INTERFERENCE:r8",
)
S1_LR_TARGET_CASE_RECORD = next(row for row in S1_JX_CASE_RECORDS if row[0] == S1_LR_CASE_ID)
S1_LR_TARGET_REPLICA_RECORDS = tuple(
    row for row in S1_JX_REPLICA_RECORDS if row[0] in S1_LR_TARGET_REPLICA_IDS
)
S1_LR_SEQUENCE_RECORDS = tuple(
    row for row in S1_JX_SEQUENCE_RECORDS if row[0] in S1_LR_SEQUENCE_KEYS
)
S1_LR_FRESH_STATE_RECORD = next(
    row for row in S1_JZ_FRESH_STATE_RECORDS
    if row[0] == "B3" and row[1] == "THREE_NODE_OPEN_LINE"
)
S1_LR_FRESH_FIELD_DIGEST = (
    "335a80757cf6abbe3365f09352de47b758e4da2c6e18b2d577c48fac63cb0b05"
)
S1_LR_FRESH_PRIVATE_STATE_DIGEST = (
    "811bed92599dea6277bb629442efa8ea9967ba5187ed284f57acc77abd69d4b0"
)
S1_LR_EMBEDDED_M_STATE_DIGEST = (
    "718660a305ae5022e690196be1260402c7431fe17e0e05c80914b9782f0c5088"
)
S1_LR_FRESH_START_AND_CARRY_RULES = (
    "r2-r4-and-r8-each-use-three-independent-corrected-B3-fresh-states-one-per-sequence",
    "P_IK_A_B_A-and-P_IK_A_GAP_A-each-start-once-from-bit-identical-fresh-field-and-complete-B3-M-state",
    "complete-field-M-private-state-carry-only-across-the-four-ordered-intervals-within-one-sequence",
    "no-field-M-state-output-or-provenance-carries-between-sequences-or-refinements",
)
S1_LR_EXECUTION_BUDGET = (
    ("target_replica_count", 3),
    ("sequences_per_replica", 2),
    ("interval_calls_per_sequence", 4),
    ("interval_calls_per_replica", 8),
    ("maximum_new_interval_calls", 24),
    ("retry_or_repeat_calls", 0),
)
S1_LR_OUTPUT_ACCEPTANCE_RULES = (
    "each-replica-publishes-one-atomic-mcm.s1jz.complete-replica-output.v2-or-one-error",
    "each-output-has-two-terminal-checkpoints-six-signed-components-and-eight-adapter-diagnostics",
    "every-checkpoint-replica_id-bit-equals-its-parent-output-replica_id",
    "the-two-sequence-start-field-and-complete-B3-M-state-digests-must-be-bit-identical-within-each-refinement",
    "B3-P_IK-comparison-digests-must-be-bit-identical-across-r2-r4-r8",
    "complete-output-digests-remain-identity-bearing-and-must-be-distinct",
    "all-three-replicas-must-pass-before-C11-may-be-composed-in-a-later-stage",
)
S1_LR_SELECTION_RATIONALE = (
    "C11-is-the-only-registered-follow-up-to-static-C10-after-complete-cases-and-gates",
    "B3-receives-the-model-neutral-A-B-A-versus-A-Gap-A-history-and-checkpoint-plan",
    "selection-does-not-predict-baseline-closure-ranking-or-candidate-outcome",
)
S1_LR_FORBIDDEN_SCOPE = (
    "no-runner-initializer-adapter-or-output-implementation",
    "no-replica-sequence-interval-retry-or-repeat-execution",
    "no-C11-output-or-24-case-matrix-publication",
    "no-other-role-profile-selection",
    "no-baseline-candidate-runtime-or-research-judgment",
)
S1_LR_DECISION = (
    "B3_PIK_C11_SELECTED_THREE_REFINEMENT_TWO_SEQUENCE_DUAL_DIGEST_TWENTY_FOUR_CALL_CONTRACT_BOUND_NO_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1LRB3PIKCaseSelectionContract:
    contract_id: str
    source_s1lp_digest: str
    source_s1lp_decision: str
    target_case_record: tuple[object, ...]
    target_replica_ids: tuple[str, ...]
    target_replica_records: tuple[tuple[object, ...], ...]
    sequence_records: tuple[tuple[object, ...], ...]
    corrected_fresh_state_record: tuple[object, ...]
    fresh_field_digest: str
    fresh_private_state_digest: str
    embedded_m_state_digest: str
    complete_provenance_digest_role: tuple[tuple[str, object], ...]
    comparison_digest_role: tuple[tuple[str, object], ...]
    corrected_output_schema: tuple[tuple[str, object], ...]
    fresh_start_and_carry_rules: tuple[str, ...]
    execution_budget: tuple[tuple[str, int], ...]
    output_acceptance_rules: tuple[str, ...]
    selection_rationale: tuple[str, ...]
    forbidden_scope: tuple[str, ...]
    target_replica_count: int
    sequences_per_target_replica: int
    intervals_per_sequence: int
    intervals_per_target_replica: int
    checkpoints_per_target_replica: int
    signed_components_per_target_replica: int
    diagnostics_per_target_replica: int
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
        payload = {field.name: getattr(self, field.name) for field in fields(self) if field.name != "contract_digest"}
        if (
            self.contract_id != S1_LR_CONTRACT_ID
            or self.source_s1lp_digest != S1_LR_SOURCE_S1LP_DIGEST
            or self.source_s1lp_decision != S1_LR_SOURCE_S1LP_DECISION
            or self.target_case_record != S1_LR_TARGET_CASE_RECORD
            or self.target_replica_ids != S1_LR_TARGET_REPLICA_IDS
            or self.target_replica_records != S1_LR_TARGET_REPLICA_RECORDS
            or self.sequence_records != S1_LR_SEQUENCE_RECORDS
            or self.corrected_fresh_state_record != S1_LR_FRESH_STATE_RECORD
            or self.fresh_field_digest != S1_LR_FRESH_FIELD_DIGEST
            or self.fresh_private_state_digest != S1_LR_FRESH_PRIVATE_STATE_DIGEST
            or self.embedded_m_state_digest != S1_LR_EMBEDDED_M_STATE_DIGEST
            or self.complete_provenance_digest_role != S1_KE_COMPLETE_PROVENANCE_DIGEST_ROLE
            or self.comparison_digest_role != S1_KE_COMPARISON_DIGEST_ROLE
            or self.corrected_output_schema != S1_KE_CORRECTED_OUTPUT_SCHEMA
            or self.fresh_start_and_carry_rules != S1_LR_FRESH_START_AND_CARRY_RULES
            or self.execution_budget != S1_LR_EXECUTION_BUDGET
            or self.output_acceptance_rules != S1_LR_OUTPUT_ACCEPTANCE_RULES
            or self.selection_rationale != S1_LR_SELECTION_RATIONALE
            or self.forbidden_scope != S1_LR_FORBIDDEN_SCOPE
            or (self.target_replica_count, self.sequences_per_target_replica, self.intervals_per_sequence, self.intervals_per_target_replica) != (3, 2, 4, 8)
            or (self.checkpoints_per_target_replica, self.signed_components_per_target_replica, self.diagnostics_per_target_replica, self.maximum_new_interval_calls) != (2, 6, 8, 24)
            or self.case_selected is not True
            or self.runner_extension_implemented is not False
            or (self.target_replicas_executed, self.interval_calls_executed) != (0, 0)
            or self.case_output_composed is not False
            or self.matrix_24_case_output_published is not False
            or self.baseline_judgment_present is not False
            or self.runtime_integration_present is not False
            or self.exact_implementation_execution_authorized_next_stage is not True
            or self.decision != S1_LR_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1LRB3PIKCaseSelectionContractError(
                "S1-LR weakened the static B3/P_IK case selection"
            )


def build_dts1_s1lr_b3_pik_case_selection_contract() -> DTS1S1LRB3PIKCaseSelectionContract:
    """Select and bind C11 without implementing or executing its replicas."""

    source = build_dts1_s1lp_b3_pih_case_output_contract()
    if (
        source.contract_digest != S1_LR_SOURCE_S1LP_DIGEST
        or source.decision != S1_LR_SOURCE_S1LP_DECISION
        or source.case_output_digest is None
        or source.new_replicas_executed != 0
        or source.new_interval_calls_executed != 0
        or source.replica_count != len(S1_LR_TARGET_REPLICA_IDS)
        or len(S1_LR_TARGET_REPLICA_RECORDS) != 3
        or tuple(row[0] for row in S1_LR_TARGET_REPLICA_RECORDS) != S1_LR_TARGET_REPLICA_IDS
        or tuple(row[0] for row in S1_LR_SEQUENCE_RECORDS) != S1_LR_SEQUENCE_KEYS
        or tuple(row[3] for row in S1_LR_SEQUENCE_RECORDS) != (4, 4)
        or tuple(row[1] for row in S1_LR_SEQUENCE_RECORDS) != ("P_IK_INTERFERENCE", "P_IK_INTERFERENCE")
        or S1_LR_FRESH_STATE_RECORD[6] != S1_LR_FRESH_FIELD_DIGEST
        or S1_LR_FRESH_STATE_RECORD[8] != S1_LR_FRESH_PRIVATE_STATE_DIGEST
        or dict(S1_LR_FRESH_STATE_RECORD[7])["embedded_M_state_digest"] != S1_LR_EMBEDDED_M_STATE_DIGEST
        or source.source_s1jx_case_record[0] != S1_LP_CASE_ID
    ):
        raise DTS1S1LRB3PIKCaseSelectionContractError(
            "registered C11 evidence or corrected B3 fresh state differs"
        )
    values = {
        "contract_id": S1_LR_CONTRACT_ID,
        "source_s1lp_digest": source.contract_digest,
        "source_s1lp_decision": source.decision,
        "target_case_record": S1_LR_TARGET_CASE_RECORD,
        "target_replica_ids": S1_LR_TARGET_REPLICA_IDS,
        "target_replica_records": S1_LR_TARGET_REPLICA_RECORDS,
        "sequence_records": S1_LR_SEQUENCE_RECORDS,
        "corrected_fresh_state_record": S1_LR_FRESH_STATE_RECORD,
        "fresh_field_digest": S1_LR_FRESH_FIELD_DIGEST,
        "fresh_private_state_digest": S1_LR_FRESH_PRIVATE_STATE_DIGEST,
        "embedded_m_state_digest": S1_LR_EMBEDDED_M_STATE_DIGEST,
        "complete_provenance_digest_role": S1_KE_COMPLETE_PROVENANCE_DIGEST_ROLE,
        "comparison_digest_role": S1_KE_COMPARISON_DIGEST_ROLE,
        "corrected_output_schema": S1_KE_CORRECTED_OUTPUT_SCHEMA,
        "fresh_start_and_carry_rules": S1_LR_FRESH_START_AND_CARRY_RULES,
        "execution_budget": S1_LR_EXECUTION_BUDGET,
        "output_acceptance_rules": S1_LR_OUTPUT_ACCEPTANCE_RULES,
        "selection_rationale": S1_LR_SELECTION_RATIONALE,
        "forbidden_scope": S1_LR_FORBIDDEN_SCOPE,
        "target_replica_count": 3,
        "sequences_per_target_replica": 2,
        "intervals_per_sequence": 4,
        "intervals_per_target_replica": 8,
        "checkpoints_per_target_replica": 2,
        "signed_components_per_target_replica": 6,
        "diagnostics_per_target_replica": 8,
        "maximum_new_interval_calls": 24,
        "case_selected": True,
        "runner_extension_implemented": False,
        "target_replicas_executed": 0,
        "interval_calls_executed": 0,
        "case_output_composed": False,
        "matrix_24_case_output_published": False,
        "baseline_judgment_present": False,
        "runtime_integration_present": False,
        "exact_implementation_execution_authorized_next_stage": True,
        "decision": S1_LR_DECISION,
    }
    return DTS1S1LRB3PIKCaseSelectionContract(
        **values, contract_digest=_digest(values)
    )
