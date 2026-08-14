"""S1-EC104 static provenance gate for future EC67/EC96 result ingress."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_common_probe_ec96_authorized_r4_r8_once import (
    E1CommonProbeEC96AtomicResult,
    E1CommonProbeEC96RefinementResult,
)
from .e1_common_probe_ec102_coordinator_result_extractor import (
    extract_e1_common_probe_ec102_coordinator_results,
)
from .e1_common_probe_n2_r2_real_mode_coordinator import (
    E1CommonProbeN2R2RealModeCoordinatorResult,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeEC104RealResultProvenanceGateError(ValueError):
    """Raised when the EC104 fail-closed provenance gate is changed."""


S1_EC104_GATE_ID = "e1.common-probe-real-result-provenance-gate.s1ec104.v1"
S1_EC104_REQUIRED_ATTESTATION_FIELDS = (
    "producer_id",
    "one_shot_authorization_digest",
    "source_result_digests",
    "source_probe_receipt_digests",
    "accounted_field_steps",
    "producer_sequence",
    "attestation_digest",
)
S1_EC104_CONSTRUCTIBLE_MARKERS = (
    "execution_mode",
    "actual_field_steps_executed",
    "authorization_digest",
    "authorization_consumed",
    "exactly_once_completed",
)
S1_EC104_CHECK_NAMES = (
    "ec67-result-type-explicit",
    "ec96-result-types-explicit",
    "current-real-markers-are-plain-fields",
    "ec67-has-no-atomic-producer-attestation",
    "ec96-has-no-atomic-producer-attestation",
    "ec102-has-no-attestation-parameter",
    "gate-does-not-call-extractor",
    "gate-does-not-call-coordinators",
    "gate-does-not-call-field-kernels",
    "gate-does-not-write-or-decide",
)
S1_EC104_FORBIDDEN_CALLS = frozenset(
    {
        "extract_e1_common_probe_ec102_coordinator_results",
        "run_e1_common_probe_n2_r2_real_mode_coordinator",
        "run_e1_common_probe_ec96_authorized_r4_r8_once",
        "advance_frozen_e1_fast_shared_field_transient",
        "advance_neutral_fast_shared_field_transient",
        "run_e1_common_probe_real_formation_wrapper",
        "run_e1_common_probe_real_probe_wrapper",
        "decide_common_probe_evidence",
        "write_text",
        "write_bytes",
        "open",
    }
)


def _called_names(source: str) -> frozenset[str]:
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
class E1CommonProbeEC104RealResultProvenanceGate:
    gate_id: str
    source_result_types: tuple[str, ...]
    constructible_markers: tuple[str, ...]
    required_attestation_fields: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    outer_result_contracts_validatable: bool
    nested_receipt_contracts_validatable: bool
    actual_execution_provenance_established: bool
    current_results_admissible_as_real_execution: bool
    ec102_ingress_permitted: bool
    new_execution_permitted: bool
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
            self.gate_id != S1_EC104_GATE_ID
            or self.source_result_types
            != (
                "E1CommonProbeN2R2RealModeCoordinatorResult",
                "E1CommonProbeEC96AtomicResult",
                "E1CommonProbeEC96RefinementResult",
            )
            or self.constructible_markers != S1_EC104_CONSTRUCTIBLE_MARKERS
            or self.required_attestation_fields
            != S1_EC104_REQUIRED_ATTESTATION_FIELDS
            or tuple(name for name, _ in self.checks) != S1_EC104_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or self.outer_result_contracts_validatable is not True
            or self.nested_receipt_contracts_validatable is not True
            or any(
                value is not False
                for value in (
                    self.actual_execution_provenance_established,
                    self.current_results_admissible_as_real_execution,
                    self.ec102_ingress_permitted,
                    self.new_execution_permitted,
                    self.persistence_permitted,
                    self.retry_permitted,
                    self.ec46_decision_permitted,
                    self.research_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "REAL_RESULT_PROVENANCE_NOT_ESTABLISHED_INGRESS_CLOSED"
            or not self.reason
            or self.gate_digest != _digest(payload)
        ):
            raise E1CommonProbeEC104RealResultProvenanceGateError(
                "S1-EC104 provenance gate changed or opened an unproven ingress"
            )


def audit_e1_common_probe_ec104_real_result_provenance_gate(
) -> E1CommonProbeEC104RealResultProvenanceGate:
    """Show statically why current result metadata cannot attest execution."""

    r2_fields = E1CommonProbeN2R2RealModeCoordinatorResult.__dataclass_fields__
    atomic_fields = E1CommonProbeEC96AtomicResult.__dataclass_fields__
    refinement_fields = E1CommonProbeEC96RefinementResult.__dataclass_fields__
    extractor_parameters = inspect.signature(
        extract_e1_common_probe_ec102_coordinator_results
    ).parameters
    source = inspect.getsource(audit_e1_common_probe_ec104_real_result_provenance_gate)
    called = _called_names(source)
    source_types = (
        "E1CommonProbeN2R2RealModeCoordinatorResult",
        "E1CommonProbeEC96AtomicResult",
        "E1CommonProbeEC96RefinementResult",
    )
    current_fields = set(r2_fields) | set(atomic_fields) | set(refinement_fields)
    checks = (
        (S1_EC104_CHECK_NAMES[0], "probes" in r2_fields and "formations" in r2_fields),
        (
            S1_EC104_CHECK_NAMES[1],
            "refinements" in atomic_fields
            and "probes" in refinement_fields
            and "formations" in refinement_fields,
        ),
        (
            S1_EC104_CHECK_NAMES[2],
            set(S1_EC104_CONSTRUCTIBLE_MARKERS).issubset(current_fields),
        ),
        (
            S1_EC104_CHECK_NAMES[3],
            set(S1_EC104_REQUIRED_ATTESTATION_FIELDS).isdisjoint(r2_fields),
        ),
        (
            S1_EC104_CHECK_NAMES[4],
            set(S1_EC104_REQUIRED_ATTESTATION_FIELDS).isdisjoint(atomic_fields),
        ),
        (
            S1_EC104_CHECK_NAMES[5],
            "producer_attestation" not in extractor_parameters,
        ),
        (
            S1_EC104_CHECK_NAMES[6],
            "extract_e1_common_probe_ec102_coordinator_results" not in called,
        ),
        (
            S1_EC104_CHECK_NAMES[7],
            called.isdisjoint(
                {
                    "run_e1_common_probe_n2_r2_real_mode_coordinator",
                    "run_e1_common_probe_ec96_authorized_r4_r8_once",
                }
            ),
        ),
        (
            S1_EC104_CHECK_NAMES[8],
            called.isdisjoint(
                {
                    "advance_frozen_e1_fast_shared_field_transient",
                    "advance_neutral_fast_shared_field_transient",
                    "run_e1_common_probe_real_formation_wrapper",
                    "run_e1_common_probe_real_probe_wrapper",
                }
            ),
        ),
        (
            S1_EC104_CHECK_NAMES[9],
            called.isdisjoint({"write_text", "write_bytes", "open", "decide_common_probe_evidence"}),
        ),
    )
    values = {
        "gate_id": S1_EC104_GATE_ID,
        "source_result_types": source_types,
        "constructible_markers": S1_EC104_CONSTRUCTIBLE_MARKERS,
        "required_attestation_fields": S1_EC104_REQUIRED_ATTESTATION_FIELDS,
        "checks": checks,
        "outer_result_contracts_validatable": True,
        "nested_receipt_contracts_validatable": True,
        "actual_execution_provenance_established": False,
        "current_results_admissible_as_real_execution": False,
        "ec102_ingress_permitted": False,
        "new_execution_permitted": False,
        "persistence_permitted": False,
        "retry_permitted": False,
        "ec46_decision_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "decision": "REAL_RESULT_PROVENANCE_NOT_ESTABLISHED_INGRESS_CLOSED",
        "reason": (
            "current EC67/EC96 execution markers are constructible metadata; "
            "neither result binds one atomic producer attestation to both result "
            "digests, all 24 probe digests, step accounting, and authorization"
        ),
    }
    return E1CommonProbeEC104RealResultProvenanceGate(
        **values, gate_digest=_digest(values)
    )
