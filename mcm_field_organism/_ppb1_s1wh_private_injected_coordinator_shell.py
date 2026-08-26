"""Private S1-WH in-memory coordinator shell stopping before real H2."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re


S1WH_SCHEMA_VERSION = "ppb1.s1wh.private.injected-coordinator-shell.v1"
S1WH_CONTRACT_DIGEST = (
    "c220857ae7974ed4ad7aa60676dc66c67574cd3dc94cf879b26cf220ade3e84b"
)
S1WH_PARENT_PREFLIGHT_DIGEST = (
    "bdd1f9652ac2cd094d794c4a589a2eeae90ca5357f5ccf34863f1368e99c96af"
)
S1WH_MODE = "INJECTED_IN_MEMORY_TEST_ONLY"
S1WH_DECISION = "BLOCKED_BEFORE_H2_REAL_PRODUCER_RESOLUTION"
S1WH_INVALID_ROLE = "S1WH_INVALID_ROLE"
S1WH_STAGE_FAILED = "S1WH_STAGE_FAILED"
S1WH_PRODUCTION_EXECUTION_BLOCKED = "S1WH_PRODUCTION_EXECUTION_BLOCKED"

S1WH_H0_H1_ORDER = ("H0A", "H0B", "H0C", "H0D", "H0E", "H1")
S1WH_PRODUCTION_ROOT_ROLE = "CONTRACT_BOUND_BUT_UNRESOLVED"

_ADAPTER_ID = re.compile(r"^s1wh\.injected\.[a-z0-9][a-z0-9.-]{2,80}$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S1WHCoordinatorError(ValueError):
    """One fail-closed injected coordinator boundary violation."""

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


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


@dataclass(frozen=True, slots=True)
class S1WHInjectedStageReceipt:
    stage: str
    adapter_id: str
    passed: bool
    effect_count: int
    detail_digest: str
    receipt_digest: str

    def __post_init__(self) -> None:
        if (
            self.stage not in S1WH_H0_H1_ORDER
            or _ADAPTER_ID.fullmatch(self.adapter_id) is None
            or not isinstance(self.passed, bool)
            or self.effect_count != 0
            or not _valid_digest(self.detail_digest)
            or self.receipt_digest != _digest(self.payload_without_digest())
        ):
            raise S1WHCoordinatorError(
                S1WH_INVALID_ROLE,
                "invalid injected stage receipt",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": S1WH_SCHEMA_VERSION,
            "mode": S1WH_MODE,
            "stage": self.stage,
            "adapter_id": self.adapter_id,
            "passed": self.passed,
            "effect_count": self.effect_count,
            "detail_digest": self.detail_digest,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "receipt_digest": self.receipt_digest,
        }


def build_s1wh_injected_receipt(
    stage: str,
    adapter_id: str,
    *,
    passed: bool = True,
    detail_role: str = "SYNTHETIC_PASS",
) -> S1WHInjectedStageReceipt:
    if not isinstance(detail_role, str) or not detail_role:
        raise S1WHCoordinatorError(
            S1WH_INVALID_ROLE,
            "injected receipt detail role is invalid",
        )
    values = {
        "stage": stage,
        "adapter_id": adapter_id,
        "passed": passed,
        "effect_count": 0,
        "detail_digest": _digest(
            {
                "mode": S1WH_MODE,
                "stage": stage,
                "adapter_id": adapter_id,
                "detail_role": detail_role,
            }
        ),
    }
    payload = {
        "schema_version": S1WH_SCHEMA_VERSION,
        "mode": S1WH_MODE,
        **values,
    }
    return S1WHInjectedStageReceipt(
        **values,
        receipt_digest=_digest(payload),
    )


def _validate_adapter_id(adapter_id: object) -> None:
    if not isinstance(adapter_id, str) or _ADAPTER_ID.fullmatch(adapter_id) is None:
        raise S1WHCoordinatorError(
            S1WH_INVALID_ROLE,
            "invalid injected adapter id",
        )


@dataclass(frozen=True, slots=True)
class S1WHInjectedStageAdapter:
    adapter_id: str
    expected_stage: str
    passed: bool = True
    detail_role: str = "SYNTHETIC_PASS"

    def __post_init__(self) -> None:
        _validate_adapter_id(self.adapter_id)
        if (
            self.expected_stage not in S1WH_H0_H1_ORDER
            or not isinstance(self.passed, bool)
            or not isinstance(self.detail_role, str)
            or not self.detail_role
        ):
            raise S1WHCoordinatorError(
                S1WH_INVALID_ROLE,
                "invalid immutable injected stage adapter",
            )

    def __call__(self, stage: str) -> S1WHInjectedStageReceipt:
        if stage != self.expected_stage:
            raise S1WHCoordinatorError(
                S1WH_STAGE_FAILED,
                "immutable injected adapter received the wrong stage",
            )
        return build_s1wh_injected_receipt(
            stage,
            self.adapter_id,
            passed=self.passed,
            detail_role=self.detail_role,
        )


def _validate_adapter(adapter: object, expected_stage: str) -> None:
    if (
        not isinstance(adapter, S1WHInjectedStageAdapter)
        or adapter.expected_stage != expected_stage
    ):
        raise S1WHCoordinatorError(
            S1WH_INVALID_ROLE,
            "injected adapter has the wrong immutable stage role",
        )


@dataclass(frozen=True, slots=True)
class S1WGProductionResourceObserverAdapter:
    adapter_id: str
    observe: S1WHInjectedStageAdapter
    production_observation_enabled: bool = False

    def __post_init__(self) -> None:
        _validate_adapter_id(self.adapter_id)
        _validate_adapter(self.observe, "H0C")
        if self.observe.adapter_id != self.adapter_id:
            raise S1WHCoordinatorError(
                S1WH_INVALID_ROLE,
                "resource adapter ids do not match",
            )
        if self.production_observation_enabled is not False:
            raise S1WHCoordinatorError(
                S1WH_INVALID_ROLE,
                "production resource observation must remain disabled",
            )


@dataclass(frozen=True, slots=True)
class S1WGExactProductionAuthorizationActivator:
    adapter_id: str
    validate: S1WHInjectedStageAdapter
    production_authorization_enabled: bool = False

    def __post_init__(self) -> None:
        _validate_adapter_id(self.adapter_id)
        _validate_adapter(self.validate, "H0D")
        if self.validate.adapter_id != self.adapter_id:
            raise S1WHCoordinatorError(
                S1WH_INVALID_ROLE,
                "authorization adapter ids do not match",
            )
        if self.production_authorization_enabled is not False:
            raise S1WHCoordinatorError(
                S1WH_INVALID_ROLE,
                "production authorization must remain disabled",
            )


@dataclass(frozen=True, slots=True)
class S1WGProductionLockTerminalAdapter:
    adapter_id: str
    validate_paths: S1WHInjectedStageAdapter
    consume_injected_h1: S1WHInjectedStageAdapter
    production_filesystem_enabled: bool = False

    def __post_init__(self) -> None:
        _validate_adapter_id(self.adapter_id)
        _validate_adapter(self.validate_paths, "H0E")
        _validate_adapter(self.consume_injected_h1, "H1")
        if (
            self.validate_paths.adapter_id != self.adapter_id
            or self.consume_injected_h1.adapter_id != self.adapter_id
        ):
            raise S1WHCoordinatorError(
                S1WH_INVALID_ROLE,
                "lock adapter ids do not match",
            )
        if self.production_filesystem_enabled is not False:
            raise S1WHCoordinatorError(
                S1WH_INVALID_ROLE,
                "production lock and terminal writes must remain disabled",
            )


@dataclass(frozen=True, slots=True)
class S1WGPrivateS1VQProducerResolver:
    adapter_id: str
    resolution_enabled: bool = False

    def __post_init__(self) -> None:
        _validate_adapter_id(self.adapter_id)
        if self.resolution_enabled is not False:
            raise S1WHCoordinatorError(
                S1WH_INVALID_ROLE,
                "real producer resolution must remain disabled",
            )


@dataclass(frozen=True, slots=True)
class S1WGProductionArtifactRootResolver:
    adapter_id: str
    validate_contract_root: S1WHInjectedStageAdapter
    production_root_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        _validate_adapter_id(self.adapter_id)
        _validate_adapter(self.validate_contract_root, "H0B")
        if self.validate_contract_root.adapter_id != self.adapter_id:
            raise S1WHCoordinatorError(
                S1WH_INVALID_ROLE,
                "root adapter ids do not match",
            )
        if self.production_root_resolution_enabled is not False:
            raise S1WHCoordinatorError(
                S1WH_INVALID_ROLE,
                "production root resolution must remain disabled",
            )


@dataclass(frozen=True, slots=True)
class S1WHCoordinatorResult:
    decision: str
    receipts: tuple[S1WHInjectedStageReceipt, ...]
    next_stage: str
    production_root_role: str
    resource_probe_count: int
    filesystem_write_count: int
    authorization_instantiation_count: int
    producer_resolution_count: int
    producer_call_count: int
    matrix_path_count: int
    production_artifact_count: int
    result_digest: str

    def __post_init__(self) -> None:
        if (
            self.decision != S1WH_DECISION
            or tuple(receipt.stage for receipt in self.receipts) != S1WH_H0_H1_ORDER
            or any(not receipt.passed for receipt in self.receipts)
            or self.next_stage != "H2_BLOCKED"
            or self.production_root_role != S1WH_PRODUCTION_ROOT_ROLE
            or any(
                value != 0
                for value in (
                    self.resource_probe_count,
                    self.filesystem_write_count,
                    self.authorization_instantiation_count,
                    self.producer_resolution_count,
                    self.producer_call_count,
                    self.matrix_path_count,
                    self.production_artifact_count,
                )
            )
            or self.result_digest != _digest(self.payload_without_digest())
        ):
            raise S1WHCoordinatorError(
                S1WH_INVALID_ROLE,
                "invalid injected coordinator result",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": S1WH_SCHEMA_VERSION,
            "mode": S1WH_MODE,
            "contract_digest": S1WH_CONTRACT_DIGEST,
            "parent_preflight_digest": S1WH_PARENT_PREFLIGHT_DIGEST,
            "decision": self.decision,
            "receipts": [receipt.canonical_payload() for receipt in self.receipts],
            "next_stage": self.next_stage,
            "production_root_role": self.production_root_role,
            "resource_probe_count": self.resource_probe_count,
            "filesystem_write_count": self.filesystem_write_count,
            "authorization_instantiation_count": (
                self.authorization_instantiation_count
            ),
            "producer_resolution_count": self.producer_resolution_count,
            "producer_call_count": self.producer_call_count,
            "matrix_path_count": self.matrix_path_count,
            "production_artifact_count": self.production_artifact_count,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "result_digest": self.result_digest,
        }


class S1WGPrivateProductionCoordinator:
    """Evaluate injected H0-H1 adapters and stop before producer resolution."""

    __slots__ = (
        "_resource",
        "_authorization",
        "_lock_terminal",
        "_producer",
        "_artifact_root",
    )

    def __init__(
        self,
        resource: S1WGProductionResourceObserverAdapter,
        authorization: S1WGExactProductionAuthorizationActivator,
        lock_terminal: S1WGProductionLockTerminalAdapter,
        producer: S1WGPrivateS1VQProducerResolver,
        artifact_root: S1WGProductionArtifactRootResolver,
    ) -> None:
        roles = (
            (resource, S1WGProductionResourceObserverAdapter),
            (authorization, S1WGExactProductionAuthorizationActivator),
            (lock_terminal, S1WGProductionLockTerminalAdapter),
            (producer, S1WGPrivateS1VQProducerResolver),
            (artifact_root, S1WGProductionArtifactRootResolver),
        )
        if any(not isinstance(value, expected) for value, expected in roles):
            raise S1WHCoordinatorError(
                S1WH_INVALID_ROLE,
                "coordinator role set is incomplete",
            )
        self._resource = resource
        self._authorization = authorization
        self._lock_terminal = lock_terminal
        self._producer = producer
        self._artifact_root = artifact_root

    @staticmethod
    def _accept(
        receipt: object,
        stage: str,
        adapter_id: str,
    ) -> S1WHInjectedStageReceipt:
        if (
            not isinstance(receipt, S1WHInjectedStageReceipt)
            or receipt.stage != stage
            or receipt.adapter_id != adapter_id
            or not receipt.passed
            or receipt.effect_count != 0
        ):
            raise S1WHCoordinatorError(
                S1WH_STAGE_FAILED,
                f"injected stage {stage} failed closed",
            )
        return receipt

    def run_injected_h0_h1(self) -> S1WHCoordinatorResult:
        receipts = [
            build_s1wh_injected_receipt(
                "H0A",
                "s1wh.injected.contract-validator",
                detail_role="STATIC_CONTRACT_PLAN_SOURCE_PASS",
            )
        ]
        steps = (
            (
                "H0B",
                self._artifact_root.adapter_id,
                self._artifact_root.validate_contract_root,
            ),
            ("H0C", self._resource.adapter_id, self._resource.observe),
            ("H0D", self._authorization.adapter_id, self._authorization.validate),
            (
                "H0E",
                self._lock_terminal.adapter_id,
                self._lock_terminal.validate_paths,
            ),
            (
                "H1",
                self._lock_terminal.adapter_id,
                self._lock_terminal.consume_injected_h1,
            ),
        )
        for stage, adapter_id, adapter in steps:
            try:
                receipt = adapter(stage)
            except Exception as exc:
                raise S1WHCoordinatorError(
                    S1WH_STAGE_FAILED,
                    f"injected stage {stage} raised {type(exc).__name__}",
                ) from exc
            receipts.append(self._accept(receipt, stage, adapter_id))

        values = {
            "decision": S1WH_DECISION,
            "receipts": tuple(receipts),
            "next_stage": "H2_BLOCKED",
            "production_root_role": S1WH_PRODUCTION_ROOT_ROLE,
            "resource_probe_count": 0,
            "filesystem_write_count": 0,
            "authorization_instantiation_count": 0,
            "producer_resolution_count": 0,
            "producer_call_count": 0,
            "matrix_path_count": 0,
            "production_artifact_count": 0,
        }
        payload = {
            "schema_version": S1WH_SCHEMA_VERSION,
            "mode": S1WH_MODE,
            "contract_digest": S1WH_CONTRACT_DIGEST,
            "parent_preflight_digest": S1WH_PARENT_PREFLIGHT_DIGEST,
            **{
                key: (
                    [receipt.canonical_payload() for receipt in value]
                    if key == "receipts"
                    else value
                )
                for key, value in values.items()
            },
        }
        return S1WHCoordinatorResult(
            **values,
            result_digest=_digest(payload),
        )


def execute_s1wh_production_once() -> None:
    raise S1WHCoordinatorError(
        S1WH_PRODUCTION_EXECUTION_BLOCKED,
        "S1-WH stops before real root authorization producer and H2",
    )
