"""Static S1-VX post-integration and production-resource preflight."""

from __future__ import annotations

import ast
from dataclasses import dataclass, fields
import hashlib
import json
from pathlib import Path

from . import _ppb1_s1vq_corrected_matrix as s1vq
from . import _ppb1_s1vt_result_pipeline as s1vt
from . import _ppb1_s1vw_synthetic_one_shot_handoff as s1vw


S1VX_SCHEMA_VERSION = "ppb1.s1vx.static.preflight.v1"
S1VX_EXPECTED_PARENT_PLAN_DIGEST = (
    "35c1e589f749f1c1f1f24900f611fd43f8329d803a4b82ca94584d1925067ba3"
)
S1VX_EXPECTED_CORRECTED_PLAN_DIGEST = (
    "f307363400ba66e53a49ec9cd21bc17973f93f240f3946eade2c6a7dbdcd1210"
)
S1VX_EXPECTED_PREFLIGHT_DIGEST = (
    "31147b026d7f7faacba93f15e607e077fa55ace537500bf4c450f8c7d278258c"
)
S1VX_EXPECTED_CASE_COUNT = 528
S1VX_EXPECTED_CALL_COUNT = 75808
S1VX_PRODUCTION_ARTIFACT_ROOT = "data/generated/ppb1/one_shot"
S1VX_DECISION = (
    "BLOCKED_PRODUCTION_BINDING_AND_RESOURCE_GATE_REQUIRED_NO_EXECUTION"
)
S1VX_BLOCKERS = (
    "PRIVATE_REAL_PRODUCER_NOT_BOUND_TO_ONE_SHOT_ORCHESTRATOR",
    "PRODUCTION_AUTHORIZATION_TYPE_MISSING",
    "PRODUCTION_RESOURCE_GATE_AND_MINIMA_MISSING",
    "PRODUCTION_ARTIFACT_PUBLICATION_PATH_NOT_WIRED",
    "PRODUCTION_ENTRYPOINT_HARD_BLOCKED",
)
S1VX_PREFLIGHT_DRIFT = "S1VX_PREFLIGHT_DRIFT"


