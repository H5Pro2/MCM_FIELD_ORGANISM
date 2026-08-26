"""Private S1-WN composition of existing injected H0 receipts."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from ._ppb1_s1wh_private_injected_coordinator_shell import (
    S1WGExactProductionAuthorizationActivator,
    S1WGPrivateProductionCoordinator,
    S1WGPrivateS1VQProducerResolver,
    S1WGProductionArtifactRootResolver,
    S1WGProductionLockTerminalAdapter,
    S1WGProductionResourceObserverAdapter,
    S1WHCoordinatorResult,
    S1WHInjectedStageAdapter,
)
from ._ppb1_s1wj_injected_root_resource_adapters import (
    S1WJInjectedResourceReceipt,
    S1WJRootMirrorReceipt,
)
from ._ppb1_s1wl_private_authorization_validator_adapter import (
    S1WLInjectedAuthorizationValidationReceipt,
)


S1WN_SCHEMA_VERSION = "ppb1.s1wn.private.receipt-coordinator-composition.v1"
S1WN_MODE = "EXISTING_INJECTED_RECEIPTS_IN_MEMORY_ONLY"
S1WN_DECISION = (
    "BLOCKED_AT_H2_RECEIPTS_COMPOSED_NO_PRODUCTION_AUTHORIZATION"
)
S1WN_INVALID_RECEIPT_CHAIN = "S1WN_INVALID_RECEIPT_CHAIN"
S1WN_PRODUCTION_EXECUTION_BLOCKED = "S1WN_PRODUCTION_EXECUTION_BLOCKED"


class S1WNCompositionError(ValueError):
    """One fail-closed S1-WN receipt composition violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _canonical_bytes(payload: object) -> bytes:
    return json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _digest(payload: object) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


@dataclass(frozen=True, slots=True)
class S1WNReceiptCompositionResult:
    decision: str
    root_receipt_digest: str
    resource_receipt_digest: str
    authorization_validation_receipt_digest: str
    cross_receipt_binding_passed: bool
    input_receipt_count: int
    composed_stage_count: int
    coordinator_result: S1WHCoordinatorResult
    in_memory_coordinator_call_count: int
    operating_system_probe_count: int
    filesystem_read_count: int
    filesystem_write_count: int
    execution_id_freshness_check_count: int
    authorization_instantiation_count: int
    producer_resolution_count: int
    producer_call_count: int
    matrix_path_count: int
    production_artifact_count: int
    result_digest: str

    def __post_init__(self) -> None:
        if (
            self.decision != S1WN_DECISION
            or self.cross_receipt_binding_passed is not True
            or self.input_receipt_count != 3
            or self.composed_stage_count != 6
            or not isinstance(self.coordinator_result, S1WHCoordinatorResult)
            or self.coordinator_result.next_stage != "H2_BLOCKED"
            or self.in_memory_coordinator_call_count != 1
            or any(
                value != 0
                for value in (
                    self.operating_system_probe_count,
                    self.filesystem_read_count,
                    self.filesystem_write_count,
                    self.execution_id_freshness_check_count,
                    self.authorization_instantiation_count,
                    self.producer_resolution_count,
                    self.producer_call_count,
                    self.matrix_path_count,
                    self.production_artifact_count,
                )
            )
            or self.result_digest != _digest(self.payload_without_digest())
        ):
            raise S1WNCompositionError(
                S1WN_INVALID_RECEIPT_CHAIN,
                "invalid private receipt composition result",
            )

    @property
    def ready_for_production_execution(self) -> bool:
        return False

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": S1WN_SCHEMA_VERSION,
            "mode": S1WN_MODE,
            "decision": self.decision,
            "root_receipt_digest": self.root_receipt_digest,
            "resource_receipt_digest": self.resource_receipt_digest,
            "authorization_validation_receipt_digest": (
                self.authorization_validation_receipt_digest
            ),
            "cross_receipt_binding_passed": self.cross_receipt_binding_passed,
            "input_receipt_count": self.input_receipt_count,
            "composed_stage_count": self.composed_stage_count,
            "coordinator_result": self.coordinator_result.canonical_payload(),
            "in_memory_coordinator_call_count": (
                self.in_memory_coordinator_call_count
            ),
            "operating_system_probe_count": self.operating_system_probe_count,
            "filesystem_read_count": self.filesystem_read_count,
            "filesystem_write_count": self.filesystem_write_count,
            "execution_id_freshness_check_count": (
                self.execution_id_freshness_check_count
            ),
            "authorization_instantiation_count": (
                self.authorization_instantiation_count
            ),
            "producer_resolution_count": self.producer_resolution_count,
            "producer_call_count": self.producer_call_count,
            "matrix_path_count": self.matrix_path_count,
            "production_artifact_count": self.production_artifact_count,
            "ready_for_production_execution": self.ready_for_production_execution,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "result_digest": self.result_digest,
        }


