"""S1-EC68 final static real preflight for the bounded n2/r2 run."""

from __future__ import annotations

from dataclasses import dataclass

from .e1_common_probe_n2_r2_object_handoff import E1CommonProbeN2R2ObjectHandoff
from .e1_common_probe_n2_r2_positive_step_coordinator_fixture import (
    E1CommonProbeN2R2PositiveStepCoordinatorFixtureResult,
)
from .e1_common_probe_n2_r2_real_call_adapters import (
    E1CommonProbeN2R2RealCallAdapterAudit,
)
from .e1_common_probe_n2_r2_real_mode_coordinator import (
    E1CommonProbeN2R2RealModeCoordinatorAudit,
)
from .e1_common_probe_n2_r2_real_preflight import (
    E1CommonProbeProtectedArtifactAudit,
)
from .e1_refined_formation_runner import _digest
from .e1_repetition_pilot_real_preflight import E1PilotRealResourceSnapshot
from .e1_repetition_pilot_release_contract import (
    S1_EC29_MIN_FREE_DISK_BYTES,
    S1_EC29_MIN_FREE_MEMORY_BYTES,
)


class E1CommonProbeN2R2FinalRealPreflightError(ValueError):
    """Raised when EC68 changes or releases the bounded real run."""


S1_EC68_PREFLIGHT_ID = "e1.common-probe-n2-r2-final-real-preflight.s1ec68.v1"
S1_EC68_EC59_HANDOFF_DIGEST = (
    "5acf624ffaa209e058b74134a069946e21eb2db6609ad7db8301c2c122bca3cb"
)
S1_EC68_EC65_AUDIT_DIGEST = (
    "dba7a309bf49dfb57881883a049c80d7c58ea5a98f74ef0744167b2a26d718af"
)
S1_EC68_EC66_FIXTURE_DIGEST = (
    "bc07f3059139ef40a364f5fdbc61787aa68ca63722c26039410fee593e2359a7"
)
S1_EC68_EC67_AUDIT_DIGEST = (
    "0703dda56cf70429f0845393abfa3d39c8993837f0ea3f18e6ae799a5c1713a0"
)
S1_EC68_REQUIRED_CHECKS = (
    "ec59-object-handoff-exact",
    "ec65-real-call-adapters-exact-and-unreleased",
    "ec66-positive-coordinator-fixture-exact-and-nonexecuting",
    "ec67-real-mode-coordinator-exact-and-unreleased",
    "planned-load-exactly-3208-field-steps",
    "four-formation-eight-fresh-eight-probe-routes",
    "all-five-protected-artifact-hashes-exact",
    "free-memory-at-least-four-gib",
    "free-disk-at-least-one-gib",
    "runtime-cap-nine-hundred-seconds",
    "in-memory-no-persistence-decision-or-claim",
    "new-owner-execution-authorization-not-present",
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeN2R2FinalRealPreflight:
    preflight_id: str
    ec59_handoff_digest: str
    ec65_audit_digest: str
    ec66_fixture_digest: str
    ec67_audit_digest: str
    resource_snapshot_digest: str
    protected_artifact_audit_digest: str
    planned_formation_steps: int
    planned_probe_steps: int
    planned_total_steps: int
    maximum_runtime_seconds: float
    checks: tuple[tuple[str, bool], ...]
    technical_execution_ready: bool
    owner_execution_authorized: bool
    coordinator_execution_permitted: bool
    adapter_execution_permitted: bool
    persistence_permitted: bool
    research_decision_permitted: bool
    ec46_decision_permitted: bool
    memory_claim_permitted: bool
    decision: str
    reason: str
    preflight_digest: str

    def __post_init__(self) -> None:
        checks = dict(self.checks)
        technical_ready = all(
            checks[name] for name in S1_EC68_REQUIRED_CHECKS[:-1]
        )
        expected = (
            "TECHNISCH_BEREIT_NEUE_EINMALLAUFFREIGABE_FEHLT"
            if technical_ready
            else "KORREKTUR_TECHNISCHE_GATES"
        )
        if (
            self.preflight_id != S1_EC68_PREFLIGHT_ID
            or self.ec59_handoff_digest != S1_EC68_EC59_HANDOFF_DIGEST
            or self.ec65_audit_digest != S1_EC68_EC65_AUDIT_DIGEST
            or self.ec66_fixture_digest != S1_EC68_EC66_FIXTURE_DIGEST
            or self.ec67_audit_digest != S1_EC68_EC67_AUDIT_DIGEST
            or len(self.resource_snapshot_digest) != 64
            or len(self.protected_artifact_audit_digest) != 64
            or (self.planned_formation_steps, self.planned_probe_steps, self.planned_total_steps) != (1608, 1600, 3208)
            or self.maximum_runtime_seconds != 900.0
            or tuple(name for name, _ in self.checks) != S1_EC68_REQUIRED_CHECKS
            or self.technical_execution_ready is not technical_ready
            or any(value is not False for value in (
                self.owner_execution_authorized,
                self.coordinator_execution_permitted,
                self.adapter_execution_permitted,
                self.persistence_permitted,
                self.research_decision_permitted,
                self.ec46_decision_permitted,
                self.memory_claim_permitted,
            ))
            or self.decision != expected
            or not self.reason
        ):
            raise E1CommonProbeN2R2FinalRealPreflightError(
                "S1-EC68 changed or released the bounded real run"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "preflight_digest"
        }
        if self.preflight_digest != _digest(payload):
            raise E1CommonProbeN2R2FinalRealPreflightError(
                "S1-EC68 preflight digest changed"
            )


def audit_e1_common_probe_n2_r2_final_real_preflight(
    handoff: E1CommonProbeN2R2ObjectHandoff,
    adapters: E1CommonProbeN2R2RealCallAdapterAudit,
    synthetic_coordinator: E1CommonProbeN2R2PositiveStepCoordinatorFixtureResult,
    real_coordinator: E1CommonProbeN2R2RealModeCoordinatorAudit,
    resources: E1PilotRealResourceSnapshot,
    protected: E1CommonProbeProtectedArtifactAudit,
) -> E1CommonProbeN2R2FinalRealPreflight:
    """Check every technical gate without accepting an owner release."""

    for value in (
        handoff,
        adapters,
        synthetic_coordinator,
        real_coordinator,
        resources,
        protected,
    ):
        value.__post_init__()
    checks = (
        ("ec59-object-handoff-exact", handoff.handoff_digest == S1_EC68_EC59_HANDOFF_DIGEST and handoff.field_steps_executed == 0),
        ("ec65-real-call-adapters-exact-and-unreleased", adapters.audit_digest == S1_EC68_EC65_AUDIT_DIGEST and adapters.adapter_execution_permitted is False),
        ("ec66-positive-coordinator-fixture-exact-and-nonexecuting", synthetic_coordinator.result_digest == S1_EC68_EC66_FIXTURE_DIGEST and synthetic_coordinator.actual_field_steps_executed == 0 and synthetic_coordinator.real_adapter_execution_permitted is False),
        ("ec67-real-mode-coordinator-exact-and-unreleased", real_coordinator.audit_digest == S1_EC68_EC67_AUDIT_DIGEST and real_coordinator.coordinator_execution_permitted is False and real_coordinator.preflight_required_before_adapter_calls),
        ("planned-load-exactly-3208-field-steps", (synthetic_coordinator.accounted_formation_steps, synthetic_coordinator.accounted_probe_steps, synthetic_coordinator.accounted_total_steps) == (1608, 1600, 3208)),
        ("four-formation-eight-fresh-eight-probe-routes", (synthetic_coordinator.formation_count, synthetic_coordinator.fresh_field_count, synthetic_coordinator.probe_count) == (4, 8, 8)),
        ("all-five-protected-artifact-hashes-exact", protected.all_exact),
        ("free-memory-at-least-four-gib", resources.free_memory_bytes >= S1_EC29_MIN_FREE_MEMORY_BYTES),
        ("free-disk-at-least-one-gib", resources.free_disk_bytes >= S1_EC29_MIN_FREE_DISK_BYTES),
        ("runtime-cap-nine-hundred-seconds", True),
        ("in-memory-no-persistence-decision-or-claim", not any((handoff.persistence_performed, synthetic_coordinator.persistence_performed, synthetic_coordinator.research_decision_permitted, synthetic_coordinator.memory_claim_permitted, adapters.persistence_permitted, adapters.research_decision_permitted, adapters.memory_claim_permitted, real_coordinator.persistence_permitted, real_coordinator.research_decision_permitted, real_coordinator.memory_claim_permitted))),
        ("new-owner-execution-authorization-not-present", False),
    )
    technical_ready = all(value for _, value in checks[:-1])
    values = {
        "preflight_id": S1_EC68_PREFLIGHT_ID,
        "ec59_handoff_digest": handoff.handoff_digest,
        "ec65_audit_digest": adapters.audit_digest,
        "ec66_fixture_digest": synthetic_coordinator.result_digest,
        "ec67_audit_digest": real_coordinator.audit_digest,
        "resource_snapshot_digest": resources.digest(),
        "protected_artifact_audit_digest": protected.audit_digest,
        "planned_formation_steps": synthetic_coordinator.accounted_formation_steps,
        "planned_probe_steps": synthetic_coordinator.accounted_probe_steps,
        "planned_total_steps": synthetic_coordinator.accounted_total_steps,
        "maximum_runtime_seconds": 900.0,
        "checks": checks,
        "technical_execution_ready": technical_ready,
        "owner_execution_authorized": False,
        "coordinator_execution_permitted": False,
        "adapter_execution_permitted": False,
        "persistence_permitted": False,
        "research_decision_permitted": False,
        "ec46_decision_permitted": False,
        "memory_claim_permitted": False,
        "decision": "TECHNISCH_BEREIT_NEUE_EINMALLAUFFREIGABE_FEHLT" if technical_ready else "KORREKTUR_TECHNISCHE_GATES",
        "reason": "all-technical-gates-ready-explicit-new-owner-one-shot-release-required" if technical_ready else "one-or-more-technical-gates-failed",
    }
    return E1CommonProbeN2R2FinalRealPreflight(
        **values,
        preflight_digest=_digest(values),
    )
