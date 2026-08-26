"""Static S1-WF audit after private S1-WD and S1-WE implementation."""

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
from . import _ppb1_s1wd_temporary_resource_observer as s1wd
from . import _ppb1_s1we_private_lock_terminal_types as s1we


S1WF_SCHEMA_VERSION = "ppb1.s1wf.static.roles-integration-preflight.v1"
S1WF_CONTRACT_DIGEST = (
    "e1d6c99f9141140c7db207513e725d3521065bab488d7541d4392db0b5218413"
)
S1WF_CALIBRATION_DIGEST = (
    "e8b0aa78c66ec3d9586cf89827f93463b5ce33cd9cf63e3c80ef64f099ff2928"
)
S1WF_S1WD_SOURCE_DIGEST = (
    "9db1b25065241b19c57fa5ad4bd939d73909eaac7980899e308017ba4fc71bef"
)
S1WF_S1WE_SOURCE_DIGEST = (
    "59c0e98e08b6ecdc85ad44629fd55a9d6125e62957e2a386c3a92094639d9ace"
)
S1WF_DECISION = "BLOCKED_PRIVATE_ROLES_PRESENT_PRODUCTION_INTEGRATION_MISSING"
S1WF_BLOCKERS = (
    "PRODUCTION_RESOURCE_OBSERVER_NOT_WIRED",
    "PRODUCTION_AUTHORIZATION_INSTANTIATION_LOCKED",
    "PRODUCTION_LOCK_TERMINAL_WRITERS_NOT_WIRED",
    "PRIVATE_REAL_PRODUCER_NOT_BOUND",
    "PRODUCTION_ARTIFACT_PATH_NOT_WIRED",
    "PRODUCTION_ENTRYPOINT_HARD_BLOCKED",
)
S1WF_PREFLIGHT_DRIFT = "S1WF_PREFLIGHT_DRIFT"

_LOCK_FIELDS = {
    "execution_id",
    "authorization_digest",
    "resource_gate_digest",
    "source_digests",
    "authorization_consumed",
    "retry_permitted",
    "marker_digest",
}
_SUCCESS_FIELDS = {
    "execution_id",
    "authorization_digest",
    "resource_gate_digest",
    "marker_digest",
    "source_digests",
    "accepted_call_count",
    "matrix_result_digest",
    "composition_result_digest",
    "evaluation_result_digest",
    "authorization_consumed",
    "exactly_once_completed",
    "retry_permitted",
    "partial_result_exposed",
    "terminal_digest",
}
_ERROR_FIELDS = {
    "execution_id",
    "authorization_digest",
    "resource_gate_digest",
    "marker_digest",
    "source_digests",
    "error_stage",
    "error_code",
    "error_detail_digest",
    "last_completed_stage",
    "known_accepted_call_count",
    "authorization_consumed",
    "exactly_once_completed",
    "retry_permitted",
    "partial_result_exposed",
    "terminal_digest",
}


