"""Read bounded neutral evidence; consistent fixture claims never grant authority."""
from pathlib import Path
from tools import _s2uc_source_execution_binding as binding
from tools._s2uc_resource_contract_v7 import _need, _same_typed


def read(path):
    path = Path(path)
    summary, data, _ = binding.discovery.read_file(path.parent, path.name)
    _need(summary["bytes"] <= binding.FILES["qualification_summary"][3], "V9_QUALIFICATION_SUMMARY_BUDGET")
    value = binding.old._json(data)
    ids = binding.test_ids()
    _need(set(value) == {"version", "scope", "inventory_sha256", "test_ids_sha256", "log", "inventory",
                         "tests_run", "exit_code", "real_execution_authorized", "formal_qualification"},
          "V9_QUALIFICATION_SCHEMA_INVALID")
    _need(value["version"] == "s2uc.executed-neutral-summary.v9"
          and value["scope"] == "EXECUTED_NEUTRAL_DEVELOPMENT"
          and value["formal_qualification"] is False and value["real_execution_authorized"] is False,
          "V9_QUALIFICATION_SCOPE_INVALID")
    inv = binding.current()
    _need(value["inventory_sha256"] == binding.discovery.sha(binding.old.canonical(inv)),
          "V9_QUALIFICATION_STALE_CODE_OR_RUNTIME")
    _need(value["test_ids_sha256"] == binding.discovery.sha(binding.old.canonical(ids))
          and type(value["tests_run"]) is int and value["tests_run"] == len(ids)
          and type(value["exit_code"]) is int and value["exit_code"] == 0, "V9_QUALIFICATION_TESTS_INVALID")
    refs = [summary]
    loaded = {}
    for key, filename, ceiling in (("log", "tests.log", binding.FILES["qualification_protocol"][3]),
                                  ("inventory", "dependency-inventory.json", binding.FILES["inventory"][3])):
        _need(type(value[key]) is dict and value[key].get("path") == filename, "V9_QUALIFICATION_PATH_INVALID")
        ref, content, _ = binding.discovery.read_file(path.parent, filename)
        _need(_same_typed(ref, value[key]) and ref["bytes"] <= ceiling, "V9_QUALIFICATION_ARTIFACT_INVALID")
        refs.append(ref)
        loaded[key] = content
    _need(loaded["inventory"] == binding.old.canonical(inv), "V9_QUALIFICATION_INVENTORY_CHANGED")
    _need(loaded["log"] == "".join(name + " PASS\n" for name in ids).encode(), "V9_QUALIFICATION_LOG_INCOMPLETE")
    return {"status": "NEUTRAL_EVIDENCE_CONSISTENT", "real_execution_authorized": False,
            "independent_acceptance": "OPEN", "tests_run": len(ids), "code_bytes": inv["code_bytes"],
            "artifacts": refs, "inventory_sha256": value["inventory_sha256"]}
