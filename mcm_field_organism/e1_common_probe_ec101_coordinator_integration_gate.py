"""S1-EC101 static compatibility gate for future coordinator outputs."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_common_probe_ec96_authorized_r4_r8_once import (
    E1CommonProbeEC96AtomicResult,
    E1CommonProbeEC96RefinementResult,
    run_e1_common_probe_ec96_authorized_r4_r8_once,
)
from .e1_common_probe_ec100_atomic_vector_handoff import (
    build_e1_common_probe_ec100_atomic_vector_handoff,
    build_e1_common_probe_ec100_source_bundle,
)
from .e1_common_probe_n2_r2_real_mode_coordinator import (
    E1CommonProbeN2R2RealModeCoordinatorResult,
    run_e1_common_probe_n2_r2_real_mode_coordinator,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeEC101CoordinatorIntegrationGateError(ValueError):
    """Raised when coordinator outputs no longer fit the closed EC100 input."""


S1_EC101_GATE_ID = "e1.common-probe-coordinator-integration-gate.s1ec101.v1"
S1_EC101_COORDINATOR_NAMES = (
    "run_e1_common_probe_n2_r2_real_mode_coordinator",
    "run_e1_common_probe_ec96_authorized_r4_r8_once",
)
S1_EC101_RESULT_TYPES = (
    "E1CommonProbeN2R2RealModeCoordinatorResult",
    "E1CommonProbeEC96AtomicResult",
    "E1CommonProbeEC96RefinementResult",
)
S1_EC101_EXTRACTION_CONTRACT = (
    ("r2", "r2_result.probes", "E1PositiveStepProbeReceipt", 8),
    ("r4", "r4_r8_result.refinements[0].probes", "E1CommonProbeEC91ProbeReceipt", 8),
    ("r8", "r4_r8_result.refinements[1].probes", "E1CommonProbeEC91ProbeReceipt", 8),
)
S1_EC101_CHECK_NAMES = (
    "r2-result-exposes-typed-probes",
    "r2-result-binds-eight-probes",
    "r4-r8-result-exposes-refinements",
    "refinement-result-exposes-typed-probes",
    "r4-r8-result-binds-two-ordered-refinements",
    "ec100-source-accepts-r2-and-r4-r8-probes",
    "ec100-handoff-accepts-one-closed-source",
    "coordinator-result-types-are-explicit",
    "same-process-extraction-contract-complete",
    "gate-does-not-call-coordinators",
    "gate-does-not-call-field-kernels",
    "gate-does-not-write-or-decide",
)
S1_EC101_COORDINATOR_CALL_NAMES = frozenset(S1_EC101_COORDINATOR_NAMES)
S1_EC101_FIELD_CALL_NAMES = frozenset(
    {
        "advance_frozen_e1_fast_shared_field_transient",
        "advance_neutral_fast_shared_field_transient",
        "run_e1_common_probe_real_probe_wrapper",
    }
)
S1_EC101_WRITE_DECISION_CALL_NAMES = frozenset(
    {"write_text", "write_bytes", "open", "decide_common_probe_evidence"}
)


def _called_function_names(source: str) -> frozenset[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            names.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            names.add(node.func.attr)
    return frozenset(names)


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC101CoordinatorIntegrationGate:
    gate_id: str
    coordinator_names: tuple[str, ...]
    result_types: tuple[str, ...]
    extraction_contract: tuple[tuple[str, str, str, int], ...]
    checks: tuple[tuple[str, bool], ...]
    required_refinement_ids: tuple[str, ...]
    required_probe_counts: tuple[tuple[str, int], ...]
    total_source_probe_count: int
    same_process_handoff_required: bool
    ec100_source_bundle_required: bool
    ec99_then_ec98_order_required: bool
    new_owner_authorization_required_for_future_execution: bool
    coordinator_execution_permitted: bool
    field_execution_performed: bool
    persistence_permitted: bool
    retry_permitted: bool
    ec46_decision_permitted: bool
    research_decision_permitted: bool
    claims_permitted: bool
    decision: str
    reason: str
    gate_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "gate_digest"
        }
        if (
            self.gate_id != S1_EC101_GATE_ID
            or self.coordinator_names != S1_EC101_COORDINATOR_NAMES
            or self.result_types != S1_EC101_RESULT_TYPES
            or self.extraction_contract != S1_EC101_EXTRACTION_CONTRACT
            or tuple(name for name, _ in self.checks) != S1_EC101_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or self.required_refinement_ids != ("r2", "r4", "r8")
            or self.required_probe_counts != (("r2", 8), ("r4", 8), ("r8", 8))
            or self.total_source_probe_count != 24
            or any(
                value is not True
                for value in (
                    self.same_process_handoff_required,
                    self.ec100_source_bundle_required,
                    self.ec99_then_ec98_order_required,
                    self.new_owner_authorization_required_for_future_execution,
                )
            )
            or any(
                value is not False
                for value in (
                    self.coordinator_execution_permitted,
                    self.field_execution_performed,
                    self.persistence_permitted,
                    self.retry_permitted,
                    self.ec46_decision_permitted,
                    self.research_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "COORDINATOR_OUTPUTS_COMPATIBLE_EC100_INTEGRATION_GATE_CLOSED"
            or not self.reason
            or self.gate_digest != _digest(payload)
        ):
            raise E1CommonProbeEC101CoordinatorIntegrationGateError(
                "S1-EC101 gate changed or opened execution"
            )


def audit_e1_common_probe_ec101_coordinator_integration_gate(
) -> E1CommonProbeEC101CoordinatorIntegrationGate:
    """Audit schemas and signatures without invoking either coordinator."""

    r2_fields = E1CommonProbeN2R2RealModeCoordinatorResult.__dataclass_fields__
    r4_r8_fields = E1CommonProbeEC96AtomicResult.__dataclass_fields__
    refinement_fields = E1CommonProbeEC96RefinementResult.__dataclass_fields__
    r2_source = inspect.getsource(E1CommonProbeN2R2RealModeCoordinatorResult)
    r4_r8_source = inspect.getsource(E1CommonProbeEC96AtomicResult)
    gate_source = inspect.getsource(
        audit_e1_common_probe_ec101_coordinator_integration_gate
    )
    called_names = _called_function_names(gate_source)
    source_signature = inspect.signature(build_e1_common_probe_ec100_source_bundle)
    handoff_signature = inspect.signature(
        build_e1_common_probe_ec100_atomic_vector_handoff
    )
    coordinator_signatures = (
        inspect.signature(run_e1_common_probe_n2_r2_real_mode_coordinator),
        inspect.signature(run_e1_common_probe_ec96_authorized_r4_r8_once),
    )
    checks = (
        (
            S1_EC101_CHECK_NAMES[0],
            str(r2_fields["probes"].type)
            == "tuple[E1PositiveStepProbeReceipt, ...]",
        ),
        (
            S1_EC101_CHECK_NAMES[1],
            "self.probe_count" in r2_source and "!= (4, 8, 8)" in r2_source,
        ),
        (
            S1_EC101_CHECK_NAMES[2],
            str(r4_r8_fields["refinements"].type)
            == "tuple[E1CommonProbeEC96RefinementResult, ...]",
        ),
        (
            S1_EC101_CHECK_NAMES[3],
            str(refinement_fields["probes"].type)
            == "tuple[E1CommonProbeEC91ProbeReceipt, ...]",
        ),
        (
            S1_EC101_CHECK_NAMES[4],
            "self.refinement_ids != (\"r4\", \"r8\")" in r4_r8_source
            and "len(self.probes) != 8" in inspect.getsource(
                E1CommonProbeEC96RefinementResult
            ),
        ),
        (
            S1_EC101_CHECK_NAMES[5],
            tuple(source_signature.parameters) == ("r2_probes", "r4_r8_probes"),
        ),
        (
            S1_EC101_CHECK_NAMES[6],
            tuple(handoff_signature.parameters) == ("source_bundle",),
        ),
        (
            S1_EC101_CHECK_NAMES[7],
            tuple(str(item.return_annotation) for item in coordinator_signatures)
            == (
                "E1CommonProbeN2R2RealModeCoordinatorResult",
                "E1CommonProbeEC96AtomicResult",
            ),
        ),
        (
            S1_EC101_CHECK_NAMES[8],
            sum(item[3] for item in S1_EC101_EXTRACTION_CONTRACT) == 24
            and tuple(item[0] for item in S1_EC101_EXTRACTION_CONTRACT)
            == ("r2", "r4", "r8"),
        ),
        (
            S1_EC101_CHECK_NAMES[9],
            called_names.isdisjoint(S1_EC101_COORDINATOR_CALL_NAMES),
        ),
        (
            S1_EC101_CHECK_NAMES[10],
            called_names.isdisjoint(S1_EC101_FIELD_CALL_NAMES),
        ),
        (
            S1_EC101_CHECK_NAMES[11],
            called_names.isdisjoint(S1_EC101_WRITE_DECISION_CALL_NAMES),
        ),
    )
    values = {
        "gate_id": S1_EC101_GATE_ID,
        "coordinator_names": S1_EC101_COORDINATOR_NAMES,
        "result_types": S1_EC101_RESULT_TYPES,
        "extraction_contract": S1_EC101_EXTRACTION_CONTRACT,
        "checks": checks,
        "required_refinement_ids": ("r2", "r4", "r8"),
        "required_probe_counts": (("r2", 8), ("r4", 8), ("r8", 8)),
        "total_source_probe_count": 24,
        "same_process_handoff_required": True,
        "ec100_source_bundle_required": True,
        "ec99_then_ec98_order_required": True,
        "new_owner_authorization_required_for_future_execution": True,
        "coordinator_execution_permitted": False,
        "field_execution_performed": False,
        "persistence_permitted": False,
        "retry_permitted": False,
        "ec46_decision_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "decision": "COORDINATOR_OUTPUTS_COMPATIBLE_EC100_INTEGRATION_GATE_CLOSED",
        "reason": (
            "r2 exposes eight EC63 probe receipts; ordered r4/r8 refinements "
            "expose sixteen EC91 probe receipts; EC100 accepts exactly these "
            "types, while execution and decision remain closed"
        ),
    }
    return E1CommonProbeEC101CoordinatorIntegrationGate(
        **values, gate_digest=_digest(values)
    )
