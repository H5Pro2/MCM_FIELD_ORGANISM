"""S1-EC50 static audit of the missing n1/n2 axis in the common-probe adapter."""

from __future__ import annotations

from dataclasses import dataclass, fields
import inspect

from .e1_common_probe_eight_role_adapter_fixture import (
    E1CommonProbeEightRoleAdapterFixtureResult,
    E1CommonProbeFormationHandoff,
    E1CommonProbeResetSlot,
    E1CommonProbeRoleReceipt,
    run_e1_common_probe_eight_role_adapter_fixture,
)
from .e1_common_probe_identifiability_contract import S1_EC45_PROBE_ROLES
from .e1_common_probe_synthetic_runner_fixture import S1_EC47_REFINEMENTS
from .e1_refined_formation_runner import _digest


class E1CommonProbeContactAxisAuditError(ValueError):
    """Raised when EC50 hides or bypasses the missing n1/n2 axis."""


S1_EC50_AUDIT_ID = "e1.common-probe-contact-axis-audit.s1ec50.v1"
S1_EC50_EC49_RESULT_DIGEST = (
    "726a04e6c0e4f285e60962d520fba2cf48942e13e717dde9c591b305c35ee29c"
)
S1_EC50_REQUIRED_CONTACT_COUNTS = (1, 2)
S1_EC50_CHECKS = (
    "ec44-source-had-n1-and-n2",
    "ec45-role-inventory-is-reusable-per-contact-count",
    "ec49-formation-handoff-lacks-contact-count",
    "ec49-reset-slot-lacks-contact-count",
    "ec49-role-receipt-lacks-contact-count",
    "ec49-runner-signature-has-no-contact-axis",
    "current-synthetic-sample-count-is-24",
    "required-two-contact-axis-sample-count-is-48",
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeContactAxisAudit:
    audit_id: str
    source_adapter_digest: str
    required_contact_counts: tuple[int, ...]
    contact_count_roles: tuple[tuple[int, str], ...]
    refinements: tuple[str, ...]
    roles_per_contact_count: tuple[str, ...]
    current_sample_count: int
    required_sample_count: int
    checks: tuple[tuple[str, bool], ...]
    n1_role: str
    n2_role: str
    existing_adapter_contact_axis_complete: bool
    contact_axis_correction_permitted: bool
    real_kernel_binding_permitted: bool
    field_execution_permitted: bool
    persistence_permitted: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    decision: str
    reason: str
    audit_digest: str

    def __post_init__(self) -> None:
        if (
            self.audit_id != S1_EC50_AUDIT_ID
            or self.source_adapter_digest != S1_EC50_EC49_RESULT_DIGEST
            or self.required_contact_counts != S1_EC50_REQUIRED_CONTACT_COUNTS
            or self.contact_count_roles != (
                (1, "single-contact-control-branch"),
                (2, "two-contact-observed-order-contrast-branch"),
            )
            or self.refinements != S1_EC47_REFINEMENTS
            or self.roles_per_contact_count != S1_EC45_PROBE_ROLES
            or self.current_sample_count != 24
            or self.required_sample_count != 48
            or tuple(name for name, _ in self.checks) != S1_EC50_CHECKS
            or any(value is not True for _, value in self.checks)
            or self.n1_role != "required-control-not-discardable"
            or self.n2_role != "candidate-branch-not-generalizable-to-n1"
            or self.existing_adapter_contact_axis_complete is not False
            or self.contact_axis_correction_permitted is not True
            or any(value is not False for value in (
                self.real_kernel_binding_permitted,
                self.field_execution_permitted,
                self.persistence_permitted,
                self.research_decision_permitted,
                self.memory_claim_permitted,
            ))
            or self.decision != "KORREKTUR_CONTACT_COUNT_AXIS_MISSING"
            or not self.reason
        ):
            raise E1CommonProbeContactAxisAuditError(
                "S1-EC50 changed or bypassed the missing contact-count axis"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "audit_digest"
        }
        if self.audit_digest != _digest(payload):
            raise E1CommonProbeContactAxisAuditError(
                "S1-EC50 audit digest changed"
            )


def audit_e1_common_probe_contact_axis() -> E1CommonProbeContactAxisAudit:
    """Detect the missing EC44 n1/n2 axis without invoking any adapter."""

    handoff_fields = {item.name for item in fields(E1CommonProbeFormationHandoff)}
    reset_fields = {item.name for item in fields(E1CommonProbeResetSlot)}
    receipt_fields = {item.name for item in fields(E1CommonProbeRoleReceipt)}
    result_fields = {item.name for item in fields(E1CommonProbeEightRoleAdapterFixtureResult)}
    runner_parameters = inspect.signature(
        run_e1_common_probe_eight_role_adapter_fixture
    ).parameters
    current_count = 3 * len(S1_EC45_PROBE_ROLES)
    required_count = len(S1_EC50_REQUIRED_CONTACT_COUNTS) * current_count
    checks = (
        ("ec44-source-had-n1-and-n2", S1_EC50_REQUIRED_CONTACT_COUNTS == (1, 2)),
        ("ec45-role-inventory-is-reusable-per-contact-count", (
            len(S1_EC45_PROBE_ROLES) == 8
            and len(set(S1_EC45_PROBE_ROLES)) == 8
        )),
        ("ec49-formation-handoff-lacks-contact-count", (
            "contact_count" not in handoff_fields
        )),
        ("ec49-reset-slot-lacks-contact-count", (
            "contact_count" not in reset_fields
        )),
        ("ec49-role-receipt-lacks-contact-count", (
            "contact_count" not in receipt_fields
        )),
        ("ec49-runner-signature-has-no-contact-axis", (
            "contact_counts" not in runner_parameters
            and "contact_count" not in result_fields
        )),
        ("current-synthetic-sample-count-is-24", current_count == 24),
        ("required-two-contact-axis-sample-count-is-48", required_count == 48),
    )
    values = {
        "audit_id": S1_EC50_AUDIT_ID,
        "source_adapter_digest": S1_EC50_EC49_RESULT_DIGEST,
        "required_contact_counts": S1_EC50_REQUIRED_CONTACT_COUNTS,
        "contact_count_roles": (
            (1, "single-contact-control-branch"),
            (2, "two-contact-observed-order-contrast-branch"),
        ),
        "refinements": S1_EC47_REFINEMENTS,
        "roles_per_contact_count": S1_EC45_PROBE_ROLES,
        "current_sample_count": current_count,
        "required_sample_count": required_count,
        "checks": checks,
        "n1_role": "required-control-not-discardable",
        "n2_role": "candidate-branch-not-generalizable-to-n1",
        "existing_adapter_contact_axis_complete": False,
        "contact_axis_correction_permitted": True,
        "real_kernel_binding_permitted": False,
        "field_execution_permitted": False,
        "persistence_permitted": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
        "decision": "KORREKTUR_CONTACT_COUNT_AXIS_MISSING",
        "reason": (
            "ec44-separated-n1-and-n2;ec45-through-ec49-dropped-contact-count;"
            "restore-two-branch-axis-before-real-kernel-binding"
        ),
    }
    return E1CommonProbeContactAxisAudit(
        **values,
        audit_digest=_digest(values),
    )
