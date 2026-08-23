"""Static S1-WK preflight for private S1-WJ root/resource adapters."""

from __future__ import annotations

import ast
from dataclasses import dataclass, fields
import hashlib
import json
from pathlib import Path

from . import _ppb1_s1wj_injected_root_resource_adapters as s1wj


S1WK_SCHEMA_VERSION = "ppb1.s1wk.static.root-resource-preflight.v1"
S1WK_CONTRACT_DIGEST = (
    "c220857ae7974ed4ad7aa60676dc66c67574cd3dc94cf879b26cf220ade3e84b"
)
S1WK_S1WJ_SOURCE_DIGEST = (
    "60cbacf603e2a8d5235fbd3d52bd21fa466a353b9404eb11479926d461c556af"
)
S1WK_DECISION = "BLOCKED_INJECTED_ROOT_RESOURCE_VALID_PRODUCTION_ACCESS_MISSING"
S1WK_BLOCKERS = (
    "PRODUCTION_RESOURCE_OBSERVER_NOT_WIRED",
    "PRODUCTION_AUTHORIZATION_INSTANTIATION_LOCKED",
    "PRODUCTION_LOCK_TERMINAL_WRITERS_NOT_WIRED",
    "PRIVATE_REAL_PRODUCER_NOT_BOUND",
    "PRODUCTION_ARTIFACT_PATH_NOT_WIRED",
    "PRODUCTION_ENTRYPOINT_HARD_BLOCKED",
)
S1WK_PREFLIGHT_DRIFT = "S1WK_PREFLIGHT_DRIFT"

_ROOT_FIELDS = {
    "declared_production_relative_root",
    "mirror_root_digest",
    "artifact_volume_identity",
    "temporary_volume_identity",
    "same_volume",
    "mirror_only",
    "production_root_accessed",
    "filesystem_write_count",
    "production_artifact_count",
    "receipt_digest",
}
_RESOURCE_FIELDS = {
    "root_receipt_digest",
    "observation",
    "gate",
    "injected_value_count",
    "operating_system_probe_count",
    "filesystem_write_count",
    "production_root_access_count",
    "production_artifact_count",
    "receipt_digest",
}
_REQUIRED_RESOURCE_PARAMETERS = (
    "root_receipt",
    "available_physical_memory_bytes",
    "artifact_volume_free_bytes",
    "atomic_replace_probe_passed",
    "artifact_paths_free",
)


class S1WKPreflightError(ValueError):
    """One fail-closed static S1-WJ inventory violation."""

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


def _calls(function: ast.FunctionDef | None) -> set[str]:
    if function is None:
        return set()
    result = set()
    for node in ast.walk(function):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            result.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            result.add(node.func.attr)
    return result


def _attributes(function: ast.FunctionDef | None) -> set[str]:
    if function is None:
        return set()
    return {
        node.attr for node in ast.walk(function) if isinstance(node, ast.Attribute)
    }


def _imports(tree: ast.Module) -> set[str]:
    result = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            result.update(alias.name for alias in node.names)
    return result


def _json_digest(path: Path) -> str:
    return _digest(json.loads(path.read_text(encoding="utf-8")))


@dataclass(frozen=True, slots=True)
class S1WKPreflightResult:
    decision: str
    contract_digest: str
    s1wj_source_digest: str
    checks: tuple[tuple[str, bool], ...]
    blockers: tuple[str, ...]
    source_read_count: int
    contract_read_count: int
    root_adapter_call_count: int
    resource_adapter_call_count: int
    coordinator_call_count: int
    operating_system_probe_count: int
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
            "schema_version": S1WK_SCHEMA_VERSION,
            "decision": self.decision,
            "contract_digest": self.contract_digest,
            "s1wj_source_digest": self.s1wj_source_digest,
            "checks": [
                {"role": role, "passed": passed}
                for role, passed in self.checks
            ],
            "blockers": list(self.blockers),
            "source_read_count": self.source_read_count,
            "contract_read_count": self.contract_read_count,
            "root_adapter_call_count": self.root_adapter_call_count,
            "resource_adapter_call_count": self.resource_adapter_call_count,
            "coordinator_call_count": self.coordinator_call_count,
            "operating_system_probe_count": self.operating_system_probe_count,
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


