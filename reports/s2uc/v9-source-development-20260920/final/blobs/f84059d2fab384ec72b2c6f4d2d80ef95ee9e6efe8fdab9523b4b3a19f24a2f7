import copy
import hashlib
import json
import math
import struct
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from tools import _s2ty_audio_materialization as materialization
from tools import _s2ub_candidate_confirmation as ub
from tools import _s2uc_neutral_connection as connection
from tools import _s2uc_record_codec as codec
from tools import _s2uc_resource_ledger as ledger
from tools import _s2uc_run_entry as entry
from tools import _s2uc_source_binding as binding
from tools import _s2uc_verification as verification
from tools import _s2uc_evaluation as evaluation
from tools import _s2uc_run_binding as run_binding
from tools import _s2uc_source_adapter as source_adapter
from tools import _s2tu_retained_trace as tu
from tools import s2uc_run_bound_once as starter


PAYLOAD = bytes(4_800 * 4)
PAYLOAD_HASH = hashlib.sha256(PAYLOAD).hexdigest()

def neutral_manifest():
    value = copy.deepcopy(binding.manifest())
    for event in value["events"]:
        if "endpoint" in event:
            event["endpoint"]["pcm_sha256"] = PAYLOAD_HASH
    bare = {key: item for key, item in value.items() if key not in {"binding_digest", "binding_bytes"}}
    value["binding_digest"] = binding.digest(bare)
    value["binding_bytes"] = len(binding.canonical(bare))
    binding.validate(value)
    return value

def adapter(counters, *, fail_call=None):
    calls = [0]
    def materialize(endpoint):
        calls[0] += 1
        if calls[0] == fail_call:
            raise connection.S2UCConnectionError("NEUTRAL_MATERIALIZATION_FAILURE")
        return materialization.materialize(endpoint, PAYLOAD, counters=counters)
    return materialize, calls


