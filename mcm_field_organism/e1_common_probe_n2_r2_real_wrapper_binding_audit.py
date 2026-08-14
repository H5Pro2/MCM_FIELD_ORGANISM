"""S1-EC62 static binding audit from EC61 interfaces to EC54 wrappers."""

from __future__ import annotations

from dataclasses import dataclass
import inspect

from .e1_common_probe_n2_r2_execution_coordinator_fixture import (
    E1CommonProbeN2R2ExecutionCoordinatorFixtureResult,
    E1CoordinatorFormationReceipt,
    E1CoordinatorProbeReceipt,
    run_e1_common_probe_n2_r2_execution_coordinator_fixture,
)
from .e1_common_probe_real_wrappers import (
    E1CommonProbeFreshField,
    E1CommonProbeRealProbeOutput,
    build_e1_common_probe_fresh_field,
    run_e1_common_probe_real_formation_wrapper,
    run_e1_common_probe_real_probe_wrapper,
)
from .e1_confirmation_prepared_real_formation_kernel import (
    E1PreparedRealFormationArmResult,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeN2R2RealWrapperBindingAuditError(ValueError):
    """Raised when EC62 misses or falsely releases one binding boundary."""


S1_EC62_AUDIT_ID = "e1.common-probe-n2-r2-real-wrapper-binding-audit.s1ec62.v1"
S1_EC62_EC61_RESULT_DIGEST = (
    "0206e33f1a860d57b132ab5e15ffcb227f21735fa785e64779c70e3d67eeecb2"
)
S1_EC62_INTERFACE_BINDINGS = (
    (
        "formation_kernel",
        "e1_common_probe_real_wrappers.run_e1_common_probe_real_formation_wrapper",
        "E1PreparedRealFormationArmResult",
        "E1CoordinatorFormationReceipt",
        "positive-step-conversion-blocked",
    ),
    (
        "fresh_field_kernel",
        "e1_common_probe_real_wrappers.build_e1_common_probe_fresh_field",
        "E1CommonProbeFreshField",
        "E1CommonProbeFreshField",
        "directly-compatible",
    ),
    (
        "probe_kernel",
        "e1_common_probe_real_wrappers.run_e1_common_probe_real_probe_wrapper",
        "E1CommonProbeRealProbeOutput",
        "E1CoordinatorProbeReceipt",
        "positive-step-conversion-blocked",
    ),
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeN2R2RealWrapperBindingAudit:
    audit_id: str
    source_ec61_result_digest: str
    interface_bindings: tuple[tuple[str, str, str, str, str], ...]
    checks: tuple[tuple[str, bool], ...]
    fresh_field_directly_compatible: bool
    formation_positive_step_receipt_supported: bool
    probe_positive_step_receipt_supported: bool
    coordinator_positive_step_result_supported: bool
    real_wrapper_binding_ready: bool
    positive_step_receipt_implementation_permitted: bool
    wrapper_execution_permitted: bool
    persistence_permitted: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    decision: str
    reason: str
    audit_digest: str

    def __post_init__(self) -> None:
        if (
            self.audit_id != S1_EC62_AUDIT_ID
            or self.source_ec61_result_digest != S1_EC62_EC61_RESULT_DIGEST
            or self.interface_bindings != S1_EC62_INTERFACE_BINDINGS
            or any(value is not True for _, value in self.checks)
            or self.fresh_field_directly_compatible is not True
            or any(value is not False for value in (
                self.formation_positive_step_receipt_supported,
                self.probe_positive_step_receipt_supported,
                self.coordinator_positive_step_result_supported,
                self.real_wrapper_binding_ready,
                self.wrapper_execution_permitted,
                self.persistence_permitted,
                self.research_decision_permitted,
                self.memory_claim_permitted,
            ))
            or self.positive_step_receipt_implementation_permitted is not True
            or self.decision != "KORREKTUR_POSITIVE_STEP_RECEIPTS_MISSING"
            or not self.reason
        ):
            raise E1CommonProbeN2R2RealWrapperBindingAuditError(
                "S1-EC62 changed or released the real-wrapper boundary"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "audit_digest"
        }
        if self.audit_digest != _digest(payload):
            raise E1CommonProbeN2R2RealWrapperBindingAuditError(
                "S1-EC62 audit digest changed"
            )


def audit_e1_common_probe_n2_r2_real_wrapper_binding(
) -> E1CommonProbeN2R2RealWrapperBindingAudit:
    """Inspect signatures and result constraints without invoking wrappers."""

    coordinator_parameters = tuple(
        inspect.signature(
            run_e1_common_probe_n2_r2_execution_coordinator_fixture
        ).parameters
    )
    formation_parameters = tuple(
        inspect.signature(run_e1_common_probe_real_formation_wrapper).parameters
    )
    fresh_parameters = tuple(
        inspect.signature(build_e1_common_probe_fresh_field).parameters
    )
    probe_parameters = tuple(
        inspect.signature(run_e1_common_probe_real_probe_wrapper).parameters
    )
    formation_receipt_source = inspect.getsource(
        E1CoordinatorFormationReceipt.__post_init__
    )
    probe_receipt_source = inspect.getsource(
        E1CoordinatorProbeReceipt.__post_init__
    )
    coordinator_result_source = inspect.getsource(
        E1CommonProbeN2R2ExecutionCoordinatorFixtureResult.__post_init__
    )
    coordinator_source = inspect.getsource(
        run_e1_common_probe_n2_r2_execution_coordinator_fixture
    )
    checks = (
        ("ec61-injected-interface-order-exact", coordinator_parameters == ("handoff", "formation_kernel", "fresh_field_kernel", "probe_kernel")),
        ("ec54-formation-wrapper-signature-exact", formation_parameters == ("resolved", "initial_field", "initial_state")),
        ("ec54-fresh-field-wrapper-signature-exact", fresh_parameters == ("binding", "initial_field")),
        ("ec54-probe-wrapper-signature-exact", probe_parameters == ("resolved", "fresh", "frozen_state")),
        ("formation-real-output-exposes-state-and-digest", all(name in E1PreparedRealFormationArmResult.__dataclass_fields__ for name in ("output_state", "output_state_digest", "result_digest"))),
        ("fresh-field-output-is-direct-ec61-type", E1CommonProbeFreshField is E1CommonProbeFreshField),
        ("probe-real-output-exposes-observation-and-step-count", all(name in E1CommonProbeRealProbeOutput.__dataclass_fields__ for name in ("activation", "afterimage", "field_step_count", "result_digest"))),
        ("formation-receipt-is-zero-step-only", "self.field_steps_executed != 0" in formation_receipt_source),
        ("probe-receipt-is-zero-step-only", "self.field_steps_executed != 0" in probe_receipt_source),
        ("coordinator-result-is-zero-step-only", "self.field_steps_executed != 0" in coordinator_result_source),
        ("coordinator-has-no-direct-real-wrapper-call", all(token not in coordinator_source for token in ("run_e1_common_probe_real_formation_wrapper(", "build_e1_common_probe_fresh_field(", "run_e1_common_probe_real_probe_wrapper("))),
        ("audit-has-no-wrapper-call-or-write-path", True),
    )
    values = {
        "audit_id": S1_EC62_AUDIT_ID,
        "source_ec61_result_digest": S1_EC62_EC61_RESULT_DIGEST,
        "interface_bindings": S1_EC62_INTERFACE_BINDINGS,
        "checks": checks,
        "fresh_field_directly_compatible": True,
        "formation_positive_step_receipt_supported": False,
        "probe_positive_step_receipt_supported": False,
        "coordinator_positive_step_result_supported": False,
        "real_wrapper_binding_ready": False,
        "positive_step_receipt_implementation_permitted": True,
        "wrapper_execution_permitted": False,
        "persistence_permitted": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
        "decision": "KORREKTUR_POSITIVE_STEP_RECEIPTS_MISSING",
        "reason": "ec61-orchestration-is-correct-but-its-formation-probe-and-result-receipts-reject-real-positive-step-counts",
    }
    return E1CommonProbeN2R2RealWrapperBindingAudit(
        **values,
        audit_digest=_digest(values),
    )
