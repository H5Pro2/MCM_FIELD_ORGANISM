"""Static S1-WC post-implementation preflight for production roles."""

from __future__ import annotations

import ast
from dataclasses import dataclass, fields
import hashlib
import json
from pathlib import Path

from . import _ppb1_s1vq_corrected_matrix as s1vq
from . import _ppb1_s1vt_result_pipeline as s1vt
from . import _ppb1_s1vw_synthetic_one_shot_handoff as s1vw
from . import _ppb1_s1vz_synthetic_resource_calibration as s1vz
from . import _ppb1_s1wb_private_production_h0_types as s1wb


S1WC_SCHEMA_VERSION = "ppb1.s1wc.static.production-roles-preflight.v1"
S1WC_CONTRACT_DIGEST = (
    "e1d6c99f9141140c7db207513e725d3521065bab488d7541d4392db0b5218413"
)
S1WC_CALIBRATION_DIGEST = (
    "e8b0aa78c66ec3d9586cf89827f93463b5ce33cd9cf63e3c80ef64f099ff2928"
)
S1WC_DECISION = "BLOCKED_REMAINING_PRIVATE_PRODUCTION_ROLES_NO_EXECUTION"
S1WC_BLOCKERS = (
    "REAL_RESOURCE_OBSERVER_NOT_IMPLEMENTED",
    "PRODUCTION_AUTHORIZATION_INSTANTIATION_LOCKED",
    "PRODUCTION_LOCK_AND_TERMINAL_TYPES_MISSING",
    "PRIVATE_REAL_PRODUCER_NOT_BOUND",
    "PRODUCTION_ARTIFACT_PATH_NOT_WIRED",
    "PRODUCTION_ENTRYPOINT_HARD_BLOCKED",
)
S1WC_PREFLIGHT_DRIFT = "S1WC_PREFLIGHT_DRIFT"

_RESOURCE_OBSERVATION_FIELDS = {
    "platform_binding",
    "source_digests",
    "available_physical_memory_bytes",
    "artifact_volume_free_bytes",
    "artifact_volume_identity",
    "temporary_volume_identity",
    "same_volume",
    "atomic_replace_probe_passed",
    "artifact_paths_free",
    "observation_digest",
}
_RESOURCE_GATE_FIELDS = {
    "resource_contract_digest",
    "calibration_digest",
    "observation_digest",
    "minimum_free_memory_bytes",
    "minimum_free_disk_bytes",
    "memory_gate_passed",
    "disk_gate_passed",
    "platform_gate_passed",
    "source_gate_passed",
    "same_volume_gate_passed",
    "atomic_replace_gate_passed",
    "artifact_paths_gate_passed",
    "all_resource_gates_passed",
    "resource_gate_digest",
}
_AUTHORIZATION_FIELDS = {
    "execution_id",
    "rendered_authorization_text",
    "contract_digest",
    "calibration_digest",
    "resource_gate_digest",
    "parent_plan_digest",
    "corrected_plan_digest",
    "case_count",
    "maximum_registered_call_count",
    "production_entrypoint_id",
    "retry_permitted",
    "authorization_digest",
}


class S1WCPreflightError(ValueError):
    """One fail-closed static inventory violation."""

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


def _tree(module: object) -> ast.Module:
    return ast.parse(_source(module))


def _class_names(tree: ast.Module) -> set[str]:
    return {node.name for node in tree.body if isinstance(node, ast.ClassDef)}


def _function(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    return next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == name
        ),
        None,
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


def _imports(tree: ast.Module) -> set[str]:
    result = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            result.update(alias.name for alias in node.names)
    return result


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


def _json_digest(path: Path, excluded: str | None = None) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if excluded is not None:
        payload.pop(excluded)
    return _digest(payload)


