"""Static S1-MS completeness gate for the registered 24-case matrix."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    S1_JX_CASE_RECORDS,
)
from .dynamic_substrate_s1mo_matrix_completeness_gate import (
    S1_MO_COMPLETED_CASE_CONTRACT_DIGESTS,
    S1_MO_COMPLETED_CASE_IDS,
    S1_MO_COMPLETED_CASE_OUTPUT_DIGESTS,
    S1_MO_DECISION,
    build_dts1_s1mo_matrix_completeness_gate,
)
from .dynamic_substrate_s1mr_b5_pie_case_output_contract import (
    S1_MR_CASE_OUTPUT_DIGEST,
    build_dts1_s1mr_b5_pie_case_output_contract,
)


class DTS1S1MSMatrixCompletenessGateError(ValueError):
    """Raised when the S1-MS matrix gate weakens completion or selection."""


S1_MS_CONTRACT_ID = "dynamic-substrate.matrix-completeness-gate.s1ms.v1"
S1_MS_SOURCE_S1MO_DIGEST = (
    "52ad6a28920511257f51488d41e0434cd4d99676977e4ceb857c6b8c31705819"
)
S1_MS_COMPLETED_CASE_IDS = S1_MO_COMPLETED_CASE_IDS + ("C17",)
S1_MS_MISSING_CASE_IDS = tuple(f"C{index:02d}" for index in range(18, 25))
S1_MS_COMPLETED_CASE_CONTRACT_DIGESTS = S1_MO_COMPLETED_CASE_CONTRACT_DIGESTS + (
    "ddccef97b32e42b9319af2d637593875dca0197ff3401d08865b6a4e0d9ba917",
)
S1_MS_COMPLETED_CASE_OUTPUT_DIGESTS = (
    *S1_MO_COMPLETED_CASE_OUTPUT_DIGESTS,
    S1_MR_CASE_OUTPUT_DIGEST,
)
S1_MS_NEXT_CASE_ID = "C18"
S1_MS_NEXT_CASE_RECORD = next(
    row for row in S1_JX_CASE_RECORDS if row[0] == S1_MS_NEXT_CASE_ID
)
S1_MS_CORRECTION_RULES = (
    "C01-through-C17-are-now-complete-with-case-contract-and-case-output-digests",
    "C17-completion-does-not-authorize-24-case-matrix-composition",
    "C18-B5-P_IH-is-the-only-next-case-that-may-be-selected",
    "MCM-Memory-remains-a-development-direction-not-a-demonstrated-capability",
    "all-baseline-candidate-memory-ai-and-runtime-judgments-remain-blocked",
)
S1_MS_FORBIDDEN_SCOPE = (
    "no-case-composition-or-matrix-publication",
    "no-case-selection-or-implementation-before-C18",
    "no-technical-execution-or-runtime-integration",
    "no-baseline-closure-ranking-candidate-runtime-memory-or-ai-judgment",
    "no-new-case-output-or-24-case-matrix-publication",
)
S1_MS_DECISION = (
    "SEVENTEEN_OF_TWENTY_FOUR_CASES_COMPLETE_MATRIX_COMPOSITION_BLOCKED_C18_SELECTION_AUTHORIZED"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1MSMatrixCompletenessGate:
    contract_id: str
    source_s1mo_digest: str
    source_s1mo_decision: str
    registered_case_ids: tuple[str, ...]
    completed_case_ids: tuple[str, ...]
    completed_case_contract_digests: tuple[str, ...]
    completed_case_output_digests: tuple[str, ...]
    missing_case_ids: tuple[str, ...]
    next_case_record: tuple[object, ...]
    correction_rules: tuple[str, ...]
    forbidden_scope: tuple[str, ...]
    registered_case_count: int
    completed_case_count: int
    missing_case_count: int
    refinements_per_case: int
    required_refinement_output_count: int
    completed_refinement_output_count: int
    missing_refinement_output_count: int
    matrix_complete: bool
    matrix_composition_authorized: bool
    matrix_output_published: bool
    prior_matrix_authorization_superseded: bool
    c18_selection_authorized_next_stage: bool
    new_replicas_executed: int
    new_interval_calls_executed: int
    judgment_present: bool
    memory_capability_claim_present: bool
    ai_system_claim_present: bool
    runtime_integration_present: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_MS_CONTRACT_ID
            or self.source_s1mo_digest != S1_MS_SOURCE_S1MO_DIGEST
            or self.source_s1mo_decision != S1_MO_DECISION
            or self.registered_case_ids != tuple(f"C{index:02d}" for index in range(1, 25))
            or self.completed_case_ids != S1_MS_COMPLETED_CASE_IDS
            or self.completed_case_contract_digests != S1_MS_COMPLETED_CASE_CONTRACT_DIGESTS
            or self.completed_case_output_digests != S1_MS_COMPLETED_CASE_OUTPUT_DIGESTS
            or self.missing_case_ids != S1_MS_MISSING_CASE_IDS
            or self.next_case_record != S1_MS_NEXT_CASE_RECORD
            or self.correction_rules != S1_MS_CORRECTION_RULES
            or self.forbidden_scope != S1_MS_FORBIDDEN_SCOPE
            or (self.registered_case_count, self.completed_case_count, self.missing_case_count) != (24, 17, 7)
            or (
                self.refinements_per_case,
                self.required_refinement_output_count,
                self.completed_refinement_output_count,
                self.missing_refinement_output_count,
            ) != (3, 72, 51, 21)
            or self.matrix_complete is not False
            or self.matrix_composition_authorized is not False
            or self.matrix_output_published is not False
            or self.prior_matrix_authorization_superseded is not True
            or self.c18_selection_authorized_next_stage is not True
            or (self.new_replicas_executed, self.new_interval_calls_executed) != (0, 0)
            or self.judgment_present is not False
            or self.memory_capability_claim_present is not False
            or self.ai_system_claim_present is not False
            or self.runtime_integration_present is not False
            or self.decision != S1_MS_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1MSMatrixCompletenessGateError(
                "S1-MS weakened the matrix completion gate"
            )


def build_dts1_s1ms_matrix_completeness_gate() -> DTS1S1MSMatrixCompletenessGate:
    """Bind C01 through C17 as complete and keep the next selection fixed at C18."""

    source = build_dts1_s1mo_matrix_completeness_gate()
    c17 = build_dts1_s1mr_b5_pie_case_output_contract()
    if (
        source.contract_digest != S1_MS_SOURCE_S1MO_DIGEST
        or source.c17_selection_authorized_next_stage is not True
        or c17.contract_digest != S1_MS_COMPLETED_CASE_CONTRACT_DIGESTS[16]
        or c17.case_output_digest != S1_MS_COMPLETED_CASE_OUTPUT_DIGESTS[16]
        or c17.matrix_gate_authorized_next_stage is not True
        or c17.memory_capability_claim_present is not False
        or c17.ai_system_claim_present is not False
    ):
        raise DTS1S1MSMatrixCompletenessGateError(
            "S1-MS requires completed C17 source contract and output"
        )
    if S1_MS_NEXT_CASE_RECORD[:6] != (
        "C18",
        "B5",
        "B5_F3_FULL",
        "P_IH_ATTENUATION",
        2,
        8,
    ):
        raise DTS1S1MSMatrixCompletenessGateError(
            "registered C18 case record differs"
        )
    values = {
        "contract_id": S1_MS_CONTRACT_ID,
        "source_s1mo_digest": source.contract_digest,
        "source_s1mo_decision": source.decision,
        "registered_case_ids": tuple(f"C{index:02d}" for index in range(1, 25)),
        "completed_case_ids": S1_MS_COMPLETED_CASE_IDS,
        "completed_case_contract_digests": S1_MS_COMPLETED_CASE_CONTRACT_DIGESTS,
        "completed_case_output_digests": S1_MS_COMPLETED_CASE_OUTPUT_DIGESTS,
        "missing_case_ids": S1_MS_MISSING_CASE_IDS,
        "next_case_record": S1_MS_NEXT_CASE_RECORD,
        "correction_rules": S1_MS_CORRECTION_RULES,
        "forbidden_scope": S1_MS_FORBIDDEN_SCOPE,
        "registered_case_count": 24,
        "completed_case_count": 17,
        "missing_case_count": 7,
        "refinements_per_case": 3,
        "required_refinement_output_count": 72,
        "completed_refinement_output_count": 51,
        "missing_refinement_output_count": 21,
        "matrix_complete": False,
        "matrix_composition_authorized": False,
        "matrix_output_published": False,
        "prior_matrix_authorization_superseded": True,
        "c18_selection_authorized_next_stage": True,
        "new_replicas_executed": 0,
        "new_interval_calls_executed": 0,
        "judgment_present": False,
        "memory_capability_claim_present": False,
        "ai_system_claim_present": False,
        "runtime_integration_present": False,
        "decision": S1_MS_DECISION,
    }
    return DTS1S1MSMatrixCompletenessGate(**values, contract_digest=_digest(values))
