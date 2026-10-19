import copy
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from tools import _s2ty_real_run_entry as entry
from tools import _s2ty_real_source_supplier as supplier
from tools import _s2ty_evaluation as evaluation
from tools import _s2ty_run_envelope as envelope
from tools import _s2ty_source_time_binding as source_time


QUALIFICATION = "reports/s2ty/s2ty-neutral-overall-qualification-20260920-03/qualification-result.json"


def neutral_manifest():
    manifest = copy.deepcopy(source_time.source_manifest())
    payload = bytes(19_200)
    for event in manifest["events"]:
        if "endpoint" in event:
            event["endpoint"]["pcm_sha256"] = hashlib.sha256(payload).hexdigest()
    return source_time.reseal_manifest(manifest)


def write_binding(path, manifest):
    source = {
        "source_plan_sha256": "neutral-source-plan",
        "source_execution_digest": "neutral-source-execution",
        "profile": manifest["profile"],
        "endpoint_ordinals": [item["ordinal"] for item in manifest["events"] if "endpoint" in item],
    }
    qualification_path = entry.ROOT / QUALIFICATION
    qualification = {"path": QUALIFICATION, "sha256": hashlib.sha256(qualification_path.read_bytes()).hexdigest(), "bytes": qualification_path.stat().st_size}
    value = {
        "schema": "s2ty.real-run-binding.v1",
        "run_id": "s2ty-neutral-entry",
        "source_manifest_digest": manifest["binding_digest"],
        "source_binding": source,
        "owners": {"adapter": "neutral-adapter", "direct": "neutral-direct"},
        "code_hashes": envelope.code_hashes(),
        "qualification_dependencies": [{"path": QUALIFICATION, "sha256": qualification["sha256"]}],
        "active_dependencies": [qualification],
        "budget": {
            "active_reference_bytes": qualification["bytes"],
            "metadata_reserved_bytes": 8192,
            "success_publication_reserved_bytes": 196608,
            "failure_publication_reserved_bytes": 196608,
            "terminal_error_reserved_bytes": 8192,
            "verification_reserved_bytes": 32768,
        },
    }
    value["binding_digest"] = entry._digest(value)
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    return source


