"""Passive exact comparison of candidate and matched baseline checkpoints."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

from .g2_d3_matched_retention_baseline import (
    BASELINE_CONTRACT_DIGEST,
    G2D3MatchedRetentionBaselineReceipt,
    G2D3MatchedRetentionBaselineResult,
)
from .g2_d3_two_step_o3_checkpoints import (
    CHECKPOINT_CONTRACT_DIGEST,
    G2D3TwoStepO3CheckpointReceipt,
    G2D3TwoStepO3CheckpointResult,
)
from .kfs1_schema_validator import canonical_json_bytes, sha256_hex


RECEIPT_SCHEMA_ID = "g2_d3_checkpoint_baseline_comparison_receipt"
RECEIPT_SCHEMA_VERSION = "s1pa.v1"
CLOSURE_STATUSES = ("BASELINE_CLOSED_CURRENT_CHECKPOINT_VECTOR", "not_computable")
COMPARISON_PHASES = (
    "api_intake",
    "candidate_validation",
    "baseline_validation",
    "chain_provenance_gate",
    "checkpoint_identity_gate",
    "residual_evaluation",
    "persistence_guard",
    "comparison_receipt",
)
FAILURE_CODES = (
    "PA_CANDIDATE_RESULT_INVALID",
    "PA_BASELINE_RESULT_INVALID",
    "PA_CHAIN_PROVENANCE_MISMATCH",
    "PA_CHECKPOINT_IDENTITY_MISMATCH",
    "PA_RESIDUAL_IDENTITY_MISMATCH",
)
COMPARISON_CONTRACT_DIGEST = (
    "7b3818ca3e9ce2b2b1502399e52d69ca25a02247cca43f06b883633a61d28f0d"
)
CLOSURE_CONTRACT_DIGEST = (
    "ac13a848fab0e766b4c02568d4c20aa93915cf0f34dce68ac682969f1fcb376c"
)
EXPECTED_CHECKPOINT_VALUES = (0.5, 0.25, 0.125)
EXPECTED_COMPONENTS = (-0.25, -0.125, -0.375)
EXPECTED_COMPARISON_DIGEST = (
    "5c8d3b60bbc205594974f632a878472bf628426dc914af72514cf7b42e8a86a5"
)
EXPECTED_CLOSURE_PAYLOAD_DIGEST = (
    "bce12955a3df61976dcf650b9dba93a59c5894d148a07414efd44489d5f2af15"
)
_NOT_COMPUTABLE = "not_computable"


@dataclass(frozen=True)
class G2D3CheckpointBaselineComparisonRegistry:
    receipt_schema_id: str
    receipt_schema_version: str
    closure_statuses: tuple[str, ...]
    comparison_phases: tuple[str, ...]
    failure_codes: tuple[str, ...]
    accepted_candidate_checkpoint_contract_digest: str
    accepted_baseline_contract_digest: str
    comparison_contract_digest: str
    closure_contract_digest: str


@dataclass(frozen=True)
class G2D3CheckpointBaselineComparisonReceipt:
    receipt_schema_id: str
    receipt_schema_version: str
    candidate_chain_role: str
    baseline_chain_role: str
    candidate_checkpoint_receipt_digest: str
    baseline_receipt_digest: str
    candidate_checkpoint_values: tuple[float, float, float] | str
    baseline_checkpoint_values: tuple[float, float, float] | str
    candidate_directed_components: tuple[float, float, float] | str
    baseline_directed_components: tuple[float, float, float] | str
    candidate_comparison_digest: str
    baseline_comparison_digest: str
    residual_checkpoint_values: tuple[float, float, float] | str
    residual_directed_components: tuple[float, float, float] | str
    closure_payload_digest: str
    closure_status: str
    validation_status: str
    completed_checks: tuple[str, ...]
    failure_reasons: tuple[str, ...]
    accepted_candidate_checkpoint_contract_digest: str
    accepted_baseline_contract_digest: str
    comparison_contract_digest: str
    closure_contract_digest: str
    comparison_receipt_digest: str

    def canonical_payload(self) -> dict[str, Any]:
        payload = {item.name: getattr(self, item.name) for item in fields(self)}
        for name in (
            "candidate_checkpoint_values",
            "baseline_checkpoint_values",
            "candidate_directed_components",
            "baseline_directed_components",
            "residual_checkpoint_values",
            "residual_directed_components",
        ):
            if type(payload[name]) is tuple:
                payload[name] = list(payload[name])
        payload["completed_checks"] = list(self.completed_checks)
        payload["failure_reasons"] = list(self.failure_reasons)
        return payload


@dataclass(frozen=True)
class G2D3CheckpointBaselineComparisonResult:
    closure_status: str
    residual_checkpoint_values: tuple[float, float, float] | str
    residual_directed_components: tuple[float, float, float] | str
    receipt: G2D3CheckpointBaselineComparisonReceipt


def build_g2_d3_checkpoint_baseline_comparison_registry() -> G2D3CheckpointBaselineComparisonRegistry:
    return G2D3CheckpointBaselineComparisonRegistry(
        receipt_schema_id=RECEIPT_SCHEMA_ID,
        receipt_schema_version=RECEIPT_SCHEMA_VERSION,
        closure_statuses=CLOSURE_STATUSES,
        comparison_phases=COMPARISON_PHASES,
        failure_codes=FAILURE_CODES,
        accepted_candidate_checkpoint_contract_digest=CHECKPOINT_CONTRACT_DIGEST,
        accepted_baseline_contract_digest=BASELINE_CONTRACT_DIGEST,
        comparison_contract_digest=COMPARISON_CONTRACT_DIGEST,
        closure_contract_digest=CLOSURE_CONTRACT_DIGEST,
    )


def _receipt_digest_is_valid(receipt: Any, digest_field: str) -> bool:
    payload = receipt.canonical_payload()
    digest = payload.pop(digest_field)
    return digest == sha256_hex(canonical_json_bytes(payload))


def _candidate_is_valid(result: G2D3TwoStepO3CheckpointResult) -> bool:
    receipt = result.receipt
    return (
        type(receipt) is G2D3TwoStepO3CheckpointReceipt
        and receipt.validation_status == "valid"
        and receipt.checkpoint_status == "THREE_CHECKPOINTS_EVALUATED"
        and receipt.failure_reasons == ()
        and receipt.checkpoint_contract_digest == CHECKPOINT_CONTRACT_DIGEST
        and _receipt_digest_is_valid(receipt, "checkpoint_receipt_digest")
    )


def _baseline_is_valid(result: G2D3MatchedRetentionBaselineResult) -> bool:
    receipt = result.receipt
    return (
        type(receipt) is G2D3MatchedRetentionBaselineReceipt
        and receipt.validation_status == "valid"
        and receipt.baseline_status == "THREE_CHECKPOINTS_EVALUATED"
        and receipt.failure_reasons == ()
        and receipt.baseline_contract_digest == BASELINE_CONTRACT_DIGEST
        and _receipt_digest_is_valid(receipt, "baseline_receipt_digest")
    )


def _build_receipt(
    *,
    candidate_role: str,
    baseline_role: str,
    candidate_receipt_digest: str,
    baseline_receipt_digest: str,
    candidate_values: tuple[float, float, float] | None,
    baseline_values: tuple[float, float, float] | None,
    candidate_components: tuple[float, float, float] | None,
    baseline_components: tuple[float, float, float] | None,
    candidate_comparison_digest: str,
    baseline_comparison_digest: str,
    residual_values: tuple[float, float, float] | None,
    residual_components: tuple[float, float, float] | None,
    closure_payload_digest: str,
    closure_status: str,
    completed: list[str],
    failures: tuple[str, ...],
) -> G2D3CheckpointBaselineComparisonReceipt:
    payload = {
        "receipt_schema_id": RECEIPT_SCHEMA_ID,
        "receipt_schema_version": RECEIPT_SCHEMA_VERSION,
        "candidate_chain_role": candidate_role,
        "baseline_chain_role": baseline_role,
        "candidate_checkpoint_receipt_digest": candidate_receipt_digest,
        "baseline_receipt_digest": baseline_receipt_digest,
        "candidate_checkpoint_values": list(candidate_values) if candidate_values is not None else _NOT_COMPUTABLE,
        "baseline_checkpoint_values": list(baseline_values) if baseline_values is not None else _NOT_COMPUTABLE,
        "candidate_directed_components": list(candidate_components) if candidate_components is not None else _NOT_COMPUTABLE,
        "baseline_directed_components": list(baseline_components) if baseline_components is not None else _NOT_COMPUTABLE,
        "candidate_comparison_digest": candidate_comparison_digest,
        "baseline_comparison_digest": baseline_comparison_digest,
        "residual_checkpoint_values": list(residual_values) if residual_values is not None else _NOT_COMPUTABLE,
        "residual_directed_components": list(residual_components) if residual_components is not None else _NOT_COMPUTABLE,
        "closure_payload_digest": closure_payload_digest,
        "closure_status": closure_status,
        "validation_status": "invalid" if failures else "valid",
        "completed_checks": completed,
        "failure_reasons": list(failures),
        "accepted_candidate_checkpoint_contract_digest": CHECKPOINT_CONTRACT_DIGEST,
        "accepted_baseline_contract_digest": BASELINE_CONTRACT_DIGEST,
        "comparison_contract_digest": COMPARISON_CONTRACT_DIGEST,
        "closure_contract_digest": CLOSURE_CONTRACT_DIGEST,
    }
    receipt_digest = sha256_hex(canonical_json_bytes(payload))
    tuple_fields = {
        "candidate_checkpoint_values": candidate_values if candidate_values is not None else _NOT_COMPUTABLE,
        "baseline_checkpoint_values": baseline_values if baseline_values is not None else _NOT_COMPUTABLE,
        "candidate_directed_components": candidate_components if candidate_components is not None else _NOT_COMPUTABLE,
        "baseline_directed_components": baseline_components if baseline_components is not None else _NOT_COMPUTABLE,
        "residual_checkpoint_values": residual_values if residual_values is not None else _NOT_COMPUTABLE,
        "residual_directed_components": residual_components if residual_components is not None else _NOT_COMPUTABLE,
    }
    return G2D3CheckpointBaselineComparisonReceipt(
        **{
            **payload,
            **tuple_fields,
            "completed_checks": tuple(completed),
            "failure_reasons": failures,
            "comparison_receipt_digest": receipt_digest,
        }
    )


def compare_g2_d3_candidate_and_retention_baseline(
    candidate_result: G2D3TwoStepO3CheckpointResult,
    baseline_result: G2D3MatchedRetentionBaselineResult,
    comparison_registry: G2D3CheckpointBaselineComparisonRegistry,
) -> G2D3CheckpointBaselineComparisonResult:
    """Compare two complete passive checkpoint results without re-execution."""

    if type(candidate_result) is not G2D3TwoStepO3CheckpointResult:
        raise TypeError("candidate_result must be G2D3TwoStepO3CheckpointResult")
    if type(baseline_result) is not G2D3MatchedRetentionBaselineResult:
        raise TypeError("baseline_result must be G2D3MatchedRetentionBaselineResult")
    if type(comparison_registry) is not G2D3CheckpointBaselineComparisonRegistry:
        raise TypeError("comparison_registry must be G2D3CheckpointBaselineComparisonRegistry")
    if comparison_registry != build_g2_d3_checkpoint_baseline_comparison_registry():
        raise ValueError("comparison_registry does not match the bound S1-PA registry")

    completed = ["api_intake"]
    candidate_receipt = candidate_result.receipt
    baseline_receipt = baseline_result.receipt
    candidate_role = getattr(candidate_receipt, "chain_role", _NOT_COMPUTABLE)
    baseline_role = getattr(baseline_receipt, "chain_role", _NOT_COMPUTABLE)
    candidate_receipt_digest = getattr(
        candidate_receipt, "checkpoint_receipt_digest", _NOT_COMPUTABLE
    )
    baseline_receipt_digest = getattr(
        baseline_receipt, "baseline_receipt_digest", _NOT_COMPUTABLE
    )

    def fail(code: str) -> G2D3CheckpointBaselineComparisonResult:
        completed.extend(("persistence_guard", "comparison_receipt"))
        receipt = _build_receipt(
            candidate_role=candidate_role,
            baseline_role=baseline_role,
            candidate_receipt_digest=candidate_receipt_digest,
            baseline_receipt_digest=baseline_receipt_digest,
            candidate_values=None,
            baseline_values=None,
            candidate_components=None,
            baseline_components=None,
            candidate_comparison_digest=_NOT_COMPUTABLE,
            baseline_comparison_digest=_NOT_COMPUTABLE,
            residual_values=None,
            residual_components=None,
            closure_payload_digest=_NOT_COMPUTABLE,
            closure_status=_NOT_COMPUTABLE,
            completed=completed,
            failures=(code,),
        )
        return G2D3CheckpointBaselineComparisonResult(
            _NOT_COMPUTABLE, _NOT_COMPUTABLE, _NOT_COMPUTABLE, receipt
        )

    completed.append("candidate_validation")
    if not _candidate_is_valid(candidate_result):
        return fail("PA_CANDIDATE_RESULT_INVALID")
    completed.append("baseline_validation")
    if not _baseline_is_valid(baseline_result):
        return fail("PA_BASELINE_RESULT_INVALID")
    completed.append("chain_provenance_gate")
    if candidate_role != baseline_role:
        return fail("PA_CHAIN_PROVENANCE_MISMATCH")

    candidate_values = candidate_result.checkpoint_values
    baseline_values = baseline_result.checkpoint_values
    candidate_components = (
        candidate_receipt.delta_cp1_cp0,
        candidate_receipt.delta_cp2_cp1,
        candidate_receipt.delta_cp2_cp0,
    )
    baseline_components = (
        baseline_receipt.delta_cp1_cp0,
        baseline_receipt.delta_cp2_cp1,
        baseline_receipt.delta_cp2_cp0,
    )
    completed.append("checkpoint_identity_gate")
    if (
        candidate_values != EXPECTED_CHECKPOINT_VALUES
        or baseline_values != EXPECTED_CHECKPOINT_VALUES
        or candidate_components != EXPECTED_COMPONENTS
        or baseline_components != EXPECTED_COMPONENTS
        or candidate_receipt.comparison_digest != EXPECTED_COMPARISON_DIGEST
        or baseline_receipt.comparison_digest != EXPECTED_COMPARISON_DIGEST
    ):
        return fail("PA_CHECKPOINT_IDENTITY_MISMATCH")

    residual_values = tuple(
        baseline - candidate
        for candidate, baseline in zip(candidate_values, baseline_values, strict=True)
    )
    residual_components = tuple(
        baseline - candidate
        for candidate, baseline in zip(candidate_components, baseline_components, strict=True)
    )
    closure_payload = {
        "baseline_checkpoint_values": list(baseline_values),
        "baseline_directed_components": list(baseline_components),
        "candidate_checkpoint_values": list(candidate_values),
        "candidate_directed_components": list(candidate_components),
        "residual_checkpoint_values": list(residual_values),
        "residual_directed_components": list(residual_components),
    }
    closure_payload_digest = sha256_hex(canonical_json_bytes(closure_payload))
    completed.append("residual_evaluation")
    if (
        residual_values != (0.0, 0.0, 0.0)
        or residual_components != (0.0, 0.0, 0.0)
        or closure_payload_digest != EXPECTED_CLOSURE_PAYLOAD_DIGEST
    ):
        return fail("PA_RESIDUAL_IDENTITY_MISMATCH")

    closure_status = "BASELINE_CLOSED_CURRENT_CHECKPOINT_VECTOR"
    completed.extend(("persistence_guard", "comparison_receipt"))
    receipt = _build_receipt(
        candidate_role=candidate_role,
        baseline_role=baseline_role,
        candidate_receipt_digest=candidate_receipt_digest,
        baseline_receipt_digest=baseline_receipt_digest,
        candidate_values=candidate_values,
        baseline_values=baseline_values,
        candidate_components=candidate_components,
        baseline_components=baseline_components,
        candidate_comparison_digest=candidate_receipt.comparison_digest,
        baseline_comparison_digest=baseline_receipt.comparison_digest,
        residual_values=residual_values,
        residual_components=residual_components,
        closure_payload_digest=closure_payload_digest,
        closure_status=closure_status,
        completed=completed,
        failures=(),
    )
    return G2D3CheckpointBaselineComparisonResult(
        closure_status, residual_values, residual_components, receipt
    )


__all__ = (
    "RECEIPT_SCHEMA_ID",
    "RECEIPT_SCHEMA_VERSION",
    "CLOSURE_STATUSES",
    "COMPARISON_PHASES",
    "FAILURE_CODES",
    "COMPARISON_CONTRACT_DIGEST",
    "CLOSURE_CONTRACT_DIGEST",
    "G2D3CheckpointBaselineComparisonRegistry",
    "G2D3CheckpointBaselineComparisonReceipt",
    "G2D3CheckpointBaselineComparisonResult",
    "build_g2_d3_checkpoint_baseline_comparison_registry",
    "compare_g2_d3_candidate_and_retention_baseline",
)
