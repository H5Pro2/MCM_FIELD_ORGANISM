"""Static S1-WI preflight for the private S1-WH coordinator shell."""

from __future__ import annotations

import ast
from dataclasses import dataclass, fields
import hashlib
import json
from pathlib import Path

from . import _ppb1_s1wh_private_injected_coordinator_shell as s1wh


S1WI_SCHEMA_VERSION = "ppb1.s1wi.static.coordinator-preflight.v1"
S1WI_CONTRACT_DIGEST = (
    "c220857ae7974ed4ad7aa60676dc66c67574cd3dc94cf879b26cf220ade3e84b"
)
S1WI_PARENT_PREFLIGHT_DIGEST = (
    "bdd1f9652ac2cd094d794c4a589a2eeae90ca5357f5ccf34863f1368e99c96af"
)
S1WI_S1WH_SOURCE_DIGEST = (
    "7a054f7acb3c9ee8bb695013d53caae4a0a06397e2136e354df6dc68ebc6ffe3"
)
S1WI_DECISION = "BLOCKED_IN_MEMORY_COORDINATOR_VALID_PRODUCTION_INTEGRATION_MISSING"
S1WI_BLOCKERS = (
    "PRODUCTION_RESOURCE_OBSERVER_NOT_WIRED",
    "PRODUCTION_AUTHORIZATION_INSTANTIATION_LOCKED",
    "PRODUCTION_LOCK_TERMINAL_WRITERS_NOT_WIRED",
    "PRIVATE_REAL_PRODUCER_NOT_BOUND",
    "PRODUCTION_ARTIFACT_PATH_NOT_WIRED",
    "PRODUCTION_ENTRYPOINT_HARD_BLOCKED",
)
S1WI_PREFLIGHT_DRIFT = "S1WI_PREFLIGHT_DRIFT"

_ROLE_CLASS_NAMES = {
    "S1WGProductionResourceObserverAdapter",
    "S1WGExactProductionAuthorizationActivator",
    "S1WGProductionLockTerminalAdapter",
    "S1WGPrivateS1VQProducerResolver",
    "S1WGProductionArtifactRootResolver",
    "S1WGPrivateProductionCoordinator",
}
_PRODUCER_FIELDS = {"adapter_id", "resolution_enabled"}
_RESULT_FIELDS = {
    "decision",
    "receipts",
    "next_stage",
    "production_root_role",
    "resource_probe_count",
    "filesystem_write_count",
    "authorization_instantiation_count",
    "producer_resolution_count",
    "producer_call_count",
    "matrix_path_count",
    "production_artifact_count",
    "result_digest",
}
_ZERO_COUNTER_NAMES = (
    "resource_probe_count",
    "filesystem_write_count",
    "authorization_instantiation_count",
    "producer_resolution_count",
    "producer_call_count",
    "matrix_path_count",
    "production_artifact_count",
)


class S1WIPreflightError(ValueError):
    """One fail-closed static coordinator inventory violation."""

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


def _source(module: object) -> str:
    return Path(module.__file__).read_text(encoding="utf-8")


def _source_digest(module: object) -> str:
    return hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()


def _class(tree: ast.Module, name: str) -> ast.ClassDef | None:
    return next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == name
        ),
        None,
    )


def _method(class_node: ast.ClassDef | None, name: str) -> ast.FunctionDef | None:
    if class_node is None:
        return None
    return next(
        (
            node
            for node in class_node.body
            if isinstance(node, ast.FunctionDef) and node.name == name
        ),
        None,
    )


def _function(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    return next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == name
        ),
        None,
    )


def _only_raises(function: ast.FunctionDef | None) -> bool:
    if function is None:
        return False
    executable = [
        node
        for node in function.body
        if not (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        )
    ]
    return len(executable) == 1 and isinstance(executable[0], ast.Raise)


