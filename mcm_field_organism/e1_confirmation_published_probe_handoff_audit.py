"""Private S1-EC20 static handoff audit for the published S1-EC19 states."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

from .e1_confirmation_full_formation_handoff import (
    S1_EC14_EDGE_BINDING_COUNT,
    S1_EC14_PROBE_CANDIDATE_ROLES,
    S1_EC14_STATE_COUNT,
    load_full_formation_handoff_payload,
)
from .e1_confirmation_full_published_one_shot import S1_EC19_SCHEMA_ID
from .e1_confirmation_prepared_execution_bundle import E1PreparedExecutionBundle
from .e1_confirmation_prepared_formation_consumer import (
    S1_EC7_FORMATION_ARMS,
    _typed_values_from_bundle,
)
from .e1_frozen_state_transfer import _state_payload
from .e1_frozen_state_transfer_contract import _probe_digest
from .e1_refined_formation_runner import _digest


class E1ConfirmationPublishedProbeHandoffAuditError(ValueError):
    """Raised when the S1-EC20 static probe handoff is incomplete."""


S1_EC20_AUDIT_ID = "e1.published-probe-handoff-audit.s1ec20.v1"
S1_EC20_REPORT_SHA256 = (
    "93cc94ddb18f80919067ff4e29ccae5aa038bb436d72584acef2d38e57be1fcc"
)
S1_EC20_REFINEMENTS = ("r2", "r4", "r8")
S1_EC20_ACTIVE_STATE_ROLES = tuple(
    f"{refinement}:{arm}"
    for refinement in S1_EC20_REFINEMENTS
    for arm in ("ab", "ba")
)
S1_EC20_NUMERICAL_CONTROL_ROLES = S1_EC20_ACTIVE_STATE_ROLES[:4]
S1_EC20_DECISION_CANDIDATE_ROLES = ("r8:ab", "r8:ba")
S1_EC20_STATE_EQUIVALENCE_CLASSES = (
    ("r2:ab", "r2:ab_identity"),
    ("r4:ab", "r4:ab_identity"),
    ("r8:ab", "r8:ab_identity"),
    tuple(
        f"{refinement}:{arm}"
        for refinement in S1_EC20_REFINEMENTS
        for arm in ("ab_formation_ablated", "ba_formation_ablated")
    ),
)
S1_EC20_PROBE_ARMS = (
    "p0",
    "ab0",
    "ba0",
    "ab1",
    "ba1",
    "abf",
    "baf",
)
S1_EC20_REQUIRED_IDENTITIES = (
    "seven-fresh-fields-value-identical-and-object-separate",
    "same-av-probe-source-and-supports-for-r2-r4-r8",
    "p0-equals-ab0-equals-ba0-bit-exact",
    "ab1-equals-abf-bit-exact",
    "ba1-equals-baf-bit-exact",
    "all-six-active-e1-states-frozen-during-probe",
    "all-probe-supports-assigned-exactly-once",
    "r2-r4-and-r4-r8-probe-residuals-reported",
    "no-posthoc-source-threshold-or-parameter-change",
)
S1_EC20_METRICS = (
    "active_ab_ba_s_linf",
    "active_ab_ba_h_linf",
    "probe_ablation_residual",
    "fixed_adapter_residual",
    "frozen_state_change",
    "r2_r4_probe_residual",
    "r4_r8_probe_residual",
)
S1_EC20_THRESHOLD_POLICY = (
    "no-decision-until-fine-active-signal-exceeds-eight-times-fine-residual"
)


def _valid_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


@dataclass(frozen=True, slots=True)
class E1PublishedProbeHandoffAudit:
    audit_id: str
    report_path: str
    report_sha256: str
    report_bytes: int
    execution_id: str
    formation_result_digest: str
    handoff_payload_digest: str
    input_bundle_digest: str
    state_count: int
    edge_binding_count: int
    all_state_roles: tuple[str, ...]
    all_state_digests: tuple[tuple[str, str], ...]
    unique_state_digest_count: int
    state_equivalence_classes: tuple[tuple[str, ...], ...]
    handoff_candidate_roles: tuple[str, ...]
    active_state_roles: tuple[str, ...]
    numerical_control_roles: tuple[str, ...]
    decision_candidate_roles: tuple[str, ...]
    probe_source_digest: str
    probe_plan_set_digest: str
    probe_plan_digests: tuple[tuple[str, str], ...]
    probe_arms: tuple[str, ...]
    required_identities: tuple[str, ...]
    metrics: tuple[str, ...]
    threshold_policy: str
    static_handoff_ready: bool
    probe_execution_permitted: bool
    result_decision_permitted: bool
    claims_permitted: bool
    audit_digest: str

    def __post_init__(self) -> None:
        all_roles = tuple(
            f"{refinement}:{arm}"
            for refinement in S1_EC20_REFINEMENTS
            for arm in S1_EC7_FORMATION_ARMS
        )
        if (
            self.audit_id != S1_EC20_AUDIT_ID
            or self.report_sha256 != S1_EC20_REPORT_SHA256
            or self.report_bytes <= 0
            or not self.execution_id.endswith("s1ec19.once.v1")
            or any(
                not _valid_digest(value)
                for value in (
                    self.formation_result_digest,
                    self.handoff_payload_digest,
                    self.input_bundle_digest,
                    self.probe_source_digest,
                    self.probe_plan_set_digest,
                    self.audit_digest,
                )
            )
            or self.state_count != S1_EC14_STATE_COUNT
            or self.edge_binding_count != S1_EC14_EDGE_BINDING_COUNT
            or self.all_state_roles != all_roles
            or tuple(role for role, _ in self.all_state_digests) != all_roles
            or any(not _valid_digest(value) for _, value in self.all_state_digests)
            or self.unique_state_digest_count != 7
            or self.state_equivalence_classes
            != S1_EC20_STATE_EQUIVALENCE_CLASSES
            or self.handoff_candidate_roles != S1_EC14_PROBE_CANDIDATE_ROLES
            or self.active_state_roles != S1_EC20_ACTIVE_STATE_ROLES
            or self.numerical_control_roles != S1_EC20_NUMERICAL_CONTROL_ROLES
            or self.decision_candidate_roles != S1_EC20_DECISION_CANDIDATE_ROLES
            or tuple(role for role, _ in self.probe_plan_digests)
            != S1_EC20_REFINEMENTS
            or any(not _valid_digest(value) for _, value in self.probe_plan_digests)
            or self.probe_arms != S1_EC20_PROBE_ARMS
            or self.required_identities != S1_EC20_REQUIRED_IDENTITIES
            or self.metrics != S1_EC20_METRICS
            or self.threshold_policy != S1_EC20_THRESHOLD_POLICY
            or self.static_handoff_ready is not True
            or self.probe_execution_permitted is not False
            or self.result_decision_permitted is not False
            or self.claims_permitted is not False
        ):
            raise E1ConfirmationPublishedProbeHandoffAuditError(
                "S1-EC20 audit changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "audit_digest"
        }
        if self.audit_digest != _digest(payload):
            raise E1ConfirmationPublishedProbeHandoffAuditError(
                "S1-EC20 audit digest changed"
            )
        digest_by_role = dict(self.all_state_digests)
        if any(
            len({digest_by_role[role] for role in roles}) != 1
            for roles in self.state_equivalence_classes
        ):
            raise E1ConfirmationPublishedProbeHandoffAuditError(
                "S1-EC20 state control equivalence changed"
            )


def audit_published_probe_handoff(
    report_path: Path,
    bundle: E1PreparedExecutionBundle,
    *,
    expected_report_sha256: str = S1_EC20_REPORT_SHA256,
) -> E1PublishedProbeHandoffAudit:
    """Audit states and probe inputs without constructing a probe field."""

    path = Path(report_path).resolve()
    if not isinstance(bundle, E1PreparedExecutionBundle) or not path.is_file():
        raise E1ConfirmationPublishedProbeHandoffAuditError(
            "S1-EC20 requires one report and its prepared bundle"
        )
    bundle.__post_init__()
    raw = path.read_bytes()
    observed_sha256 = hashlib.sha256(raw).hexdigest()
    if (
        expected_report_sha256 != S1_EC20_REPORT_SHA256
        or observed_sha256 != expected_report_sha256
    ):
        raise E1ConfirmationPublishedProbeHandoffAuditError(
            "S1-EC20 report hash changed"
        )
    try:
        report = json.loads(raw.decode("ascii"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise E1ConfirmationPublishedProbeHandoffAuditError(
            "S1-EC20 report is not canonical JSON"
        ) from exc
    if (
        report.get("schema_id") != S1_EC19_SCHEMA_ID
        or report.get("input_bundle_digest") != bundle.bundle_digest
        or report.get("full_formation_executed") is not True
        or report.get("probe_execution_permitted") is not False
        or report.get("claims_permitted") is not False
        or _digest(report.get("payload")) != report.get("handoff_payload_digest")
    ):
        raise E1ConfirmationPublishedProbeHandoffAuditError(
            "S1-EC20 report controls changed"
        )
    loaded = load_full_formation_handoff_payload(report["payload"])
    if loaded.result_digest != report.get("formation_result_digest"):
        raise E1ConfirmationPublishedProbeHandoffAuditError(
            "S1-EC20 typed result digest changed"
        )

    all_states = tuple(
        (
            f"{refinement.refinement_id}:{arm.arm_id}",
            _digest(_state_payload(arm.output_state)),
        )
        for refinement in loaded.refinements
        for arm in refinement.arms
    )
    values = _typed_values_from_bundle(bundle)
    probe_plan_digests = tuple(
        (plan.refinement_id, plan.digest()) for plan in values.probe_plans.plans
    )
    payload = {
        "audit_id": S1_EC20_AUDIT_ID,
        "report_path": str(path),
        "report_sha256": observed_sha256,
        "report_bytes": len(raw),
        "execution_id": report["execution_id"],
        "formation_result_digest": loaded.result_digest,
        "handoff_payload_digest": report["handoff_payload_digest"],
        "input_bundle_digest": bundle.bundle_digest,
        "state_count": S1_EC14_STATE_COUNT,
        "edge_binding_count": S1_EC14_EDGE_BINDING_COUNT,
        "all_state_roles": tuple(role for role, _ in all_states),
        "all_state_digests": all_states,
        "unique_state_digest_count": len({value for _, value in all_states}),
        "state_equivalence_classes": S1_EC20_STATE_EQUIVALENCE_CLASSES,
        "handoff_candidate_roles": S1_EC14_PROBE_CANDIDATE_ROLES,
        "active_state_roles": S1_EC20_ACTIVE_STATE_ROLES,
        "numerical_control_roles": S1_EC20_NUMERICAL_CONTROL_ROLES,
        "decision_candidate_roles": S1_EC20_DECISION_CANDIDATE_ROLES,
        "probe_source_digest": _probe_digest(values.probe_sequences),
        "probe_plan_set_digest": values.probe_plans.digest(),
        "probe_plan_digests": probe_plan_digests,
        "probe_arms": S1_EC20_PROBE_ARMS,
        "required_identities": S1_EC20_REQUIRED_IDENTITIES,
        "metrics": S1_EC20_METRICS,
        "threshold_policy": S1_EC20_THRESHOLD_POLICY,
        "static_handoff_ready": True,
        "probe_execution_permitted": False,
        "result_decision_permitted": False,
        "claims_permitted": False,
    }
    return E1PublishedProbeHandoffAudit(
        **payload,
        audit_digest=_digest(payload),
    )
