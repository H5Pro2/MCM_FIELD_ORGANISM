"""V8 neutral integration. Test-only bindings never authorize the public starter."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
import uuid
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from tools import _s2uc_binding_v8 as binding
from tools import _s2uc_resources_v8 as resources
from tools import _s2uc_execution_v8 as execution
from tools import _s2uc_publication_v7 as publication
from tools import _s2uc_resource_contract_v7 as v7
from tools import _s2uc_prestart_v7 as prestart
from tools import _s2uc_inventory_v7 as inventory
from tools import _s2uc_run_entry as old_entry
from tools import s2uc_run_bound_once as starter


def write(root, name, value):
    (root / name).write_bytes(prestart.canonical(value))


def seal(bundle, inv, run_id, output):
    path = bundle / binding.FILENAME
    ledger = bundle / "resource-ledger.json"
    if not ledger.exists(): ledger.write_bytes(b"{}")
    for _ in range(16):
        refs = {}
        for role, (ns, name, category, _) in binding.FILES.items():
            ref, _, _ = inventory.read_file(inventory.ROOT if ns == "project" else bundle, name)
            refs[role] = {**ref, "namespace": ns, "category": category}
        value = {"version": binding.VERSION, "contract_id": resources.CONTRACT_ID, "run_id": run_id,
                 "output": output.resolve().as_posix(), "authorization": {"kind": "ONE_NEUTRAL_EXECUTION",
                 "max_uses": 1, "payload": "ZERO_PCM_F32LE", "real_sources": False}, "artifacts": refs}
        data = prestart.canonical(value); path.write_bytes(data)
        budget = binding.accounting(inv["code_bytes"], {k: r["bytes"] for k, r in refs.items()}, len(data))
        encoded = prestart.canonical(budget)
        if ledger.read_bytes() == encoded: return path
        ledger.write_bytes(encoded)
    raise AssertionError("neutral fixture did not converge")


def fixture(root, inv=None):
    inv = inv or binding.current()
    run_id = "S2UC-V8-NEUTRAL-" + uuid.uuid4().hex
    bundle, output = root / "bundle", root / run_id
    bundle.mkdir()
    values = {"manifest": binding.manifest(), "source_binding": binding.sources(), "inventory": inv,
              "resource_contract": binding.contract(), **binding.evidence(inv)}
    for role, value in values.items(): write(bundle, binding.FILES[role][1], value)
    return seal(bundle, inv, run_id, output), run_id, output


class V8ExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = binding.current()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path, self.run_id, self.output = fixture(self.root, self.inventory)
        self.calls = []

    def supplier(self, endpoint):
        self.calls.append(endpoint["source_id"])
        return binding.ZERO_PCM

    def run_neutral(self, supplier=None):
        result = execution.run_neutral(self.path, supplier or self.supplier, run_id=self.run_id, output_directory=self.output)
        self.assertFalse(execution.GATE)
        return result

    def check_accounting(self, result):
        files = {p.name: p.read_bytes() for p in self.output.iterdir()}
        self.assertEqual(set(files), {r["path"] for r in result["result_inventory"]})
        for row in result["result_inventory"]:
            self.assertEqual((row["bytes"], row["sha256"]), (len(files[row["path"]]), inventory.sha(files[row["path"]])))
        self.assertEqual(result["actual"]["total_bytes"], sum(r["bytes"] for r in result["inputs"]) + sum(map(len, files.values())))
        self.assertTrue(result["accounting_complete"])
        self.assertTrue(result["actual"]["within_limits"])
        self.assertEqual(result["actual"]["categories"]["code"], self.inventory["code_bytes"])
        self.assertEqual(result["version"], "s2uc.neutral-integration.v8")
        self.assertTrue(all(r["closed"] for r in result["owner_cleanup"]))

    def test_v8_revision_changes_only_code_cap_and_counts_every_bound_suite(self):
        self.assertEqual(resources.LIMITS["code"], 720896)
        self.assertEqual(v7.LIMITS["code"], 655360)
        self.assertEqual({k: v for k, v in resources.LIMITS.items() if k != "code"}, {k: v for k, v in v7.LIMITS.items() if k != "code"})
        self.assertEqual(resources.RESERVES, v7.RESERVES)
        names = {r["path"] for r in self.inventory["files"]}
        self.assertTrue(set(binding.ENTRIES) <= names)
        self.assertTrue(set(inventory.TESTS) <= names)
        self.assertEqual(self.inventory["code_bytes"], sum((inventory.ROOT / r["path"]).stat().st_size for r in self.inventory["files"]))
        self.assertLessEqual(self.inventory["code_bytes"], 720896)
        for size in (720896, 720897):
            amounts = dict.fromkeys(resources.CATEGORIES, 0); amounts["code"] = size
            actual = resources.account("failure_before_publication", amounts)
            self.assertEqual(actual["within_limits"], size == 720896)
            self.assertEqual(actual["total_bytes"], size)
        with self.assertRaises(TypeError): resources.LIMITS["code"] = 1

    def test_strict_binding_rejects_development_authorization_identity_and_v7_mix(self):
        original = self.path.read_bytes()
        changes = (lambda v: v.update(version=prestart.VERSION), lambda v: v.update(contract_id=v7.CONTRACT_ID),
                   lambda v: v.update(authorization={"kind": "development"}),
                   lambda v: v["authorization"].update(max_uses=True),
                   lambda v: v["authorization"].update(real_sources=True),
                   lambda v: v.update(run_id="unbound"), lambda v: v.update(output=str(self.root / "wrong")))
        for change in changes:
            value = json.loads(original); change(value); self.path.write_bytes(prestart.canonical(value))
            with self.subTest(value=value.get("version")), self.assertRaises(ValueError): self.run_neutral()
            self.assertEqual(self.calls, []); self.assertFalse(self.output.exists()); self.assertFalse(execution.GATE)
        self.path.write_bytes(original)
        with self.assertRaisesRegex(ValueError, "V8_EXECUTION_IDENTITY_INVALID"):
            execution.run_neutral(self.path, self.supplier, run_id=self.run_id, output_directory=self.root / "wrong")

    def test_binding_rejects_consistently_undercounted_inventory_and_false_roles(self):
        inv = copy.deepcopy(self.inventory); inv["files"].pop(); inv["code_bytes"] = sum(r["bytes"] for r in inv["files"])
        write(self.path.parent, "dependency-inventory.json", inv)
        seal(self.path.parent, inv, self.run_id, self.output)
        with self.assertRaisesRegex(ValueError, "V8_CONTENT_MISMATCH:inventory"): self.run_neutral()
        value = json.loads(self.path.read_bytes()); value["artifacts"]["manifest"]["category"] = "code"
        self.path.write_bytes(prestart.canonical(value))
        with self.assertRaisesRegex(ValueError, "V8_ARTIFACT_MISMATCH"): self.run_neutral()
        self.assertEqual(self.calls, [])

    def test_public_starter_unconditionally_stops_before_supplier_adapter_and_run(self):
        with patch.object(starter.adapter, "SourceAdapter") as adapter, patch.object(old_entry, "run_bound_once") as run:
            old_entry.MAIN_GATE = True
            with self.assertRaisesRegex(ValueError, "V8_REAL_EXECUTION_DISABLED"):
                starter.start(self.output, self.supplier, authorize=True, binding_file=self.path)
            self.assertFalse(old_entry.MAIN_GATE)
            adapter.assert_not_called(); run.assert_not_called()
            # Even a structurally accepted legacy result cannot open this starter.
            with patch.object(starter.binding, "load_for_start", return_value={}):
                with self.assertRaisesRegex(ValueError, "REAL_EXECUTION_DISABLED"):
                    starter.start(self.output, self.supplier, authorize=True, binding_file=self.path)
        self.assertEqual(self.calls, []); self.assertFalse(self.output.exists())

    def test_full_58_materializations_share_identical_values_between_both_arms(self):
        seen = {}
        def observe(cls, method, role):
            original = getattr(cls, method)
            def call(arm, frame):
                seen.setdefault(frame.ordinal, {})[role] = id(frame.values)
                return original(arm, frame)
            return patch.object(cls, method, call)
        with ExitStack() as stack:
            for cls, role in ((execution.connection.ub.ImmediateTwArm, "left"), (execution.connection.ub.CandidateConfirmationArm, "right")):
                for method in ("form", "hint"): stack.enter_context(observe(cls, method, role))
            result = self.run_neutral()
        self.assertEqual(result["status"], "CLOSED_NEUTRAL_VERIFIED")
        self.assertEqual(len(self.calls), 58); self.assertEqual(len(seen), 58)
        self.assertTrue(all(row["left"] == row["right"] for row in seen.values()))
        self.assertEqual(result["source_completion"]["counters"], {"pcm_hashes": 58, "audio_analyses": 58, "nj_projections": 58})
        self.assertEqual(result["source_completion"]["status"], "COMPLETE")
        record = publication.codec.loads((self.output / "record.json").read_bytes())
        self.assertEqual(len(record["source_completion"]["receipt_digests"]), 58)
        self.assertEqual(len(record["owner_cleanup"]), 6)
        proof = json.loads((self.output / "verification.json").read_bytes())
        self.assertEqual(proof["version"], "s2uc.verification-evaluation.v8")
        terminal = json.loads((self.output / "terminal.json").read_bytes())
        self.assertEqual(terminal["verification"]["sha256"], inventory.sha((self.output / "verification.json").read_bytes()))
        self.check_accounting(result)

    def test_failed_attempt_58_keeps_57_successes_and_original_error(self):
        def supplier(endpoint):
            self.calls.append(endpoint["source_id"])
            if len(self.calls) == 58: raise execution.connection.S2UCConnectionError("LAST_ENDPOINT_FAILURE")
            return binding.ZERO_PCM
        with patch.object(publication.evaluation, "evaluate") as evaluate: result = self.run_neutral(supplier)
        evaluate.assert_not_called()
        self.assertEqual(result["primary_error"], "LAST_ENDPOINT_FAILURE")
        self.assertEqual((result["source_completion"]["attempts"], result["source_completion"]["successes"]), (58, 57))
        self.assertEqual(result["source_completion"]["status"], "PARTIAL")
        self.assertEqual(result["source_completion"]["counters"], {"pcm_hashes": 57, "audio_analyses": 57, "nj_projections": 57})
        self.assertEqual(json.loads((self.output / "verification.json").read_bytes())["technical"]["status"], "VERIFIED_FAILURE")
        self.check_accounting(result)

    def test_missing_or_manipulated_receipts_and_full_completion_are_rejected(self):
        self.run_neutral()
        original = publication.codec.loads((self.output / "record.json").read_bytes())
        source, owners = original["source_completion"], original["owner_cleanup"]
        variants = {
            "missing_receipt": lambda r: r["stories"][0]["events"][0].pop("materialization"),
            "pcm": lambda r: r["stories"][0]["events"][0]["materialization"].update(pcm_sha256="0" * 64),
            "projection": lambda r: r["stories"][0]["events"][0]["materialization"].update(projection_digest="0" * 64),
            "values": lambda r: r["stories"][0]["events"][0]["values_hex"].__setitem__(0, (0.5).hex()),
            "time": lambda r: r["stories"][0]["events"][0]["materialization"]["projection_binding"].update(window_start_tick=1),
            "profile": lambda r: r["stories"][0]["events"][0]["materialization"]["projection_binding"].update(profile_digest="0" * 64),
            "crosslink": lambda r: r["stories"][0]["events"][0]["materialization"].update(raw_state_digest="0" * 64),
            "missing_completion": lambda r: r.pop("source_completion"),
            "counters": lambda r: r["source_completion"]["counters"].update(pcm_hashes=57),
            "boolean": lambda r: r["source_completion"].update(attempts=True),
            "digest_list": lambda r: r["source_completion"]["receipt_digests"].pop(),
        }
        for name, mutate in variants.items():
            record = copy.deepcopy(original); mutate(record)
            with self.subTest(name=name), self.assertRaises((ValueError, TypeError)):
                execution.verify_materialized(record, binding.manifest(), source, owners)
        # Recompute a valid projection digest: live materialization must still bind it.
        record = copy.deepcopy(original)
        row = record["stories"][0]["events"][0]
        row["values_hex"][0] = (0.25).hex()
        receipt = row["materialization"]
        values = tuple(float.fromhex(v) for v in row["values_hex"])
        receipt["projection_digest"] = execution.nj.digest({**receipt["projection_binding"], "values": values})
        with self.assertRaisesRegex(ValueError, "V8_RECEIPT_LIVE_BINDING_INVALID"):
            execution.verify_materialized(record, binding.manifest(), source, owners)
        # Internally consistent shifted time is still outside the endpoint binding.
        record = copy.deepcopy(original)
        row = record["stories"][0]["events"][0]; receipt = row["materialization"]
        for key, delta in (("snapshot_index", 1), ("window_start_tick", 480), ("window_end_tick", 480)):
            receipt["projection_binding"][key] += delta
        receipt["projection_digest"] = execution.nj.digest({**receipt["projection_binding"], "values": tuple(float.fromhex(v) for v in row["values_hex"])})
        with self.assertRaisesRegex(ValueError, "V8_PROJECTION_TIME_INVALID"):
            execution.verify_materialized(record, binding.manifest(), source, owners)

    def test_counter_phases_supplier_hash_receptor_and_projection_failures(self):
        cases = (("supplier", (0, 0, 0), "NONE"), ("hash", (1, 0, 0), "HASH"),
                 ("receptor", (1, 1, 0), "ANALYZE"), ("projection", (1, 1, 1), "NJ"))
        for name, expected, step in cases:
            root = self.root / name; root.mkdir()
            path, run_id, output = fixture(root, self.inventory)
            def supplier(_):
                if name == "supplier": raise ValueError("NEUTRAL_SUPPLIER")
                return b"x" * 19200 if name == "hash" else binding.ZERO_PCM
            with ExitStack() as stack:
                if name == "receptor": stack.enter_context(patch.object(execution.adapter.ty.LogSpectralReceptor, "analyze", side_effect=ValueError("RECEPTOR")))
                if name == "projection": stack.enter_context(patch.object(execution.adapter.ty.nj, "project_auditory_half_v1", side_effect=ValueError("NJ")))
                stack.enter_context(patch.object(publication.evaluation, "evaluate", side_effect=AssertionError("evaluation forbidden")))
                result = execution.run_neutral(path, supplier, run_id=run_id, output_directory=output)
            self.assertEqual(result["status"], "NOT_EVALUABLE")
            self.assertEqual(tuple(result["source_completion"]["counters"].values()), expected)
            self.assertEqual(result["source_completion"]["reached_step"], step)
            self.assertFalse(execution.GATE)
            self.assertTrue((output / "verification.json").exists())

    def test_failure_between_arm_calls_preserves_pending_materialization(self):
        with patch.object(execution.connection.ub.CandidateConfirmationArm, "form", side_effect=execution.connection.S2UCConnectionError("SECOND_ARM_FAILURE")):
            result = self.run_neutral()
        self.assertEqual(result["primary_error"], "SECOND_ARM_FAILURE")
        self.assertEqual(len(self.calls), 1)
        record = publication.codec.loads((self.output / "record.json").read_bytes())
        self.assertIsNotNone(record["source_completion"]["pending"])
        self.assertEqual(record["source_completion"]["successes"], 1)
        self.assertEqual(record["stories"][0]["events"], [])
        self.check_accounting(result)

    def test_constructor_failure_closes_both_registered_owners_and_resets_gate(self):
        original = execution.connection.ub.CandidateConfirmationArm.__init__
        def fail(arm, *args):
            original(arm, *args)
            raise execution.connection.S2UCConnectionError("CONSTRUCTOR_FAILURE")
        with patch.object(execution.connection.ub.CandidateConfirmationArm, "__init__", fail): result = self.run_neutral()
        self.assertEqual(result["primary_error"], "CONSTRUCTOR_FAILURE")
        self.assertEqual(self.calls, [])
        self.assertEqual(len(result["owner_cleanup"]), 2)
        self.assertTrue(all(r["closed"] for r in result["owner_cleanup"]))
        self.assertTrue(result["owner_cleanup"][1]["construction_failed"])
        self.check_accounting(result)

    def test_owner_close_failure_is_primary_and_cleanup_closes_both(self):
        with patch.object(execution.connection.ub.ImmediateTwArm, "close_owner", side_effect=execution.connection.S2UCConnectionError("OWNER_FAILURE")):
            result = self.run_neutral()
        self.assertEqual(result["primary_error"], "OWNER_CLOSE_INVALID")
        self.assertEqual(len(self.calls), 22)
        self.assertTrue(all(r["closed"] for r in result["owner_cleanup"]))
        self.assertTrue(result["owner_cleanup"][0]["fallback"])
        self.assertEqual(result["source_completion"]["status"], "PARTIAL")
        self.check_accounting(result)

    def test_codec_failure_preserves_connection_error_and_closed_owners(self):
        def fail(_): raise execution.connection.S2UCConnectionError("PRIMARY_SUPPLIER_FAILURE")
        with patch.object(publication.codec, "dumps", side_effect=ValueError("SECONDARY_CODEC_FAILURE")):
            result = self.run_neutral(fail)
        self.assertEqual(result["primary_error"], "PRIMARY_SUPPLIER_FAILURE")
        self.assertFalse((self.output / "record.json").exists())
        self.assertTrue(any(r["error"] == "SECONDARY_CODEC_FAILURE" for r in result["secondary_errors"]))
        self.check_accounting(result)

    def test_full_source_completion_error_does_not_overwrite_an_aborted_record(self):
        def fail(_): raise execution.connection.S2UCConnectionError("PRIMARY_ABORT")
        with patch.object(execution._Source, "snapshot", side_effect=ValueError("SECONDARY_COMPLETION")):
            result = self.run_neutral(fail)
        self.assertEqual(result["primary_error"], "PRIMARY_ABORT")
        self.assertFalse(result["evaluation_allowed"])
        self.check_accounting(result)

    def test_existing_output_and_repeated_use_never_invoke_supplier(self):
        self.output.mkdir(); (self.output / "keep").write_bytes(b"unchanged")
        with self.assertRaisesRegex(ValueError, "V8_OUTPUT_ALREADY_EXISTS"): self.run_neutral()
        self.assertEqual(self.calls, []); self.assertEqual((self.output / "keep").read_bytes(), b"unchanged")
        (self.output / "keep").unlink(); self.output.rmdir()
        self.run_neutral(); count = len(self.calls)
        with self.assertRaisesRegex(ValueError, "V8_ALREADY_USED"): self.run_neutral()
        self.assertEqual(len(self.calls), count); self.assertFalse(execution.GATE)

    def test_process_restart_with_existing_output_remains_closed(self):
        self.run_neutral()
        code = """from tools import _s2uc_execution_v8 as e
