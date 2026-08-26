"""Static S1-KW selection contract for the finite B1/P_IK case."""

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
from .dynamic_substrate_s1kv_b2_pih_case_output_contract import (
    build_dts1_s1kv_b2_pih_case_output_contract,
)


class DTS1S1KWB1PIKCaseSelectionContractError(ValueError):
    """Raised when the finite S1-KW case selection is weakened."""


S1_KW_CONTRACT_ID = "dynamic-substrate.b1-pik-case-selection.s1kw.v1"
S1_KW_SOURCE_S1KV_DIGEST = "495139baff29222708e261d0be4c949cf403b6dd6af267670da8774d84cfaf41"
S1_KW_CASE_ID = "C03"
S1_KW_SEQUENCE_KEYS = ("P_IK_A_B_A", "P_IK_A_GAP_A")
S1_KW_TARGET_REPLICA_IDS = (
    "B1:P_IK_INTERFERENCE:r2",
    "B1:P_IK_INTERFERENCE:r4",
    "B1:P_IK_INTERFERENCE:r8",
)
S1_KW_TARGET_CASE_RECORD = next(row for row in S1_JX_CASE_RECORDS if row[0] == S1_KW_CASE_ID)
S1_KW_TARGET_REPLICA_RECORDS = tuple(row for row in S1_JX_REPLICA_RECORDS if row[0] in S1_KW_TARGET_REPLICA_IDS)
S1_KW_SEQUENCE_RECORDS = tuple(row for row in S1_JX_SEQUENCE_RECORDS if row[0] in S1_KW_SEQUENCE_KEYS)
S1_KW_FRESH_STATE_RECORD = next(
    row for row in S1_JZ_FRESH_STATE_RECORDS
    if row[0] == "B1" and row[1] == "THREE_NODE_OPEN_LINE"
)
S1_KW_FRESH_FIELD_DIGEST = "55278f3e39a856f4846a45f65a0e4289b486b1a3bb5c32deb5eede0828e3c2d8"
S1_KW_FRESH_PRIVATE_STATE_DIGEST = "7f9afbe3dccf65514ba8dd5b61d6c24b5113c068655a05861fe1415ade374ee1"
S1_KW_FRESH_START_AND_CARRY_RULES = (
    "r2-r4-and-r8-each-use-two-independent-corrected-B1-fresh-states-one-per-sequence",
    "P_IK_A_B_A-and-P_IK_A_GAP_A-each-start-once-from-bit-identical-fresh-field-and-fixed-adapter-state",
    "complete-field-and-fixed-adapter-private-state-carry-only-across-the-four-ordered-intervals-within-one-sequence",
    "no-field-private-state-output-or-provenance-carries-between-sequences-or-refinements",
)
S1_KW_EXECUTION_BUDGET = (
    ("target_replica_count", 3),
    ("sequences_per_replica", 2),
    ("interval_calls_per_sequence", 4),
    ("interval_calls_per_replica", 8),
    ("maximum_new_interval_calls", 24),
    ("retry_or_repeat_calls", 0),
)
S1_KW_OUTPUT_ACCEPTANCE_RULES = (
    "each-replica-publishes-one-atomic-mcm.s1jz.complete-replica-output.v2-or-one-error",
    "each-output-has-two-terminal-checkpoints-six-signed-components-and-eight-adapter-diagnostics",
    "every-checkpoint-replica_id-bit-equals-its-parent-output-replica_id",
    "the-two-sequence-start-field-and-private-state-digests-must-be-bit-identical-within-each-refinement",
    "B1-refinement-comparison-digests-must-be-bit-identical-across-r2-r4-r8",
    "complete-output-digests-remain-identity-bearing-and-must-be-distinct",
    "all-three-replicas-must-pass-before-C03-may-be-composed-in-a-later-stage",
)
S1_KW_SELECTION_RATIONALE = (
    "C03-is-the-next-canonical-registered-case-after-technically-complete-C01-C02-C05-and-C06",
    "C03-binds-the-model-neutral-A-B-A-versus-A-Gap-A-history-to-the-fixed-B1-adapter",
    "selection-does-not-predict-sign-threshold-interference-baseline-closure-or-candidate-outcome",
)
S1_KW_FORBIDDEN_SCOPE = (
    "no-runner-initializer-adapter-or-output-implementation",
    "no-replica-sequence-interval-retry-or-repeat-execution",
    "no-C03-output-or-24-case-matrix-publication",
    "no-B2-P_IK-or-other-role-profile-selection",
    "no-baseline-candidate-runtime-or-research-judgment",
)
S1_KW_DECISION = "B1_PIK_C03_SELECTED_THREE_REFINEMENT_TWO_SEQUENCE_DUAL_DIGEST_TWENTY_FOUR_CALL_CONTRACT_BOUND_NO_EXECUTION"