def run_s1wk_static_preflight() -> S1WKPreflightResult:
    """Inspect S1-WJ without executing any root or resource adapter."""

    root = Path(__file__).resolve().parents[1]
    contract_path = (
        root
        / "docs"
        / "S1WG_PPB1_PRODUKTIONSINTEGRATIONSDELTA_VERTRAG_V1.json"
    )
    source = _source(s1wj)
    tree = ast.parse(source)
    root_resolver = _function(tree, "resolve_s1wj_injected_root_mirror")
    resource_observer = _function(tree, "observe_s1wj_injected_resources")
    h0b_builder = _function(tree, "build_s1wj_h0b_adapter")
    h0c_builder = _function(tree, "build_s1wj_h0c_adapter")
    entry = _function(tree, "execute_s1wj_production_once")

    required_parameters = (
        tuple(argument.arg for argument in resource_observer.args.args)
        if resource_observer is not None
        else ()
    )
    root_structure_complete = (
        _ROOT_FIELDS == {item.name for item in fields(s1wj.S1WJRootMirrorReceipt)}
        and s1wj.S1WJ_PRODUCTION_RELATIVE_ROOT
        == "data/generated/ppb1/one_shot"
        and s1wj.S1WJ_MIRROR_ROOT_NAME == "s1wj-production-root-mirror"
        and {"absolute", "resolve", "is_dir"}.issubset(_calls(root_resolver))
        and "write_text" not in _calls(root_resolver)
        and "write_bytes" not in _calls(root_resolver)
        and "open" not in _calls(root_resolver)
    )
    resource_structure_complete = (
        _RESOURCE_FIELDS
        == {item.name for item in fields(s1wj.S1WJInjectedResourceReceipt)}
        and required_parameters == _REQUIRED_RESOURCE_PARAMETERS
        and not resource_observer.args.defaults
        and {
            "build_s1wb_injected_observation",
            "evaluate_s1wb_resource_gate",
        }.issubset(_calls(resource_observer))
    )
    h0_bridge_complete = (
        "same_volume" in _attributes(h0b_builder)
        and {"gate", "all_resource_gates_passed"}.issubset(
            _attributes(h0c_builder)
        )
        and "S1WHInjectedStageAdapter" in _calls(h0b_builder)
        and "S1WHInjectedStageAdapter" in _calls(h0c_builder)
    )
    runtime_imports_absent = {
        "os",
        "ctypes",
        "shutil",
        "platform",
    }.isdisjoint(_imports(tree))
    runtime_calls_absent = {
        "disk_usage",
        "_available_physical_memory",
        "open",
        "write_text",
        "write_bytes",
        "replace",
        "rename",
        "link",
        "_execute_s1vq_corrected_matrix",
    }.isdisjoint(
        {
            call
            for function in tree.body
            if isinstance(function, ast.FunctionDef)
            for call in _calls(function)
        }
    )
    entry_blocked = _only_raises(entry)

    checks = (
        (
            "S1WG_CONTRACT_DIGEST_VALID",
            _json_digest(contract_path) == S1WK_CONTRACT_DIGEST,
        ),
        (
            "S1WJ_SOURCE_DIGEST_BOUND",
            _source_digest(s1wj) == S1WK_S1WJ_SOURCE_DIGEST,
        ),
        ("ROOT_MIRROR_RECEIPT_AND_BOUNDARY_COMPLETE", root_structure_complete),
        ("RESOURCE_RECEIPT_AND_FOUR_INJECTIONS_COMPLETE", resource_structure_complete),
        ("H0B_H0C_BRIDGE_STATICALLY_COMPLETE", h0_bridge_complete),
        ("OS_RESOURCE_AND_WRITE_IMPORTS_ABSENT", runtime_imports_absent),
        ("OS_RESOURCE_AND_WRITE_CALLS_ABSENT", runtime_calls_absent),
        ("PRODUCTION_ENTRY_HARD_BLOCKED", entry_blocked),
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
        raise S1WKPreflightError(
            S1WK_PREFLIGHT_DRIFT,
            "S1-WJ structure no longer matches the bound static boundary",
        )

    return S1WKPreflightResult(
        S1WK_DECISION,
        S1WK_CONTRACT_DIGEST,
        S1WK_S1WJ_SOURCE_DIGEST,
        checks,
        S1WK_BLOCKERS,
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
        0,
        0,
    )
