"""S1-EC56 static audit of the transient EC55 small real-wrapper result."""

from __future__ import annotations

from dataclasses import dataclass

from .e1_common_probe_identifiability_contract import S1_EC45_PROBE_ROLES
from .e1_refined_formation_runner import _digest


class E1CommonProbeSmallRealResultAuditError(ValueError):
    """Raised when EC56 overstates EC55 or releases a larger matrix."""


S1_EC56_AUDIT_ID = "e1.common-probe-small-real-result-audit.s1ec56.v1"
S1_EC56_EC55_RESULT_DIGEST = (
    "dbc057ec06ace7c30b0fe15bfe26244fd27184cf2ea3ef0d34ec292c11c2e1b0"
)
S1_EC56_CHECKS = (
    "ec55-exactly-n2-r2",
    "ec55-exactly-three-roles",
    "ec55-exactly-1002-field-steps",
    "ec55-initial-fields-identical-and-separate",
    "ec55-frozen-state-preserved",
    "ec55-inputs-preserved",
    "ec55-active-feedback-activation-difference-positive",
    "ec55-active-feedback-afterimage-difference-positive",
    "ec55-no-full-matrix-persistence-decision-or-claim",
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeSmallRealResultAudit:
    audit_id: str
    source_result_digest: str
    source_contact_count: int
    source_refinement_id: str
    source_roles: tuple[str, ...]
    source_total_field_steps: int
    active_feedback_activation_linf: float
    active_feedback_afterimage_linf: float
    checks: tuple[tuple[str, bool], ...]
    bounded_finding: str
    missing_comparators: tuple[str, ...]
    next_fixture_contact_count: int
    next_fixture_refinement_id: str
    next_fixture_roles: tuple[str, ...]
    next_formation_state_count: int
    next_formation_step_count: int
    next_probe_slot_count: int
    next_probe_step_count: int
    next_total_field_steps: int
    next_fixture_implementation_permitted: bool
    next_fixture_execution_permitted: bool
    full_matrix_execution_permitted: bool
    persistence_permitted: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    decision: str
    reason: str
    audit_digest: str

    def __post_init__(self) -> None:
        if (
            self.audit_id != S1_EC56_AUDIT_ID
            or self.source_result_digest != S1_EC56_EC55_RESULT_DIGEST
            or self.source_contact_count != 2
            or self.source_refinement_id != "r2"
            or self.source_roles != (
                "p0-reset-ab",
                "e1-active-ab",
                "e1-probe-feedback-ablated-ab",
            )
            or self.source_total_field_steps != 1002
            or self.active_feedback_activation_linf
            != 2.8709257103076702e-05
            or self.active_feedback_afterimage_linf
            != 1.7290444112694203e-05
            or tuple(name for name, _ in self.checks) != S1_EC56_CHECKS
            or any(value is not True for _, value in self.checks)
            or self.bounded_finding
            != "real-wrapper-backreaction-route-technically-observable"
            or self.missing_comparators != (
                "p0-reset-ba",
                "e1-active-ba",
                "e1-probe-feedback-ablated-ba",
                "e1-formation-ablated-ab",
                "e1-formation-ablated-ba",
                "same-run-p0-reset-ab-and-active-ab-replication",
            )
            or (self.next_fixture_contact_count, self.next_fixture_refinement_id)
            != (2, "r2")
            or self.next_fixture_roles != S1_EC45_PROBE_ROLES
            or self.next_formation_state_count != 4
            or self.next_formation_step_count != 1608
            or self.next_probe_slot_count != 8
            or self.next_probe_step_count != 1600
            or self.next_total_field_steps != 3208
            or self.next_fixture_implementation_permitted is not True
            or any(value is not False for value in (
                self.next_fixture_execution_permitted,
                self.full_matrix_execution_permitted,
                self.persistence_permitted,
                self.research_decision_permitted,
                self.memory_claim_permitted,
            ))
            or self.decision
            != "WRAPPER_CONFIRMED_NEXT_MINIMUM_N2_R2_EIGHT_ROLE_FIXTURE"
            or not self.reason
        ):
            raise E1CommonProbeSmallRealResultAuditError(
                "S1-EC56 changed EC55 or exceeded the minimum next fixture"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "audit_digest"
        }
        if self.audit_digest != _digest(payload):
            raise E1CommonProbeSmallRealResultAuditError(
                "S1-EC56 audit digest changed"
            )


def audit_e1_common_probe_small_real_result(
) -> E1CommonProbeSmallRealResultAudit:
    """Audit only reported EC55 scalars; never reconstruct or run EC55."""

    activation = 2.8709257103076702e-05
    afterimage = 1.7290444112694203e-05
    checks = (
        ("ec55-exactly-n2-r2", True),
        ("ec55-exactly-three-roles", True),
        ("ec55-exactly-1002-field-steps", True),
        ("ec55-initial-fields-identical-and-separate", True),
        ("ec55-frozen-state-preserved", True),
        ("ec55-inputs-preserved", True),
        ("ec55-active-feedback-activation-difference-positive", activation > 0.0),
        ("ec55-active-feedback-afterimage-difference-positive", afterimage > 0.0),
        ("ec55-no-full-matrix-persistence-decision-or-claim", True),
    )
    values = {
        "audit_id": S1_EC56_AUDIT_ID,
        "source_result_digest": S1_EC56_EC55_RESULT_DIGEST,
        "source_contact_count": 2,
        "source_refinement_id": "r2",
        "source_roles": (
            "p0-reset-ab",
            "e1-active-ab",
            "e1-probe-feedback-ablated-ab",
        ),
        "source_total_field_steps": 1002,
        "active_feedback_activation_linf": activation,
        "active_feedback_afterimage_linf": afterimage,
        "checks": checks,
        "bounded_finding": (
            "real-wrapper-backreaction-route-technically-observable"
        ),
        "missing_comparators": (
            "p0-reset-ba",
            "e1-active-ba",
            "e1-probe-feedback-ablated-ba",
            "e1-formation-ablated-ab",
            "e1-formation-ablated-ba",
            "same-run-p0-reset-ab-and-active-ab-replication",
        ),
        "next_fixture_contact_count": 2,
        "next_fixture_refinement_id": "r2",
        "next_fixture_roles": S1_EC45_PROBE_ROLES,
        "next_formation_state_count": 4,
        "next_formation_step_count": 4 * 402,
        "next_probe_slot_count": 8,
        "next_probe_step_count": 8 * 200,
        "next_total_field_steps": 4 * 402 + 8 * 200,
        "next_fixture_implementation_permitted": True,
        "next_fixture_execution_permitted": False,
        "full_matrix_execution_permitted": False,
        "persistence_permitted": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
        "decision": (
            "WRAPPER_CONFIRMED_NEXT_MINIMUM_N2_R2_EIGHT_ROLE_FIXTURE"
        ),
        "reason": (
            "ec55-confirms-only-one-ab-backreaction-route;matched-order-and-"
            "causal-controls-require-all-eight-n2-r2-roles-in-one-run"
        ),
    }
    return E1CommonProbeSmallRealResultAudit(
        **values,
        audit_digest=_digest(values),
    )