class S1VXPreflightError(ValueError):
    """One fail-closed S1-VX inventory violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _module_source(module: object) -> str:
    path = Path(module.__file__)
    return path.read_text(encoding="utf-8")


def _module_digest(module: object) -> str:
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


def _calls(function: ast.FunctionDef | None) -> set[str]:
    if function is None:
        return set()
    result: set[str] = set()
    for node in ast.walk(function):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            result.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            result.add(node.func.attr)
    return result


def _imports(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.update(alias.name for alias in node.names)
    return names


def _class_names(tree: ast.Module) -> set[str]:
    return {
        node.name for node in tree.body if isinstance(node, ast.ClassDef)
    }


def _is_unconditional_raise(function: ast.FunctionDef | None) -> bool:
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


@dataclass(frozen=True, slots=True)
class S1VXPreflightResult:
    decision: str
    parent_plan_digest: str
    corrected_plan_digest: str
    prior_preflight_digest: str
    case_count: int
    call_count: int
    production_artifact_root: str
    source_digests: tuple[tuple[str, str], ...]
    checks: tuple[tuple[str, bool], ...]
    blockers: tuple[str, ...]
    authorization_text: str | None

    @property
    def ready_for_real_execution(self) -> bool:
        return (
            not self.blockers
            and self.authorization_text is not None
            and all(passed for _, passed in self.checks)
        )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": S1VX_SCHEMA_VERSION,
            "decision": self.decision,
            "parent_plan_digest": self.parent_plan_digest,
            "corrected_plan_digest": self.corrected_plan_digest,
            "prior_preflight_digest": self.prior_preflight_digest,
            "case_count": self.case_count,
            "call_count": self.call_count,
            "production_artifact_root": self.production_artifact_root,
            "source_digests": [
                {"role": role, "digest": digest}
                for role, digest in self.source_digests
            ],
            "checks": [
                {"role": role, "passed": passed}
                for role, passed in self.checks
            ],
            "blockers": list(self.blockers),
            "authorization_text": self.authorization_text,
            "ready_for_real_execution": self.ready_for_real_execution,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def run_s1vx_static_preflight() -> S1VXPreflightResult:
    """Read static production roles without calling any execution function."""

    q_source = _module_source(s1vq)
    t_source = _module_source(s1vt)
    w_source = _module_source(s1vw)
    q_tree = ast.parse(q_source)
    t_tree = ast.parse(t_source)
    w_tree = ast.parse(w_source)

    synthetic_calls = _calls(_function(w_tree, "run_s1vw_synthetic_once"))
    production_function = _function(w_tree, "execute_s1vw_production_once")
    production_calls = _calls(production_function)
    imported_names = _imports(w_tree)
    class_names = _class_names(w_tree)

    synthetic_chain_present = {
        "_lock_marker",
        "_validate_legacy_result",
        "seal_adapter",
        "compose_adapter",
        "evaluate_adapter",
        "publisher",
    }.issubset(synthetic_calls)
    terminal_types_present = {
        "S1VWLockMarker",
        "S1VWSuccessOutcome",
        "S1VWErrorOutcome",
    }.issubset(class_names)
    real_producer_bound = (
        "_execute_s1vq_corrected_matrix" in imported_names
        and "_execute_s1vq_corrected_matrix" in production_calls
    )
    production_authorization_present = (
        "S1VWProductionAuthorization" in class_names
    )
    production_resource_gate_present = {
        "S1VWProductionResourceGate",
        "S1VWProductionResourceObservation",
    }.issubset(class_names)
    production_artifact_path_wired = (
        S1VX_PRODUCTION_ARTIFACT_ROOT in w_source
        and not _is_unconditional_raise(production_function)
        and "_atomic_publish" in production_calls
    )
    production_entrypoint_open = not _is_unconditional_raise(
        production_function
    )

    success_fields = {item.name for item in fields(s1vw.S1VWSuccessOutcome)}
    error_fields = {item.name for item in fields(s1vw.S1VWErrorOutcome)}
    terminal_roles_complete = {
        "authorization_digest",
        "marker_digest",
        "source_digests",
        "terminal_digest",
        "partial_result_exposed",
    }.issubset(success_fields & error_fields)

    q_execution_calls = _calls(_function(q_tree, "_execute_s1vq_corrected_matrix"))
    pipeline_functions = {
        node.name
        for node in t_tree.body
        if isinstance(node, ast.FunctionDef)
    }
    checks = (
        (
            "PARENT_PLAN_DIGEST_PRESERVED",
            s1vw.S1VW_PARENT_PLAN_DIGEST
            == S1VX_EXPECTED_PARENT_PLAN_DIGEST,
        ),
        (
            "CORRECTED_PLAN_DIGEST_PRESERVED",
            s1vw.S1VW_CORRECTED_PLAN_DIGEST
            == S1VX_EXPECTED_CORRECTED_PLAN_DIGEST,
        ),
        (
            "PRIOR_PREFLIGHT_DIGEST_PRESERVED",
            s1vw.S1VW_PREFLIGHT_DIGEST == S1VX_EXPECTED_PREFLIGHT_DIGEST,
        ),
        (
            "EXACT_528_CASE_AND_75808_CALL_BUDGET",
            s1vw.S1VW_EXPECTED_CASE_COUNT == S1VX_EXPECTED_CASE_COUNT
            and s1vw.S1VW_EXPECTED_CALL_COUNT == S1VX_EXPECTED_CALL_COUNT,
        ),
        (
            "PRIVATE_REGISTERED_RUNNER_BODY_PRESENT",
            "_execute_s1vq_registered_path" in q_execution_calls,
        ),
        (
            "S1VT_PIPELINE_STAGES_PRESENT",
            {
                "seal_s1vt_matrix_result",
                "compose_s1vt_arm_records",
                "evaluate_s1vt_composition",
            }.issubset(pipeline_functions),
        ),
        ("SYNTHETIC_H0_TO_H7_CHAIN_PRESENT", synthetic_chain_present),
        ("TERMINAL_TYPES_COMPLETE", terminal_types_present),
        ("TERMINAL_DIGEST_ROLES_COMPLETE", terminal_roles_complete),
        (
            "SYNTHETIC_RESOURCE_GATE_EXPLICITLY_NON_PRODUCTION",
            "no-production-resources" in w_source,
        ),
        (
            "PRIVATE_REAL_PRODUCER_BOUND",
            real_producer_bound,
        ),
        (
            "PRODUCTION_AUTHORIZATION_TYPE_PRESENT",
            production_authorization_present,
        ),
        (
            "PRODUCTION_RESOURCE_GATE_AND_MINIMA_PRESENT",
            production_resource_gate_present,
        ),
        (
            "PRODUCTION_ARTIFACT_PUBLICATION_PATH_WIRED",
            production_artifact_path_wired,
        ),
        ("PRODUCTION_ENTRYPOINT_OPEN", production_entrypoint_open),
    )
    failed_roles = tuple(role for role, passed in checks if not passed)
    expected_failed_roles = (
        "PRIVATE_REAL_PRODUCER_BOUND",
        "PRODUCTION_AUTHORIZATION_TYPE_PRESENT",
        "PRODUCTION_RESOURCE_GATE_AND_MINIMA_PRESENT",
        "PRODUCTION_ARTIFACT_PUBLICATION_PATH_WIRED",
        "PRODUCTION_ENTRYPOINT_OPEN",
    )
    if failed_roles != expected_failed_roles:
        raise S1VXPreflightError(
            S1VX_PREFLIGHT_DRIFT,
            "post-integration inventory no longer matches the bound boundary",
        )

    source_digests = (
        ("s1vq_runner", _module_digest(s1vq)),
        ("s1vt_pipeline", _module_digest(s1vt)),
        ("s1vw_synthetic_orchestrator", _module_digest(s1vw)),
    )
    return S1VXPreflightResult(
        S1VX_DECISION,
        S1VX_EXPECTED_PARENT_PLAN_DIGEST,
        S1VX_EXPECTED_CORRECTED_PLAN_DIGEST,
        S1VX_EXPECTED_PREFLIGHT_DIGEST,
        S1VX_EXPECTED_CASE_COUNT,
        S1VX_EXPECTED_CALL_COUNT,
        S1VX_PRODUCTION_ARTIFACT_ROOT,
        source_digests,
        checks,
        S1VX_BLOCKERS,
        None,
    )