class S1WFPreflightError(ValueError):
    """One fail-closed static S1-WF inventory violation."""

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
class S1WFPreflightResult:
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
    filesystem_write_count: int
    authorization_instantiation_count: int
    producer_call_count: int
    production_artifact_count: int

    @property
    def ready_for_production_execution(self) -> bool:
        return not self.blockers and all(passed for _, passed in self.checks)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": S1WF_SCHEMA_VERSION,
            "decision": self.decision,
            "contract_digest": self.contract_digest,
            "calibration_digest": self.calibration_digest,
            "case_count": self.case_count,
            "maximum_registered_call_count": self.maximum_registered_call_count,
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
            "filesystem_write_count": self.filesystem_write_count,
            "authorization_instantiation_count": (
                self.authorization_instantiation_count
            ),
            "producer_call_count": self.producer_call_count,
            "production_artifact_count": self.production_artifact_count,
            "ready_for_production_execution": self.ready_for_production_execution,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def run_s1wf_static_preflight() -> S1WFPreflightResult:
    """Inspect S1-WD/S1-WE structure without invoking either runtime."""

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
    wd_tree = _tree(s1wd)
    we_tree = _tree(s1we)
    wb_tree = _tree(s1wb)

    wd_observer = _function(wd_tree, "observe_s1wd_temporary_h0")
    wd_entry = _function(wd_tree, "execute_s1wd_production_once")
    we_lock_writer = _function(we_tree, "write_s1we_synthetic_lock")
    we_terminal_writer = _function(we_tree, "publish_s1we_synthetic_terminal")
    we_atomic_move = _function(we_tree, "_atomic_move_without_replace")
    we_entry = _function(we_tree, "execute_s1we_production_once")
    wb_entry = _function(wb_tree, "execute_s1wb_production_once")

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

    calibrated_sources = dict(s1wb.S1WB_CALIBRATED_SOURCE_DIGESTS)
    current_calibrated_sources = {
        "s1vq_runner": _source_digest(s1vq),
        "s1vt_pipeline": _source_digest(s1vt),
        "s1vw_synthetic_orchestrator": _source_digest(s1vw),
        "s1vz_resource_calibrator": _source_digest(s1vz),
    }
    wd_source = _source(s1wd)
    we_source = _source(s1we)
    wd_observer_calls = _calls(wd_observer)
    we_lock_calls = _calls(we_lock_writer)
    we_terminal_calls = _calls(we_terminal_writer)
    we_atomic_calls = _calls(we_atomic_move)

    private_resource_observer_complete = (
        wd_observer is not None
        and {
            "_available_physical_memory",
            "disk_usage",
            "_atomic_replace_probe",
        }.issubset(wd_observer_calls)
        and "TEMPORARY_TEST_ONLY" in wd_source
        and "S1WD_PRODUCTION_ROOT_BLOCKED" in wd_source
        and _only_raises(wd_entry)
    )
    private_lock_terminal_types_complete = (
        _LOCK_FIELDS == {item.name for item in fields(s1we.S1WAProductionLockMarker)}
        and _SUCCESS_FIELDS
        == {item.name for item in fields(s1we.S1WAProductionSuccessOutcome)}
        and _ERROR_FIELDS
        == {item.name for item in fields(s1we.S1WAProductionErrorOutcome)}
    )
    private_lock_terminal_writers_complete = (
        we_lock_writer is not None
        and we_terminal_writer is not None
        and {"_validate_temporary_root", "_exclusive_json"}.issubset(we_lock_calls)
        and {
            "_validate_temporary_root",
            "_exclusive_json",
            "_atomic_move_without_replace",
        }.issubset(we_terminal_calls)
        and {"rename", "link"}.issubset(we_atomic_calls)
        and "TEMPORARY_TEST_ONLY" in we_source
        and "S1WE_PRODUCTION_ROOT_BLOCKED" in we_source
        and _only_raises(we_entry)
    )
    production_resource_observer_wired = not _only_raises(wd_entry)
    production_authorization_unlocked = not _only_raises(auth_init)
    production_lock_terminal_writers_wired = not _only_raises(we_entry)
    combined_calls = set()
    for tree in (wb_tree, wd_tree, we_tree):
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                combined_calls.update(_calls(node))
    real_producer_bound = "_execute_s1vq_corrected_matrix" in combined_calls
    production_entry_open = not all(
        _only_raises(entry) for entry in (wb_entry, wd_entry, we_entry)
    )
    production_artifact_path_wired = (
        production_entry_open
        and "data/generated/ppb1/one_shot" in wd_source
        and "data/generated/ppb1/one_shot" in we_source
    )

    checks = (
        (
            "S1WA_CONTRACT_DIGEST_VALID",
            _json_digest(wa_path) == S1WF_CONTRACT_DIGEST,
        ),
        (
            "S1VZ_CALIBRATION_DIGEST_VALID",
            _json_digest(vz_path, "calibration_digest")
            == S1WF_CALIBRATION_DIGEST,
        ),
        (
            "CALIBRATED_SOURCE_DIGESTS_PRESERVED",
            calibrated_sources == current_calibrated_sources,
        ),
        (
            "S1WD_SOURCE_DIGEST_BOUND",
            _source_digest(s1wd) == S1WF_S1WD_SOURCE_DIGEST,
        ),
        (
            "S1WE_SOURCE_DIGEST_BOUND",
            _source_digest(s1we) == S1WF_S1WE_SOURCE_DIGEST,
        ),
        (
            "CALIBRATED_RESOURCE_MINIMA_PRESERVED",
            s1wb.S1WB_MINIMUM_FREE_MEMORY_BYTES == 2 * 1024**3
            and s1wb.S1WB_MINIMUM_FREE_DISK_BYTES == 1024**3,
        ),
        (
            "PRIVATE_TEMP_RESOURCE_OBSERVER_COMPLETE",
            private_resource_observer_complete,
        ),
        (
            "PRIVATE_LOCK_TERMINAL_TYPES_COMPLETE",
            private_lock_terminal_types_complete,
        ),
        (
            "PRIVATE_TEMP_LOCK_TERMINAL_WRITERS_COMPLETE",
            private_lock_terminal_writers_complete,
        ),
        (
            "PRODUCTION_RESOURCE_OBSERVER_WIRED",
            production_resource_observer_wired,
        ),
        (
            "PRODUCTION_AUTHORIZATION_UNLOCKED",
            production_authorization_unlocked,
        ),
        (
            "PRODUCTION_LOCK_TERMINAL_WRITERS_WIRED",
            production_lock_terminal_writers_wired,
        ),
        ("PRIVATE_REAL_PRODUCER_BOUND", real_producer_bound),
        (
            "PRODUCTION_ARTIFACT_PATH_WIRED",
            production_artifact_path_wired,
        ),
        ("PRODUCTION_ENTRYPOINT_OPEN", production_entry_open),
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
        raise S1WFPreflightError(
            S1WF_PREFLIGHT_DRIFT,
            "S1-WD/S1-WE inventory no longer matches the bound boundary",
        )

    source_digests = (
        *tuple(current_calibrated_sources.items()),
        ("s1wb_private_h0_types", _source_digest(s1wb)),
        ("s1wd_temporary_resource_observer", _source_digest(s1wd)),
        ("s1we_private_lock_terminal_types", _source_digest(s1we)),
    )
    return S1WFPreflightResult(
        S1WF_DECISION,
        S1WF_CONTRACT_DIGEST,
        S1WF_CALIBRATION_DIGEST,
        s1wb.S1WB_CASE_COUNT,
        s1wb.S1WB_MAXIMUM_CALL_COUNT,
        s1wb.S1WB_MINIMUM_FREE_MEMORY_BYTES,
        s1wb.S1WB_MINIMUM_FREE_DISK_BYTES,
        source_digests,
        checks,
        S1WF_BLOCKERS,
        0,
        0,
        0,
        0,
        0,
    )
