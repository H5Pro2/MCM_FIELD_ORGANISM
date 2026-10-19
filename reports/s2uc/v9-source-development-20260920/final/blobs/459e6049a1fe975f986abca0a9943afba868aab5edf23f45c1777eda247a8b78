"""Static, machine-readable S2-UC run binding; never opens PCM."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from tools import _s2uc_source_binding as source_binding
from tools import _s2ts_temporal_trace_run as source
from tools import _s2uc_resource_ledger as resource_ledger
from tools import _s2uc_dependencies as dependency_inventory

RUN_ID = "s2uc-source-comparison-real-20260920-01"
OUTPUT = "reports/s2uc-source-comparison-real-20260920-01"
PREPARED_RUN_ID = "s2uc-source-comparison-real-20260920-02"
PREPARED_OUTPUT = "reports/s2uc-source-comparison-real-20260920-02"
RUNS = {RUN_ID: OUTPUT, PREPARED_RUN_ID: PREPARED_OUTPUT}
TARGETS = {
    ("g1", 12): {"target": "A", "formations": ("g1-p1", "g1-p2")},
    ("g1", 24): {"target": "A", "formations": ("g1-p1", "g1-p2")},
    ("g1", 26): {"target": "B", "formations": ("g1-p3",)},
    ("g2", 38): {"target": "A", "formations": ("g2-p1",)},
    ("g3", 60): {"target": "A", "formations": ("g3-p1",)},
    ("g3", 67): {"target": "A", "formations": ("g3-p1",)},
    ("g3", 69): {"target": "B", "formations": ("g3-p3", "g3-p4")},
}

def _sha(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _run_pair(run_id: str, output: str) -> None:
    if RUNS.get(run_id) != output:
        raise ValueError("RUN_IDENTITY_INVALID")


def build(*, run_id: str = RUN_ID, output: str = OUTPUT) -> dict[str, object]:
    _run_pair(run_id, output)
    manifest = source_binding.manifest()
    rows, _ = source.source_rows()
    uses = [event["endpoint"] for event in manifest["events"] if "endpoint" in event]
    sources = {source_id: {key: rows[source_id][key] for key in ("source_id", "pcm_sha256", "pcm_byte_count", "nj_snapshot_index", "window_start_sample", "window_end_sample")}
               for source_id in source_binding.IDS.values()}
    root = Path(__file__).parent
    code = {name: _sha(root / name) for name in ("_s2uc_run_entry.py", "_s2uc_source_adapter.py", "s2uc_run_bound_once.py", "_s2uc_record_codec.py", "_s2uc_verification.py", "_s2uc_evaluation.py")}
    value = {"version": "s2uc.run-binding.v1", "run_id": run_id, "output": output,
             "manifest_digest": manifest["binding_digest"], "source_plan_path": str(source.SOURCE_PLAN), "source_plan_sha256": _sha(source.SOURCE_PLAN),
             "sources": sources, "endpoint_uses": uses, "code": code, "targets": {f"{story}/{ordinal}": {"target": target["target"], "formations": list(target["formations"])} for (story, ordinal), target in TARGETS.items()},
             "qualification": {"tests": ["tests.test_s2ub_candidate_confirmation", "tests.test_s2uc_neutral_connection", "tests.test_s2uc_materialization_connection"]}}
    value["binding_digest"] = source_binding.digest(value)
    return value

def validate(value: dict[str, object]) -> None:
    if type(value) is not dict or type(value.get("run_id")) is not str or type(value.get("output")) is not str:
        raise ValueError("RUN_BINDING_INVALID")
    _run_pair(value["run_id"], value["output"])
    if value != build(run_id=value["run_id"], output=value["output"]):
        raise ValueError("RUN_BINDING_INVALID")

def freeze(path, *, run_id: str = RUN_ID, output: str = OUTPUT) -> dict[str, object]:
    value = build(run_id=run_id, output=output)
    data = source_binding.canonical(value)
    from pathlib import Path
    target = Path(path)
    if target.exists(): raise ValueError("RUN_BINDING_ALREADY_EXISTS")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return {"path": str(target), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def reference(path) -> dict[str, object]:
    """Return a lossless, independently checkable reference to a frozen binding."""
    target = Path(path)
    data = target.read_bytes()
    return {"path": str(target), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def final_binding(path, *, source_binding_path, dependencies, inventory_path, qualifications, budget,
                  run_id: str = RUN_ID, output: str = OUTPUT) -> dict[str, object]:
    """Freeze a compact final binding that refers to, rather than copies, its source binding."""
    target = Path(path)
    if target.exists():
        raise ValueError("FINAL_BINDING_ALREADY_EXISTS")
    _run_pair(run_id, output)
    value = {
        "version": "s2uc.final-run-binding.v5",
        "run_id": run_id,
        "output": output,
        "source_binding_ref": reference(source_binding_path),
        "dependencies": dependencies,
        "inventory_ref": reference(inventory_path),
        "qualifications": qualifications,
        "budget": budget,
    }
    data = source_binding.canonical(value)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return {"path": str(target), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def final_binding_v6(path, *, source_binding_path, dependencies, inventory_path, qualification_result, budget,
                     run_id: str, output: str) -> dict[str, object]:
    """Freeze the post-codec V3 closure with distinct success and failure budgets."""
    _run_pair(run_id, output)
    target = Path(path)
    if target.exists():
        raise ValueError("FINAL_BINDING_ALREADY_EXISTS")
    value = {"version": "s2uc.final-run-binding.v6", "run_id": run_id, "output": output,
             "source_binding_ref": reference(source_binding_path), "dependencies": dependencies,
             "inventory_ref": reference(inventory_path), "qualification_result": reference(qualification_result),
             "budget": budget}
    data = source_binding.canonical(value)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return {"path": str(target), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def _resolve_reference(value: object) -> dict[str, object]:
    if type(value) is not dict or set(value) != {"path", "bytes", "sha256"}:
        raise ValueError("FINAL_REFERENCE_INVALID")
    path = Path(value["path"])
    if not path.is_file() or path.stat().st_size != value["bytes"] or _sha(path) != value["sha256"]:
        raise ValueError("FINAL_REFERENCE_INVALID")
    loaded = json.loads(path.read_bytes())
    if type(loaded) is not dict:
        raise ValueError("FINAL_REFERENCE_INVALID")
    return loaded


def _validate_qualification(value: dict[str, object], dependencies: list[dict[str, object]]) -> None:
    """Admit only a successful test protocol bound to the current allowed files."""
    expected = {"version", "command", "result", "tests_run", "real_payloads_opened", "scope", "files"}
    if (set(value) != expected or value["version"] != "s2uc.finalformat-neutral-test.v2"
            or value["result"] != "OK" or type(value["tests_run"]) is not int or value["tests_run"] <= 0
            or value["real_payloads_opened"] is not False or type(value["files"]) is not list):
        raise ValueError("FINAL_QUALIFICATION_INVALID")
    dependency_refs = {(item["path"], item["bytes"], item["sha256"]) for item in dependencies}
    code_refs = {(str(item.get("path", "")).replace("\\", "/"), item.get("bytes"), item.get("sha256"))
                 for item in value["files"] if type(item) is dict}
    dependency_refs = {(str(path).replace("\\", "/"), size, digest) for path, size, digest in dependency_refs}
    required = {"tools/_s2uc_run_binding.py", "tests/test_s2uc_materialization_connection.py"}
    if len(code_refs) != len(value["files"]) or {item[0] for item in code_refs} != required or not code_refs <= dependency_refs:
        raise ValueError("FINAL_QUALIFICATION_INVALID")


def _validate_protocol(value: dict[str, object], dependencies: list[dict[str, object]], summary_ref: dict[str, object]) -> None:
    expected = {"version", "command", "result", "tests_run", "test_cases", "summary_sha256", "files"}
    if (set(value) != expected or value["version"] != "s2uc.finalformat-neutral-protocol.v1"
            or value["result"] != "OK" or type(value["tests_run"]) is not int or value["tests_run"] <= 0
            or type(value["test_cases"]) is not list or len(value["test_cases"]) != value["tests_run"]
            or len(set(value["test_cases"])) != len(value["test_cases"]) or value["summary_sha256"] != summary_ref["sha256"]):
        raise ValueError("FINAL_QUALIFICATION_INVALID")
    _validate_qualification({"version": "s2uc.finalformat-neutral-test.v2", "command": value["command"], "result": value["result"],
                             "tests_run": value["tests_run"], "real_payloads_opened": False, "scope": ["full protocol"],
                             "files": value["files"]}, dependencies)


def _validate_inventory(value: dict[str, object], dependencies: list[dict[str, object]]) -> None:
    expected = {"version", "files", "external", "source"}
    if set(value) != expected or value["version"] != "s2uc.dependency-inventory.v6" or type(value["files"]) is not list:
        raise ValueError("FINAL_INVENTORY_INVALID")
    actual = {(str(item.get("path", "")).replace("\\", "/"), item.get("bytes"), item.get("sha256"))
              for item in value["files"] if type(item) is dict and type(item.get("role")) is str}
    expected_rows = {(str(item["path"]).replace("\\", "/"), item["bytes"], item["sha256"]) for item in dependencies}
    if len(actual) != len(value["files"]) or actual != expected_rows:
        raise ValueError("FINAL_INVENTORY_INVALID")


def _v6_rows(items, expected):
    if type(items) is not list or len(items) != len(expected):
        raise ValueError("FINAL_BUDGET_INVALID")
    rows = {}
    for item in items:
        if (type(item) is not dict or set(item) != {"name", "bytes"}
                or type(item["name"]) is not str or item["name"] in rows
                or type(item["bytes"]) is not int or item["bytes"] < 0):
            raise ValueError("FINAL_BUDGET_INVALID")
        rows[item["name"]] = item["bytes"]
    if rows != expected:
        raise ValueError("FINAL_BUDGET_INVALID")
    return sum(rows.values())


def _v6_alternatives(value, metadata, shared):
    if type(value) is not dict or set(value) != {"success", "failure", "minimal"}:
        raise ValueError("FINAL_BUDGET_INVALID")
    for name, branch in value.items():
        expected = {"metadata": metadata, "shared": shared,
                    "record": resource_ledger.RESERVES["success_record" if name == "success" else "failure_record"],
                    "verification": 0 if name == "minimal" else resource_ledger.RESERVES["verification"]}
        if type(branch) is not dict or set(branch) != {"contributions", "total_bytes", "violations"}:
            raise ValueError("FINAL_BUDGET_INVALID")
        contributions = branch["contributions"]
        if (type(contributions) is not dict or contributions != expected
                or any(type(size) is not int or size < 0 for size in contributions.values())
                or type(branch["total_bytes"]) is not int or branch["total_bytes"] != sum(expected.values())
                or branch["violations"] != []
                or any(size > resource_ledger.LIMITS[key] for key, size in expected.items())
                or sum(expected.values()) > resource_ledger.LIMITS["total"]):
            raise ValueError("FINAL_BUDGET_INVALID")


def _validate_v6_budget(value: dict[str, object], *, manifest_bytes: int, final_bytes: int,
                        dependencies: list[dict[str, object]], source_ref: dict[str, object],
                        inventory_ref: dict[str, object], qualification_ref: dict[str, object],
                        budget_ref: dict[str, object]) -> None:
    """Validate exact file sizes; final_binding_reserve is NOT an upper bound.

    The historical field name is retained. Record/verification/terminal reserves
    are separately fixed allowances, never replacements for measured file sizes.
    """
    required = {"version", "method", "limits", "reserves", "metadata_items", "shared_items", "alternatives", "structural_bound", "result"}
    if (type(value) is not dict or set(value) != required
            or value["version"] != "s2uc.closure-budget.v6" or value["limits"] != resource_ledger.LIMITS
            or value["reserves"] != resource_ledger.RESERVES or value["result"] != "WITHIN_LIMITS"):
        raise ValueError("FINAL_BUDGET_INVALID")
    qualification = _resolve_reference(qualification_ref)
    expected_metadata = {"manifest": manifest_bytes, "final_binding_reserve": final_bytes}
    expected_shared = {
        "active_dependency_sources": sum(item["bytes"] for item in dependencies),
        "frozen_source_binding": source_ref["bytes"], "dependency_inventory": inventory_ref["bytes"],
        "qualification_summary": qualification["test_summary"]["bytes"],
        "qualification_protocol": qualification["test_protocol"]["bytes"],
        "qualification_budget": qualification["budget"]["bytes"],
        "qualification_result": qualification_ref["bytes"], "budget_ledger": budget_ref["bytes"],
        "terminal_reserve": resource_ledger.RESERVES["terminal"],
    }
    metadata = _v6_rows(value["metadata_items"], expected_metadata)
    shared = _v6_rows(value["shared_items"], expected_shared)
    _v6_alternatives(value["alternatives"], metadata, shared)


_V6_TEST_FILES = ("tests/test_s2uc_neutral_connection.py", "tests/test_s2uc_materialization_connection.py")
_V6_COMMAND = "python -m unittest -v tests.test_s2uc_neutral_connection tests.test_s2uc_materialization_connection"


def _v6_test_ids():
    """Read the declared suite without importing or running any tests."""
    result = []
    for filename in _V6_TEST_FILES:
        module = filename[:-3].replace("/", ".")
        tree = ast.parse(Path(filename).read_text(encoding="utf-8-sig"))
        for cls in tree.body:
            if isinstance(cls, ast.ClassDef):
                result.extend(f"{module}.{cls.name}.{method.name}" for method in cls.body
                              if isinstance(method, ast.FunctionDef) and method.name.startswith("test_"))
    return sorted(result)


def _validate_v6_qualification(value, dependencies):
    error = "FINAL_QUALIFICATION_INVALID"
    required = {"version", "qualification_id", "status", "test_summary", "test_protocol", "budget", "gates", "real_payloads_opened"}
    if (type(value) is not dict or set(value) - {"supersedes"} != required
            or value["version"] != "s2uc.codec-error-qualification-result.v2"
            or type(value["qualification_id"]) is not str or not value["qualification_id"]
            or value["status"] != "QUALIFIED" or value["real_payloads_opened"] is not False
            or value["gates"] != {"main_gate": False, "used": False}
            or any(type(v) is not bool for v in value["gates"].values())):
        raise ValueError(error)
    summary, protocol, budget = (_resolve_reference(value[key]) for key in ("test_summary", "test_protocol", "budget"))
    expected_files = {str(Path(item["path"]).resolve()): item for item in dependencies}
    for filename in _V6_TEST_FILES:
        expected_files[str(Path(filename).resolve())] = reference(filename)
    def check_files(rows):
        if type(rows) is not list or len(rows) != len(expected_files):
            raise ValueError(error)
        seen = set()
        for row in rows:
            if type(row) is not dict or set(row) != {"path", "bytes", "sha256"} or type(row["path"]) is not str:
                raise ValueError(error)
            key = str(Path(row["path"]).resolve())
            if (key in seen or key not in expected_files or type(row["bytes"]) is not int
                    or row["bytes"] != expected_files[key]["bytes"] or row["sha256"] != expected_files[key]["sha256"]):
                raise ValueError(error)
            seen.add(key)
    common = {"version", "qualification_id", "command", "result", "tests_run", "files"}
    if (set(summary) != common | {"real_payloads_opened", "scope"}
            or summary["version"] != "s2uc.codec-error-neutral-test.v2"
            or summary["real_payloads_opened"] is not False
            or type(summary["scope"]) is not list or not summary["scope"]
            or any(type(item) is not str or not item for item in summary["scope"])):
        raise ValueError(error)
    if (set(protocol) != common | {"test_cases", "summary_sha256"}
            or protocol["version"] != "s2uc.codec-error-neutral-protocol.v2"
            or protocol["summary_sha256"] != value["test_summary"]["sha256"]
            or type(protocol["test_cases"]) is not list
            or any(type(item) is not str for item in protocol["test_cases"])
            or sorted(protocol["test_cases"]) != _v6_test_ids()):
        raise ValueError(error)
    for artifact in (summary, protocol):
        if (artifact["qualification_id"] != value["qualification_id"] or artifact["command"] != _V6_COMMAND
                or artifact["result"] != "OK" or type(artifact["tests_run"]) is not int
                or artifact["tests_run"] != len(protocol["test_cases"])):
            raise ValueError(error)
        check_files(artifact["files"])
    # A qualification budget is separate from the self-referential final ledger.
    required_budget = {"version", "qualification_id", "limits", "reserves", "metadata_items", "shared_items", "alternatives", "result"}
    if (set(budget) != required_budget or budget["version"] != "s2uc.qualification-budget.v1"
            or budget["qualification_id"] != value["qualification_id"]
            or budget["limits"] != resource_ledger.LIMITS or budget["reserves"] != resource_ledger.RESERVES
            or budget["result"] != "WITHIN_LIMITS"):
        raise ValueError(error)
    try:
        metadata = _v6_rows(budget["metadata_items"], {"manifest": source_binding.manifest()["binding_bytes"]})
        shared = _v6_rows(budget["shared_items"], {
            "active_dependency_sources": sum(item["bytes"] for item in dependencies),
            "qualification_summary": value["test_summary"]["bytes"],
            "qualification_protocol": value["test_protocol"]["bytes"],
            "terminal_reserve": resource_ledger.RESERVES["terminal"],
        })
        _v6_alternatives(budget["alternatives"], metadata, shared)
    except ValueError as exc:
        raise ValueError(error) from exc


def _validate_budget(value: dict[str, object], *, manifest_bytes: int, final_binding_bytes: int, shared_origins: dict[str, int]) -> None:
    """Recompute all branches; stored totals and empty violation lists are never trusted."""
    expected = {"version", "method", "limits", "metadata_items", "shared_items", "alternatives", "result", "historical_overage"}
    if set(value) != expected or value["version"] != "s2uc.closure-budget.v5" or value["limits"] != resource_ledger.LIMITS:
        raise ValueError("FINAL_BUDGET_INVALID")
    metadata = value["metadata_items"]
    shared = value["shared_items"]
    alternatives = value["alternatives"]
    if type(metadata) is not list or type(shared) is not list or set(alternatives) != {"success", "failure", "minimal"}:
        raise ValueError("FINAL_BUDGET_INVALID")
    def subtotal(rows, names):
        if (len(rows) != len(names) or {row.get("name") for row in rows if type(row) is dict} != names
                or any(type(row.get("bytes")) is not int or row["bytes"] < 0 for row in rows if type(row) is dict)):
            raise ValueError("FINAL_BUDGET_INVALID")
        return sum(row["bytes"] for row in rows)
    metadata_total = subtotal(metadata, {"manifest", "compact_final_binding"})
    if metadata_total != manifest_bytes + final_binding_bytes:
        raise ValueError("FINAL_BUDGET_INVALID")
    shared_names = {"active_dependency_sources", "frozen_source_binding", "dependency_inventory", "qualification_protocol", "budget_ledger", "terminal_reserve"}
    shared_total = subtotal(shared, shared_names)
    if {row["name"]: row["bytes"] for row in shared} != shared_origins:
        raise ValueError("FINAL_BUDGET_INVALID")
    for name, record_bytes, verification_bytes in (("success", resource_ledger.RESERVES["success_record"], resource_ledger.RESERVES["verification"]),
                                                    ("failure", resource_ledger.RESERVES["failure_record"], resource_ledger.RESERVES["verification"]),
                                                    ("minimal", resource_ledger.RESERVES["failure_record"], 0)):
        branch = alternatives[name]
        if type(branch) is not dict or set(branch) != {"contributions", "total", "violations"}:
            raise ValueError("FINAL_BUDGET_INVALID")
        expected_contributions = {"metadata": metadata_total, "shared": shared_total, "record": record_bytes, "verification": verification_bytes}
        total = sum(expected_contributions.values())
        violations = [key for key, limit in resource_ledger.LIMITS.items() if key != "total" and expected_contributions[key] > limit]
        if total > resource_ledger.LIMITS["total"]:
            violations.append("total")
        if branch["contributions"] != expected_contributions or branch["total"] != total or branch["violations"] != violations:
            raise ValueError("FINAL_BUDGET_INVALID")
    if value["result"] != "WITHIN_LIMITS" or any(alternatives[name]["violations"] for name in alternatives):
        raise ValueError("FINAL_BUDGET_INVALID")

def load(path) -> dict[str, object]:
    """Validate artifact structure only; this is NOT real starter admission."""
    value = json.loads(Path(path).read_bytes())
    if value.get("version") == "s2uc.final-run-binding.v1":
        required = {"version", "run_id", "output", "source_binding", "dependencies", "qualifications", "budget"}
        if set(value) != required or value["run_id"] != RUN_ID or value["output"] != OUTPUT or type(value["dependencies"]) is not list:
            raise ValueError("FINAL_BINDING_INVALID")
        for item in value["dependencies"]:
            path_item = Path(item["path"])
            if not path_item.is_file() or path_item.stat().st_size != item["bytes"] or _sha(path_item) != item["sha256"]:
                raise ValueError("FINAL_DEPENDENCY_INVALID")
        value = value["source_binding"]
    elif value.get("version") == "s2uc.final-run-binding.v2":
        required = {"version", "run_id", "output", "source_binding_ref", "dependencies", "qualifications", "budget"}
        if (set(value) != required or value["run_id"] != RUN_ID or value["output"] != OUTPUT
                or type(value["dependencies"]) is not list or set(value["qualifications"]) != {"finalformat_test"}
                or set(value["budget"]) != {"ledger"}):
            raise ValueError("FINAL_BINDING_INVALID")
        for item in value["dependencies"]:
            if type(item) is not dict or set(item) != {"path", "bytes", "sha256"}:
                raise ValueError("FINAL_DEPENDENCY_INVALID")
            item_path = Path(item["path"])
            if not item_path.is_file() or item_path.stat().st_size != item["bytes"] or _sha(item_path) != item["sha256"]:
                raise ValueError("FINAL_DEPENDENCY_INVALID")
        _resolve_reference(value["qualifications"]["finalformat_test"])
        _resolve_reference(value["budget"]["ledger"])
        value = _resolve_reference(value["source_binding_ref"])
    elif value.get("version") == "s2uc.final-run-binding.v3":
        required = {"version", "run_id", "output", "source_binding_ref", "dependencies", "qualifications", "budget"}
        if (set(value) != required or value["run_id"] != RUN_ID or value["output"] != OUTPUT
                or type(value["dependencies"]) is not list or set(value["qualifications"]) != {"finalformat_test"}
                or set(value["budget"]) != {"ledger"}):
            raise ValueError("FINAL_BINDING_INVALID")
        for item in value["dependencies"]:
            if type(item) is not dict or set(item) != {"path", "bytes", "sha256"}:
                raise ValueError("FINAL_DEPENDENCY_INVALID")
            item_path = Path(item["path"])
            if not item_path.is_file() or item_path.stat().st_size != item["bytes"] or _sha(item_path) != item["sha256"]:
                raise ValueError("FINAL_DEPENDENCY_INVALID")
        source_value = _resolve_reference(value["source_binding_ref"])
        qualification = _resolve_reference(value["qualifications"]["finalformat_test"])
        budget = _resolve_reference(value["budget"]["ledger"])
        _validate_qualification(qualification, value["dependencies"])
        _validate_budget(budget, manifest_bytes=source_binding.manifest()["binding_bytes"], final_binding_bytes=Path(path).stat().st_size)
        value = source_value
    elif value.get("version") == "s2uc.final-run-binding.v4":
        required = {"version", "run_id", "output", "source_binding_ref", "dependencies", "qualifications", "budget"}
        if (set(value) != required or value["run_id"] != RUN_ID or value["output"] != OUTPUT
                or type(value["dependencies"]) is not list
                or set(value["qualifications"]) != {"finalformat_test", "finalformat_protocol"}
                or set(value["budget"]) != {"ledger"}):
            raise ValueError("FINAL_BINDING_INVALID")
        for item in value["dependencies"]:
            if type(item) is not dict or set(item) != {"path", "bytes", "sha256"}:
                raise ValueError("FINAL_DEPENDENCY_INVALID")
            item_path = Path(item["path"])
            if not item_path.is_file() or item_path.stat().st_size != item["bytes"] or _sha(item_path) != item["sha256"]:
                raise ValueError("FINAL_DEPENDENCY_INVALID")
        source_value = _resolve_reference(value["source_binding_ref"])
        summary = _resolve_reference(value["qualifications"]["finalformat_test"])
        protocol = _resolve_reference(value["qualifications"]["finalformat_protocol"])
        budget = _resolve_reference(value["budget"]["ledger"])
        _validate_qualification(summary, value["dependencies"])
        _validate_protocol(protocol, value["dependencies"], value["qualifications"]["finalformat_test"])
        _validate_budget(budget, manifest_bytes=source_binding.manifest()["binding_bytes"], final_binding_bytes=Path(path).stat().st_size)
        value = source_value
    elif value.get("version") == "s2uc.final-run-binding.v6":
        required = {"version", "run_id", "output", "source_binding_ref", "dependencies", "inventory_ref", "qualification_result", "budget"}
        if (set(value) != required or type(value.get("run_id")) is not str or type(value.get("output")) is not str
                or type(value["dependencies"]) is not list or set(value["budget"]) != {"ledger"}):
            raise ValueError("FINAL_BINDING_INVALID")
        _run_pair(value["run_id"], value["output"])
        seen_dependencies = set()
        for item in value["dependencies"]:
            if type(item) is not dict or set(item) != {"path", "bytes", "sha256"}:
                raise ValueError("FINAL_DEPENDENCY_INVALID")
            if (type(item["path"]) is not str or type(item["bytes"]) is not int or item["bytes"] < 0
                    or type(item["sha256"]) is not str):
                raise ValueError("FINAL_DEPENDENCY_INVALID")
            item_path = Path(item["path"])
            identity = str(item_path.resolve())
            if identity in seen_dependencies:
                raise ValueError("FINAL_DEPENDENCY_INVALID")
            seen_dependencies.add(identity)
            if not item_path.is_file() or item_path.stat().st_size != item["bytes"] or _sha(item_path) != item["sha256"]:
                raise ValueError("FINAL_DEPENDENCY_INVALID")
        source_value = _resolve_reference(value["source_binding_ref"])
        inventory = _resolve_reference(value["inventory_ref"])
        qualification = _resolve_reference(value["qualification_result"])
        budget = _resolve_reference(value["budget"]["ledger"])
        _validate_inventory(inventory, value["dependencies"])
        _validate_v6_qualification(qualification, value["dependencies"])
        if budget.get("version") != "s2uc.closure-budget.v6" or budget.get("result") != "WITHIN_LIMITS":
            raise ValueError("FINAL_BUDGET_INVALID")
        _validate_v6_budget(budget, manifest_bytes=source_binding.manifest()["binding_bytes"], final_bytes=Path(path).stat().st_size,
                            dependencies=value["dependencies"], source_ref=value["source_binding_ref"], inventory_ref=value["inventory_ref"],
                            qualification_ref=value["qualification_result"], budget_ref=value["budget"]["ledger"])
        value = source_value
    elif value.get("version") == "s2uc.final-run-binding.v5":
        required = {"version", "run_id", "output", "source_binding_ref", "dependencies", "inventory_ref", "qualifications", "budget"}
        if (set(value) != required or type(value.get("run_id")) is not str or type(value.get("output")) is not str
                or type(value["dependencies"]) is not list
                or set(value["qualifications"]) != {"finalformat_test", "finalformat_protocol"}
                or set(value["budget"]) != {"ledger"}):
            raise ValueError("FINAL_BINDING_INVALID")
        _run_pair(value["run_id"], value["output"])
        for item in value["dependencies"]:
            if type(item) is not dict or set(item) != {"path", "bytes", "sha256"}:
                raise ValueError("FINAL_DEPENDENCY_INVALID")
            item_path = Path(item["path"])
            if not item_path.is_file() or item_path.stat().st_size != item["bytes"] or _sha(item_path) != item["sha256"]:
                raise ValueError("FINAL_DEPENDENCY_INVALID")
        source_value = _resolve_reference(value["source_binding_ref"])
        inventory = _resolve_reference(value["inventory_ref"])
        summary = _resolve_reference(value["qualifications"]["finalformat_test"])
        protocol = _resolve_reference(value["qualifications"]["finalformat_protocol"])
        budget = _resolve_reference(value["budget"]["ledger"])
        _validate_inventory(inventory, value["dependencies"])
        _validate_qualification(summary, value["dependencies"])
        _validate_protocol(protocol, value["dependencies"], value["qualifications"]["finalformat_test"])
        shared_origins = {
            "active_dependency_sources": sum(item["bytes"] for item in value["dependencies"]),
            "frozen_source_binding": value["source_binding_ref"]["bytes"],
            "dependency_inventory": value["inventory_ref"]["bytes"],
            "qualification_protocol": value["qualifications"]["finalformat_test"]["bytes"] + value["qualifications"]["finalformat_protocol"]["bytes"],
            "budget_ledger": value["budget"]["ledger"]["bytes"],
            "terminal_reserve": resource_ledger.RESERVES["terminal"],
        }
        _validate_budget(budget, manifest_bytes=source_binding.manifest()["binding_bytes"], final_binding_bytes=Path(path).stat().st_size,
                         shared_origins=shared_origins)
        value = source_value
    validate(value)
    return value


def load_for_start(path):
    """Non-optional admission for the real starter, before gate or supplier.

    Synthetic structure fixtures may use load(), but cannot pass this boundary.
    Completeness and source-byte allowances are checked before a large binding's
    qualification/closure ledger, so an oversized complete set has its own error.
    """
    value = json.loads(Path(path).read_bytes())
    if type(value) is not dict:
        raise ValueError("FINAL_BINDING_INVALID")
    if value.get("version") == "s2uc.execution-binding.v8":
        raise ValueError("V8_REAL_EXECUTION_DISABLED")
    if value.get("version") == "s2uc.prestart-binding.v7" or "contract_id" in value:
        from tools import _s2uc_prestart_v7 as v7
        v7.validate(path)  # Fixed project root; no caller-supplied discovery switches.
        raise ValueError(v7.STOP)  # Never return a V7 binding into V6 publication.
    if value.get("version") != "s2uc.final-run-binding.v6":
        load(path)  # Preserve specific structural failures in historical formats.
        raise ValueError("FINAL_START_BINDING_VERSION_INVALID")
    qualification = _resolve_reference(value.get("qualification_result"))
    summary = _resolve_reference(qualification.get("test_summary"))
    identifier = qualification.get("qualification_id")
    scope = summary.get("scope")
    if (type(identifier) is not str
            or not identifier.startswith("S2UC-CODEC-ERROR-NEUTRAL-QUALIFICATION-")
            or "SYNTHETIC" in identifier.upper()
            or type(scope) is not list or any(type(item) is not str for item in scope)
            or any("SYNTHETIC" in item.upper() or "TEST DATA" in item.upper() for item in scope)):
        raise ValueError("FINAL_SYNTHETIC_QUALIFICATION_FORBIDDEN")
    dependencies = value.get("dependencies")
    if type(dependencies) is not list:
        raise ValueError("FINAL_DEPENDENCY_INVALID")
    root = Path(__file__).resolve().parents[1]
    actual = {}
    for item in dependencies:
        if (type(item) is not dict or set(item) != {"path", "bytes", "sha256"}
                or type(item["path"]) is not str or type(item["bytes"]) is not int
                or item["bytes"] < 0 or type(item["sha256"]) is not str):
            raise ValueError("FINAL_DEPENDENCY_INVALID")
        source_path = Path(item["path"]).resolve()
        if (source_path in actual or not source_path.is_relative_to(root) or not source_path.is_file()
                or source_path.stat().st_size != item["bytes"] or _sha(source_path) != item["sha256"]):
            raise ValueError("FINAL_DEPENDENCY_INVALID")
        actual[source_path] = item
    inventory = _resolve_reference(value.get("inventory_ref"))
    _validate_inventory(inventory, dependencies)
    current = dependency_inventory.current()
    required = {(root / item["path"]).resolve() for item in current["files"]}
    if not required <= actual.keys():
        raise ValueError("FINAL_DEPENDENCY_INCOMPLETE")
    if inventory["external"] != current["external"]:
        raise ValueError("FINAL_EXTERNAL_DEPENDENCY_INVALID")
    # Count complete bound source files, not serialized references or RAM.
    source_bytes = sum(item["bytes"] for item in dependencies)
    if (source_bytes > resource_ledger.RESERVES["active_bindings"]
            or source_bytes > resource_ledger.LIMITS["shared"]):
        raise ValueError("FINAL_DEPENDENCY_BUDGET_EXCEEDED")
    return load(path)
