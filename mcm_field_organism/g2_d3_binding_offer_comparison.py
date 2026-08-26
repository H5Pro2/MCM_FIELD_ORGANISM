"""Passive S1-PJ candidate/baseline contrast comparator."""

from __future__ import annotations

from dataclasses import dataclass, fields
import json
from typing import Any, Mapping

from .g2_d3_local_binding_offer import G2D3LocalBindingOfferResult, NOT_COMPUTABLE
from .g2_d3_matched_retention_baseline import G2D3MatchedRetentionBaselineResult
from .kfs1_schema_validator import canonical_json_bytes, sha256_hex


FAILURE_CODES = (
    "PL_CANDIDATE_RESULT_INVALID", "PL_BASELINE_RESULT_INVALID",
    "PL_BASELINE_PROVENANCE_MISMATCH", "PL_CP2_EXCLUSION_FAILED",
    "PL_CANDIDATE_CONTRAST_MISMATCH", "PL_BASELINE_CONTRAST_MISMATCH",
    "PL_PREDICTION_OR_DECISION_MISMATCH",
)
_PREDICTION_DIGEST = "0fabfc2935e47e5c5b6be99d4a31ae28e2c1d26f25cfe12892060c42ed2dbb61"
_CHAIN = "OP_CHAIN_XXX"
_FIRST = "c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c"
_SECOND = "6d4a6a51e8c3fb81734598f23edff930f88b5f85e00b79c5d84d1da2b5b0ad9a"
_INITIAL = "f67406ef5f4da6ecd3775ab8c12139dbee607dd33b0c89e14842774c48d0ffd2"
_CONFIG = "12e6d381c0dcc0f170c39453bde291152bc55499e0292edacb2d0a09c27e1d93"
_EVENT = "dbffc12bef77155c2271d3990ebe1b8ae4d481ce6155bf8716b1f6e19128b30f"
_DECISION = "CANDIDATE_DIFFERENT_BASELINE_EQUAL"
_PHASES = (
    "api_intake", "prediction_validation", "candidate_validation",
    "baseline_validation", "provenance_validation", "cp2_exclusion",
    "contrast_evaluation", "decision", "receipt",
)
_CONTRACT_DIGEST = sha256_hex(b"g2.d3.binding_offer_comparison.s1pl.v1")


@dataclass(frozen=True)
class G2D3BindingOfferComparisonRegistry:
    prediction_digest: str
    chain_role: str
    first_boundary_digest: str
    second_boundary_digest: str
    comparison_contract_digest: str
    phases: tuple[str, ...]
    failure_codes: tuple[str, ...]


@dataclass(frozen=True)
class G2D3BindingOfferComparisonReceipt:
    validation_status: str
    completed_checks: tuple[str, ...]
    failure_reasons: tuple[str, ...]
    prediction_input_digest: str
    prediction_digest: str
    free_candidate_receipt_digest: str
    blocked_candidate_receipt_digest: str
    free_baseline_receipt_digest: str
    blocked_baseline_receipt_digest: str
    comparison_contract_digest: str
    receipt_digest: str

    def canonical_payload(self) -> dict[str, Any]:
        value = {item.name: getattr(self, item.name) for item in fields(self)}
        value["completed_checks"] = list(self.completed_checks)
        value["failure_reasons"] = list(self.failure_reasons)
        return value


@dataclass(frozen=True)
class G2D3BindingOfferComparisonResult:
    candidate_commits: tuple[float, float] | str
    candidate_binding_contrast: float | str
    baseline_first_step_responses: tuple[float, float] | str
    baseline_replica_contrast: float | str
    decision: str
    receipt: G2D3BindingOfferComparisonReceipt


def build_g2_d3_binding_offer_comparison_registry() -> G2D3BindingOfferComparisonRegistry:
    return G2D3BindingOfferComparisonRegistry(
        _PREDICTION_DIGEST, _CHAIN, _FIRST, _SECOND, _CONTRACT_DIGEST, _PHASES, FAILURE_CODES
    )


def _prediction(raw: bytes) -> Mapping[str, Any] | None:
    try:
        value = json.loads(raw)
        if not isinstance(value, dict) or canonical_json_bytes(value) != raw:
            return None
        declared = value.get("prediction_digest")
        if declared != sha256_hex(canonical_json_bytes({k: v for k, v in value.items() if k != "prediction_digest"})):
            return None
        return value
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
        return None


def _baseline_receipt_digest_valid(result: G2D3MatchedRetentionBaselineResult) -> bool:
    payload = result.receipt.canonical_payload()
    declared = payload.pop("baseline_receipt_digest")
    return declared == sha256_hex(canonical_json_bytes(payload))


