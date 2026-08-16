"""Static S1-MC completeness gate for the registered 24-case matrix."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    S1_JX_CASE_RECORDS,
)
from .dynamic_substrate_s1ly_matrix_completeness_gate import (
    S1_LY_COMPLETED_CASE_CONTRACT_DIGESTS,
    S1_LY_COMPLETED_CASE_IDS,
    S1_LY_COMPLETED_CASE_OUTPUT_DIGESTS,
    S1_LY_DECISION,
    build_dts1_s1ly_matrix_completeness_gate,
)
from .dynamic_substrate_s1mb_b4_pie_case_output_contract import (
    S1_MB_CASE_OUTPUT_DIGEST,
    build_dts1_s1mb_b4_pie_case_output_contract,
)


class DTS1S1MCMatrixCompletenessGateError(ValueError):
    """Raised when the S1-MC matrix gate weakens completion or selection."""


S1_MC_CONTRACT_ID = "dynamic-substrate.matrix-completeness-gate.s1mc.v1"
S1_MC_SOURCE_S1LY_DIGEST = (
    "9801f7ed7628d0e89e0858521617c34b6eaba52d0f1682274544f54fdd2c5009"
)
S1_MC_COMPLETED_CASE_IDS = S1_LY_COMPLETED_CASE_IDS + ("C13",)
S1_MC_MISSING_CASE_IDS = tuple(f"C{index:02d}" for index in range(14, 25))
S1_MC_COMPLETED_CASE_CONTRACT_DIGESTS = S1_LY_COMPLETED_CASE_CONTRACT_DIGESTS + (
    "8e45f668286fdaeda5cd80a95a424dccde3bdc260c576f2b0b9f2d061f48f54e",
)
S1_MC_COMPLETED_CASE_OUTPUT_DIGESTS = (
    *S1_LY_COMPLETED_CASE_OUTPUT_DIGESTS,
    S1_MB_CASE_OUTPUT_DIGEST,
)
S1_MC_NEXT_CASE_ID = "C14"
S1_MC_NEXT_CASE_RECORD = next(
    row for row in S1_JX_CASE_RECORDS if row[0] == S1_MC_NEXT_CASE_ID
)
S1_MC_CORRECTION_RULES = (
    "C01-through-C13-are-now-complete-with-case-contract-and-case-output-digests",
    "C13-completion-does-not-authorize-24-case-matrix-composition",
    "C14-B4-P_IH-is-the-only-next-case-that-may-be-selected",
    "MCM-Memory-remains-a-development-direction-not-a-demonstrated-capability",
    "all-baseline-candidate-memory-ai-and-runtime-judgments-remain-blocked",
)
S1_MC_FORBIDDEN_SCOPE = (
    "no-case-composition-or-matrix-publication",
    "no-case-selection-or-implementation-before-C14",
    "no-technical-execution-or-runtime-integration",
    "no-baseline-closure-ranking-candidate-runtime-memory-or-ai-judgment",
    "no-new-case-output-or-24-case-matrix-publication",
)
S1_MC_DECISION = (
    "THIRTEEN_OF_TWENTY_FOUR_CASES_COMPLETE_MATRIX_COMPOSITION_BLOCKED_C14_SELECTION_AUTHORIZED"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1MCMatrixCompletenessGate:
    contract_id: str
    source_s1ly_digest: str
    source_s1ly_decision: str
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
    c14_selection_authorized_next_stage: bool
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
            self.contract_id != S1_MC_CONTRACT_ID
            or self.source_s1ly_digest != S1_MC_SOURCE_S1LY_DIGEST
            or self.source_s1ly_decision != S1_LY_DECISION
            or self.registered_case_ids != tuple(f"C{index:02d}" for index in range(1, 25))
            or self.completed_case_ids != S1_MC_COMPLETED_CASE_IDS
            or self.completed_case_contract_digests != S1_MC_COMPLETED_CASE_CONTRACT_DIGESTS
            or self.completed_case_output_digests != S1_MC_COMPLETED_CASE_OUTPUT_DIGESTS
            or self.missing_case_ids != S1_MC_MISSING_CASE_IDS
            or self.next_case_record != S1_MC_NEXT_CASE_RECORD
            or self.correction_rules != S1_MC_CORRECTION_RULES
            or self.forbidden_scope != S1_MC_FORBIDDEN_SCOPE
            or (self.registered_case_count, self.completed_case_count, self.missing_case_count) != (24, 13, 11)
            or (
                self.refinements_per_case,
                self.required_refinement_output_count,
                self.completed_refinement_output_count,
                self.missing_refinement_output_count,
            ) != (3, 72, 39, 33)
            or self.matrix_complete is not False
            or self.matrix_composition_authorized is not False
            or self.matrix_output_published is not False
            or self.prior_matrix_authorization_superseded is not True
            or self.c14_selection_authorized_next_stage is not True
            or (self.new_replicas_executed, self.new_interval_calls_executed) != (0, 0)
            or self.judgment_present is not False
            or self.memory_capability_claim_present is not False
            or self.ai_system_claim_present is not False
            or self.runtime_integration_present is not False
            or self.decision != S1_MC_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1MCMatrixCompletenessGateError(
                "S1-MC weakened the matrix completion gate"
            )


def build_dts1_s1mc_matrix_completeness_gate() -> DTS1S1MCMatrixCompletenessGate:
    """Bind C01 through C13 as complete and keep the next selection fixed at C14."""

    source = build_dts1_s1ly_matrix_completeness_gate()
    c13 = build_dts1_s1mb_b4_pie_case_output_contract()
    if (
        source.contract_digest != S1_MC_SOURCE_S1LY_DIGEST
        or source.c13_selection_authorized_next_stage is not True
        or c13.contract_digest != S1_MC_COMPLETED_CASE_CONTRACT_DIGESTS[12]
        or c13.case_output_digest != S1_MC_COMPLETED_CASE_OUTPUT_DIGESTS[12]
        or c13.matrix_gate_authorized_next_stage is not True
    ):
        raise DTS1S1MCMatrixCompletenessGateError(
            "S1-MC requires completed C13 source contract and output"
        )
    if S1_MC_NEXT_CASE_RECORD[:6] != (
        "C14",
        "B4",
        "B4_F3_LINEAR_COUPLED",
        "P_IH_ATTENUATION",
        2,
        8,
    ):
        raise DTS1S1MCMatrixCompletenessGateError(
            "registered C14 case record differs"
        )
    values = {
        "contract_id": S1_MC_CONTRACT_ID,
        "source_s1ly_digest": source.contract_digest,
        "source_s1ly_decision": source.decision,
        "registered_case_ids": tuple(f"C{index:02d}" for index in range(1, 25)),
        "completed_case_ids": S1_MC_COMPLETED_CASE_IDS,
        "completed_case_contract_digests": S1_MC_COMPLETED_CASE_CONTRACT_DIGESTS,
        "completed_case_output_digests": S1_MC_COMPLETED_CASE_OUTPUT_DIGESTS,
        "missing_case_ids": S1_MC_MISSING_CASE_IDS,
        "next_case_record": S1_MC_NEXT_CASE_RECORD,
        "correction_rules": S1_MC_CORRECTION_RULES,
        "forbidden_scope": S1_MC_FORBIDDEN_SCOPE,
        "registered_case_count": 24,
        "completed_case_count": 13,
        "missing_case_count": 11,
        "refinements_per_case": 3,
        "required_refinement_output_count": 72,
        "completed_refinement_output_count": 39,
        "missing_refinement_output_count": 33,
        "matrix_complete": False,
        "matrix_composition_authorized": False,
        "matrix_output_published": False,
        "prior_matrix_authorization_superseded": True,
        "c14_selection_authorized_next_stage": True,
        "new_replicas_executed": 0,
        "new_interval_calls_executed": 0,
        "judgment_present": False,
        "memory_capability_claim_present": False,
        "ai_system_claim_present": False,
        "runtime_integration_present": False,
        "decision": S1_MC_DECISION,
    }
    return DTS1S1MCMatrixCompletenessGate(**values, contract_digest=_digest(values))
