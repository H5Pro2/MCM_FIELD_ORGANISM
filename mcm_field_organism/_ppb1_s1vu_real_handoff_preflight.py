"""Static S1-VU preflight for the private S1-VQ to S1-VT handoff."""

from __future__ import annotations

import ast
from dataclasses import dataclass, fields, is_dataclass
import hashlib
import inspect
import json
import textwrap

from . import _ppb1_s1vq_corrected_matrix as s1vq
from . import _ppb1_s1vt_result_pipeline as s1vt


S1VU_SCHEMA_VERSION = "ppb1.s1vu.private.v1"
S1VU_EXPECTED_PARENT_PLAN_DIGEST = (
    "35c1e589f749f1c1f1f24900f611fd43f8329d803a4b82ca94584d1925067ba3"
)
S1VU_EXPECTED_CORRECTED_PLAN_DIGEST = (
    "f307363400ba66e53a49ec9cd21bc17973f93f240f3946eade2c6a7dbdcd1210"
)
S1VU_BLOCKERS = (
    "S1VQ_RUNNER_OUTPUT_NOT_SEALED_AS_S1VT_MATRIX_RESULT",
    "S1VQ_TO_S1VT_ATOMIC_HANDOFF_CHAIN_MISSING",
    "ONE_SHOT_TERMINAL_SUCCESS_OR_ERROR_OUTCOME_MISSING",
)
S1VU_PREFLIGHT_DECISION = "BLOCKED_PRIVATE_REAL_HANDOFF_REQUIRED_NO_EXECUTION"

S1VU_PREFLIGHT_DRIFT = "S1VU_PREFLIGHT_DRIFT"

_REQUIRED_HANDOFF_CALLS = {
    "_execute_s1vq_corrected_matrix",
    "seal_s1vt_matrix_result",
    "compose_s1vt_arm_records",
    "evaluate_s1vt_composition",
}
_TERMINAL_OUTCOME_FIELDS = {
    "matrix_result",
    "composition_result",
    "evaluation_result",
    "error",
}


class S1VUPreflightError(ValueError):
    """One fail-closed S1-VU preflight violation."""

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


def _function_call_inventory(module: object) -> dict[str, set[str]]:
    source = textwrap.dedent(inspect.getsource(module))
    tree = ast.parse(source)
    inventory: dict[str, set[str]] = {}
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        calls: set[str] = set()
        for child in ast.walk(node):
            if not isinstance(child, ast.Call):
                continue
            if isinstance(child.func, ast.Name):
                calls.add(child.func.id)
            elif isinstance(child.func, ast.Attribute):
                calls.add(child.func.attr)
        inventory[node.name] = calls
    return inventory


def _has_terminal_outcome(module: object) -> bool:
    for value in vars(module).values():
        if not isinstance(value, type) or not is_dataclass(value):
            continue
        if _TERMINAL_OUTCOME_FIELDS.issubset(
            {item.name for item in fields(value)}
        ):
            return True
    return False


