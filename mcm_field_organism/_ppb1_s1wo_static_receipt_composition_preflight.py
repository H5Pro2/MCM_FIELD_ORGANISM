"""Static S1-WO preflight for the private S1-WN receipt composition."""

from __future__ import annotations

import ast
from dataclasses import dataclass, fields
import hashlib
import json
from pathlib import Path

from . import _ppb1_s1wn_private_receipt_coordinator_composition as s1wn


S1WO_SCHEMA_VERSION = "ppb1.s1wo.static.receipt-composition-preflight.v1"
S1WO_CONTRACT_DIGEST = (
    "c220857ae7974ed4ad7aa60676dc66c67574cd3dc94cf879b26cf220ade3e84b"
)
S1WO_S1WN_SOURCE_DIGEST = (
    "0195e26f7b26905e87a7b22ba04229701f01c66dab7795ee38c949c8bbe321bd"
)
S1WO_DECISION = (
    "BLOCKED_STATIC_RECEIPT_COMPOSITION_VALID_PRODUCTION_EFFECTS_MISSING"
)
S1WO_BLOCKERS = (
    "PRODUCTION_RESOURCE_OBSERVER_NOT_WIRED",
    "PRODUCTION_AUTHORIZATION_INSTANTIATION_LOCKED",
    "PRODUCTION_LOCK_TERMINAL_WRITERS_NOT_WIRED",
    "PRIVATE_REAL_PRODUCER_NOT_BOUND",
    "PRODUCTION_ARTIFACT_PATH_NOT_WIRED",
    "PRODUCTION_ENTRYPOINT_HARD_BLOCKED",
)
S1WO_PREFLIGHT_DRIFT = "S1WO_PREFLIGHT_DRIFT"

_RESULT_FIELDS = {
    "decision",
    "root_receipt_digest",
    "resource_receipt_digest",
    "authorization_validation_receipt_digest",
    "cross_receipt_binding_passed",
    "input_receipt_count",
    "composed_stage_count",
    "coordinator_result",
    "in_memory_coordinator_call_count",
    "operating_system_probe_count",
    "filesystem_read_count",
    "filesystem_write_count",
    "execution_id_freshness_check_count",
    "authorization_instantiation_count",
    "producer_resolution_count",
    "producer_call_count",
    "matrix_path_count",
    "production_artifact_count",
    "result_digest",
}
_ZERO_RESULT_FIELDS = {
    "operating_system_probe_count",
    "filesystem_read_count",
    "filesystem_write_count",
    "execution_id_freshness_check_count",
    "authorization_instantiation_count",
    "producer_resolution_count",
    "producer_call_count",
    "matrix_path_count",
    "production_artifact_count",
}


class S1WOPreflightError(ValueError):
    """One fail-closed static S1-WN composition violation."""

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


def _attribute_path(node: ast.expr) -> str | None:
    parts = []
    current: ast.expr = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if not isinstance(current, ast.Name):
        return None
    parts.append(current.id)
    return ".".join(reversed(parts))


def _equality_pairs(function: ast.FunctionDef | None) -> set[frozenset[str]]:
    result = set()
    if function is None:
        return result
    for node in ast.walk(function):
        if (
            isinstance(node, ast.Compare)
            and len(node.ops) == 1
            and isinstance(node.ops[0], ast.Eq)
            and len(node.comparators) == 1
        ):
            left = _attribute_path(node.left)
            right = _attribute_path(node.comparators[0])
            if left is not None and right is not None:
                result.add(frozenset((left, right)))
    return result


def _attributes(function: ast.FunctionDef | None) -> set[str]:
    if function is None:
        return set()
    return {
        path
        for node in ast.walk(function)
        if isinstance(node, ast.Attribute)
        for path in (_attribute_path(node),)
        if path is not None
    }


