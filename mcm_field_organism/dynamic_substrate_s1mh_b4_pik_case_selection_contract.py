"""Static S1-MH selection contract for the finite B4/P_IK case."""

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
from .dynamic_substrate_s1mg_matrix_completeness_gate import (
    build_dts1_s1mg_matrix_completeness_gate,
)


class DTS1S1MHB4PIKCaseSelectionContractError(ValueError):
    """Raised when the finite S1-MH C15 selection is weakened."""


S1_MH_CONTRACT_ID = "dynamic-substrate.b4-pik-case-selection.s1mh.v1"
S1_MH_SOURCE_S1MG_DIGEST = (
    "6825d0ee397eb8a431f629dac6d426b3c8a758fac7c14b90e318caef72d99952"
)
S1_MH_CASE_ID = "C15"
S1_MH_SEQUENCE_KEYS = ("P_IK_A_B_A", "P_IK_A_GAP_A")
S1_MH_TARGET_REPLICA_IDS = (
    "B4:P_IK_INTERFERENCE:r2",
    "B4:P_IK_INTERFERENCE:r4",
    "B4:P_IK_INTERFERENCE:r8",
)
S1_MH_TARGET_CASE_RECORD = next(
    row for row in S1_JX_CASE_RECORDS if row[0] == S1_MH_CASE_ID
)
S1_MH_TARGET_REPLICA_RECORDS = tuple(
    row for row in S1_JX_REPLICA_RECORDS if row[0] in S1_MH_TARGET_REPLICA_IDS
)
S1_MH_SEQUENCE_RECORDS = tuple(
    row for row in S1_JX_SEQUENCE_RECORDS if row[0] in S1_MH_SEQUENCE_KEYS
)
S1_MH_FRESH_STATE_RECORD = next(
    row
    for row in S1_JZ_FRESH_STATE_RECORDS
    if row[0] == "B4" and row[1] == "THREE_NODE_OPEN_LINE"
)
S1_MH_FRESH_FIELD_DIGEST = (
    "1796764e32f24f04cede7cef496a5e15390930306f5f8f6cca34e930d4e29c3b"
)
S1_MH_FRESH_PRIVATE_STATE_DIGEST = (
    "6b83e11901795f68307888acc95c85b6160bd88726824edcbe79a2314ad795c3"
)
S1_MH_EMBEDDED_M_STATE_DIGEST = (
    "60fa063bc2d1c90a38b9a81bccecce816c3984b620f97eb7fff05bdbf1242d14"
)
S1_MH_B4_CONFIGURATION_DIGEST = (
    "fa36b68073f4bef8405496b1dd42cd2fd85af6d5bfedd99146efb25443ca6f06"
)
S1_MH_FRESH_START_RULES = (
    "r2-r4-and-r8-each-use-two-independent-corrected-B4-fresh-states-one-per-sequence",
    "P_IK_A_B_A-and-P_IK_A_GAP_A-each-start-once-from-bit-identical-fresh-field-and-complete-B4-M-state",
    "complete-field-M-state-and-linear-coupled-configuration-carry-only-across-the-four-ordered-intervals-within-one-sequence",
    "no-field-M-state-output-or-provenance-carries-between-sequences-or-refinements",
)
S1_MH_EXECUTION_BUDGET = (
    ("target_replica_count", 3),
    ("sequences_per_replica", 2),
    ("interval_calls_per_sequence", 4),
    ("interval_calls_per_replica", 8),
    ("maximum_new_interval_calls", 24),
    ("retry_or_repeat_calls", 0),
)
S1_MH_OUTPUT_ACCEPTANCE_RULES = (
    "each-replica-publishes-one-atomic-mcm.s1jz.complete-replica-output.v2-or-one-error",
    "each-output-has-two-terminal-checkpoints-six-signed-components-and-eight-adapter-diagnostics",
    "every-checkpoint-replica_id-bit-equals-its-parent-output-replica_id",
    "the-two-sequence-start-field-and-complete-B4-M-state-digests-must-be-bit-identical-within-each-refinement",
    "B4-P_IK-comparison-content-may-differ-across-r2-r4-r8-and-must-not-be-forced-bit-identical",
    "complete-output-digests-remain-identity-bearing-and-must-be-distinct",
    "all-three-replicas-must-pass-before-C15-may-be-composed-in-a-later-stage",
)
S1_MH_SELECTION_RATIONALE = (
    "C15-is-the-first-missing-case-after-complete-C01-through-C14",
    "B4-receives-the-model-neutral-A-B-A-versus-A-Gap-A-history-and-checkpoint-plan",
    "B4-is-the-registered-F3-linear-coupled-counterbaseline-with-its-own-complete-M-state-and-configuration",
    "selection-does-not-predict-interference-baseline-closure-ranking-or-candidate-outcome",
)
S1_MH_FORBIDDEN_SCOPE = (
    "no-runner-initializer-adapter-or-output-implementation",
    "no-replica-sequence-interval-retry-or-repeat-execution",
    "no-C15-output-or-24-case-matrix-publication",
    "no-other-role-profile-selection",
    "no-baseline-candidate-runtime-memory-or-ai-judgment",
)
S1_MH_DECISION = (
    "B4_PIK_C15_SELECTED_THREE_REFINEMENT_TWO_SEQUENCE_DUAL_DIGEST_TWENTY_FOUR_CALL_CONTRACT_BOUND_NO_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1MHB4PIKCaseSelectionContract:
    contract_id: str
    source_s1mg_digest: str
    target_case_record: tuple[object, ...]
    target_replica_ids: tuple[str, ...]
    target_replica_records: tuple[tuple[object, ...], ...]
    sequence_records: tuple[tuple[object, ...], ...]
    corrected_fresh_state_record: tuple[object, ...]
    fresh_field_digest: str
    fresh_private_state_digest: str
    embedded_m_state_digest: str
    b4_configuration_digest: str
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
    candidate_comparison_present: bool
    memory_capability_claim_present: bool
    ai_system_claim_present: bool
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
            self.contract_id != S1_MH_CONTRACT_ID
            or self.source_s1mg_digest != S1_MH_SOURCE_S1MG_DIGEST
            or self.target_case_record != S1_MH_TARGET_CASE_RECORD
            or self.target_replica_ids != S1_MH_TARGET_REPLICA_IDS
            or self.target_replica_records != S1_MH_TARGET_REPLICA_RECORDS
            or self.sequence_records != S1_MH_SEQUENCE_RECORDS
            or self.corrected_fresh_state_record != S1_MH_FRESH_STATE_RECORD
            or self.fresh_field_digest != S1_MH_FRESH_FIELD_DIGEST
            or self.fresh_private_state_digest != S1_MH_FRESH_PRIVATE_STATE_DIGEST
            or self.embedded_m_state_digest != S1_MH_EMBEDDED_M_STATE_DIGEST
            or self.b4_configuration_digest != S1_MH_B4_CONFIGURATION_DIGEST
            or self.complete_provenance_digest_role != S1_KE_COMPLETE_PROVENANCE_DIGEST_ROLE
            or self.comparison_digest_role != S1_KE_COMPARISON_DIGEST_ROLE
            or self.corrected_output_schema != S1_KE_CORRECTED_OUTPUT_SCHEMA
            or self.fresh_start_and_carry_rules != S1_MH_FRESH_START_RULES
            or self.execution_budget != S1_MH_EXECUTION_BUDGET
            or self.output_acceptance_rules != S1_MH_OUTPUT_ACCEPTANCE_RULES
            or self.selection_rationale != S1_MH_SELECTION_RATIONALE
            or self.forbidden_scope != S1_MH_FORBIDDEN_SCOPE
            or (
                self.target_replica_count,
                self.sequences_per_target_replica,
                self.intervals_per_sequence,
                self.intervals_per_target_replica,
            ) != (3, 2, 4, 8)
            or (
                self.checkpoints_per_target_replica,
                self.signed_components_per_target_replica,
                self.diagnostics_per_target_replica,
                self.maximum_new_interval_calls,
            ) != (2, 6, 8, 24)
            or self.case_selected is not True
            or self.runner_extension_implemented is not False
            or (self.target_replicas_executed, self.interval_calls_executed) != (0, 0)
            or self.case_output_composed is not False
            or self.matrix_24_case_output_published is not False
            or self.baseline_judgment_present is not False
            or self.candidate_comparison_present is not False
            or self.memory_capability_claim_present is not False
            or self.ai_system_claim_present is not False
            or self.runtime_integration_present is not False
            or self.exact_implementation_execution_authorized_next_stage is not True
            or self.decision != S1_MH_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1MHB4PIKCaseSelectionContractError(
                "S1-MH weakened the finite B4/P_IK case selection"
            )


def build_dts1_s1mh_b4_pik_case_selection_contract(
) -> DTS1S1MHB4PIKCaseSelectionContract:
    """Select and bind C15 without implementing or executing its replicas."""

    source = build_dts1_s1mg_matrix_completeness_gate()
    field_payload = dict(S1_MH_FRESH_STATE_RECORD[5])
    substrate = dict(field_payload["substrate"])
    arm = dict(substrate["arm"])
    private = dict(S1_MH_FRESH_STATE_RECORD[7])
    if (
        source.contract_digest != S1_MH_SOURCE_S1MG_DIGEST
        or source.c15_selection_authorized_next_stage is not True
        or len(S1_MH_TARGET_REPLICA_RECORDS) != 3
        or tuple(row[0] for row in S1_MH_TARGET_REPLICA_RECORDS)
        != S1_MH_TARGET_REPLICA_IDS
        or tuple(row[0] for row in S1_MH_SEQUENCE_RECORDS) != S1_MH_SEQUENCE_KEYS
        or tuple(row[1] for row in S1_MH_SEQUENCE_RECORDS)
        != ("P_IK_INTERFERENCE", "P_IK_INTERFERENCE")
        or tuple(row[3] for row in S1_MH_SEQUENCE_RECORDS) != (4, 4)
        or tuple(row[5] for row in S1_MH_SEQUENCE_RECORDS)
        != ((4,), (4,))
        or S1_MH_FRESH_STATE_RECORD[6] != S1_MH_FRESH_FIELD_DIGEST
        or S1_MH_FRESH_STATE_RECORD[8] != S1_MH_FRESH_PRIVATE_STATE_DIGEST
        or private["embedded_M_state_digest"] != S1_MH_EMBEDDED_M_STATE_DIGEST
        or private["B4_configuration_digest"] != S1_MH_B4_CONFIGURATION_DIGEST
        or substrate["masses"]
        != (
            ("node-a", 0.3333333333333333),
            ("node-b", 0.3333333333333333),
            ("node-c", 0.3333333333333333),
        )
        or arm["arm_id"] != "mcm.s1jt.b4.linear-coupled"
        or arm["lambda_sm_per_second"] != 1.0
        or arm["kappa"] != 0.5
        or arm["eta"] != 1.0
    ):
        raise DTS1S1MHB4PIKCaseSelectionContractError(
            "registered C15 replicas or corrected B4 fresh state differ"
        )
    values = {
        "contract_id": S1_MH_CONTRACT_ID,
        "source_s1mg_digest": source.contract_digest,
        "target_case_record": S1_MH_TARGET_CASE_RECORD,
        "target_replica_ids": S1_MH_TARGET_REPLICA_IDS,
        "target_replica_records": S1_MH_TARGET_REPLICA_RECORDS,
        "sequence_records": S1_MH_SEQUENCE_RECORDS,
        "corrected_fresh_state_record": S1_MH_FRESH_STATE_RECORD,
        "fresh_field_digest": S1_MH_FRESH_FIELD_DIGEST,
        "fresh_private_state_digest": S1_MH_FRESH_PRIVATE_STATE_DIGEST,
        "embedded_m_state_digest": S1_MH_EMBEDDED_M_STATE_DIGEST,
        "b4_configuration_digest": S1_MH_B4_CONFIGURATION_DIGEST,
        "complete_provenance_digest_role": S1_KE_COMPLETE_PROVENANCE_DIGEST_ROLE,
        "comparison_digest_role": S1_KE_COMPARISON_DIGEST_ROLE,
        "corrected_output_schema": S1_KE_CORRECTED_OUTPUT_SCHEMA,
        "fresh_start_and_carry_rules": S1_MH_FRESH_START_RULES,
        "execution_budget": S1_MH_EXECUTION_BUDGET,
        "output_acceptance_rules": S1_MH_OUTPUT_ACCEPTANCE_RULES,
        "selection_rationale": S1_MH_SELECTION_RATIONALE,
        "forbidden_scope": S1_MH_FORBIDDEN_SCOPE,
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
        "candidate_comparison_present": False,
        "memory_capability_claim_present": False,
        "ai_system_claim_present": False,
        "runtime_integration_present": False,
        "exact_implementation_execution_authorized_next_stage": True,
        "decision": S1_MH_DECISION,
    }
    return DTS1S1MHB4PIKCaseSelectionContract(
        **values, contract_digest=_digest(values)
    )