class S2UCMaterializationConnectionTests(unittest.TestCase):
    def setUp(self):
        entry.MAIN_GATE = False
        entry.USED = False

    def test_static_run_binding_covers_sources_uses_and_all_expectations(self):
        value = run_binding.build()
        run_binding.validate(value)
        self.assertEqual((len(value["sources"]), len(value["endpoint_uses"]), set(value["targets"])),
                         (5, 58, {"g1/12", "g1/24", "g1/26", "g2/38", "g3/60", "g3/67", "g3/69"}))
        self.assertEqual((value["targets"]["g1/24"], value["targets"]["g3/69"]),
                         ({"target": "A", "formations": ["g1-p1", "g1-p2"]}, {"target": "B", "formations": ["g3-p3", "g3-p4"]}))
        changed = copy.deepcopy(value); changed["endpoint_uses"][0]["pcm_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "RUN_BINDING_INVALID"):
            run_binding.validate(changed)
        entry.MAIN_GATE = True
        with self.assertRaisesRegex(ValueError, "RUN_BOUNDARY_INVALID"):
            entry.run_bound_once(value, neutral_manifest(), lambda _: None, "wrong-output")
        entry.MAIN_GATE = False

    def test_prepared_run_identity_is_accepted_and_unknown_identity_is_rejected(self):
        prepared = run_binding.build(run_id=run_binding.PREPARED_RUN_ID, output=run_binding.PREPARED_OUTPUT)
        run_binding.validate(prepared)
        unknown = copy.deepcopy(prepared); unknown["run_id"] = "s2uc-source-comparison-real-unknown"
        with self.assertRaisesRegex(ValueError, "RUN_IDENTITY_INVALID"):
            run_binding.validate(unknown)

    def _v6_neutral_fixture(self, root, *, undercount_dependency=False, mutate_budget=None, mutate_qualification=None,
                            admission_claim=False, complete_dependencies=False):
        source_path = root / "source.json"; source_path.write_bytes(binding.canonical(run_binding.build(run_id=run_binding.PREPARED_RUN_ID, output=run_binding.PREPARED_OUTPUT)))
        dependencies = [run_binding.reference(Path("tools/_s2uc_run_binding.py")), run_binding.reference(Path("tests/test_s2uc_materialization_connection.py"))]
        if complete_dependencies:
            dependencies = run_binding.dependency_inventory.current()["files"]
        inventory_path = root / "inventory.json"
        inventory_path.write_text(json.dumps({"version": "s2uc.dependency-inventory.v6", "source": "neutral test fixture",
                                              "external": run_binding.dependency_inventory.current()["external"] if admission_claim else [],
                                              "files": [{**item, "role": "runtime"} for item in dependencies]}), encoding="utf-8")
        def alternatives(metadata, shared):
            result = {}
            for name in ("success", "failure", "minimal"):
                c = {"metadata": metadata, "shared": shared,
                     "record": ledger.RESERVES["success_record" if name == "success" else "failure_record"],
                     "verification": 0 if name == "minimal" else ledger.RESERVES["verification"]}
                violations = [key for key, size in c.items() if size > ledger.LIMITS[key]]
                if sum(c.values()) > ledger.LIMITS["total"]:
                    violations.append("total")
                result[name] = {"contributions": c, "total_bytes": sum(c.values()), "violations": violations}
            return result

        summary_path = root / "summary.json"
        protocol_path = root / "protocol.json"
        qualification_budget_path = root / "qualification-budget.json"
        qualification_path = root / "qualification.json"
        files = {str(Path(item["path"]).resolve()): item for item in dependencies}
        for filename in ("tests/test_s2uc_neutral_connection.py", "tests/test_s2uc_materialization_connection.py"):
            files[str(Path(filename).resolve())] = run_binding.reference(filename)
        # Explicitly synthetic evidence, never a formal qualification result.
        test_ids = sorted(unittest.defaultTestLoader.getTestCaseNames(S2UCMaterializationConnectionTests))
        from tests.test_s2uc_neutral_connection import S2UCNeutralConnectionTests
        ids = sorted([f"tests.test_s2uc_materialization_connection.S2UCMaterializationConnectionTests.{name}" for name in test_ids]
                     + [f"tests.test_s2uc_neutral_connection.S2UCNeutralConnectionTests.{name}"
                        for name in unittest.defaultTestLoader.getTestCaseNames(S2UCNeutralConnectionTests)])
        # Negative admission fixtures deliberately forge a formal-looking claim.
        identifier = ("S2UC-CODEC-ERROR-NEUTRAL-QUALIFICATION-FORGED-TEST-CLAIM" if admission_claim
                      else "SYNTHETIC-TEST-DATA-NOT-A-QUALIFICATION")
        common = {"qualification_id": identifier,
                  "command": "python -m unittest -v tests.test_s2uc_neutral_connection tests.test_s2uc_materialization_connection",
                  "result": "OK", "tests_run": len(ids), "files": copy.deepcopy(list(files.values()))}
        summary = {**common, "version": "s2uc.codec-error-neutral-test.v2", "real_payloads_opened": False,
                   "scope": ["Forged claim for negative admission test" if admission_claim
                             else "SYNTHETIC TEST DATA: structural validator fixture only"]}
        protocol = {**copy.deepcopy(common), "version": "s2uc.codec-error-neutral-protocol.v2",
                    "test_cases": ids, "summary_sha256": ""}
        if mutate_qualification:
            mutate_qualification("summary", summary)
        summary_path.write_bytes(binding.canonical(summary))
        protocol["summary_sha256"] = run_binding.reference(summary_path)["sha256"]
        if mutate_qualification:
            mutate_qualification("protocol", protocol)
        protocol_path.write_bytes(binding.canonical(protocol))
        metadata = [{"name": "manifest", "bytes": binding.manifest()["binding_bytes"]}]
        shared = [{"name": "active_dependency_sources", "bytes": sum(item["bytes"] for item in dependencies)},
                  {"name": "qualification_summary", "bytes": summary_path.stat().st_size},
                  {"name": "qualification_protocol", "bytes": protocol_path.stat().st_size},
                  {"name": "terminal_reserve", "bytes": ledger.RESERVES["terminal"]}]
        qualification_budget = {"version": "s2uc.qualification-budget.v1", "qualification_id": common["qualification_id"],
                                "limits": ledger.LIMITS, "reserves": ledger.RESERVES,
                                "metadata_items": metadata, "shared_items": shared,
                                "alternatives": alternatives(sum(x["bytes"] for x in metadata), sum(x["bytes"] for x in shared)),
                                "result": "EXCEEDS_LIMITS" if complete_dependencies else "WITHIN_LIMITS"}
        if mutate_qualification:
            mutate_qualification("budget", qualification_budget)
        qualification_budget_path.write_bytes(binding.canonical(qualification_budget))
        qualification_path.write_bytes(binding.canonical({"version": "s2uc.codec-error-qualification-result.v2",
                                                          "qualification_id": common["qualification_id"], "status": "QUALIFIED",
                                                          "test_summary": run_binding.reference(summary_path), "test_protocol": run_binding.reference(protocol_path),
                                                          "budget": run_binding.reference(qualification_budget_path), "gates": {"main_gate": False, "used": False},
                                                          "real_payloads_opened": False}))
        budget_path = root / "budget.json"
        budget_path.write_text("{}", encoding="utf-8")
        final_path = root / "final.json"
        # The ledger counts itself and the final binding at their actual sizes.
        # Rebuild references after each write until both sizes are stable.
        final_bytes = 0
        for _ in range(20):
            budget_bytes = budget_path.stat().st_size
            metadata_items = [
                {"name": "manifest", "bytes": binding.manifest()["binding_bytes"]},
                {"name": "final_binding_reserve", "bytes": final_bytes},
            ]
            shared_actual = {
                "active_dependency_sources": sum(item["bytes"] for item in dependencies),
                "frozen_source_binding": source_path.stat().st_size,
                "dependency_inventory": inventory_path.stat().st_size,
                "qualification_summary": summary_path.stat().st_size,
                "qualification_protocol": protocol_path.stat().st_size,
                "qualification_budget": qualification_budget_path.stat().st_size,
                "qualification_result": qualification_path.stat().st_size,
                "budget_ledger": budget_bytes,
            }
            if undercount_dependency:
                shared_actual["active_dependency_sources"] -= 1
            shared_items = [{"name": name, "bytes": size} for name, size in shared_actual.items()]
            shared_items.append({"name": "terminal_reserve", "bytes": ledger.RESERVES["terminal"]})
            alternatives = {}
            for name in ("success", "failure", "minimal"):
                contributions = {
                    "metadata": sum(item["bytes"] for item in metadata_items),
                    "shared": sum(item["bytes"] for item in shared_items),
                    "record": ledger.RESERVES["success_record" if name == "success" else "failure_record"],
                    "verification": 0 if name == "minimal" else ledger.RESERVES["verification"],
                }
                total = sum(contributions.values())
                if not complete_dependencies:
                    self.assertTrue(all(size <= ledger.LIMITS[key] for key, size in contributions.items()))
                self.assertLessEqual(total, ledger.LIMITS["total"])
                violations = [key for key, size in contributions.items() if size > ledger.LIMITS[key]]
                alternatives[name] = {"contributions": contributions, "total_bytes": total, "violations": violations}
            budget = {
                "version": "s2uc.closure-budget.v6",
                "method": "neutral fixture file sizes plus separate record, verification and terminal reserves",
                "limits": ledger.LIMITS, "reserves": ledger.RESERVES,
                "metadata_items": metadata_items, "shared_items": shared_items,
                "alternatives": alternatives, "structural_bound": "neutral fixture only",
                "result": "EXCEEDS_LIMITS" if complete_dependencies else "WITHIN_LIMITS",
            }
            if mutate_budget:
                mutate_budget(budget)
            budget_path.write_bytes(binding.canonical(budget))
            if final_path.exists():
                final_path.unlink()
            run_binding.final_binding_v6(final_path, source_binding_path=source_path, dependencies=dependencies, inventory_path=inventory_path,
                                         qualification_result=qualification_path, budget={"ledger": run_binding.reference(budget_path)},
                                         run_id=run_binding.PREPARED_RUN_ID, output=run_binding.PREPARED_OUTPUT)
            next_final_bytes = final_path.stat().st_size
            if (next_final_bytes, budget_path.stat().st_size) == (final_bytes, budget_bytes):
                break
            final_bytes = next_final_bytes
        else:
            self.fail("Neutral V6 fixture byte sizes did not stabilize")
        return final_path

    def test_v6_final_binding_accepts_only_the_prepared_identity_and_resolved_artifacts(self):
        with tempfile.TemporaryDirectory() as root:
            final_path = self._v6_neutral_fixture(Path(root))
            self.assertEqual(run_binding.load(final_path)["run_id"], run_binding.PREPARED_RUN_ID)

    def _assert_v6_validation_rejection(self, final_path, *, error="FINAL_BUDGET_INVALID", budget_reached=True):
        final = json.loads(final_path.read_bytes())
        self.assertEqual(final["version"], "s2uc.final-run-binding.v6")
        budget = run_binding._resolve_reference(final["budget"]["ledger"])
        self.assertEqual(budget["version"], "s2uc.closure-budget.v6")
        self.assertIs(entry.MAIN_GATE, False)
        # Structural validation is intentionally isolated from real admission.
        with patch.object(run_binding, "_validate_v6_budget", wraps=run_binding._validate_v6_budget) as validate:
            with self.assertRaisesRegex(ValueError, f"^{error}$"):
                run_binding.load(final_path)
            if budget_reached:
                validate.assert_called_once()
            else:
                validate.assert_not_called()
        self.assertIs(entry.MAIN_GATE, False)
        self.assertFalse((final_path.parent / "unused-output").exists())

    def test_v6_validation_rejects_undercounted_single_item_with_current_digests(self):
        with tempfile.TemporaryDirectory() as root:
            final_path = self._v6_neutral_fixture(Path(root), undercount_dependency=True)
            final = json.loads(final_path.read_bytes())
            budget = run_binding._resolve_reference(final["budget"]["ledger"])
            items = {item["name"]: item["bytes"] for item in budget["shared_items"]}
            actual = sum(Path(item["path"]).stat().st_size for item in final["dependencies"])
            self.assertEqual(items["active_dependency_sources"], actual - 1)
            for branch in budget["alternatives"].values():
                self.assertEqual(branch["contributions"]["shared"], sum(items.values()))
                self.assertEqual(branch["total_bytes"], sum(branch["contributions"].values()))
            self._assert_v6_validation_rejection(final_path)

    def test_v6_validation_rejects_actual_final_file_above_bound_reserve(self):
        with tempfile.TemporaryDirectory() as root:
            final_path = self._v6_neutral_fixture(Path(root))
            self.assertEqual(run_binding.load(final_path)["run_id"], run_binding.PREPARED_RUN_ID)
            final = json.loads(final_path.read_bytes())
            budget = run_binding._resolve_reference(final["budget"]["ledger"])
            reserve = next(item["bytes"] for item in budget["metadata_items"]
                           if item["name"] == "final_binding_reserve")
            self.assertEqual(final_path.stat().st_size, reserve)
            # Valid JSON whitespace grows the real file without changing any references.
            with final_path.open("ab") as stream:
                stream.write(b"\n")
            self.assertEqual(final_path.stat().st_size, reserve + 1)
            self._assert_v6_validation_rejection(final_path)

    def test_v6_validation_rejects_inconsistent_branch_contributions_with_current_digests(self):
        def change(budget):
            branch = budget["alternatives"]["success"]
            branch["contributions"]["shared"] -= 1
            branch["total_bytes"] -= 1
        with tempfile.TemporaryDirectory() as root:
            self._assert_v6_validation_rejection(self._v6_neutral_fixture(Path(root), mutate_budget=change))

    def test_v6_validation_rejects_missing_or_extra_branches_and_contribution_keys(self):
        for target in ("success", "failure", "minimal", "extra_branch", "missing_key", "extra_key"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as root:
                def change(budget):
                    if target == "extra_branch":
                        budget["alternatives"]["extra"] = copy.deepcopy(budget["alternatives"]["success"])
                    elif target in ("missing_key", "extra_key"):
                        c = budget["alternatives"]["success"]["contributions"]
                        if target == "missing_key":
                            del c["record"]
                        else:
                            c["extra"] = 0
                        budget["alternatives"]["success"]["total_bytes"] = sum(c.values())
                    else:
                        del budget["alternatives"][target]
                self._assert_v6_validation_rejection(self._v6_neutral_fixture(Path(root), mutate_budget=change))

    def test_v6_validation_rejects_duplicate_negative_missing_and_noninteger_items(self):
        for group in ("metadata_items", "shared_items"):
            for mutation in ("duplicate", "negative", "missing", "bool", "extra"):
                with self.subTest(group=group, mutation=mutation), tempfile.TemporaryDirectory() as root:
                    def change(budget):
                        rows = budget[group]
                        if mutation == "duplicate":
                            rows.append(copy.deepcopy(rows[0]))
                        elif mutation == "negative":
                            rows[0]["bytes"] = -1
                        elif mutation == "bool":
                            rows[0]["bytes"] = True
                        elif mutation == "extra":
                            rows.append({"name": "unknown", "bytes": 0})
                        else:
                            rows.pop()
                    self._assert_v6_validation_rejection(self._v6_neutral_fixture(Path(root), mutate_budget=change))

    def test_v6_validation_rejects_changed_reserves_and_qualification_artifact_sizes(self):
        for target in ("reserves", "qualification_summary", "qualification_protocol", "qualification_budget"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as root:
                def change(budget):
                    if target == "reserves":
                        budget["reserves"] = {**budget["reserves"], "success_record": ledger.RESERVES["success_record"] + 1}
                    else:
                        next(row for row in budget["shared_items"] if row["name"] == target)["bytes"] -= 1
                self._assert_v6_validation_rejection(self._v6_neutral_fixture(Path(root), mutate_budget=change))

    def test_v6_validation_rejects_empty_qualification_artifacts(self):
        for target in ("summary", "protocol", "budget"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as root:
                def change(name, value):
                    if name == target:
                        value.clear()
                self._assert_v6_validation_rejection(
                    self._v6_neutral_fixture(Path(root), mutate_qualification=change),
                    error="FINAL_QUALIFICATION_INVALID", budget_reached=False)

    def test_v6_validation_rejects_mismatched_qualification_ids_results_tests_and_code(self):
        for target in ("summary", "protocol", "budget"):
            mutations = ("qualification_id", "result")
            if target != "budget":
                mutations += ("code", "tests_run", "command")
            if target == "protocol":
                mutations += ("missing_test", "duplicate_test", "unknown_test", "summary_digest")
            for mutation in mutations:
                with self.subTest(target=target, mutation=mutation), tempfile.TemporaryDirectory() as root:
                    def change(name, value):
                        if name != target:
                            return
                        if mutation == "code":
                            value["files"][0]["sha256"] = "0" * 64
                        elif mutation == "tests_run":
                            value["tests_run"] -= 1
                        elif mutation == "missing_test":
                            value["test_cases"].pop()
                            value["tests_run"] -= 1
                        elif mutation == "duplicate_test":
                            value["test_cases"][-1] = value["test_cases"][0]
                        elif mutation == "unknown_test":
                            value["test_cases"][-1] = "unknown.test"
                        elif mutation == "summary_digest":
                            value["summary_sha256"] = "0" * 64
                        else:
                            value[mutation] = "WRONG"
                    self._assert_v6_validation_rejection(
                        self._v6_neutral_fixture(Path(root), mutate_qualification=change),
                        error="FINAL_QUALIFICATION_INVALID", budget_reached=False)

    def _assert_real_starter_admission_rejection(self, final_path, error):
        self.assertEqual(json.loads(final_path.read_bytes())["version"], "s2uc.final-run-binding.v6")
        calls = [0]
        def supplier(endpoint):
            calls[0] += 1
            raise AssertionError("Supplier must not be reached")
        output = final_path.parent / "admission-output"
        self.assertIs(entry.MAIN_GATE, False)
        # Only observe the downstream execution; the entire admission is real.
        with patch.object(entry, "run_bound_once", wraps=entry.run_bound_once) as execute:
            with self.assertRaisesRegex(ValueError, f"^{error}$"):
                starter.start(output, supplier, authorize=True, binding_file=final_path)
            execute.assert_not_called()
        self.assertEqual(calls[0], 0)
        self.assertIs(entry.MAIN_GATE, False)
        self.assertFalse(output.exists())

    def test_v6_real_starter_rejects_synthetic_qualification(self):
        with tempfile.TemporaryDirectory() as root:
            final_path = self._v6_neutral_fixture(Path(root))
            # This fixture is valid on the structural layer, but never admitted.
            self.assertEqual(run_binding.load(final_path)["run_id"], run_binding.PREPARED_RUN_ID)
            self._assert_real_starter_admission_rejection(final_path, "FINAL_SYNTHETIC_QUALIFICATION_FORBIDDEN")

    def test_v6_real_starter_rejects_matching_but_incomplete_dependencies(self):
        with tempfile.TemporaryDirectory() as root:
            final_path = self._v6_neutral_fixture(Path(root), admission_claim=True)
            final = json.loads(final_path.read_bytes())
            inventory = run_binding._resolve_reference(final["inventory_ref"])
            run_binding._validate_inventory(inventory, final["dependencies"])
            self.assertEqual(run_binding.load(final_path)["run_id"], run_binding.PREPARED_RUN_ID)
            self._assert_real_starter_admission_rejection(final_path, "FINAL_DEPENDENCY_INCOMPLETE")

    def test_v6_real_starter_rejects_complete_but_oversized_dependencies(self):
        with tempfile.TemporaryDirectory() as root:
            final_path = self._v6_neutral_fixture(Path(root), admission_claim=True, complete_dependencies=True)
            final = json.loads(final_path.read_bytes())
            current = run_binding.dependency_inventory.current()
            self.assertEqual(final["dependencies"], current["files"])
            self.assertGreater(sum(item["bytes"] for item in final["dependencies"]), ledger.LIMITS["shared"])
            self.assertGreater(sum(item["bytes"] for item in final["dependencies"]), ledger.RESERVES["active_bindings"])
            self._assert_real_starter_admission_rejection(final_path, "FINAL_DEPENDENCY_BUDGET_EXCEEDED")

    def test_v6_dependency_closure_includes_transitive_delayed_and_package_imports(self):
        current = run_binding.dependency_inventory.current()
        rows = {item["path"]: item for item in current["files"]}
        for name in ("tools/_s2ub_candidate_verification.py", "tools/_s2nu_private_source_binding.py",
                     "mcm_field_organism/__init__.py", "mcm_field_organism/root_lazy_exports.py",
                     "mcm_field_organism/carrier_baselines.py", "tools/_s2uc_dependencies.py"):
            self.assertIn(name, rows)
            self.assertEqual(rows[name], {**run_binding.reference(name), "path": name})
        self.assertIn("tools/_s2nu_private_source_binding.py", current["imports"]["tools/s2uc_run_bound_once.py"])
        self.assertIn("mcm_field_organism/root_lazy_exports.py", current["imports"]["mcm_field_organism/__init__.py"])
        self.assertEqual(current["project_source_bytes"], sum(item["bytes"] for item in rows.values()))
        self.assertEqual([row["module"] for row in current["external"] if row["kind"] == "third-party"], ["numpy"])

    def test_v6_dependency_scanner_follows_nested_relative_and_delayed_imports(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            (root / "pkg").mkdir()
            sources = {"entry.py": "from pkg import first\ndef deferred():\n    from pkg import delayed\n",
                       "pkg/__init__.py": "from . import initializer\n",
                       "pkg/first.py": "from . import nested\n", "pkg/nested.py": "",
                       "pkg/initializer.py": "", "pkg/delayed.py": ""}
            for name, data in sources.items():
                (root / name).write_text(data, encoding="utf-8")
            inventory = run_binding.dependency_inventory._scan(root, "entry.py")
            self.assertEqual({row["path"] for row in inventory["files"]}, set(sources))
            self.assertIn("pkg/delayed.py", inventory["imports"]["entry.py"])
            self.assertIn("pkg/nested.py", inventory["imports"]["pkg/first.py"])
            (root / "entry.py").write_text("from importlib import import_module as loader\ndef deferred(name):\n    loader(name)\n")
            with self.assertRaisesRegex(ValueError, "^FINAL_DEPENDENCY_DISCOVERY_UNRESOLVED$"):
                run_binding.dependency_inventory._scan(root, "entry.py")

    def test_v6_real_starter_rejects_omitted_delayed_transitive_and_package_files(self):
        for omitted in ("tools/_s2nu_private_source_binding.py", "tools/_s2ub_candidate_verification.py",
                        "mcm_field_organism/root_lazy_exports.py"):
            with self.subTest(omitted=omitted), tempfile.TemporaryDirectory() as root:
                final_path = self._v6_neutral_fixture(Path(root), admission_claim=True, complete_dependencies=True)
                final = json.loads(final_path.read_bytes())
                final["dependencies"] = [row for row in final["dependencies"] if row["path"] != omitted]
                inventory_path = Path(final["inventory_ref"]["path"])
                inventory = json.loads(inventory_path.read_bytes())
                inventory["files"] = [row for row in inventory["files"] if row["path"] != omitted]
                inventory_path.write_bytes(binding.canonical(inventory))
                final["inventory_ref"] = run_binding.reference(inventory_path)
                final_path.write_bytes(binding.canonical(final))
                run_binding._validate_inventory(inventory, final["dependencies"])
                self._assert_real_starter_admission_rejection(final_path, "FINAL_DEPENDENCY_INCOMPLETE")

    def test_real_starter_rejects_structurally_valid_legacy_binding(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "legacy.json"
            run_binding.freeze(path)
            calls = [0]
            output = Path(root) / "output"
            with self.assertRaisesRegex(ValueError, "^FINAL_START_BINDING_VERSION_INVALID$"):
                starter.start(output, lambda _: calls.__setitem__(0, calls[0] + 1), authorize=True, binding_file=path)
            self.assertEqual(calls[0], 0)
            self.assertIs(entry.MAIN_GATE, False)
            self.assertFalse(output.exists())

    def test_source_adapter_uses_all_bound_positions_without_deduplication(self):
        bound = run_binding.build(); bound = copy.deepcopy(bound)
        for endpoint in bound["endpoint_uses"]: endpoint["pcm_sha256"] = PAYLOAD_HASH
        for source in bound["sources"].values(): source["pcm_sha256"] = PAYLOAD_HASH
        adapter = source_adapter.SourceAdapter(bound, lambda endpoint: PAYLOAD)
        for endpoint in bound["endpoint_uses"]: adapter(endpoint)
        self.assertEqual(adapter.complete(), {"attempts": 58, "successes": 58, "counters": {"pcm_hashes": 58, "audio_analyses": 58, "nj_projections": 58}})
        adapter = source_adapter.SourceAdapter(bound, lambda endpoint: PAYLOAD)
        with self.assertRaisesRegex(ValueError, "ENDPOINT_ORDER_INVALID"):
            adapter(bound["endpoint_uses"][1])

    def test_verifier_rejects_missing_and_manipulated_source_completion(self):
        manifest = neutral_manifest(); record = connection.execute(manifest, lambda endpoint: tuple(0.0 for _ in range(48)))
        record["source_completion"] = {"attempts": 58, "successes": 58, "counters": {"pcm_hashes": 58, "audio_analyses": 58, "nj_projections": 58}}
        self.assertEqual(verification.verify(codec.loads(codec.dumps(record)), manifest)["status"], "VERIFIED")
        missing = copy.deepcopy(record); del missing["source_completion"]
        with self.assertRaisesRegex(ValueError, "SOURCE_COMPLETION_INVALID"):
            verification.verify(codec.loads(codec.dumps(missing)), manifest, require_source_completion=True)
        absent = copy.deepcopy(record); absent["source_completion"] = None
        with self.assertRaisesRegex(ValueError, "SOURCE_COMPLETION_INVALID"):
            verification.verify(codec.loads(codec.dumps(absent)), manifest, require_source_completion=True)
        record["source_completion"]["successes"] = 57
        with self.assertRaisesRegex(ValueError, "SOURCE_COMPLETION_INVALID"):
            verification.verify(codec.loads(codec.dumps(record)), manifest)
        for key in ("attempts", "successes"):
            changed = copy.deepcopy(record); changed["source_completion"][key] = 57
            with self.subTest(key=key):
                with self.assertRaisesRegex(ValueError, "SOURCE_COMPLETION_INVALID"):
                    verification.verify(codec.loads(codec.dumps(changed)), manifest, require_source_completion=True)
        for key in ("pcm_hashes", "audio_analyses", "nj_projections"):
            changed = copy.deepcopy(record); changed["source_completion"]["counters"][key] = 57
            with self.subTest(key=key):
                with self.assertRaisesRegex(ValueError, "SOURCE_COMPLETION_INVALID"):
                    verification.verify(codec.loads(codec.dumps(changed)), manifest, require_source_completion=True)

    def test_last_endpoint_failure_preserves_attempt_and_success_difference(self):
        bound = copy.deepcopy(run_binding.build())
        for endpoint in bound["endpoint_uses"]: endpoint["pcm_sha256"] = PAYLOAD_HASH
        for source in bound["sources"].values(): source["pcm_sha256"] = PAYLOAD_HASH
        calls = [0]
        def supplier(endpoint):
            calls[0] += 1
            if calls[0] == 58: raise source_adapter.S2UCSourceAdapterError("LAST_ENDPOINT_FAILURE")
            return PAYLOAD
        adapter = source_adapter.SourceAdapter(bound, supplier)
        for endpoint in bound["endpoint_uses"][:-1]: adapter(endpoint)
        with self.assertRaisesRegex(ValueError, "LAST_ENDPOINT_FAILURE"):
            adapter(bound["endpoint_uses"][-1])
        self.assertEqual((adapter._index, adapter._successes, adapter.counters.snapshot()), (58, 57, {"pcm_hashes": 57, "audio_analyses": 57, "nj_projections": 57}))

    def test_authorization_gate_and_isolated_neutral_execution(self):
        manifest = neutral_manifest()
        calls = [0]
        def supplier(endpoint):
            calls[0] += 1
            return PAYLOAD
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaisesRegex(ValueError, "RUN_NOT_AUTHORIZED"):
                starter.start(Path(root) / "no-auth", supplier)
            self.assertEqual(calls[0], 0)
            # Exercise neutral execution below admission; no mock bypass of starter.
            bound = copy.deepcopy(run_binding.build())
            for endpoint in bound["endpoint_uses"]:
                endpoint["pcm_sha256"] = PAYLOAD_HASH
            for source_row in bound["sources"].values():
                source_row["pcm_sha256"] = PAYLOAD_HASH
            bound["manifest_digest"] = manifest["binding_digest"]
            source = source_adapter.SourceAdapter(bound, supplier)
            entry.MAIN_GATE = True
            try:
                result = entry.run_once(manifest, source, Path(root) / "out", source.complete)
            finally:
                entry.MAIN_GATE = False
            self.assertTrue((Path(root) / "out" / "record.json").is_file())
        self.assertTrue(result["evaluation_allowed"])
        self.assertEqual(calls[0], 58)

    def test_starter_rejects_code_binding_before_supplier(self):
        calls = [0]
        with patch.object(starter.binding, "load_for_start", side_effect=ValueError("RUN_BINDING_INVALID")):
            with self.assertRaisesRegex(ValueError, "RUN_BINDING_INVALID"):
                starter.start("unused", lambda endpoint: calls.__setitem__(0, calls[0] + 1), authorize=True)
        self.assertEqual(calls[0], 0)

    def test_final_binding_validates_referenced_qualification_and_budget_before_supplier(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            source_path = root / "source.json"
            run_binding.freeze(source_path)
            dependencies = [run_binding.reference(Path("tools/_s2uc_run_binding.py")),
                            run_binding.reference(Path("tests/test_s2uc_materialization_connection.py"))]
            inventory_path = root / "inventory.json"
            inventory_path.write_text(json.dumps({"version": "s2uc.dependency-inventory.v6",
                "files": [{**row, "role": "neutral"} for row in dependencies], "external": [], "source": "neutral"}), encoding="utf-8")
            protocol_path = root / "protocol.json"
            protocol = {"version": "s2uc.finalformat-neutral-test.v2", "command": "neutral", "result": "OK", "tests_run": 1,
                        "real_payloads_opened": False, "scope": ["final format"], "files": copy.deepcopy(dependencies)}
            protocol_path.write_text(json.dumps(protocol), encoding="utf-8")
            full_protocol_path = root / "full-protocol.json"
            def write_full_protocol():
                full_protocol_path.write_text(json.dumps({"version": "s2uc.finalformat-neutral-protocol.v1", "command": "neutral", "result": "OK",
                    "tests_run": 1, "test_cases": ["final-format"], "summary_sha256": hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
                    "files": copy.deepcopy(dependencies)}), encoding="utf-8")
            write_full_protocol()
            budget_path = root / "budget.json"
            budget_path.write_text("{}", encoding="utf-8")
            final_path = root / "final.json"

            def write_budget(final_bytes, *, total_delta=0, metadata_delta=0):
                metadata = binding.manifest()["binding_bytes"] + final_bytes + metadata_delta
                shared = (sum(row["bytes"] for row in dependencies) + source_path.stat().st_size + inventory_path.stat().st_size
                          + protocol_path.stat().st_size + full_protocol_path.stat().st_size + budget_path.stat().st_size
                          + ledger.RESERVES["terminal"])
                alternatives = {}
                for name, record, verified in (("success", ledger.RESERVES["success_record"], ledger.RESERVES["verification"]),
                                              ("failure", ledger.RESERVES["failure_record"], ledger.RESERVES["verification"]),
                                              ("minimal", ledger.RESERVES["failure_record"], 0)):
                    contributions = {"metadata": metadata, "shared": shared, "record": record, "verification": verified}
                    alternatives[name] = {"contributions": contributions, "total": sum(contributions.values()) + total_delta, "violations": []}
                value = {"version": "s2uc.closure-budget.v5", "method": "neutral", "limits": ledger.LIMITS,
                         "metadata_items": [{"name": "manifest", "bytes": binding.manifest()["binding_bytes"]}, {"name": "compact_final_binding", "bytes": final_bytes + metadata_delta}],
                         "shared_items": [{"name": "active_dependency_sources", "bytes": sum(row["bytes"] for row in dependencies)}, {"name": "frozen_source_binding", "bytes": source_path.stat().st_size},
                                          {"name": "dependency_inventory", "bytes": inventory_path.stat().st_size}, {"name": "qualification_protocol", "bytes": protocol_path.stat().st_size + full_protocol_path.stat().st_size},
                                          {"name": "budget_ledger", "bytes": budget_path.stat().st_size}, {"name": "terminal_reserve", "bytes": ledger.RESERVES["terminal"]}],
                         "alternatives": alternatives, "result": "WITHIN_LIMITS", "historical_overage": {}}
                budget_path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")), encoding="utf-8")

            state = (0, 0)
            for _ in range(8):
                write_budget(state[0])
                draft = root / "draft.json"
                if draft.exists(): draft.unlink()
                run_binding.final_binding(draft, source_binding_path=source_path, dependencies=dependencies,
                                          inventory_path=inventory_path,
                                          qualifications={"finalformat_test": run_binding.reference(protocol_path), "finalformat_protocol": run_binding.reference(full_protocol_path)}, budget={"ledger": run_binding.reference(budget_path)})
                next_state = (draft.stat().st_size, budget_path.stat().st_size)
                draft.unlink()
                if next_state == state: break
                state = next_state
            write_budget(state[0])
            run_binding.final_binding(final_path, source_binding_path=source_path, dependencies=dependencies,
                                      inventory_path=inventory_path,
                                      qualifications={"finalformat_test": run_binding.reference(protocol_path), "finalformat_protocol": run_binding.reference(full_protocol_path)}, budget={"ledger": run_binding.reference(budget_path)})
            self.assertEqual(run_binding.load(final_path), run_binding.build())
            self.assertEqual(json.loads(budget_path.read_text(encoding="utf-8"))["alternatives"]["minimal"]["contributions"]["record"], ledger.RESERVES["failure_record"])
            final = json.loads(final_path.read_text(encoding="utf-8"))
            final["source_binding_ref"]["sha256"] = "0" * 64
            final_path.write_text(json.dumps(final), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "FINAL_REFERENCE_INVALID"):
                run_binding.load(final_path)

            protocol["result"] = "FAILED"; protocol_path.write_text(json.dumps(protocol), encoding="utf-8"); write_full_protocol()
            invalid_qualification = root / "invalid-qualification.json"
            run_binding.final_binding(invalid_qualification, source_binding_path=source_path, dependencies=dependencies,
                                      inventory_path=inventory_path,
                                      qualifications={"finalformat_test": run_binding.reference(protocol_path), "finalformat_protocol": run_binding.reference(full_protocol_path)}, budget={"ledger": run_binding.reference(budget_path)})
            with self.assertRaisesRegex(ValueError, "FINAL_QUALIFICATION_INVALID"):
                run_binding.load(invalid_qualification)
            calls = [0]
            with self.assertRaisesRegex(ValueError, "FINAL_QUALIFICATION_INVALID"):
                starter.start(root / "qualification-output", lambda _: calls.__setitem__(0, calls[0] + 1), authorize=True, binding_file=invalid_qualification)
            self.assertEqual(calls[0], 0)

            protocol["result"] = "OK"; protocol_path.write_text(json.dumps(protocol), encoding="utf-8"); write_full_protocol()
            for name, total_delta, metadata_delta in (("wrong-total", 1, 0), ("over-metadata", 0, ledger.LIMITS["metadata"])):
                with self.subTest(name=name):
                    write_budget(state[0], total_delta=total_delta, metadata_delta=metadata_delta)
                    invalid_budget = root / f"{name}.json"
                    run_binding.final_binding(invalid_budget, source_binding_path=source_path, dependencies=dependencies,
                                              inventory_path=inventory_path,
                                              qualifications={"finalformat_test": run_binding.reference(protocol_path), "finalformat_protocol": run_binding.reference(full_protocol_path)}, budget={"ledger": run_binding.reference(budget_path)})
                    with self.assertRaisesRegex(ValueError, "FINAL_BUDGET_INVALID"):
                        run_binding.load(invalid_budget)
                    calls = [0]
                    with self.assertRaisesRegex(ValueError, "FINAL_BUDGET_INVALID"):
                        starter.start(root / f"{name}-output", lambda _: calls.__setitem__(0, calls[0] + 1), authorize=True, binding_file=invalid_budget)
                    self.assertEqual(calls[0], 0)

            write_budget(state[0])
            smaller = json.loads(budget_path.read_text(encoding="utf-8"))
            smaller["shared_items"][0]["bytes"] -= 1
            for branch in smaller["alternatives"].values():
                branch["contributions"]["shared"] -= 1
                branch["total"] -= 1
            budget_path.write_text(json.dumps(smaller, sort_keys=True, separators=(",", ":")), encoding="utf-8")
            invalid_shared = root / "share.json"
            run_binding.final_binding(invalid_shared, source_binding_path=source_path, dependencies=dependencies,
                                      inventory_path=inventory_path,
                                      qualifications={"finalformat_test": run_binding.reference(protocol_path), "finalformat_protocol": run_binding.reference(full_protocol_path)}, budget={"ledger": run_binding.reference(budget_path)})
            with self.assertRaisesRegex(ValueError, "FINAL_BUDGET_INVALID"):
                run_binding.load(invalid_shared)
            calls = [0]
            with self.assertRaisesRegex(ValueError, "FINAL_BUDGET_INVALID"):
                starter.start(root / "shared-output", lambda _: calls.__setitem__(0, calls[0] + 1), authorize=True, binding_file=invalid_shared)
            self.assertEqual(calls[0], 0)
    def test_full_neutral_materialization_roundtrip_and_reloaded_verification(self):
        manifest = neutral_manifest(); counters = materialization.MaterializationCounters(); materialize, calls = adapter(counters)
        record = connection.execute(manifest, materialize)
        data = codec.dumps(record); reloaded = codec.loads(data)
        self.assertEqual((record["status"], calls[0], counters.snapshot()), ("COMPLETE", 58, {"pcm_hashes": 58, "audio_analyses": 58, "nj_projections": 58}))
        self.assertEqual(verification.verify(reloaded, manifest), {"status": "VERIFIED", "stories": ["g1", "g2", "g3"]})
        budget = ledger.ledger(manifest_bytes=manifest["binding_bytes"], success_record_bytes=len(data), failure_record_bytes=1, verification_bytes=1, terminal_bytes=1)
        self.assertFalse(budget["branches"]["success"]["violations"])

    def test_materialization_failure_in_second_story_roundtrips_and_verifies_prefix(self):
        manifest = neutral_manifest(); counters = materialization.MaterializationCounters(); materialize, calls = adapter(counters, fail_call=23)
        record = connection.execute(manifest, materialize); reloaded = codec.loads(codec.dumps(record))
        self.assertEqual((record["status"], record["failure"]["code"], calls[0], counters.snapshot()), ("NOT_EVALUABLE", "NEUTRAL_MATERIALIZATION_FAILURE", 23, {"pcm_hashes": 22, "audio_analyses": 22, "nj_projections": 22}))
        self.assertEqual(verification.verify_failure(reloaded, manifest)["story"], "g2")

    def test_reloaded_record_rejects_manipulated_materialization_origin(self):
        manifest = neutral_manifest(); counters = materialization.MaterializationCounters(); materialize, _ = adapter(counters)
        record = codec.loads(codec.dumps(connection.execute(manifest, materialize)))
        record["stories"][0]["events"][0]["materialization"]["pcm_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "MATERIALIZATION_BINDING_INVALID"):
            verification.verify(record, manifest)

    def test_owner_close_error_after_neutral_materialization_stops_and_roundtrips(self):
        manifest = neutral_manifest(); counters = materialization.MaterializationCounters(); materialize, _ = adapter(counters); closes = []
        class CloseFailingImmediate(ub.ImmediateTwArm):
            def close_owner(self):
                closes.append("immediate")
                raise connection.S2UCConnectionError("NEUTRAL_OWNER_CLOSE_FAILURE")
        class ClosingCandidate(ub.CandidateConfirmationArm):
            def close_owner(self):
                closes.append("candidate")
                return super().close_owner()
        with patch.object(connection.ub, "ImmediateTwArm", CloseFailingImmediate), patch.object(connection.ub, "CandidateConfirmationArm", ClosingCandidate):
            record = connection.execute(manifest, materialize)
        reloaded = codec.loads(codec.dumps(record))
        self.assertEqual((record["status"], closes, record["not_executed"]), ("NOT_EVALUABLE", ["immediate", "candidate"], ["g2", "g3"]))
        self.assertEqual(verification.verify_failure(reloaded, manifest)["phase"], "OWNER_CLOSE")

    def test_full_entry_serializes_reloads_verifies_and_only_then_evaluates(self):
        manifest = neutral_manifest(); counters = materialization.MaterializationCounters(); materialize, _ = adapter(counters)
        with tempfile.TemporaryDirectory() as root:
            entry.MAIN_GATE = True
            result = entry.run_once(manifest, materialize, Path(root) / "out")
            self.assertTrue((Path(result["output_directory"]) / "record.json").is_file())
            self.assertTrue((Path(result["output_directory"]) / "terminal.json").is_file())
            terminal_bytes = (Path(result["output_directory"]) / "terminal.json").read_bytes()
            terminal = json.loads(terminal_bytes)
            self.assertEqual(len(terminal_bytes), terminal["budget"]["branches"]["success"]["contributions"]["shared"] - terminal["active_bindings"]["bytes"])
        self.assertTrue(result["evaluation_allowed"])
        self.assertEqual((result["technical_verification"]["status"], result["evaluation"]["status"], result["evaluation"]["hint_count"]), ("VERIFIED", "EVALUATED", 7))
        self.assertEqual({tuple(item["key"]) for item in result["evaluation"]["confirmed_expectations"] + result["evaluation"]["violated_expectations"]}, set(evaluation.EXPECTED))
        self.assertFalse(any(branch["violations"] for branch in result["actual_budget"]["branches"].values()))
        self.assertFalse(entry.MAIN_GATE)

    def test_existing_output_directory_is_never_modified(self):
        manifest = neutral_manifest(); counters = materialization.MaterializationCounters(); materialize, _ = adapter(counters)
        with tempfile.TemporaryDirectory() as root:
            output = Path(root) / "out"; output.mkdir(); target = output / "terminal.json"; target.write_bytes(b"historical")
            entry.MAIN_GATE = True
            result = entry.run_once(manifest, materialize, output)
            self.assertEqual(target.read_bytes(), b"historical")
        self.assertEqual(result["primary_error"], "OUTPUT_DIRECTORY_ALREADY_EXISTS")
        self.assertFalse(entry.MAIN_GATE)

    def test_evaluation_rejects_missing_and_duplicate_expected_receipts(self):
        manifest = neutral_manifest(); counters = materialization.MaterializationCounters(); materialize, _ = adapter(counters)
        record = connection.execute(manifest, materialize)
        missing = copy.deepcopy(record); missing["stories"][0]["hints"].pop()
        with self.assertRaisesRegex(ValueError, "EXPECTED_RECEIPT_COUNT_INVALID"):
            evaluation.evaluate(missing)
        duplicate = copy.deepcopy(record); duplicate["stories"][0]["hints"].append(copy.deepcopy(duplicate["stories"][0]["hints"][0]))
        with self.assertRaisesRegex(ValueError, "EXPECTED_RECEIPT_COUNT_INVALID"):
            evaluation.evaluate(duplicate)

    def test_full_entry_verification_failure_publishes_terminal_and_blocks_evaluation(self):
        manifest = neutral_manifest(); counters = materialization.MaterializationCounters(); materialize, _ = adapter(counters)
        with tempfile.TemporaryDirectory() as root:
            entry.MAIN_GATE = True
            with patch.object(entry.verification, "verify", side_effect=ValueError("VERIFY_FAILURE")):
                result = entry.run_once(manifest, materialize, Path(root) / "out")
            terminal = (Path(root) / "out" / "terminal.json").read_text(encoding="utf-8")
        self.assertEqual((result["primary_error"], result["evaluation_allowed"]), ("VERIFY_FAILURE", False))
        self.assertIn("VERIFY_FAILURE", terminal)
        self.assertFalse(entry.MAIN_GATE)

    def test_failure_budget_counts_error_receipt_and_terminal_separately(self):
        manifest = neutral_manifest(); counters = materialization.MaterializationCounters(); materialize, _ = adapter(counters)
        with tempfile.TemporaryDirectory() as root:
            entry.MAIN_GATE = True
            with patch.object(entry.verification, "verify", side_effect=ValueError("VERIFY_FAILURE")):
                result = entry.run_once(manifest, materialize, Path(root) / "out")
            terminal_bytes = (Path(root) / "out" / "terminal.json").read_bytes()
            terminal = json.loads(terminal_bytes)
        failure = terminal["budget"]["branches"]["failure"]["contributions"]
        self.assertEqual(failure["shared"], terminal["active_bindings"]["bytes"] + result["error_evidence"]["bytes"] + len(terminal_bytes))
        self.assertFalse(entry.MAIN_GATE)

    def test_codec_failure_after_connection_retains_completed_progress_and_blocks_evaluation(self):
        manifest = neutral_manifest(); counters = materialization.MaterializationCounters(); materialize, _ = adapter(counters)
        with tempfile.TemporaryDirectory() as root:
            entry.MAIN_GATE = True
            with patch.object(entry.codec, "dumps", side_effect=ValueError("CODEC_FAILURE")):
                result = entry.run_once(manifest, materialize, Path(root) / "out")
            terminal = json.loads((Path(root) / "out" / "terminal.json").read_text(encoding="utf-8"))
        self.assertEqual((result["primary_error"], result["evaluation_allowed"], terminal["progress"]["completed_events"]), ("CODEC_FAILURE", False, 69))
        self.assertFalse(entry.MAIN_GATE)

    def test_unbudgetable_error_terminal_publishes_bounded_minimal_evidence(self):
        manifest = neutral_manifest(); counters = materialization.MaterializationCounters(); materialize, _ = adapter(counters)
        with tempfile.TemporaryDirectory() as root:
            entry.MAIN_GATE = True
            with patch.object(entry, "_terminal_with_budget", side_effect=ValueError("TERMINAL_BUDGET_UNSTABLE")):
                result = entry.run_once(manifest, materialize, Path(root) / "out")
            self.assertFalse((Path(root) / "out" / "terminal.json").exists())
            self.assertTrue((Path(root) / "out" / "terminal-minimal.json").is_file())
        self.assertEqual(result["primary_error"], "TERMINAL_BUDGET_UNSTABLE")
        self.assertTrue(result["terminal"]["minimal_terminal"]["published"])
        self.assertFalse(entry.MAIN_GATE)

    def test_terminal_write_failure_preserves_primary_codec_error(self):
        manifest = neutral_manifest(); counters = materialization.MaterializationCounters(); materialize, _ = adapter(counters)
        with tempfile.TemporaryDirectory() as root:
            entry.MAIN_GATE = True
            with patch.object(entry.codec, "dumps", side_effect=ValueError("CODEC_FAILURE")), patch.object(entry, "_publish", side_effect=OSError("WRITE_FAILURE")):
                result = entry.run_once(manifest, materialize, Path(root) / "out")
        self.assertEqual(result["primary_error"], "CODEC_FAILURE")
        self.assertIn("terminal_publication_error", result["terminal"])
        self.assertFalse(entry.MAIN_GATE)

    def test_full_entry_failure_blocks_evaluation_and_resets_gate(self):
        manifest = neutral_manifest(); counters = materialization.MaterializationCounters(); materialize, _ = adapter(counters, fail_call=23)
        with tempfile.TemporaryDirectory() as root:
            entry.MAIN_GATE = True
            result = entry.run_once(manifest, materialize, Path(root) / "out")
        self.assertEqual((result["technical_verification"]["status"], result["evaluation_allowed"], result["evaluation"]), ("VERIFIED_FAILURE", False, None))
        self.assertFalse(entry.MAIN_GATE)

    def test_full_entry_rejects_actual_reserve_overflow_and_resets_gate(self):
        manifest = neutral_manifest(); counters = materialization.MaterializationCounters(); materialize, _ = adapter(counters)
        with tempfile.TemporaryDirectory() as root:
            entry.MAIN_GATE = True
            with patch.object(entry.codec, "dumps", return_value=b"x" * (ledger.LIMITS["record"] + 1)):
                result = entry.run_once(manifest, materialize, Path(root) / "out")
            record_published = (Path(root) / "out" / "record.json").exists()
            evidence = json.loads((Path(root) / "out" / "error.json").read_text(encoding="utf-8"))
        self.assertEqual(result["primary_error"], "RECORD_BUDGET_INVALID")
        self.assertFalse(record_published)
        self.assertEqual((evidence["primary_error"], evidence["phase"], evidence["candidate_record"]["bytes"]),
                         ("RECORD_BUDGET_INVALID", "RECORD_PREFLIGHT", ledger.LIMITS["record"] + 1))
        self.assertFalse(entry.MAIN_GATE)

    def test_v2_codec_keeps_binary64_values_and_separate_frame_identities(self):
        values = (-0.0, math.ldexp(1.0, -1074), -float.fromhex("0x1.fffffffffffffp+1023")) + (0.0,) * 45
        first = tu.Frame(values, "p" * 64, "owner-a", "segment-a", 1)
        second = tu.Frame(values, "p" * 64, "owner-b", "segment-b", 2)
        encoded = codec.dumps({"frames": (first, second)})
        envelope = json.loads(encoded)
        decoded = codec.loads(encoded)["frames"]
        self.assertEqual((envelope["version"], len(envelope["vectors"]), len(envelope["frames"])), (codec.VERSION, 1, 2))
        self.assertEqual((decoded[0].owner, decoded[1].owner, decoded[0].segment, decoded[1].segment),
                         ("owner-a", "owner-b", "segment-a", "segment-b"))
        self.assertEqual([struct.pack(">d", value) for value in decoded[0].values], [struct.pack(">d", value) for value in values])

    def test_codec_keeps_historical_v1_record_form_readable(self):
        values = [value.hex() for value in ((0.0,) * 48)]
        legacy = {"version": codec.LEGACY_VERSION,
                  "frames": [{"values_hex": values, "profile": "l" * 64, "owner": "legacy-owner",
                              "segment": "legacy-segment", "ordinal": 7}],
                  "record": {"frame": {"@frame": 0}}}
        decoded = codec.loads(json.dumps(legacy, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        self.assertEqual((decoded["frame"].profile, decoded["frame"].owner, decoded["frame"].segment, decoded["frame"].ordinal),
                         ("l" * 64, "legacy-owner", "legacy-segment", 7))

    def test_v3_codec_references_event_values_hex_without_losing_long_binary64_forms(self):
        values = [float.fromhex("0x0.0000000000001p-1022").hex()] * 48
        frame = tu.Frame(tuple(float.fromhex(item) for item in values), "p" * 64, "owner", "segment", 1)
        encoded = codec.dumps({"values_hex": values, "frame": frame})
        envelope = json.loads(encoded); decoded = codec.loads(encoded)
        self.assertEqual((envelope["version"], len(envelope["vectors"]), envelope["record"]["values_hex"]),
                         (codec.VERSION, 1, {"@values_hex": 0}))
        self.assertEqual(decoded["values_hex"], values)

    def test_record_preflight_rejects_oversized_metadata_before_publication(self):
        manifest = neutral_manifest(); calls = [0]
        def oversized_receipt(_endpoint):
            calls[0] += 1
            return {"values": (0.0,) * 48, "pcm_sha256": PAYLOAD_HASH, "payload_bytes": len(PAYLOAD),
                    "raw_state_digest": "r" * 64, "projection_digest": "p" * 64, "source_values_digest": "s" * 64,
                    "projection_binding": {"diagnostic": "x" * 120_000}, "subnormal_band_indices": [], "underflow_band_indices": []}
        with tempfile.TemporaryDirectory() as root:
            entry.MAIN_GATE = True
            result = entry.run_once(manifest, oversized_receipt, Path(root) / "out")
            output = Path(root) / "out"
            evidence = json.loads((output / "error.json").read_text(encoding="utf-8"))
            self.assertFalse((output / "record.json").exists())
        self.assertEqual(result["primary_error"], "RECORD_BUDGET_INVALID")
        self.assertGreater(evidence["candidate_record"]["bytes"], ledger.RESERVES["success_record"])
        self.assertEqual(calls[0], 58)
        self.assertFalse(entry.MAIN_GATE)

    def test_v2_codec_worst_case_distinct_vectors_stays_within_its_bound(self):
        frames = tuple(tu.Frame((float(index),) + (0.0,) * 47, "p" * 64, f"owner-{index}", f"segment-{index}", index)
                       for index in range(116))
        encoded = codec.dumps({"frames": frames})
        envelope = json.loads(encoded)
        metadata = len(json.dumps(envelope["record"], sort_keys=True, separators=(",", ":")).encode("utf-8"))
        self.assertEqual((len(envelope["frames"]), len(envelope["vectors"])), (116, 116))
        self.assertLessEqual(len(encoded), codec.estimate_worst_case(frame_count=116, record_metadata_bytes=metadata))

    def test_v2_codec_full_neutral_structure_with_distinct_vectors_fits_record_reserve(self):
        """The bound also covers the complete neutral connection shape, not only frames."""
        manifest = neutral_manifest(); calls = [0]
        def distinct_materialize(_endpoint):
            calls[0] += 1
            return (float(calls[0]),) + (0.0,) * 47
        record = connection.execute(manifest, distinct_materialize)
        encoded = codec.dumps(record); envelope = json.loads(encoded)
        metadata = len(json.dumps(envelope["record"], sort_keys=True, separators=(",", ":")).encode("utf-8"))
        self.assertEqual((record["status"], calls[0]), ("COMPLETE", 58))
        self.assertLessEqual(len(envelope["frames"]), 116)
        self.assertLessEqual(len(envelope["vectors"]), len(envelope["frames"]))
        self.assertLessEqual(len(encoded), codec.estimate_worst_case(frame_count=116, record_metadata_bytes=metadata))
        self.assertLessEqual(len(encoded), ledger.RESERVES["success_record"])

    def test_record_write_failure_preserves_primary_error_and_closes_gate(self):
        manifest = neutral_manifest(); counters = materialization.MaterializationCounters(); materialize, _ = adapter(counters)
        original_publish = entry._publish
        def fail_record(path, value):
            if path.name == "record.json":
                raise OSError("RECORD_WRITE_FAILURE")
            return original_publish(path, value)
        with tempfile.TemporaryDirectory() as root:
            entry.MAIN_GATE = True
            with patch.object(entry, "_publish", side_effect=fail_record):
                result = entry.run_once(manifest, materialize, Path(root) / "out")
            evidence = json.loads((Path(root) / "out" / "error.json").read_text(encoding="utf-8"))
        self.assertEqual((result["primary_error"], evidence["primary_error"], result["error_evidence"]["published"]),
                         ("RECORD_WRITE_FAILURE", "RECORD_WRITE_FAILURE", True))
        self.assertFalse(entry.MAIN_GATE)

    def test_ledger_separates_record_reserve_from_absolute_record_limit(self):
        manifest = neutral_manifest()
        reserve = ledger.ledger(manifest_bytes=manifest["binding_bytes"], success_record_bytes=245_761,
                                failure_record_bytes=1, verification_bytes=1, terminal_bytes=1, active_binding_bytes=1)
        absolute = ledger.ledger(manifest_bytes=manifest["binding_bytes"], success_record_bytes=262_145,
                                 failure_record_bytes=1, verification_bytes=1, terminal_bytes=1, active_binding_bytes=1)
        self.assertEqual((reserve["branches"]["success"]["violations"], reserve["branches"]["success"]["reserve_violations"]), ([], ["record_reserve"]))
        self.assertIn("record", absolute["branches"]["success"]["violations"])
