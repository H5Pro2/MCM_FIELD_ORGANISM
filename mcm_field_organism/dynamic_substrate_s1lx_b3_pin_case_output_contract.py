"""Static S1-LX complete B3/P_IN C12 case output contract."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_dts1_one_replica_orchestrator import (
    S1_LW_CHECKPOINT_ADAPTER_OUTPUT_DIGESTS,
    S1_LW_CHECKPOINT_FIELD_DIGESTS,
    S1_LW_CHECKPOINT_PRIVATE_STATE_DIGESTS,
    S1_LW_DECISION,
    S1_LW_TARGET_COMPARISON_DIGESTS,
    S1_LW_TARGET_COMPONENTS_BY_REFINEMENT,
    S1_LW_TARGET_OUTPUT_DIGESTS,
    S1_LW_TARGET_REPLICA_IDS,
    build_dts1_s1lw_implementation_receipt,
)
from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    S1_JX_CASE_RECORDS,
)
from .dynamic_substrate_s1lv_b3_pin_case_selection_contract import (
    S1_LV_CASE_ID,
    build_dts1_s1lv_b3_pin_case_selection_contract,
)


class DTS1S1LXB3PINCaseOutputContractError(ValueError):
    """Raised when the static S1-LX C12 case output is weakened."""


S1_LX_CONTRACT_ID = "dynamic-substrate.b3-pin-case-output.s1lx.v1"
S1_LX_SOURCE_S1LV_DIGEST = (
    "bc11f71be2ab76f19f14b9846061895059db5dd926cb020d8aae3be84773da44"
)
S1_LX_SOURCE_S1LW_DIGEST = (
    "9e608a0e25e3ba3b9de18f5de8009544d372aa5517ed46e8d194da73fc87c4b4"
)
S1_LX_CASE_ID = S1_LV_CASE_ID


def _subtract(left: tuple[float, ...], right: tuple[float, ...]) -> tuple[float, ...]:
    if len(left) != 6 or len(right) != 6:
        raise DTS1S1LXB3PINCaseOutputContractError(
            "C12 residual inputs must each contain six components"
        )
    return tuple(
        0.0 if left_value == right_value else left_value - right_value
        for left_value, right_value in zip(left, right, strict=True)
    )


_COMPONENTS = dict(S1_LW_TARGET_COMPONENTS_BY_REFINEMENT)
S1_LX_REFINEMENT_RESIDUALS = (
    ("r2_minus_r4", _subtract(_COMPONENTS[2], _COMPONENTS[4])),
    ("r4_minus_r8", _subtract(_COMPONENTS[4], _COMPONENTS[8])),
)
S1_LX_CASE_SCHEMA = (
    ("schema_id", "mcm.s1lx.complete-three-refinement-case.v1"),
    (
        "fields",
        (
            "schema_id",
            "case_id",
            "model_role",
            "long_model_role",
            "profile_block",
            "node_count",
            "component_count",
            "replica_ids",
            "replica_output_digests",
            "refinement_comparison_digests",
            "components_by_refinement",
            "primary_refinement",
            "primary_components",
            "refinement_residuals",
            "checkpoint_field_digests",
            "checkpoint_private_state_digests",
            "checkpoint_adapter_output_digests",
            "checkpoint_parent_identity_valid",
            "independent_sequence_terminals_bit_identical",
            "refinement_outputs_distinct",
            "status",
            "case_output_digest",
        ),
    ),
    ("publication", "one-complete-case-record-or-one-error-with-no-partial-value"),
)
S1_LX_STATUS = "TECHNICALLY_COMPLETE_NO_PIN_BASELINE_OR_CANDIDATE_JUDGMENT"
S1_LX_DECISION = (
    "C12_B3_PIN_THREE_REFINEMENT_CASE_OUTPUT_AND_RESIDUALS_BOUND_FROM_S1LW_RECEIPT_NO_NEW_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _case_payload() -> dict[str, object]:
    return {
        "schema_id": "mcm.s1lx.complete-three-refinement-case.v1",
        "case_id": S1_LX_CASE_ID,
        "model_role": "B3",
        "long_model_role": "B3_F3_LOCAL_LEAKY",
        "profile_block": "P_IN_RELEASE_REUSE",
        "node_count": 3,
        "component_count": 6,
        "replica_ids": S1_LW_TARGET_REPLICA_IDS,
        "replica_output_digests": S1_LW_TARGET_OUTPUT_DIGESTS,
        "refinement_comparison_digests": S1_LW_TARGET_COMPARISON_DIGESTS,
        "components_by_refinement": S1_LW_TARGET_COMPONENTS_BY_REFINEMENT,
        "primary_refinement": 4,
        "primary_components": _COMPONENTS[4],
        "refinement_residuals": S1_LX_REFINEMENT_RESIDUALS,
        "checkpoint_field_digests": S1_LW_CHECKPOINT_FIELD_DIGESTS,
        "checkpoint_private_state_digests": S1_LW_CHECKPOINT_PRIVATE_STATE_DIGESTS,
        "checkpoint_adapter_output_digests": S1_LW_CHECKPOINT_ADAPTER_OUTPUT_DIGESTS,
        "checkpoint_parent_identity_valid": True,
        "independent_sequence_terminals_bit_identical": True,
        "refinement_outputs_distinct": True,
        "status": S1_LX_STATUS,
    }


S1_LX_CASE_OUTPUT_DIGEST = _digest(_case_payload())


@dataclass(frozen=True, slots=True)
class DTS1S1LXB3PINCaseOutputContract:
    contract_id: str
    source_s1lv_digest: str
    source_s1lw_digest: str
    source_s1jx_case_record: tuple[object, ...]
    source_s1lw_decision: str
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
    independent_sequence_terminals_bit_identical: bool
    refinement_outputs_distinct: bool
    all_primary_components_zero: bool
    primary_components_nonzero: bool
    all_refinement_residuals_zero: bool
    case_record_composed: bool
    new_replicas_executed: int
    new_interval_calls_executed: int
    matrix_24_case_output_published: bool
    baseline_judgment_present: bool
    candidate_comparison_present: bool
    runtime_integration_present: bool
    c13_selection_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        expected_case = next(
            row for row in S1_JX_CASE_RECORDS if row[0] == S1_LX_CASE_ID
        )
        residual_values = tuple(
            value for _, values in S1_LX_REFINEMENT_RESIDUALS for value in values
        )
        if (
            self.contract_id != S1_LX_CONTRACT_ID
            or self.source_s1lv_digest != S1_LX_SOURCE_S1LV_DIGEST
            or self.source_s1lw_digest != S1_LX_SOURCE_S1LW_DIGEST
            or self.source_s1jx_case_record != expected_case
            or self.source_s1lw_decision != S1_LW_DECISION
            or self.case_schema != S1_LX_CASE_SCHEMA
            or self.case_payload != tuple(_case_payload().items())
            or self.case_output_digest != S1_LX_CASE_OUTPUT_DIGEST
            or (self.replica_count, self.sequence_count_per_refinement) != (3, 2)
            or (self.checkpoint_count_per_refinement, self.component_count_per_refinement) != (2, 6)
            or (self.primary_refinement, self.comparison_digest_count) != (4, 3)
            or self.distinct_provenance_digest_count != 3
            or (self.residual_block_count, self.residual_component_count) != (2, 12)
            or self.checkpoint_parent_identity_valid is not True
            or self.independent_sequence_terminals_bit_identical is not True
            or self.refinement_outputs_distinct is not True
            or self.all_primary_components_zero is not True
            or self.primary_components_nonzero is not False
            or self.all_refinement_residuals_zero is not True
            or self.case_record_composed is not True
            or (self.new_replicas_executed, self.new_interval_calls_executed) != (0, 0)
            or self.matrix_24_case_output_published is not False
            or self.baseline_judgment_present is not False
            or self.candidate_comparison_present is not False
            or self.runtime_integration_present is not False
            or self.c13_selection_authorized_next_stage is not True
            or self.decision != S1_LX_DECISION
            or self.contract_digest != _digest(payload)
            or any(value != 0.0 for value in residual_values)
        ):
            raise DTS1S1LXB3PINCaseOutputContractError(
                "S1-LX weakened the complete C12 case output"
            )


def build_dts1_s1lx_b3_pin_case_output_contract(
) -> DTS1S1LXB3PINCaseOutputContract:
    """Compose C12 and its residuals without executing a replica."""

    source_lv = build_dts1_s1lv_b3_pin_case_selection_contract()
    source_lw = build_dts1_s1lw_implementation_receipt()
    if (
        source_lv.contract_digest != S1_LX_SOURCE_S1LV_DIGEST
        or source_lw.receipt_digest != S1_LX_SOURCE_S1LW_DIGEST
        or source_lw.decision != S1_LW_DECISION
        or source_lv.target_case_record[0] != S1_LX_CASE_ID
        or source_lv.target_case_record[1] != "B3"
        or source_lv.target_case_record[2] != "B3_F3_LOCAL_LEAKY"
        or source_lv.target_case_record[3] != "P_IN_RELEASE_REUSE"
        or not source_lv.case_selected
        or source_lv.runner_extension_implemented is not False
        or source_lv.exact_implementation_execution_authorized_next_stage is not True
        or source_lw.case_output_composed is not False
        or source_lw.matrix_case_output_published is not False
        or source_lw.release_reuse_or_baseline_judgment_present is not False
    ):
        raise DTS1S1LXB3PINCaseOutputContractError(
            "S1-LX source contracts are not the expected static boundary"
        )
    residual_values = tuple(
        value for _, values in S1_LX_REFINEMENT_RESIDUALS for value in values
    )
    values = {
        "contract_id": S1_LX_CONTRACT_ID,
        "source_s1lv_digest": source_lv.contract_digest,
        "source_s1lw_digest": source_lw.receipt_digest,
        "source_s1jx_case_record": next(
            row for row in S1_JX_CASE_RECORDS if row[0] == S1_LX_CASE_ID
        ),
        "source_s1lw_decision": source_lw.decision,
        "case_schema": S1_LX_CASE_SCHEMA,
        "case_payload": tuple(_case_payload().items()),
        "case_output_digest": S1_LX_CASE_OUTPUT_DIGEST,
        "replica_count": 3,
        "sequence_count_per_refinement": 2,
        "checkpoint_count_per_refinement": 2,
        "component_count_per_refinement": 6,
        "primary_refinement": 4,
        "comparison_digest_count": len(set(S1_LW_TARGET_COMPARISON_DIGESTS)),
        "distinct_provenance_digest_count": len(set(S1_LW_TARGET_OUTPUT_DIGESTS)),
        "residual_block_count": 2,
        "residual_component_count": len(residual_values),
        "checkpoint_parent_identity_valid": True,
        "independent_sequence_terminals_bit_identical": all(
            row[0] == row[1]
            for rows in (
                S1_LW_CHECKPOINT_FIELD_DIGESTS,
                S1_LW_CHECKPOINT_PRIVATE_STATE_DIGESTS,
                S1_LW_CHECKPOINT_ADAPTER_OUTPUT_DIGESTS,
            )
            for row in rows
        ),
        "refinement_outputs_distinct": True,
        "all_primary_components_zero": all(value == 0.0 for value in _COMPONENTS[4]),
        "primary_components_nonzero": all(value != 0.0 for value in _COMPONENTS[4]),
        "all_refinement_residuals_zero": all(value == 0.0 for value in residual_values),
        "case_record_composed": True,
        "new_replicas_executed": 0,
        "new_interval_calls_executed": 0,
        "matrix_24_case_output_published": False,
        "baseline_judgment_present": False,
        "candidate_comparison_present": False,
        "runtime_integration_present": False,
        "c13_selection_authorized_next_stage": True,
        "decision": S1_LX_DECISION,
    }
    return DTS1S1LXB3PINCaseOutputContract(
        **values, contract_digest=_digest(values)
    )
