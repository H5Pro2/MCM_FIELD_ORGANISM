"""Private S1-DJ static evidence audit for the published S1-DI report."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path


class E1A0AVHistoryEvidenceAuditError(ValueError):
    """Raised when S1-DI evidence cannot support the bounded next step."""


S1_DI_REPORT_SHA256 = (
    "831e535b0193d0bce03081545c5bda6bb4cc5655fd8b32cf77daa8a1b2fc9d1a"
)
S1_DI_RESULT_SHA256 = (
    "7fe242f667ff77b9c4e79e5800c890ab37d269c68ff6b52fccf12224645348d9"
)
S1_DI_CONTRACT_DIGEST = (
    "bce53a59cdc4afff5b88fe36ecd891a94b00167169e9b502abf0949eac9a1224"
)
S1_DJ_E1_INTEGRATOR_DIGEST = (
    "c2dfce5b78a1ba3b9aa2a903cffabbc3bacd66829c7816ee2de380c9d6d3b777"
)
S1_DJ_TRANSIENT_COUPLING_DIGEST = (
    "96d95aff9f63b77e98ba20bba22a2ae04a52aa6d5b6cf0e67795b651e0d97073"
)
S1_DJ_FROZEN_PROBE_OPERATOR_DIGEST = (
    "6ef369c6d2eb9f2059e8512f2dc950ea3ca7469dca3ee0498a0cd43507718912"
)
S1_DJ_DECISION = "FULL_S1_DC_BLOCKED_NARROW_STATE_TRANSFER_ONLY"
_EXPECTED_REPORT_FIELDS = (
    "execution_id",
    "one_shot_contract_digest",
    "history_ab_digest",
    "history_ba_digest",
    "permutation_digest",
    "producer_implementation_digest",
    "configuration_digest",
    "result_digest",
    "technical_status",
    "d_state",
    "d_total_binding",
    "result",
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _normalized_source_digest(path: Path) -> str:
    if not path.is_file():
        raise E1A0AVHistoryEvidenceAuditError(
            f"S1-DJ source is missing: {path.name}"
        )
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def current_s1_dj_implementation_digests() -> tuple[str, str, str]:
    root = Path(__file__).parent
    return (
        _normalized_source_digest(root / "e1_local_edge_plasticity.py"),
        _normalized_source_digest(root / "e1_transient_coupled_field.py"),
        _normalized_source_digest(root / "e1_frozen_transient_probe.py"),
    )


@dataclass(frozen=True, slots=True)
class E1A0AVHistoryEvidenceAudit:
    report_sha256: str
    result_sha256: str
    edge_count: int
    d_state: float
    d_total_binding: float
    controls_complete: bool
    numerical_refinement_present: bool
    analytic_global_error_bound_present: bool
    history_rerun_permitted: bool
    full_s1_dc_probe_permitted: bool
    narrow_frozen_state_transfer_contract_permitted: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        for role in ("report_sha256", "result_sha256", "audit_digest"):
            value = getattr(self, role)
            if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
                raise E1A0AVHistoryEvidenceAuditError(f"{role} is not SHA-256")
        if self.edge_count != 145:
            raise E1A0AVHistoryEvidenceAuditError(
                "S1-DJ requires the published 145-edge inventory"
            )
        if any(
            not math.isfinite(value) or value < 0.0
            for value in (self.d_state, self.d_total_binding)
        ):
            raise E1A0AVHistoryEvidenceAuditError(
                "S1-DJ metrics must be finite and nonnegative"
            )
        if self.controls_complete is not True:
            raise E1A0AVHistoryEvidenceAuditError(
                "S1-DJ published controls are incomplete"
            )
        if any(
            value is not False
            for value in (
                self.numerical_refinement_present,
                self.analytic_global_error_bound_present,
                self.history_rerun_permitted,
                self.full_s1_dc_probe_permitted,
            )
        ):
            raise E1A0AVHistoryEvidenceAuditError(
                "S1-DJ cannot release the full S1-DC branch"
            )
        if self.narrow_frozen_state_transfer_contract_permitted is not True:
            raise E1A0AVHistoryEvidenceAuditError(
                "S1-DJ bounded state-transfer contract must remain available"
            )
        if self.decision != S1_DJ_DECISION:
            raise E1A0AVHistoryEvidenceAuditError(
                "S1-DJ decision boundary changed"
            )


def audit_e1_a0_av_history_evidence(
    report_path: Path,
) -> E1A0AVHistoryEvidenceAudit:
    """Audit only published JSON and static source; execute no field role."""

    path = Path(report_path)
    if not path.is_file():
        raise E1A0AVHistoryEvidenceAuditError("S1-DI report is missing")
    raw = path.read_bytes()
    report_sha256 = hashlib.sha256(raw).hexdigest()
    if report_sha256 != S1_DI_REPORT_SHA256:
        raise E1A0AVHistoryEvidenceAuditError("S1-DI report digest changed")
    try:
        report = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise E1A0AVHistoryEvidenceAuditError(
            "S1-DI report is not canonical JSON"
        ) from exc
    if tuple(report) != _EXPECTED_REPORT_FIELDS:
        raise E1A0AVHistoryEvidenceAuditError("S1-DI report fields changed")
    if (
        report["execution_id"] != "e1.a0-av-history.s1di.once.v1"
        or report["one_shot_contract_digest"] != S1_DI_CONTRACT_DIGEST
        or report["technical_status"]
        != "E1_A0_AV_HISTORY_STATES_PRODUCED"
        or report["result_digest"] != S1_DI_RESULT_SHA256
    ):
        raise E1A0AVHistoryEvidenceAuditError("S1-DI report binding changed")
    result = report["result"]
    if not isinstance(result, dict):
        raise E1A0AVHistoryEvidenceAuditError("S1-DI result is invalid")
    result_sha256 = _digest(result)
    if result_sha256 != S1_DI_RESULT_SHA256:
        raise E1A0AVHistoryEvidenceAuditError("S1-DI result digest changed")

    try:
        left = result["b_ab"]
        right = result["b_ba"]
        left_bindings = left["edge_bindings"]
        right_bindings = right["edge_bindings"]
        audits = result["arm_audits"]
    except (KeyError, TypeError) as exc:
        raise E1A0AVHistoryEvidenceAuditError(
            "S1-DI state roles are incomplete"
        ) from exc
    if (
        left["edge_inventory_digest"] != right["edge_inventory_digest"]
        or left["contract"] != right["contract"]
        or len(left_bindings) != 145
        or len(right_bindings) != 145
    ):
        raise E1A0AVHistoryEvidenceAuditError(
            "S1-DI E1 inventories are incompatible"
        )
    left_edges = tuple(
        (item["first_neuron_id"], item["second_neuron_id"])
        for item in left_bindings
    )
    right_edges = tuple(
        (item["first_neuron_id"], item["second_neuron_id"])
        for item in right_bindings
    )
    if left_edges != right_edges:
        raise E1A0AVHistoryEvidenceAuditError("S1-DI edge order changed")
    left_values = tuple(float(item["binding"]) for item in left_bindings)
    right_values = tuple(float(item["binding"]) for item in right_bindings)
    d_state = max(
        abs(first - second)
        for first, second in zip(left_values, right_values, strict=True)
    )
    d_total_binding = abs(math.fsum(left_values) - math.fsum(right_values))
    if d_state != report["d_state"] or d_total_binding != report["d_total_binding"]:
        raise E1A0AVHistoryEvidenceAuditError(
            "S1-DI published metrics do not match its states"
        )
    controls_complete = (
        isinstance(audits, list)
        and tuple(item.get("history_id") for item in audits) == ("ab", "ba")
        and all(
            item.get("source_support_count") == 220
            and item.get("assigned_event_count") == 220
            and item.get("p0_field_digest") == item.get("a0_field_digest")
            and item.get("resource_budget_error") == 0.0
            and item.get("all_adapters_ablated") is True
            for item in audits
        )
    )
    expected_sources = (
        S1_DJ_E1_INTEGRATOR_DIGEST,
        S1_DJ_TRANSIENT_COUPLING_DIGEST,
        S1_DJ_FROZEN_PROBE_OPERATOR_DIGEST,
    )
    if current_s1_dj_implementation_digests() != expected_sources:
        raise E1A0AVHistoryEvidenceAuditError(
            "S1-DJ implementation evidence changed"
        )

    audit_payload = {
        "contract_id": "e1.a0-av-history.evidence-audit.s1dj.v1",
        "report_sha256": report_sha256,
        "result_sha256": result_sha256,
        "implementation_digests": expected_sources,
        "edge_count": len(left_bindings),
        "d_state": d_state,
        "d_total_binding": d_total_binding,
        "controls_complete": controls_complete,
        "numerical_refinement_present": False,
        "analytic_global_error_bound_present": False,
        "history_rerun_permitted": False,
        "full_s1_dc_probe_permitted": False,
        "narrow_frozen_state_transfer_contract_permitted": True,
        "decision": S1_DJ_DECISION,
    }
    return E1A0AVHistoryEvidenceAudit(
        report_sha256=report_sha256,
        result_sha256=result_sha256,
        edge_count=len(left_bindings),
        d_state=d_state,
        d_total_binding=d_total_binding,
        controls_complete=controls_complete,
        numerical_refinement_present=False,
        analytic_global_error_bound_present=False,
        history_rerun_permitted=False,
        full_s1_dc_probe_permitted=False,
        narrow_frozen_state_transfer_contract_permitted=True,
        decision=S1_DJ_DECISION,
        audit_digest=_digest(audit_payload),
    )
