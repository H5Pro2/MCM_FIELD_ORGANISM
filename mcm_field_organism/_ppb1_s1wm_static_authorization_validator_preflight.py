"""Static S1-WM preflight for the private S1-WL text validator."""

from __future__ import annotations

import ast
from dataclasses import dataclass, fields
import hashlib
import json
from pathlib import Path

from . import _ppb1_s1wl_private_authorization_validator_adapter as s1wl


S1WM_SCHEMA_VERSION = "ppb1.s1wm.static.authorization-validator-preflight.v1"
S1WM_CONTRACT_DIGEST = (
    "c220857ae7974ed4ad7aa60676dc66c67574cd3dc94cf879b26cf220ade3e84b"
)
S1WM_S1WL_SOURCE_DIGEST = (
    "a61d4bfe66e2195f24f022c95b8d70c7aa5909dec94e0815f67351215718e857"
)
S1WM_DECISION = (
    "BLOCKED_INJECTED_AUTHORIZATION_VALIDATOR_VALID_"
    "PRODUCTION_AUTHORIZATION_MISSING"
)
S1WM_BLOCKERS = (
    "PRODUCTION_RESOURCE_OBSERVER_NOT_WIRED",
    "PRODUCTION_AUTHORIZATION_INSTANTIATION_LOCKED",
    "PRODUCTION_LOCK_TERMINAL_WRITERS_NOT_WIRED",
    "PRIVATE_REAL_PRODUCER_NOT_BOUND",
    "PRODUCTION_ARTIFACT_PATH_NOT_WIRED",
    "PRODUCTION_ENTRYPOINT_HARD_BLOCKED",
)
S1WM_PREFLIGHT_DRIFT = "S1WM_PREFLIGHT_DRIFT"

_RECEIPT_FIELDS = {
    "execution_id",
    "rendered_authorization_text_digest",
    "contract_digest",
    "calibration_digest",
    "resource_gate_digest",
    "parent_plan_digest",
    "corrected_plan_digest",
    "case_count",
    "maximum_registered_call_count",
    "production_entrypoint_id",
    "execution_id_format_valid",
    "exact_text_match",
    "digest_roles_match",
    "production_authorization_instantiated",
    "execution_id_freshness_check_count",
    "authorization_instantiation_count",
    "filesystem_read_count",
    "filesystem_write_count",
    "producer_resolution_count",
    "producer_call_count",
    "matrix_path_count",
    "production_artifact_count",
    "receipt_digest",
}
_ZERO_ROLE_FIELDS = {
    "execution_id_freshness_check_count",
    "authorization_instantiation_count",
    "filesystem_read_count",
    "filesystem_write_count",
    "producer_resolution_count",
    "producer_call_count",
    "matrix_path_count",
    "production_artifact_count",
}


class S1WMPreflightError(ValueError):
    """One fail-closed static S1-WL inventory violation."""

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


def _json_digest(path: Path) -> str:
    return _digest(json.loads(path.read_text(encoding="utf-8")))


def _function(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    return next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == name
        ),
        None,
    )


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


def _only_returns_false(function: ast.FunctionDef | None) -> bool:
    if function is None:
        return False
    return (
        len(function.body) == 1
        and isinstance(function.body[0], ast.Return)
        and isinstance(function.body[0].value, ast.Constant)
        and function.body[0].value.value is False
    )


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


def _names(function: ast.FunctionDef | None) -> set[str]:
    if function is None:
        return set()
    return {
        node.id for node in ast.walk(function) if isinstance(node, ast.Name)
    }


def _imports(tree: ast.Module) -> set[str]:
    result = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            result.update(alias.name for alias in node.names)
    return result


