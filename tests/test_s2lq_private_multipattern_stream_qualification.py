"""Neutral qualification of the bounded private S2-LQ stream extension."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tools import _s2lq_private_multipattern_stream_runner as runner
from tools import _s2lq_private_multipattern_stream_verifier as verifier
from tools import _s2lo_private_role_free_stream_runner as lo_runner


ROOT = Path(__file__).resolve().parents[1]


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("ascii")).hexdigest()


class S2LQQualificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = runner.neutral_qualification_record(ROOT)

    def test_01_main_plan_is_fixed_neutral_and_not_executed(self) -> None:
        specs = runner.MAIN_EVENT_SPECS
        self.assertEqual(29, len(specs))
        self.assertEqual(tuple(f"e{index:02d}" for index in range(1, 30)), tuple(item.event_code for item in specs))
        self.assertEqual(21, sum(item.event_type == "COMPLETE_AV_PERCEPTION" for item in specs))
        self.assertEqual(4, sum(item.event_type == "PARTIAL_AUDITORY_CUE" for item in specs))
        self.assertEqual(4, sum(item.event_type == "PARTIAL_VISUAL_CUE" for item in specs))
        serialized = json.dumps([item.payload_without_digest() for item in specs], sort_keys=True)
        for forbidden in ("TARGET", "DISTRACTOR", "STABLE", "UNSTABLE", "FORGOTTEN"):
            self.assertNotIn(forbidden, serialized)
        self.assertFalse(self.record["plan"]["main_story_executed"])

    def test_02_event_specs_are_immutable_and_digest_bound(self) -> None:
        with self.assertRaises(FrozenInstanceError):
            runner.MAIN_EVENT_SPECS[0].ordinal = 9
        for item in runner.MAIN_EVENT_SPECS:
            self.assertEqual(item.spec_digest, runner._digest(item.payload_without_digest()))

    def test_03_four_real_source_bindings_have_exact_dimensions(self) -> None:
        bindings = self.record["source_bindings"]
        self.assertEqual(4, len(bindings))
        self.assertEqual(
            [item.spec_digest for item in runner.QUALIFICATION_SOURCE_SPECS],
            [item["event_spec_digest"] for item in bindings],
        )
        for item in bindings:
            self.assertEqual((48, 288), (item["auditory_dimension"], item["visual_dimension"]))
            for key in ("source_digest", "source_receipt_digest", "pairing_digest"):
                self.assertRegex(item[key], r"^[0-9a-f]{64}$")

    def test_04_qualification_counters_and_main_budgets_are_exact(self) -> None:
        self.assertEqual(
            {
                "source_binding_count": 4,
                "field_calls": 0,
                "memory_calls": 0,
                "scan_calls": 0,
                "main_events_processed": 0,
            },
            self.record["qualification_counters"],
        )
        self.assertEqual(8_400, runner.MAIN_FIELD_CONTACTS)
        self.assertEqual(74_592, runner.MAIN_MEMORY_L1_TERMS)
        self.assertEqual(10_624, runner.MAIN_SCAN_COMPARISONS)
        self.assertEqual(156_000_000, runner.MAIN_RAW_BYTES)

    def test_05_multislot_evaluator_accepts_complete_three_slot_inventory(self) -> None:
        inventory = self.record["multislot_inventory"]
        runner.validate_multislot_summary(inventory)
        for modality in ("auditory", "visual"):
            self.assertEqual(3, inventory[modality]["occupied_slot_count"])
            self.assertEqual(2, inventory[modality]["stable_slot_count"])
            self.assertEqual({"p00": 3, "p01": 3, "p02": 2}, inventory[modality]["support_by_content"])

    def test_06_multislot_evaluator_rejects_one_slot_assumption_and_bad_support(self) -> None:
        for mutation in ("slot_count", "support"):
            changed = json.loads(json.dumps(self.record["multislot_inventory"]))
            if mutation == "slot_count":
                changed["auditory"]["occupied_slot_count"] = 1
            else:
                changed["visual"]["support_by_content"]["p02"] = 3
            with self.assertRaises(runner.S2LQError):
                runner.validate_multislot_summary(changed)

    def test_07_transition_chain_mutations_fail_closed(self) -> None:
        for mutation in ("support", "digest", "slot"):
            changed = json.loads(json.dumps(self.record["multislot_inventory"]))
            chain = changed["auditory"]["transition_chains"]["p00"]
            if mutation == "support":
                chain["support_chain"] = [1, 3, 3]
            elif mutation == "digest":
                chain["prototype_digests"][1] = "0" * 63
            else:
                chain["slot_id"] = None
            with self.assertRaises(runner.S2LQError):
                runner.validate_multislot_summary(changed)

    def test_08_read_only_evidence_requires_identical_state_digests(self) -> None:
        evidence = self.record["read_only_evidence"]
        self.assertEqual(evidence["prestate_digest"], evidence["poststate_digest"])
        changed = json.loads(json.dumps(self.record))
        changed["read_only_evidence"]["poststate_digest"] = _sha("changed")
        payload = dict(changed)
        payload.pop("record_digest", None)
        changed["record_digest"] = runner._digest(payload)
        with self.assertRaises(verifier.S2LQVerificationError):
            verifier._verify_record(changed, ROOT, "QUALIFICATION")

    def test_09_interference_is_classified_without_claiming_own_storage(self) -> None:
        expected = _sha("neutral-interference")
        self.assertEqual(
            "SENSOR_CONFUSION_WITH_EXISTING_STABLE_CONTENT",
            runner.classify_interference(
                decision="ADMIT_SINGLE_CONTEXT",
                hypothesis_digest=expected,
                expected_content_digest=expected,
                own_content_stored=False,
            ),
        )
        for kwargs in (
            {"decision": "ABSTAIN_NO_CONTEXT", "hypothesis_digest": expected, "own_content_stored": False},
            {"decision": "ADMIT_SINGLE_CONTEXT", "hypothesis_digest": _sha("foreign"), "own_content_stored": False},
            {"decision": "ADMIT_SINGLE_CONTEXT", "hypothesis_digest": expected, "own_content_stored": True},
        ):
            with self.assertRaises(runner.S2LQError):
                runner.classify_interference(expected_content_digest=expected, **kwargs)

    def test_10_atomic_record_verifies_read_only_and_cannot_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            path = lo_runner.write_result_once(root, "s2lq-neutral-qualification", self.record)
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            result = verifier.verify_result_file(path, ROOT, expected_mode="QUALIFICATION")
            after = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual("RECORDING_COMPLETE", result["verification_status"])
            self.assertTrue(result["read_only"])
            self.assertEqual(before, after)
            with self.assertRaises(FileExistsError):
                lo_runner.write_result_once(root, "s2lq-neutral-qualification", self.record)

    def test_11_verifier_rejects_source_counter_slot_and_raw_mutations(self) -> None:
        for mutation in ("source", "counter", "slot", "raw"):
            changed = json.loads(json.dumps(self.record))
            if mutation == "source":
                changed["source_bindings"][0]["pairing_digest"] = _sha("foreign")
            elif mutation == "counter":
                changed["qualification_counters"]["memory_calls"] = 1
            elif mutation == "slot":
                changed["multislot_inventory"]["visual"]["stable_slot_count"] = 1
            else:
                changed["raw_payload"] = [1]
            payload = dict(changed)
            payload.pop("record_digest", None)
            changed["record_digest"] = runner._digest(payload)
            with self.assertRaises(verifier.S2LQVerificationError):
                verifier._verify_record(changed, ROOT, "QUALIFICATION")

    def test_12_main_gate_is_closed_without_output(self) -> None:
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            with self.assertRaises(runner.S2LQError):
                runner.run_main_once(
                    workspace_root=ROOT,
                    output_root=root,
                    run_id=runner.AUTHORIZED_RUN_ID,
                )
            self.assertEqual([], list(root.iterdir()))
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)


if __name__ == "__main__":
    unittest.main()
