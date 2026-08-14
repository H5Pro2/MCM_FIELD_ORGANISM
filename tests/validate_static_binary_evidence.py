"""Bound, single-process validation controller for static_binary_evidence.py.

This file is implemented for later, separately authorized execution. It must
not be imported or run before its independent static acceptance.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import runpy
import shutil
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
from typing import Any, NoReturn


TOOL_RUN_NAME = "mcm_g1_static_binary_evidence_fixture_target"
EXCLUSION_SCHEMA = "mcm-g1-validation-realpath-exclusion-v1"
SYNTAX_SCHEMA = "mcm-g1-static-binary-syntax-validation-v1"
FIXTURE_SCHEMA = "mcm-g1-static-binary-synthetic-fixtures-v1"
REPORT_SCHEMA = "mcm-g1-static-binary-validation-report-v1"
ERROR_SCHEMA = "mcm-g1-tool-validation-error-v1"
ALLOWED_TARGET_IMPORTS = {
    "__future__",
    "argparse",
    "dataclasses",
    "datetime",
    "hashlib",
    "json",
    "os",
    "pathlib",
    "struct",
    "sys",
    "typing",
}
SUCCESS_FILES = {
    "syntax_validation.json",
    "synthetic_fixture_validation.json",
    "validation_report.json",
}
FLAGS = {
    "g2_touched": False,
    "manifest_generated": False,
    "project_control_opened": False,
    "real_target_binary_opened": False,
    "resolver_run": False,
}


class ValidationStop(Exception):
    def __init__(self, code: str, detail: str, *, phase: str, case_id: str | None = None) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail
        self.phase = phase
        self.case_id = case_id


def stop(code: str, detail: str, *, phase: str, case_id: str | None = None) -> NoReturn:
    raise ValidationStop(code, detail, phase=phase, case_id=case_id)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def binding(path: Path, role: str) -> dict[str, Any]:
    resolved = path.resolve(strict=True)
    if not resolved.is_file():
        stop("META_BINDING_MISMATCH", f"not a file: {resolved}", phase="binding")
    return {
        "path": resolved.as_posix(),
        "role": role,
        "sha256": sha256(resolved),
        "size": resolved.stat().st_size,
    }


def verify_binding(
    path: Path,
    role: str,
    expected_size: int,
    expected_sha256: str,
    *,
    expected_path: Path | None = None,
) -> dict[str, Any]:
    actual = binding(path, role)
    if expected_path is not None and Path(actual["path"]) != expected_path.resolve(strict=True):
        stop("META_BINDING_MISMATCH", f"path mismatch for {role}", phase="binding")
    if actual["size"] != expected_size or actual["sha256"] != expected_sha256.upper():
        stop("META_BINDING_MISMATCH", f"size or SHA-256 mismatch for {role}", phase="binding")
    return actual


def lexical_windows_path(value: str) -> str:
    pure = PureWindowsPath(value)
    if not pure.is_absolute() or not pure.drive or "\\" in value or not value.startswith(f"{pure.drive}/"):
        stop("EXCLUSION_BINDING_MISMATCH", f"invalid excluded path: {value}", phase="exclusion")
    return value.casefold()


def verify_exclusion(document: Any, protected_paths: list[Path]) -> list[str]:
    if not isinstance(document, dict) or document.get("schema") != EXCLUSION_SCHEMA:
        stop("EXCLUSION_BINDING_MISMATCH", "unexpected exclusion schema", phase="exclusion")
    counts = document.get("expected_counts")
    if not isinstance(counts, dict) or (
        counts.get("cpython_binary"), counts.get("native_candidate"), counts.get("total")
    ) != (1, 53, 54):
        stop("EXCLUSION_BINDING_MISMATCH", "unexpected exclusion counts", phase="exclusion")
    entries = document.get("entries")
    if not isinstance(entries, list) or len(entries) != 54:
        stop("EXCLUSION_BINDING_MISMATCH", "exclusion list must contain 54 entries", phase="exclusion")
    roles = {"cpython-binary": 0, "native-candidate": 0}
    paths: list[str] = []
    for item in entries:
        if not isinstance(item, dict) or set(item) != {"path", "role"}:
            stop("EXCLUSION_BINDING_MISMATCH", "invalid exclusion entry", phase="exclusion")
        role = item.get("role")
        if role not in roles or not isinstance(item.get("path"), str):
            stop("EXCLUSION_BINDING_MISMATCH", "invalid exclusion role or path", phase="exclusion")
        roles[role] += 1
        paths.append(lexical_windows_path(item["path"]))
    if roles != {"cpython-binary": 1, "native-candidate": 53} or len(set(paths)) != 54:
        stop("EXCLUSION_BINDING_MISMATCH", "role count or uniqueness mismatch", phase="exclusion")
    protected = {Path(os.path.abspath(path)).as_posix().casefold() for path in protected_paths}
    for candidate in protected:
        for excluded in paths:
            prefix = excluded.rstrip("/") + "/"
            if candidate == excluded or candidate.startswith(prefix):
                stop("EXCLUSION_BINDING_MISMATCH", "controller path collides with exclusion", phase="exclusion")
    return paths


def pycache_inventory(paths: list[Path]) -> set[str]:
    result: set[str] = set()
    for source in paths:
        cache = source.parent / "__pycache__"
        if cache.exists():
            result.update(item.resolve(strict=False).as_posix() for item in cache.rglob("*"))
    return result


def install_write_guard(allowed_roots: list[Path]) -> tuple[list[str], list[Path]]:
    roots = [root.resolve(strict=False) for root in allowed_roots]
    observed: list[str] = []

    def audit(event: str, args: tuple[Any, ...]) -> None:
        path_value: Any = None
        write = False
        if event == "open" and args:
            path_value = args[0]
            mode = args[1] if len(args) > 1 else None
            flags = args[2] if len(args) > 2 else 0
            write = (isinstance(mode, str) and any(marker in mode for marker in "wax+")) or (
                isinstance(flags, int) and bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            )
        elif event in {"os.mkdir", "os.remove", "os.rename", "os.rmdir"} and args:
            path_value = args[0]
            write = True
        if not write or not isinstance(path_value, (str, bytes, os.PathLike)):
            return
        candidate = Path(path_value).resolve(strict=False)
        if not any(candidate == root or root in candidate.parents for root in roots):
            raise PermissionError(f"write outside allowed roots: {candidate}")
        observed.append(candidate.as_posix())

    sys.addaudithook(audit)
    return observed, roots


def direct_imports(tree: ast.Module) -> set[str]:
    result: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level or node.module is None:
                stop("TARGET_IMPORT_SET_MISMATCH", "relative target import", phase="syntax")
            result.add(node.module.split(".", 1)[0])
    return result


def named_function(tree: ast.Module, name: str) -> ast.FunctionDef:
    matches = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name]
    if len(matches) != 1:
        stop("AST_ORACLE_MISMATCH", f"expected one function {name}", phase="syntax")
    return matches[0]


def call_name(node: ast.AST) -> str | None:
    if not isinstance(node, ast.Call):
        return None
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def is_error_context_assignment(node: ast.stmt) -> bool:
    return (
        isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id == "error_context"
        and call_name(node.value) == "ErrorContext"
        and any(keyword.arg == "started_utc" for keyword in node.value.keywords)
    )


def is_expected_context_assignment(node: ast.AST) -> bool:
    return (
        isinstance(node, (ast.Assign, ast.AnnAssign))
        and isinstance(node.target if isinstance(node, ast.AnnAssign) else node.targets[0], ast.Attribute)
        and (node.target if isinstance(node, ast.AnnAssign) else node.targets[0]).attr == "expected_control"
    )


def routing_oracle(tree: ast.Module) -> dict[str, bool]:
    main = named_function(tree, "main")
    tries = [node for node in main.body if isinstance(node, ast.Try)]
    if not tries:
        return {name: False for name in (
            "context_before_try", "parse_binding_in_try", "evidence_handler", "writer_before_return",
            "expected_control_after_parse",
        )}
    first_try = tries[0]
    context_before = any(is_error_context_assignment(node) for node in main.body[: main.body.index(first_try)])
    parse_positions = [
        index for index, node in enumerate(first_try.body)
        if any(call_name(child) == "_parse_binding" for child in ast.walk(node))
        and any(
            isinstance(child, ast.Constant) and child.value == "independent_control_binding"
            for child in ast.walk(node)
        )
    ]
    handlers = [
        handler for handler in first_try.handlers
        if isinstance(handler.type, ast.Name) and handler.type.id == "EvidenceError" and handler.name == "exc"
    ]
    writer_before_return = False
    if len(handlers) == 1:
        writer = return_two = None
        for index, statement in enumerate(handlers[0].body):
            for child in ast.walk(statement):
                if call_name(child) == "_write_error_only" and isinstance(child, ast.Call):
                    keyword_ok = any(
                        keyword.arg == "context" and isinstance(keyword.value, ast.Name)
                        and keyword.value.id == "error_context" for keyword in child.keywords
                    )
                    positional_ok = len(child.args) >= 2 and isinstance(child.args[1], ast.Name) and child.args[1].id == "exc"
                    if keyword_ok and positional_ok:
                        writer = index
            if isinstance(statement, ast.Return) and isinstance(statement.value, ast.Constant) and statement.value.value == 2:
                return_two = index
        writer_before_return = writer is not None and return_two is not None and writer < return_two
    expected_positions = [index for index, node in enumerate(first_try.body) if any(is_expected_context_assignment(x) for x in ast.walk(node))]
    return {
        "context_before_try": context_before,
        "parse_binding_in_try": len(parse_positions) == 1,
        "evidence_handler": len(handlers) == 1,
        "writer_before_return": writer_before_return,
        "expected_control_after_parse": bool(parse_positions) and bool(expected_positions)
        and min(expected_positions) > parse_positions[0],
    }


def evaluate_count_expression(node: ast.AST, environment: dict[str, Any]) -> int:
    if isinstance(node, ast.Constant) and isinstance(node.value, (str, int)):
        return node.value
    if isinstance(node, ast.Name) and node.id in environment:
        return environment[node.id]
    if isinstance(node, ast.Subscript):
        container = evaluate_count_expression(node.value, environment)
        if isinstance(node.slice, ast.Slice):
            lower = evaluate_count_expression(node.slice.lower, environment) if node.slice.lower else None
            upper = evaluate_count_expression(node.slice.upper, environment) if node.slice.upper else None
            if lower != 1 or upper != 4 or node.slice.step is not None:
                stop("AST_ORACLE_MISMATCH", "only slice 1:4 is allowed", phase="fixtures")
            return container[1:4]
        key = evaluate_count_expression(node.slice, environment)
        if not isinstance(key, (str, int)):
            stop("AST_ORACLE_MISMATCH", "invalid count subscript", phase="fixtures")
        return container[key]
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "len" and len(node.args) == 1 and not node.keywords:
        return len(evaluate_count_expression(node.args[0], environment))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "sum" and len(node.args) == 1 and not node.keywords:
        generator = node.args[0]
        if not isinstance(generator, ast.GeneratorExp) or len(generator.generators) != 1:
            stop("AST_ORACLE_MISMATCH", "sum requires one generator", phase="fixtures")
        clause = generator.generators[0]
        if clause.ifs or clause.is_async or not isinstance(clause.target, ast.Name):
            stop("AST_ORACLE_MISMATCH", "invalid sum generator", phase="fixtures")
        iterable = evaluate_count_expression(clause.iter, environment)
        values = []
        for item in iterable:
            nested = dict(environment)
            nested[clause.target.id] = item
            values.append(evaluate_count_expression(generator.elt, nested))
        return sum(values)
    stop("AST_ORACLE_MISMATCH", f"forbidden count AST node: {type(node).__name__}", phase="fixtures")


def count_oracle(tree: ast.Module, case: dict[str, int]) -> list[int]:
    collect = named_function(tree, "collect")
    report_assignments = [
        node for node in collect.body if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "report_document" for target in node.targets)
    ]
    if len(report_assignments) != 1 or not isinstance(report_assignments[0].value, ast.Dict):
        stop("AST_ORACLE_MISMATCH", "report_document assignment missing", phase="fixtures")
    report_dict = report_assignments[0].value
    counts_nodes = [value for key, value in zip(report_dict.keys, report_dict.values)
                    if isinstance(key, ast.Constant) and key.value == "counts"]
    if len(counts_nodes) != 1 or not isinstance(counts_nodes[0], ast.Dict):
        stop("AST_ORACLE_MISMATCH", "counts dictionary missing", phase="fixtures")
    actual_keys = [key.value for key in counts_nodes[0].keys if isinstance(key, ast.Constant)]
    expected_keys = [
        "builtin_entries", "frozen_entries", "frozen_override_entries",
        "frozen_alias_entries", "native_candidates", "native_init_exports",
    ]
    if actual_keys != expected_keys:
        stop("AST_ORACLE_MISMATCH", "count key order or membership differs", phase="fixtures")
    def entries(count: int) -> list[dict[str, int]]:
        return [{"index": index} for index in range(count)]

    table_result = {
        "override": {"entries": entries(case["override"])},
        "tables": [
            {"entries": entries(case["builtin"])},
            {"entries": entries(case["bootstrap"])},
            {"entries": entries(case["stdlib"])},
            {"entries": entries(case["test"])},
            {"entries": entries(case["alias"])},
        ],
    }
    export_results = [
        {"init_candidates": entries(case["init"] if index == 0 else 0)}
        for index in range(case["native"])
    ]
    environment = {"export_results": export_results, "table_result": table_result}
    return [evaluate_count_expression(value, environment) for value in counts_nodes[0].values]


def pe_bytes(*, image_base: int = 0x180000000, file_alignment: int = 0x200,
             section_alignment: int = 0x1000) -> bytes:
    data = bytearray(0x400)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3C, 0x80)
    data[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<HHIIIHH", data, 0x84, 0x8664, 1, 0, 0, 0, 0xF0, 0)
    optional = 0x98
    struct.pack_into("<H", data, optional, 0x20B)
    struct.pack_into("<Q", data, optional + 24, image_base)
    struct.pack_into("<I", data, optional + 32, section_alignment)
    struct.pack_into("<I", data, optional + 36, file_alignment)
    struct.pack_into("<I", data, optional + 56, 0x2000)
    struct.pack_into("<I", data, optional + 60, 0x200)
    struct.pack_into("<I", data, optional + 108, 0)
    section = optional + 0xF0
    data[section:section + 8] = b".data\0\0\0"
    struct.pack_into("<IIII", data, section + 8, 0x200, 0x1000, 0x200, 0x200)
    return bytes(data)


def case_result(case_id: str, inputs: Any, expected: Any, observed: Any, passed: bool,
                error: Any = None) -> dict[str, Any]:
    return {"error": error, "expected": expected, "id": case_id, "inputs": inputs,
            "observed": observed, "passed": passed}


def run_count_cases(tree: ast.Module) -> list[dict[str, Any]]:
    cases = [
        ("C-EMPTY", dict(builtin=0, bootstrap=0, stdlib=0, test=0, override=0, alias=0, native=0, init=0), [0, 0, 0, 0, 0, 0]),
        ("C-DISJOINT", dict(builtin=2, bootstrap=3, stdlib=5, test=7, override=11, alias=13, native=2, init=3), [2, 15, 11, 13, 2, 3]),
        ("C-ALIAS-ONLY", dict(builtin=0, bootstrap=0, stdlib=0, test=0, override=0, alias=4, native=0, init=0), [0, 0, 0, 4, 0, 0]),
        ("C-OVERRIDE-ONLY", dict(builtin=0, bootstrap=0, stdlib=0, test=0, override=6, alias=0, native=0, init=0), [0, 0, 6, 0, 0, 0]),
    ]
    results = []
    for case_id, inputs, expected in cases:
        observed = count_oracle(tree, inputs)
        results.append(case_result(case_id, inputs, expected, observed, observed == expected))
    return results


def early_pe_failure_branches(tree: ast.Module) -> dict[str, bool]:
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "PEImage"]
    method = next((node for node in classes[0].body if isinstance(node, ast.FunctionDef) and node.name == "_parse_headers"), None) if len(classes) == 1 else None
    if method is None:
        return {}
    failure_lines: dict[str, int] = {}
    directory_loop = section_assignment = None
    for node in ast.walk(method):
        if isinstance(node, ast.Call) and call_name(node) == "_fail" and len(node.args) >= 2:
            code, detail = node.args[:2]
            if (
                isinstance(code, ast.Constant) and code.value == "UNSUPPORTED_PE_FORMAT"
                and isinstance(detail, ast.Constant) and isinstance(detail.value, str)
            ):
                failure_lines[detail.value] = node.lineno
        if isinstance(node, ast.For) and isinstance(node.target, ast.Name) and node.target.id == "index" and any(
            isinstance(child, ast.Name) and child.id == "directory_count" for child in ast.walk(node.iter)
        ):
            directory_loop = node.lineno
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "section_offset" for target in node.targets
        ):
            section_assignment = node.lineno
    if directory_loop is None or section_assignment is None or directory_loop >= section_assignment:
        return {}
    return {detail: line < directory_loop for detail, line in failure_lines.items()}


def run_pe_cases(namespace: dict[str, Any], tree: ast.Module, fixture_dir: Path) -> list[dict[str, Any]]:
    cases = [
        ("PE-VALID-NORMAL", {}, "success", None),
        ("PE-VALID-LOW", {"file_alignment": 0x200, "section_alignment": 0x200}, "success", None),
        ("PE-IMAGEBASE-ZERO", {"image_base": 0}, "UNSUPPORTED_PE_FORMAT", "zero PE base, alignment, or image size"),
        ("PE-IMAGEBASE-MISALIGNED", {"image_base": 0x180001000}, "UNSUPPORTED_PE_FORMAT", "invalid PE alignment invariants"),
        ("PE-FILE-BELOW", {"file_alignment": 0x100}, "UNSUPPORTED_PE_FORMAT", "invalid PE alignment invariants"),
        ("PE-FILE-ABOVE", {"file_alignment": 0x20000}, "UNSUPPORTED_PE_FORMAT", "invalid PE alignment invariants"),
        ("PE-FILE-NONPOWER", {"file_alignment": 0x300}, "UNSUPPORTED_PE_FORMAT", "invalid PE alignment invariants"),
        ("PE-SECTION-BELOW-FILE", {"file_alignment": 0x200, "section_alignment": 0x100}, "UNSUPPORTED_PE_FORMAT", "invalid PE alignment invariants"),
        ("PE-LOW-MISMATCH", {"file_alignment": 0x200, "section_alignment": 0x800}, "UNSUPPORTED_PE_FORMAT", "invalid PE alignment invariants"),
    ]
    results = []
    branches = early_pe_failure_branches(tree)
    for case_id, variation, expected, expected_detail in cases:
        path = fixture_dir / f"{case_id}.synthetic-pe.bin"
        path.write_bytes(pe_bytes(**variation))
        try:
            namespace["PEImage"].read(path)
            observed = "success"
            observed_detail = None
            error = None
        except namespace["EvidenceError"] as exc:
            observed = exc.code
            observed_detail = exc.detail
            error = exc.record()
        early_abort_bound = expected == "success" or branches.get(expected_detail) is True
        results.append(case_result(
            case_id, variation,
            {"detail": expected_detail, "early_failure_branch": expected != "success", "result": expected},
            {"detail": observed_detail, "early_failure_branch_bound": early_abort_bound, "result": observed},
            observed == expected and observed_detail == expected_detail and early_abort_bound, error,
        ))
    return results


def synthetic_binding(namespace: dict[str, Any], name: str, role: str) -> Any:
    return namespace["Binding"](path=f"Z:/mcm-g1-synthetic/{name}", role=role, size=1, sha256="0" * 64)


def run_error_cases(namespace: dict[str, Any], fixture_dir: Path) -> list[dict[str, Any]]:
    stages = ["E-NONE", "E-EXPECTED", "E-CONTROL", "E-TOOL", "E-CONTRACT", "E-INPUT-1", "E-INPUT-3"]
    results = []
    for case_id in stages:
        context = namespace["ErrorContext"](started_utc="2026-01-01T00:00:00Z")
        if case_id != "E-NONE":
            context.expected_control = synthetic_binding(namespace, "expected.json", "control")
        if case_id in stages[2:]:
            context.control_binding = synthetic_binding(namespace, "control.json", "control")
        if case_id in stages[3:]:
            context.tool_binding = synthetic_binding(namespace, "tool.py", "tool")
        if case_id in stages[4:]:
            context.contract_binding = synthetic_binding(namespace, "contract.md", "contract")
        if case_id == "E-INPUT-1":
            context.input_bindings = [synthetic_binding(namespace, "input-1.bin", "synthetic")]
        if case_id == "E-INPUT-3":
            context.input_bindings = [synthetic_binding(namespace, f"input-{index}.bin", "synthetic") for index in range(1, 4)]
        output = fixture_dir / f"{case_id}.error-output"
        error = namespace["EvidenceError"]("SYNTHETIC_VALIDATION_ERROR", case_id)
        namespace["_write_error_only"](output, error, context=context)
        document = json.loads((output / "static_binary_evaluation_errors.json").read_text(encoding="utf-8"))
        expected_input_bindings = [namespace["asdict"](item) for item in context.input_bindings]
        expected_bindings = {
            "control_binding_expected": namespace["asdict"](context.expected_control) if context.expected_control else None,
            "control_binding_verified": namespace["asdict"](context.control_binding) if context.control_binding else None,
            "tool_binding": namespace["asdict"](context.tool_binding) if context.tool_binding else None,
            "contract_binding": namespace["asdict"](context.contract_binding) if context.contract_binding else None,
            "input_bindings": expected_input_bindings,
        }
        observed_bindings = {key: document.get(key) for key in expected_bindings}
        passed = (
            document.get("complete") is False
            and document.get("stops") == ["SYNTHETIC_VALIDATION_ERROR"]
            and [item.get("code") for item in document.get("errors", [])] == ["SYNTHETIC_VALIDATION_ERROR"]
            and observed_bindings == expected_bindings
            and document.get("started_utc") == "2026-01-01T00:00:00Z"
            and isinstance(document.get("finished_utc"), str) and document["finished_utc"].endswith("Z")
        )
        expected = {"bindings": expected_bindings, "complete": False, "stop": ["SYNTHETIC_VALIDATION_ERROR"]}
        observed = {"bindings": observed_bindings, "complete": document.get("complete"), "stop": document.get("stops")}
        results.append(case_result(case_id, {"context_stage": case_id}, expected, observed, passed))
    return results


def write_documents(staging: Path, documents: dict[str, Any]) -> None:
    if set(documents) != SUCCESS_FILES:
        stop("OUTPUT_INVARIANT_FAILURE", "success file set mismatch", phase="publication")
    for name in sorted(documents):
        with (staging / name).open("xb") as handle:
            handle.write(canonical_json(documents[name]))
            handle.flush()
            os.fsync(handle.fileno())


def publish_directory(staging: Path, final: Path) -> None:
    if final.exists():
        stop("OUTPUT_ALREADY_EXISTS", f"final path exists: {final}", phase="publication")
    staging.replace(final)


def publish_error(error_staging: Path, error_final: Path, document: dict[str, Any]) -> None:
    if error_staging.exists() or error_final.exists():
        return
    error_staging.mkdir(parents=False, exist_ok=False)
    with (error_staging / "validation_error.json").open("xb") as handle:
        handle.write(canonical_json(document))
        handle.flush()
        os.fsync(handle.fileno())
    error_staging.replace(error_final)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    for name in ("runner", "tool", "contract-x", "contract-z", "exclusion", "interpreter"):
        result.add_argument(f"--{name}", required=True, type=Path)
        result.add_argument(f"--{name}-size", required=True, type=int)
        result.add_argument(f"--{name}-sha256", required=True)
    result.add_argument("--workspace", required=True, type=Path)
    result.add_argument("--temp-dir", required=True, type=Path)
    result.add_argument("--success-dir", required=True, type=Path)
    result.add_argument("--error-dir", required=True, type=Path)
    return result


def main() -> int:
    args = parser().parse_args()
    started = utc_now()
    verified: dict[str, Any] = {}
    success_published = False
    allowed_write_roots: list[Path] = []
    staging = args.success_dir.parent / f".{args.success_dir.name}.staging"
    error_staging = args.error_dir.parent / f".{args.error_dir.name}.staging"
    try:
        if args.runner.resolve(strict=True) != Path(__file__).resolve(strict=True):
            stop("META_BINDING_MISMATCH", "--runner does not identify this file", phase="binding")
        if args.interpreter.resolve(strict=True) != Path(sys.executable).resolve(strict=True):
            stop("META_BINDING_MISMATCH", "--interpreter does not identify sys.executable", phase="binding")
        for name, role in (("runner", "runner"), ("tool", "tool"), ("contract_x", "contract-x"),
                           ("contract_z", "contract-z"), ("exclusion", "exclusion"),
                           ("interpreter", "interpreter")):
            verified[name] = verify_binding(getattr(args, name), role, getattr(args, f"{name}_size"),
                                            getattr(args, f"{name}_sha256"))
        if sys.implementation.name != "cpython" or sys.version_info[:3] != (3, 14, 4):
            stop("INTERPRETER_BINDING_MISMATCH", "expected CPython 3.14.4", phase="binding")
        workspace = args.workspace.resolve(strict=True)
        protected = [args.runner, args.tool, args.contract_x, args.contract_z, args.exclusion,
                     args.interpreter, args.temp_dir, args.success_dir, args.error_dir, staging, error_staging]
        if any(workspace not in path.resolve(strict=False).parents and path.resolve(strict=False) != workspace
               for path in protected if path != args.interpreter):
            stop("PATH_SCOPE_MISMATCH", "project path outside workspace", phase="binding")
        if any(path.exists() for path in (args.temp_dir, args.success_dir, args.error_dir, staging, error_staging)):
            stop("OUTPUT_ALREADY_EXISTS", "temp, staging, success, or error path exists", phase="binding")
        exclusion_document = json.loads(args.exclusion.read_text(encoding="utf-8"))
        excluded_paths = verify_exclusion(exclusion_document, protected)
        args.temp_dir.mkdir(parents=False, exist_ok=False)
        staging.mkdir(parents=False, exist_ok=False)
        source = args.tool.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=args.tool.as_posix(), mode="exec")
        imports = direct_imports(tree)
        if imports != ALLOWED_TARGET_IMPORTS:
            stop("TARGET_IMPORT_SET_MISMATCH", f"observed imports: {sorted(imports)}", phase="syntax")
        syntax_document = {
            "bytecode_generated": False, "finished_utc": utc_now(), "interpreter_binding": verified["interpreter"],
            "module_executed": False, "parse_ok": True, "schema": SYNTAX_SCHEMA, "started_utc": started,
            "sys_version": sys.version, "tool_binding": verified["tool"],
        }
        path_before = list(sys.path)
        meta_before = list(sys.meta_path)
        cache_before = pycache_inventory([args.runner, args.tool])
        observed_writes, allowed_write_roots = install_write_guard([args.temp_dir, staging])
        previous_dont_write_bytecode = sys.dont_write_bytecode
        sys.dont_write_bytecode = True
        try:
            namespace = runpy.run_path(args.tool, run_name=TOOL_RUN_NAME)
        finally:
            sys.dont_write_bytecode = previous_dont_write_bytecode
        if sys.path != path_before or sys.meta_path != meta_before:
            stop("IMPORT_STATE_MUTATION", "sys.path or sys.meta_path changed", phase="fixtures")
        cache_after = pycache_inventory([args.runner, args.tool])
        if cache_after != cache_before:
            stop("UNEXPECTED_FILE_CREATED", "__pycache__ inventory changed", phase="fixtures")
        forbidden_calls = ("main", "collect", "_verify_binding")
        if any(not callable(namespace.get(name)) for name in forbidden_calls):
            stop("TARGET_NAMESPACE_MISMATCH", "required forbidden-call guards unavailable", phase="fixtures")
        results = run_count_cases(tree)
        results.extend(run_pe_cases(namespace, tree, args.temp_dir))
        results.extend(run_error_cases(namespace, args.temp_dir))
        routing = routing_oracle(tree)
        results.append(case_result("R-CLI-EARLY-ERROR", {}, {key: True for key in routing}, routing, all(routing.values())))
        passed = sum(item["passed"] is True for item in results)
        failed = len(results) - passed
        if len(results) != 21 or passed != 21 or failed != 0:
            stop("FIXTURE_VALIDATION_FAILED", f"passed={passed}, failed={failed}", phase="fixtures")
        shutil.rmtree(args.temp_dir)
        if error_staging.exists():
            stop("UNEXPECTED_FILE_CREATED", "error staging exists on success path", phase="publication")
        fixture_document = {"cases": results, "failed": failed, "passed": passed, "schema": FIXTURE_SCHEMA, "total": len(results)}
        report_document = {
            **FLAGS, "contract_bindings": [verified["contract_x"], verified["contract_z"]],
            "controller_process_count": 1, "error_publication_renames": 0,
            "excluded_path_count": len(excluded_paths), "exclusion_binding": verified["exclusion"],
            "finished_utc": utc_now(), "fixture_count": 21,
            "fixture_groups": {"alignment": 9, "count": 4, "error_context": 7, "routing": 1},
            "interpreter_binding": verified["interpreter"], "runner_binding": verified["runner"],
            "schema": REPORT_SCHEMA, "started_utc": started, "success_publication_renames": 1,
            "target_runpy_executions": 1, "tool_binding": verified["tool"],
            "unexpected_write_count": 0 if all(
                any(
                    Path(path).resolve(strict=False) == root.resolve(strict=False)
                    or root.resolve(strict=False) in Path(path).resolve(strict=False).parents
                    for root in allowed_write_roots
                )
                for path in observed_writes
            ) else 1,
        }
        write_documents(staging, {
            "syntax_validation.json": syntax_document,
            "synthetic_fixture_validation.json": fixture_document,
            "validation_report.json": report_document,
        })
        publish_directory(staging, args.success_dir)
        success_published = True
        return 0
    except Exception as exc:
        if staging.exists():
            shutil.rmtree(staging)
        code = exc.code if isinstance(exc, ValidationStop) else "INTERNAL_VALIDATION_FAILURE"
        detail = exc.detail if isinstance(exc, ValidationStop) else f"{type(exc).__name__}: {exc}"
        phase = exc.phase if isinstance(exc, ValidationStop) else "internal"
        case_id = exc.case_id if isinstance(exc, ValidationStop) else None
        error_document = {
            **FLAGS, "case_id": case_id, "detail": detail, "error_code": code,
            "finished_utc": utc_now(), "meta_bindings": verified, "phase": phase,
            "schema": ERROR_SCHEMA, "started_utc": started,
        }
        if not success_published:
            allowed_write_roots.append(error_staging.resolve(strict=False))
            try:
                publish_error(error_staging, args.error_dir, error_document)
            except OSError:
                pass
        print(f"{code}: {detail}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
