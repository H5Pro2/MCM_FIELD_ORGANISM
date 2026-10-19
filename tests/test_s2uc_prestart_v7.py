"""Synthetic structural evidence only; never a formal qualification or run."""
import copy
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tools import _s2uc_inventory_v7 as inventory
from tools import _s2uc_prestart_v7 as prestart
from tools import _s2uc_resource_contract_v7 as ledger
from tools import _s2uc_run_binding as legacy
from tools import _s2uc_run_entry as entry
from tools import s2uc_run_bound_once as starter


def write(root, name, value):
    (root / name).write_bytes(prestart.canonical(value))


def seal(bundle, project, current):
    """Test-only finite size fixed point. No production binding writer exists."""
    path = bundle / prestart.FILENAME
    if not path.exists():
        path.write_bytes(b"{}")
    ledger_path = bundle / "resource-ledger.json"
    if not ledger_path.exists():
        ledger_path.write_bytes(b"{}")
    for _ in range(16):
        refs = {}
        for role, (ns, name, category, _) in prestart.FILES.items():
            ref, _, _ = inventory.read_file(project if ns == "project" else bundle, name)
            refs[role] = {**ref, "namespace": ns, "category": category}
        value = {"version": prestart.VERSION, "contract_id": ledger.CONTRACT_ID,
                 "stage": "prestart", "evidence_kind": "synthetic-development", "artifacts": refs}
        data = prestart.canonical(value)
        path.write_bytes(data)
        budget = prestart.accounting(current["code_bytes"], {k: v["bytes"] for k, v in refs.items()}, len(data))
        encoded = prestart.canonical(budget)
        if ledger_path.read_bytes() == encoded:
            return path
        ledger_path.write_bytes(encoded)
    raise AssertionError("test fixture fixed point did not converge")


def fixture(bundle, project=inventory.ROOT, current=None):
    bundle.mkdir()
    current = current or inventory.current(project)
    write(bundle, "dependency-inventory.json", current)
    write(bundle, "resource-contract.json", prestart.contract())
    write(bundle, "manifest.json", prestart.science_manifest.manifest())
    write(bundle, "source-binding.json", legacy.build())
    for role, value in prestart.evidence_expected(current, prestart.test_ids(project), "synthetic-development").items():
        write(bundle, prestart.FILES[role][1], value)
    return seal(bundle, project, current), current


