"""Static S1-LM selection contract for the finite B3/P_IH case."""

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
from .dynamic_substrate_s1ll_b3_pie_case_output_contract import (
    S1_LL_CASE_OUTPUT_DIGEST,
    build_dts1_s1ll_b3_pie_case_output_contract,
)


class DTS1S1LMB3PIHCaseSelectionContractError(ValueError):
    """Raised when the finite S1-LM C10 selection is weakened."""


S1_LM_CONTRACT_ID = "dynamic-substrate.b3-pih-case-selection.s1lm.v1"
S1_LM_SOURCE_S1LL_DIGEST = (
    "b0bfe3b9574654922b7522001ad54b10ea083c62d7e95f14d3d5fe4cc3c58e9f"
)
S1_LM_CASE_ID = "C10"
S1_LM_SEQUENCE_KEY = "P_IH_A_A_A"
S1_LM_TARGET_REPLICA_IDS = (
    "B3:P_IH_ATTENUATION:r2",
    "B3:P_IH_ATTENUATION:r4",
    "B3:P_IH_ATTENUATION:r8",
)
S1_LM_TARGET_CASE_RECORD = next(row for row in S1_JX_CASE_RECORDS if row[0] == S1_LM_CASE_ID)
S1_LM_TARGET_REPLICA_RECORDS = tuple(
    row for row in S1_JX_REPLICA_RECORDS if row[0] in S1_LM_TARGET_REPLICA_IDS
)
S1_LM_SEQUENCE_RECORD = next(
    row for row in S1_JX_SEQUENCE_RECORDS if row[0] == S1_LM_SEQUENCE_KEY
)
S1_LM_FRESH_STATE_RECORD = next(
    row
    for row in S1_JZ_FRESH_STATE_RECORDS
    if row[0] == "B3" and row[1] == "TWO_NODE_OPEN_LINE"
)
S1_LM_FRESH_FIELD_DIGEST = "0314a0ef30d3bc27b4398169073f6ffd0919016f086f73083b55e6be18b175bb"
S1_LM_FRESH_PRIVATE_STATE_DIGEST = "18e61bccd53473161d8dfc22878234d3ad0b64bb39340a2c909609542a555ab5"
S1_LM_EMBEDDED_M_STATE_DIGEST = "f70feda06d15eea22b6da68ed7b746e05a697f3f7d6e1489487ea945d1fe2c26"
S1_LM_FRESH_START_RULES = (
    "r2-r4-and-r8-each-use-two-independent-corrected-B3-fresh-states-one-per-sequence",
    "P_IH_A_A_A-starts-once-from-that-refinements-own-fresh-state",
    "complete-field-M-state-and-bound-arm-carry-only-between-the-three-ordered-intervals-within-one-sequence",
    "no-field-M-state-output-or-provenance-carries-between-sequences-or-refinements",
)
S1_LM_EXECUTION_BUDGET = (
    ("target_replica_count", 3),
    ("sequences_per_replica", 1),
    ("interval_calls_per_sequence", 3),
    ("interval_calls_per_replica", 3),
    ("maximum_new_interval_calls", 9),
    ("retry_or_repeat_calls", 0),
)
S1_LM_OUTPUT_ACCEPTANCE_RULES = (
    "each-replica-publishes-one-atomic-mcm.s1jz.complete-replica-output.v2-or-one-error",
    "each-output-carries-one-complete-provenance-digest-and-one-identity-neutral-comparison-digest",
    "B3-comparison-content-may-differ-across-r2-r4-r8-and-must-not-be-forced-bit-identical",
    "all-three-replicas-must-pass-before-C10-may-be-composed-in-a-later-stage",
)
S1_LM_SELECTION_RATIONALE = (
    "C10-is-the-next-registered-B3-baseline-case-after-complete-C09",
    "B3-is-the-registered-f3-local-leaky-counterbaseline-with-its-own-complete-M-state-and-arm",
    "selection-does-not-predict-baseline-closure-ranking-or-candidate-outcome",
)
S1_LM_FORBIDDEN_SCOPE = (
    "no-runner-initializer-adapter-or-output-implementation",
    "no-replica-sequence-interval-retry-or-repeat-execution",
    "no-C10-output-or-24-case-matrix-publication",
    "no-other-role-profile-selection",
    "no-baseline-candidate-runtime-or-research-judgment",
)
S1_LM_DECISION = (
    "B3_PIH_C10_SELECTED_THREE_REFINEMENT_DUAL_DIGEST_NINE_CALL_CONTRACT_BOUND_NO_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1LMB3PIHCaseSelectionContract:
    contract_id: str
    source_s1ll_digest: str
    target_case_record: tuple[object, ...]
    target_replica_ids: tuple[str, ...]
    target_replica_records: tuple[tuple[object, ...], ...]
    sequence_record: tuple[object, ...]
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
    maximum_new_interval_calls: int
    case_selected: bool
    runner_extension_implemented: bool
    target_replicas_executed: int
    interval_calls_executed: int
    case_output_composed: bool
    matrix_24_case_output_published: bool
    baseline_judgment_present: bool
    candidate_comparison_present: bool
    runtime_integration_present: bool
    exact_implementation_execution_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {field.name: getattr(self, field.name) for field in fields(self) if field.name != "contract_digest"}
        if (
            self.contract_id != S1_LM_CONTRACT_ID
            or self.source_s1ll_digest != S1_LM_SOURCE_S1LL_DIGEST
            or self.target_case_record != S1_LM_TARGET_CASE_RECORD
            or self.target_replica_ids != S1_LM_TARGET_REPLICA_IDS
            or self.target_replica_records != S1_LM_TARGET_REPLICA_RECORDS
            or self.sequence_record != S1_LM_SEQUENCE_RECORD
            or self.corrected_fresh_state_record != S1_LM_FRESH_STATE_RECORD
            or self.fresh_field_digest != S1_LM_FRESH_FIELD_DIGEST
            or self.fresh_private_state_digest != S1_LM_FRESH_PRIVATE_STATE_DIGEST
            or self.embedded_m_state_digest != S1_LM_EMBEDDED_M_STATE_DIGEST
            or self.complete_provenance_digest_role != S1_KE_COMPLETE_PROVENANCE_DIGEST_ROLE
            or self.comparison_digest_role != S1_KE_COMPARISON_DIGEST_ROLE
            or self.corrected_output_schema != S1_KE_CORRECTED_OUTPUT_SCHEMA
            or self.fresh_start_and_carry_rules != S1_LM_FRESH_START_RULES
            or self.execution_budget != S1_LM_EXECUTION_BUDGET
            or self.output_acceptance_rules != S1_LM_OUTPUT_ACCEPTANCE_RULES
            or self.selection_rationale != S1_LM_SELECTION_RATIONALE
            or self.forbidden_scope != S1_LM_FORBIDDEN_SCOPE
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
            or self.runtime_integration_present is not False
            or self.exact_implementation_execution_authorized_next_stage is not True
            or self.decision != S1_LM_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1LMB3PIHCaseSelectionContractError(
                "S1-LM weakened the finite B3/P_IH case selection"
            )


def build_dts1_s1lm_b3_pih_case_selection_contract(
) -> DTS1S1LMB3PIHCaseSelectionContract:
    """Select and bind C10 without implementing or executing its replicas."""

    source = build_dts1_s1ll_b3_pie_case_output_contract()
    private = dict(S1_LM_FRESH_STATE_RECORD[7])
    if (
        source.contract_digest != S1_LM_SOURCE_S1LL_DIGEST
        or source.case_output_digest != S1_LL_CASE_OUTPUT_DIGEST
        or not source.decision.startswith("C09_B3_PIE")
        or len(S1_LM_TARGET_REPLICA_RECORDS) != 3
        or tuple(row[0] for row in S1_LM_TARGET_REPLICA_RECORDS) != S1_LM_TARGET_REPLICA_IDS
        or S1_LM_SEQUENCE_RECORD[3] != 3
        or S1_LM_FRESH_STATE_RECORD[6] != S1_LM_FRESH_FIELD_DIGEST
        or S1_LM_FRESH_STATE_RECORD[8] != S1_LM_FRESH_PRIVATE_STATE_DIGEST
        or private["embedded_M_state_digest"] != S1_LM_EMBEDDED_M_STATE_DIGEST
    ):
        raise DTS1S1LMB3PIHCaseSelectionContractError(
            "registered C10 replicas or corrected B3 fresh state differ"
        )
    values = {
        "contract_id": S1_LM_CONTRACT_ID,
        "source_s1ll_digest": source.contract_digest,
        "target_case_record": S1_LM_TARGET_CASE_RECORD,
        "target_replica_ids": S1_LM_TARGET_REPLICA_IDS,
        "target_replica_records": S1_LM_TARGET_REPLICA_RECORDS,
        "sequence_record": S1_LM_SEQUENCE_RECORD,
        "corrected_fresh_state_record": S1_LM_FRESH_STATE_RECORD,
        "fresh_field_digest": S1_LM_FRESH_FIELD_DIGEST,
        "fresh_private_state_digest": S1_LM_FRESH_PRIVATE_STATE_DIGEST,
        "embedded_m_state_digest": S1_LM_EMBEDDED_M_STATE_DIGEST,
        "complete_provenance_digest_role": S1_KE_COMPLETE_PROVENANCE_DIGEST_ROLE,
        "comparison_digest_role": S1_KE_COMPARISON_DIGEST_ROLE,
        "corrected_output_schema": S1_KE_CORRECTED_OUTPUT_SCHEMA,
        "fresh_start_and_carry_rules": S1_LM_FRESH_START_RULES,
        "execution_budget": S1_LM_EXECUTION_BUDGET,
        "output_acceptance_rules": S1_LM_OUTPUT_ACCEPTANCE_RULES,
        "selection_rationale": S1_LM_SELECTION_RATIONALE,
        "forbidden_scope": S1_LM_FORBIDDEN_SCOPE,
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
        "runtime_integration_present": False,
        "exact_implementation_execution_authorized_next_stage": True,
        "decision": S1_LM_DECISION,
    }
    return DTS1S1LMB3PIHCaseSelectionContract(
        **values, contract_digest=_digest(values)
    )