def _string_constants(function: ast.FunctionDef | None) -> set[str]:
    if function is None:
        return set()
    return {
        node.value
        for node in ast.walk(function)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }


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
class S1WOPreflightResult:
    decision: str
    contract_digest: str
    s1wn_source_digest: str
    checks: tuple[tuple[str, bool], ...]
    blockers: tuple[str, ...]
    source_read_count: int
    contract_read_count: int
    composition_call_count: int
    coordinator_call_count: int
    adapter_call_count: int
    root_receipt_producer_call_count: int
    resource_receipt_producer_call_count: int
    authorization_validator_call_count: int
    operating_system_probe_count: int
    filesystem_write_count: int
    execution_id_freshness_check_count: int
    authorization_instantiation_count: int
    lock_write_count: int
    producer_resolution_count: int
    producer_call_count: int
    matrix_path_count: int
    production_artifact_count: int

    @property
    def ready_for_production_execution(self) -> bool:
        return not self.blockers and all(passed for _, passed in self.checks)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": S1WO_SCHEMA_VERSION,
            "decision": self.decision,
            "contract_digest": self.contract_digest,
            "s1wn_source_digest": self.s1wn_source_digest,
            "checks": [
                {"role": role, "passed": passed}
                for role, passed in self.checks
            ],
            "blockers": list(self.blockers),
            "source_read_count": self.source_read_count,
            "contract_read_count": self.contract_read_count,
            "composition_call_count": self.composition_call_count,
            "coordinator_call_count": self.coordinator_call_count,
            "adapter_call_count": self.adapter_call_count,
            "root_receipt_producer_call_count": (
                self.root_receipt_producer_call_count
            ),
            "resource_receipt_producer_call_count": (
                self.resource_receipt_producer_call_count
            ),
            "authorization_validator_call_count": (
                self.authorization_validator_call_count
            ),
            "operating_system_probe_count": self.operating_system_probe_count,
            "filesystem_write_count": self.filesystem_write_count,
            "execution_id_freshness_check_count": (
                self.execution_id_freshness_check_count
            ),
            "authorization_instantiation_count": (
                self.authorization_instantiation_count
            ),
            "lock_write_count": self.lock_write_count,
            "producer_resolution_count": self.producer_resolution_count,
            "producer_call_count": self.producer_call_count,
            "matrix_path_count": self.matrix_path_count,
            "production_artifact_count": self.production_artifact_count,
            "ready_for_production_execution": self.ready_for_production_execution,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def run_s1wo_static_preflight() -> S1WOPreflightResult:
    """Inspect S1-WN without executing any receipt or coordinator function."""

    root = Path(__file__).resolve().parents[1]
    contract_path = (
        root
        / "docs"
        / "S1WG_PPB1_PRODUKTIONSINTEGRATIONSDELTA_VERTRAG_V1.json"
    )
    source = _source(s1wn)
    tree = ast.parse(source)
    composition = _function(tree, "compose_s1wn_in_memory_h0_h1")
    entry = _function(tree, "execute_s1wn_production_once")
    result_class = _class(tree, "S1WNReceiptCompositionResult")
    ready_property = _method(result_class, "ready_for_production_execution")
    parameters = (
        tuple(argument.arg for argument in composition.args.args)
        if composition is not None
        else ()
    )
    names = _names(composition)
    calls = _calls(composition)
    attributes = _attributes(composition)
    strings = _string_constants(composition)
    literals = _literal_dict_values(composition)
    equality_pairs = _equality_pairs(composition)

    input_types_complete = (
        parameters
        == ("root_receipt", "resource_receipt", "authorization_receipt")
        and {
            "S1WJRootMirrorReceipt",
            "S1WJInjectedResourceReceipt",
            "S1WLInjectedAuthorizationValidationReceipt",
        }.issubset(names)
        and "isinstance" in calls
    )
    digest_chain_complete = {
        frozenset(
            (
                "resource_receipt.root_receipt_digest",
                "root_receipt.receipt_digest",
            )
        ),
        frozenset(
            (
                "authorization_receipt.resource_gate_digest",
                "resource_receipt.gate.resource_gate_digest",
            )
        ),
    }.issubset(equality_pairs)
    positive_gates_complete = {
        "root_receipt.same_volume",
        "resource_receipt.gate.all_resource_gates_passed",
        "authorization_receipt.injected_text_and_digests_match",
    }.issubset(attributes)
    composition_roles_complete = (
        {
            "S1WHInjectedStageAdapter",
            "S1WGProductionArtifactRootResolver",
            "S1WGProductionResourceObserverAdapter",
            "S1WGExactProductionAuthorizationActivator",
            "S1WGProductionLockTerminalAdapter",
            "S1WGPrivateS1VQProducerResolver",
            "S1WGPrivateProductionCoordinator",
            "run_injected_h0_h1",
        }.issubset(calls)
        and {"H0B", "H0C", "H0D", "H0E", "H1"}.issubset(strings)
    )
    synthetic_boundary_complete = (
        {
            "S1WN_SYNTHETIC_PATHS_FREE_NO_WRITE",
            "S1WN_SYNTHETIC_H1_NO_LOCK_NO_CONSUMPTION",
        }.issubset(strings)
        and literals.get("input_receipt_count") == 3
        and literals.get("in_memory_coordinator_call_count") == 1
        and all(literals.get(role) == 0 for role in _ZERO_RESULT_FIELDS)
        and _only_returns_false(ready_property)
        and "H2_BLOCKED" in source
    )
    result_fields_complete = _RESULT_FIELDS == {
        item.name for item in fields(s1wn.S1WNReceiptCompositionResult)
    }
    producers_absent = {
        "resolve_s1wj_injected_root_mirror",
        "observe_s1wj_injected_resources",
        "validate_s1wl_injected_authorization_text",
        "S1WAProductionAuthorization",
        "build_s1we_synthetic_lock_marker",
        "_execute_s1vq_corrected_matrix",
    }.isdisjoint(calls | _imports(tree))
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
    }.isdisjoint(calls)

    checks = (
        (
            "S1WG_CONTRACT_DIGEST_VALID",
            _json_digest(contract_path) == S1WO_CONTRACT_DIGEST,
        ),
        (
            "S1WN_SOURCE_DIGEST_BOUND",
            _source_digest(s1wn) == S1WO_S1WN_SOURCE_DIGEST,
        ),
        ("THREE_PRIVATE_INPUT_TYPES_COMPLETE", input_types_complete),
        ("TWO_DIGEST_EQUALITIES_COMPLETE", digest_chain_complete),
        ("THREE_POSITIVE_INPUT_GATES_COMPLETE", positive_gates_complete),
        ("H0B_TO_H1_COMPOSITION_ROLES_COMPLETE", composition_roles_complete),
        (
            "SYNTHETIC_H0E_H1_AND_ZERO_EFFECTS_BOUND",
            synthetic_boundary_complete and result_fields_complete,
        ),
        (
            "RECEIPT_PRODUCERS_RUNTIME_ABSENT_ENTRY_BLOCKED",
            producers_absent
            and runtime_imports_absent
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
        raise S1WOPreflightError(
            S1WO_PREFLIGHT_DRIFT,
            "S1-WN no longer matches the bound static composition boundary",
        )

    return S1WOPreflightResult(
        S1WO_DECISION,
        S1WO_CONTRACT_DIGEST,
        S1WO_S1WN_SOURCE_DIGEST,
        checks,
        S1WO_BLOCKERS,
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
        0,
        0,
        0,
        0,
    )
