"""Static S1-LQ completeness gate for the registered 24-case matrix."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1li_matrix_completeness_gate import (
    S1_LI_COMPLETED_CASE_CONTRACT_DIGESTS,
    S1_LI_COMPLETED_CASE_OUTPUT_DIGESTS,
    S1_LI_COMPLETED_CASE_IDS,
    S1_LI_DECISION,
    S1_LI_MISSING_CASE_IDS,
    build_dts1_s1li_matrix_completeness_gate,
)
from .dynamic_substrate_s1lj_b3_pie_case_selection_contract import (
    build_dts1_s1lj_b3_pie_case_selection_contract,
)
from .dynamic_substrate_s1ll_b3_pie_case_output_contract import (
    S1_LL_CASE_OUTPUT_DIGEST,
    build_dts1_s1ll_b3_pie_case_output_contract,
)
from .dynamic_substrate_s1lp_b3_pih_case_output_contract import (
    S1_LP_CASE_OUTPUT_DIGEST,
    build_dts1_s1lp_b3_pih_case_output_contract,
)
from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    S1_JX_CASE_RECORDS,
)


class DTS1S1LQMatrixCompletenessGateError(ValueError):
    """Raised when the S1-LQ matrix gate weakens completion or selection."""


S1_LQ_CONTRACT_ID = "dynamic-substrate.matrix-completeness-gate.s1lq.v1"
S1_LQ_SOURCE_S1LI_DIGEST = (
    "e4f4bed962cdf8164271c7c388df5fc726fd144f8857f94200ca81e21dbfc1d8"
)
S1_LQ_COMPLETED_CASE_IDS = S1_LI_COMPLETED_CASE_IDS + ("C09", "C10")
S1_LQ_MISSING_CASE_IDS = tuple(f"C{index:02d}" for index in range(11, 25))
S1_LQ_COMPLETED_CASE_CONTRACT_DIGESTS = S1_LI_COMPLETED_CASE_CONTRACT_DIGESTS + (
    "b0bfe3b9574654922b7522001ad54b10ea083c62d7e95f14d3d5fe4cc3c58e9f",
    "ae1ec48d4e8dd36a022c4b6434651deff8f65890315658d5121e716f0d149f90",
)
S1_LQ_COMPLETED_CASE_OUTPUT_DIGESTS = (
    *S1_LI_COMPLETED_CASE_OUTPUT_DIGESTS,
    S1_LL_CASE_OUTPUT_DIGEST,
    S1_LP_CASE_OUTPUT_DIGEST,
)
S1_LQ_NEXT_CASE_ID = "C11"
S1_LQ_NEXT_CASE_RECORD = next(
    row for row in S1_JX_CASE_RECORDS if row[0] == S1_LQ_NEXT_CASE_ID
)
S1_LQ_CORRECTION_RULES = (
    "the-registered-24-case-matrix-means-C01-through-C24-not-eight-cases-times-three-refinements",
    "C01-through-C10-are-now-complete-with-case-contract-and-case-output-digests",
    "C01-through-C10-could-only-have-been-bound-after-C01-through-C08-and-C09-and-C10-completed",
    "C11-B3-P_IK_IS-the-only-next-case-that-may-be-selected",
)
S1_LQ_FORBIDDEN_SCOPE = (
    "no-case-composition-or-matrix-publication",
    "no-case-selection-or-implementation-before-C11",
    "no-technical-execution-or-runtime-integration",
    "no-baseline-closure-ranking-candidate-runtime-or-research-judgment",
    "no-new-case-output-or-24-case-matrix-publication",
)
S1_LQ_DECISION = (
    "TEN_OF_TWENTY_FOUR_CASES_COMPLETE_MATRIX_COMPOSITION_BLOCKED_C11_SELECTION_AUTHORIZED"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1LQMatrixCompletenessGate:
    contract_id: str
    source_s1li_digest: str
    source_s1li_decision: str
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
    c11_selection_authorized_next_stage: bool
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
            self.contract_id != S1_LQ_CONTRACT_ID
            or self.source_s1li_digest != S1_LQ_SOURCE_S1LI_DIGEST
            or self.source_s1li_decision != S1_LI_DECISION
            or self.registered_case_ids != tuple(f"C{index:02d}" for index in range(1, 25))
            or self.completed_case_ids != S1_LQ_COMPLETED_CASE_IDS
            or self.completed_case_contract_digests != S1_LQ_COMPLETED_CASE_CONTRACT_DIGESTS
            or self.completed_case_output_digests != S1_LQ_COMPLETED_CASE_OUTPUT_DIGESTS
            or self.missing_case_ids != S1_LQ_MISSING_CASE_IDS
            or self.next_case_record != S1_LQ_NEXT_CASE_RECORD
            or self.correction_rules != S1_LQ_CORRECTION_RULES
            or self.forbidden_scope != S1_LQ_FORBIDDEN_SCOPE
            or (self.registered_case_count, self.completed_case_count, self.missing_case_count) != (
                24,
                10,
                14,
            )
            or (
                self.refinements_per_case,
                self.required_refinement_output_count,
                self.completed_refinement_output_count,
                self.missing_refinement_output_count,
            ) != (3, 72, 30, 42)
            or self.matrix_complete is not False
            or self.matrix_composition_authorized is not False
            or self.matrix_output_published is not False
            or self.prior_matrix_authorization_superseded is not True
            or self.c11_selection_authorized_next_stage is not True
            or (self.new_replicas_executed, self.new_interval_calls_executed) != (0, 0)
            or self.judgment_present is not False
            or self.runtime_integration_present is not False
            or self.decision != S1_LQ_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1LQMatrixCompletenessGateError(
                "S1-LQ weakened the matrix completion gate"
            )


def build_dts1_s1lq_matrix_completeness_gate() -> DTS1S1LQMatrixCompletenessGate:
    """Bind C01 through C10 as complete and keep the next selection fixed at C11."""

    source = build_dts1_s1li_matrix_completeness_gate()
    c09 = build_dts1_s1ll_b3_pie_case_output_contract()
    c10 = build_dts1_s1lp_b3_pih_case_output_contract()
    if (
        source.contract_digest != S1_LQ_SOURCE_S1LI_DIGEST
        or source.c09_selection_authorized_next_stage is not True
        or c09.contract_digest != S1_LQ_COMPLETED_CASE_CONTRACT_DIGESTS[8]
        or c10.contract_digest != S1_LQ_COMPLETED_CASE_CONTRACT_DIGESTS[9]
        or c09.case_output_digest != S1_LQ_COMPLETED_CASE_OUTPUT_DIGESTS[8]
        or c10.case_output_digest != S1_LQ_COMPLETED_CASE_OUTPUT_DIGESTS[9]
    ):
        raise DTS1S1LQMatrixCompletenessGateError(
            "S1-LQ requires completed C09 and C10 source contracts and outputs"
        )
    if (
        S1_LQ_NEXT_CASE_RECORD[:6]
        != ("C11", "B3", "B3_F3_LOCAL_LEAKY", "P_IK_INTERFERENCE", 3, 6)
        or build_dts1_s1lj_b3_pie_case_selection_contract().exact_implementation_execution_authorized_next_stage
        is not True
    ):
        raise DTS1S1LQMatrixCompletenessGateError(
            "source case records or previous selection guard differ"
        )

    values = {
        "contract_id": S1_LQ_CONTRACT_ID,
        "source_s1li_digest": source.contract_digest,
        "source_s1li_decision": source.decision,
        "registered_case_ids": tuple(f"C{index:02d}" for index in range(1, 25)),
        "completed_case_ids": S1_LQ_COMPLETED_CASE_IDS,
        "completed_case_contract_digests": S1_LQ_COMPLETED_CASE_CONTRACT_DIGESTS,
        "completed_case_output_digests": S1_LQ_COMPLETED_CASE_OUTPUT_DIGESTS,
        "missing_case_ids": S1_LQ_MISSING_CASE_IDS,
        "next_case_record": S1_LQ_NEXT_CASE_RECORD,
        "correction_rules": S1_LQ_CORRECTION_RULES,
        "forbidden_scope": S1_LQ_FORBIDDEN_SCOPE,
        "registered_case_count": 24,
        "completed_case_count": 10,
        "missing_case_count": 14,
        "refinements_per_case": 3,
        "required_refinement_output_count": 72,
        "completed_refinement_output_count": 30,
        "missing_refinement_output_count": 42,
        "matrix_complete": False,
        "matrix_composition_authorized": False,
        "matrix_output_published": False,
        "prior_matrix_authorization_superseded": True,
        "c11_selection_authorized_next_stage": True,
        "new_replicas_executed": 0,
        "new_interval_calls_executed": 0,
        "judgment_present": False,
        "runtime_integration_present": False,
        "decision": S1_LQ_DECISION,
    }
    return DTS1S1LQMatrixCompletenessGate(**values, contract_digest=_digest(values))
