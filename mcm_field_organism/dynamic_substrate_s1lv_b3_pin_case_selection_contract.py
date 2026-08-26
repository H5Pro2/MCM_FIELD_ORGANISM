"""Static S1-LV selection contract for the finite B3/P_IN case."""

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
    S1_JX_SEQUENCE_RECORDS,
)
from .dynamic_substrate_s1ke_dual_refinement_digest_contract import (
    S1_KE_COMPARISON_DIGEST_ROLE,
    S1_KE_COMPLETE_PROVENANCE_DIGEST_ROLE,
    S1_KE_CORRECTED_OUTPUT_SCHEMA,
)
from .dynamic_substrate_s1lu_matrix_completeness_gate import (
    build_dts1_s1lu_matrix_completeness_gate,
)


class DTS1S1LVB3PINCaseSelectionContractError(ValueError):
    """Raised when the static S1-LV case selection is weakened."""


S1_LV_CONTRACT_ID = "dynamic-substrate.b3-pin-case-selection.s1lv.v1"
S1_LV_SOURCE_S1LU_DIGEST = (
    "d8e4db8cbff1d378d55d63634443d9472578f84cee838c1c101cfdd5712a9242"
)
S1_LV_SOURCE_S1LU_DECISION = (
    "ELEVEN_OF_TWENTY_FOUR_CASES_COMPLETE_MATRIX_COMPOSITION_BLOCKED_C12_SELECTION_AUTHORIZED"
)
S1_LV_CASE_ID = "C12"
S1_LV_SEQUENCE_KEYS = ("P_IN_RECOVERY_ON", "P_IN_RECOVERY_OFF")
S1_LV_TARGET_REPLICA_IDS = (
    "B3:P_IN_RELEASE_REUSE:r2",
    "B3:P_IN_RELEASE_REUSE:r4",
    "B3:P_IN_RELEASE_REUSE:r8",
)
S1_LV_TARGET_CASE_RECORD = next(
    row for row in S1_JX_CASE_RECORDS if row[0] == S1_LV_CASE_ID
)
S1_LV_TARGET_REPLICA_RECORDS = tuple(
    row for row in S1_JX_REPLICA_RECORDS if row[0] in S1_LV_TARGET_REPLICA_IDS
)
S1_LV_SEQUENCE_RECORDS = tuple(
    row for row in S1_JX_SEQUENCE_RECORDS if row[0] in S1_LV_SEQUENCE_KEYS
)
S1_LV_FRESH_STATE_RECORD = next(
    row for row in S1_JZ_FRESH_STATE_RECORDS
    if row[0] == "B3" and row[1] == "THREE_NODE_OPEN_LINE"
)
S1_LV_FRESH_FIELD_DIGEST = (
    "335a80757cf6abbe3365f09352de47b758e4da2c6e18b2d577c48fac63cb0b05"
)
S1_LV_FRESH_PRIVATE_STATE_DIGEST = (
    "811bed92599dea6277bb629442efa8ea9967ba5187ed284f57acc77abd69d4b0"
)
S1_LV_EMBEDDED_M_STATE_DIGEST = (
    "718660a305ae5022e690196be1260402c7431fe17e0e05c80914b9782f0c5088"
)
S1_LV_FRESH_START_AND_CARRY_RULES = (
    "r2-r4-and-r8-each-use-two-independent-corrected-B3-fresh-states-one-per-sequence",
    "P_IN_RECOVERY_ON-and-P_IN_RECOVERY_OFF-each-start-once-from-bit-identical-fresh-field-and-complete-B3-M-state",
    "complete-field-M-private-state-carry-only-across-the-four-ordered-intervals-within-one-sequence",
    "no-field-M-state-output-or-provenance-carries-between-sequences-or-refinements",
)
S1_LV_EXECUTION_BUDGET = (
    ("target_replica_count", 3),
    ("sequences_per_replica", 2),
    ("interval_calls_per_sequence", 4),
    ("interval_calls_per_replica", 8),
    ("maximum_new_interval_calls", 24),
    ("retry_or_repeat_calls", 0),
)
S1_LV_OUTPUT_ACCEPTANCE_RULES = (
    "each-replica-publishes-one-atomic-mcm.s1jz.complete-replica-output.v2-or-one-error",
    "each-output-has-two-terminal-checkpoints-six-signed-components-and-eight-adapter-diagnostics",
    "every-checkpoint-replica_id-bit-equals-its-parent-output-replica_id",
    "the-two-sequence-start-field-and-complete-B3-M-state-digests-must-be-bit-identical-within-each-refinement",
    "B3-P_IN-comparison-digests-must-not-be-forced-bit-identical-across-r2-r4-r8",
    "complete-output-digests-remain-identity-bearing-and-must-be-distinct",
    "all-three-replicas-must-pass-before-C12-may-be-composed-in-a-later-stage",
)
S1_LV_SELECTION_RATIONALE = (
    "C12-is-the-only-registered-follow-up-after-C11-completion-and-S1-LU-gate",
    "B3-receives-the-model-neutral-recovery-on-versus-recovery-off-history-and-checkpoint-plan",
    "selection-does-not-predict-release-reuse-baseline-closure-ranking-or-candidate-outcome",
)
S1_LV_FORBIDDEN_SCOPE = (
    "no-runner-initializer-adapter-or-output-implementation",
    "no-replica-sequence-interval-retry-or-repeat-execution",
    "no-C12-output-or-24-case-matrix-publication",
    "no-other-role-profile-selection",
    "no-release-reuse-baseline-candidate-runtime-or-research-judgment",
)
S1_LV_DECISION = (
    "B3_PIN_C12_SELECTED_THREE_REFINEMENT_TWO_SEQUENCE_DUAL_DIGEST_TWENTY_FOUR_CALL_CONTRACT_BOUND_NO_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1LVB3PINCaseSelectionContract:
    contract_id: str
    source_s1lu_digest: str
    source_s1lu_decision: str
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
    release_reuse_judgment_present: bool
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
            self.contract_id != S1_LV_CONTRACT_ID
            or self.source_s1lu_digest != S1_LV_SOURCE_S1LU_DIGEST
            or self.source_s1lu_decision != S1_LV_SOURCE_S1LU_DECISION
            or self.target_case_record != S1_LV_TARGET_CASE_RECORD
            or self.target_replica_ids != S1_LV_TARGET_REPLICA_IDS
            or self.target_replica_records != S1_LV_TARGET_REPLICA_RECORDS
            or self.sequence_records != S1_LV_SEQUENCE_RECORDS
            or self.corrected_fresh_state_record != S1_LV_FRESH_STATE_RECORD
            or self.fresh_field_digest != S1_LV_FRESH_FIELD_DIGEST
            or self.fresh_private_state_digest != S1_LV_FRESH_PRIVATE_STATE_DIGEST
            or self.embedded_m_state_digest != S1_LV_EMBEDDED_M_STATE_DIGEST
            or self.complete_provenance_digest_role != S1_KE_COMPLETE_PROVENANCE_DIGEST_ROLE
            or self.comparison_digest_role != S1_KE_COMPARISON_DIGEST_ROLE
            or self.corrected_output_schema != S1_KE_CORRECTED_OUTPUT_SCHEMA
            or self.fresh_start_and_carry_rules != S1_LV_FRESH_START_AND_CARRY_RULES
            or self.execution_budget != S1_LV_EXECUTION_BUDGET
            or self.output_acceptance_rules != S1_LV_OUTPUT_ACCEPTANCE_RULES
            or self.selection_rationale != S1_LV_SELECTION_RATIONALE
            or self.forbidden_scope != S1_LV_FORBIDDEN_SCOPE
            or (self.target_replica_count, self.sequences_per_target_replica, self.intervals_per_sequence, self.intervals_per_target_replica) != (3, 2, 4, 8)
            or (self.checkpoints_per_target_replica, self.signed_components_per_target_replica, self.diagnostics_per_target_replica, self.maximum_new_interval_calls) != (2, 6, 8, 24)
            or self.case_selected is not True
            or self.runner_extension_implemented is not False
            or (self.target_replicas_executed, self.interval_calls_executed) != (0, 0)
            or self.case_output_composed is not False
            or self.matrix_24_case_output_published is not False
            or self.release_reuse_judgment_present is not False
            or self.baseline_judgment_present is not False
            or self.runtime_integration_present is not False
            or self.exact_implementation_execution_authorized_next_stage is not True
            or self.decision != S1_LV_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1LVB3PINCaseSelectionContractError(
                "S1-LV weakened the static B3/P_IN case selection"
            )


def build_dts1_s1lv_b3_pin_case_selection_contract(
) -> DTS1S1LVB3PINCaseSelectionContract:
    """Select and bind C12 without implementing or executing its replicas."""

    source = build_dts1_s1lu_matrix_completeness_gate()
    if (
        source.contract_digest != S1_LV_SOURCE_S1LU_DIGEST
        or source.decision != S1_LV_SOURCE_S1LU_DECISION
        or source.c12_selection_authorized_next_stage is not True
        or source.next_case_record != S1_LV_TARGET_CASE_RECORD
        or len(S1_LV_TARGET_REPLICA_RECORDS) != 3
        or tuple(row[0] for row in S1_LV_TARGET_REPLICA_RECORDS)
        != S1_LV_TARGET_REPLICA_IDS
        or tuple(row[0] for row in S1_LV_SEQUENCE_RECORDS) != S1_LV_SEQUENCE_KEYS
        or tuple(row[3] for row in S1_LV_SEQUENCE_RECORDS) != (4, 4)
        or tuple(row[5] for row in S1_LV_SEQUENCE_RECORDS) != ((4,), (4,))
        or S1_LV_FRESH_STATE_RECORD[6] != S1_LV_FRESH_FIELD_DIGEST
        or S1_LV_FRESH_STATE_RECORD[8] != S1_LV_FRESH_PRIVATE_STATE_DIGEST
        or dict(S1_LV_FRESH_STATE_RECORD[7])["embedded_M_state_digest"] != S1_LV_EMBEDDED_M_STATE_DIGEST
    ):
        raise DTS1S1LVB3PINCaseSelectionContractError(
            "registered C12 evidence or corrected B3 fresh state differs"
        )
    values = {
        "contract_id": S1_LV_CONTRACT_ID,
        "source_s1lu_digest": source.contract_digest,
        "source_s1lu_decision": source.decision,
        "target_case_record": S1_LV_TARGET_CASE_RECORD,
        "target_replica_ids": S1_LV_TARGET_REPLICA_IDS,
        "target_replica_records": S1_LV_TARGET_REPLICA_RECORDS,
        "sequence_records": S1_LV_SEQUENCE_RECORDS,
        "corrected_fresh_state_record": S1_LV_FRESH_STATE_RECORD,
        "fresh_field_digest": S1_LV_FRESH_FIELD_DIGEST,
        "fresh_private_state_digest": S1_LV_FRESH_PRIVATE_STATE_DIGEST,
        "embedded_m_state_digest": S1_LV_EMBEDDED_M_STATE_DIGEST,
        "complete_provenance_digest_role": S1_KE_COMPLETE_PROVENANCE_DIGEST_ROLE,
        "comparison_digest_role": S1_KE_COMPARISON_DIGEST_ROLE,
        "corrected_output_schema": S1_KE_CORRECTED_OUTPUT_SCHEMA,
        "fresh_start_and_carry_rules": S1_LV_FRESH_START_AND_CARRY_RULES,
        "execution_budget": S1_LV_EXECUTION_BUDGET,
        "output_acceptance_rules": S1_LV_OUTPUT_ACCEPTANCE_RULES,
        "selection_rationale": S1_LV_SELECTION_RATIONALE,
        "forbidden_scope": S1_LV_FORBIDDEN_SCOPE,
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
        "release_reuse_judgment_present": False,
        "baseline_judgment_present": False,
        "runtime_integration_present": False,
        "exact_implementation_execution_authorized_next_stage": True,
        "decision": S1_LV_DECISION,
    }
    return DTS1S1LVB3PINCaseSelectionContract(
        **values, contract_digest=_digest(values)
    )
