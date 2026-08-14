"""S1-EC48 static audit of real kernels for the EC45 common probe."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import inspect
from pathlib import Path

from .e1_common_probe_synthetic_runner_fixture import S1_EC47_RUNNER_ID
from .e1_confirmation_formation_runner import E1ConfirmationFormationResult
from .e1_confirmation_prepared_real_formation_kernel import (
    run_prepared_real_formation_arm_in_memory,
)
from .e1_confirmation_seven_arm_probe import S1_EB6_FIELD_ROLES
from .e1_frozen_transient_probe import (
    advance_frozen_e1_fast_shared_field_transient,
)
from .e1_refined_formation_runner import _digest
from .neutral_local_field_substrate import (
    advance_neutral_fast_shared_field_transient,
)


class E1CommonProbeRealKernelAuditError(ValueError):
    """Raised when EC48 changes its static kernel or adapter boundary."""


S1_EC48_AUDIT_ID = "e1.common-probe-real-kernel-audit.s1ec48.v1"
S1_EC48_EC47_RESULT_DIGEST = (
    "45fc3b5bf22451d4ca0aa49422d2523bd02b94558b10688085501fd99aec34f9"
)
S1_EC48_ROLE_MAPPING = (
    ("p0-reset-ab", "neutral-kernel-available:dedicated-slot-missing"),
    ("p0-reset-ba", "neutral-kernel-available:dedicated-slot-missing"),
    ("e1-active-ab", "existing-seven-arm-probe-path"),
    ("e1-active-ba", "existing-seven-arm-probe-path"),
    ("e1-probe-feedback-ablated-ab", "existing-seven-arm-probe-path"),
    ("e1-probe-feedback-ablated-ba", "existing-seven-arm-probe-path"),
    ("e1-formation-ablated-ab", "formed-state-available:probe-slot-missing"),
    ("e1-formation-ablated-ba", "formed-state-available:probe-slot-missing"),
)
S1_EC48_CHECKS = (
    "prepared-real-formation-kernel-present",
    "active-ab-ba-formed-states-present",
    "formation-ablated-ab-ba-states-present",
    "neutral-p0-transient-kernel-present",
    "frozen-e1-transient-kernel-present",
    "explicit-boolean-backreaction-switch-present",
    "existing-probe-has-active-ab-ba-slots",
    "existing-probe-has-feedback-ablation-ab-ba-slots",
    "existing-probe-uses-object-separated-fresh-fields",
    "existing-seven-arm-inventory-is-not-eight-role-contract",
)


def _source_digest(path: Path) -> str:
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class E1CommonProbeRealKernelAudit:
    audit_id: str
    source_fixture_id: str
    source_fixture_digest: str
    implementation_digests: tuple[tuple[str, str], ...]
    role_mapping: tuple[tuple[str, str], ...]
    checks: tuple[tuple[str, bool], ...]
    required_new_adapter_slots: tuple[str, ...]
    existing_kernels_sufficient: bool
    existing_eight_role_adapter_complete: bool
    narrow_adapter_implementation_permitted: bool
    field_execution_permitted: bool
    persistence_permitted: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    decision: str
    reason: str
    audit_digest: str

    def __post_init__(self) -> None:
        if (
            self.audit_id != S1_EC48_AUDIT_ID
            or self.source_fixture_id != S1_EC47_RUNNER_ID
            or self.source_fixture_digest != S1_EC48_EC47_RESULT_DIGEST
            or tuple(role for role, _ in self.implementation_digests) != (
                "formation",
                "probe-adapter",
                "frozen-probe",
                "neutral-field",
            )
            or any(len(value) != 64 for _, value in self.implementation_digests)
            or self.role_mapping != S1_EC48_ROLE_MAPPING
            or tuple(name for name, _ in self.checks) != S1_EC48_CHECKS
            or any(value is not True for _, value in self.checks)
            or self.required_new_adapter_slots != (
                "p0-reset-ab",
                "p0-reset-ba",
                "e1-formation-ablated-ab",
                "e1-formation-ablated-ba",
            )
            or self.existing_kernels_sufficient is not True
            or self.existing_eight_role_adapter_complete is not False
            or self.narrow_adapter_implementation_permitted is not True
            or any(value is not False for value in (
                self.field_execution_permitted,
                self.persistence_permitted,
                self.research_decision_permitted,
                self.memory_claim_permitted,
            ))
            or self.decision != "KERNELS_AVAILABLE_NARROW_EIGHT_ROLE_ADAPTER_MISSING"
            or not self.reason
        ):
            raise E1CommonProbeRealKernelAuditError(
                "S1-EC48 changed or crossed its static audit scope"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "audit_digest"
        }
        if self.audit_digest != _digest(payload):
            raise E1CommonProbeRealKernelAuditError(
                "S1-EC48 audit digest changed"
            )


def audit_e1_common_probe_real_kernels() -> E1CommonProbeRealKernelAudit:
    """Inspect typed APIs and source structure without invoking a kernel."""

    root = Path(__file__).resolve().parent
    formation_fields = tuple(item.name for item in fields(E1ConfirmationFormationResult))
    frozen_signature = inspect.signature(advance_frozen_e1_fast_shared_field_transient)
    formation_signature = inspect.signature(run_prepared_real_formation_arm_in_memory)
    neutral_signature = inspect.signature(advance_neutral_fast_shared_field_transient)
    adapter_source = (root / "e1_confirmation_canonical_probe_adapter.py").read_text(
        encoding="utf-8"
    )
    checks = (
        ("prepared-real-formation-kernel-present", (
            tuple(formation_signature.parameters) == (
                "arm_id", "refinement_id", "sequences", "proposal_steps",
                "initial_field", "initial_state", "formation_enabled",
            )
        )),
        ("active-ab-ba-formed-states-present", (
            "b_ab" in formation_fields and "b_ba" in formation_fields
        )),
        ("formation-ablated-ab-ba-states-present", (
            "b_ab_formation_ablated" in formation_fields
            and "b_ba_formation_ablated" in formation_fields
        )),
        ("neutral-p0-transient-kernel-present", (
            tuple(neutral_signature.parameters)[:2] == ("field", "distribution")
        )),
        ("frozen-e1-transient-kernel-present", (
            tuple(frozen_signature.parameters)[:2] == ("field", "frozen_e1_state")
        )),
        ("explicit-boolean-backreaction-switch-present", (
            "backreaction_enabled" in frozen_signature.parameters
            and frozen_signature.parameters["backreaction_enabled"].kind
            is inspect.Parameter.KEYWORD_ONLY
        )),
        ("existing-probe-has-active-ab-ba-slots", (
            "ab_active" in S1_EB6_FIELD_ROLES and "ba_active" in S1_EB6_FIELD_ROLES
        )),
        ("existing-probe-has-feedback-ablation-ab-ba-slots", (
            "ab_probe_ablated" in S1_EB6_FIELD_ROLES
            and "ba_probe_ablated" in S1_EB6_FIELD_ROLES
        )),
        ("existing-probe-uses-object-separated-fresh-fields", (
            "fields = tuple(field_factory() for _ in S1_EB6_FIELD_ROLES)"
            in adapter_source
            and "requires seven object-separated fields" in adapter_source
        )),
        ("existing-seven-arm-inventory-is-not-eight-role-contract", (
            len(S1_EB6_FIELD_ROLES) == 7
            and "p0" in S1_EB6_FIELD_ROLES
            and "ab_formation_ablated" not in S1_EB6_FIELD_ROLES
            and "ba_formation_ablated" not in S1_EB6_FIELD_ROLES
        )),
    )
    if any(value is not True for _, value in checks):
        failed = ",".join(name for name, value in checks if not value)
        raise E1CommonProbeRealKernelAuditError(
            f"S1-EC48 kernel capability check failed: {failed}"
        )
    values = {
        "audit_id": S1_EC48_AUDIT_ID,
        "source_fixture_id": S1_EC47_RUNNER_ID,
        "source_fixture_digest": S1_EC48_EC47_RESULT_DIGEST,
        "implementation_digests": tuple(
            (role, _source_digest(root / filename))
            for role, filename in (
                ("formation", "e1_confirmation_prepared_real_formation_kernel.py"),
                ("probe-adapter", "e1_confirmation_canonical_probe_adapter.py"),
                ("frozen-probe", "e1_frozen_transient_probe.py"),
                ("neutral-field", "neutral_local_field_substrate.py"),
            )
        ),
        "role_mapping": S1_EC48_ROLE_MAPPING,
        "checks": checks,
        "required_new_adapter_slots": (
            "p0-reset-ab",
            "p0-reset-ba",
            "e1-formation-ablated-ab",
            "e1-formation-ablated-ba",
        ),
        "existing_kernels_sufficient": True,
        "existing_eight_role_adapter_complete": False,
        "narrow_adapter_implementation_permitted": True,
        "field_execution_permitted": False,
        "persistence_permitted": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
        "decision": "KERNELS_AVAILABLE_NARROW_EIGHT_ROLE_ADAPTER_MISSING",
        "reason": (
            "formation-neutral-and-frozen-feedback-kernels-exist;duplicate-p0-"
            "and-formation-ablated-probe-slots-are-not-integrated"
        ),
    }
    return E1CommonProbeRealKernelAudit(
        **values,
        audit_digest=_digest(values),
    )
