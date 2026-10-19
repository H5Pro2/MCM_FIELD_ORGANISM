"""Strict neutral-execution binding; never a real-run authorization or writer."""
import ast
import os
import sys
import re
from pathlib import Path

from tools import _s2uc_inventory_v7 as discovery
from tools import _s2uc_prestart_v7 as old
from tools import _s2uc_resources_v9 as resources
from tools._s2uc_resource_contract_v7 import _need, _same_typed

VERSION = "s2uc.execution-binding.v9"
FILENAME = "execution-binding.json"
TESTS = discovery.TESTS + ("tests/test_s2uc_execution_v8.py", "tests/test_s2uc_source_execution.py", "tests/test_s2uc_source_process_guard.py",)
TOOLS = ("tools/s2uc_source_process_once.py", "tools/s2uc_v9_neutral_check.py",
         "reports/s2uc/v8-process-limit-corrected-20260920/limit.py",
         "reports/s2uc/v8-process-memory-20260920/measure.py")
ENTRIES = ("tools/s2uc_run_bound_once.py",) + TESTS + TOOLS
FILES = old.FILES
from tools import _s2uc_source_context_v9 as context


def current(project_root=discovery.ROOT):
    value = discovery._collect(project_root, ENTRIES, "s2uc.dependency-inventory.v9")
    native = [Path(sys.base_prefix) / f"python{sys.version_info.major}{sys.version_info.minor}.dll"]
    native += [Path(os.environ["SystemRoot"]) / "System32" / name for name in ("kernel32.dll", "psapi.dll")]
    value["external"]["native_runtime"] = [{"path": str(path.resolve()), "bytes": path.stat().st_size,
                                           "sha256": discovery.sha(path.read_bytes())} for path in native]
    return value


def read_source_preparation(path, qualification_path):
    """Read static prospective NU context plus actual neutral evidence; never admit."""
    from tools import _s2uc_qualification_v9 as qualification
    path = Path(path)
    ref, data, _ = discovery.read_file(path.parent, path.name)
    _need(ref["bytes"] <= resources.LIMITS["metadata"], "V9_SOURCE_CONTEXT_BUDGET_EXCEEDED")
    source = context.validate_source_context(old._json(data))
    evidence_result = qualification.read(qualification_path)
    nu_ref, _, _ = discovery.read_file(discovery.ROOT, old.NU_PLAN)
    _need(nu_ref["sha256"] == context.science.SOURCE_PLAN_SHA256, "V9_NU_PLAN_CHANGED")
    amounts = dict.fromkeys(resources.CATEGORIES, 0)
    amounts.update(code=evidence_result["code_bytes"], metadata=ref["bytes"],
                   static_shared=nu_ref["bytes"] + sum(r["bytes"] for r in evidence_result["artifacts"]))
    actual = resources.account("failure_before_publication", amounts)
    _need(actual["within_limits"], "V9_SOURCE_PREPARATION_BUDGET_EXCEEDED")
    return {"source_context": source, "source_context_file": ref, "qualification": evidence_result,
            "nu_plan": nu_ref, "actual": actual, "status": "PREPARATION_ONLY",
            "real_execution_authorized": False}


def manifest():
    return context.neutral_manifest()


def sources():
    return context.endpoints(manifest(), "NEUTRAL_NONZERO_V9")


def contract():
    value = old.contract()
    value.update(contract_id=resources.CONTRACT_ID, binding_version=VERSION, limits=dict(resources.LIMITS),
                 entries=list(ENTRIES), binding={"path": FILENAME, "category": "metadata"},
                 execution="NEUTRAL_ONLY; public real starter disabled")
    return value


def test_ids(root=discovery.ROOT):
    ids = []
    for name in TESTS:
        _, data, _ = discovery.read_file(root, name)
        for cls in ast.parse(data).body:
            if isinstance(cls, ast.ClassDef):
                ids.extend(f"{name[:-3].replace('/', '.')}.{cls.name}.{n.name}" for n in cls.body
                           if isinstance(n, ast.FunctionDef) and n.name.startswith("test_"))
    return sorted(ids)


def evidence(inv):
    common = {"contract_id": resources.CONTRACT_ID, "scope": "NEUTRAL_EXECUTION_TEST_EVIDENCE",
              "inventory_sha256": discovery.sha(old.canonical(inv)), "formal_qualification": False, "evidence_kind": "SYNTHETIC_FIXTURE_NOT_EXECUTED"}
    return {
        "qualification_summary": {**common, "version": "s2uc.qualification-summary.v9", "result": "FIXTURE_ONLY",
                                  "tests_run": len(test_ids()), "real_payloads_opened": False},
        "qualification_protocol": {**common, "version": "s2uc.qualification-protocol.v9", "test_ids": test_ids()},
        "qualification_budget": {**common, "version": "s2uc.qualification-budget.v9", "code_bytes": inv["code_bytes"],
                                 "code_limit": resources.LIMITS["code"]},
        "qualification_result": {**common, "version": "s2uc.qualification-result.v9", "status": "NEUTRAL_ONLY",
                                 "real_execution_authorized": False},
    }


