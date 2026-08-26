"""Static S1-EC24 decision audit for the protected S1-EC23 probe report."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path

from .e1_confirmation_full_published_probe_once import (
    S1_EC23_SCHEMA_ID,
    E1FullPublishedProbeRawResult,
    load_full_published_probe_raw_result,
)
from .e1_confirmation_published_probe_handoff_audit import (
    S1_EC20_REPORT_SHA256,
    S1_EC20_THRESHOLD_POLICY,
)
from .e1_refined_formation_runner import _digest


class E1ConfirmationFullProbeResultAuditError(ValueError):
    """Raised when the protected S1-EC23 evidence is incomplete or changed."""


S1_EC24_AUDIT_ID = "e1.full-probe-result-audit.s1ec24.v1"
S1_EC24_REPORT_SHA256 = (
    "85a114b9de5f2152558ca78a03a15f5690607fab98b7f9ddbf10cadf32e8b50e"
)
S1_EC24_RAW_RESULT_DIGEST = (
    "4c0e74fe291a43d69ca49fa6285ae36eeee2829df4225cf1aba75240b022de81"
)
S1_EC24_SIGNAL_MARGIN = 8.0
S1_EC24_DECISIONS = (
    "NO_CONFIRMED_PERSISTENT_PROBE_DIFFERENCE",
    "CONFIRMED_NUMERICALLY_CLEAR_PERSISTENT_STATE_PROBE_DIFFERENCE",
    "NUMERICALLY_UNDECIDABLE",
)
S1_EC24_REQUIRED_CHECKS = (
    "protected-s1ec23-report-hash-exact",
    "s1ec23-schema-and-execution-identity-exact",
    "typed-raw-result-digest-exact",
    "s1ec19-persistent-state-source-bound",
    "source-state-digests-unchanged-by-probe",
    "registered-controls-pass",
    "all-control-residuals-bit-zero",
    "all-probe-supports-assigned-once",
    "coarse-to-fine-probe-residual-nonincreasing",
    "strict-eight-times-threshold-unchanged",
    "source-report-contained-no-decision-or-claims",
)


def decide_persistent_probe_evidence(
    *,
    active_s: float,
    active_h: float,
    coarse_residual: float,
    fine_residual: float,
    controls_passed: bool,
) -> str:
    """Apply only the preregistered EC20 numerical probe rule."""

    values = (active_s, active_h, coarse_residual, fine_residual)
    if any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
        or float(value) < 0.0
        for value in values
    ) or not isinstance(controls_passed, bool):
        raise E1ConfirmationFullProbeResultAuditError(
            "S1-EC24 decision inputs are invalid"
        )
    if controls_passed is not True:
        raise E1ConfirmationFullProbeResultAuditError(
            "S1-EC24 cannot decide with failed controls"
        )
    if active_s == 0.0 and active_h == 0.0:
        return "NO_CONFIRMED_PERSISTENT_PROBE_DIFFERENCE"
    threshold = S1_EC24_SIGNAL_MARGIN * fine_residual
    if (
        fine_residual <= coarse_residual
        and active_s > threshold
        and active_h > threshold
    ):
        return "CONFIRMED_NUMERICALLY_CLEAR_PERSISTENT_STATE_PROBE_DIFFERENCE"
    return "NUMERICALLY_UNDECIDABLE"


@dataclass(frozen=True, slots=True)
class E1FullProbeResultAudit:
    audit_id: str
    report_path: str
    report_sha256: str
    raw_result_digest: str
    source_report_sha256: str
    threshold_policy: str
    signal_margin: float
    r8_active_s: float
    r8_active_h: float
    coarse_residual: float
    fine_residual: float
    strict_threshold: float
    active_s_margin_ratio: float
    active_h_margin_ratio: float
    checks: tuple[tuple[str, bool], ...]
    technical_decision: str
    evidence_scope: str
    field_execution_performed: bool
    report_written: bool
    memory_claim_permitted: bool
    ai_claim_permitted: bool
    audit_digest: str

    def __post_init__(self) -> None:
        expected = decide_persistent_probe_evidence(
            active_s=self.r8_active_s,
            active_h=self.r8_active_h,
            coarse_residual=self.coarse_residual,
            fine_residual=self.fine_residual,
            controls_passed=all(value for _, value in self.checks),
        )
        if (
            self.audit_id != S1_EC24_AUDIT_ID
            or self.report_sha256 != S1_EC24_REPORT_SHA256
            or self.raw_result_digest != S1_EC24_RAW_RESULT_DIGEST
            or self.source_report_sha256 != S1_EC20_REPORT_SHA256
            or self.threshold_policy != S1_EC20_THRESHOLD_POLICY
            or self.signal_margin != S1_EC24_SIGNAL_MARGIN
            or tuple(name for name, _ in self.checks) != S1_EC24_REQUIRED_CHECKS
            or any(value is not True for _, value in self.checks)
            or self.strict_threshold != self.signal_margin * self.fine_residual
            or self.active_s_margin_ratio != self.r8_active_s / self.fine_residual
            or self.active_h_margin_ratio != self.r8_active_h / self.fine_residual
            or self.technical_decision not in S1_EC24_DECISIONS
            or self.technical_decision != expected
            or self.evidence_scope
            != "controlled-persistent-state-dependent-later-field-response-only"
            or any(
                value is not False
                for value in (
                    self.field_execution_performed,
                    self.report_written,
                    self.memory_claim_permitted,
                    self.ai_claim_permitted,
                )
            )
        ):
            raise E1ConfirmationFullProbeResultAuditError(
                "S1-EC24 audit changed or exceeded its evidence boundary"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "audit_digest"
        }
        if self.audit_digest != _digest(payload):
            raise E1ConfirmationFullProbeResultAuditError(
                "S1-EC24 audit digest changed"
            )


def _all_control_residuals_zero(raw: E1FullPublishedProbeRawResult) -> bool:
    return all(
        refinement.probe_ablation_residual == 0.0
        and refinement.fixed_adapter_residual == 0.0
        and refinement.frozen_state_change == 0.0
        for refinement in raw.refinements
    )


def audit_full_published_probe_result(
    report_path: Path,
) -> E1FullProbeResultAudit:
    """Read and decide the protected report without running or writing fields."""

    report = Path(report_path).resolve()
    if not report.is_file():
        raise E1ConfirmationFullProbeResultAuditError(
            "S1-EC24 requires the protected S1-EC23 report"
        )
    encoded = report.read_bytes()
    report_sha = hashlib.sha256(encoded).hexdigest()
    if report_sha != S1_EC24_REPORT_SHA256:
        raise E1ConfirmationFullProbeResultAuditError(
            "S1-EC23 protected report hash changed"
        )
    try:
        payload = json.loads(encoded.decode("ascii"))
        raw = load_full_published_probe_raw_result(payload["raw_result"])
    except (KeyError, TypeError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise E1ConfirmationFullProbeResultAuditError(
            "S1-EC23 report cannot be typed-reloaded"
        ) from exc

    fine = raw.refinements[-1]
    checks = (
        ("protected-s1ec23-report-hash-exact", report_sha == S1_EC24_REPORT_SHA256),
        ("s1ec23-schema-and-execution-identity-exact", (
            payload.get("schema_id") == S1_EC23_SCHEMA_ID
            and payload.get("execution_id") == S1_EC23_SCHEMA_ID
        )),
        ("typed-raw-result-digest-exact", (
            raw.result_digest == S1_EC24_RAW_RESULT_DIGEST
            and payload.get("raw_result_digest") == raw.result_digest
        )),
        ("s1ec19-persistent-state-source-bound", (
            raw.source_report_sha256 == S1_EC20_REPORT_SHA256
        )),
        ("source-state-digests-unchanged-by-probe", (
            raw.source_state_digests_before == raw.source_state_digests_after
        )),
        ("registered-controls-pass", raw.all_registered_controls_passed),
        ("all-control-residuals-bit-zero", _all_control_residuals_zero(raw)),
        ("all-probe-supports-assigned-once", all(
            item.supports_assigned_once and item.initial_fields_identical_and_separate
            for item in raw.refinements
        )),
        ("coarse-to-fine-probe-residual-nonincreasing", (
            raw.convergence_nonincreasing
            and raw.r4_r8_probe_residual <= raw.r2_r4_probe_residual
        )),
        ("strict-eight-times-threshold-unchanged", (
            S1_EC24_SIGNAL_MARGIN == 8.0
            and S1_EC20_THRESHOLD_POLICY.endswith(
                "exceeds-eight-times-fine-residual"
            )
        )),
        ("source-report-contained-no-decision-or-claims", (
            raw.result_decision_permitted is False
            and raw.claims_permitted is False
            and payload.get("result_decision_permitted") is False
            and payload.get("claims_permitted") is False
        )),
    )
    if any(value is not True for _, value in checks):
        failed = ", ".join(name for name, value in checks if not value)
        raise E1ConfirmationFullProbeResultAuditError(
            f"S1-EC24 evidence gate failed: {failed}"
        )
    decision = decide_persistent_probe_evidence(
        active_s=fine.active_s_linf,
        active_h=fine.active_h_linf,
        coarse_residual=raw.r2_r4_probe_residual,
        fine_residual=raw.r4_r8_probe_residual,
        controls_passed=True,
    )
    audit_payload = {
        "audit_id": S1_EC24_AUDIT_ID,
        "report_path": str(report),
        "report_sha256": report_sha,
        "raw_result_digest": raw.result_digest,
        "source_report_sha256": raw.source_report_sha256,
        "threshold_policy": S1_EC20_THRESHOLD_POLICY,
        "signal_margin": S1_EC24_SIGNAL_MARGIN,
        "r8_active_s": fine.active_s_linf,
        "r8_active_h": fine.active_h_linf,
        "coarse_residual": raw.r2_r4_probe_residual,
        "fine_residual": raw.r4_r8_probe_residual,
        "strict_threshold": S1_EC24_SIGNAL_MARGIN * raw.r4_r8_probe_residual,
        "active_s_margin_ratio": fine.active_s_linf / raw.r4_r8_probe_residual,
        "active_h_margin_ratio": fine.active_h_linf / raw.r4_r8_probe_residual,
        "checks": checks,
        "technical_decision": decision,
        "evidence_scope": (
            "controlled-persistent-state-dependent-later-field-response-only"
        ),
        "field_execution_performed": False,
        "report_written": False,
        "memory_claim_permitted": False,
        "ai_claim_permitted": False,
    }
    return E1FullProbeResultAudit(
        **audit_payload,
        audit_digest=_digest(audit_payload),
    )
