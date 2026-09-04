"""Neutral qualification of the private S2-LS corpus stream shell."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tools import _s2ls_private_corpus_stream_runner as runner
from tools import _s2ls_private_corpus_stream_verifier as verifier


ROOT = Path(__file__).resolve().parents[1]


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("ascii")).hexdigest()


def _resign(record: dict[str, object]) -> None:
    execution = record["execution"]
    execution_payload = dict(execution)
    execution_payload.pop("execution_digest", None)
    execution["execution_digest"] = runner._digest(execution_payload)
    payload = dict(record)
    payload.pop("record_digest", None)
    record["record_digest"] = runner._digest(payload)


class S2LSQualificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = runner.neutral_qualification_record(ROOT)

    def test_01_frozen_plan_and_receptor_evidence_are_exact(self) -> None:
        corpus = runner.load_frozen_corpus(ROOT)
        self.assertEqual(runner.EXPECTED_PLAN_DIGEST, corpus.plan["plan_digest"])
        self.assertEqual(runner.EXPECTED_EVIDENCE_DIGEST, corpus.evidence["evidence_digest"])
        self.assertEqual((21, 4, 25), (len(corpus.content), len(corpus.visual_cues), len(corpus.events)))

    def test_02_qualification_uses_one_formation_and_both_cue_modalities(self) -> None:
        events = self.record["execution"]["events"]
        self.assertEqual(
            ["COMPLETE_AV_PERCEPTION", "PARTIAL_VISUAL_CUE", "PARTIAL_AUDITORY_CUE"],
            [event["event_type"] for event in events],
        )
        self.assertEqual(["event-001", "event-018", "event-019"], [event["frozen_event_id"] for event in events])

    def test_03_actual_fast_assignment_is_recorded(self) -> None:
        transition = self.record["execution"]["events"][0]["formation_transition"]
        self.assertEqual("CREATED", transition["fast"]["event"])
        self.assertEqual(1, transition["fast"]["post_slot"]["support_count"])
        self.assertEqual(1, transition["formation_index"])
        self.assertEqual(transition["fast"]["selected_slot_id"], transition["fast"]["post_slot"]["slot_id"])

    def test_04_every_formation_has_separate_auditory_and_visual_ppb_records(self) -> None:
        transition = self.record["execution"]["events"][0]["formation_transition"]
        self.assertEqual({"auditory_ppb", "visual_ppb"}, {key for key in transition if key.endswith("_ppb")})
        self.assertEqual("NO_UPDATE", transition["auditory_ppb"]["event"])
        self.assertEqual("NO_UPDATE", transition["visual_ppb"]["event"])

    def test_05_both_scans_are_read_only_and_independent(self) -> None:
        final_memory = self.record["execution"]["counters"]["final_memory_digest"]
        for event in self.record["execution"]["events"][1:]:
            primary = event["primary_scan"]
            baseline = event["baseline_scan"]
            self.assertEqual("PRIMARY", primary["scan_role"])
            self.assertEqual("DIRECT_BASELINE", baseline["scan_role"])
            self.assertEqual((final_memory, final_memory), (primary["prestate_digest"], primary["poststate_digest"]))
            self.assertEqual((final_memory, final_memory), (baseline["prestate_digest"], baseline["poststate_digest"]))
            self.assertNotEqual(primary["receipt_digest"], baseline["receipt_digest"])

    def test_06_technical_completion_has_no_positive_function_gate(self) -> None:
        self.assertEqual("RECORDING_COMPLETE", self.record["technical_status"])
        self.assertIsNone(self.record["evaluation"])
        self.assertFalse(self.record["plan"]["main_story_executed"])
        self.assertFalse(self.record["plan"]["main_execution_enabled"])

    def test_07_adaptive_frozen_and_replay_arms_accept_regular_negative_results(self) -> None:
        target = (0.5, 0.5)
        adaptive = runner._arm_result((("slot-a", (0.9, 0.9)),), target, (0, 1), 0.01)
        frozen = runner._arm_result((("first", (0.1, 0.1)),), target, (0, 1), 0.01)
        replay = runner._arm_result((("r1", (0.2, 0.2)), ("r2", (0.8, 0.8))), target, (0, 1), 0.01)
        self.assertEqual([], adaptive["accepted_candidate_ids"])
        self.assertEqual([], frozen["accepted_candidate_ids"])
        self.assertEqual([], replay["accepted_candidate_ids"])
        self.assertTrue(all(value["arm_digest"] == runner._digest({key: item for key, item in value.items() if key != "arm_digest"}) for value in (adaptive, frozen, replay)))

    def test_08_raw_sources_are_absent_from_the_result(self) -> None:
        serialized = json.dumps(self.record, sort_keys=True)
        for forbidden in ("raw_bytes", "rgb_bytes", "pcm_samples", "image_bytes", "audio_bytes"):
            self.assertNotIn(forbidden, serialized)
        self.assertFalse(self.record["raw_payload_retained"])

    def test_09_atomic_result_verifies_without_modification(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            path = runner.write_result_once(root, runner.QUALIFICATION_ID, self.record)
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            result = verifier.verify_result_file(path, ROOT, expected_mode="QUALIFICATION")
            after = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual("RECORDING_COMPLETE", result["verification_status"])
            self.assertEqual(before, after)
            with self.assertRaises(FileExistsError):
                runner.write_result_once(root, runner.QUALIFICATION_ID, self.record)

    def test_10_transition_mutation_is_rejected_fail_closed(self) -> None:
        changed = json.loads(json.dumps(self.record))
        changed["execution"]["events"][0]["formation_transition"]["fast"]["selected_slot_id"] = "foreign-slot"
        _resign(changed)
        with self.assertRaises(verifier.S2LSVerificationError):
            verifier._verify_record(changed, ROOT, "QUALIFICATION")

    def test_11_frozen_evidence_and_source_mutations_are_rejected(self) -> None:
        for role in ("frozen", "source"):
            changed = json.loads(json.dumps(self.record))
            if role == "frozen":
                changed["frozen_binding"]["evidence_digest"] = _sha("foreign-evidence")
            else:
                changed["source_hashes"][runner.SOURCE_PATHS[0]] = _sha("foreign-source")
            _resign(changed)
            with self.assertRaises(verifier.S2LSVerificationError):
                verifier._verify_record(changed, ROOT, "QUALIFICATION")

    def test_12_main_gate_is_closed_and_creates_no_output(self) -> None:
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            with self.assertRaises(runner.S2LSStreamError):
                runner.run_main_once(workspace_root=ROOT, output_root=root, run_id=runner.AUTHORIZED_RUN_ID)
            self.assertEqual([], list(root.iterdir()))
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)


if __name__ == "__main__":
    unittest.main()