def _has_name_equality(
    function: ast.FunctionDef | None,
    left: str,
    right: str,
) -> bool:
    if function is None:
        return False
    for node in ast.walk(function):
        if not isinstance(node, ast.Compare) or len(node.ops) != 1:
            continue
        if not isinstance(node.ops[0], ast.Eq) or len(node.comparators) != 1:
            continue
        first = node.left
        second = node.comparators[0]
        if (
            isinstance(first, ast.Name)
            and isinstance(second, ast.Name)
            and {first.id, second.id} == {left, right}
        ):
            return True
    return False


def _literal_dict_values(function: ast.FunctionDef | None) -> dict[str, object]:
    result: dict[str, object] = {}
    if function is None:
        return result
    for node in ast.walk(function):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values, strict=True):
            if (
                isinstance(key, ast.Constant)
                and isinstance(key.value, str)
                and isinstance(value, ast.Constant)
            ):
                result[key.value] = value.value
    return result


@dataclass(frozen=True, slots=True)
class S1WMPreflightResult:
    decision: str
    contract_digest: str
    s1wl_source_digest: str
    checks: tuple[tuple[str, bool], ...]
    blockers: tuple[str, ...]
    source_read_count: int
    contract_read_count: int
    validator_call_count: int
    h0d_adapter_call_count: int
    coordinator_call_count: int
    operating_system_probe_count: int
    execution_id_freshness_check_count: int
    authorization_instantiation_count: int
    filesystem_write_count: int
    producer_resolution_count: int
    producer_call_count: int
    matrix_path_count: int
    production_artifact_count: int

    @property
    def ready_for_production_execution(self) -> bool:
        return not self.blockers and all(passed for _, passed in self.checks)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": S1WM_SCHEMA_VERSION,
            "decision": self.decision,
            "contract_digest": self.contract_digest,
            "s1wl_source_digest": self.s1wl_source_digest,
            "checks": [
                {"role": role, "passed": passed}
                for role, passed in self.checks
            ],
            "blockers": list(self.blockers),
            "source_read_count": self.source_read_count,
            "contract_read_count": self.contract_read_count,
            "validator_call_count": self.validator_call_count,
            "h0d_adapter_call_count": self.h0d_adapter_call_count,
            "coordinator_call_count": self.coordinator_call_count,
            "operating_system_probe_count": self.operating_system_probe_count,
            "execution_id_freshness_check_count": (
                self.execution_id_freshness_check_count
            ),
            "authorization_instantiation_count": (
                self.authorization_instantiation_count
            ),
            "filesystem_write_count": self.filesystem_write_count,
            "producer_resolution_count": self.producer_resolution_count,
            "producer_call_count": self.producer_call_count,
            "matrix_path_count": self.matrix_path_count,
            "production_artifact_count": self.production_artifact_count,
            "ready_for_production_execution": self.ready_for_production_execution,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def run_s1wm_static_preflight() -> S1WMPreflightResult:
    """Inspect S1-WL without executing its validator or H0D adapter."""

    root = Path(__file__).resolve().parents[1]
    contract_path = (
        root
        / "docs"
        / "S1WG_PPB1_PRODUKTIONSINTEGRATIONSDELTA_VERTRAG_V1.json"
    )
    source = _source(s1wl)
    tree = ast.parse(source)
    receipt_class = _class(
        tree,
        "S1WLInjectedAuthorizationValidationReceipt",
    )
    validator = _function(tree, "validate_s1wl_injected_authorization_text")
    h0d_builder = _function(tree, "build_s1wl_injected_h0d_adapter")
    entry = _function(tree, "execute_s1wl_production_once")
    ready_property = _method(
        receipt_class,
        "ready_for_production_authorization",
    )

    validator_parameters = (
        tuple(argument.arg for argument in validator.args.args)
        if validator is not None
        else ()
    )
    validator_keyword_parameters = (
        tuple(argument.arg for argument in validator.args.kwonlyargs)
        if validator is not None
        else ()
    )
    literal_values = _literal_dict_values(validator)
    receipt_complete = (
        _RECEIPT_FIELDS
        == {
            item.name
            for item in fields(s1wl.S1WLInjectedAuthorizationValidationReceipt)
        }
        and "rendered_authorization_text" not in _RECEIPT_FIELDS
        and "rendered_authorization_text_digest" in _RECEIPT_FIELDS
    )
    validator_complete = (
        validator_parameters
        == (
            "rendered_authorization_text",
            "execution_id",
            "resource_gate_digest",
        )
        and validator_keyword_parameters
        == (
            "contract_digest",
            "calibration_digest",
            "parent_plan_digest",
            "corrected_plan_digest",
        )
        and {
            "S1WB_AUTHORIZATION_TEMPLATE",
            "S1WB_CONTRACT_DIGEST",
            "S1WB_CALIBRATION_DIGEST",
            "S1WB_PARENT_PLAN_DIGEST",
            "S1WB_CORRECTED_PLAN_DIGEST",
        }.issubset(_names(validator))
        and {"format", "_text_digest", "fullmatch"}.issubset(
            _calls(validator)
        )
        and _has_name_equality(
            validator,
            "rendered_authorization_text",
            "expected_text",
        )
    )
    h0d_bridge_complete = (
        {
            "S1WHInjectedStageAdapter",
            "S1WGExactProductionAuthorizationActivator",
        }.issubset(_calls(h0d_builder))
        and "injected_text_and_digests_match" in source
        and "production_authorization_enabled=False" in source
    )
    zero_roles_complete = all(
        literal_values.get(role) == 0 for role in _ZERO_ROLE_FIELDS
    )
    authorization_remains_blocked = (
        "S1WAProductionAuthorization" not in _imports(tree)
        and "S1WAProductionAuthorization" not in _calls(validator)
        and "S1WAProductionAuthorization" not in _calls(h0d_builder)
        and _only_returns_false(ready_property)
    )
    runtime_imports_absent = {
        "os",
        "ctypes",
        "shutil",
        "tempfile",
        "pathlib",
    }.isdisjoint(_imports(tree))
    runtime_calls_absent = {
        "open",
        "read_text",
        "read_bytes",
        "write_text",
        "write_bytes",
        "replace",
        "rename",
        "disk_usage",
        "run_injected_h0_h1",
        "_execute_s1vq_corrected_matrix",
    }.isdisjoint(
        {
            call
            for function in tree.body
            if isinstance(function, ast.FunctionDef)
            for call in _calls(function)
        }
    )

    checks = (
        (
            "S1WG_CONTRACT_DIGEST_VALID",
            _json_digest(contract_path) == S1WM_CONTRACT_DIGEST,
        ),
        (
            "S1WL_SOURCE_DIGEST_BOUND",
            _source_digest(s1wl) == S1WM_S1WL_SOURCE_DIGEST,
        ),
        ("RECEIPT_FIELDS_COMPLETE_RAW_TEXT_ABSENT", receipt_complete),
        ("EXACT_TEXT_AND_DIGEST_BINDING_COMPLETE", validator_complete),
        ("SYNTHETIC_H0D_BRIDGE_COMPLETE", h0d_bridge_complete),
        ("EIGHT_ZERO_EFFECT_ROLES_BOUND", zero_roles_complete),
        (
            "PRODUCTION_AUTHORIZATION_TYPE_UNREACHABLE",
            authorization_remains_blocked,
        ),
        (
            "RUNTIME_IMPORTS_CALLS_ABSENT_ENTRY_BLOCKED",
            runtime_imports_absent
            and runtime_calls_absent
            and _only_raises(entry),
        ),
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
        raise S1WMPreflightError(
            S1WM_PREFLIGHT_DRIFT,
            "S1-WL structure no longer matches the bound static boundary",
        )

    return S1WMPreflightResult(
        S1WM_DECISION,
        S1WM_CONTRACT_DIGEST,
        S1WM_S1WL_SOURCE_DIGEST,
        checks,
        S1WM_BLOCKERS,
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
        0,
    )
