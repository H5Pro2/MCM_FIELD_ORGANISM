"""Bound one-shot file entry for the prospective S2-TY source run."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from tools import _s2ty_evaluation as evaluation
from tools import _s2ty_real_source_supplier as source_supplier
from tools import _s2ty_record as record
from tools import _s2ty_resource_ledger as ledger
from tools import _s2ty_run_envelope as envelope
from tools import _s2ty_source_time_binding as source_time


ROOT = Path(__file__).resolve().parents[1]
VERSION = "s2ty.real-run-entry.v1"
MAIN_GATE = False
USED = False


class S2TYRealEntryError(ValueError):
    def __init__(self, code: str, details: dict[str, object] | None = None) -> None:
        self.code, self.details = code, {} if details is None else details
        super().__init__(code)


def _need(ok: bool, code: str) -> None:
    if not ok:
        raise S2TYRealEntryError(code)


def _canonical(value: object) -> bytes:
    return json.dumps(value, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _read_binding(path: Path) -> dict[str, object]:
    _need(path.is_file(), "RUN_BINDING_MISSING")
    try:
        value = json.loads(path.read_bytes())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise S2TYRealEntryError("RUN_BINDING_INVALID") from exc
    _need(type(value) is dict and value.get("schema") == "s2ty.real-run-binding.v1", "RUN_BINDING_INVALID")
    payload = {key: item for key, item in value.items() if key != "binding_digest"}
    _need(value.get("binding_digest") == _digest(payload), "RUN_BINDING_DIGEST_INVALID")
    return value


def _file_hash(relative_path: str) -> str:
    path = ROOT / relative_path
    _need(path.is_file(), "DEPENDENCY_MISSING")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _preflight(binding_path: Path, output: Path) -> tuple[dict[str, object], dict[str, object]]:
    bound = _read_binding(binding_path)
    _need(type(bound.get("run_id")) is str and bound["run_id"], "RUN_BINDING_INVALID")
    _need(not output.exists(), "OUTPUT_ALREADY_EXISTS")
    expected_hashes = bound.get("code_hashes")
    _need(type(expected_hashes) is dict and expected_hashes == envelope.code_hashes(), "CODE_BINDING_INVALID")
    manifest = source_time.source_manifest()
    _need(bound.get("source_manifest_digest") == manifest["binding_digest"], "SOURCE_MANIFEST_INVALID")
    resolved = source_supplier.source_binding(manifest)
    _need(
        bound.get("source_binding") == {
            "source_plan_sha256": resolved["source_plan_sha256"],
            "source_execution_digest": resolved["source_execution_digest"],
            "profile": resolved["profile"],
            "endpoint_ordinals": list(resolved["endpoint_ordinals"]),
        },
        "SOURCE_BINDING_INVALID",
    )
    owners = bound.get("owners")
    _need(type(owners) is dict and set(owners) == {"adapter", "direct"} and owners["adapter"] != owners["direct"], "OWNER_BINDING_INVALID")
    qualifications = bound.get("qualification_dependencies")
    _need(type(qualifications) is list and qualifications, "QUALIFICATION_BINDING_INVALID")
    for dependency in qualifications:
        _need(type(dependency) is dict and type(dependency.get("path")) is str and type(dependency.get("sha256")) is str, "QUALIFICATION_BINDING_INVALID")
        _need(_file_hash(dependency["path"]) == dependency["sha256"], "QUALIFICATION_BINDING_INVALID")
    dependencies = bound.get("active_dependencies")
    _need(type(dependencies) is list and dependencies, "DEPENDENCY_BINDING_INVALID")
    total_references = 0
    for dependency in dependencies:
        _need(type(dependency) is dict and type(dependency.get("path")) is str, "DEPENDENCY_BINDING_INVALID")
        path = ROOT / dependency["path"]
        _need(path.is_file() and type(dependency.get("sha256")) is str and type(dependency.get("bytes")) is int, "DEPENDENCY_BINDING_INVALID")
        _need(hashlib.sha256(path.read_bytes()).hexdigest() == dependency["sha256"] and path.stat().st_size == dependency["bytes"], "DEPENDENCY_BINDING_INVALID")
        total_references += dependency["bytes"]
    budget = bound.get("budget")
    _need(type(budget) is dict and budget.get("active_reference_bytes") == total_references, "BUDGET_BINDING_INVALID")
    _need(binding_path.stat().st_size <= budget.get("metadata_reserved_bytes", -1), "BUDGET_BINDING_INVALID")
    try:
        ledger.ledger(
            ledger.planned_shape(), source_bytes=manifest["binding_bytes"],
            metadata_bytes=budget["metadata_reserved_bytes"], shared_bytes=total_references,
            success_record_bytes=budget["success_publication_reserved_bytes"],
            failure_record_bytes=budget["failure_publication_reserved_bytes"] + budget["terminal_error_reserved_bytes"],
            verification_bytes=budget["verification_reserved_bytes"],
        )
    except (KeyError, TypeError, ledger.S2TYBudgetError) as exc:
        raise S2TYRealEntryError("BUDGET_BINDING_INVALID") from exc
    return bound, manifest


def _artifact_sizes(artifacts: dict[str, object]) -> dict[str, int]:
    return {name: len(_canonical(value)) for name, value in artifacts.items()}


def _check_publication_budget(bound: dict[str, object], binding_path: Path, artifacts: dict[str, object], branch: str, manifest_bytes: int) -> dict[str, object]:
    _need(branch in {"success", "failure"}, "BUDGET_BINDING_INVALID")
    sizes = _artifact_sizes(artifacts)
    verification = sizes.get("outer-verification.json", 0)
    publication = sum(size for name, size in sizes.items() if name != "outer-verification.json")
    budget = bound["budget"]
    limit = budget[f"{branch}_publication_reserved_bytes"]
    details = {
        "phase": "CLOSURE_BUDGET",
        "branch": branch,
        "artifact_bytes": sizes,
        "publication_bytes": publication,
        "publication_limit": limit,
        "verification_bytes": verification,
        "verification_limit": budget["verification_reserved_bytes"],
        "metadata_bytes": binding_path.stat().st_size,
        "metadata_limit": budget["metadata_reserved_bytes"],
        "reference_bytes": budget["active_reference_bytes"],
        "progress": artifacts.get("envelope.json", {}).get("materialization", {}).get("counts") if type(artifacts.get("envelope.json")) is dict else {"pcm_hashes": 0, "audio_analyses": 0, "nj_projections": 0},
    }
    if publication > limit or verification > budget["verification_reserved_bytes"] or binding_path.stat().st_size > budget["metadata_reserved_bytes"]:
        raise S2TYRealEntryError("PUBLICATION_BUDGET_INVALID", details)
    try:
        ledger_value = ledger.ledger(
            ledger.planned_shape(), source_bytes=artifacts["envelope.json"]["source_manifest"]["binding_bytes"] if type(artifacts.get("envelope.json")) is dict else manifest_bytes,
            metadata_bytes=binding_path.stat().st_size, shared_bytes=budget["active_reference_bytes"],
            success_record_bytes=publication if branch == "success" else 0,
            failure_record_bytes=publication if branch == "failure" else 0,
            verification_bytes=verification,
        )
    except (KeyError, TypeError, ledger.S2TYBudgetError) as exc:
        details["ledger_error"] = getattr(exc, "code", type(exc).__name__)
        raise S2TYRealEntryError("PUBLICATION_LEDGER_INVALID", details) from exc
    return {"artifact_bytes": sizes, "ledger": ledger_value["branches"][branch], "branch": branch}


def _closure_with_balance(base: dict[str, object], artifacts: dict[str, object], bound: dict[str, object], binding_path: Path, branch: str, manifest_bytes: int) -> tuple[dict[str, object], dict[str, object]]:
    closure = dict(base)
    for _ in range(8):
        artifacts["closure.json"] = closure
        balance = _check_publication_budget(bound, binding_path, artifacts, branch, manifest_bytes)
        candidate = {**base, "artifact_balance": balance}
        if candidate == closure:
            return closure, balance
        closure = candidate
    raise S2TYRealEntryError("CLOSURE_BALANCE_UNSTABLE", {"phase": "CLOSURE_BUDGET"})


def _failure_artifacts(*, bound: dict[str, object], binding_path: Path, manifest: dict[str, object], result: object, outer: object, evaluation_result: object = None, phase: str, code: str, details: dict[str, object]) -> tuple[dict[str, object], dict[str, object]]:
    artifacts: dict[str, object] = {}
    if result is not None:
        artifacts["envelope.json"] = result
    if outer is not None:
        artifacts["outer-verification.json"] = outer
    if evaluation_result is not None:
        artifacts["evaluation.json"] = evaluation_result
    artifacts["entry-failure.json"] = {"schema": VERSION, "phase": phase, "code": code, "details": details}
    base = {"schema": VERSION, "run_id": bound["run_id"], "run_status": "NOT_EVALUABLE", "outer_verification": outer.get("status") if type(outer) is dict else "NOT_RUN", "evaluation_allowed": False, "failure": {"phase": phase, "code": code}}
    closure, balance = _closure_with_balance(base, artifacts, bound, binding_path, "failure", manifest["binding_bytes"])
    artifacts["closure.json"] = closure
    return artifacts, balance


def _terminal_error_artifact(*, bound: dict[str, object], binding_path: Path, manifest: dict[str, object], phase: str, code: str, details: dict[str, object], unpublished: dict[str, object]) -> dict[str, object]:
    """Last bounded error record when the full failure envelope cannot fit."""
    omitted = {
        name: {"bytes": len(_canonical(value)), "sha256": hashlib.sha256(_canonical(value)).hexdigest()}
        for name, value in unpublished.items()
    }
    terminal = {
        "schema": "s2ty.terminal-error.v1",
        "run_id": bound["run_id"],
        "status": "NOT_EVALUABLE",
        "phase": phase,
        "code": code,
        "details_digest": _digest(details),
        "progress": details.get("progress", "UNKNOWN"),
        "published_artifacts": [],
        "unpublished_artifacts": omitted,
        "evidence_complete": False,
    }
    size = len(_canonical(terminal))
    budget = bound["budget"]
    _need(size <= budget["terminal_error_reserved_bytes"], "TERMINAL_ERROR_LIMIT")
    try:
        ledger.ledger(
            ledger.planned_shape(), source_bytes=manifest["binding_bytes"],
            metadata_bytes=binding_path.stat().st_size, shared_bytes=budget["active_reference_bytes"],
            success_record_bytes=0, failure_record_bytes=size, verification_bytes=0,
        )
    except ledger.S2TYBudgetError as exc:
        raise S2TYRealEntryError("TERMINAL_ERROR_LIMIT", {"ledger_error": exc.code}) from exc
    return terminal


def _publish_failure(*, output: Path, bound: dict[str, object], binding_path: Path, manifest: dict[str, object], result: object, outer: object, evaluation_result: object, phase: str, code: str, details: dict[str, object]) -> dict[str, object]:
    try:
        artifacts, _ = _failure_artifacts(
            bound=bound, binding_path=binding_path, manifest=manifest, result=result, outer=outer,
            evaluation_result=evaluation_result, phase=phase, code=code, details=details,
        )
    except S2TYRealEntryError as exc:
        unpublished = {}
        if result is not None:
            unpublished["envelope.json"] = result
        if outer is not None:
            unpublished["outer-verification.json"] = outer
        if evaluation_result is not None:
            unpublished["evaluation.json"] = evaluation_result
        terminal = _terminal_error_artifact(
            bound=bound, binding_path=binding_path, manifest=manifest, phase="TERMINAL_CLOSURE",
            code=exc.code, details={"progress": details.get("progress", "UNKNOWN"), "full_failure": details, "full_failure_error": exc.details},
            unpublished=unpublished,
        )
        _publish(output / "terminal-error.json", terminal)
        return terminal
    for name, value in artifacts.items():
        _publish(output / name, value)
    return artifacts["closure.json"]


def _publish(path: Path, value: object) -> None:
    data = _canonical(value)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            path.unlink(missing_ok=True)
        finally:
            raise


def run_bound_once(binding_path: Path, output: Path) -> dict[str, object]:
    """Run the bound source chain once when an authorized caller opens the gate."""
    global MAIN_GATE, USED
    _need(MAIN_GATE and not USED, "RUN_NOT_AUTHORIZED")
    try:
        bound, manifest = _preflight(Path(binding_path), Path(output))
        USED = True
        Path(output).mkdir()
        try:
            supplied = source_supplier.create_payload_supplier(manifest)
        except Exception as exc:
            return _publish_failure(
                output=Path(output), bound=bound, binding_path=Path(binding_path), manifest=manifest,
                result=None, outer=None, evaluation_result=None, phase="SUPPLIER_INITIALIZATION",
                code=getattr(exc, "code", type(exc).__name__), details={"progress": {"state": "NOT_STARTED"}},
            )
        try:
            result = envelope.run_materialized_once(
                run_id=bound["run_id"], manifest=manifest, payload_supplier=supplied,
                owners=bound["owners"], expected_code_hashes=bound["code_hashes"],
            )
        except Exception as exc:
            return _publish_failure(
                output=Path(output), bound=bound, binding_path=Path(binding_path), manifest=manifest,
                result=None, outer=None, evaluation_result=None, phase="RUN_EXECUTION",
                code=getattr(exc, "code", type(exc).__name__), details={"progress": "UNKNOWN"},
            )
        try:
            outer = {"status": "VERIFIED", "proof": envelope.verify_envelope(result)}
        except Exception as exc:
            outer = {"status": "NOT_EVALUABLE", "code": getattr(exc, "code", type(exc).__name__)}
        try:
            evaluation_result = evaluation.evaluate_verified(result) if result.get("status") == "COMPLETE" and outer["status"] == "VERIFIED" else None
        except Exception as exc:
            return _publish_failure(
                output=Path(output), bound=bound, binding_path=Path(binding_path), manifest=manifest,
                result=result, outer=outer, evaluation_result=None, phase="EVALUATION",
                code=getattr(exc, "code", type(exc).__name__), details={"progress": result.get("materialization", {}).get("counts", "UNKNOWN")},
            )
        artifacts = {"envelope.json": result, "outer-verification.json": outer}
        if evaluation_result is not None:
            artifacts["evaluation.json"] = evaluation_result
        normal = {"schema": VERSION, "run_id": bound["run_id"], "run_status": result.get("status"), "outer_verification": outer["status"], "evaluation_allowed": evaluation_result is not None}
        branch = "success" if result.get("status") == "COMPLETE" and outer["status"] == "VERIFIED" else "failure"
        if branch == "failure":
            normal["source_run_status"] = normal["run_status"]
            normal["run_status"] = "NOT_EVALUABLE"
        try:
            closure, balance = _closure_with_balance(normal, artifacts, bound, Path(binding_path), branch, manifest["binding_bytes"])
            artifacts["closure.json"] = closure
        except S2TYRealEntryError as exc:
            return _publish_failure(
                output=Path(output), bound=bound, binding_path=Path(binding_path), manifest=manifest,
                result=result, outer=outer, evaluation_result=evaluation_result, phase="CLOSURE_BUDGET",
                code=exc.code, details=exc.details,
            )
        for name, value in artifacts.items():
            _publish(Path(output) / name, value)
        return artifacts["closure.json"]
    finally:
        MAIN_GATE = False
