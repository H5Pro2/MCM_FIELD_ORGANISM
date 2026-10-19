"""V9 neutral-only connection and adversarial source/evidence tests."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import uuid
from contextlib import ExitStack
from unittest.mock import patch

from tools import _s2uc_source_execution_binding as b
from tools import _s2uc_source_context_v9 as context
from tools import _s2uc_source_execution as execution
from tools import _s2uc_qualification_v9 as qualification
from tools import _s2uc_resources_v9 as resources
from tools import _s2nu_private_source_binding as nu
from tools import _s2uc_record_codec as codec


def write(path, value):
    path.write_bytes(b.old.canonical(value))


def seal(bundle, inv, rid, output):
    ledger = bundle / "resource-ledger.json"
    if not ledger.exists():
        ledger.write_bytes(b"{}")
    for _ in range(16):
        refs = {}
        for role, (ns, name, category, _) in b.FILES.items():
            ref, _, _ = b.discovery.read_file(b.discovery.ROOT if ns == "project" else bundle, name)
            refs[role] = {**ref, "namespace": ns, "category": category}
        value = {"version": b.VERSION, "contract_id": resources.CONTRACT_ID, "run_id": rid,
                 "output": output.resolve().as_posix(), "authorization": {"kind": "ONE_NEUTRAL_EXECUTION",
                 "max_uses": 1, "payload": "SYNTHETIC_NONZERO_F32LE", "real_sources": False}, "artifacts": refs}
        path = bundle / b.FILENAME
        write(path, value)
        data = b.old.canonical(b.accounting(inv["code_bytes"], {k: r["bytes"] for k, r in refs.items()}, path.stat().st_size))
        if ledger.read_bytes() == data:
            return path
        ledger.write_bytes(data)
    raise AssertionError("fixture ledger failed to converge")


def fixture(root, inv):
    rid = "S2UC-V9-NEUTRAL-" + uuid.uuid4().hex
    bundle, output = root / "bundle", root / rid
    bundle.mkdir()
    for role, value in {"manifest": b.manifest(), "source_binding": b.sources(), "inventory": inv,
                        "resource_contract": b.contract(), **b.evidence(inv)}.items():
        write(bundle / b.FILES[role][1], value)
    return seal(bundle, inv, rid, output), rid, output


class SourceExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inv = b.current()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path, self.rid, self.output = fixture(self.root, self.inv)
        self.calls = []
        self.nu = patch.object(nu, "pcm_window", side_effect=AssertionError("REAL_PRODUCTION_FORBIDDEN")).start()
        self.addCleanup(patch.stopall)

    def supply(self, endpoint):
        self.calls.append(endpoint["source_id"])
        return context.neutral_payload(endpoint["source_id"])

    def run_neutral(self, supply=None):
        result = execution.run_neutral(self.path, supply or self.supply, run_id=self.rid, output_directory=self.output)
        self.assertFalse(execution.core.GATE)
        self.nu.assert_not_called()
        self.assertTrue(result["accounting_complete"])
        self.assertTrue(result["actual"]["within_limits"])
        self.assertTrue(all(r["closed"] for r in result["owner_cleanup"]))
        files = {p.name: p.read_bytes() for p in self.output.iterdir()}
        self.assertEqual(set(files), {r["path"] for r in result["result_inventory"]})
        for row in result["result_inventory"]:
            self.assertEqual((len(files[row["path"]]), b.discovery.sha(files[row["path"]])), (row["bytes"], row["sha256"]))
        self.assertEqual(result["actual"]["total_bytes"], sum(r["bytes"] for r in result["inputs"]) + sum(map(len, files.values())))
        return result

    def test_fixed_sources_targets_profiles_and_order(self):
        value = context.source_context()
        self.assertEqual([r["source_id"] for r in value["rows"]], list(context.science.IDS.values()))
        self.assertEqual(len(value["adapter"]["endpoint_uses"]), 58)
        context.validate_source_context(value)
        for mutate in (
            lambda x: x["rows"].reverse(), lambda x: x["rows"].pop(),
            lambda x: x["rows"][0].update(recipe="changed"),
            lambda x: x["rows"][0].update(pcm_sha256="0" * 64),
            lambda x: x["manifest"]["events"][0]["endpoint"].update(profile="0" * 64),
            lambda x: x["manifest"]["events"][0]["endpoint"].update(window_start_sample=0),
            lambda x: x["adapter"]["endpoint_uses"].reverse(),
            lambda x: x.update(targets={}), lambda x: x.update(real_execution_authorized=True),
        ):
            bad = copy.deepcopy(value)
            mutate(bad)
            with self.assertRaisesRegex(ValueError, "SOURCE_CONTEXT_INVALID"):
                context.validate_source_context(bad)

    def test_public_real_entry_unconditionally_closed(self):
        value = context.source_context()
        with patch.object(context, "prepare_nu_supplier") as supplier:
            with self.assertRaisesRegex(ValueError, "V9_REAL_EXECUTION_DISABLED"):
                execution.start_real(value)
            supplier.assert_not_called()
        self.assertFalse(execution.legacy_entry.MAIN_GATE)
        self.assertFalse(self.output.exists())

    def test_prepared_supplier_is_lazy_fixed_five_uncached_no_copy(self):
        value = context.source_context()
        supplier = context.prepare_nu_supplier(value)
        self.nu.assert_not_called()
        payload = bytearray(19200)
        self.nu.side_effect = None
        self.nu.return_value = payload
        for endpoint in value["adapter"]["sources"].values():
            for _ in range(2):
                self.assertIs(supplier(endpoint), payload)
        self.assertEqual(self.nu.call_count, 10)
        specs = [call.args[0] for call in self.nu.call_args_list]
        self.assertEqual(specs, [nu.WindowSpec(2, i) for i in range(5) for _ in range(2)])
        for key, val in (("source_id", "nu-s03-w00"), ("pcm_sha256", "0" * 64)):
            bad = dict(next(iter(value["adapter"]["sources"].values())))
            bad[key] = val
            with self.assertRaises(ValueError):
                supplier(bad)
        self.assertEqual(self.nu.call_count, 10)

    def test_neutral_binding_rejects_real_null_legacy_and_missing_authorization(self):
        original = json.loads(self.path.read_bytes())
        for auth in ({}, {**original["authorization"], "real_sources": True},
                     {**original["authorization"], "payload": "ZERO_PCM_F32LE"}):
            write(self.path, {**original, "authorization": auth})
            with self.assertRaises(ValueError):
                execution.run_neutral(self.path, self.supply, run_id=self.rid, output_directory=self.output)
        write(self.path, {**original, "version": "s2uc.execution-binding.v8"})
        with self.assertRaises(ValueError):
            b.validate(self.path)
        self.assertFalse(self.calls)
        self.assertFalse(self.output.exists())

    def test_neutral_binder_rejects_resealed_real_manifest_and_stale_inventory(self):
        write(self.path.parent / "manifest.json", context.science.manifest())
        seal(self.path.parent, self.inv, self.rid, self.output)
        with self.assertRaises(ValueError):
            b.validate(self.path)
        write(self.path.parent / "manifest.json", b.manifest())
        wrong = copy.deepcopy(self.inv)
        wrong["files"].pop()
        write(self.path.parent / "dependency-inventory.json", wrong)
        seal(self.path.parent, wrong, self.rid, self.output)
        with self.assertRaises(ValueError):
            b.validate(self.path)

    def test_nonzero_58_receipts_five_vectors_same_arm_values(self):
        seen = {}
        def observe(cls, method, role):
            original = getattr(cls, method)
            def call(arm, frame):
                seen.setdefault(frame.ordinal, {})[role] = id(frame.values)
                return original(arm, frame)
            return patch.object(cls, method, call)
        with ExitStack() as stack:
            for cls, role in ((execution.core.connection.ub.ImmediateTwArm, "left"),
                              (execution.core.connection.ub.CandidateConfirmationArm, "right")):
                for method in ("form", "hint"):
                    stack.enter_context(observe(cls, method, role))
            result = self.run_neutral()
        self.assertEqual(len(seen), 58)
        self.assertTrue(all(row["left"] == row["right"] for row in seen.values()))
        self.assertEqual(len(self.calls), 58)
        self.assertTrue(result["evaluation_allowed"], result.get("primary_error"))
        self.assertEqual(result["candidate_gain_loss_status"], "NOT_MEASURED")
        record = codec.loads((self.output / "record.json").read_bytes())
        rows = [e for s in record["stories"] for e in s["events"] if e["kind"] != "CLOSE"]
        self.assertEqual(len({tuple(r["values_hex"]) for r in rows}), 5)
        self.assertTrue(all(any(float.fromhex(v) != 0 for v in r["values_hex"]) for r in rows))
        self.assertEqual(record["source_completion"]["counters"], {"pcm_hashes": 58, "audio_analyses": 58, "nj_projections": 58})
        self.assertEqual(result["evaluation"]["candidate_gains"], [])
        self.assertEqual(result["evaluation"]["candidate_losses"], [])
        old = object.__new__(execution.core.publication._Publication)
        with self.assertRaisesRegex(ValueError, "V7_NEUTRAL_RECORD_REQUIRED"):
            old.check_record(record)
        damaged = copy.deepcopy(record)
        damaged["stories"][0]["events"][0]["materialization"]["subnormal_band_indices"] = [0, 2, 47]
        with self.assertRaises(ValueError):
            execution.core.verify_materialized(damaged, b.manifest(), record["source_completion"], record["owner_cleanup"])

    def test_nonzero_pending_receipt_and_owner_constructor_failure(self):
        with patch.object(execution.core.connection.ub.CandidateConfirmationArm, "form",
                          side_effect=execution.core.connection.S2UCConnectionError("SECOND_ARM_FAILURE")):
            result = self.run_neutral()
        self.assertEqual(result["primary_error"], "SECOND_ARM_FAILURE")
        record = codec.loads((self.output / "record.json").read_bytes())
        self.assertIsNotNone(record["source_completion"]["pending"])
        self.assertEqual(record["source_completion"]["successes"], 1)
        self.assertEqual(record["stories"][0]["events"], [])
        with self.assertRaisesRegex(ValueError, "ALREADY_USED"):
            self.run_neutral()

    def test_constructor_failure_zero_sources_closes_owners(self):
        cls = execution.core.connection.ub.CandidateConfirmationArm
        original = cls.__init__
        def fail(arm, *args):
            original(arm, *args)
            raise ValueError("V9_CONSTRUCTOR_FAILURE")
        with patch.object(cls, "__init__", fail):
            result = self.run_neutral()
        self.assertEqual(result["primary_error"], "V9_CONSTRUCTOR_FAILURE")
        self.assertEqual(self.calls, [])
        self.assertEqual(len(result["owner_cleanup"]), 2)

    def test_publication_terminal_failure_counts_minimal_and_record(self):
        publication = execution.core.publication
        original = publication.os.replace
        def fail(source, target):
            original(source, target)
            if target.name == "terminal.json":
                raise OSError("V9_TERMINAL_AFTER_RENAME")
        # A first-source failure keeps this publication countertest source-free.
        def supplier(endpoint):
            raise ValueError("V9_PRIMARY_SUPPLIER")
        with patch.object(publication.os, "replace", side_effect=fail):
            result = self.run_neutral(supplier)
        self.assertFalse(result["evaluation_allowed"])
        self.assertEqual(result["primary_error"], "ValueError")
        self.assertTrue({"record.json", "verification.json", "error.json", "terminal.json", "terminal-minimal.json"}
                        <= {p.name for p in self.output.iterdir()})

    def test_staging_failure_counts_all_remaining_bytes(self):
        original = Path.unlink
        def fail(path, data):
            path.write_bytes(data[:73])
            raise OSError("V9_PARTIAL_WRITE")
        def no_cleanup(path, *args, **kwargs):
            if path.name == "publication.tmp":
                raise OSError("V9_CLEANUP_FAIL")
            return original(path, *args, **kwargs)
        with patch.object(execution.core.publication, "_write", side_effect=fail), patch.object(Path, "unlink", no_cleanup):
            result = self.run_neutral(lambda endpoint: bytearray(19200))
        self.assertEqual(result["actual"]["categories"]["staging"], 73)
        self.assertTrue(result["missing_durable_evidence"])

    def test_source_preparation_reader_has_no_authority(self):
        path = self.root / "source-context.json"
        write(path, context.source_context())
        with patch.object(qualification, "read", return_value={"real_execution_authorized": False, "code_bytes": self.inv["code_bytes"], "artifacts": []}):
            result = b.read_source_preparation(path, self.root / "not-an-authorization.json")
            self.assertFalse(result["real_execution_authorized"])
            self.assertEqual(result["status"], "PREPARATION_ONLY")
            bad = context.source_context()
            bad["profiles"] = {}
            write(path, bad)
            with self.assertRaises(ValueError):
                b.read_source_preparation(path, self.root / "not-an-authorization.json")

    def test_failure_58_retains_57_and_primary(self):
        def supplier(endpoint):
            if len(self.calls) == 57:
                self.calls.append("failure")
                raise MemoryError("INJECTED")
            return self.supply(endpoint)
        result = self.run_neutral(supplier)
        self.assertEqual(result["source_completion"]["attempts"], 58)
        self.assertEqual(result["source_completion"]["successes"], 57)
        self.assertEqual(result["primary_error"], "MemoryError")
        self.assertFalse(result["evaluation_allowed"])

    def test_payload_hash_mismatch_before_receptor(self):
        result = self.run_neutral(lambda endpoint: bytearray(19200))
        self.assertFalse(result["evaluation_allowed"])
        self.assertEqual(result["source_completion"]["counters"], {"pcm_hashes": 1, "audio_analyses": 0, "nj_projections": 0})

    def test_codec_failure_closes_owners_and_gate(self):
        with patch.object(codec, "dumps", side_effect=ValueError("V9_CODEC_FAIL")):
            result = self.run_neutral()
        self.assertEqual(result["primary_error"], "V9_CODEC_FAIL")
        self.assertFalse(result["evaluation_allowed"])

    def test_nonzero_codec_vectors_flags_and_boundary(self):
        value = {"values_hex": [(i / 97).hex() for i in range(48)],
                 "nested": {"values_hex": [(-i / 103).hex() for i in range(48)]},
                 "subnormal_band_indices": list(range(48)), "underflow_band_indices": [0, 2, 47]}
        self.assertEqual(codec.loads(codec.dumps(value)), value)
        initial = b.validate(self.path)
        pub = execution._Publication(self.path, initial)
        self.output.mkdir()
        # Exact reserve is accepted by byte admission; +1 cannot be published.
        pub.atomic("record.json", b" " * resources.RESERVES["record"])
        self.assertEqual((self.output / "record.json").stat().st_size, resources.RESERVES["record"])
        with self.assertRaisesRegex(ValueError, "PUBLICATION_BUDGET_EXCEEDED"):
            pub.atomic("record.json", b" " * (resources.RESERVES["record"] + 1))
        failure = pub.failure(ValueError("NEUTRAL_INVALID_RECORD"))
        self.assertFalse(failure["evaluation_allowed"])

    def test_qualification_fixture_and_mutations_never_authorize(self):
        ids = b.test_ids()
        log = self.root / "tests.log"
        log.write_text("".join(name + " PASS\n" for name in ids), newline="\n")
        ref, _, _ = b.discovery.read_file(self.root, log.name)
        write(self.root / "dependency-inventory.json", self.inv)
        invref, _, _ = b.discovery.read_file(self.root, "dependency-inventory.json")
        value = {"version": "s2uc.executed-neutral-summary.v9", "scope": "EXECUTED_NEUTRAL_DEVELOPMENT",
                 "inventory_sha256": b.discovery.sha(b.old.canonical(self.inv)),
                 "test_ids_sha256": b.discovery.sha(b.old.canonical(ids)), "inventory": invref,
                 "log": ref, "tests_run": len(ids),
                 "exit_code": 0, "formal_qualification": False, "real_execution_authorized": False}
        path = self.root / "evidence.json"
        write(path, value)
        self.assertFalse(qualification.read(path)["real_execution_authorized"])
        for mutate in (lambda x: x.update(scope="SYNTHETIC_FIXTURE_NOT_EXECUTED"),
                       lambda x: x.update(inventory_sha256="0" * 64),
                       lambda x: x.update(test_ids_sha256="0" * 64), lambda x: x.update(formal_qualification=True),
                       lambda x: x.update(real_execution_authorized=True),
                       lambda x: x.update(exit_code=1)):
            bad = copy.deepcopy(value)
            mutate(bad)
            write(path, bad)
            with self.assertRaises(ValueError):
                qualification.read(path)
        write(path, b.evidence(self.inv)["qualification_summary"])
        with self.assertRaises(ValueError):
            qualification.read(path)

    def test_inventory_complete_tools_and_limits_unchanged(self):
        names = {r["path"] for r in self.inv["files"]}
        self.assertTrue(set(b.TOOLS) <= names)
        self.assertTrue(set(b.TESTS) <= names)
        self.assertLessEqual(self.inv["code_bytes"], 851968)
        self.assertEqual({k: v for k, v in resources.LIMITS.items() if k != "code"},
                         {k: v for k, v in b.old.ledger.LIMITS.items() if k != "code"})
        self.assertEqual(resources.RESERVES, b.old.ledger.RESERVES)