def _digest(payload: object) -> str:
    return hashlib.sha256(json.dumps(payload, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1KWB1PIKCaseSelectionContract:
    contract_id: str
    source_s1kv_digest: str
    target_case_record: tuple[object, ...]
    target_replica_ids: tuple[str, ...]
    target_replica_records: tuple[tuple[object, ...], ...]
    sequence_records: tuple[tuple[object, ...], ...]
    corrected_fresh_state_record: tuple[object, ...]
    fresh_field_digest: str
    fresh_private_state_digest: str
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
            self.contract_id != S1_KW_CONTRACT_ID
            or self.source_s1kv_digest != S1_KW_SOURCE_S1KV_DIGEST
            or self.target_case_record != S1_KW_TARGET_CASE_RECORD
            or self.target_replica_ids != S1_KW_TARGET_REPLICA_IDS
            or self.target_replica_records != S1_KW_TARGET_REPLICA_RECORDS
            or self.sequence_records != S1_KW_SEQUENCE_RECORDS
            or self.corrected_fresh_state_record != S1_KW_FRESH_STATE_RECORD
            or self.fresh_field_digest != S1_KW_FRESH_FIELD_DIGEST
            or self.fresh_private_state_digest != S1_KW_FRESH_PRIVATE_STATE_DIGEST
            or self.complete_provenance_digest_role != S1_KE_COMPLETE_PROVENANCE_DIGEST_ROLE
            or self.comparison_digest_role != S1_KE_COMPARISON_DIGEST_ROLE
            or self.corrected_output_schema != S1_KE_CORRECTED_OUTPUT_SCHEMA
            or self.fresh_start_and_carry_rules != S1_KW_FRESH_START_AND_CARRY_RULES
            or self.execution_budget != S1_KW_EXECUTION_BUDGET
            or self.output_acceptance_rules != S1_KW_OUTPUT_ACCEPTANCE_RULES
            or self.selection_rationale != S1_KW_SELECTION_RATIONALE
            or self.forbidden_scope != S1_KW_FORBIDDEN_SCOPE
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
            or self.decision != S1_KW_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1KWB1PIKCaseSelectionContractError("S1-KW weakened the finite B1/P_IK case selection")


def build_dts1_s1kw_b1_pik_case_selection_contract() -> DTS1S1KWB1PIKCaseSelectionContract:
    """Select and bind C03 without implementing or executing its replicas."""

    source = build_dts1_s1kv_b2_pih_case_output_contract()
    if (
        source.contract_digest != S1_KW_SOURCE_S1KV_DIGEST
        or len(S1_KW_TARGET_REPLICA_RECORDS) != 3
        or tuple(row[0] for row in S1_KW_TARGET_REPLICA_RECORDS) != S1_KW_TARGET_REPLICA_IDS
        or tuple(row[0] for row in S1_KW_SEQUENCE_RECORDS) != S1_KW_SEQUENCE_KEYS
        or tuple(row[3] for row in S1_KW_SEQUENCE_RECORDS) != (4, 4)
        or tuple(row[5] for row in S1_KW_SEQUENCE_RECORDS) != ((4,), (4,))
        or S1_KW_FRESH_STATE_RECORD[6] != S1_KW_FRESH_FIELD_DIGEST
        or S1_KW_FRESH_STATE_RECORD[8] != S1_KW_FRESH_PRIVATE_STATE_DIGEST
    ):
        raise DTS1S1KWB1PIKCaseSelectionContractError("registered C03 evidence or corrected B1 fresh state differs")
    values = {
        "contract_id": S1_KW_CONTRACT_ID,
        "source_s1kv_digest": source.contract_digest,
        "target_case_record": S1_KW_TARGET_CASE_RECORD,
        "target_replica_ids": S1_KW_TARGET_REPLICA_IDS,
        "target_replica_records": S1_KW_TARGET_REPLICA_RECORDS,
        "sequence_records": S1_KW_SEQUENCE_RECORDS,
        "corrected_fresh_state_record": S1_KW_FRESH_STATE_RECORD,
        "fresh_field_digest": S1_KW_FRESH_FIELD_DIGEST,
        "fresh_private_state_digest": S1_KW_FRESH_PRIVATE_STATE_DIGEST,
        "complete_provenance_digest_role": S1_KE_COMPLETE_PROVENANCE_DIGEST_ROLE,
        "comparison_digest_role": S1_KE_COMPARISON_DIGEST_ROLE,
        "corrected_output_schema": S1_KE_CORRECTED_OUTPUT_SCHEMA,
        "fresh_start_and_carry_rules": S1_KW_FRESH_START_AND_CARRY_RULES,
        "execution_budget": S1_KW_EXECUTION_BUDGET,
        "output_acceptance_rules": S1_KW_OUTPUT_ACCEPTANCE_RULES,
        "selection_rationale": S1_KW_SELECTION_RATIONALE,
        "forbidden_scope": S1_KW_FORBIDDEN_SCOPE,
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
        "decision": S1_KW_DECISION,
    }
    return DTS1S1KWB1PIKCaseSelectionContract(**values, contract_digest=_digest(values))
