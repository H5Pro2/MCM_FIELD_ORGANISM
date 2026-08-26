"""Static S1-MD selection contract for the finite B4/P_IH case."""

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
from .dynamic_substrate_s1mc_matrix_completeness_gate import (
    build_dts1_s1mc_matrix_completeness_gate,
)


class DTS1S1MDB4PIHCaseSelectionContractError(ValueError):
    """Raised when the finite S1-MD C14 selection is weakened."""


S1_MD_CONTRACT_ID = "dynamic-substrate.b4-pih-case-selection.s1md.v1"
S1_MD_SOURCE_S1MC_DIGEST = (
    "41d1e2187d3c1c78ea6c774c06ceda6bc61e98304e82ed273fd79a32019b77c9"
)
S1_MD_CASE_ID = "C14"
S1_MD_SEQUENCE_KEY = "P_IH_A_A_A"
S1_MD_TARGET_REPLICA_IDS = (
    "B4:P_IH_ATTENUATION:r2",
    "B4:P_IH_ATTENUATION:r4",
    "B4:P_IH_ATTENUATION:r8",
)
S1_MD_TARGET_CASE_RECORD = next(
    row for row in S1_JX_CASE_RECORDS if row[0] == S1_MD_CASE_ID
)
S1_MD_TARGET_REPLICA_RECORDS = tuple(
    row for row in S1_JX_REPLICA_RECORDS if row[0] in S1_MD_TARGET_REPLICA_IDS
)
S1_MD_SEQUENCE_RECORD = next(
    row for row in S1_JX_SEQUENCE_RECORDS if row[0] == S1_MD_SEQUENCE_KEY
)
S1_MD_FRESH_STATE_RECORD = next(
    row
    for row in S1_JZ_FRESH_STATE_RECORDS
    if row[0] == "B4" and row[1] == "TWO_NODE_OPEN_LINE"
)
S1_MD_FRESH_FIELD_DIGEST = (
    "c937abffd0b17ebbdd4675f2577f9920b8792f83214e0a3bc6203c24eb2ea11b"
)
S1_MD_FRESH_PRIVATE_STATE_DIGEST = (
    "3919b9274f067ae67b1db96be68b075be21f7e799e2d714eea0f83c50df82466"
)
S1_MD_EMBEDDED_M_STATE_DIGEST = (
    "4de08462e5d7f747c84934edd93493bd8cf93b6627726ec82dc1c5b86767128c"
)
S1_MD_B4_CONFIGURATION_DIGEST = (
    "fa36b68073f4bef8405496b1dd42cd2fd85af6d5bfedd99146efb25443ca6f06"
)
S1_MD_FRESH_START_RULES = (
    "r2-r4-and-r8-each-use-one-independent-corrected-B4-fresh-state",
    "P_IH_A_A_A-starts-once-from-that-refinements-own-fresh-state",
    "complete-field-M-state-and-linear-coupled-configuration-carry-only-between-the-three-ordered-intervals-within-one-sequence",
    "no-field-M-state-output-or-provenance-carries-between-refinements",
)
S1_MD_EXECUTION_BUDGET = (
    ("target_replica_count", 3),
    ("sequences_per_replica", 1),
    ("interval_calls_per_sequence", 3),
    ("interval_calls_per_replica", 3),
    ("maximum_new_interval_calls", 9),
    ("retry_or_repeat_calls", 0),
)
S1_MD_OUTPUT_ACCEPTANCE_RULES = (
    "each-replica-publishes-one-atomic-mcm.s1jz.complete-replica-output.v2-or-one-error",
    "each-output-carries-one-complete-provenance-digest-and-one-identity-neutral-comparison-digest",
    "B4-comparison-content-may-differ-across-r2-r4-r8-and-must-not-be-forced-bit-identical",
    "all-three-replicas-must-pass-before-C14-may-be-composed-in-a-later-stage",
)
S1_MD_SELECTION_RATIONALE = (
    "C14-is-the-first-missing-case-after-complete-C01-through-C13",
    "B4-is-the-registered-F3-linear-coupled-counterbaseline-with-its-own-complete-M-state-and-configuration",
    "selection-does-not-predict-attenuation-baseline-closure-ranking-or-candidate-outcome",
)
S1_MD_FORBIDDEN_SCOPE = (
    "no-runner-initializer-adapter-or-output-implementation",
    "no-replica-sequence-interval-retry-or-repeat-execution",
    "no-C14-output-or-24-case-matrix-publication",
    "no-other-role-profile-selection",
    "no-baseline-candidate-runtime-memory-or-ai-judgment",
)
S1_MD_DECISION = (
    "B4_PIH_C14_SELECTED_THREE_REFINEMENT_DUAL_DIGEST_NINE_CALL_CONTRACT_BOUND_NO_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1MDB4PIHCaseSelectionContract:
    contract_id: str
    source_s1mc_digest: str
    target_case_record: tuple[object, ...]
    target_replica_ids: tuple[str, ...]
    target_replica_records: tuple[tuple[object, ...], ...]
    sequence_record: tuple[object, ...]
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
            self.contract_id != S1_MD_CONTRACT_ID
            or self.source_s1mc_digest != S1_MD_SOURCE_S1MC_DIGEST
            or self.target_case_record != S1_MD_TARGET_CASE_RECORD
            or self.target_replica_ids != S1_MD_TARGET_REPLICA_IDS
            or self.target_replica_records != S1_MD_TARGET_REPLICA_RECORDS
            or self.sequence_record != S1_MD_SEQUENCE_RECORD
            or self.corrected_fresh_state_record != S1_MD_FRESH_STATE_RECORD
            or self.fresh_field_digest != S1_MD_FRESH_FIELD_DIGEST
            or self.fresh_private_state_digest != S1_MD_FRESH_PRIVATE_STATE_DIGEST
            or self.embedded_m_state_digest != S1_MD_EMBEDDED_M_STATE_DIGEST
            or self.b4_configuration_digest != S1_MD_B4_CONFIGURATION_DIGEST
            or self.complete_provenance_digest_role != S1_KE_COMPLETE_PROVENANCE_DIGEST_ROLE
            or self.comparison_digest_role != S1_KE_COMPARISON_DIGEST_ROLE
            or self.corrected_output_schema != S1_KE_CORRECTED_OUTPUT_SCHEMA
            or self.fresh_start_and_carry_rules != S1_MD_FRESH_START_RULES
            or self.execution_budget != S1_MD_EXECUTION_BUDGET
            or self.output_acceptance_rules != S1_MD_OUTPUT_ACCEPTANCE_RULES
            or self.selection_rationale != S1_MD_SELECTION_RATIONALE
            or self.forbidden_scope != S1_MD_FORBIDDEN_SCOPE
            or (
                self.target_replica_count,
                self.sequences_per_target_replica,
                self.intervals_per_sequence,
                self.intervals_per_target_replica,
                self.maximum_new_interval_calls,
            ) != (3, 1, 3, 3, 9)
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
            or self.decision != S1_MD_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1MDB4PIHCaseSelectionContractError(
                "S1-MD weakened the finite B4/P_IH case selection"
            )


def build_dts1_s1md_b4_pih_case_selection_contract(
) -> DTS1S1MDB4PIHCaseSelectionContract:
    """Select and bind C14 without implementing or executing its replicas."""

    source = build_dts1_s1mc_matrix_completeness_gate()
    field_payload = dict(S1_MD_FRESH_STATE_RECORD[5])
    substrate = dict(field_payload["substrate"])
    arm = dict(substrate["arm"])
    private = dict(S1_MD_FRESH_STATE_RECORD[7])
    if (
        source.contract_digest != S1_MD_SOURCE_S1MC_DIGEST
        or source.c14_selection_authorized_next_stage is not True
        or len(S1_MD_TARGET_REPLICA_RECORDS) != 3
        or tuple(row[0] for row in S1_MD_TARGET_REPLICA_RECORDS)
        != S1_MD_TARGET_REPLICA_IDS
        or S1_MD_SEQUENCE_RECORD[3] != 3
        or S1_MD_SEQUENCE_RECORD[5] != (1, 2, 3)
        or S1_MD_FRESH_STATE_RECORD[6] != S1_MD_FRESH_FIELD_DIGEST
        or S1_MD_FRESH_STATE_RECORD[8] != S1_MD_FRESH_PRIVATE_STATE_DIGEST
        or private["embedded_M_state_digest"] != S1_MD_EMBEDDED_M_STATE_DIGEST
        or private["B4_configuration_digest"] != S1_MD_B4_CONFIGURATION_DIGEST
        or substrate["masses"] != (("node-a", 0.5), ("node-b", 0.5))
        or arm["arm_id"] != "mcm.s1jt.b4.linear-coupled"
        or arm["lambda_sm_per_second"] != 1.0
        or arm["kappa"] != 0.5
        or arm["eta"] != 1.0
    ):
        raise DTS1S1MDB4PIHCaseSelectionContractError(
            "registered C14 replicas or corrected B4 fresh state differ"
        )
    values = {
        "contract_id": S1_MD_CONTRACT_ID,
        "source_s1mc_digest": source.contract_digest,
        "target_case_record": S1_MD_TARGET_CASE_RECORD,
        "target_replica_ids": S1_MD_TARGET_REPLICA_IDS,
        "target_replica_records": S1_MD_TARGET_REPLICA_RECORDS,
        "sequence_record": S1_MD_SEQUENCE_RECORD,
        "corrected_fresh_state_record": S1_MD_FRESH_STATE_RECORD,
        "fresh_field_digest": S1_MD_FRESH_FIELD_DIGEST,
        "fresh_private_state_digest": S1_MD_FRESH_PRIVATE_STATE_DIGEST,
        "embedded_m_state_digest": S1_MD_EMBEDDED_M_STATE_DIGEST,
        "b4_configuration_digest": S1_MD_B4_CONFIGURATION_DIGEST,
        "complete_provenance_digest_role": S1_KE_COMPLETE_PROVENANCE_DIGEST_ROLE,
        "comparison_digest_role": S1_KE_COMPARISON_DIGEST_ROLE,
        "corrected_output_schema": S1_KE_CORRECTED_OUTPUT_SCHEMA,
        "fresh_start_and_carry_rules": S1_MD_FRESH_START_RULES,
        "execution_budget": S1_MD_EXECUTION_BUDGET,
        "output_acceptance_rules": S1_MD_OUTPUT_ACCEPTANCE_RULES,
        "selection_rationale": S1_MD_SELECTION_RATIONALE,
        "forbidden_scope": S1_MD_FORBIDDEN_SCOPE,
        "target_replica_count": 3,
        "sequences_per_target_replica": 1,
        "intervals_per_sequence": 3,
        "intervals_per_target_replica": 3,
        "maximum_new_interval_calls": 9,
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
        "decision": S1_MD_DECISION,
    }
    return DTS1S1MDB4PIHCaseSelectionContract(
        **values, contract_digest=_digest(values)
    )
