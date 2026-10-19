"""Neutral, previously generated inputs. Publication itself executes no story."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import _s2uc_publication_v7 as publication
from tools import _s2uc_inventory_v7 as inventory
from tools import _s2uc_prestart_v7 as prestart
from tools import _s2uc_resource_contract_v7 as ledger
from tools import _s2uc_record_codec as codec
from tools import _s2uc_neutral_connection as connection
from tools import _s2uc_run_entry as entry
from tools import s2uc_run_bound_once as starter
from tests.test_s2uc_neutral_connection import neutral_materializer
from tests.test_s2uc_prestart_v7 import fixture


class V7PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.current = inventory.current()
        manifest = prestart.science_manifest.manifest()
        cls.record = codec.dumps(connection.execute(manifest, neutral_materializer))
        calls = [0]
        def fail(endpoint):
            calls[0] += 1
            if calls[0] == 23:
                raise ValueError("NEUTRAL_INPUT_FAILURE")
            return neutral_materializer(endpoint)
        cls.failed_record = codec.dumps(connection.execute(manifest, fail))

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.binding, _ = fixture(self.root / "bundle", current=self.current)
        self.output = self.root / "output"

    def run_publication(self, data=None):
        with patch.object(connection, "execute", side_effect=AssertionError("new story forbidden")) as execute:
            result = publication.publish_neutral(self.record if data is None else data, self.binding, self.output)
        execute.assert_not_called()
        return result

    def check_files(self, result, names, *, audit=True):
        self.assertEqual({r["path"] for r in result["result_inventory"]}, set(names))
        actual_files = {p.name: p.read_bytes() for p in self.output.iterdir()}
        self.assertEqual(set(actual_files), set(names))
        for row in result["result_inventory"]:
            self.assertEqual(row["bytes"], len(actual_files[row["path"]]))
            self.assertEqual(row["sha256"], inventory.sha(actual_files[row["path"]]))
            self.assertEqual(row["category"], prestart.RESULT_FILES[row["path"]])
        amounts = result["actual"]["categories"]
        for cat in ("record", "verification", "error", "terminal", "minimal", "staging"):
            expected = sum(len(data) for name, data in actual_files.items() if prestart.RESULT_FILES[name] == cat)
            self.assertEqual(amounts[cat], expected)
        self.assertEqual(result["actual"]["total_bytes"], sum(r["bytes"] for r in result["inputs"]) + sum(map(len, actual_files.values())))
        self.assertEqual(amounts["static_shared"] + amounts["error"] + amounts["terminal"] + amounts["minimal"], result["actual"]["main_accounts"]["shared"])
        if audit:
            fresh = publication.audit(self.binding, self.output)
            self.assertEqual(fresh["actual"], result["actual"])
            self.assertEqual(fresh["result_inventory"], result["result_inventory"])
        self.assertTrue(result["accounting_complete"])
        self.assertTrue(result["actual"]["within_limits"])

    def test_success_reloads_record_and_publishes_separate_verification(self):
        before = {p.name: p.read_bytes() for p in self.binding.parent.iterdir()}
        with patch.object(publication.verification, "verify", wraps=publication.verification.verify) as verify:
            result = self.run_publication()
        verify.assert_called_once()
        self.assertEqual(result["status"], "CLOSED_NEUTRAL_VERIFIED")
        self.assertTrue(result["evaluation_allowed"])
        self.assertEqual(result["missing_durable_evidence"], [])
        self.check_files(result, {"record.json", "verification.json", "terminal.json"})
        terminal = json.loads((self.output / "terminal.json").read_bytes())
        proof_data = (self.output / "verification.json").read_bytes()
        self.assertEqual(terminal["verification"], {"path": "verification.json", "bytes": len(proof_data), "sha256": inventory.sha(proof_data)})
        self.assertNotIn("technical", terminal)
        self.assertNotIn("evaluation", terminal)
        self.assertEqual(json.loads(proof_data)["technical"]["status"], "VERIFIED")
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.binding.parent.iterdir()})

    def test_oversized_record_stops_before_record_publication_or_evaluation(self):
        with patch.object(publication.evaluation, "evaluate") as evaluate:
            result = self.run_publication(b"x" * (ledger.RESERVES["record"] + 1))
        evaluate.assert_not_called()
        self.assertEqual(result["primary_error"], "V7_RECORD_BUDGET_EXCEEDED")
        self.assertFalse(result["evaluation_allowed"])
        self.check_files(result, {"error.json", "terminal.json"})
        error = json.loads((self.output / "error.json").read_bytes())
        self.assertEqual(error["candidate_record"]["bytes"], 245761)

    def test_read_failure_after_record_publication_blocks_verification_and_evaluation(self):
        original = publication._read
        reads = [0]
        def fail(path):
            if path.name == "record.json":
                reads[0] += 1
                if reads[0] == 2:
                    raise OSError("NEUTRAL_RECORD_READ_FAILURE")
            return original(path)
        with patch.object(publication, "_read", side_effect=fail), patch.object(publication.verification, "verify") as verify, patch.object(publication.evaluation, "evaluate") as evaluate:
            result = self.run_publication()
        verify.assert_not_called(); evaluate.assert_not_called()
        self.assertEqual(result["primary_error"], "NEUTRAL_RECORD_READ_FAILURE")
        self.check_files(result, {"record.json", "error.json", "terminal.json"})

    def test_changed_reloaded_record_is_rejected(self):
        original = publication._read
        reads = [0]
        def change(path):
            data = original(path)
            if path.name == "record.json":
                reads[0] += 1
                if reads[0] == 2:
                    return data + b" "
            return data
        with patch.object(publication, "_read", side_effect=change), patch.object(publication.evaluation, "evaluate") as evaluate:
            result = self.run_publication()
        evaluate.assert_not_called()
        self.assertEqual(result["primary_error"], "V7_RECORD_RELOAD_CHANGED")
        self.check_files(result, {"record.json", "error.json", "terminal.json"})

    def test_technical_verification_failure_preserves_primary_and_blocks_evaluation(self):
        with patch.object(publication.verification, "verify", side_effect=ValueError("NEUTRAL_VERIFY_FAILURE")), patch.object(publication.evaluation, "evaluate") as evaluate:
            result = self.run_publication()
        evaluate.assert_not_called()
        self.assertEqual(result["primary_error"], "NEUTRAL_VERIFY_FAILURE")
        self.assertIsNone(result["evaluation"])
        self.check_files(result, {"record.json", "error.json", "terminal.json"})

    def test_changed_verified_bytes_cannot_be_rebound_to_success(self):
        for phase in ("verify", "evaluate", "receipt"):
            self.output = self.root / phase
            owner = {"verify": publication.verification, "evaluate": publication.evaluation,
                     "receipt": publication._Publication}[phase]
            original = getattr(owner, phase)
            def change(*args, **kwargs):
                value = original(*args, **kwargs)
                if phase != "receipt" or args[1] == "CLOSED_NEUTRAL_VERIFIED":
                    name = "verification.json" if phase == "receipt" else "record.json"
                    with (self.output / name).open("ab") as stream: stream.write(b" ")
                return value
            with self.subTest(phase=phase), patch.object(owner, phase, change):
                result = self.run_publication()
            self.assertFalse(result["evaluation_allowed"])
            self.assertIsNone(result["evaluation"])
            names = {"record.json", "error.json", "terminal.json"}
            if phase != "verify": names |= {"verification.json", "terminal-minimal.json"}
            self.check_files(result, names)

    def test_failed_input_is_verified_without_evaluation_and_keeps_input_primary(self):
        primary = codec.loads(self.failed_record)["failure"]["code"]
        with patch.object(publication.evaluation, "evaluate") as evaluate:
            result = self.run_publication(self.failed_record)
        evaluate.assert_not_called()
        self.assertEqual(result["primary_error"], primary)
        self.check_files(result, {"record.json", "verification.json", "error.json", "terminal.json"})
        self.assertEqual(json.loads((self.output / "verification.json").read_bytes())["technical"]["status"], "VERIFIED_FAILURE")

    def test_rename_failure_after_verification_keeps_published_verification_counted(self):
        original = publication.os.replace
        def after(source, target):
            original(source, target)
            if target.name == "verification.json":
                raise OSError("NEUTRAL_AFTER_VERIFICATION_RENAME")
        with patch.object(publication.os, "replace", side_effect=after):
            result = self.run_publication()
        self.assertEqual(result["primary_error"], "NEUTRAL_AFTER_VERIFICATION_RENAME")
        self.assertFalse(result["evaluation_allowed"])
        self.assertIsNone(result["evaluation"])
        self.check_files(result, {"record.json", "verification.json", "error.json", "terminal.json"})

    def test_post_terminal_failure_counts_error_terminal_and_minimal_together(self):
        original = publication.os.replace
        def after(source, target):
            original(source, target)
            if target.name == "terminal.json":
                raise OSError("NEUTRAL_AFTER_TERMINAL_RENAME")
        with patch.object(publication.os, "replace", side_effect=after):
            result = self.run_publication()
        self.assertEqual(result["primary_error"], "NEUTRAL_AFTER_TERMINAL_RENAME")
        self.assertFalse(result["evaluation_allowed"])
        self.assertEqual(result["missing_durable_evidence"], [])
        self.check_files(result, {"record.json", "verification.json", "error.json", "terminal.json", "terminal-minimal.json"})

    def test_partial_write_cleanup_failure_retains_one_counted_staging_file(self):
        original_unlink = Path.unlink
        writes = []
        def partial(path, data):
            writes.append(path.name)
            path.write_bytes(data[:113])
            raise OSError("NEUTRAL_PARTIAL_WRITE")
        def cannot_clean(path, *args, **kwargs):
            if path.name == publication.STAGING:
                raise OSError("NEUTRAL_CLEANUP_FAILURE")
            return original_unlink(path, *args, **kwargs)
        with patch.object(publication, "_write", side_effect=partial), patch.object(Path, "unlink", cannot_clean):
            result = self.run_publication()
        self.assertEqual(writes, ["publication.tmp"])
        self.assertEqual(result["primary_error"], "NEUTRAL_PARTIAL_WRITE")
        self.assertEqual(result["actual"]["categories"]["staging"], 113)
        self.assertEqual(result["missing_durable_evidence"], ["error.json", "terminal.json or terminal-minimal.json"])
        self.assertTrue(any(r["error"] == "NEUTRAL_CLEANUP_FAILURE" for r in result["secondary_errors"]))
        self.check_files(result, {"publication.tmp"})

    def test_rename_failure_cleanup_then_error_receipts_use_same_staging_name(self):
        original = publication.os.replace
        names = []
        def fail(source, target):
            names.append(source.name)
            if target.name == "record.json":
                raise OSError("NEUTRAL_RENAME_FAILURE")
            original(source, target)
        with patch.object(publication.os, "replace", side_effect=fail):
            result = self.run_publication()
        self.assertEqual(set(names), {"publication.tmp"})
        self.assertEqual(result["primary_error"], "NEUTRAL_RENAME_FAILURE")
        self.assertEqual(result["staging_cleanup_observations"][0]["bytes"], len(self.record))
        self.check_files(result, {"error.json", "terminal.json"})

    def test_error_receipt_failure_does_not_replace_primary(self):
        original = publication.os.replace
        def fail(source, target):
            if target.name == "error.json":
                raise OSError("NEUTRAL_ERROR_RECEIPT_FAILURE")
            original(source, target)
        with patch.object(publication.os, "replace", side_effect=fail), patch.object(publication.verification, "verify", side_effect=ValueError("FIRST_FAILURE")):
            result = self.run_publication()
        self.assertEqual(result["primary_error"], "FIRST_FAILURE")
        self.assertEqual(result["missing_durable_evidence"], ["error.json"])
        self.check_files(result, {"record.json", "terminal.json"})

    def test_partial_write_with_successful_cleanup_leaves_only_error_closure(self):
        original = publication._write
        calls = [0]
        def fail(path, data):
            calls[0] += 1
            if calls[0] == 1:
                path.write_bytes(data[:19])
                raise OSError("NEUTRAL_PARTIAL_WRITE")
            original(path, data)
        with patch.object(publication, "_write", side_effect=fail):
            result = self.run_publication()
        self.assertEqual(result["staging_cleanup_observations"][0]["bytes"], 19)
        self.assertEqual(result["primary_error"], "NEUTRAL_PARTIAL_WRITE")
        self.check_files(result, {"error.json", "terminal.json"})

    def test_terminal_partial_write_and_cleanup_failure_keep_verification_and_staging(self):
        original_write, original_unlink = publication._write, Path.unlink
        def fail(path, data):
            if b'CLOSED_NEUTRAL_VERIFIED' in data:
                path.write_bytes(data[:71])
                raise OSError("NEUTRAL_TERMINAL_WRITE")
            original_write(path, data)
        def cannot_clean(path, *args, **kwargs):
            if path.name == publication.STAGING:
                raise OSError("NEUTRAL_CLEANUP_FAILURE")
            return original_unlink(path, *args, **kwargs)
        with patch.object(publication, "_write", side_effect=fail), patch.object(Path, "unlink", cannot_clean):
            result = self.run_publication()
        self.assertFalse(result["evaluation_allowed"])
        self.assertEqual(result["primary_error"], "NEUTRAL_TERMINAL_WRITE")
        self.assertEqual(result["actual"]["categories"]["staging"], 71)
        self.check_files(result, {"record.json", "verification.json", "publication.tmp"})

    def test_verification_reserve_and_corrupt_stage_fail_before_publication(self):
        with patch.object(publication.evaluation, "evaluate", return_value={"oversize": "x" * 131072}):
            result = self.run_publication()
        self.assertEqual(result["primary_error"], "V7_PUBLICATION_BUDGET_EXCEEDED")
        self.check_files(result, {"record.json", "error.json", "terminal.json"})
        self.output = self.root / "second-output"
        original = publication._write
        calls = [0]
        def corrupt(path, data):
            calls[0] += 1
            original(path, data if calls[0] > 1 else b"corrupt")
        with patch.object(publication, "_write", side_effect=corrupt):
            result = self.run_publication()
        self.assertEqual(result["primary_error"], "V7_STAGING_BYTES_CHANGED")
        self.check_files(result, {"error.json", "terminal.json"})

    def test_existing_folder_unchanged_and_callable_rejected(self):
        self.output.mkdir()
        (self.output / "keep.txt").write_bytes(b"unchanged")
        with self.assertRaisesRegex(ValueError, "V7_OUTPUT_ALREADY_EXISTS"):
            self.run_publication()
        self.assertEqual({p.name: p.read_bytes() for p in self.output.iterdir()}, {"keep.txt": b"unchanged"})
        with self.assertRaisesRegex(ValueError, "V7_RECORD_BYTES_REQUIRED"):
            publication.publish_neutral(lambda: self.record, self.binding, self.root / "not-created")
        self.assertFalse((self.root / "not-created").exists())

    def test_unknown_result_files_are_measured_and_invalidate_accounting(self):
        self.run_publication()
        (self.output / "extra.tmp").write_bytes(b"unknown")
        result = publication.audit(self.binding, self.output)
        self.assertFalse(result["accounting_complete"])
        self.assertEqual(result["unclassified_bytes"], 7)
        self.assertEqual(result["observed_total_bytes"], result["actual"]["total_bytes"] + 7)
        self.assertIsNone(next(r for r in result["result_inventory"] if r["path"] == "extra.tmp")["category"])

    def test_prestart_change_during_publication_stops_and_reports_missing_evidence(self):
        original = publication.os.replace
        def change(source, target):
            original(source, target)
            if target.name == "record.json":
                with (self.binding.parent / "manifest.json").open("ab") as stream:
                    stream.write(b" ")
        with patch.object(publication.os, "replace", side_effect=change), patch.object(publication.evaluation, "evaluate") as evaluate:
            result = self.run_publication()
        evaluate.assert_not_called()
        self.assertFalse(result["prestart_unchanged"])
        self.assertFalse(result["accounting_complete"])
        self.assertFalse(result["evaluation_allowed"])
        self.assertTrue(result["missing_durable_evidence"])

    def test_starter_still_closed_with_publication_in_fixed_inventory(self):
        names = {r["path"] for r in self.current["files"]}
        self.assertTrue({"tools/_s2uc_publication_v7.py", "tests/test_s2uc_publication_v7.py"} <= names)
        self.assertLessEqual(self.current["code_bytes"], 655360)
        entry.MAIN_GATE = False
        calls = [0]
        with patch.object(starter.adapter, "SourceAdapter") as adapter, patch.object(entry, "run_bound_once") as execute:
            with self.assertRaisesRegex(ValueError, "V7_EXECUTION_NOT_CONNECTED"):
                starter.start(self.output, lambda _: calls.__setitem__(0, calls[0] + 1), authorize=True, binding_file=self.binding)
        self.assertEqual(calls[0], 0); adapter.assert_not_called(); execute.assert_not_called()
        self.assertFalse(entry.MAIN_GATE)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
