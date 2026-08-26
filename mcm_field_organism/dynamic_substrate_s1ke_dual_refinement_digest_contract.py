"""Static S1-KE overlay contract for dual refinement digest roles."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1kd_refinement_digest_precheck import (
    build_dts1_s1kd_refinement_digest_precheck,
)
from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    build_dts1_s1jx_sequence_carry_orchestration_contract,
)
from .dynamic_substrate_s1jz_finite_orchestrator_api_contract import (
    build_dts1_s1jz_finite_orchestrator_api_contract,
)


class DTS1S1KEDualRefinementDigestContractError(ValueError):
    """Raised when the S1-KE dual-digest contract is weakened."""


S1_KE_CONTRACT_ID = "dynamic-substrate.dual-refinement-digest-contract.s1ke.v1"
S1_KE_SOURCE_S1KD_DIGEST = (
    "fa51056bfaa3a916a3adec45697cfeb069d4009a557405e55ea299673bf0611f"
)
S1_KE_SOURCE_S1JX_DIGEST = (
    "4bbf3bfb4997fe7e5ad3364276f127d6a8eb53c6b2452c0b4cac387e097cb5a8"
)
S1_KE_SOURCE_S1JZ_DIGEST = (
    "83a5c6248d0dca0e0ba2461bbc6c0f76470a5af1b21ac89049238f1256380079"
)
S1_KE_COMPLETE_PROVENANCE_DIGEST_ROLE = (
    ("name", "output_digest"),
    ("domain", "complete-identity-bearing-replica-output-excluding-only-output_digest"),
    ("purpose", "provenance-and-tamper-evidence"),
    ("cross_refinement_equality_required", False),
)
S1_KE_COMPARISON_DIGEST_ROLE = (
    ("name", "refinement_comparison_digest"),
    ("schema_id", "mcm.s1ke.refinement-comparison-content.v1"),
    ("purpose", "identity-neutral-bit-comparison-across-r2-r4-r8"),
    ("cross_refinement_equality_required_for_B1_B2", True),
)
S1_KE_TOP_LEVEL_EXCLUSIONS = (
    ("replica_id", "refinement-specific-control-identity"),
    ("refinement", "refinement-specific-control-identity"),
    ("output_digest", "derived-complete-provenance-digest"),
    ("refinement_comparison_digest", "derived-self-digest"),
)
S1_KE_CHECKPOINT_EXCLUSIONS = (
    ("replica_id", "refinement-specific-control-identity"),
)
S1_KE_COMPARISON_PAYLOAD_SCHEMA = (
    ("schema_id", "mcm.s1ke.refinement-comparison-content.v1"),
    ("fields", (
        "schema_id",
        "source_output_schema_id",
        "model_role",
        "profile_block",
        "sequence_digests",
        "checkpoints",
        "signed_components",
        "adapter_diagnostics",
    )),
    ("checkpoint_fields", (
        "schema_id",
        "sequence_key",
        "sequence_digest",
        "ordinal",
        "interval_digest",
        "node_ids",
        "activation",
        "afterimage",
        "complete_field_digest",
        "private_state_digest",
        "adapter_output_digest",
    )),
    ("top_level_exclusions", S1_KE_TOP_LEVEL_EXCLUSIONS),
    ("checkpoint_exclusions", S1_KE_CHECKPOINT_EXCLUSIONS),
    ("ordering", "preserve-exact-S1-JZ-sequence-checkpoint-component-and-diagnostic-order"),
    ("canonicalization", "reuse-exact-S1-JZ-canonical-digest-rules"),
)
S1_KE_CORRECTED_OUTPUT_SCHEMA = (
    ("schema_id", "mcm.s1jz.complete-replica-output.v2"),
    ("fields", (
        "schema_id",
        "replica_id",
        "model_role",
        "profile_block",
        "refinement",
        "sequence_digests",
        "checkpoints",
        "signed_components",
        "adapter_diagnostics",
        "refinement_comparison_digest",
        "output_digest",
    )),
    ("output_digest", "covers-all-fields-except-output_digest-including-refinement_comparison_digest"),
    ("refinement_comparison_digest", "digest-of-exact-S1-KE-comparison-payload"),
    ("publication", "one-complete-output-with-both-digests-or-one-error-with-no-partial-value"),
)
S1_KE_CORRECTED_REFINEMENT_RULES = (
    "B1-and-B2-require-bit-identical-refinement_comparison_digest-across-r2-r4-r8",
    "B1-and-B2-complete-output-digests-remain-identity-bearing-and-need-not-be-equal-across-refinements",
    "B3-through-B6-retain-complete-signed-r2-minus-r4-and-r4-minus-r8-component-residuals",
    "no-numeric-checkpoint-private-state-adapter-output-component-or-diagnostic-content-is-excluded-from-comparison",
)
S1_KE_DECISION = (
    "DUAL_PROVENANCE_AND_IDENTITY_NEUTRAL_REFINEMENT_DIGEST_ROLES_BOUND_NO_RUNNER_CHANGE_OR_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _synthetic_records() -> tuple[tuple[str, int, str, str], ...]:
    checkpoint_content = {
        "schema_id": "mcm.s1jz.replica-checkpoint.v1",
        "sequence_key": "P_IE_F_HIGH",
        "sequence_digest": "1" * 64,
        "ordinal": 1,
        "interval_digest": "2" * 64,
        "node_ids": ("node-a", "node-b"),
        "activation": (0.25, -0.25),
        "afterimage": (0.1, -0.1),
        "complete_field_digest": "3" * 64,
        "private_state_digest": "4" * 64,
        "adapter_output_digest": "5" * 64,
    }
    comparison_payload = {
        "schema_id": "mcm.s1ke.refinement-comparison-content.v1",
        "source_output_schema_id": "mcm.s1jz.complete-replica-output.v2",
        "model_role": "B1",
        "profile_block": "P_IE_CAUSAL_TWO_SUBSTEP",
        "sequence_digests": ("1" * 64, "6" * 64),
        "checkpoints": (checkpoint_content,),
        "signed_components": (0.0,) * 8,
        "adapter_diagnostics": (("P_IE_F_HIGH", 1, (("method_id", "exact-spectral"),)),),
    }
    comparison_digest = _digest(comparison_payload)
    rows = []
    for refinement in (2, 4, 8):
        replica_id = f"B1:P_IE_CAUSAL_TWO_SUBSTEP:r{refinement}"
        checkpoint = {"replica_id": replica_id, **checkpoint_content}
        complete_payload = {
            "schema_id": "mcm.s1jz.complete-replica-output.v2",
            "replica_id": replica_id,
            "model_role": "B1",
            "profile_block": "P_IE_CAUSAL_TWO_SUBSTEP",
            "refinement": refinement,
            "sequence_digests": comparison_payload["sequence_digests"],
            "checkpoints": (checkpoint,),
            "signed_components": comparison_payload["signed_components"],
            "adapter_diagnostics": comparison_payload["adapter_diagnostics"],
            "refinement_comparison_digest": comparison_digest,
        }
        rows.append((replica_id, refinement, _digest(complete_payload), comparison_digest))
    return tuple(rows)


S1_KE_SYNTHETIC_DUAL_DIGEST_RECORDS = _synthetic_records()


@dataclass(frozen=True, slots=True)
class DTS1S1KEDualRefinementDigestContract:
    contract_id: str
    source_s1kd_digest: str
    source_s1jx_digest: str
    source_s1jz_digest: str
    complete_provenance_digest_role: tuple[tuple[str, object], ...]
    comparison_digest_role: tuple[tuple[str, object], ...]
    comparison_payload_schema: tuple[tuple[str, object], ...]
    corrected_output_schema: tuple[tuple[str, object], ...]
    corrected_refinement_rules: tuple[str, ...]
    synthetic_dual_digest_records: tuple[tuple[str, int, str, str], ...]
    distinct_complete_provenance_digest_count: int
    distinct_comparison_digest_count: int
    existing_r2_runner_changed: bool
    r4_r8_runner_implemented: bool
    r4_r8_replicas_executed: int
    interval_calls_executed: int
    complete_matrix_cases_executed: int
    runtime_integration_present: bool
    r2_dual_digest_implementation_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_KE_CONTRACT_ID
            or self.source_s1kd_digest != S1_KE_SOURCE_S1KD_DIGEST
            or self.source_s1jx_digest != S1_KE_SOURCE_S1JX_DIGEST
            or self.source_s1jz_digest != S1_KE_SOURCE_S1JZ_DIGEST
            or self.complete_provenance_digest_role != S1_KE_COMPLETE_PROVENANCE_DIGEST_ROLE
            or self.comparison_digest_role != S1_KE_COMPARISON_DIGEST_ROLE
            or self.comparison_payload_schema != S1_KE_COMPARISON_PAYLOAD_SCHEMA
            or self.corrected_output_schema != S1_KE_CORRECTED_OUTPUT_SCHEMA
            or self.corrected_refinement_rules != S1_KE_CORRECTED_REFINEMENT_RULES
            or self.synthetic_dual_digest_records != S1_KE_SYNTHETIC_DUAL_DIGEST_RECORDS
            or self.distinct_complete_provenance_digest_count != 3
            or self.distinct_comparison_digest_count != 1
            or self.existing_r2_runner_changed is not False
            or self.r4_r8_runner_implemented is not False
            or self.r4_r8_replicas_executed != 0
            or self.interval_calls_executed != 0
            or self.complete_matrix_cases_executed != 0
            or self.runtime_integration_present is not False
            or self.r2_dual_digest_implementation_authorized_next_stage is not True
            or self.decision != S1_KE_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1KEDualRefinementDigestContractError(
                "S1-KE weakened the dual refinement digest contract"
            )


def build_dts1_s1ke_dual_refinement_digest_contract(
) -> DTS1S1KEDualRefinementDigestContract:
    """Bind corrected digest roles without changing or running the runner."""

    kd = build_dts1_s1kd_refinement_digest_precheck()
    jx = build_dts1_s1jx_sequence_carry_orchestration_contract()
    jz = build_dts1_s1jz_finite_orchestrator_api_contract()
    values = {
        "contract_id": S1_KE_CONTRACT_ID,
        "source_s1kd_digest": kd.audit_digest,
        "source_s1jx_digest": jx.contract_digest,
        "source_s1jz_digest": jz.contract_digest,
        "complete_provenance_digest_role": S1_KE_COMPLETE_PROVENANCE_DIGEST_ROLE,
        "comparison_digest_role": S1_KE_COMPARISON_DIGEST_ROLE,
        "comparison_payload_schema": S1_KE_COMPARISON_PAYLOAD_SCHEMA,
        "corrected_output_schema": S1_KE_CORRECTED_OUTPUT_SCHEMA,
        "corrected_refinement_rules": S1_KE_CORRECTED_REFINEMENT_RULES,
        "synthetic_dual_digest_records": S1_KE_SYNTHETIC_DUAL_DIGEST_RECORDS,
        "distinct_complete_provenance_digest_count": len({row[2] for row in S1_KE_SYNTHETIC_DUAL_DIGEST_RECORDS}),
        "distinct_comparison_digest_count": len({row[3] for row in S1_KE_SYNTHETIC_DUAL_DIGEST_RECORDS}),
        "existing_r2_runner_changed": False,
        "r4_r8_runner_implemented": False,
        "r4_r8_replicas_executed": 0,
        "interval_calls_executed": 0,
        "complete_matrix_cases_executed": 0,
        "runtime_integration_present": False,
        "r2_dual_digest_implementation_authorized_next_stage": True,
        "decision": S1_KE_DECISION,
    }
    return DTS1S1KEDualRefinementDigestContract(
        **values, contract_digest=_digest(values)
    )
