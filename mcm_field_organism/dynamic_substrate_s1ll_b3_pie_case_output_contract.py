"""Static S1-LL complete B3/P_IE C09 case output contract."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_dts1_one_replica_orchestrator import (
    S1_LK_CHECKPOINT_ADAPTER_OUTPUT_DIGESTS,
    S1_LK_CHECKPOINT_FIELD_DIGESTS,
    S1_LK_CHECKPOINT_PRIVATE_STATE_DIGESTS,
    S1_LK_TARGET_COMPARISON_DIGESTS,
    S1_LK_TARGET_COMPONENTS_BY_REFINEMENT,
    S1_LK_TARGET_OUTPUT_DIGESTS,
    S1_LK_TARGET_REPLICA_IDS,
    build_dts1_s1lk_implementation_receipt,
)
from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    S1_JX_CASE_RECORDS,
)
from .dynamic_substrate_s1li_matrix_completeness_gate import (
    build_dts1_s1li_matrix_completeness_gate,
)


class DTS1S1LLB3PIECaseOutputContractError(ValueError):
    """Raised when the finite S1-LL C09 case output is weakened."""


S1_LL_CONTRACT_ID = "dynamic-substrate.b3-pie-case-output.s1ll.v1"
S1_LL_SOURCE_S1LI_DIGEST = (
    "e4f4bed962cdf8164271c7c388df5fc726fd144f8857f94200ca81e21dbfc1d8"
)
S1_LL_SOURCE_S1LK_DIGEST = (
    "ac97bedfa3811a8e41240c9b1b3a1a8288c5f40f05b678e6074d71852617c7c2"
)
S1_LL_CASE_ID = "C09"


def _subtract(left: tuple[float, ...], right: tuple[float, ...]) -> tuple[float, ...]:
    if len(left) != 8 or len(right) != 8:
        raise DTS1S1LLB3PIECaseOutputContractError(
            "C09 residual inputs must each contain eight components"
        )
    return tuple(0.0 if left_value == right_value else left_value - right_value for left_value, right_value in zip(left, right, strict=True))


_COMPONENTS = dict(S1_LK_TARGET_COMPONENTS_BY_REFINEMENT)
S1_LL_REFINEMENT_RESIDUALS = (
    ("r2_minus_r4", _subtract(_COMPONENTS[2], _COMPONENTS[4])),
    ("r4_minus_r8", _subtract(_COMPONENTS[4], _COMPONENTS[8])),
)
S1_LL_CASE_SCHEMA = (
    ("schema_id", "mcm.s1ll.complete-three-refinement-case.v1"),
    ("fields", (
        "schema_id", "case_id", "model_role", "long_model_role",
        "profile_block", "node_count", "component_count", "replica_ids",
        "replica_output_digests", "refinement_comparison_digests",
        "components_by_refinement", "primary_refinement", "primary_components",
        "refinement_residuals", "checkpoint_field_digests",
        "checkpoint_private_state_digests", "checkpoint_adapter_output_digests",
        "checkpoint_parent_identity_valid", "independent_sequences_bit_identical_within_refinement",
        "refinement_outputs_distinct", "status", "case_output_digest",
    )),
    ("publication", "one-complete-case-record-or-one-error-with-no-partial-value"),
)
S1_LL_STATUS = "TECHNICALLY_COMPLETE_NO_PIE_BASELINE_OR_CANDIDATE_JUDGMENT"
S1_LL_DECISION = (
    "C09_B3_PIE_THREE_REFINEMENT_CASE_OUTPUT_AND_RESIDUALS_BOUND_FROM_S1LK_RECEIPT_NO_NEW_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _case_payload() -> dict[str, object]:
    return {
        "schema_id": "mcm.s1ll.complete-three-refinement-case.v1",
        "case_id": S1_LL_CASE_ID,
        "model_role": "B3",
        "long_model_role": "B3_F3_LOCAL_LEAKY",
        "profile_block": "P_IE_CAUSAL_TWO_SUBSTEP",
        "node_count": 2,
        "component_count": 8,
        "replica_ids": S1_LK_TARGET_REPLICA_IDS,
        "replica_output_digests": S1_LK_TARGET_OUTPUT_DIGESTS,
        "refinement_comparison_digests": S1_LK_TARGET_COMPARISON_DIGESTS,
        "components_by_refinement": S1_LK_TARGET_COMPONENTS_BY_REFINEMENT,
        "primary_refinement": 4,
        "primary_components": _COMPONENTS[4],
        "refinement_residuals": S1_LL_REFINEMENT_RESIDUALS,
        "checkpoint_field_digests": S1_LK_CHECKPOINT_FIELD_DIGESTS,
        "checkpoint_private_state_digests": S1_LK_CHECKPOINT_PRIVATE_STATE_DIGESTS,
        "checkpoint_adapter_output_digests": S1_LK_CHECKPOINT_ADAPTER_OUTPUT_DIGESTS,
        "checkpoint_parent_identity_valid": True,
        "independent_sequences_bit_identical_within_refinement": True,
        "refinement_outputs_distinct": True,
        "status": S1_LL_STATUS,
    }


S1_LL_CASE_OUTPUT_DIGEST = _digest(_case_payload())


@dataclass(frozen=True, slots=True)
class DTS1S1LLB3PIECaseOutputContract:
    contract_id: str
    source_s1li_digest: str
    source_s1lk_digest: str
    source_s1jx_case_record: tuple[object, ...]
    case_schema: tuple[tuple[str, object], ...]
    case_payload: tuple[tuple[str, object], ...]
    case_output_digest: str
    replica_count: int
    sequence_count_per_refinement: int
    checkpoint_count_per_refinement: int
    component_count_per_refinement: int
    primary_refinement: int
    comparison_digest_count: int
    distinct_provenance_digest_count: int
    residual_block_count: int
    residual_component_count: int
    checkpoint_parent_identity_valid: bool
    independent_sequences_bit_identical_within_refinement: bool
    refinement_outputs_distinct: bool
    all_primary_components_zero: bool
    all_refinement_residuals_zero: bool
    case_record_composed: bool
    new_replicas_executed: int
    new_interval_calls_executed: int
    matrix_24_case_output_published: bool
    baseline_judgment_present: bool
    candidate_comparison_present: bool
    runtime_integration_present: bool
    c10_selection_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        expected_case = next(
            row for row in S1_JX_CASE_RECORDS if row[0] == S1_LL_CASE_ID
        )
        if (
            self.contract_id != S1_LL_CONTRACT_ID
            or self.source_s1li_digest != S1_LL_SOURCE_S1LI_DIGEST
            or self.source_s1lk_digest != S1_LL_SOURCE_S1LK_DIGEST
            or self.source_s1jx_case_record != expected_case
            or self.case_schema != S1_LL_CASE_SCHEMA
            or self.case_payload != tuple(_case_payload().items())
            or self.case_output_digest != S1_LL_CASE_OUTPUT_DIGEST
            or (self.replica_count, self.sequence_count_per_refinement, self.checkpoint_count_per_refinement, self.component_count_per_refinement) != (3, 2, 4, 8)
            or (self.primary_refinement, self.comparison_digest_count, self.distinct_provenance_digest_count) != (4, 3, 3)
            or (self.residual_block_count, self.residual_component_count) != (2, 16)
            or self.checkpoint_parent_identity_valid is not True
            or self.independent_sequences_bit_identical_within_refinement is not True
            or self.refinement_outputs_distinct is not True
            or self.all_primary_components_zero is not True
            or self.all_refinement_residuals_zero is not True
            or self.case_record_composed is not True
            or (self.new_replicas_executed, self.new_interval_calls_executed) != (0, 0)
            or self.matrix_24_case_output_published is not False
            or self.baseline_judgment_present is not False
            or self.candidate_comparison_present is not False
            or self.runtime_integration_present is not False
            or self.c10_selection_authorized_next_stage is not True
            or self.decision != S1_LL_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1LLB3PIECaseOutputContractError(
                "S1-LL weakened the complete C09 case output"
            )


def build_dts1_s1ll_b3_pie_case_output_contract(
) -> DTS1S1LLB3PIECaseOutputContract:
    """Compose C09 and its residuals without executing a replica."""

    prior = build_dts1_s1li_matrix_completeness_gate()
    source = build_dts1_s1lk_implementation_receipt()
    if (
        prior.contract_digest != S1_LL_SOURCE_S1LI_DIGEST
        or source.receipt_digest != S1_LL_SOURCE_S1LK_DIGEST
        or source.target_output_digests != S1_LK_TARGET_OUTPUT_DIGESTS
        or source.target_comparison_digests != S1_LK_TARGET_COMPARISON_DIGESTS
        or source.target_components_by_refinement
        != S1_LK_TARGET_COMPONENTS_BY_REFINEMENT
        or source.checkpoint_field_digests != S1_LK_CHECKPOINT_FIELD_DIGESTS
        or source.checkpoint_private_state_digests
        != S1_LK_CHECKPOINT_PRIVATE_STATE_DIGESTS
        or source.checkpoint_adapter_output_digests
        != S1_LK_CHECKPOINT_ADAPTER_OUTPUT_DIGESTS
    ):
        raise DTS1S1LLB3PIECaseOutputContractError(
            "S1-LI matrix gate or S1-LK output source differs"
        )
    residual_values = tuple(value for _, values in S1_LL_REFINEMENT_RESIDUALS for value in values)
    values = {
        "contract_id": S1_LL_CONTRACT_ID,
        "source_s1li_digest": prior.contract_digest,
        "source_s1lk_digest": source.receipt_digest,
        "source_s1jx_case_record": next(
            row for row in S1_JX_CASE_RECORDS if row[0] == S1_LL_CASE_ID
        ),
        "case_schema": S1_LL_CASE_SCHEMA,
        "case_payload": tuple(_case_payload().items()),
        "case_output_digest": S1_LL_CASE_OUTPUT_DIGEST,
        "replica_count": 3,
        "sequence_count_per_refinement": 2,
        "checkpoint_count_per_refinement": 4,
        "component_count_per_refinement": 8,
        "primary_refinement": 4,
        "comparison_digest_count": len(set(S1_LK_TARGET_COMPARISON_DIGESTS)),
        "distinct_provenance_digest_count": len(set(S1_LK_TARGET_OUTPUT_DIGESTS)),
        "residual_block_count": 2,
        "residual_component_count": len(residual_values),
        "checkpoint_parent_identity_valid": True,
        "independent_sequences_bit_identical_within_refinement": True,
        "refinement_outputs_distinct": True,
        "all_primary_components_zero": all(value == 0.0 for value in _COMPONENTS[4]),
        "all_refinement_residuals_zero": all(value == 0.0 for value in residual_values),
        "case_record_composed": True,
        "new_replicas_executed": 0,
        "new_interval_calls_executed": 0,
        "matrix_24_case_output_published": False,
        "baseline_judgment_present": False,
        "candidate_comparison_present": False,
        "runtime_integration_present": False,
        "c10_selection_authorized_next_stage": True,
        "decision": S1_LL_DECISION,
    }
    return DTS1S1LLB3PIECaseOutputContract(
        **values, contract_digest=_digest(values)
    )
