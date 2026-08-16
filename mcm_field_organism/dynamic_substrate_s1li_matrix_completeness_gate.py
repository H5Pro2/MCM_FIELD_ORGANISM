"""Static S1-LI completeness gate for the registered 24-case matrix."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    S1_JX_CASE_RECORDS,
)
from .dynamic_substrate_s1ko_corrected_b1_pie_case_output_contract import (
    S1_KO_CASE_OUTPUT_DIGEST,
)
from .dynamic_substrate_s1ks_b1_pih_case_output_contract import (
    S1_KS_CASE_OUTPUT_DIGEST,
)
from .dynamic_substrate_s1ky_b1_pik_case_output_contract import (
    S1_KY_CASE_OUTPUT_DIGEST,
)
from .dynamic_substrate_s1le_b1_pin_case_output_contract import (
    S1_LE_CASE_OUTPUT_DIGEST,
)
from .dynamic_substrate_s1kp_b2_pie_case_output_contract import (
    S1_KP_CASE_OUTPUT_DIGEST,
)
from .dynamic_substrate_s1kv_b2_pih_case_output_contract import (
    S1_KV_CASE_OUTPUT_DIGEST,
)
from .dynamic_substrate_s1lb_b2_pik_case_output_contract import (
    S1_LB_CASE_OUTPUT_DIGEST,
)
from .dynamic_substrate_s1lh_b2_pin_case_output_contract import (
    S1_LH_CASE_OUTPUT_DIGEST,
)


class DTS1S1LIMatrixCompletenessGateError(ValueError):
    """Raised when S1-LI permits an incomplete matrix to proceed."""


S1_LI_CONTRACT_ID = "dynamic-substrate.matrix-completeness-gate.s1li.v1"
S1_LI_SOURCE_S1LH_DIGEST = (
    "862e37b9dfa47d980f13694fcb4f78e06a742812d5dfbf6821c4af7f8eaf0c25"
)
S1_LI_COMPLETED_CASE_IDS = tuple(f"C{index:02d}" for index in range(1, 9))
S1_LI_MISSING_CASE_IDS = tuple(f"C{index:02d}" for index in range(9, 25))
S1_LI_COMPLETED_CASE_CONTRACT_DIGESTS = (
    "f97b306256c42ab9872f7db71ad5605f18a97a274052ba96430c7b0e2244cfa0",
    "d2ed48ba9be2fcbac31d069ad9fc741cd517f521b5d8037441ead40fd19e53aa",
    "0877c42df920ef9302cf46fc5c4247638b456cf3961d640e9b3752629e5f96f9",
    "9c6a97a47a9fda8a14590aca0c67b4fd109f67b0824a2bd22b49c2bc8522b812",
    "133680fef4e057f5500d4836ee6f47814d37d9133df78fd250bf48df0f84a473",
    "495139baff29222708e261d0be4c949cf403b6dd6af267670da8774d84cfaf41",
    "d5ebc93d6521d384d0087ea2601df52a5b0ebe2cacea34d3b920966b326c54ed",
    S1_LI_SOURCE_S1LH_DIGEST,
)
S1_LI_COMPLETED_CASE_OUTPUT_DIGESTS = (
    S1_KO_CASE_OUTPUT_DIGEST,
    S1_KS_CASE_OUTPUT_DIGEST,
    S1_KY_CASE_OUTPUT_DIGEST,
    S1_LE_CASE_OUTPUT_DIGEST,
    S1_KP_CASE_OUTPUT_DIGEST,
    S1_KV_CASE_OUTPUT_DIGEST,
    S1_LB_CASE_OUTPUT_DIGEST,
    S1_LH_CASE_OUTPUT_DIGEST,
)
S1_LI_NEXT_CASE_ID = "C09"
S1_LI_NEXT_CASE_RECORD = next(
    row for row in S1_JX_CASE_RECORDS if row[0] == S1_LI_NEXT_CASE_ID
)
S1_LI_CORRECTION_RULES = (
    "the-registered-24-case-matrix-means-C01-through-C24-not-eight-cases-times-three-refinements",
    "C01-through-C08-contribute-24-complete-refinement-outputs-but-only-eight-complete-profile-cases",
    "the-S1LH-next-stage-matrix-composition-authorization-is-superseded-as-incomplete",
    "C09-B3-P_IE-is-the-only-next-case-that-may-be-selected",
)
S1_LI_FORBIDDEN_SCOPE = (
    "no-matrix-composition-or-publication",
    "no-case-replica-sequence-or-interval-execution",
    "no-C09-implementation-or-output",
    "no-baseline-candidate-or-research-judgment",
    "no-runtime-integration",
)
S1_LI_DECISION = (
    "EIGHT_OF_TWENTY_FOUR_CASES_COMPLETE_MATRIX_COMPOSITION_BLOCKED_C09_SELECTION_AUTHORIZED"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1LIMatrixCompletenessGate:
    contract_id: str
    source_s1lh_digest: str
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
    c09_selection_authorized_next_stage: bool
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
        registered_ids = tuple(row[0] for row in S1_JX_CASE_RECORDS)
        if (
            self.contract_id != S1_LI_CONTRACT_ID
            or self.source_s1lh_digest != S1_LI_SOURCE_S1LH_DIGEST
            or self.registered_case_ids != registered_ids
            or self.completed_case_ids != S1_LI_COMPLETED_CASE_IDS
            or self.completed_case_contract_digests
            != S1_LI_COMPLETED_CASE_CONTRACT_DIGESTS
            or self.completed_case_output_digests
            != S1_LI_COMPLETED_CASE_OUTPUT_DIGESTS
            or self.missing_case_ids != S1_LI_MISSING_CASE_IDS
            or self.next_case_record != S1_LI_NEXT_CASE_RECORD
            or self.correction_rules != S1_LI_CORRECTION_RULES
            or self.forbidden_scope != S1_LI_FORBIDDEN_SCOPE
            or (self.registered_case_count, self.completed_case_count, self.missing_case_count) != (24, 8, 16)
            or (self.refinements_per_case, self.required_refinement_output_count, self.completed_refinement_output_count, self.missing_refinement_output_count) != (3, 72, 24, 48)
            or self.matrix_complete is not False
            or self.matrix_composition_authorized is not False
            or self.matrix_output_published is not False
            or self.prior_matrix_authorization_superseded is not True
            or self.c09_selection_authorized_next_stage is not True
            or (self.new_replicas_executed, self.new_interval_calls_executed) != (0, 0)
            or self.judgment_present is not False
            or self.runtime_integration_present is not False
            or self.decision != S1_LI_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1LIMatrixCompletenessGateError(
                "S1-LI permitted an incomplete 24-case matrix"
            )


def build_dts1_s1li_matrix_completeness_gate(
) -> DTS1S1LIMatrixCompletenessGate:
    """Block matrix composition and bind C09 as the only next selection."""

    registered_ids = tuple(row[0] for row in S1_JX_CASE_RECORDS)
    if (
        registered_ids != tuple(f"C{index:02d}" for index in range(1, 25))
        or S1_LI_COMPLETED_CASE_IDS + S1_LI_MISSING_CASE_IDS != registered_ids
        or S1_LI_NEXT_CASE_RECORD[:6]
        != ("C09", "B3", "B3_F3_LOCAL_LEAKY", "P_IE_CAUSAL_TWO_SUBSTEP", 2, 8)
        or len(set(S1_LI_COMPLETED_CASE_CONTRACT_DIGESTS)) != 8
        or len(set(S1_LI_COMPLETED_CASE_OUTPUT_DIGESTS)) != 8
    ):
        raise DTS1S1LIMatrixCompletenessGateError(
            "registered cases or completed outputs differ"
        )
    values = {
        "contract_id": S1_LI_CONTRACT_ID,
        "source_s1lh_digest": S1_LI_SOURCE_S1LH_DIGEST,
        "registered_case_ids": registered_ids,
        "completed_case_ids": S1_LI_COMPLETED_CASE_IDS,
        "completed_case_contract_digests": S1_LI_COMPLETED_CASE_CONTRACT_DIGESTS,
        "completed_case_output_digests": S1_LI_COMPLETED_CASE_OUTPUT_DIGESTS,
        "missing_case_ids": S1_LI_MISSING_CASE_IDS,
        "next_case_record": S1_LI_NEXT_CASE_RECORD,
        "correction_rules": S1_LI_CORRECTION_RULES,
        "forbidden_scope": S1_LI_FORBIDDEN_SCOPE,
        "registered_case_count": 24,
        "completed_case_count": 8,
        "missing_case_count": 16,
        "refinements_per_case": 3,
        "required_refinement_output_count": 72,
        "completed_refinement_output_count": 24,
        "missing_refinement_output_count": 48,
        "matrix_complete": False,
        "matrix_composition_authorized": False,
        "matrix_output_published": False,
        "prior_matrix_authorization_superseded": True,
        "c09_selection_authorized_next_stage": True,
        "new_replicas_executed": 0,
        "new_interval_calls_executed": 0,
        "judgment_present": False,
        "runtime_integration_present": False,
        "decision": S1_LI_DECISION,
    }
    return DTS1S1LIMatrixCompletenessGate(
        **values, contract_digest=_digest(values)
    )
