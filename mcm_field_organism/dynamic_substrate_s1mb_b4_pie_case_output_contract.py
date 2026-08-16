"""Static S1-MB complete B4/P_IE C13 case output contract."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_dts1_one_replica_orchestrator import (
    S1_MA_CHECKPOINT_ADAPTER_OUTPUT_DIGESTS,
    S1_MA_CHECKPOINT_FIELD_DIGESTS,
    S1_MA_CHECKPOINT_PRIVATE_STATE_DIGESTS,
    S1_MA_TARGET_COMPARISON_DIGESTS,
    S1_MA_TARGET_COMPONENTS_BY_REFINEMENT,
    S1_MA_TARGET_OUTPUT_DIGESTS,
    S1_MA_TARGET_REPLICA_IDS,
    build_dts1_s1ma_implementation_receipt,
)
from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    S1_JX_CASE_RECORDS,
)
from .dynamic_substrate_s1ly_matrix_completeness_gate import (
    build_dts1_s1ly_matrix_completeness_gate,
)


class DTS1S1MBB4PIECaseOutputContractError(ValueError):
    """Raised when the finite S1-MB C13 case output is weakened."""


S1_MB_CONTRACT_ID = "dynamic-substrate.b4-pie-case-output.s1mb.v1"
S1_MB_SOURCE_S1LY_DIGEST = (
    "9801f7ed7628d0e89e0858521617c34b6eaba52d0f1682274544f54fdd2c5009"
)
S1_MB_SOURCE_S1MA_DIGEST = (
    "24e4fe8c8641b0df2e4d0c3e167883eaa51643a69ea2563d108e0a024220f6a3"
)
S1_MB_CASE_ID = "C13"


def _subtract(left: tuple[float, ...], right: tuple[float, ...]) -> tuple[float, ...]:
    if len(left) != 8 or len(right) != 8:
        raise DTS1S1MBB4PIECaseOutputContractError(
            "C13 residual inputs must each contain eight components"
        )
    return tuple(
        0.0 if left_value == right_value else left_value - right_value
        for left_value, right_value in zip(left, right, strict=True)
    )


_COMPONENTS = dict(S1_MA_TARGET_COMPONENTS_BY_REFINEMENT)
S1_MB_REFINEMENT_RESIDUALS = (
    ("r2_minus_r4", _subtract(_COMPONENTS[2], _COMPONENTS[4])),
    ("r4_minus_r8", _subtract(_COMPONENTS[4], _COMPONENTS[8])),
)
S1_MB_CASE_SCHEMA = (
    ("schema_id", "mcm.s1mb.complete-three-refinement-case.v1"),
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
S1_MB_STATUS = "TECHNICALLY_COMPLETE_NO_PIE_BASELINE_OR_CANDIDATE_JUDGMENT"
S1_MB_DECISION = (
    "C13_B4_PIE_THREE_REFINEMENT_CASE_OUTPUT_AND_RESIDUALS_BOUND_FROM_S1MA_RECEIPT_NO_NEW_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _case_payload() -> dict[str, object]:
    return {
        "schema_id": "mcm.s1mb.complete-three-refinement-case.v1",
        "case_id": S1_MB_CASE_ID,
        "model_role": "B4",
        "long_model_role": "B4_F3_LINEAR_COUPLED",
        "profile_block": "P_IE_CAUSAL_TWO_SUBSTEP",
        "node_count": 2,
        "component_count": 8,
        "replica_ids": S1_MA_TARGET_REPLICA_IDS,
        "replica_output_digests": S1_MA_TARGET_OUTPUT_DIGESTS,
        "refinement_comparison_digests": S1_MA_TARGET_COMPARISON_DIGESTS,
        "components_by_refinement": S1_MA_TARGET_COMPONENTS_BY_REFINEMENT,
        "primary_refinement": 4,
        "primary_components": _COMPONENTS[4],
        "refinement_residuals": S1_MB_REFINEMENT_RESIDUALS,
        "checkpoint_field_digests": S1_MA_CHECKPOINT_FIELD_DIGESTS,
        "checkpoint_private_state_digests": S1_MA_CHECKPOINT_PRIVATE_STATE_DIGESTS,
        "checkpoint_adapter_output_digests": S1_MA_CHECKPOINT_ADAPTER_OUTPUT_DIGESTS,
        "checkpoint_parent_identity_valid": True,
        "independent_sequences_bit_identical_within_refinement": True,
        "refinement_outputs_distinct": True,
        "status": S1_MB_STATUS,
    }


S1_MB_CASE_OUTPUT_DIGEST = _digest(_case_payload())


@dataclass(frozen=True, slots=True)
class DTS1S1MBB4PIECaseOutputContract:
    contract_id: str
    source_s1ly_digest: str
    source_s1ma_digest: str
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
    matrix_gate_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        expected_case = next(
            row for row in S1_JX_CASE_RECORDS if row[0] == S1_MB_CASE_ID
        )
        if (
            self.contract_id != S1_MB_CONTRACT_ID
            or self.source_s1ly_digest != S1_MB_SOURCE_S1LY_DIGEST
            or self.source_s1ma_digest != S1_MB_SOURCE_S1MA_DIGEST
            or self.source_s1jx_case_record != expected_case
            or self.case_schema != S1_MB_CASE_SCHEMA
            or self.case_payload != tuple(_case_payload().items())
            or self.case_output_digest != S1_MB_CASE_OUTPUT_DIGEST
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
            or self.matrix_gate_authorized_next_stage is not True
            or self.decision != S1_MB_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1MBB4PIECaseOutputContractError(
                "S1-MB weakened the complete C13 case output"
            )


def build_dts1_s1mb_b4_pie_case_output_contract(
) -> DTS1S1MBB4PIECaseOutputContract:
    """Compose C13 and its residuals without executing a replica."""

    prior = build_dts1_s1ly_matrix_completeness_gate()
    source = build_dts1_s1ma_implementation_receipt()
    if (
        prior.contract_digest != S1_MB_SOURCE_S1LY_DIGEST
        or source.receipt_digest != S1_MB_SOURCE_S1MA_DIGEST
        or source.target_output_digests != S1_MA_TARGET_OUTPUT_DIGESTS
        or source.target_comparison_digests != S1_MA_TARGET_COMPARISON_DIGESTS
        or source.target_components_by_refinement
        != S1_MA_TARGET_COMPONENTS_BY_REFINEMENT
        or source.checkpoint_field_digests != S1_MA_CHECKPOINT_FIELD_DIGESTS
        or source.checkpoint_private_state_digests
        != S1_MA_CHECKPOINT_PRIVATE_STATE_DIGESTS
        or source.checkpoint_adapter_output_digests
        != S1_MA_CHECKPOINT_ADAPTER_OUTPUT_DIGESTS
        or source.case_output_composed is not False
        or source.matrix_case_output_published is not False
        or source.baseline_or_candidate_judgment_present is not False
    ):
        raise DTS1S1MBB4PIECaseOutputContractError(
            "S1-LY matrix gate or S1-MA output source differs"
        )
    residual_values = tuple(
        value for _, values in S1_MB_REFINEMENT_RESIDUALS for value in values
    )
    values = {
        "contract_id": S1_MB_CONTRACT_ID,
        "source_s1ly_digest": prior.contract_digest,
        "source_s1ma_digest": source.receipt_digest,
        "source_s1jx_case_record": next(
            row for row in S1_JX_CASE_RECORDS if row[0] == S1_MB_CASE_ID
        ),
        "case_schema": S1_MB_CASE_SCHEMA,
        "case_payload": tuple(_case_payload().items()),
        "case_output_digest": S1_MB_CASE_OUTPUT_DIGEST,
        "replica_count": 3,
        "sequence_count_per_refinement": 2,
        "checkpoint_count_per_refinement": 4,
        "component_count_per_refinement": 8,
        "primary_refinement": 4,
        "comparison_digest_count": len(set(S1_MA_TARGET_COMPARISON_DIGESTS)),
        "distinct_provenance_digest_count": len(set(S1_MA_TARGET_OUTPUT_DIGESTS)),
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
        "matrix_gate_authorized_next_stage": True,
        "decision": S1_MB_DECISION,
    }
    return DTS1S1MBB4PIECaseOutputContract(
        **values, contract_digest=_digest(values)
    )