def _string_constants(node: ast.AST | None) -> set[str]:
    if node is None:
        return set()
    return {
        child.value
        for child in ast.walk(node)
        if isinstance(child, ast.Constant) and isinstance(child.value, str)
    }


def _attribute_names(node: ast.AST | None) -> set[str]:
    if node is None:
        return set()
    return {
        child.attr
        for child in ast.walk(node)
        if isinstance(child, ast.Attribute)
    }


def _assigned_zero_names(function: ast.FunctionDef | None) -> set[str]:
    if function is None:
        return set()
    result = set()
    for node in ast.walk(function):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values, strict=True):
            if (
                isinstance(key, ast.Constant)
                and isinstance(key.value, str)
                and isinstance(value, ast.Constant)
                and value.value == 0
            ):
                result.add(key.value)
    return result


def _json_digest(path: Path) -> str:
    return _digest(json.loads(path.read_text(encoding="utf-8")))


@dataclass(frozen=True, slots=True)
class S1WIPreflightResult:
    decision: str
    contract_digest: str
    parent_preflight_digest: str
    s1wh_source_digest: str
    checks: tuple[tuple[str, bool], ...]
    blockers: tuple[str, ...]
    source_read_count: int
    contract_read_count: int
    coordinator_call_count: int
    resource_probe_count: int
    filesystem_write_count: int
    authorization_instantiation_count: int
    producer_resolution_count: int
    producer_call_count: int
    matrix_path_count: int
    production_artifact_count: int

    @property
    def ready_for_production_execution(self) -> bool:
        return not self.blockers and all(passed for _, passed in self.checks)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": S1WI_SCHEMA_VERSION,
            "decision": self.decision,
            "contract_digest": self.contract_digest,
            "parent_preflight_digest": self.parent_preflight_digest,
            "s1wh_source_digest": self.s1wh_source_digest,
            "checks": [
                {"role": role, "passed": passed}
                for role, passed in self.checks
            ],
            "blockers": list(self.blockers),
            "source_read_count": self.source_read_count,
            "contract_read_count": self.contract_read_count,
            "coordinator_call_count": self.coordinator_call_count,
            "resource_probe_count": self.resource_probe_count,
            "filesystem_write_count": self.filesystem_write_count,
            "authorization_instantiation_count": (
                self.authorization_instantiation_count
            ),
            "producer_resolution_count": self.producer_resolution_count,
            "producer_call_count": self.producer_call_count,
            "matrix_path_count": self.matrix_path_count,
            "production_artifact_count": self.production_artifact_count,
            "ready_for_production_execution": self.ready_for_production_execution,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def run_s1wi_static_preflight() -> S1WIPreflightResult:
    """Read source and contract only; never execute the coordinator shell."""

    root = Path(__file__).resolve().parents[1]
    contract_path = (
        root
        / "docs"
        / "S1WG_PPB1_PRODUKTIONSINTEGRATIONSDELTA_VERTRAG_V1.json"
    )
    source = _source(s1wh)
    tree = ast.parse(source)
    class_names = {
        node.name for node in tree.body if isinstance(node, ast.ClassDef)
    }
    coordinator_class = _class(tree, "S1WGPrivateProductionCoordinator")
    run_method = _method(coordinator_class, "run_injected_h0_h1")
    producer_class = _class(tree, "S1WGPrivateS1VQProducerResolver")
    entry = _function(tree, "execute_s1wh_production_once")
    run_constants = _string_constants(run_method)
    run_attributes = _attribute_names(run_method)

    immutable_adapter_complete = (
        s1wh.S1WHInjectedStageAdapter.__dataclass_params__.frozen
        and "__slots__" in vars(s1wh.S1WHInjectedStageAdapter)
        and {"adapter_id", "expected_stage", "passed", "detail_role"}
        == {item.name for item in fields(s1wh.S1WHInjectedStageAdapter)}
        and "Callable" not in source
        and "from typing" not in source
    )
    role_types_complete = (
        _ROLE_CLASS_NAMES.issubset(class_names)
        and _RESULT_FIELDS
        == {item.name for item in fields(s1wh.S1WHCoordinatorResult)}
    )
    producer_resolver_noncallable = (
        producer_class is not None
        and _PRODUCER_FIELDS
        == {item.name for item in fields(s1wh.S1WGPrivateS1VQProducerResolver)}
        and "resolve" not in {
            node.name
            for node in producer_class.body
            if isinstance(node, ast.FunctionDef)
        }
        and "resolve" not in run_attributes
        and "_producer" not in run_attributes
    )
    h0_h1_order_bound = (
        set(s1wh.S1WH_H0_H1_ORDER).issubset(run_constants)
        and "H2_BLOCKED" in run_constants
        and "receipts" in run_constants
        and "next_stage" in run_constants
    )
    zero_effects_bound = set(_ZERO_COUNTER_NAMES).issubset(
        _assigned_zero_names(run_method)
    )
    runtime_imports_absent = all(
        forbidden not in source
        for forbidden in (
            "import os",
            "from pathlib",
            "from tempfile",
            "import ctypes",
            "import shutil",
            "S1WAProductionAuthorization",
            "_execute_s1vq_corrected_matrix",
            "SharedMCMField",
            "ReceptorContactFrame",
        )
    )
    entry_blocked = _only_raises(entry)

    checks = (
        (
            "S1WG_CONTRACT_DIGEST_VALID",
            _json_digest(contract_path) == S1WI_CONTRACT_DIGEST,
        ),
        (
            "S1WH_SOURCE_DIGEST_BOUND",
            _source_digest(s1wh) == S1WI_S1WH_SOURCE_DIGEST,
        ),
        ("SIX_PRIVATE_INTEGRATION_ROLE_TYPES_COMPLETE", role_types_complete),
        ("IMMUTABLE_IN_MEMORY_ADAPTER_COMPLETE", immutable_adapter_complete),
        ("PRODUCER_RESOLVER_STRUCTURALLY_NONCALLABLE", producer_resolver_noncallable),
        ("H0A_TO_H1_AND_H2_BLOCK_STATICALLY_BOUND", h0_h1_order_bound),
        ("SEVEN_ZERO_EFFECT_COUNTERS_BOUND", zero_effects_bound),
        ("RUNTIME_IMPORTS_ABSENT_AND_ENTRY_BLOCKED", runtime_imports_absent and entry_blocked),
        ("PRODUCTION_RESOURCE_OBSERVER_WIRED", False),
        ("PRODUCTION_AUTHORIZATION_UNLOCKED", False),
        ("PRODUCTION_LOCK_TERMINAL_WRITERS_WIRED", False),
        ("PRIVATE_REAL_PRODUCER_BOUND", False),
        ("PRODUCTION_ARTIFACT_PATH_WIRED", False),
        ("PRODUCTION_ENTRYPOINT_OPEN", False),
    )
    expected_failed = (
        "PRODUCTION_RESOURCE_OBSERVER_WIRED",
        "PRODUCTION_AUTHORIZATION_UNLOCKED",
        "PRODUCTION_LOCK_TERMINAL_WRITERS_WIRED",
        "PRIVATE_REAL_PRODUCER_BOUND",
        "PRODUCTION_ARTIFACT_PATH_WIRED",
        "PRODUCTION_ENTRYPOINT_OPEN",
    )
    failed = tuple(role for role, passed in checks if not passed)
    if failed != expected_failed:
        raise S1WIPreflightError(
            S1WI_PREFLIGHT_DRIFT,
            "S1-WH structure no longer matches the bound static boundary",
        )

    return S1WIPreflightResult(
        S1WI_DECISION,
        S1WI_CONTRACT_DIGEST,
        S1WI_PARENT_PREFLIGHT_DIGEST,
        S1WI_S1WH_SOURCE_DIGEST,
        checks,
        S1WI_BLOCKERS,
        1,
        1,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    )