class V7PrestartTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.current = inventory.current()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path, _ = fixture(self.root / "bundle", current=self.current)
        self.bundle = self.path.parent
        entry.MAIN_GATE = False
        entry.USED = False

    def replace(self, role, mutate, *, reseal=True, project=inventory.ROOT, current=None):
        path = self.bundle / prestart.FILES[role][1]
        value = json.loads(path.read_bytes())
        mutate(value)
        path.write_bytes(prestart.canonical(value))
        if reseal:
            seal(self.bundle, project, current or self.current)

    def rejects(self, error, project=inventory.ROOT):
        with self.assertRaisesRegex(ValueError, error):
            prestart.validate(self.path, project_root=project)

    def clone(self):
        root = self.root / "project"
        for name in [r["path"] for r in self.current["files"]] + [prestart.NU_PLAN]:
            dest = root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(inventory.ROOT / name, dest)
        return root

    def test_complete_union_includes_bound_tests_packages_and_actual_sizes(self):
        result = prestart.validate(self.path)
        self.assertFalse(result["execution_authorized"])
        self.assertEqual(result["result_inventory"], [])
        rows = result["inventory"]["files"]
        names = {r["path"] for r in rows}
        self.assertTrue(set(inventory.ENTRIES) <= names)
        self.assertTrue({"tests/__init__.py", "mcm_field_organism/__init__.py",
                         "tools/_s2uc_prestart_v7.py", "tools/_s2nu_private_source_binding.py"} <= names)
        self.assertEqual(len(names), len(rows))
        self.assertEqual(sum((inventory.ROOT / r["path"]).stat().st_size for r in rows), result["inventory"]["code_bytes"])
        actual = result["budget"]["actual"]
        self.assertEqual(actual["total_bytes"], sum(r["bytes"] for r in rows) +
                         sum(r["bytes"] for r in result["prestart_artifacts"].values()) + self.path.stat().st_size)
        for category in ("record", "verification", "error", "terminal", "minimal", "staging"):
            self.assertEqual(actual["categories"][category], 0)
        self.assertEqual(result["prestart_artifacts"]["nu_plan"]["bytes"], (inventory.ROOT / prestart.NU_PLAN).stat().st_size)
        self.assertGreater(result["prestart_artifacts"]["resource_contract"]["bytes"], 0)
        reserved = result["budget"]["reservations"]["minimal_with_terminal"]["reserved"]["categories"]
        self.assertEqual((reserved["record"], reserved["verification"], reserved["terminal"], reserved["minimal"]),
                         (245760, 131072, 16384, 16384))

    def test_missing_transitive_test_dependency_with_consistent_digests_fails(self):
        project = self.clone()
        test = project / inventory.TESTS[-1]
        with test.open("a") as stream:
            stream.write("\ndef delayed_test_import():\n    from tests import v7_helper\n")
        (project / "tests/v7_helper.py").write_text("from . import v7_leaf\n")
        (project / "tests/v7_leaf.py").write_text("VALUE = 1\n")
        complete = inventory.current(project)
        names = {r["path"] for r in complete["files"]}
        self.assertTrue({"tests/v7_helper.py", "tests/v7_leaf.py"} <= names)
        shutil.rmtree(self.bundle)
        self.path, _ = fixture(self.bundle, project, complete)
        prestart.validate(self.path, project_root=project)
        forged = copy.deepcopy(complete)
        forged["files"] = [r for r in forged["files"] if r["path"] != "tests/v7_leaf.py"]
        forged["code_bytes"] = sum(r["bytes"] for r in forged["files"])
        write(self.bundle, "dependency-inventory.json", forged)
        for role, value in prestart.evidence_expected(forged, prestart.test_ids(project), "synthetic-development").items():
            write(self.bundle, prestart.FILES[role][1], value)
        seal(self.bundle, project, forged)
        self.rejects("V7_INVENTORY_MISMATCH", project)
        # A missing physical module must not disappear from discovery either.
        (project / "tests/v7_leaf.py").unlink()
        self.rejects("V7_PROJECT_IMPORT_MISSING", project)
        (project / "tests/v7_helper.py").write_text(
            'from importlib import import_module as load\nload("tests.v7_leaf")\n')
        self.rejects("V7_PROJECT_IMPORT_MISSING", project)

    def test_changed_source_hash_and_consistent_undercount_are_rejected(self):
        original = copy.deepcopy(self.current)
        for mode in ("hash", "size", "category", "duplicate", "missing", "extra", "path", "boolean"):
            with self.subTest(mode=mode):
                forged = copy.deepcopy(original)
                row = next(r for r in forged["files"] if r["bytes"] > 1)
                if mode == "hash": row["sha256"] = "0" * 64
                if mode == "size": row["bytes"] -= 1
                if mode == "category": row["category"] = "static_shared"
                if mode == "duplicate": forged["files"].append(copy.deepcopy(row))
                if mode == "missing": forged["files"].remove(row)
                if mode == "extra": forged["files"].append({**row, "path": "tools/not-required.py"})
                if mode == "path": row["path"] = "./" + row["path"]
                if mode == "boolean": row["bytes"] = True
                forged["code_bytes"] = sum(r["bytes"] for r in forged["files"])
                write(self.bundle, "dependency-inventory.json", forged)
                seal(self.bundle, inventory.ROOT, forged)
                self.rejects("V7_INVENTORY_MISMATCH")

    def test_external_identity_and_bound_entry_set_cannot_be_forged(self):
        for mutate in (lambda x: x["external"]["interpreter"].update(sha256="0" * 64),
                       lambda x: x["external"]["modules"][0].update(version="forged"),
                       lambda x: x["external"]["distributions"][0].update(files_sha256="0" * 64),
                       lambda x: x["entries"].pop()):
            write(self.bundle, "dependency-inventory.json", self.current)
            self.replace("inventory", mutate)
            self.rejects("V7_INVENTORY_MISMATCH")
        external = self.current["external"]
        self.assertGreater(external["distributions"][0]["installed_bytes"], 0)
        self.assertGreater(external["distributions"][0]["files"], 0)

    def test_external_installation_hash_measures_bytes_despite_unchanged_version(self):
        installed = self.root / "installed"
        installed.mkdir()
        (installed / "module.py").write_bytes(b"a=1\n")
        (installed / "RECORD").write_bytes(b"unchanged manifest")
        dist = SimpleNamespace(files=[Path("module.py"), Path("RECORD")], version="1.0",
                               metadata={"Name": "neutral"}, locate_file=lambda name: installed / name)
        with patch.object(inventory.metadata, "distribution", return_value=dist):
            before = inventory.runtime_identity([{"module": "neutral", "kind": "third-party", "version": "1.0"}])
            (installed / "module.py").write_bytes(b"a=2\n")
            after = inventory.runtime_identity([{"module": "neutral", "kind": "third-party", "version": "1.0"}])
        self.assertEqual(before["distributions"][0]["installed_bytes"], after["distributions"][0]["installed_bytes"])
        self.assertNotEqual(before["distributions"][0]["files_sha256"], after["distributions"][0]["files_sha256"])

    def test_disk_change_after_binding_is_rejected(self):
        project = self.clone()
        target = project / "tests/test_s2ub_candidate_confirmation.py"
        target.write_bytes(target.read_bytes() + b"\n# changed after binding\n")
        self.rejects("V7_INVENTORY_MISMATCH", project)
        with (self.bundle / "qualification-summary.json").open("ab") as stream:
            stream.write(b" ")
        self.rejects("V7_ARTIFACT_MISMATCH")

    def test_missing_unknown_and_unregistered_static_evidence_fail(self):
        original = self.path.read_bytes()
        for mode in ("missing", "unknown"):
            value = json.loads(original)
            if mode == "missing": value["artifacts"].pop("nu_plan")
            else: value["artifacts"]["unknown_evidence"] = value["artifacts"]["nu_plan"]
            self.path.write_bytes(prestart.canonical(value))
            self.rejects("V7_REQUIRED_ARTIFACTS_INVALID")
        self.path.write_bytes(original)
        for name in ("sidecar.json", "record.json", "terminal.json", "publication.tmp"):
            (self.bundle / name).write_bytes(b"")
            self.rejects("V7_UNREGISTERED_ARTIFACT")
            (self.bundle / name).unlink()
        (self.bundle / "resource-contract.json").unlink()
        self.rejects("V7_UNREGISTERED_ARTIFACT")

    def test_roles_paths_categories_and_contract_are_not_binding_controlled(self):
        original = self.path.read_bytes()
        for key, replacement in (("category", "code"), ("namespace", "project"),
                                  ("path", "../manifest.json"), ("path", "Manifest.json")):
            value = json.loads(original)
            value["artifacts"]["manifest"][key] = replacement
            self.path.write_bytes(prestart.canonical(value))
            self.rejects("V7_ARTIFACT_MISMATCH")
        self.path.write_bytes(original)
        self.replace("resource_contract", lambda c: c["limits"].update(code=999999))
        self.rejects("V7_CONTRACT_MISMATCH")

    def test_reservation_and_actual_inventories_cannot_be_mixed(self):
        self.replace("resource_ledger", lambda x: x["actual"]["categories"].update(record=245760), reseal=False)
        # Refresh only the reference; a full reseal would repair the attacked ledger.
        value = json.loads(self.path.read_bytes())
        ref, _, _ = inventory.read_file(self.bundle, "resource-ledger.json")
        value["artifacts"]["resource_ledger"].update(ref)
        self.path.write_bytes(prestart.canonical(value))
        self.rejects("V7_PRESTART_LEDGER_MISMATCH")

    def test_true_code_budget_exact_and_plus_one_use_disk_bytes(self):
        project = self.clone()
        target = project / "tests/test_s2ub_candidate_confirmation.py"
        target.write_bytes(target.read_bytes() + b"\n#" + b"x" * (ledger.LIMITS["code"] - self.current["code_bytes"] - 2))
        exact = inventory.current(project)
        self.assertEqual(exact["code_bytes"], ledger.LIMITS["code"])
        shutil.rmtree(self.bundle)
        self.path, _ = fixture(self.bundle, project, exact)
        prestart.validate(self.path, project_root=project)
        with target.open("ab") as stream: stream.write(b"x")
        self.rejects("V7_CODE_BUDGET_EXCEEDED", project)

    def test_static_subcap_and_metadata_combined_cap_use_real_bytes(self):
        target = self.bundle / "qualification-summary.json"
        data = target.read_bytes()
        target.write_bytes(data + b" " * (16385 - len(data)))
        seal(self.bundle, inventory.ROOT, self.current)
        self.rejects("V7_ARTIFACT_BUDGET_EXCEEDED")
        target.write_bytes(data)
        manifest = self.bundle / "manifest.json"
        data = manifest.read_bytes()
        manifest.write_bytes(data + b" " * (65536 - len(data)))
        seal(self.bundle, inventory.ROOT, self.current)
        self.rejects("V7_BUDGET_EXCEEDED")

    def test_v6_v7_mixing_fails_in_both_directions(self):
        original = self.path.read_bytes()
        value = json.loads(original); value["version"] = "s2uc.final-run-binding.v6"
        self.path.write_bytes(prestart.canonical(value))
        self.rejects("V7_BINDING_INVALID")
        with self.assertRaisesRegex(ValueError, "V7_BINDING_INVALID"):
            starter.start(self.root / "out", authorize=True, binding_file=self.path)
        self.path.write_bytes(original)
        with self.assertRaisesRegex(ValueError, "RUN_BINDING_INVALID"):
            legacy.load(self.path)
        self.replace("resource_contract", lambda x: x.update(contract_id="s2uc.resources.v6"))
        self.rejects("V7_CONTRACT_MISMATCH")

    def test_starter_always_stops_valid_v7_before_supplier_adapter_gate_and_output(self):
        output = self.root / "never-created"
        calls = [0]
        def supplier(_): calls[0] += 1
        entry.MAIN_GATE = True  # Also close any stale gate before admission.
        with patch.object(entry, "run_bound_once", wraps=entry.run_bound_once) as execute, \
             patch.object(starter.adapter, "SourceAdapter", wraps=starter.adapter.SourceAdapter) as adapter, \
             patch.object(starter.manifest_binding, "manifest", wraps=starter.manifest_binding.manifest) as manifest:
            with self.assertRaisesRegex(ValueError, "V7_EXECUTION_NOT_CONNECTED"):
                starter.start(output, supplier, authorize=True, binding_file=self.path)
            execute.assert_not_called()
            adapter.assert_not_called()
            # The manifest may be read by validation; no execution follows.
        self.assertEqual(calls[0], 0)
        self.assertFalse(entry.MAIN_GATE)
        self.assertFalse(entry.USED)
        self.assertFalse(output.exists())
        self.assertEqual(prestart.validate(self.path)["execution_status"], prestart.STOP)

    def test_invalid_v7_starter_also_keeps_supplier_zero_gate_closed_and_output_absent(self):
        self.replace("inventory", lambda x: x["files"].pop())
        output = self.root / "never-created"
        calls = [0]
        with self.assertRaisesRegex(ValueError, "V7_INVENTORY_MISMATCH"):
            starter.start(output, lambda _: calls.__setitem__(0, calls[0] + 1), authorize=True, binding_file=self.path)
        self.assertEqual(calls[0], 0)
        self.assertFalse(entry.MAIN_GATE)
        self.assertFalse(output.exists())

    def test_duplicate_json_keys_and_evidence_claims_rejected(self):
        original = self.path.read_bytes()
        self.path.write_bytes(b'{"version":"ignored",' + original[1:])
        self.rejects("V7_DUPLICATE_JSON_KEY")
        self.path.write_bytes(original)
        self.replace("qualification_protocol", lambda x: x["test_ids"].pop())
        self.rejects("V7_EVIDENCE_MISMATCH")

    def test_project_hardlink_and_noncanonical_path_rejected(self):
        project = self.clone()
        target = project / "tests/test_s2uc_resource_contract_v7.py"
        target.unlink()
        os.link(project / "tests/test_s2ub_candidate_confirmation.py", target)
        with self.assertRaisesRegex(ValueError, "V7_FILE_ALIAS"):
            inventory.current(project)
        for name in ("../outside", "./tools/s2uc_run_bound_once.py", "tools\\s2uc_run_bound_once.py",
                     "C:drive-relative", "/absolute", "tools/S2uc_run_bound_once.py"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                inventory.read_file(inventory.ROOT, name)


if __name__ == "__main__":
    unittest.main()
