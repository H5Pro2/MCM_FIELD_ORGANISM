"""Static S1-LY completeness gate for the registered 24-case matrix."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    S1_JX_CASE_RECORDS,
)
from .dynamic_substrate_s1lu_matrix_completeness_gate import (
    S1_LU_COMPLETED_CASE_CONTRACT_DIGESTS,
    S1_LU_COMPLETED_CASE_IDS,
    S1_LU_COMPLETED_CASE_OUTPUT_DIGESTS,
    S1_LU_DECISION,
    build_dts1_s1lu_matrix_completeness_gate,
)
from .dynamic_substrate_s1lx_b3_pin_case_output_contract import (
    S1_LX_CASE_OUTPUT_DIGEST,
    build_dts1_s1lx_b3_pin_case_output_contract,
)


class DTS1S1LYMatrixCompletenessGateError(ValueError):
    """Raised when the S1-LY matrix gate weakens completion or selection."""


S1_LY_CONTRACT_ID = "dynamic-substrate.matrix-completeness-gate.s1ly.v1"
S1_LY_SOURCE_S1LU_DIGEST = (
    "d8e4db8cbff1d378d55d63634443d9472578f84cee838c1c101cfdd5712a9242"
)
S1_LY_COMPLETED_CASE_IDS = S1_LU_COMPLETED_CASE_IDS + ("C12",)
S1_LY_MISSING_CASE_IDS = tuple(f"C{index:02d}" for index in range(13, 25))
S1_LY_COMPLETED_CASE_CONTRACT_DIGESTS = S1_LU_COMPLETED_CASE_CONTRACT_DIGESTS + (
    "51446ae577a2973e54d91a649f5b449807b89148288c1a8e8f9cffdcb5c485c5",
)
S1_LY_COMPLETED_CASE_OUTPUT_DIGESTS = (
    *S1_LU_COMPLETED_CASE_OUTPUT_DIGESTS,
    S1_LX_CASE_OUTPUT_DIGEST,
)
S1_LY_NEXT_CASE_ID = "C13"
S1_LY_NEXT_CASE_RECORD = next(
    row for row in S1_JX_CASE_RECORDS if row[0] == S1_LY_NEXT_CASE_ID
)
S1_LY_CORRECTION_RULES = (
    "C01-through-C12-are-now-complete-with-case-contract-and-case-output-digests",
    "C12-completion-does-not-authorize-24-case-matrix-composition",
    "C13-B4-P_IE-is-the-only-next-case-that-may-be-selected",
    "all-baseline-candidate-and-runtime-judgments-remain-blocked",
)
S1_LY_FORBIDDEN_SCOPE = (
    "no-case-composition-or-matrix-publication",
    "no-case-selection-or-implementation-before-C13",
    "no-technical-execution-or-runtime-integration",
    "no-baseline-closure-ranking-candidate-runtime-or-research-judgment",
    "no-new-case-output-or-24-case-matrix-publication",
)
S1_LY_DECISION = (
    "TWELVE_OF_TWENTY_FOUR_CASES_COMPLETE_MATRIX_COMPOSITION_BLOCKED_C13_SELECTION_AUTHORIZED"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1LYMatrixCompletenessGate:
    contract_id: str
    source_s1lu_digest: str
    source_s1lu_decision: str
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
    c13_selection_authorized_next_stage: bool
    new_replicas_executed: int
    new_interval_calls_executed: int
    judgment_present: bool
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
            self.contract_id != S1_LY_CONTRACT_ID
            or self.source_s1lu_digest != S1_LY_SOURCE_S1LU_DIGEST
            or self.source_s1lu_decision != S1_LU_DECISION
            or self.registered_case_ids != tuple(f"C{index:02d}" for index in range(1, 25))
            or self.completed_case_ids != S1_LY_COMPLETED_CASE_IDS
            or self.completed_case_contract_digests != S1_LY_COMPLETED_CASE_CONTRACT_DIGESTS
            or self.completed_case_output_digests != S1_LY_COMPLETED_CASE_OUTPUT_DIGESTS
            or self.missing_case_ids != S1_LY_MISSING_CASE_IDS
            or self.next_case_record != S1_LY_NEXT_CASE_RECORD
            or self.correction_rules != S1_LY_CORRECTION_RULES
            or self.forbidden_scope != S1_LY_FORBIDDEN_SCOPE
            or (self.registered_case_count, self.completed_case_count, self.missing_case_count) != (24, 12, 12)
            or (
                self.refinements_per_case,
                self.required_refinement_output_count,
                self.completed_refinement_output_count,
                self.missing_refinement_output_count,
            ) != (3, 72, 36, 36)
            or self.matrix_complete is not False
            or self.matrix_composition_authorized is not False
            or self.matrix_output_published is not False
            or self.prior_matrix_authorization_superseded is not True
            or self.c13_selection_authorized_next_stage is not True
            or (self.new_replicas_executed, self.new_interval_calls_executed) != (0, 0)
            or self.judgment_present is not False
            or self.runtime_integration_present is not False
            or self.decision != S1_LY_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1LYMatrixCompletenessGateError(
                "S1-LY weakened the matrix completion gate"
            )


def build_dts1_s1ly_matrix_completeness_gate() -> DTS1S1LYMatrixCompletenessGate:
    """Bind C01 through C12 as complete and keep the next selection fixed at C13."""

    source = build_dts1_s1lu_matrix_completeness_gate()
    c12 = build_dts1_s1lx_b3_pin_case_output_contract()
    if (
        source.contract_digest != S1_LY_SOURCE_S1LU_DIGEST
        or source.c12_selection_authorized_next_stage is not True
        or c12.contract_digest != S1_LY_COMPLETED_CASE_CONTRACT_DIGESTS[11]
        or c12.case_output_digest != S1_LY_COMPLETED_CASE_OUTPUT_DIGESTS[11]
        or c12.c13_selection_authorized_next_stage is not True
    ):
        raise DTS1S1LYMatrixCompletenessGateError(
            "S1-LY requires completed C12 source contract and output"
        )
    if S1_LY_NEXT_CASE_RECORD[:6] != (
        "C13",
        "B4",
        "B4_F3_LINEAR_COUPLED",
        "P_IE_CAUSAL_TWO_SUBSTEP",
        2,
        8,
    ):
        raise DTS1S1LYMatrixCompletenessGateError(
            "registered C13 case record differs"
        )
    values = {
        "contract_id": S1_LY_CONTRACT_ID,
        "source_s1lu_digest": source.contract_digest,
        "source_s1lu_decision": source.decision,
        "registered_case_ids": tuple(f"C{index:02d}" for index in range(1, 25)),
        "completed_case_ids": S1_LY_COMPLETED_CASE_IDS,
        "completed_case_contract_digests": S1_LY_COMPLETED_CASE_CONTRACT_DIGESTS,
        "completed_case_output_digests": S1_LY_COMPLETED_CASE_OUTPUT_DIGESTS,
        "missing_case_ids": S1_LY_MISSING_CASE_IDS,
        "next_case_record": S1_LY_NEXT_CASE_RECORD,
        "correction_rules": S1_LY_CORRECTION_RULES,
        "forbidden_scope": S1_LY_FORBIDDEN_SCOPE,
        "registered_case_count": 24,
        "completed_case_count": 12,
        "missing_case_count": 12,
        "refinements_per_case": 3,
        "required_refinement_output_count": 72,
        "completed_refinement_output_count": 36,
        "missing_refinement_output_count": 36,
        "matrix_complete": False,
        "matrix_composition_authorized": False,
        "matrix_output_published": False,
        "prior_matrix_authorization_superseded": True,
        "c13_selection_authorized_next_stage": True,
        "new_replicas_executed": 0,
        "new_interval_calls_executed": 0,
        "judgment_present": False,
        "runtime_integration_present": False,
        "decision": S1_LY_DECISION,
    }
    return DTS1S1LYMatrixCompletenessGate(**values, contract_digest=_digest(values))
