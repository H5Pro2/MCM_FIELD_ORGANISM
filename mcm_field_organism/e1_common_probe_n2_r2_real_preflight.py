"""S1-EC58 static real preflight for the bounded 3,208-step n2/r2 fixture."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

from .e1_common_probe_n2_r2_runner_fixture import E1CommonProbeN2R2RunnerFixtureResult
from .e1_common_probe_real_binding_contract import E1CommonProbeRealBindingContract
from .e1_common_probe_real_wrappers import E1CommonProbeRealWrappersAudit
from .e1_common_probe_small_real_result_audit import E1CommonProbeSmallRealResultAudit
from .e1_refined_formation_runner import _digest
from .e1_repetition_pilot_real_preflight import E1PilotRealResourceSnapshot
from .e1_repetition_pilot_release_contract import (
    S1_EC29_MIN_FREE_DISK_BYTES,
    S1_EC29_MIN_FREE_MEMORY_BYTES,
)


class E1CommonProbeN2R2RealPreflightError(ValueError):
    """Raised when EC58 changes scope or releases the bounded fixture."""


S1_EC58_PREFLIGHT_ID = "e1.common-probe-n2-r2-real-preflight.s1ec58.v1"
S1_EC58_EC52_CONTRACT_DIGEST = (
    "291ea70c96ad26b3f6e696588ebd55d3e6f7163967b45de9a689bd731cb7bf7b"
)
S1_EC58_EC54_AUDIT_DIGEST = (
    "cc80b40fc7b7c97bcab7135da10a23e45d739572f9b94ff6f7bf45bb836b2bfb"
)
S1_EC58_EC56_AUDIT_DIGEST = (
    "959703db814d753744de67de65c216365ced4761fdfeb5f874916c94cba0340d"
)
S1_EC58_EC57_FIXTURE_DIGEST = (
    "73009f5847200ad8497b454482f8e7e33320c53ecd325b124314ea7720a4758d"
)
S1_EC58_PROTECTED_ARTIFACTS = (
    (
        "reports/e1_refined_formation_transfer_s1ea_once_v1.json",
        "adf8b2b6c1b9fdda48062dbb1cd9149fcde462a3dc77a348aa2dfb0cb1fcaa47",
    ),
    (
        "reports/e1_refined_confirmation_s1eb_once_v1.attempt.json",
        "695f8170011d3c7afe1a0c8816021fb4814ac409c71fef36253f2ce9ce091782",
    ),
    (
        "synthetic_runs/s1ec13_full_formation_once_v1/e1_confirmation_s1ec3_synthetic_once_v1.json",
        "15932c1f3f6b493ebc090c6e2da5612dd3bc35e6f9aa012f416ef710ee54e48a",
    ),
    (
        "synthetic_runs/s1ec19_full_published_once_v1/e1_full_formation_published_s1ec19_once_v1.json",
        "93cc94ddb18f80919067ff4e29ccae5aa038bb436d72584acef2d38e57be1fcc",
    ),
    (
        "synthetic_runs/s1ec23_full_published_probe_once_v1/e1_full_published_probe_s1ec23_once_v1.json",
        "85a114b9de5f2152558ca78a03a15f5690607fab98b7f9ddbf10cadf32e8b50e",
    ),
)
S1_EC58_REQUIRED_CHECKS = (
    "ec52-contact-aware-real-binding-exact",
    "ec54-real-wrappers-implemented",
    "ec56-next-scope-exactly-n2-r2-eight-roles",
    "ec57-zero-step-runner-exact",
    "planned-load-exactly-3208-field-steps",
    "four-formation-and-eight-probe-slots",
    "all-five-protected-artifact-hashes-exact",
    "free-memory-at-least-four-gib",
    "free-disk-at-least-one-gib",
    "runtime-cap-nine-hundred-seconds",
    "in-memory-no-persistence-decision-or-claim",
    "real-n2-r2-execution-adapter-implemented",
    "new-owner-execution-authorization-not-present",
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeProtectedArtifactAudit:
    hashes: tuple[tuple[str, str, bool], ...]
    all_exact: bool
    audit_digest: str

    def __post_init__(self) -> None:
        if (
            tuple((path, expected) for path, expected, _ in self.hashes)
            != S1_EC58_PROTECTED_ARTIFACTS
            or self.all_exact is not all(exact for _, _, exact in self.hashes)
        ):
            raise E1CommonProbeN2R2RealPreflightError(
                "S1-EC58 protected-artifact audit changed"
            )
        payload = {"hashes": self.hashes, "all_exact": self.all_exact}
        if self.audit_digest != _digest(payload):
            raise E1CommonProbeN2R2RealPreflightError(
                "S1-EC58 protected-artifact digest changed"
            )


def audit_e1_common_probe_protected_artifacts(
    root: Path,
) -> E1CommonProbeProtectedArtifactAudit:
    """Read only the five protected artifacts and compare SHA-256."""

    root = Path(root).resolve()
    hashes = []
    for relative, expected in S1_EC58_PROTECTED_ARTIFACTS:
        path = root / relative
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ""
        hashes.append((relative, expected, actual == expected))
    values = {"hashes": tuple(hashes), "all_exact": all(x[2] for x in hashes)}
    return E1CommonProbeProtectedArtifactAudit(
        **values,
        audit_digest=_digest(values),
    )


@dataclass(frozen=True, slots=True)
class E1CommonProbeN2R2RealPreflight:
    preflight_id: str
    ec52_contract_digest: str
    ec54_audit_digest: str
    ec56_audit_digest: str
    ec57_fixture_digest: str
    resource_snapshot_digest: str
    protected_artifact_audit_digest: str
    maximum_runtime_seconds: float
    checks: tuple[tuple[str, bool], ...]
    technical_execution_ready: bool
    real_execution_adapter_implemented: bool
    real_execution_adapter_implementation_permitted: bool
    owner_execution_authorized: bool
    fixture_execution_permitted: bool
    persistence_permitted: bool
    research_decision_permitted: bool
    ec46_decision_permitted: bool
    memory_claim_permitted: bool
    decision: str
    reason: str
    preflight_digest: str

    def __post_init__(self) -> None:
        checks = dict(self.checks)
        technical = S1_EC58_REQUIRED_CHECKS[:-1]
        ready = all(checks[name] for name in technical)
        expected = "TECHNISCH_BEREIT_NEUE_EINMALLAUFFREIGABE_FEHLT" if ready else "KORREKTUR_REAL_EXECUTION_ADAPTER_MISSING"
        if (
            self.preflight_id != S1_EC58_PREFLIGHT_ID
            or self.ec52_contract_digest != S1_EC58_EC52_CONTRACT_DIGEST
            or self.ec54_audit_digest != S1_EC58_EC54_AUDIT_DIGEST
            or self.ec56_audit_digest != S1_EC58_EC56_AUDIT_DIGEST
            or self.ec57_fixture_digest != S1_EC58_EC57_FIXTURE_DIGEST
            or len(self.resource_snapshot_digest) != 64
            or len(self.protected_artifact_audit_digest) != 64
            or self.maximum_runtime_seconds != 900.0
            or tuple(name for name, _ in self.checks) != S1_EC58_REQUIRED_CHECKS
            or self.technical_execution_ready is not ready
            or self.real_execution_adapter_implemented is not False
            or self.real_execution_adapter_implementation_permitted is not True
            or any(value is not False for value in (
                self.owner_execution_authorized,
                self.fixture_execution_permitted,
                self.persistence_permitted,
                self.research_decision_permitted,
                self.ec46_decision_permitted,
                self.memory_claim_permitted,
            ))
            or self.decision != expected
            or not self.reason
        ):
            raise E1CommonProbeN2R2RealPreflightError(
                "S1-EC58 changed or released the bounded fixture"
            )
        payload = {name: getattr(self, name) for name in self.__dataclass_fields__ if name != "preflight_digest"}
        if self.preflight_digest != _digest(payload):
            raise E1CommonProbeN2R2RealPreflightError(
                "S1-EC58 preflight digest changed"
            )


def audit_e1_common_probe_n2_r2_real_preflight(
    contract: E1CommonProbeRealBindingContract,
    wrappers: E1CommonProbeRealWrappersAudit,
    result_audit: E1CommonProbeSmallRealResultAudit,
    runner_fixture: E1CommonProbeN2R2RunnerFixtureResult,
    resources: E1PilotRealResourceSnapshot,
    protected: E1CommonProbeProtectedArtifactAudit,
) -> E1CommonProbeN2R2RealPreflight:
    """Check all technical gates without accepting an authorization."""

    for value in (contract, wrappers, result_audit, runner_fixture, resources, protected):
        value.__post_init__()
    checks = (
        ("ec52-contact-aware-real-binding-exact", contract.contract_digest == S1_EC58_EC52_CONTRACT_DIGEST),
        ("ec54-real-wrappers-implemented", wrappers.audit_digest == S1_EC58_EC54_AUDIT_DIGEST and wrappers.wrappers_implemented),
        ("ec56-next-scope-exactly-n2-r2-eight-roles", result_audit.audit_digest == S1_EC58_EC56_AUDIT_DIGEST and result_audit.next_fixture_contact_count == 2 and result_audit.next_fixture_refinement_id == "r2"),
        ("ec57-zero-step-runner-exact", runner_fixture.result_digest == S1_EC58_EC57_FIXTURE_DIGEST and runner_fixture.executed_field_steps == 0),
        ("planned-load-exactly-3208-field-steps", runner_fixture.planned_total_steps == 3208),
        ("four-formation-and-eight-probe-slots", runner_fixture.formation_state_count == 4 and runner_fixture.probe_slot_count == 8),
        ("all-five-protected-artifact-hashes-exact", protected.all_exact),
        ("free-memory-at-least-four-gib", resources.free_memory_bytes >= S1_EC29_MIN_FREE_MEMORY_BYTES),
        ("free-disk-at-least-one-gib", resources.free_disk_bytes >= S1_EC29_MIN_FREE_DISK_BYTES),
        ("runtime-cap-nine-hundred-seconds", True),
        ("in-memory-no-persistence-decision-or-claim", not any((runner_fixture.persistence_performed, runner_fixture.research_decision_permitted, runner_fixture.ec46_decision_permitted, runner_fixture.memory_claim_permitted))),
        ("real-n2-r2-execution-adapter-implemented", False),
        ("new-owner-execution-authorization-not-present", False),
    )
    ready = all(value for _, value in checks[:-1])
    values = {
        "preflight_id": S1_EC58_PREFLIGHT_ID,
        "ec52_contract_digest": contract.contract_digest,
        "ec54_audit_digest": wrappers.audit_digest,
        "ec56_audit_digest": result_audit.audit_digest,
        "ec57_fixture_digest": runner_fixture.result_digest,
        "resource_snapshot_digest": resources.digest(),
        "protected_artifact_audit_digest": protected.audit_digest,
        "maximum_runtime_seconds": 900.0,
        "checks": checks,
        "technical_execution_ready": ready,
        "real_execution_adapter_implemented": False,
        "real_execution_adapter_implementation_permitted": True,
        "owner_execution_authorized": False,
        "fixture_execution_permitted": False,
        "persistence_permitted": False,
        "research_decision_permitted": False,
        "ec46_decision_permitted": False,
        "memory_claim_permitted": False,
        "decision": "TECHNISCH_BEREIT_NEUE_EINMALLAUFFREIGABE_FEHLT" if ready else "KORREKTUR_REAL_EXECUTION_ADAPTER_MISSING",
        "reason": "all-technical-gates-ready-explicit-owner-authorization-required" if ready else "typed-receipt-runner-does-not-carry-real-plan-field-and-state-objects",
    }
    return E1CommonProbeN2R2RealPreflight(**values, preflight_digest=_digest(values))