class Tests(unittest.TestCase):
    def setUp(self):
        entry.MAIN_GATE = False
        entry.USED = False

    def tearDown(self):
        entry.MAIN_GATE = False
        entry.USED = False

    def _run(self, *, outer_failure=False, supplier_failure=False, supplier_initialization_failure=False, execution_failure=False, evaluation_failure=False, success_budget=None, failure_budget=None):
        manifest = neutral_manifest()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            binding_path, output = root / "binding.json", root / "output"
            resolved = write_binding(binding_path, manifest)
            if success_budget is not None:
                document = json.loads(binding_path.read_text(encoding="utf-8"))
                document["budget"]["success_publication_reserved_bytes"] = success_budget
                if failure_budget is not None:
                    document["budget"]["failure_publication_reserved_bytes"] = failure_budget
                document["binding_digest"] = entry._digest({key: value for key, value in document.items() if key != "binding_digest"})
                binding_path.write_text(json.dumps(document, sort_keys=True, separators=(",", ":")), encoding="utf-8")

            def source_binding(value):
                self.assertIs(value, manifest)
                return {**resolved, "source_rows": {ordinal: {} for ordinal in resolved["endpoint_ordinals"]}}

            calls = 0

            def payload_supplier(value):
                self.assertIs(value, manifest)

                def supply(ordinal, endpoint):
                    nonlocal calls
                    calls += 1
                    if supplier_failure and calls == 3:
                        raise OSError("neutral-source-stop")
                    return bytearray(19_200)

                return supply

            supplier_factory = RuntimeError("neutral-supplier-initialization") if supplier_initialization_failure else payload_supplier
            evaluator = RuntimeError("neutral-evaluation") if evaluation_failure else evaluation.evaluate_verified
            with patch.object(source_time, "source_manifest", return_value=manifest), patch.object(
                supplier, "source_binding", side_effect=source_binding
            ), patch.object(supplier, "create_payload_supplier", side_effect=supplier_factory), patch.object(
                evaluation, "evaluate_verified", side_effect=evaluator
            ):
                if outer_failure:
                    verifier = patch.object(envelope, "verify_envelope", side_effect=envelope.S2TYRunError("neutral-outer"))
                else:
                    verifier = patch.object(envelope, "verify_envelope", wraps=envelope.verify_envelope)
                with verifier:
                    execution = patch.object(envelope, "run_materialized_once", side_effect=RuntimeError("neutral-execution")) if execution_failure else patch.object(envelope, "run_materialized_once", wraps=envelope.run_materialized_once)
                    with execution:
                        entry.MAIN_GATE = True
                        closure = entry.run_bound_once(binding_path, output)
            documents = {item.name: json.loads(item.read_text(encoding="utf-8")) for item in output.iterdir()}
            return closure, documents, calls

    def test_neutral_entry_publishes_one_outer_verification_before_evaluation(self):
        closure, documents, calls = self._run()
        self.assertEqual((closure["run_status"], closure["outer_verification"], closure["evaluation_allowed"], calls), ("COMPLETE", "VERIFIED", True, 22))
        self.assertEqual(sorted(documents), ["closure.json", "envelope.json", "evaluation.json", "outer-verification.json"])
        self.assertFalse(entry.MAIN_GATE)

    def test_materialization_abort_publishes_error_without_evaluation(self):
        closure, documents, calls = self._run(supplier_failure=True)
        self.assertEqual((closure["run_status"], closure["outer_verification"], closure["evaluation_allowed"], calls), ("NOT_EVALUABLE", "VERIFIED", False, 3))
        self.assertNotIn("evaluation.json", documents)

    def test_failed_outer_verification_blocks_evaluation(self):
        closure, documents, _ = self._run(outer_failure=True)
        self.assertEqual((closure["outer_verification"], closure["evaluation_allowed"]), ("NOT_EVALUABLE", False))
        self.assertNotIn("evaluation.json", documents)

    def test_actual_success_publication_overflow_preserves_evidence_in_failure_closure(self):
        closure, documents, _ = self._run(success_budget=1)
        self.assertEqual((closure["run_status"], closure["evaluation_allowed"]), ("NOT_EVALUABLE", False))
        self.assertEqual(documents["entry-failure.json"]["code"], "PUBLICATION_BUDGET_INVALID")
        self.assertIn("evaluation.json", documents)
        self.assertFalse(entry.MAIN_GATE)

    def test_supplier_initialization_error_after_output_creation_is_closed(self):
        closure, documents, calls = self._run(supplier_initialization_failure=True)
        self.assertEqual((closure["run_status"], closure["evaluation_allowed"], calls), ("NOT_EVALUABLE", False, 0))
        self.assertEqual(documents["entry-failure.json"]["phase"], "SUPPLIER_INITIALIZATION")
        self.assertFalse(entry.MAIN_GATE)

    def test_evaluation_error_preserves_verified_envelope_and_blocks_successful_closure(self):
        closure, documents, _ = self._run(evaluation_failure=True)
        self.assertEqual((closure["run_status"], closure["evaluation_allowed"]), ("NOT_EVALUABLE", False))
        self.assertEqual(documents["entry-failure.json"]["phase"], "EVALUATION")
        self.assertIn("envelope.json", documents)
        self.assertIn("outer-verification.json", documents)

    def test_both_full_publication_reserves_exhausted_publish_terminal_error_only(self):
        closure, documents, _ = self._run(success_budget=1, failure_budget=1)
        self.assertEqual((closure["status"], closure["phase"], closure["evidence_complete"]), ("NOT_EVALUABLE", "TERMINAL_CLOSURE", False))
        self.assertEqual(sorted(documents), ["terminal-error.json"])
        self.assertIn("envelope.json", closure["unpublished_artifacts"])
        self.assertIn("evaluation.json", closure["unpublished_artifacts"])
        self.assertFalse(entry.MAIN_GATE)

    def test_unexpected_execution_failure_is_not_misclassified_as_supplier_initialization(self):
        closure, documents, _ = self._run(execution_failure=True)
        self.assertEqual(documents["entry-failure.json"]["phase"], "RUN_EXECUTION")
        self.assertEqual(documents["entry-failure.json"]["details"]["progress"], "UNKNOWN")
        self.assertEqual(closure["run_status"], "NOT_EVALUABLE")

    def test_existing_output_is_rejected_and_gate_is_closed(self):
        manifest = neutral_manifest()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            binding_path, output = root / "binding.json", root / "output"
            write_binding(binding_path, manifest)
            output.mkdir()
            with patch.object(source_time, "source_manifest", return_value=manifest):
                entry.MAIN_GATE = True
                with self.assertRaises(entry.S2TYRealEntryError) as raised:
                    entry.run_bound_once(binding_path, output)
            self.assertEqual(raised.exception.code, "OUTPUT_ALREADY_EXISTS")
            self.assertFalse(entry.MAIN_GATE)
