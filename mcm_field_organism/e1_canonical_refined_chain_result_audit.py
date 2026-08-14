"""Read-only S1-EA6 audit of the published canonical refined-chain result."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path

from .e1_refined_chain_one_shot_contract import S1_DW_REPORT_FIELDS
from .e1_refined_chain_one_shot_execution import (
    E1RefinedChainExecutionResult,
    E1RefinedChainRefinementResult,
)
from .e1_refined_world_formation_contract import (
    S1_DS_METRICS,
    S1_DS_REQUIRED_CONTROLS,
)


class E1CanonicalRefinedChainResultAuditError(ValueError):
    """Raised when the terminal S1-EA6 report is incomplete or changed."""


S1_EA6_REPORT_SHA256 = (
    "adf8b2b6c1b9fdda48062dbb1cd9149fcde462a3dc77a348aa2dfb0cb1fcaa47"
)
S1_EA6_RESULT_SHA256 = (
    "321b83ca3a99df0474b09d8d9131f031c734dcc2ae67ea32993ed604802678bc"
)


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class E1CanonicalRefinedChainResultAudit:
    audit_id: str
    report_sha256: str
    result_sha256: str
    technical_decision: str
    all_controls_passed: bool
    exact_control_residuals_zero: bool
    state_converges: bool
    probe_converges: bool
    state_margin_passed: bool
    probe_s_margin_passed: bool
    probe_h_margin_passed: bool
    fine_state_margin_ratio: float
    fine_probe_s_margin_ratio: float
    fine_probe_h_margin_ratio: float
    rerun_permitted: bool
    memory_claim_permitted: bool
    ai_claim_permitted: bool

    def __post_init__(self) -> None:
        if (
            self.audit_id != "e1.canonical-refined-chain-result-audit.s1ea6.v1"
            or self.report_sha256 != S1_EA6_REPORT_SHA256
            or self.result_sha256 != S1_EA6_RESULT_SHA256
            or self.technical_decision != "NUMERICALLY_UNDECIDABLE"
        ):
            raise E1CanonicalRefinedChainResultAuditError(
                "S1-EA6 terminal identity or decision changed"
            )
        required_true = (
            self.all_controls_passed,
            self.exact_control_residuals_zero,
            self.state_converges,
            self.probe_converges,
            self.state_margin_passed,
        )
        if any(value is not True for value in required_true):
            raise E1CanonicalRefinedChainResultAuditError(
                "S1-EA6 required technical control changed"
            )
        if self.probe_s_margin_passed is not False or self.probe_h_margin_passed is not False:
            raise E1CanonicalRefinedChainResultAuditError(
                "S1-EA6 undecidable probe-margin boundary changed"
            )
        for role in (
            "fine_state_margin_ratio",
            "fine_probe_s_margin_ratio",
            "fine_probe_h_margin_ratio",
        ):
            value = getattr(self, role)
            if not math.isfinite(value) or value <= 0.0:
                raise E1CanonicalRefinedChainResultAuditError(
                    f"{role} is invalid"
                )
        if (
            self.fine_state_margin_ratio <= 8.0
            or self.fine_probe_s_margin_ratio >= 8.0
            or self.fine_probe_h_margin_ratio >= 8.0
        ):
            raise E1CanonicalRefinedChainResultAuditError(
                "S1-EA6 margin classification changed"
            )
        if (
            self.rerun_permitted is not False
            or self.memory_claim_permitted is not False
            or self.ai_claim_permitted is not False
        ):
            raise E1CanonicalRefinedChainResultAuditError(
                "S1-EA6 cannot permit rerun or strong claims"
            )


def _load_result(value: object) -> E1RefinedChainExecutionResult:
    if not isinstance(value, dict):
        raise E1CanonicalRefinedChainResultAuditError(
            "S1-EA6 result payload is invalid"
        )
    refinements = tuple(
        E1RefinedChainRefinementResult(
            refinement_id=item["refinement_id"],
            factor=item["factor"],
            formation_state_digests=tuple(
                tuple(pair) for pair in item["formation_state_digests"]
            ),
            probe_field_digests=tuple(
                tuple(pair) for pair in item["probe_field_digests"]
            ),
            d_state=item["d_state"],
            d_total_binding=item["d_total_binding"],
            d_probe_s=item["d_probe_s"],
            d_probe_h=item["d_probe_h"],
        )
        for item in value["refinements"]
    )
    return E1RefinedChainExecutionResult(
        refinements=refinements,
        metrics=tuple(tuple(item) for item in value["metrics"]),
        controls=tuple(tuple(item) for item in value["controls"]),
        technical_decision=value["technical_decision"],
    )


def audit_e1_canonical_refined_chain_result(
    report_path: Path,
) -> E1CanonicalRefinedChainResultAudit:
    """Audit the immutable report without constructing any runtime input."""

    path = Path(report_path).resolve()
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != S1_EA6_REPORT_SHA256:
        raise E1CanonicalRefinedChainResultAuditError(
            "S1-EA6 canonical report is missing or changed"
        )
    report = json.loads(path.read_text(encoding="ascii"))
    if tuple(report) != S1_DW_REPORT_FIELDS:
        raise E1CanonicalRefinedChainResultAuditError(
            "S1-EA6 report field order changed"
        )
    result = _load_result(report["result"])
    if (
        _digest(report["result"]) != S1_EA6_RESULT_SHA256
        or report["result_digest"] != S1_EA6_RESULT_SHA256
        or report["technical_decision"] != result.technical_decision
        or tuple(tuple(item) for item in report["metrics"]) != result.metrics
        or tuple(tuple(item) for item in report["controls"]) != result.controls
    ):
        raise E1CanonicalRefinedChainResultAuditError(
            "S1-EA6 report and validated result differ"
        )
    metrics = dict(result.metrics)
    controls = dict(result.controls)
    if tuple(metrics) != S1_DS_METRICS or tuple(controls) != S1_DS_REQUIRED_CONTROLS:
        raise E1CanonicalRefinedChainResultAuditError(
            "S1-EA6 metric or control inventory changed"
        )
    state_floor = 8.0 * metrics["state_refinement_r2_r4"]
    probe_floor = 8.0 * metrics["probe_refinement_r2_r4"]
    exact_residuals = (
        metrics["identity_residual"],
        metrics["formation_ablation_residual"],
        metrics["probe_ablation_residual"],
        metrics["fixed_adapter_residual"],
        metrics["resource_budget_error"],
    )
    return E1CanonicalRefinedChainResultAudit(
        audit_id="e1.canonical-refined-chain-result-audit.s1ea6.v1",
        report_sha256=S1_EA6_REPORT_SHA256,
        result_sha256=S1_EA6_RESULT_SHA256,
        technical_decision=result.technical_decision,
        all_controls_passed=all(controls.values()),
        exact_control_residuals_zero=all(value == 0.0 for value in exact_residuals),
        state_converges=(
            metrics["state_refinement_r2_r4"]
            <= metrics["state_refinement_r1_r2"]
        ),
        probe_converges=(
            metrics["probe_refinement_r2_r4"]
            <= metrics["probe_refinement_r1_r2"]
        ),
        state_margin_passed=metrics["d_state"] > state_floor,
        probe_s_margin_passed=metrics["d_probe_s"] > probe_floor,
        probe_h_margin_passed=metrics["d_probe_h"] > probe_floor,
        fine_state_margin_ratio=(
            metrics["d_state"] / metrics["state_refinement_r2_r4"]
        ),
        fine_probe_s_margin_ratio=(
            metrics["d_probe_s"] / metrics["probe_refinement_r2_r4"]
        ),
        fine_probe_h_margin_ratio=(
            metrics["d_probe_h"] / metrics["probe_refinement_r2_r4"]
        ),
        rerun_permitted=False,
        memory_claim_permitted=False,
        ai_claim_permitted=False,
    )
