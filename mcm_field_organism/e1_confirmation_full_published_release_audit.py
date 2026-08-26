"""Private S1-EC18 static release audit for one future full published run."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from .e1_confirmation_full_formation_handoff import S1_EC14_CONTRACT_DIGEST
from .e1_confirmation_full_formation_handoff_publisher import (
    S1_EC15_POLICY_DIGEST,
)
from .e1_confirmation_full_formation_resource_preflight import (
    E1FullFormationResourcePreflight,
)
from .e1_confirmation_full_published_run_contract import S1_EC16_POLICY_DIGEST
from .e1_confirmation_full_published_run_fixture import S1_EC17_POLICY_DIGEST
from .e1_refined_formation_runner import _digest


class E1ConfirmationFullPublishedReleaseAuditError(ValueError):
    """Raised when the S1-EC18 release evidence is incomplete."""


S1_EC18_AUDIT_ID = "e1.full-published-release-audit.s1ec18.v1"
S1_EC18_DECISIONS = ("FREIGABE", "KORREKTUR", "STOPP")
S1_EC18_RELEASE_TARGET_ID = "e1.full-formation-published-run.s1ec19.once.v1"
S1_EC18_REPORT_NAME = "e1_full_formation_published_s1ec19_once_v1.json"
S1_EC18_ATTEMPT_NAME = (
    "e1_full_formation_published_s1ec19_once_v1.attempt.json"
)
S1_EC18_LOCK_NAME = "e1_full_formation_published_s1ec19_once_v1.lock"
S1_EC18_MIN_FREE_MEMORY_BYTES = 4 * 1024**3
S1_EC18_MIN_FREE_DISK_BYTES = 1 * 1024**3
S1_EC18_MAX_REPORT_BYTES = 16 * 1024**2
S1_EC18_MAX_RUNTIME_SECONDS = 900.0
S1_EC18_REFERENCE_RUNTIME_SECONDS = 430.2
S1_EC18_RUNTIME_ABORT_POLICY = "abort-before-900-seconds-retain-attempt"
S1_EC18_REQUIRED_CHECKS = (
    "s1ec12-resource-gate-passed",
    "s1ec14-complete-handoff-bound",
    "s1ec15-atomic-publisher-bound",
    "s1ec16-aggregate-policy-bound",
    "s1ec17-end-to-end-fixture-bound",
    "s1ec13-reference-report-unchanged",
    "new-target-paths-unused",
    "free-memory-at-least-four-gib",
    "free-disk-at-least-one-gib",
    "report-size-cap-sixteen-mib",
    "runtime-cap-nine-hundred-seconds",
    "no-retry-after-attempt",
    "no-canonical-path",
    "no-probe",
    "no-claims",
)
S1_EC18_POLICY_DIGEST = _digest(
    {
        "audit_id": S1_EC18_AUDIT_ID,
        "release_target_id": S1_EC18_RELEASE_TARGET_ID,
        "target_names": (
            S1_EC18_REPORT_NAME,
            S1_EC18_ATTEMPT_NAME,
            S1_EC18_LOCK_NAME,
        ),
        "required_checks": S1_EC18_REQUIRED_CHECKS,
        "minimum_free_memory_bytes": S1_EC18_MIN_FREE_MEMORY_BYTES,
        "minimum_free_disk_bytes": S1_EC18_MIN_FREE_DISK_BYTES,
        "maximum_report_bytes": S1_EC18_MAX_REPORT_BYTES,
        "maximum_runtime_seconds": S1_EC18_MAX_RUNTIME_SECONDS,
        "reference_runtime_seconds": S1_EC18_REFERENCE_RUNTIME_SECONDS,
        "runtime_abort_policy": S1_EC18_RUNTIME_ABORT_POLICY,
        "handoff_contract_digest": S1_EC14_CONTRACT_DIGEST,
        "publisher_policy_digest": S1_EC15_POLICY_DIGEST,
        "aggregate_policy_digest": S1_EC16_POLICY_DIGEST,
        "fixture_policy_digest": S1_EC17_POLICY_DIGEST,
        "execution_authorized": False,
        "probe_execution_permitted": False,
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
class E1FullPublishedResourceSnapshot:
    free_memory_bytes: int
    free_disk_bytes: int
    proposed_directory: str
    report_path_unused: bool
    attempt_path_unused: bool
    lock_path_unused: bool
    s1ec13_report_sha256: str
    s1ec13_reference_runtime_seconds: float

    def __post_init__(self) -> None:
        root = Path(self.proposed_directory)
        paths = (
            root / S1_EC18_REPORT_NAME,
            root / S1_EC18_ATTEMPT_NAME,
            root / S1_EC18_LOCK_NAME,
        )
        if (
            isinstance(self.free_memory_bytes, bool)
            or not isinstance(self.free_memory_bytes, int)
            or self.free_memory_bytes < 0
            or isinstance(self.free_disk_bytes, bool)
            or not isinstance(self.free_disk_bytes, int)
            or self.free_disk_bytes < 0
            or not str(root)
            or tuple(path.name for path in paths)
            != (
                S1_EC18_REPORT_NAME,
                S1_EC18_ATTEMPT_NAME,
                S1_EC18_LOCK_NAME,
            )
            or self.report_path_unused is not (not paths[0].exists())
            or self.attempt_path_unused is not (not paths[1].exists())
            or self.lock_path_unused is not (not paths[2].exists())
            or not _valid_digest(self.s1ec13_report_sha256)
            or self.s1ec13_reference_runtime_seconds
            != S1_EC18_REFERENCE_RUNTIME_SECONDS
        ):
            raise E1ConfirmationFullPublishedReleaseAuditError(
                "S1-EC18 resource snapshot is invalid"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


@dataclass(frozen=True, slots=True)
class E1FullPublishedReleaseDecision:
    audit_id: str
    policy_digest: str
    release_target_id: str
    resource_snapshot_digest: str
    resource_preflight_digest: str
    checks: tuple[tuple[str, bool], ...]
    decision: str
    reason: str
    maximum_report_bytes: int
    maximum_runtime_seconds: float
    runtime_abort_policy: str
    execution_authorized: bool
    field_execution_performed: bool
    markers_created: bool
    report_created: bool
    canonical_execution_permitted: bool
    probe_execution_permitted: bool
    claims_permitted: bool
    decision_digest: str

    def __post_init__(self) -> None:
        expected_decision = (
            "FREIGABE" if all(value for _, value in self.checks) else "KORREKTUR"
        )
        if (
            self.audit_id != S1_EC18_AUDIT_ID
            or self.policy_digest != S1_EC18_POLICY_DIGEST
            or self.release_target_id != S1_EC18_RELEASE_TARGET_ID
            or not _valid_digest(self.resource_snapshot_digest)
            or not _valid_digest(self.resource_preflight_digest)
            or tuple(name for name, _ in self.checks) != S1_EC18_REQUIRED_CHECKS
            or self.decision not in S1_EC18_DECISIONS
            or self.decision != expected_decision
            or not self.reason
            or self.maximum_report_bytes != S1_EC18_MAX_REPORT_BYTES
            or self.maximum_runtime_seconds != S1_EC18_MAX_RUNTIME_SECONDS
            or self.runtime_abort_policy != S1_EC18_RUNTIME_ABORT_POLICY
            or self.execution_authorized is not False
            or self.field_execution_performed is not False
            or self.markers_created is not False
            or self.report_created is not False
            or self.canonical_execution_permitted is not False
            or self.probe_execution_permitted is not False
            or self.claims_permitted is not False
        ):
            raise E1ConfirmationFullPublishedReleaseAuditError(
                "S1-EC18 release decision changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "decision_digest"
        }
        if self.decision_digest != _digest(payload):
            raise E1ConfirmationFullPublishedReleaseAuditError(
                "S1-EC18 decision digest changed"
            )


def audit_full_published_run_release(
    preflight: E1FullFormationResourcePreflight,
    snapshot: E1FullPublishedResourceSnapshot,
    *,
    expected_s1ec13_report_sha256: str,
) -> E1FullPublishedReleaseDecision:
    """Decide release readiness without creating paths, markers, or a run."""

    if not isinstance(preflight, E1FullFormationResourcePreflight):
        raise E1ConfirmationFullPublishedReleaseAuditError(
            "S1-EC18 requires one accepted S1-EC12 preflight"
        )
    if not isinstance(snapshot, E1FullPublishedResourceSnapshot):
        raise E1ConfirmationFullPublishedReleaseAuditError(
            "S1-EC18 requires one explicit resource snapshot"
        )
    preflight.__post_init__()
    snapshot.__post_init__()
    checks = (
        ("s1ec12-resource-gate-passed", preflight.resource_gate_passed),
        ("s1ec14-complete-handoff-bound", _valid_digest(S1_EC14_CONTRACT_DIGEST)),
        ("s1ec15-atomic-publisher-bound", _valid_digest(S1_EC15_POLICY_DIGEST)),
        ("s1ec16-aggregate-policy-bound", _valid_digest(S1_EC16_POLICY_DIGEST)),
        ("s1ec17-end-to-end-fixture-bound", _valid_digest(S1_EC17_POLICY_DIGEST)),
        ("s1ec13-reference-report-unchanged", (
            snapshot.s1ec13_report_sha256 == expected_s1ec13_report_sha256
        )),
        ("new-target-paths-unused", (
            snapshot.report_path_unused
            and snapshot.attempt_path_unused
            and snapshot.lock_path_unused
        )),
        ("free-memory-at-least-four-gib", (
            snapshot.free_memory_bytes >= S1_EC18_MIN_FREE_MEMORY_BYTES
        )),
        ("free-disk-at-least-one-gib", (
            snapshot.free_disk_bytes >= S1_EC18_MIN_FREE_DISK_BYTES
        )),
        ("report-size-cap-sixteen-mib", S1_EC18_MAX_REPORT_BYTES == 16 * 1024**2),
        ("runtime-cap-nine-hundred-seconds", (
            S1_EC18_REFERENCE_RUNTIME_SECONDS < S1_EC18_MAX_RUNTIME_SECONDS
        )),
        ("no-retry-after-attempt", (
            S1_EC18_RUNTIME_ABORT_POLICY.endswith("retain-attempt")
        )),
        ("no-canonical-path", True),
        ("no-probe", True),
        ("no-claims", True),
    )
    decision = "FREIGABE" if all(value for _, value in checks) else "KORREKTUR"
    failed = tuple(name for name, value in checks if not value)
    reason = (
        "all static release, resource, path, persistence, and claim gates pass"
        if decision == "FREIGABE"
        else "failed gates: " + ",".join(failed)
    )
    payload = {
        "audit_id": S1_EC18_AUDIT_ID,
        "policy_digest": S1_EC18_POLICY_DIGEST,
        "release_target_id": S1_EC18_RELEASE_TARGET_ID,
        "resource_snapshot_digest": snapshot.digest(),
        "resource_preflight_digest": preflight.result_digest,
        "checks": checks,
        "decision": decision,
        "reason": reason,
        "maximum_report_bytes": S1_EC18_MAX_REPORT_BYTES,
        "maximum_runtime_seconds": S1_EC18_MAX_RUNTIME_SECONDS,
        "runtime_abort_policy": S1_EC18_RUNTIME_ABORT_POLICY,
        "execution_authorized": False,
        "field_execution_performed": False,
        "markers_created": False,
        "report_created": False,
        "canonical_execution_permitted": False,
        "probe_execution_permitted": False,
        "claims_permitted": False,
    }
    return E1FullPublishedReleaseDecision(
        **payload,
        decision_digest=_digest(payload),
    )