def compare_g2_d3_binding_offer_results(
    free_available_candidate_result: G2D3LocalBindingOfferResult,
    blocked_held_candidate_result: G2D3LocalBindingOfferResult,
    free_comparison_baseline_result: G2D3MatchedRetentionBaselineResult,
    blocked_comparison_baseline_result: G2D3MatchedRetentionBaselineResult,
    prediction_raw_bytes: bytes,
    comparison_registry: G2D3BindingOfferComparisonRegistry,
) -> G2D3BindingOfferComparisonResult:
    if type(free_available_candidate_result) is not G2D3LocalBindingOfferResult or type(
        blocked_held_candidate_result
    ) is not G2D3LocalBindingOfferResult:
        raise TypeError("candidate result type mismatch")
    if type(free_comparison_baseline_result) is not G2D3MatchedRetentionBaselineResult or type(
        blocked_comparison_baseline_result
    ) is not G2D3MatchedRetentionBaselineResult:
        raise TypeError("baseline result type mismatch")
    if type(prediction_raw_bytes) is not bytes:
        raise TypeError("prediction_raw_bytes must be bytes")
    if type(comparison_registry) is not G2D3BindingOfferComparisonRegistry:
        raise TypeError("comparison_registry type mismatch")
    if comparison_registry != build_g2_d3_binding_offer_comparison_registry():
        raise ValueError("comparison_registry content mismatch")

    failures: set[str] = set()
    prediction = _prediction(prediction_raw_bytes)
    prediction_digest = prediction.get("prediction_digest", NOT_COMPUTABLE) if prediction else NOT_COMPUTABLE
    if prediction is None:
        failures.add("PL_PREDICTION_OR_DECISION_MISMATCH")
    elif prediction.get("excluded_baseline_checkpoint") != "cp2":
        failures.add("PL_CP2_EXCLUSION_FAILED")
    elif prediction_digest != _PREDICTION_DIGEST or prediction.get("expected_decision") != _DECISION:
        failures.add("PL_PREDICTION_OR_DECISION_MISMATCH")

    candidates = (free_available_candidate_result, blocked_held_candidate_result)
    if not failures and any(
        item.receipt.validation_status != "valid"
        or not isinstance(item.commit_amount, float)
        or not isinstance(item.poststate_raw_bytes, bytes)
        for item in candidates
    ):
        failures.add("PL_CANDIDATE_RESULT_INVALID")

    baselines = (free_comparison_baseline_result, blocked_comparison_baseline_result)
    if not failures and any(
        item.receipt.validation_status != "valid"
        or item.receipt.baseline_status != "THREE_CHECKPOINTS_EVALUATED"
        or not isinstance(item.checkpoint_values, tuple)
        or len(item.checkpoint_values) != 3
        or tuple(item.checkpoint_values) != (
            item.receipt.cp0_value, item.receipt.cp1_value, item.receipt.cp2_value
        )
        or not _baseline_receipt_digest_valid(item)
        for item in baselines
    ):
        failures.add("PL_BASELINE_RESULT_INVALID")

    if not failures and any(
        item.receipt.chain_role != _CHAIN
        or item.receipt.first_boundary_input_digest != _FIRST
        or item.receipt.second_boundary_input_digest != _SECOND
        or item.receipt.initial_state_input_bytes_digest != _INITIAL
        or item.receipt.configuration_input_bytes_digest != _CONFIG
        or item.receipt.continuation_event_input_bytes_digest != _EVENT
        for item in baselines
    ):
        failures.add("PL_BASELINE_PROVENANCE_MISMATCH")

    candidate_values: tuple[float, float] | None = None
    candidate_contrast: float | None = None
    baseline_values: tuple[float, float] | None = None
    baseline_contrast: float | None = None
    if not failures:
        candidate_values = (float(candidates[0].commit_amount), float(candidates[1].commit_amount))
        candidate_contrast = candidate_values[0] - candidate_values[1]
        if candidate_values != (0.375, 0.25) or candidate_contrast != 0.125:
            failures.add("PL_CANDIDATE_CONTRAST_MISMATCH")
    if not failures:
        baseline_values = tuple(
            float(item.checkpoint_values[0]) - float(item.checkpoint_values[1]) for item in baselines
        )
        baseline_contrast = baseline_values[0] - baseline_values[1]
        if baseline_values != (0.25, 0.25) or baseline_contrast != 0.0:
            failures.add("PL_BASELINE_CONTRAST_MISMATCH")

    decision = _DECISION if not failures else "INVALID_OR_INCOMPLETE"
    if not failures and prediction is not None and (
        prediction.get("candidate_binding_contrast") != candidate_contrast
        or prediction.get("baseline_replica_contrast") != baseline_contrast
    ):
        failures.add("PL_PREDICTION_OR_DECISION_MISMATCH")
        decision = "INVALID_OR_INCOMPLETE"

    receipt_payload = {
        "validation_status": "invalid" if failures else "valid",
        "completed_checks": list(_PHASES), "failure_reasons": sorted(failures),
        "prediction_input_digest": sha256_hex(prediction_raw_bytes),
        "prediction_digest": prediction_digest,
        "free_candidate_receipt_digest": candidates[0].receipt.receipt_digest,
        "blocked_candidate_receipt_digest": candidates[1].receipt.receipt_digest,
        "free_baseline_receipt_digest": baselines[0].receipt.baseline_receipt_digest,
        "blocked_baseline_receipt_digest": baselines[1].receipt.baseline_receipt_digest,
        "comparison_contract_digest": _CONTRACT_DIGEST,
    }
    receipt_digest = sha256_hex(canonical_json_bytes(receipt_payload))
    receipt = G2D3BindingOfferComparisonReceipt(**{
        **receipt_payload, "completed_checks": _PHASES,
        "failure_reasons": tuple(sorted(failures)), "receipt_digest": receipt_digest,
    })
    return G2D3BindingOfferComparisonResult(
        candidate_values if not failures and candidate_values is not None else NOT_COMPUTABLE,
        candidate_contrast if not failures and candidate_contrast is not None else NOT_COMPUTABLE,
        baseline_values if not failures and baseline_values is not None else NOT_COMPUTABLE,
        baseline_contrast if not failures and baseline_contrast is not None else NOT_COMPUTABLE,
        decision,
        receipt,
    )


__all__ = (
    "FAILURE_CODES", "G2D3BindingOfferComparisonRegistry", "G2D3BindingOfferComparisonReceipt",
    "G2D3BindingOfferComparisonResult", "build_g2_d3_binding_offer_comparison_registry",
    "compare_g2_d3_binding_offer_results",
)