@dataclass(frozen=True, slots=True)
class S1WCPreflightResult:
    decision: str
    contract_digest: str
    calibration_digest: str
    case_count: int
    maximum_registered_call_count: int
    minimum_free_memory_bytes: int
    minimum_free_disk_bytes: int
    source_digests: tuple[tuple[str, str], ...]
    checks: tuple[tuple[str, bool], ...]
    blockers: tuple[str, ...]
    resource_probe_count: int
    producer_call_count: int
    production_artifact_count: int

    @property
    def ready_for_production_implementation(self) -> bool:
        return not self.blockers and all(passed for _, passed in self.checks)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": S1WC_SCHEMA_VERSION,
            "decision": self.decision,
            "contract_digest": self.contract_digest,
            "calibration_digest": self.calibration_digest,
            "case_count": self.case_count,
            "maximum_registered_call_count": (
                self.maximum_registered_call_count
            ),
            "minimum_free_memory_bytes": self.minimum_free_memory_bytes,
            "minimum_free_disk_bytes": self.minimum_free_disk_bytes,
            "source_digests": [
                {"role": role, "digest": digest}
                for role, digest in self.source_digests
            ],
            "checks": [
                {"role": role, "passed": passed}
                for role, passed in self.checks
            ],
            "blockers": list(self.blockers),
            "resource_probe_count": self.resource_probe_count,
            "producer_call_count": self.producer_call_count,
            "production_artifact_count": self.production_artifact_count,
            "ready_for_production_implementation": (
                self.ready_for_production_implementation
            ),
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def run_s1wc_static_preflight() -> S1WCPreflightResult:
    """Inspect production roles without invoking any S1-WB function."""

    root = Path(__file__).resolve().parents[1]
    wa_path = (
        root
        / "docs"
        / "S1WA_PPB1_PRODUKTIONSBINDUNGS_RESSOURCEN_UND_"
        "AUTORISIERUNGSVERTRAG_V1.json"
    )
    vz_path = (
        root
        / "docs"
        / "S1VZ_PPB1_SYNTHETISCHE_RESSOURCENKALIBRIERUNG_RESULT_V1.json"
    )
    wb_source = _source(s1wb)
    wb_tree = ast.parse(wb_source)
    wb_classes = _class_names(wb_tree)
    entry = _function(wb_tree, "execute_s1wb_production_once")
    auth_class = next(
        node
        for node in wb_tree.body
        if isinstance(node, ast.ClassDef)
        and node.name == "S1WAProductionAuthorization"
    )
    auth_init = next(
        (
            node
            for node in auth_class.body
            if isinstance(node, ast.FunctionDef) and node.name == "__init__"
        ),
        None,
    )
    imports = _imports(wb_tree)
    all_calls = set()
    for node in wb_tree.body:
        if isinstance(node, ast.FunctionDef):
            all_calls.update(_calls(node))

    calibrated_sources = dict(s1wb.S1WB_CALIBRATED_SOURCE_DIGESTS)
    current_calibrated_sources = {
        "s1vq_runner": _source_digest(s1vq),
        "s1vt_pipeline": _source_digest(s1vt),
        "s1vw_synthetic_orchestrator": _source_digest(s1vw),
        "s1vz_resource_calibrator": _source_digest(s1vz),
    }
    resource_observation_complete = _RESOURCE_OBSERVATION_FIELDS == {
        item.name for item in fields(s1wb.S1WAProductionResourceObservation)
    }
    resource_gate_complete = _RESOURCE_GATE_FIELDS == {
        item.name for item in fields(s1wb.S1WAProductionResourceGate)
    }
    authorization_fields_complete = _AUTHORIZATION_FIELDS == {
        item.name for item in fields(s1wb.S1WAProductionAuthorization)
    }
    real_resource_observer_present = any(
        name in imports
        for name in ("os", "shutil", "platform", "ctypes", "pathlib")
    ) or any(
        name in all_calls
        for name in ("disk_usage", "GetProcessMemoryInfo", "open", "replace")
    )
    authorization_unlocked = not _only_raises(auth_init)
    lock_terminal_present = {
        "S1WAProductionLockMarker",
        "S1WAProductionSuccessOutcome",
        "S1WAProductionErrorOutcome",
    }.issubset(wb_classes)
    real_producer_bound = (
        "_execute_s1vq_corrected_matrix" in imports
        and "_execute_s1vq_corrected_matrix" in all_calls
    )
    production_artifact_wired = (
        "data/generated/ppb1/one_shot" in wb_source
        and "_atomic_publish" in all_calls
    )
    production_entry_open = not _only_raises(entry)

    checks = (
        (
            "S1WA_CONTRACT_DIGEST_VALID",
            _json_digest(wa_path) == S1WC_CONTRACT_DIGEST,
        ),
        (
            "S1VZ_CALIBRATION_DIGEST_VALID",
            _json_digest(vz_path, "calibration_digest")
            == S1WC_CALIBRATION_DIGEST,
        ),
        (
            "CALIBRATED_SOURCE_DIGESTS_PRESERVED",
            calibrated_sources == current_calibrated_sources,
        ),
        ("RESOURCE_OBSERVATION_FIELDS_COMPLETE", resource_observation_complete),
        ("RESOURCE_GATE_FIELDS_COMPLETE", resource_gate_complete),
        ("AUTHORIZATION_FIELDS_COMPLETE", authorization_fields_complete),
        (
            "CALIBRATED_RESOURCE_MINIMA_PRESERVED",
            s1wb.S1WB_MINIMUM_FREE_MEMORY_BYTES == 2 * 1024**3
            and s1wb.S1WB_MINIMUM_FREE_DISK_BYTES == 1024**3,
        ),
        ("REAL_RESOURCE_OBSERVER_PRESENT", real_resource_observer_present),
        ("PRODUCTION_AUTHORIZATION_UNLOCKED", authorization_unlocked),
        ("LOCK_AND_TERMINAL_TYPES_PRESENT", lock_terminal_present),
        ("PRIVATE_REAL_PRODUCER_BOUND", real_producer_bound),
        ("PRODUCTION_ARTIFACT_PATH_WIRED", production_artifact_wired),
        ("PRODUCTION_ENTRYPOINT_OPEN", production_entry_open),
    )
    expected_failed = (
        "REAL_RESOURCE_OBSERVER_PRESENT",
        "PRODUCTION_AUTHORIZATION_UNLOCKED",
        "LOCK_AND_TERMINAL_TYPES_PRESENT",
        "PRIVATE_REAL_PRODUCER_BOUND",
        "PRODUCTION_ARTIFACT_PATH_WIRED",
        "PRODUCTION_ENTRYPOINT_OPEN",
    )
    failed = tuple(role for role, passed in checks if not passed)
    if failed != expected_failed:
        raise S1WCPreflightError(
            S1WC_PREFLIGHT_DRIFT,
            "production role inventory no longer matches the bound boundary",
        )
    source_digests = (
        *tuple(current_calibrated_sources.items()),
        ("s1wb_private_h0_types", _source_digest(s1wb)),
    )
    return S1WCPreflightResult(
        S1WC_DECISION,
        S1WC_CONTRACT_DIGEST,
        S1WC_CALIBRATION_DIGEST,
        s1wb.S1WB_CASE_COUNT,
        s1wb.S1WB_MAXIMUM_CALL_COUNT,
        s1wb.S1WB_MINIMUM_FREE_MEMORY_BYTES,
        s1wb.S1WB_MINIMUM_FREE_DISK_BYTES,
        source_digests,
        checks,
        S1WC_BLOCKERS,
        0,
        0,
        0,
    )
