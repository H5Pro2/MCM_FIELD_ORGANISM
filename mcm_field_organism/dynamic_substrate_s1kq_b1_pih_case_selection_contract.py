"""Static S1-KQ selection contract for the finite B1/P_IH case."""

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
from .dynamic_substrate_s1kp_b2_pie_case_output_contract import (
    build_dts1_s1kp_b2_pie_case_output_contract,
)


class DTS1S1KQB1PIHCaseSelectionContractError(ValueError):
    """Raised when the finite S1-KQ case selection is weakened."""


S1_KQ_CONTRACT_ID = "dynamic-substrate.b1-pih-case-selection.s1kq.v1"
S1_KQ_SOURCE_S1KP_DIGEST = (
    "133680fef4e057f5500d4836ee6f47814d37d9133df78fd250bf48df0f84a473"
)
S1_KQ_CASE_ID = "C02"
S1_KQ_SEQUENCE_KEY = "P_IH_A_A_A"
S1_KQ_TARGET_REPLICA_IDS = (
    "B1:P_IH_ATTENUATION:r2",
    "B1:P_IH_ATTENUATION:r4",
    "B1:P_IH_ATTENUATION:r8",
)
S1_KQ_TARGET_CASE_RECORD = next(
    row for row in S1_JX_CASE_RECORDS if row[0] == S1_KQ_CASE_ID
)
S1_KQ_TARGET_REPLICA_RECORDS = tuple(
    row for row in S1_JX_REPLICA_RECORDS if row[0] in S1_KQ_TARGET_REPLICA_IDS
)
S1_KQ_SEQUENCE_RECORD = next(
    row for row in S1_JX_SEQUENCE_RECORDS if row[0] == S1_KQ_SEQUENCE_KEY
)
S1_KQ_FRESH_STATE_RECORD = next(
    row
    for row in S1_JZ_FRESH_STATE_RECORDS
    if row[0] == "B1" and row[1] == "TWO_NODE_OPEN_LINE"
)
S1_KQ_FRESH_FIELD_DIGEST = (
    "389f731c42f91164332fcfda65cc5130d5090db7f03e211736ae0bb6c1ca2f61"
)
S1_KQ_FRESH_PRIVATE_STATE_DIGEST = (
    "871b0308bfebdcc03a27ff0447f46e054aedc253f1a0975bd77bfbb69b3668d9"
)
S1_KQ_FRESH_START_AND_CARRY_RULES = (
    "r2-r4-and-r8-each-start-from-an-independent-corrected-B1-fresh-state",
    "P_IH_A_A_A-starts-once-from-that-refinements-own-fresh-state",
    "complete-field-and-fixed-adapter-private-state-carry-across-all-three-ordered-A-intervals",
    "no-field-private-state-output-or-provenance-carries-between-refinements",
)
S1_KQ_EXECUTION_BUDGET = (
    ("target_replica_count", 3),
    ("interval_calls_per_replica", 3),
    ("maximum_new_interval_calls", 9),
    ("retry_or_repeat_calls", 0),
)
S1_KQ_OUTPUT_ACCEPTANCE_RULES = (
    "each-replica-publishes-one-atomic-mcm.s1jz.complete-replica-output.v2-or-one-error",
    "each-output-has-three-ordered-checkpoints-eight-signed-components-and-three-adapter-diagnostics",
    "every-checkpoint-replica_id-bit-equals-its-parent-output-replica_id",
    "B1-refinement-comparison-digests-must-be-bit-identical-across-r2-r4-r8",
    "complete-output-digests-remain-identity-bearing-and-must-be-distinct",
    "all-three-replicas-must-pass-before-C02-may-be-composed-in-a-later-stage",
)
S1_KQ_SELECTION_RATIONALE = (
    "C02-is-the-next-registered-B1-control-after-complete-C01-and-C05",
    "P_IH-tests-the-registered-three-contact-attenuation-readout-under-the-fixed-adapter",
    "selection-does-not-predict-sign-threshold-baseline-closure-or-candidate-outcome",
)
S1_KQ_FORBIDDEN_SCOPE = (
    "no-runner-initializer-adapter-or-output-implementation",
    "no-replica-interval-retry-or-repeat-execution",
    "no-C02-output-or-24-case-matrix-publication",
    "no-B2-P_IH-or-other-role-profile-selection",
    "no-baseline-candidate-runtime-or-research-judgment",
)
S1_KQ_DECISION = (
    "B1_PIH_C02_SELECTED_THREE_REFINEMENT_DUAL_DIGEST_NINE_CALL_CONTRACT_BOUND_NO_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1KQB1PIHCaseSelectionContract:
    contract_id: str
    source_s1kp_digest: str
    target_case_record: tuple[object, ...]
    target_replica_ids: tuple[str, ...]
    target_replica_records: tuple[tuple[object, ...], ...]
    sequence_record: tuple[object, ...]
    corrected_fresh_state_record: tuple[object, ...]
    fresh_field_digest: str
    fresh_private_state_digest: str
    complete_provenance_digest_role: tuple[tuple[str, object], ...]
    comparison_digest_role: tuple[tuple[str, object], ...]
    corrected_output_schema: tuple[tuple[str, object], ...]
    fresh_start_and_carry_rules: tuple[str, ...]
    execution_budget: tuple[tuple[str, int], ...]
    output_acceptance_rules: tuple[str, ...]
    selection_rationale: tuple[str, ...]
    forbidden_scope: tuple[str, ...]
    target_replica_count: int
    intervals_per_target_replica: int
    checkpoints_per_target_replica: int
    signed_components_per_target_replica: int
    maximum_new_interval_calls: int
    case_selected: bool
    runner_extension_implemented: bool
    target_replicas_executed: int
    interval_calls_executed: int
    case_output_composed: bool
    matrix_24_case_output_published: bool
    baseline_judgment_present: bool
    runtime_integration_present: bool
    exact_implementation_execution_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_KQ_CONTRACT_ID
            or self.source_s1kp_digest != S1_KQ_SOURCE_S1KP_DIGEST
            or self.target_case_record != S1_KQ_TARGET_CASE_RECORD
            or self.target_replica_ids != S1_KQ_TARGET_REPLICA_IDS
            or self.target_replica_records != S1_KQ_TARGET_REPLICA_RECORDS
            or self.sequence_record != S1_KQ_SEQUENCE_RECORD
            or self.corrected_fresh_state_record != S1_KQ_FRESH_STATE_RECORD
            or self.fresh_field_digest != S1_KQ_FRESH_FIELD_DIGEST
            or self.fresh_private_state_digest != S1_KQ_FRESH_PRIVATE_STATE_DIGEST
            or self.complete_provenance_digest_role != S1_KE_COMPLETE_PROVENANCE_DIGEST_ROLE
            or self.comparison_digest_role != S1_KE_COMPARISON_DIGEST_ROLE
            or self.corrected_output_schema != S1_KE_CORRECTED_OUTPUT_SCHEMA
            or self.fresh_start_and_carry_rules != S1_KQ_FRESH_START_AND_CARRY_RULES
            or self.execution_budget != S1_KQ_EXECUTION_BUDGET
            or self.output_acceptance_rules != S1_KQ_OUTPUT_ACCEPTANCE_RULES
            or self.selection_rationale != S1_KQ_SELECTION_RATIONALE
            or self.forbidden_scope != S1_KQ_FORBIDDEN_SCOPE
            or self.target_replica_count != 3
            or self.intervals_per_target_replica != 3
            or self.checkpoints_per_target_replica != 3
            or self.signed_components_per_target_replica != 8
            or self.maximum_new_interval_calls != 9
            or self.case_selected is not True
            or self.runner_extension_implemented is not False
            or self.target_replicas_executed != 0
            or self.interval_calls_executed != 0
            or self.case_output_composed is not False
            or self.matrix_24_case_output_published is not False
            or self.baseline_judgment_present is not False
            or self.runtime_integration_present is not False
            or self.exact_implementation_execution_authorized_next_stage is not True
            or self.decision != S1_KQ_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1KQB1PIHCaseSelectionContractError(
                "S1-KQ weakened the finite B1/P_IH case selection"
            )


def build_dts1_s1kq_b1_pih_case_selection_contract(
) -> DTS1S1KQB1PIHCaseSelectionContract:
    """Select and bind C02 without implementing or executing its replicas."""

    source = build_dts1_s1kp_b2_pie_case_output_contract()
    if (
        source.contract_digest != S1_KQ_SOURCE_S1KP_DIGEST
        or len(S1_KQ_TARGET_REPLICA_RECORDS) != 3
        or tuple(row[0] for row in S1_KQ_TARGET_REPLICA_RECORDS)
        != S1_KQ_TARGET_REPLICA_IDS
        or S1_KQ_SEQUENCE_RECORD[3] != 3
        or S1_KQ_FRESH_STATE_RECORD[6] != S1_KQ_FRESH_FIELD_DIGEST
        or S1_KQ_FRESH_STATE_RECORD[8] != S1_KQ_FRESH_PRIVATE_STATE_DIGEST
    ):
        raise DTS1S1KQB1PIHCaseSelectionContractError(
            "registered C02 evidence or corrected B1 fresh state differs"
        )
    values = {
        "contract_id": S1_KQ_CONTRACT_ID,
        "source_s1kp_digest": source.contract_digest,
        "target_case_record": S1_KQ_TARGET_CASE_RECORD,
        "target_replica_ids": S1_KQ_TARGET_REPLICA_IDS,
        "target_replica_records": S1_KQ_TARGET_REPLICA_RECORDS,
        "sequence_record": S1_KQ_SEQUENCE_RECORD,
        "corrected_fresh_state_record": S1_KQ_FRESH_STATE_RECORD,
        "fresh_field_digest": S1_KQ_FRESH_FIELD_DIGEST,
        "fresh_private_state_digest": S1_KQ_FRESH_PRIVATE_STATE_DIGEST,
        "complete_provenance_digest_role": S1_KE_COMPLETE_PROVENANCE_DIGEST_ROLE,
        "comparison_digest_role": S1_KE_COMPARISON_DIGEST_ROLE,
        "corrected_output_schema": S1_KE_CORRECTED_OUTPUT_SCHEMA,
        "fresh_start_and_carry_rules": S1_KQ_FRESH_START_AND_CARRY_RULES,
        "execution_budget": S1_KQ_EXECUTION_BUDGET,
        "output_acceptance_rules": S1_KQ_OUTPUT_ACCEPTANCE_RULES,
        "selection_rationale": S1_KQ_SELECTION_RATIONALE,
        "forbidden_scope": S1_KQ_FORBIDDEN_SCOPE,
        "target_replica_count": 3,
        "intervals_per_target_replica": 3,
        "checkpoints_per_target_replica": 3,
        "signed_components_per_target_replica": 8,
        "maximum_new_interval_calls": 9,
        "case_selected": True,
        "runner_extension_implemented": False,
        "target_replicas_executed": 0,
        "interval_calls_executed": 0,
        "case_output_composed": False,
        "matrix_24_case_output_published": False,
        "baseline_judgment_present": False,
        "runtime_integration_present": False,
        "exact_implementation_execution_authorized_next_stage": True,
        "decision": S1_KQ_DECISION,
    }
    return DTS1S1KQB1PIHCaseSelectionContract(
        **values, contract_digest=_digest(values)
    )
