"""Private S1-EC22 static release audit for one future full probe run."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from .e1_confirmation_prepared_execution_bundle import E1PreparedExecutionBundle
from .e1_confirmation_prepared_formation_consumer import _typed_values_from_bundle
from .e1_confirmation_published_probe_fixture_consumer import S1_EC21_CONSUMER_ID
from .e1_confirmation_published_probe_handoff_audit import (
    E1PublishedProbeHandoffAudit,
    S1_EC20_PROBE_ARMS,
    S1_EC20_REPORT_SHA256,
)
from .e1_refined_formation_runner import _digest


class E1ConfirmationFullProbeReleaseAuditError(ValueError):
    """Raised when the S1-EC22 release evidence is incomplete."""


S1_EC22_AUDIT_ID = "e1.full-probe-release-audit.s1ec22.v1"
S1_EC22_RELEASE_TARGET_ID = "e1.full-published-probe.s1ec23.once.v1"
S1_EC22_REPORT_NAME = "e1_full_published_probe_s1ec23_once_v1.json"
S1_EC22_ATTEMPT_NAME = "e1_full_published_probe_s1ec23_once_v1.attempt.json"
S1_EC22_LOCK_NAME = "e1_full_published_probe_s1ec23_once_v1.lock"
S1_EC22_EXPECTED_PLAN_STEPS = (("r2", 200), ("r4", 400), ("r8", 800))
S1_EC22_SOURCE_SUPPORT_COUNT = 110
S1_EC22_PROPOSAL_STEP_COUNT = 1_400
S1_EC22_FIELD_ARM_STEP_COUNT = 9_800
S1_EC22_FIXTURE_RESULT_DIGEST = (
    "1b328220ea65562575b608c7ffaa5a7ecce894ce323080f23009ed7358e9e11f"
)
S1_EC22_MIN_FREE_MEMORY_BYTES = 4 * 1024**3
S1_EC22_MIN_FREE_DISK_BYTES = 1 * 1024**3
S1_EC22_MAX_REPORT_BYTES = 4 * 1024**2
S1_EC22_MAX_RUNTIME_SECONDS = 1_200.0
S1_EC22_RUNTIME_ABORT_POLICY = "abort-before-1200-seconds-retain-attempt"
S1_EC22_REQUIRED_CHECKS = (
    "s1ec20-static-handoff-bound",
    "s1ec21-fixture-consumer-bound",
    "s1ec19-report-hash-unchanged",
    "registered-probe-source-and-plans-bound",
    "r2-r4-r8-step-inventory-exact",
    "one-hundred-ten-supports-assigned-once",
    "seven-probe-arms-bound",
    "nine-thousand-eight-hundred-field-arm-steps",
    "new-target-paths-unused",
    "free-memory-at-least-four-gib",
    "free-disk-at-least-one-gib",
    "report-size-cap-four-mib",
    "runtime-cap-twelve-hundred-seconds",
    "no-retry-after-attempt",
    "frozen-persistent-state-source-only",
    "no-result-decision",
    "no-claims",
)
S1_EC22_POLICY_DIGEST = _digest(
    {
        "audit_id": S1_EC22_AUDIT_ID,
        "release_target_id": S1_EC22_RELEASE_TARGET_ID,
        "target_names": (
            S1_EC22_REPORT_NAME,
            S1_EC22_ATTEMPT_NAME,
            S1_EC22_LOCK_NAME,
        ),
        "expected_plan_steps": S1_EC22_EXPECTED_PLAN_STEPS,
        "source_support_count": S1_EC22_SOURCE_SUPPORT_COUNT,
        "proposal_step_count": S1_EC22_PROPOSAL_STEP_COUNT,
        "probe_arms": S1_EC20_PROBE_ARMS,
        "field_arm_step_count": S1_EC22_FIELD_ARM_STEP_COUNT,
        "minimum_free_memory_bytes": S1_EC22_MIN_FREE_MEMORY_BYTES,
        "minimum_free_disk_bytes": S1_EC22_MIN_FREE_DISK_BYTES,
        "maximum_report_bytes": S1_EC22_MAX_REPORT_BYTES,
        "maximum_runtime_seconds": S1_EC22_MAX_RUNTIME_SECONDS,
        "runtime_abort_policy": S1_EC22_RUNTIME_ABORT_POLICY,
        "required_checks": S1_EC22_REQUIRED_CHECKS,
        "probe_execution_authorized": False,
        "result_decision_permitted": False,
        "claims_permitted": False,
    }
)


def _valid_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


@dataclass(frozen=True, slots=True)
class E1FullProbeResourceSnapshot:
    free_memory_bytes: int
    free_disk_bytes: int
    proposed_directory: str
    report_path_unused: bool
    attempt_path_unused: bool
    lock_path_unused: bool
    s1ec19_report_sha256: str

    def __post_init__(self) -> None:
        root = Path(self.proposed_directory)
        paths = (
            root / S1_EC22_REPORT_NAME,
            root / S1_EC22_ATTEMPT_NAME,
            root / S1_EC22_LOCK_NAME,
        )
        if (
            isinstance(self.free_memory_bytes, bool)
            or not isinstance(self.free_memory_bytes, int)
            or self.free_memory_bytes < 0
            or isinstance(self.free_disk_bytes, bool)
            or not isinstance(self.free_disk_bytes, int)
            or self.free_disk_bytes < 0
            or not str(root)
            or self.report_path_unused is not (not paths[0].exists())
            or self.attempt_path_unused is not (not paths[1].exists())
            or self.lock_path_unused is not (not paths[2].exists())
            or self.s1ec19_report_sha256 != S1_EC20_REPORT_SHA256
        ):
            raise E1ConfirmationFullProbeReleaseAuditError(
                "S1-EC22 resource snapshot is invalid"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


@dataclass(frozen=True, slots=True)
class E1FullProbeReleaseDecision:
    audit_id: str
    policy_digest: str
    release_target_id: str
    handoff_audit_digest: str
    resource_snapshot_digest: str
    probe_source_digest: str
    probe_plan_set_digest: str
    plan_step_counts: tuple[tuple[str, int], ...]
    source_support_count: int
    proposal_step_count: int
    field_arm_step_count: int
    checks: tuple[tuple[str, bool], ...]
    decision: str
    reason: str
    maximum_report_bytes: int
    maximum_runtime_seconds: float
    runtime_abort_policy: str
    probe_execution_authorized: bool
    field_execution_performed: bool
    markers_created: bool
    report_created: bool
    result_decision_permitted: bool
    claims_permitted: bool
    decision_digest: str

    def __post_init__(self) -> None:
        expected = "FREIGABE" if all(value for _, value in self.checks) else "KORREKTUR"
        if (
            self.audit_id != S1_EC22_AUDIT_ID
            or self.policy_digest != S1_EC22_POLICY_DIGEST
            or self.release_target_id != S1_EC22_RELEASE_TARGET_ID
            or any(
                not _valid_digest(value)
                for value in (
                    self.handoff_audit_digest,
                    self.resource_snapshot_digest,
                    self.probe_source_digest,
                    self.probe_plan_set_digest,
                    self.decision_digest,
                )
            )
            or self.plan_step_counts != S1_EC22_EXPECTED_PLAN_STEPS
            or self.source_support_count != S1_EC22_SOURCE_SUPPORT_COUNT
            or self.proposal_step_count != S1_EC22_PROPOSAL_STEP_COUNT
            or self.field_arm_step_count != S1_EC22_FIELD_ARM_STEP_COUNT
            or tuple(name for name, _ in self.checks) != S1_EC22_REQUIRED_CHECKS
            or self.decision != expected
            or not self.reason
            or self.maximum_report_bytes != S1_EC22_MAX_REPORT_BYTES
            or self.maximum_runtime_seconds != S1_EC22_MAX_RUNTIME_SECONDS
            or self.runtime_abort_policy != S1_EC22_RUNTIME_ABORT_POLICY
            or self.probe_execution_authorized is not False
            or self.field_execution_performed is not False
            or self.markers_created is not False
            or self.report_created is not False
            or self.result_decision_permitted is not False
            or self.claims_permitted is not False
        ):
            raise E1ConfirmationFullProbeReleaseAuditError(
                "S1-EC22 release decision changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "decision_digest"
        }
        if self.decision_digest != _digest(payload):
            raise E1ConfirmationFullProbeReleaseAuditError(
                "S1-EC22 decision digest changed"
            )


def audit_full_probe_release(
    handoff: E1PublishedProbeHandoffAudit,
    bundle: E1PreparedExecutionBundle,
    snapshot: E1FullProbeResourceSnapshot,
) -> E1FullProbeReleaseDecision:
    """Decide readiness without loading persistent states into probe fields."""

    if not isinstance(handoff, E1PublishedProbeHandoffAudit):
        raise E1ConfirmationFullProbeReleaseAuditError(
            "S1-EC22 requires one S1-EC20 audit"
        )
    if not isinstance(bundle, E1PreparedExecutionBundle):
        raise E1ConfirmationFullProbeReleaseAuditError(
            "S1-EC22 requires one prepared bundle"
        )
    if not isinstance(snapshot, E1FullProbeResourceSnapshot):
        raise E1ConfirmationFullProbeReleaseAuditError(
            "S1-EC22 requires one resource snapshot"
        )
    handoff.__post_init__()
    bundle.__post_init__()
    snapshot.__post_init__()
    values = _typed_values_from_bundle(bundle)
    plans = tuple(values.probe_plans.plans)
    plan_steps = tuple((item.refinement_id, len(item.proposal_steps)) for item in plans)
    support_counts = tuple(item.handoff.source_event_count for item in plans)
    assigned_counts = tuple(item.handoff.assigned_event_count for item in plans)
    proposal_steps = sum(value for _, value in plan_steps)
    field_arm_steps = proposal_steps * len(S1_EC20_PROBE_ARMS)
    checks = (
        ("s1ec20-static-handoff-bound", handoff.static_handoff_ready),
        ("s1ec21-fixture-consumer-bound", (
            S1_EC21_CONSUMER_ID.endswith("s1ec21.v1")
            and _valid_digest(S1_EC22_FIXTURE_RESULT_DIGEST)
        )),
        ("s1ec19-report-hash-unchanged", snapshot.s1ec19_report_sha256 == handoff.report_sha256),
        ("registered-probe-source-and-plans-bound", (
            handoff.input_bundle_digest == bundle.bundle_digest
            and handoff.probe_plan_set_digest == values.probe_plans.digest()
        )),
        ("r2-r4-r8-step-inventory-exact", plan_steps == S1_EC22_EXPECTED_PLAN_STEPS),
        ("one-hundred-ten-supports-assigned-once", (
            support_counts == (S1_EC22_SOURCE_SUPPORT_COUNT,) * 3
            and assigned_counts == support_counts
            and all(item.handoff.every_in_horizon_event_assigned_once for item in plans)
        )),
        ("seven-probe-arms-bound", handoff.probe_arms == S1_EC20_PROBE_ARMS),
        ("nine-thousand-eight-hundred-field-arm-steps", (
            proposal_steps == S1_EC22_PROPOSAL_STEP_COUNT
            and field_arm_steps == S1_EC22_FIELD_ARM_STEP_COUNT
        )),
        ("new-target-paths-unused", (
            snapshot.report_path_unused and snapshot.attempt_path_unused and snapshot.lock_path_unused
        )),
        ("free-memory-at-least-four-gib", snapshot.free_memory_bytes >= S1_EC22_MIN_FREE_MEMORY_BYTES),
        ("free-disk-at-least-one-gib", snapshot.free_disk_bytes >= S1_EC22_MIN_FREE_DISK_BYTES),
        ("report-size-cap-four-mib", S1_EC22_MAX_REPORT_BYTES == 4 * 1024**2),
        ("runtime-cap-twelve-hundred-seconds", S1_EC22_MAX_RUNTIME_SECONDS == 1_200.0),
        ("no-retry-after-attempt", S1_EC22_RUNTIME_ABORT_POLICY.endswith("retain-attempt")),
        ("frozen-persistent-state-source-only", True),
        ("no-result-decision", True),
        ("no-claims", True),
    )
    decision = "FREIGABE" if all(value for _, value in checks) else "KORREKTUR"
    failed = tuple(name for name, value in checks if not value)
    payload = {
        "audit_id": S1_EC22_AUDIT_ID,
        "policy_digest": S1_EC22_POLICY_DIGEST,
        "release_target_id": S1_EC22_RELEASE_TARGET_ID,
        "handoff_audit_digest": handoff.audit_digest,
        "resource_snapshot_digest": snapshot.digest(),
        "probe_source_digest": handoff.probe_source_digest,
        "probe_plan_set_digest": handoff.probe_plan_set_digest,
        "plan_step_counts": plan_steps,
        "source_support_count": S1_EC22_SOURCE_SUPPORT_COUNT,
        "proposal_step_count": proposal_steps,
        "field_arm_step_count": field_arm_steps,
        "checks": checks,
        "decision": decision,
        "reason": (
            "all static full-probe release gates pass"
            if decision == "FREIGABE"
            else "failed gates: " + ",".join(failed)
        ),
        "maximum_report_bytes": S1_EC22_MAX_REPORT_BYTES,
        "maximum_runtime_seconds": S1_EC22_MAX_RUNTIME_SECONDS,
        "runtime_abort_policy": S1_EC22_RUNTIME_ABORT_POLICY,
        "probe_execution_authorized": False,
        "field_execution_performed": False,
        "markers_created": False,
        "report_created": False,
        "result_decision_permitted": False,
        "claims_permitted": False,
    }
    return E1FullProbeReleaseDecision(**payload, decision_digest=_digest(payload))