@dataclass(frozen=True, slots=True)
class S1VUPreflightResult:
    decision: str
    parent_plan_digest: str
    corrected_plan_digest: str
    case_count: int
    total_call_budget: int
    accepted_call_count: int
    checks: tuple[tuple[str, bool], ...]
    blockers: tuple[str, ...]

    @property
    def ready_for_execution(self) -> bool:
        return not self.blockers and all(passed for _, passed in self.checks)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": S1VU_SCHEMA_VERSION,
            "decision": self.decision,
            "parent_plan_digest": self.parent_plan_digest,
            "corrected_plan_digest": self.corrected_plan_digest,
            "case_count": self.case_count,
            "total_call_budget": self.total_call_budget,
            "accepted_call_count": self.accepted_call_count,
            "checks": [
                {"role": role, "passed": passed} for role, passed in self.checks
            ],
            "blockers": list(self.blockers),
            "ready_for_execution": self.ready_for_execution,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def run_s1vu_static_preflight() -> S1VUPreflightResult:
    """Audit the real private handoff without entering the runner body."""

    preparation = s1vq.prepare_s1vq_corrected_runner()
    q_calls = _function_call_inventory(s1vq)
    t_calls = _function_call_inventory(s1vt)

    execution_gate_active = False
    try:
        s1vq.execute_s1vq_corrected_matrix()
    except s1vq.S1VQMatrixError as exc:
        execution_gate_active = exc.code == s1vq.S1VQ_MATRIX_EXECUTION_BLOCKED

    runner_body_present = "_execute_s1vq_registered_path" in q_calls.get(
        "_execute_s1vq_corrected_matrix", set()
    )
    old_output_fields = {
        "corrected_plan_digest",
        "receipts",
        "accepted_call_count",
        "repeat_comparison_digests",
    }.issubset({item.name for item in fields(s1vq.S1VQMatrixResult)})
    runner_output_is_s1vt = inspect.signature(
        getattr(s1vq, "_execute_s1vq_corrected_matrix")
    ).return_annotation in {
        s1vt.S1VTSealedMatrixResult,
        "S1VTSealedMatrixResult",
    }

    pipeline_stages_present = all(
        callable(getattr(s1vt, name, None))
        for name in (
            "seal_s1vt_matrix_result",
            "compose_s1vt_arm_records",
            "evaluate_s1vt_composition",
        )
    )
    all_functions = {**q_calls, **t_calls}
    integrated_handoff = any(
        _REQUIRED_HANDOFF_CALLS.issubset(calls)
        for calls in all_functions.values()
    )
    terminal_outcome_present = _has_terminal_outcome(s1vq) or _has_terminal_outcome(
        s1vt
    )
    v1_bypass_absent = all(
        "evaluate_s1vo_summaries" not in calls for calls in all_functions.values()
    )

    checks = (
        (
            "PARENT_PLAN_DIGEST_PRESERVED",
            preparation.parent_plan_digest == S1VU_EXPECTED_PARENT_PLAN_DIGEST,
        ),
        (
            "CORRECTED_PLAN_DIGEST_PRESERVED",
            preparation.corrected_plan_digest
            == S1VU_EXPECTED_CORRECTED_PLAN_DIGEST,
        ),
        ("EXACT_528_CASES", preparation.case_count == 528),
        ("EXACT_75808_TOTAL_CALLS", preparation.total_call_count == 75808),
        ("ZERO_REGISTERED_CALLS_EXECUTED", preparation.accepted_call_count == 0),
        ("PUBLIC_EXECUTION_GATE_ACTIVE", execution_gate_active),
        ("PRIVATE_REGISTERED_RUNNER_BODY_PRESENT", runner_body_present),
        ("LEGACY_S1VQ_RESULT_ROLES_PRESENT", old_output_fields),
        ("S1VT_PIPELINE_STAGES_PRESENT", pipeline_stages_present),
        ("S1VO_V1_BYPASS_ABSENT", v1_bypass_absent),
        ("RUNNER_OUTPUT_IS_ATOMIC_S1VT_RESULT", runner_output_is_s1vt),
        ("ATOMIC_S1VQ_TO_S1VT_HANDOFF_CHAIN_PRESENT", integrated_handoff),
        ("ONE_SHOT_TERMINAL_OUTCOME_PRESENT", terminal_outcome_present),
    )
    blockers = tuple(
        blocker
        for blocker, resolved in zip(
            S1VU_BLOCKERS,
            (
                runner_output_is_s1vt,
                integrated_handoff,
                terminal_outcome_present,
            ),
            strict=True,
        )
        if not resolved
    )
    expected_failures = {
        "RUNNER_OUTPUT_IS_ATOMIC_S1VT_RESULT",
        "ATOMIC_S1VQ_TO_S1VT_HANDOFF_CHAIN_PRESENT",
        "ONE_SHOT_TERMINAL_OUTCOME_PRESENT",
    }
    if blockers != S1VU_BLOCKERS or any(
        not passed for role, passed in checks if role not in expected_failures
    ):
        raise S1VUPreflightError(
            S1VU_PREFLIGHT_DRIFT,
            "real handoff preflight no longer matches the bound inventory",
        )
    return S1VUPreflightResult(
        S1VU_PREFLIGHT_DECISION,
        preparation.parent_plan_digest,
        preparation.corrected_plan_digest,
        preparation.case_count,
        preparation.total_call_count,
        preparation.accepted_call_count,
        checks,
        blockers,
    )