def compose_s1wn_in_memory_h0_h1(
    root_receipt: S1WJRootMirrorReceipt,
    resource_receipt: S1WJInjectedResourceReceipt,
    authorization_receipt: S1WLInjectedAuthorizationValidationReceipt,
) -> S1WNReceiptCompositionResult:
    """Compose existing private receipts without repeating their producers."""

    if (
        not isinstance(root_receipt, S1WJRootMirrorReceipt)
        or not isinstance(resource_receipt, S1WJInjectedResourceReceipt)
        or not isinstance(
            authorization_receipt,
            S1WLInjectedAuthorizationValidationReceipt,
        )
    ):
        raise S1WNCompositionError(
            S1WN_INVALID_RECEIPT_CHAIN,
            "three typed private input receipts are required",
        )
    chain_passed = (
        resource_receipt.root_receipt_digest == root_receipt.receipt_digest
        and authorization_receipt.resource_gate_digest
        == resource_receipt.gate.resource_gate_digest
        and root_receipt.same_volume
        and resource_receipt.gate.all_resource_gates_passed
        and authorization_receipt.injected_text_and_digests_match
    )
    if not chain_passed:
        raise S1WNCompositionError(
            S1WN_INVALID_RECEIPT_CHAIN,
            "input receipt digests or injected gates do not form one chain",
        )

    root_stage = S1WHInjectedStageAdapter(
        "s1wh.injected.root",
        "H0B",
        detail_role=f"S1WN_ROOT_{root_receipt.receipt_digest}",
    )
    resource_stage = S1WHInjectedStageAdapter(
        "s1wh.injected.resource",
        "H0C",
        detail_role=f"S1WN_RESOURCE_{resource_receipt.receipt_digest}",
    )
    authorization_stage = S1WHInjectedStageAdapter(
        "s1wh.injected.authorization",
        "H0D",
        detail_role=(
            "S1WN_AUTHORIZATION_TEXT_"
            f"{authorization_receipt.receipt_digest}"
        ),
    )
    lock_terminal = S1WGProductionLockTerminalAdapter(
        "s1wh.injected.lock",
        S1WHInjectedStageAdapter(
            "s1wh.injected.lock",
            "H0E",
            detail_role="S1WN_SYNTHETIC_PATHS_FREE_NO_WRITE",
        ),
        S1WHInjectedStageAdapter(
            "s1wh.injected.lock",
            "H1",
            detail_role="S1WN_SYNTHETIC_H1_NO_LOCK_NO_CONSUMPTION",
        ),
        production_filesystem_enabled=False,
    )
    coordinator = S1WGPrivateProductionCoordinator(
        S1WGProductionResourceObserverAdapter(
            "s1wh.injected.resource",
            resource_stage,
            production_observation_enabled=False,
        ),
        S1WGExactProductionAuthorizationActivator(
            "s1wh.injected.authorization",
            authorization_stage,
            production_authorization_enabled=False,
        ),
        lock_terminal,
        S1WGPrivateS1VQProducerResolver(
            "s1wh.injected.producer",
            resolution_enabled=False,
        ),
        S1WGProductionArtifactRootResolver(
            "s1wh.injected.root",
            root_stage,
            production_root_resolution_enabled=False,
        ),
    )
    coordinator_result = coordinator.run_injected_h0_h1()
    values = {
        "decision": S1WN_DECISION,
        "root_receipt_digest": root_receipt.receipt_digest,
        "resource_receipt_digest": resource_receipt.receipt_digest,
        "authorization_validation_receipt_digest": (
            authorization_receipt.receipt_digest
        ),
        "cross_receipt_binding_passed": True,
        "input_receipt_count": 3,
        "composed_stage_count": len(coordinator_result.receipts),
        "coordinator_result": coordinator_result,
        "in_memory_coordinator_call_count": 1,
        "operating_system_probe_count": 0,
        "filesystem_read_count": 0,
        "filesystem_write_count": 0,
        "execution_id_freshness_check_count": 0,
        "authorization_instantiation_count": 0,
        "producer_resolution_count": 0,
        "producer_call_count": 0,
        "matrix_path_count": 0,
        "production_artifact_count": 0,
    }
    payload = {
        "schema_version": S1WN_SCHEMA_VERSION,
        "mode": S1WN_MODE,
        **{
            key: (
                value.canonical_payload()
                if key == "coordinator_result"
                else value
            )
            for key, value in values.items()
        },
        "ready_for_production_execution": False,
    }
    return S1WNReceiptCompositionResult(
        **values,
        result_digest=_digest(payload),
    )


def execute_s1wn_production_once() -> None:
    raise S1WNCompositionError(
        S1WN_PRODUCTION_EXECUTION_BLOCKED,
        "S1-WN composes existing injected receipts only",
    )
