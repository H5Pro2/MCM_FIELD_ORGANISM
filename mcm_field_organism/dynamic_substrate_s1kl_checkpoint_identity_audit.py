"""Static S1-KL audit of checkpoint and parent replica identity."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import inspect
import json

from .dynamic_substrate_dts1_one_replica_orchestrator import (
    S1_KC_EXEMPLAR_REPLICA_ID,
    S1_KF_EXEMPLAR_OUTPUT_DIGEST,
    S1_KH_TARGET_OUTPUT_DIGESTS,
    S1_KK_TARGET_OUTPUT_DIGESTS,
    build_dts1_s1kk_implementation_receipt,
    run_dts1_one_replica,
)


class DTS1S1KLCheckpointIdentityAuditError(ValueError):
    """Raised when the finite S1-KL provenance audit is weakened."""


S1_KL_AUDIT_ID = "dynamic-substrate.checkpoint-replica-identity-audit.s1kl.v1"
S1_KL_SOURCE_S1KK_DIGEST = (
    "503a13050c22e4e33e553a4661411868e29b8b2c3e987eee2c3d962daf977e61"
)
S1_KL_RUNNER_SOURCE_DIGEST = (
    "f989d2dc4d46ffca0d1db4314d8be355d6138db50491e1e06a150d3a8eaf2f7a"
)
S1_KL_IDENTITY_INVARIANT = (
    "every-checkpoint-replica_id-must-bit-equal-its-parent-output-replica_id"
)
S1_KL_IDENTITY_RECORDS = (
    (
        "B1:P_IE_CAUSAL_TWO_SUBSTEP:r2", "B1", 4,
        "B1:P_IE_CAUSAL_TWO_SUBSTEP:r2", "B1:P_IE_CAUSAL_TWO_SUBSTEP:r2",
        0, "UNAFFECTED",
    ),
    (
        "B1:P_IE_CAUSAL_TWO_SUBSTEP:r4", "B1", 4,
        "B1:P_IE_CAUSAL_TWO_SUBSTEP:r2", "B1:P_IE_CAUSAL_TWO_SUBSTEP:r4",
        4, "AFFECTED_HISTORICAL_V2",
    ),
    (
        "B1:P_IE_CAUSAL_TWO_SUBSTEP:r8", "B1", 4,
        "B1:P_IE_CAUSAL_TWO_SUBSTEP:r2", "B1:P_IE_CAUSAL_TWO_SUBSTEP:r8",
        4, "AFFECTED_HISTORICAL_V2",
    ),
    *tuple(
        (
            replica_id, "B2", 4, replica_id, replica_id, 0, "UNAFFECTED",
        )
        for replica_id in (
            "B2:P_IE_CAUSAL_TWO_SUBSTEP:r2",
            "B2:P_IE_CAUSAL_TWO_SUBSTEP:r4",
            "B2:P_IE_CAUSAL_TWO_SUBSTEP:r8",
        )
    ),
)
S1_KL_AFFECTED_OUTPUT_DIGESTS = S1_KH_TARGET_OUTPUT_DIGESTS
S1_KL_UNAFFECTED_OUTPUT_DIGESTS = (
    S1_KF_EXEMPLAR_OUTPUT_DIGEST,
    *S1_KK_TARGET_OUTPUT_DIGESTS,
)
S1_KL_IMPACT = (
    "B1-r4-r8-numeric-checkpoints-signed-components-and-adapter-diagnostics-remain-valid",
    "B1-r4-r8-refinement-comparison-content-remains-valid-because-checkpoint-replica_id-is-excluded",
    "B1-r4-r8-complete-v2-output-digests-remain-historical-tamper-evident-records-of-wrong-identity",
    "B1-r4-r8-complete-v2-outputs-are-not-valid-corrected-provenance-records",
    "B1-r2-and-all-B2-P_IE-outputs-are-unaffected",
)
S1_KL_REQUIRED_CORRECTION = (
    "retain-affected-v2-outputs-and-digests-unchanged-as-historical-records",
    "bind-a-versioned-overlay-requiring-checkpoint-and-parent-replica-identity",
    "recompute-only-corrected-B1-r4-r8-complete-provenance-outputs-under-an-eight-call-budget",
    "require-the-existing-B1-refinement-comparison-digest-to-remain-bit-identical",
    "compose-no-corrected-C01-or-C05-until-the-overlay-and-corrected-pair-are-accepted",
)
S1_KL_FORBIDDEN_SCOPE = (
    "no-runner-or-output-schema-change",
    "no-replica-interval-retry-or-repeat-execution",
    "no-historical-output-or-digest-rewrite",
    "no-C01-C05-or-24-case-matrix-publication",
    "no-baseline-candidate-runtime-or-research-judgment",
)
S1_KL_DECISION = (
    "STOP_C01_C05_COMPOSITION_EIGHT_B1_R4_R8_CHECKPOINT_IDENTITIES_REQUIRE_VERSIONED_CORRECTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1KLCheckpointIdentityAudit:
    audit_id: str
    source_s1kk_digest: str
    runner_source_digest: str
    identity_invariant: str
    identity_records: tuple[tuple[object, ...], ...]
    affected_output_digests: tuple[str, str]
    unaffected_output_digests: tuple[str, str, str, str]
    impact: tuple[str, ...]
    required_correction: tuple[str, ...]
    forbidden_scope: tuple[str, ...]
    audited_replica_count: int
    audited_checkpoint_count: int
    affected_replica_count: int
    mismatched_checkpoint_count: int
    numeric_results_invalidated: bool
    comparison_digests_invalidated: bool
    affected_provenance_outputs_valid_as_corrected_records: bool
    historical_records_rewritten: bool
    replicas_executed: int
    interval_calls_executed: int
    case_composition_blocked: bool
    versioned_correction_contract_authorized_next_stage: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "audit_digest"
        }
        if (
            self.audit_id != S1_KL_AUDIT_ID
            or self.source_s1kk_digest != S1_KL_SOURCE_S1KK_DIGEST
            or self.runner_source_digest != S1_KL_RUNNER_SOURCE_DIGEST
            or self.identity_invariant != S1_KL_IDENTITY_INVARIANT
            or self.identity_records != S1_KL_IDENTITY_RECORDS
            or self.affected_output_digests != S1_KL_AFFECTED_OUTPUT_DIGESTS
            or self.unaffected_output_digests != S1_KL_UNAFFECTED_OUTPUT_DIGESTS
            or self.impact != S1_KL_IMPACT
            or self.required_correction != S1_KL_REQUIRED_CORRECTION
            or self.forbidden_scope != S1_KL_FORBIDDEN_SCOPE
            or self.audited_replica_count != 6
            or self.audited_checkpoint_count != 24
            or self.affected_replica_count != 2
            or self.mismatched_checkpoint_count != 8
            or self.numeric_results_invalidated is not False
            or self.comparison_digests_invalidated is not False
            or self.affected_provenance_outputs_valid_as_corrected_records is not False
            or self.historical_records_rewritten is not False
            or self.replicas_executed != 0
            or self.interval_calls_executed != 0
            or self.case_composition_blocked is not True
            or self.versioned_correction_contract_authorized_next_stage is not True
            or self.decision != S1_KL_DECISION
            or self.audit_digest != _digest(payload)
        ):
            raise DTS1S1KLCheckpointIdentityAuditError(
                "S1-KL weakened the checkpoint identity audit"
            )


def build_dts1_s1kl_checkpoint_identity_audit(
) -> DTS1S1KLCheckpointIdentityAudit:
    """Audit bound identity evidence without executing any replica."""

    source = build_dts1_s1kk_implementation_receipt()
    source_digest = hashlib.sha256(
        inspect.getsource(run_dts1_one_replica).encode("utf-8")
    ).hexdigest()
    if (
        source.receipt_digest != S1_KL_SOURCE_S1KK_DIGEST
        or source_digest != S1_KL_RUNNER_SOURCE_DIGEST
        or S1_KC_EXEMPLAR_REPLICA_ID
        != "B1:P_IE_CAUSAL_TWO_SUBSTEP:r2"
    ):
        raise DTS1S1KLCheckpointIdentityAuditError(
            "S1-KK receipt or audited runner source differs"
        )
    values = {
        "audit_id": S1_KL_AUDIT_ID,
        "source_s1kk_digest": source.receipt_digest,
        "runner_source_digest": source_digest,
        "identity_invariant": S1_KL_IDENTITY_INVARIANT,
        "identity_records": S1_KL_IDENTITY_RECORDS,
        "affected_output_digests": S1_KL_AFFECTED_OUTPUT_DIGESTS,
        "unaffected_output_digests": S1_KL_UNAFFECTED_OUTPUT_DIGESTS,
        "impact": S1_KL_IMPACT,
        "required_correction": S1_KL_REQUIRED_CORRECTION,
        "forbidden_scope": S1_KL_FORBIDDEN_SCOPE,
        "audited_replica_count": len(S1_KL_IDENTITY_RECORDS),
        "audited_checkpoint_count": sum(row[2] for row in S1_KL_IDENTITY_RECORDS),
        "affected_replica_count": sum(row[6] == "AFFECTED_HISTORICAL_V2" for row in S1_KL_IDENTITY_RECORDS),
        "mismatched_checkpoint_count": sum(row[5] for row in S1_KL_IDENTITY_RECORDS),
        "numeric_results_invalidated": False,
        "comparison_digests_invalidated": False,
        "affected_provenance_outputs_valid_as_corrected_records": False,
        "historical_records_rewritten": False,
        "replicas_executed": 0,
        "interval_calls_executed": 0,
        "case_composition_blocked": True,
        "versioned_correction_contract_authorized_next_stage": True,
        "decision": S1_KL_DECISION,
    }
    return DTS1S1KLCheckpointIdentityAudit(
        **values, audit_digest=_digest(values)
    )
