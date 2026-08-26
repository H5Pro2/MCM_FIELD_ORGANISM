"""Static S1-LP complete B3/P_IH C10 case output contract."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_dts1_one_replica_orchestrator import (
    S1_LO_CHECKPOINT_PRIVATE_STATE_DIGESTS,
    S1_LO_TARGET_COMPARISON_DIGESTS,
    S1_LO_TARGET_COMPONENTS_BY_REFINEMENT,
    S1_LO_TARGET_OUTPUT_DIGESTS,
    S1_LO_TARGET_REPLICA_IDS,
    S1_LO_DECISION,
    build_dts1_s1lo_implementation_receipt,
)
from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    S1_JX_CASE_RECORDS,
)
from .dynamic_substrate_s1lm_b3_pih_case_selection_contract import (
    S1_LM_CASE_ID,
    build_dts1_s1lm_b3_pih_case_selection_contract,
)
from .dynamic_substrate_s1ln_b3_pih_resource_anatomy_contract import (
    S1_LN_CASE_ID,
    build_dts1_s1ln_b3_pih_resource_anatomy_contract,
)


class DTS1S1LPB3PIHCaseOutputContractError(ValueError):
    """Raised when the static S1-LP C10 case output is weakened."""


S1_LP_CONTRACT_ID = "dynamic-substrate.b3-pih-case-output.s1lp.v1"
S1_LP_SOURCE_S1LM_DIGEST = (
    "6a5217af1426462bcf910bfdb94ae19813b8fdd2de3b1c9db6c77f577506678b"
)
S1_LP_SOURCE_S1LO_DIGEST = (
    "f2a6e61e57e003d28908280b8c3d7b694b8cef1f6a50d179b3218e7600c89e85"
)
S1_LP_CASE_ID = S1_LM_CASE_ID
S1_LP_SOURCE_S1LN_DIGEST = (
    "f105fcc8601c34f701676dc966abffeb52ffc71846ce95c6f2b9d33057a00c4c"
)
S1_LP_CASE_SCHEMA = (
    ("schema_id", "mcm.s1lp.complete-three-refinement-case.v1"),
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
            "checkpoint_private_state_digests",
            "checkpoint_parent_identity_valid",
            "status",
            "case_output_digest",
        ),
    ),
    ("publication", "one-complete-case-record-or-one-error-with-no-partial-value"),
)
S1_LP_STATUS = "TECHNICALLY_COMPLETE_NO_BASELINE_OR_CANDIDATE_JUDGMENT"
S1_LP_DECISION = (
    "C10_B3_PIH_THREE_REFINEMENT_CASE_OUTPUT_BOUND_FROM_S1LO_RECEIPT_NO_NEW_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _case_payload() -> dict[str, object]:
    return {
        "schema_id": "mcm.s1lp.complete-three-refinement-case.v1",
        "case_id": S1_LP_CASE_ID,
        "model_role": "B3",
        "long_model_role": "B3_F3_LOCAL_LEAKY",
        "profile_block": "P_IH_ATTENUATION",
        "node_count": 2,
        "component_count": 8,
        "replica_ids": S1_LO_TARGET_REPLICA_IDS,
        "replica_output_digests": S1_LO_TARGET_OUTPUT_DIGESTS,
        "refinement_comparison_digests": S1_LO_TARGET_COMPARISON_DIGESTS,
        "components_by_refinement": S1_LO_TARGET_COMPONENTS_BY_REFINEMENT,
        "primary_refinement": 4,
        "primary_components": dict(S1_LO_TARGET_COMPONENTS_BY_REFINEMENT)[4],
        "checkpoint_private_state_digests": S1_LO_CHECKPOINT_PRIVATE_STATE_DIGESTS,
        "checkpoint_parent_identity_valid": True,
        "status": S1_LP_STATUS,
    }


S1_LP_CASE_OUTPUT_DIGEST = _digest(_case_payload())


@dataclass(frozen=True, slots=True)
class DTS1S1LPB3PIHCaseOutputContract:
    contract_id: str
    source_s1lm_digest: str
    source_s1ln_digest: str
    source_s1lo_receipt_digest: str
    source_s1jx_case_record: tuple[object, ...]
    source_s1lo_decision: str
    case_schema: tuple[tuple[str, object], ...]
    case_payload: tuple[tuple[str, object], ...]
    case_output_digest: str
    replica_count: int
    checkpoint_count_per_refinement: int
    component_count_per_refinement: int
    primary_refinement: int
    comparison_digest_count: int
    distinct_provenance_digest_count: int
    distinct_private_state_digest_count: int
    checkpoint_parent_identity_valid: bool
    all_components_bit_identical: bool
    primary_components_nonzero: bool
    case_record_composed: bool
    new_replicas_executed: int
    new_interval_calls_executed: int
    matrix_24_case_output_published: bool
    baseline_judgment_present: bool
    candidate_comparison_present: bool
    runtime_integration_present: bool
    next_case_output_contract_authorized: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        expected_case = next(
            row for row in S1_JX_CASE_RECORDS if row[0] == S1_LP_CASE_ID
        )
        components = tuple(value for _, value in S1_LO_TARGET_COMPONENTS_BY_REFINEMENT)
        if (
            self.contract_id != S1_LP_CONTRACT_ID
            or self.source_s1lm_digest != S1_LP_SOURCE_S1LM_DIGEST
            or self.source_s1ln_digest != S1_LP_SOURCE_S1LN_DIGEST
            or self.source_s1lo_receipt_digest != S1_LP_SOURCE_S1LO_DIGEST
            or self.source_s1jx_case_record != expected_case
            or self.source_s1lo_decision != S1_LO_DECISION
            or self.case_schema != S1_LP_CASE_SCHEMA
            or self.case_payload != tuple(_case_payload().items())
            or self.case_output_digest != S1_LP_CASE_OUTPUT_DIGEST
            or (self.replica_count, self.checkpoint_count_per_refinement, self.component_count_per_refinement) != (3, 3, 8)
            or (self.primary_refinement, self.comparison_digest_count, self.distinct_provenance_digest_count) != (4, 3, 3)
            or self.distinct_private_state_digest_count != 3
            or self.checkpoint_parent_identity_valid is not True
            or self.all_components_bit_identical is not (len(set(components)) == 1)
            or self.primary_components_nonzero is not True
            or self.case_record_composed is not True
            or (self.new_replicas_executed, self.new_interval_calls_executed) != (0, 0)
            or self.matrix_24_case_output_published is not False
            or self.baseline_judgment_present is not False
            or self.candidate_comparison_present is not False
            or self.runtime_integration_present is not False
            or self.next_case_output_contract_authorized is not False
            or self.decision != S1_LP_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1LPB3PIHCaseOutputContractError(
                "S1-LP weakened the complete C10 case output"
            )


def build_dts1_s1lp_b3_pih_case_output_contract(
) -> DTS1S1LPB3PIHCaseOutputContract:
    """Compose C10 from bound LM/LN selection and LO implementation without execution."""

    source_lm = build_dts1_s1lm_b3_pih_case_selection_contract()
    source_ln = build_dts1_s1ln_b3_pih_resource_anatomy_contract()
    source_lo = build_dts1_s1lo_implementation_receipt()
    if (
        source_lm.contract_digest != S1_LP_SOURCE_S1LM_DIGEST
        or source_ln.contract_digest != S1_LP_SOURCE_S1LN_DIGEST
        or source_lo.receipt_digest != S1_LP_SOURCE_S1LO_DIGEST
        or source_lo.decision != S1_LO_DECISION
        or source_lm.target_case_record[0] != S1_LP_CASE_ID
        or source_lm.target_case_record[1] != "B3"
        or source_lm.target_case_record[2] != "B3_F3_LOCAL_LEAKY"
        or not source_lm.case_selected
        or source_lm.runner_extension_implemented is not False
        or source_lm.exact_implementation_execution_authorized_next_stage is not True
        or source_ln.candidate_case != S1_LN_CASE_ID
        or source_ln.local_identity_bound is not True
        or source_ln.global_identity_bound is not True
        or source_ln.execution_permitted is not False
        or source_ln.field_steps_executed != 0
    ):
        raise DTS1S1LPB3PIHCaseOutputContractError(
            "S1-LP source contracts are not the expected static boundary"
        )
    values = {
        "contract_id": S1_LP_CONTRACT_ID,
        "source_s1lm_digest": source_lm.contract_digest,
        "source_s1ln_digest": source_ln.contract_digest,
        "source_s1lo_receipt_digest": source_lo.receipt_digest,
        "source_s1jx_case_record": next(
            row for row in S1_JX_CASE_RECORDS if row[0] == S1_LP_CASE_ID
        ),
        "source_s1lo_decision": source_lo.decision,
        "case_schema": S1_LP_CASE_SCHEMA,
        "case_payload": tuple(_case_payload().items()),
        "case_output_digest": S1_LP_CASE_OUTPUT_DIGEST,
        "replica_count": 3,
        "checkpoint_count_per_refinement": 3,
        "component_count_per_refinement": 8,
        "primary_refinement": 4,
        "comparison_digest_count": 3,
        "distinct_provenance_digest_count": 3,
        "distinct_private_state_digest_count": len(set(S1_LO_CHECKPOINT_PRIVATE_STATE_DIGESTS)),
        "checkpoint_parent_identity_valid": True,
        "all_components_bit_identical": len(set(value for _, value in S1_LO_TARGET_COMPONENTS_BY_REFINEMENT)) == 1,
        "primary_components_nonzero": all(
            value != 0.0
            for value in dict(S1_LO_TARGET_COMPONENTS_BY_REFINEMENT)[4]
        ),
        "case_record_composed": True,
        "new_replicas_executed": 0,
        "new_interval_calls_executed": 0,
        "matrix_24_case_output_published": False,
        "baseline_judgment_present": False,
        "candidate_comparison_present": False,
        "runtime_integration_present": False,
        "next_case_output_contract_authorized": False,
        "decision": S1_LP_DECISION,
    }
    return DTS1S1LPB3PIHCaseOutputContract(
        **values, contract_digest=_digest(values)
    )
