"""S1-EC94 final resource and object-identity gate for the r4/r8 run."""

from __future__ import annotations

from dataclasses import dataclass

from .e1_common_probe_ec89_r4_r8_object_handoffs import (
    E1CommonProbeEC89R4R8ObjectHandoffSet,
)
from .e1_common_probe_ec92_synthetic_r4_r8_coordinator import (
    E1CommonProbeEC92SyntheticCoordinatorResult,
)
from .e1_common_probe_ec93_r4_r8_real_adapter_preflight import (
    E1CommonProbeEC93R4R8RealAdapterPreflight,
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


class E1CommonProbeEC94FinalResourceIdentityGateError(ValueError):
    """Raised when EC94 loses identity isolation or opens execution."""


S1_EC94_GATE_ID = "e1.common-probe-r4-r8-final-resource-identity-gate.s1ec94.v1"
S1_EC94_EC89_RESULT_DIGEST = (
    "eadaee38d591f4ad36acbf00aec3681cd9da0069173a62055ca8ea70a34ffae9"
)
S1_EC94_EC92_RESULT_DIGEST = (
    "069c94d75a4ef2d8652abe09ed396b237e728401840db5dc1a2ac744410fcc9e"
)
S1_EC94_EC93_PREFLIGHT_DIGEST = (
    "28f2facd3130162ee7601dfe27bb5fba3589b8d8236b5f93e8a8440150cebe5e"
)
S1_EC94_REQUIRED_CHECKS = (
    "ec89-r4-r8-handoffs-exact-and-zero-step",
    "ec92-sixteen-fresh-fields-exact-and-nonexecuting",
    "ec93-real-adapters-compatible-and-unreleased",
    "two-handoff-objects-are-distinct",
    "sixteen-resolved-slot-objects-are-distinct",
    "sixteen-binding-objects-are-distinct",
    "eight-formation-slots-reference-bound-resolved-slots",
    "initial-field-and-state-baseline-shared-by-identity",
    "sixteen-fresh-field-objects-distinct-from-baseline-and-each-other",
    "planned-load-exactly-19248-field-steps",
    "all-five-protected-artifact-hashes-exact",
    "free-memory-at-least-four-gib",
    "free-disk-at-least-one-gib",
    "in-memory-no-persistence-decision-or-claim",
    "new-owner-execution-authorization-not-present",
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC94FinalResourceIdentityGate:
    gate_id: str
    source_ec89_result_digest: str
    source_ec92_result_digest: str
    source_ec93_preflight_digest: str
    resource_snapshot_digest: str
    protected_artifact_audit_digest: str
    planned_formation_steps: int
    planned_probe_steps: int
    planned_total_steps: int
    handoff_object_count: int
    resolved_slot_object_count: int
    binding_object_count: int
    formation_slot_reference_count: int
    fresh_field_object_count: int
    checks: tuple[tuple[str, bool], ...]
    technical_execution_ready: bool
    owner_execution_authorized: bool
    coordinator_execution_permitted: bool
    adapter_execution_permitted: bool
    retry_permitted: bool
    posthoc_parameter_change_permitted: bool
    persistence_permitted: bool
    ec46_decision_permitted: bool
    research_decision_permitted: bool
    claims_permitted: bool
    decision: str
    reason: str
    gate_digest: str

    def __post_init__(self) -> None:
        checks = dict(self.checks)
        technical_ready = all(
            checks[name] for name in S1_EC94_REQUIRED_CHECKS[:-1]
        )
        expected_decision = (
            "TECHNISCH_BEREIT_NEUE_R4_R8_EINMALLAUFFREIGABE_FEHLT"
            if technical_ready
            else "KORREKTUR_R4_R8_TECHNISCHE_GATES"
        )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "gate_digest"
        }
        if (
            self.gate_id != S1_EC94_GATE_ID
            or self.source_ec89_result_digest != S1_EC94_EC89_RESULT_DIGEST
            or self.source_ec92_result_digest != S1_EC94_EC92_RESULT_DIGEST
            or self.source_ec93_preflight_digest != S1_EC94_EC93_PREFLIGHT_DIGEST
            or len(self.resource_snapshot_digest) != 64
            or len(self.protected_artifact_audit_digest) != 64
            or (self.planned_formation_steps, self.planned_probe_steps, self.planned_total_steps)
            != (9648, 9600, 19248)
            or (
                self.handoff_object_count,
                self.resolved_slot_object_count,
                self.binding_object_count,
                self.formation_slot_reference_count,
                self.fresh_field_object_count,
            )
            != (2, 16, 16, 8, 16)
            or tuple(name for name, _ in self.checks) != S1_EC94_REQUIRED_CHECKS
            or self.technical_execution_ready is not technical_ready
            or any(
                value is not False
                for value in (
                    self.owner_execution_authorized,
                    self.coordinator_execution_permitted,
                    self.adapter_execution_permitted,
                    self.retry_permitted,
                    self.posthoc_parameter_change_permitted,
                    self.persistence_permitted,
                    self.ec46_decision_permitted,
                    self.research_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision != expected_decision
            or not self.reason
            or self.gate_digest != _digest(payload)
        ):
            raise E1CommonProbeEC94FinalResourceIdentityGateError(
                "S1-EC94 gate changed or opened real execution"
            )


def audit_e1_common_probe_ec94_final_resource_identity_gate(
    handoffs: E1CommonProbeEC89R4R8ObjectHandoffSet,
    coordinator: E1CommonProbeEC92SyntheticCoordinatorResult,
    preflight: E1CommonProbeEC93R4R8RealAdapterPreflight,
    resources: E1PilotRealResourceSnapshot,
    protected: E1CommonProbeProtectedArtifactAudit,
) -> E1CommonProbeEC94FinalResourceIdentityGate:
    """Check resources and identities without invoking an adapter or field."""

    for value in (handoffs, coordinator, preflight, resources, protected):
        value.__post_init__()
    if (
        handoffs.result_digest != S1_EC94_EC89_RESULT_DIGEST
        or coordinator.result_digest != S1_EC94_EC92_RESULT_DIGEST
        or preflight.preflight_digest != S1_EC94_EC93_PREFLIGHT_DIGEST
    ):
        raise E1CommonProbeEC94FinalResourceIdentityGateError(
            "S1-EC94 requires exact EC89, EC92, and EC93 inputs"
        )

    handoff_objects = handoffs.handoffs
    resolved_slots = tuple(
        item for handoff in handoff_objects for item in handoff.resolved_slots
    )
    bindings = tuple(item.binding for item in resolved_slots)
    formation_slots = tuple(
        item for handoff in handoff_objects for item in handoff.formation_slots
    )
    fresh_fields = tuple(
        item.field for group in coordinator.fresh_fields for item in group
    )
    baseline_fields = tuple(item.initial_field for item in handoff_objects)
    baseline_states = tuple(item.initial_state for item in handoff_objects)

    checks = (
        (
            S1_EC94_REQUIRED_CHECKS[0],
            handoffs.refinement_ids == ("r4", "r8")
            and handoffs.field_steps_executed == 0,
        ),
        (
            S1_EC94_REQUIRED_CHECKS[1],
            coordinator.actual_field_steps_executed == 0
            and coordinator.fresh_field_counts == (("r4", 8), ("r8", 8))
            and coordinator.atomic_scalar_return,
        ),
        (
            S1_EC94_REQUIRED_CHECKS[2],
            preflight.synthetic_compatibility_complete
            and preflight.real_execution_permitted is False,
        ),
        (S1_EC94_REQUIRED_CHECKS[3], len({id(item) for item in handoff_objects}) == 2),
        (S1_EC94_REQUIRED_CHECKS[4], len({id(item) for item in resolved_slots}) == 16),
        (S1_EC94_REQUIRED_CHECKS[5], len({id(item) for item in bindings}) == 16),
        (
            S1_EC94_REQUIRED_CHECKS[6],
            len(formation_slots) == 8
            and all(
                any(slot is resolved for resolved in resolved_slots)
                for slot in formation_slots
            ),
        ),
        (
            S1_EC94_REQUIRED_CHECKS[7],
            baseline_fields[0] is baseline_fields[1]
            and baseline_states[0] is baseline_states[1],
        ),
        (
            S1_EC94_REQUIRED_CHECKS[8],
            len(fresh_fields) == 16
            and len({id(item) for item in fresh_fields}) == 16
            and all(item is not baseline_fields[0] for item in fresh_fields),
        ),
        (
            S1_EC94_REQUIRED_CHECKS[9],
            (
                preflight.formation_steps,
                preflight.probe_steps,
                preflight.maximum_total_field_steps,
            )
            == (9648, 9600, 19248),
        ),
        (S1_EC94_REQUIRED_CHECKS[10], protected.all_exact),
        (
            S1_EC94_REQUIRED_CHECKS[11],
            resources.free_memory_bytes >= S1_EC29_MIN_FREE_MEMORY_BYTES,
        ),
        (
            S1_EC94_REQUIRED_CHECKS[12],
            resources.free_disk_bytes >= S1_EC29_MIN_FREE_DISK_BYTES,
        ),
        (
            S1_EC94_REQUIRED_CHECKS[13],
            not any(
                (
                    handoffs.persistence_performed,
                    handoffs.ec46_decision_permitted,
                    handoffs.claims_permitted,
                    coordinator.persistence_performed,
                    coordinator.ec46_decision_permitted,
                    coordinator.claims_permitted,
                    preflight.persistence_permitted,
                    preflight.ec46_decision_permitted,
                    preflight.claims_permitted,
                )
            ),
        ),
        (S1_EC94_REQUIRED_CHECKS[14], False),
    )
    technical_ready = all(value for _, value in checks[:-1])
    values = {
        "gate_id": S1_EC94_GATE_ID,
        "source_ec89_result_digest": handoffs.result_digest,
        "source_ec92_result_digest": coordinator.result_digest,
        "source_ec93_preflight_digest": preflight.preflight_digest,
        "resource_snapshot_digest": resources.digest(),
        "protected_artifact_audit_digest": protected.audit_digest,
        "planned_formation_steps": preflight.formation_steps,
        "planned_probe_steps": preflight.probe_steps,
        "planned_total_steps": preflight.maximum_total_field_steps,
        "handoff_object_count": len(handoff_objects),
        "resolved_slot_object_count": len(resolved_slots),
        "binding_object_count": len(bindings),
        "formation_slot_reference_count": len(formation_slots),
        "fresh_field_object_count": len(fresh_fields),
        "checks": checks,
        "technical_execution_ready": technical_ready,
        "owner_execution_authorized": False,
        "coordinator_execution_permitted": False,
        "adapter_execution_permitted": False,
        "retry_permitted": False,
        "posthoc_parameter_change_permitted": False,
        "persistence_permitted": False,
        "ec46_decision_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "decision": (
            "TECHNISCH_BEREIT_NEUE_R4_R8_EINMALLAUFFREIGABE_FEHLT"
            if technical_ready
            else "KORREKTUR_R4_R8_TECHNISCHE_GATES"
        ),
        "reason": (
            "all-technical-resource-identity-gates-ready;explicit-new-owner-"
            "authorization-required"
            if technical_ready
            else "one-or-more-resource-or-identity-gates-failed"
        ),
    }
    return E1CommonProbeEC94FinalResourceIdentityGate(
        **values, gate_digest=_digest(values)
    )