def accounting(code_bytes, sizes, binding_bytes):
    amounts = dict.fromkeys(resources.CATEGORIES, 0)
    amounts.update(code=code_bytes, metadata=binding_bytes)
    for role, size in sizes.items():
        amounts[FILES[role][2]] += size
    # Reuse the established branch allocations; do not inherit V7's code limit.
    branches = old.accounting(0, sizes, binding_bytes)["reservations"]
    reservations = {name: resources.reserve(row["phase"], {**row["reserved"]["categories"], "code": code_bytes})
                    for name, row in branches.items()}
    return {"version": "s2uc.prestart-ledger.v9", "contract_id": resources.CONTRACT_ID, "stage": "prestart",
            "actual": resources.account("failure_before_publication", amounts), "reservations": reservations}


def validate(path):
    path = Path(path)
    _need(path.name == FILENAME, "V9_BINDING_PATH_INVALID")
    ref, data, identity = discovery.read_file(path.parent, FILENAME)
    value = old._json(data)
    _need(set(value) == {"version", "contract_id", "run_id", "output", "authorization", "artifacts"}
          and value["version"] == VERSION and value["contract_id"] == resources.CONTRACT_ID, "V9_BINDING_INVALID")
    _need(_same_typed(value["authorization"], {"kind": "ONE_NEUTRAL_EXECUTION", "max_uses": 1,
                                            "payload": "SYNTHETIC_NONZERO_F32LE", "real_sources": False}), "V9_AUTHORIZATION_INVALID")
    _need(type(value["run_id"]) is str and re.fullmatch(r"S2UC-V9-NEUTRAL-[a-f0-9]{32}", value["run_id"]), "V9_RUN_ID_INVALID")
    _need(type(value["output"]) is str, "V9_OUTPUT_INVALID")
    output = Path(value["output"])
    _need(output.is_absolute() and output.resolve().as_posix() == value["output"]
          and output.name == value["run_id"] and output.parent.is_dir()
          and not output.is_relative_to(path.parent.resolve())
          and not path.parent.resolve().is_relative_to(output), "V9_OUTPUT_INVALID")
    refs = value["artifacts"]
    _need(type(refs) is dict and set(refs) == set(FILES), "V9_REQUIRED_ARTIFACTS_INVALID")
    expected_names = {r[1] for r in FILES.values() if r[0] == "bundle"} | {FILENAME}
    _need({p.name for p in path.parent.iterdir()} == expected_names, "V9_UNREGISTERED_ARTIFACT")
    inv = current()
    _need(inv["code_bytes"] <= resources.LIMITS["code"], "V9_CODE_BUDGET_EXCEEDED")
    identities = {identity}
    for item in inv["files"]:
        stat = (discovery.ROOT / item["path"]).stat()
        identities.add((stat.st_dev, stat.st_ino))
    measured, loaded = {}, {}
    for role, (namespace, name, category, limit) in FILES.items():
        root = discovery.ROOT if namespace == "project" else path.parent
        actual, content, identity = discovery.read_file(root, name)
        _need(identity not in identities, "V9_FILE_ALIAS")
        identities.add(identity)
        expected = {**actual, "namespace": namespace, "category": category}
        _need(_same_typed(refs[role], expected), "V9_ARTIFACT_MISMATCH")
        _need(0 < actual["bytes"] <= limit, "V9_ARTIFACT_BUDGET_EXCEEDED")
        measured[role], loaded[role] = expected, old._json(content)
    _need(measured["nu_plan"]["sha256"] == old.science_manifest.SOURCE_PLAN_SHA256, "V9_NU_PLAN_CHANGED")
    expected = {"resource_contract": contract(), "inventory": inv, "manifest": manifest(),
                "source_binding": sources(), **evidence(inv)}
    for role, content in expected.items():
        _need(_same_typed(loaded[role], content), "V9_CONTENT_MISMATCH:" + role)
    budget = accounting(inv["code_bytes"], {k: v["bytes"] for k, v in measured.items()}, len(data))
    _need(_same_typed(loaded["resource_ledger"], budget), "V9_LEDGER_MISMATCH")
    _need(budget["actual"]["within_limits"] and all(r["reserved"]["within_limits"] for r in budget["reservations"].values()),
          "V9_BUDGET_EXCEEDED")
    return {"binding": ref, "inventory": inv, "prestart_artifacts": measured, "budget": budget,
            "manifest": loaded["manifest"], "sources": loaded["source_binding"], "run_id": value["run_id"],
            "output": value["output"], "scope": "NEUTRAL_ONLY", "real_execution_authorized": False}
