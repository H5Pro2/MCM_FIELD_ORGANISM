"""S1-EC60 static preflight after the object-carrying n2/r2 handoff."""

from __future__ import annotations

from dataclasses import dataclass

from .e1_common_probe_n2_r2_object_handoff import (
    E1CommonProbeN2R2ObjectHandoff,
)
from .e1_common_probe_n2_r2_real_preflight import (
    E1CommonProbeProtectedArtifactAudit,
)
from .e1_common_probe_real_wrappers import E1CommonProbeRealWrappersAudit
from .e1_refined_formation_runner import _digest
from .e1_repetition_pilot_real_preflight import E1PilotRealResourceSnapshot
from .e1_repetition_pilot_release_contract import (
    S1_EC29_MIN_FREE_DISK_BYTES,
    S1_EC29_MIN_FREE_MEMORY_BYTES,
)


class E1CommonProbeN2R2PostHandoffPreflightError(ValueError):
    """Raised when EC60 releases or changes the bounded n2/r2 scope."""


S1_EC60_PREFLIGHT_ID = "e1.common-probe-n2-r2-post-handoff-preflight.s1ec60.v1"
S1_EC60_EC54_AUDIT_DIGEST = (
    "cc80b40fc7b7c97bcab7135da10a23e45d739572f9b94ff6f7bf45bb836b2bfb"
)
S1_EC60_EC59_HANDOFF_DIGEST = (
    "5acf624ffaa209e058b74134a069946e21eb2db6609ad7db8301c2c122bca3cb"
)
S1_EC60_REQUIRED_CHECKS = (
    "ec59-object-handoff-exact",
    "eight-resolved-slots-and-four-unique-formation-routes",
    "planned-load-exactly-3208-field-steps",
    "ec54-real-wrappers-exact",
    "all-five-protected-artifact-hashes-exact",
    "free-memory-at-least-four-gib",
    "free-disk-at-least-one-gib",
    "runtime-cap-nine-hundred-seconds",
    "in-memory-no-persistence-decision-or-claim",
    "real-n2-r2-execution-coordinator-implemented",
    "new-owner-execution-authorization-not-present",
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeN2R2PostHandoffPreflight:
    preflight_id: str
    ec54_audit_digest: str
    ec59_handoff_digest: str
    resource_snapshot_digest: str
    protected_artifact_audit_digest: str
    planned_formation_steps: int
    planned_probe_steps: int
    planned_total_steps: int
    maximum_runtime_seconds: float
    checks: tuple[tuple[str, bool], ...]
    object_handoff_ready: bool
    real_execution_coordinator_implemented: bool
    real_execution_coordinator_implementation_permitted: bool
    technical_execution_ready: bool
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
        ready = all(checks[name] for name in S1_EC60_REQUIRED_CHECKS[:-1])
        expected = (
            "TECHNISCH_BEREIT_NEUE_EINMALLAUFFREIGABE_FEHLT"
            if ready
            else "KORREKTUR_REAL_EXECUTION_COORDINATOR_MISSING"
        )
        if (
            self.preflight_id != S1_EC60_PREFLIGHT_ID
            or self.ec54_audit_digest != S1_EC60_EC54_AUDIT_DIGEST
            or self.ec59_handoff_digest != S1_EC60_EC59_HANDOFF_DIGEST
            or len(self.resource_snapshot_digest) != 64
            or len(self.protected_artifact_audit_digest) != 64
            or (self.planned_formation_steps, self.planned_probe_steps, self.planned_total_steps) != (1608, 1600, 3208)
            or self.maximum_runtime_seconds != 900.0
            or tuple(name for name, _ in self.checks) != S1_EC60_REQUIRED_CHECKS
            or self.object_handoff_ready is not True
            or self.real_execution_coordinator_implemented is not False
            or self.real_execution_coordinator_implementation_permitted is not True
            or self.technical_execution_ready is not ready
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
            raise E1CommonProbeN2R2PostHandoffPreflightError(
                "S1-EC60 changed or released the bounded fixture"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "preflight_digest"
        }
        if self.preflight_digest != _digest(payload):
            raise E1CommonProbeN2R2PostHandoffPreflightError(
                "S1-EC60 preflight digest changed"
            )


def audit_e1_common_probe_n2_r2_post_handoff_preflight(
    handoff: E1CommonProbeN2R2ObjectHandoff,
    wrappers: E1CommonProbeRealWrappersAudit,
    resources: E1PilotRealResourceSnapshot,
    protected: E1CommonProbeProtectedArtifactAudit,
) -> E1CommonProbeN2R2PostHandoffPreflight:
    """Audit the handoff and remaining coordinator gap without execution."""

    for value in (handoff, wrappers, resources, protected):
        value.__post_init__()
    formation_steps = sum(
        len(item.formation_plan.proposal_steps)
        for item in handoff.formation_slots
        if item.formation_plan is not None
    )
    probe_steps = sum(
        len(item.probe_plan.proposal_steps) for item in handoff.resolved_slots
    )
    total_steps = formation_steps + probe_steps
    checks = (
        ("ec59-object-handoff-exact", handoff.handoff_digest == S1_EC60_EC59_HANDOFF_DIGEST and handoff.field_steps_executed == 0),
        ("eight-resolved-slots-and-four-unique-formation-routes", len(handoff.resolved_slots) == 8 and len(handoff.formation_slots) == 4 and handoff.all_slot_objects_resolved and handoff.all_formation_routes_unique),
        ("planned-load-exactly-3208-field-steps", (formation_steps, probe_steps, total_steps) == (1608, 1600, 3208)),
        ("ec54-real-wrappers-exact", wrappers.audit_digest == S1_EC60_EC54_AUDIT_DIGEST and wrappers.wrappers_implemented),
        ("all-five-protected-artifact-hashes-exact", protected.all_exact),
        ("free-memory-at-least-four-gib", resources.free_memory_bytes >= S1_EC29_MIN_FREE_MEMORY_BYTES),
        ("free-disk-at-least-one-gib", resources.free_disk_bytes >= S1_EC29_MIN_FREE_DISK_BYTES),
        ("runtime-cap-nine-hundred-seconds", True),
        ("in-memory-no-persistence-decision-or-claim", not any((handoff.persistence_performed, handoff.research_decision_permitted, handoff.memory_claim_permitted))),
        ("real-n2-r2-execution-coordinator-implemented", False),
        ("new-owner-execution-authorization-not-present", False),
    )
    ready = all(value for _, value in checks[:-1])
    values = {
        "preflight_id": S1_EC60_PREFLIGHT_ID,
        "ec54_audit_digest": wrappers.audit_digest,
        "ec59_handoff_digest": handoff.handoff_digest,
        "resource_snapshot_digest": resources.digest(),
        "protected_artifact_audit_digest": protected.audit_digest,
        "planned_formation_steps": formation_steps,
        "planned_probe_steps": probe_steps,
        "planned_total_steps": total_steps,
        "maximum_runtime_seconds": 900.0,
        "checks": checks,
        "object_handoff_ready": True,
        "real_execution_coordinator_implemented": False,
        "real_execution_coordinator_implementation_permitted": True,
        "technical_execution_ready": ready,
        "owner_execution_authorized": False,
        "fixture_execution_permitted": False,
        "persistence_permitted": False,
        "research_decision_permitted": False,
        "ec46_decision_permitted": False,
        "memory_claim_permitted": False,
        "decision": "TECHNISCH_BEREIT_NEUE_EINMALLAUFFREIGABE_FEHLT" if ready else "KORREKTUR_REAL_EXECUTION_COORDINATOR_MISSING",
        "reason": "all-technical-gates-ready-explicit-owner-authorization-required" if ready else "object-handoff-exists-but-four-formation-eight-probe-execution-coordinator-is-missing",
    }
    return E1CommonProbeN2R2PostHandoffPreflight(
        **values,
        preflight_digest=_digest(values),
    )
