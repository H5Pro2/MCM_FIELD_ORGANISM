"""S1-EC109 static integration gate for EC67's future attested envelope."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_common_probe_ec101_coordinator_integration_gate import (
    audit_e1_common_probe_ec101_coordinator_integration_gate,
)
from .e1_common_probe_ec102_coordinator_result_extractor import (
    extract_e1_common_probe_ec102_coordinator_results,
)
from .e1_common_probe_ec108_r2_token_and_return_envelope import (
    E1CommonProbeEC108R2AttestedCoordinatorEnvelope,
)
from .e1_common_probe_n2_r2_real_mode_coordinator import (
    run_e1_common_probe_n2_r2_real_mode_coordinator,
)
from .e1_common_probe_r2_ec82_coordinator_handoff import (
    reduce_e1_common_probe_r2_ec82_completed_result,
)
from .e1_common_probe_r2_ec84_atomic_return import (
    build_e1_common_probe_r2_ec84_atomic_return,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeEC109EC67ConsumerIntegrationGateError(ValueError):
    """Raised when the EC109 migration map changes or opens integration."""


S1_EC109_GATE_ID = "e1.common-probe-ec67-consumer-integration-gate.s1ec109.v1"
S1_EC109_RUNTIME_CONSUMERS = (
    (
        "EC82",
        "reduce_e1_common_probe_r2_ec82_completed_result",
        "accept-envelope-validate-then-reduce-envelope.result",
    ),
    (
        "EC84",
        "build_e1_common_probe_r2_ec84_atomic_return",
        "accept-envelope-and-bind-envelope-plus-scalar-receipt",
    ),
    (
        "EC102",
        "extract_e1_common_probe_ec102_coordinator_results",
        "require-r2-envelope-and-future-combined-attestation",
    ),
)
S1_EC109_STATIC_CONSUMERS = (
    (
        "EC101",
        "audit_e1_common_probe_ec101_coordinator_integration_gate",
        "expect-attested-envelope-return-type",
    ),
    (
        "EC104-EC105",
        "provenance-and-attestation-audits",
        "recognize-integrated-r2-producer-receipt",
    ),
    (
        "EC103-EC106-EC108",
        "synthetic-fixtures",
        "retain-explicit-synthetic-scope-and-no-real-ingress",
    ),
)
S1_EC109_MIGRATION_ORDER = (
    "implement-owner-scope-r2-token-without-execution",
    "add-attested-envelope-return-path-inside-ec67",
    "migrate-ec82-to-envelope-input",
    "migrate-ec84-to-envelope-input-and-envelope-binding",
    "migrate-ec102-to-envelope-plus-attestation-input",
    "update-ec101-and-provenance-audits",
    "update-synthetic-fixtures",
    "run-full-static-and-synthetic-regression",
)
S1_EC109_CHECK_NAMES = (
    "ec67-still-returns-bare-result",
    "ec82-still-accepts-bare-result",
    "ec84-still-accepts-bare-result",
    "ec102-still-accepts-bare-r2-result",
    "ec101-still-audits-bare-return",
    "ec108-envelope-exposes-result-and-producer-receipt",
    "three-runtime-consumers-mapped",
    "three-static-consumer-groups-mapped",
    "migration-orders-producer-before-consumers",
    "gate-does-not-call-production-write-or-decide",
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
class E1CommonProbeEC109EC67ConsumerIntegrationGate:
    gate_id: str
    target_envelope_type: str
    runtime_consumers: tuple[tuple[str, str, str], ...]
    static_consumers: tuple[tuple[str, str, str], ...]
    migration_order: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    runtime_consumer_count: int
    static_consumer_group_count: int
    all_current_consumers_expect_bare_result: bool
    envelope_migration_complete: bool
    owner_scope_token_implemented: bool
    ec67_attested_return_implemented: bool
    ec82_migrated: bool
    ec84_migrated: bool
    ec102_migrated: bool
    static_audits_migrated: bool
    execution_permitted: bool
    persistence_permitted: bool
    retry_permitted: bool
    real_result_ingress_permitted: bool
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
            self.gate_id != S1_EC109_GATE_ID
            or self.target_envelope_type
            != "E1CommonProbeEC108R2AttestedCoordinatorEnvelope"
            or self.runtime_consumers != S1_EC109_RUNTIME_CONSUMERS
            or self.static_consumers != S1_EC109_STATIC_CONSUMERS
            or self.migration_order != S1_EC109_MIGRATION_ORDER
            or tuple(name for name, _ in self.checks) != S1_EC109_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or (self.runtime_consumer_count, self.static_consumer_group_count)
            != (3, 3)
            or self.all_current_consumers_expect_bare_result is not True
            or any(
                value is not False
                for value in (
                    self.envelope_migration_complete,
                    self.owner_scope_token_implemented,
                    self.ec67_attested_return_implemented,
                    self.ec82_migrated,
                    self.ec84_migrated,
                    self.ec102_migrated,
                    self.static_audits_migrated,
                    self.execution_permitted,
                    self.persistence_permitted,
                    self.retry_permitted,
                    self.real_result_ingress_permitted,
                    self.ec46_decision_permitted,
                    self.research_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "EC108_EC67_CONSUMER_MIGRATION_MAPPED_INTEGRATION_CLOSED"
            or not self.reason
            or self.gate_digest != _digest(payload)
        ):
            raise E1CommonProbeEC109EC67ConsumerIntegrationGateError(
                "S1-EC109 integration gate changed or opened migration"
            )


def audit_e1_common_probe_ec109_ec67_consumer_integration_gate(
) -> E1CommonProbeEC109EC67ConsumerIntegrationGate:
    """Map every direct consumer without invoking any producer or consumer."""

    producer_signature = inspect.signature(
        run_e1_common_probe_n2_r2_real_mode_coordinator
    )
    ec82_signature = inspect.signature(
        reduce_e1_common_probe_r2_ec82_completed_result
    )
    ec84_signature = inspect.signature(build_e1_common_probe_r2_ec84_atomic_return)
    ec102_signature = inspect.signature(
        extract_e1_common_probe_ec102_coordinator_results
    )
    envelope_fields = E1CommonProbeEC108R2AttestedCoordinatorEnvelope.__dataclass_fields__
    ec101_source = inspect.getsource(
        audit_e1_common_probe_ec101_coordinator_integration_gate
    )
    source = inspect.getsource(
        audit_e1_common_probe_ec109_ec67_consumer_integration_gate
    )
    called = _called_names(source)
    forbidden_calls = {
        "run_e1_common_probe_n2_r2_real_mode_coordinator",
        "reduce_e1_common_probe_r2_ec82_completed_result",
        "build_e1_common_probe_r2_ec84_atomic_return",
        "extract_e1_common_probe_ec102_coordinator_results",
        "run_e1_common_probe_real_formation_receipt_adapter",
        "run_e1_common_probe_real_probe_receipt_adapter",
        "decide_common_probe_evidence",
        "write_text",
        "write_bytes",
        "open",
    }
    checks = (
        (
            S1_EC109_CHECK_NAMES[0],
            str(producer_signature.return_annotation)
            == "E1CommonProbeN2R2RealModeCoordinatorResult",
        ),
        (
            S1_EC109_CHECK_NAMES[1],
            str(ec82_signature.parameters["result"].annotation)
            == "E1CommonProbeN2R2RealModeCoordinatorResult",
        ),
        (
            S1_EC109_CHECK_NAMES[2],
            str(ec84_signature.parameters["completed_result"].annotation)
            == "E1CommonProbeN2R2RealModeCoordinatorResult",
        ),
        (
            S1_EC109_CHECK_NAMES[3],
            str(ec102_signature.parameters["r2_result"].annotation)
            == "E1CommonProbeN2R2RealModeCoordinatorResult",
        ),
        (
            S1_EC109_CHECK_NAMES[4],
            "E1CommonProbeN2R2RealModeCoordinatorResult" in ec101_source
            and "E1CommonProbeEC108R2AttestedCoordinatorEnvelope"
            not in ec101_source,
        ),
        (
            S1_EC109_CHECK_NAMES[5],
            {"result", "producer_receipt", "token", "envelope_digest"}.issubset(
                envelope_fields
            ),
        ),
        (S1_EC109_CHECK_NAMES[6], len(S1_EC109_RUNTIME_CONSUMERS) == 3),
        (S1_EC109_CHECK_NAMES[7], len(S1_EC109_STATIC_CONSUMERS) == 3),
        (
            S1_EC109_CHECK_NAMES[8],
            S1_EC109_MIGRATION_ORDER.index(
                "add-attested-envelope-return-path-inside-ec67"
            )
            < S1_EC109_MIGRATION_ORDER.index("migrate-ec82-to-envelope-input")
            < S1_EC109_MIGRATION_ORDER.index(
                "migrate-ec102-to-envelope-plus-attestation-input"
            ),
        ),
        (S1_EC109_CHECK_NAMES[9], called.isdisjoint(forbidden_calls)),
    )
    values = {
        "gate_id": S1_EC109_GATE_ID,
        "target_envelope_type": "E1CommonProbeEC108R2AttestedCoordinatorEnvelope",
        "runtime_consumers": S1_EC109_RUNTIME_CONSUMERS,
        "static_consumers": S1_EC109_STATIC_CONSUMERS,
        "migration_order": S1_EC109_MIGRATION_ORDER,
        "checks": checks,
        "runtime_consumer_count": 3,
        "static_consumer_group_count": 3,
        "all_current_consumers_expect_bare_result": True,
        "envelope_migration_complete": False,
        "owner_scope_token_implemented": False,
        "ec67_attested_return_implemented": False,
        "ec82_migrated": False,
        "ec84_migrated": False,
        "ec102_migrated": False,
        "static_audits_migrated": False,
        "execution_permitted": False,
        "persistence_permitted": False,
        "retry_permitted": False,
        "real_result_ingress_permitted": False,
        "ec46_decision_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "decision": "EC108_EC67_CONSUMER_MIGRATION_MAPPED_INTEGRATION_CLOSED",
        "reason": (
            "EC82, EC84, and EC102 still accept the bare EC67 result; EC101 and "
            "the provenance fixtures also require coordinated migration before "
            "the attested envelope can replace the current return type"
        ),
    }
    return E1CommonProbeEC109EC67ConsumerIntegrationGate(
        **values, gate_digest=_digest(values)
    )