import sys, json
calls = []
def supplier(endpoint):
    calls.append(endpoint)
    raise AssertionError('SUPPLIER_CALLED')
try:
    e.run_neutral(sys.argv[1], supplier, run_id=sys.argv[2], output_directory=sys.argv[3])
except ValueError as exc:
    print(json.dumps({'error': str(exc), 'supplier_calls': len(calls), 'gate': e.GATE}))
    sys.exit(23)
"""
        result = subprocess.run([sys.executable, "-c", code, str(self.path), self.run_id, str(self.output)], capture_output=True)
        self.assertEqual(result.returncode, 23)
        self.assertEqual(json.loads(result.stdout), {"error": "V8_OUTPUT_ALREADY_EXISTS", "supplier_calls": 0, "gate": False})
        self.assertEqual(result.stderr, b"")

    def test_failed_execution_consumes_identity_and_blocks_retry(self):
        def fail(endpoint):
            self.calls.append(endpoint)
            raise execution.connection.S2UCConnectionError("ONE_SHOT_ABORT")
        result = self.run_neutral(fail)
        self.assertEqual(result["primary_error"], "ONE_SHOT_ABORT")
        before = {p.name: p.read_bytes() for p in self.output.iterdir()}
        with self.assertRaisesRegex(ValueError, "V8_ALREADY_USED"): self.run_neutral()
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.output.iterdir()})
        self.check_accounting(result)

    def test_second_story_constructor_failure_preserves_completed_source_prefix(self):
        original = execution.connection.ub.CandidateConfirmationArm.__init__
        def fail(arm, profile, name):
            if name == "s2uc-g2-candidate": raise execution.connection.S2UCConnectionError("SECOND_CONSTRUCTOR")
            original(arm, profile, name)
        with patch.object(execution.connection.ub.CandidateConfirmationArm, "__init__", fail): result = self.run_neutral()
        self.assertEqual(result["primary_error"], "SECOND_CONSTRUCTOR")
        self.assertEqual((result["source_completion"]["attempts"], result["source_completion"]["successes"]), (22, 22))
        self.assertEqual(len(result["owner_cleanup"]), 4)
        self.assertFalse(result["owner_cleanup"][-1]["initialized"])
        self.assertFalse(result["evaluation_allowed"])
        self.check_accounting(result)

    def test_last_owner_failure_keeps_full_source_completion(self):
        original = execution.connection.ub.ImmediateTwArm.close_owner
        def fail(arm):
            if arm.store.owner == "s2uc-g3-tw": raise execution.connection.S2UCConnectionError("LAST_OWNER")
            original(arm)
        with patch.object(execution.connection.ub.ImmediateTwArm, "close_owner", fail): result = self.run_neutral()
        self.assertEqual(result["primary_error"], "OWNER_CLOSE_INVALID")
        self.assertEqual(result["source_completion"]["status"], "COMPLETE")
        self.assertEqual(len(self.calls), 58)
        self.assertFalse(result["evaluation_allowed"])
        self.assertEqual(json.loads((self.output / "verification.json").read_bytes())["technical"]["status"], "VERIFIED_FAILURE")
        self.check_accounting(result)

    def test_publication_failures_use_shared_core_and_keep_verification(self):
        original = publication.os.replace
        def fail(source, target):
            original(source, target)
            if target.name == "terminal.json": raise OSError("TERMINAL_AFTER_RENAME")
        with patch.object(publication.os, "replace", side_effect=fail): result = self.run_neutral()
        self.assertEqual(result["primary_error"], "TERMINAL_AFTER_RENAME")
        self.assertFalse(result["evaluation_allowed"])
        self.assertTrue({"record.json", "verification.json", "error.json", "terminal.json", "terminal-minimal.json"} <= {p.name for p in self.output.iterdir()})
        self.check_accounting(result)

    def test_staging_cleanup_failure_is_counted_and_no_second_temporary_is_created(self):
        original = Path.unlink
        writes = []
        def fail(path, data):
            writes.append(path.name); path.write_bytes(data[:73]); raise OSError("PARTIAL_WRITE")
        def cannot_clean(path, *args, **kwargs):
            if path.name == "publication.tmp": raise OSError("CLEANUP_FAILURE")
            return original(path, *args, **kwargs)
        with patch.object(publication, "_write", side_effect=fail), patch.object(Path, "unlink", cannot_clean): result = self.run_neutral()
        self.assertEqual(writes, ["publication.tmp"])
        self.assertEqual(result["actual"]["categories"]["staging"], 73)
        self.assertTrue(result["missing_durable_evidence"])
        self.check_accounting(result)

    def test_neutral_wrapper_still_rejects_materialized_records(self):
        self.run_neutral()
        record = publication.codec.loads((self.output / "record.json").read_bytes())
        # Retain its old scope guard; the V8 subclass alone accepts these records.
        instance = object.__new__(publication._Publication)
        with self.assertRaisesRegex(ValueError, "V7_NEUTRAL_RECORD_REQUIRED"): instance.check_record(record)


if __name__ == "__main__": unittest.main()
