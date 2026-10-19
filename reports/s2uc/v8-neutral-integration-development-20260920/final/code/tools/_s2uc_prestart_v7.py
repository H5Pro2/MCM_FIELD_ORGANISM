"""V7 structural prestart validation only; never an execution authorization.

The fixed contract, not the submitted inventory, selects files and accounts.
Result artifacts are absent prestart and appear only in future reservations.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path
from types import MappingProxyType

from tools import _s2uc_inventory_v7 as inventory
from tools import _s2uc_resource_contract_v7 as ledger
from tools import _s2uc_run_binding as science_binding
from tools import _s2uc_source_binding as science_manifest

VERSION = "s2uc.prestart-binding.v7"
STOP = "V7_EXECUTION_NOT_CONNECTED: V7-Ausführung noch nicht angebunden"
FILENAME = "prestart-binding.json"
NU_PLAN = "reports/s2nu/s2nu-source-preseal-20260909-01/execution-plan.json"
# role -> (namespace, exact path, account, individual plan ceiling)
FILES = MappingProxyType({
    "manifest": ("bundle", "manifest.json", "metadata", 65_536),
    "nu_plan": ("project", NU_PLAN, "static_shared", 65_536),
    "source_binding": ("bundle", "source-binding.json", "static_shared", 24_576),
    "inventory": ("bundle", "dependency-inventory.json", "static_shared", 16_384),
    "qualification_summary": ("bundle", "qualification-summary.json", "static_shared", 16_384),
    "qualification_protocol": ("bundle", "qualification-protocol.json", "static_shared", 32_768),
    "qualification_budget": ("bundle", "qualification-budget.json", "static_shared", 8_192),
    "qualification_result": ("bundle", "qualification-result.json", "static_shared", 4_096),
    "resource_ledger": ("bundle", "resource-ledger.json", "static_shared", 8_192),
    "resource_contract": ("bundle", "resource-contract.json", "static_shared", 8_192),
})
RESULT_FILES = MappingProxyType({"record.json": "record", "verification.json": "verification",
                                "error.json": "error", "terminal.json": "terminal",
                                "terminal-minimal.json": "minimal", "publication.tmp": "staging"})


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            ledger._need(key not in result, "V7_DUPLICATE_JSON_KEY")
            result[key] = value
        return result
    value = json.loads(data, object_pairs_hook=pairs)
    ledger._need(type(value) is dict, "V7_OBJECT_INVALID")
    return value


def contract():
    return {"contract_id": ledger.CONTRACT_ID, "binding_version": VERSION,
            "limits": dict(ledger.LIMITS), "reserves": dict(ledger.RESERVES),
            "entries": list(inventory.ENTRIES),
            "prestart_files": {key: dict(namespace=ns, path=path, category=cat, limit=limit)
                               for key, (ns, path, cat, limit) in FILES.items()},
            "binding": {"path": FILENAME, "category": "metadata"},
            "result_files": dict(RESULT_FILES), "execution": "NOT_CONNECTED"}


def accounting(code_bytes, file_sizes, binding_bytes):
    """Recomputed real input bytes + separate prospective closure allocations."""
    amounts = dict.fromkeys(ledger.CATEGORIES, 0)
    amounts["code"] = code_bytes
    amounts["metadata"] = binding_bytes
    for role, size in file_sizes.items():
        amounts[FILES[role][2]] += size
    actual = ledger._account("failure_before_publication", amounts)
    alternatives = {}
    for name, phase, result in (
        ("success", "success", dict(record=245760, verification=131072, terminal=16384)),
        ("failure_before_publication", "failure_before_publication", dict(error=16384, terminal=16384)),
        ("failure_after_publication", "failure_after_publication",
         dict(record=245760, verification=131072, error=16384, terminal=16384)),
        ("minimal_with_terminal", "failure_after_publication",
         dict(record=245760, verification=131072, error=16384, terminal=16384, minimal=16384)),
    ):
        alternatives[name] = ledger.reserve(phase, {**amounts, **result, "staging": ledger.LIMITS["staging"]})
    return {"version": "s2uc.prestart-ledger.v7", "contract_id": ledger.CONTRACT_ID,
            "stage": "prestart", "actual": actual, "reservations": alternatives}


def test_ids(root):
    ids = []
    for name in inventory.TESTS:
        _, data, _ = inventory.read_file(root, name)
        module = name[:-3].replace("/", ".")
        for cls in ast.parse(data).body:
            if isinstance(cls, ast.ClassDef):
                ids.extend(f"{module}.{cls.name}.{node.name}" for node in cls.body
                           if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"))
    return sorted(ids)


def evidence_expected(current, ids, kind):
    """A binding of evidence claims, not proof that a qualification occurred."""
    common = {"contract_id": ledger.CONTRACT_ID, "evidence_kind": kind,
              "inventory_sha256": inventory.sha(canonical(current))}
    return {
        "qualification_summary": {**common, "version": "s2uc.qualification-summary.v7",
                                  "result": "OK", "tests_run": len(ids), "real_payloads_opened": False},
        "qualification_protocol": {**common, "version": "s2uc.qualification-protocol.v7",
                                   "result": "OK", "test_ids": ids},
        "qualification_budget": {**common, "version": "s2uc.qualification-budget.v7",
                                 "code_bytes": current["code_bytes"], "code_limit": ledger.LIMITS["code"]},
        "qualification_result": {**common, "version": "s2uc.qualification-result.v7",
                                 "status": "STRUCTURAL_EVIDENCE_ONLY", "execution_authorized": False},
    }


def validate(path, *, project_root=inventory.ROOT):
    """Read-only isolated validator. Never opens gate, supplier, output or PCM.

    Synthetic evidence may pass only this structural level. The real starter
    always raises STOP, even for a completely matching report from here.
    """
    path = Path(path)
    ledger._need(path.name == FILENAME, "V7_BINDING_PATH_INVALID")
    bundle = path.parent
    binding_ref, data, binding_identity = inventory.read_file(bundle, FILENAME)
    value = _json(data)
    ledger._need(set(value) == {"version", "contract_id", "stage", "evidence_kind", "artifacts"}
                 and value["version"] == VERSION and value["contract_id"] == ledger.CONTRACT_ID
                 and value["stage"] == "prestart"
                 and value["evidence_kind"] in ("synthetic-development", "development"), "V7_BINDING_INVALID")
    refs = value["artifacts"]
    ledger._need(type(refs) is dict and set(refs) == set(FILES), "V7_REQUIRED_ARTIFACTS_INVALID")
    expected_names = {spec[1] for spec in FILES.values() if spec[0] == "bundle"} | {FILENAME}
    ledger._need({p.name for p in bundle.iterdir()} == expected_names, "V7_UNREGISTERED_ARTIFACT")
    current = inventory.current(project_root)
    ledger._need(current["code_bytes"] <= ledger.LIMITS["code"], "V7_CODE_BUDGET_EXCEEDED")
    identities = {binding_identity}
    for row in current["files"]:
        identity = (Path(project_root) / row["path"]).stat()
        identities.add((identity.st_dev, identity.st_ino))
    measured = {}
    loaded = {}
    for role, (namespace, name, category, limit) in FILES.items():
        root = project_root if namespace == "project" else bundle
        ref, content, identity = inventory.read_file(root, name)
        ledger._need(identity not in identities, "V7_FILE_ALIAS")
        identities.add(identity)
        expected = {**ref, "namespace": namespace, "category": category}
        ledger._need(ledger._same_typed(refs[role], expected), "V7_ARTIFACT_MISMATCH")
        ledger._need(0 < ref["bytes"] <= limit, "V7_ARTIFACT_BUDGET_EXCEEDED")
        measured[role] = expected
        loaded[role] = _json(content)
    ledger._need(measured["nu_plan"]["sha256"] == science_manifest.SOURCE_PLAN_SHA256, "V7_NU_PLAN_CHANGED")
    ledger._need(ledger._same_typed(loaded["resource_contract"], contract()), "V7_CONTRACT_MISMATCH")
    ledger._need(ledger._same_typed(loaded["inventory"], current), "V7_INVENTORY_MISMATCH")
    # Unchanged scientific binding; no new final run identity is generated here.
    science_binding.validate(loaded["source_binding"])
    ledger._need(ledger._same_typed(loaded["manifest"], science_manifest.manifest()), "V7_MANIFEST_MISMATCH")
    for role, expected in evidence_expected(current, test_ids(project_root), value["evidence_kind"]).items():
        ledger._need(ledger._same_typed(loaded[role], expected), "V7_EVIDENCE_MISMATCH")
    budget = accounting(current["code_bytes"], {role: ref["bytes"] for role, ref in measured.items()}, len(data))
    ledger._need(ledger._same_typed(loaded["resource_ledger"], budget), "V7_PRESTART_LEDGER_MISMATCH")
    ledger._need(budget["actual"]["within_limits"] and
                 all(row["reserved"]["within_limits"] for row in budget["reservations"].values()),
                 "V7_BUDGET_EXCEEDED")
    return {"status": "V7_PRESTART_STRUCTURALLY_VALID", "execution_status": STOP,
            "execution_authorized": False, "binding": binding_ref, "inventory": current,
            "prestart_artifacts": measured, "budget": budget,
            "result_inventory": [], "process_memory": "UNMEASURED"}
