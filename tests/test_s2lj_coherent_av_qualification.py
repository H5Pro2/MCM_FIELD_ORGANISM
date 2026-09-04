"""Neutral qualification for the bounded S2-LJ integration components."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import FrozenInstanceError
import json
from pathlib import Path
import tempfile
import unittest

from tools import _s2lj_coherent_av_fixtures as fixtures
from tools import _s2lj_coherent_av_runner as runner
from tools import _s2lj_coherent_av_verifier as verifier
from tools._s2jw_default_live_profile import build_s2jw_default_live_profile


ROOT = Path(__file__).resolve().parents[1]


def _reseal(record: dict[str, object]) -> dict[str, object]:
    payload = deepcopy(record)
    payload.pop("record_digest", None)
    return {**payload, "record_digest": runner._digest(payload)}


class S2LJNeutralQualificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = runner.neutral_qualification_record(ROOT)

    def test_01_main_gate_is_closed_and_main_call_is_rejected(self) -> None:
        self.assertFalse(runner.MAIN_EXECUTION_ENABLED)
        self.assertIsNone(runner.AUTHORIZED_RUN_ID)
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(runner.S2LJRunnerError):
                runner.run_main_once(Path(temporary).resolve(), ROOT, "s2lj-main-disabled")
        self.assertFalse(runner.MAIN_EXECUTION_ENABLED)

    def test_02_main_fixture_is_bound_but_not_executed(self) -> None:
        self.assertEqual(13, fixtures.MAIN_FORMATION_COUNT)
        self.assertEqual(("P",) * 4 + tuple(f"E{i}" for i in range(1, 10)), fixtures.MAIN_SEQUENCE)
        self.assertEqual(1, len(self.record["formations"]))
        self.assertFalse(self.record["plan"]["main_story_executed"])

    def test_03_neutral_source_uses_real_default_live_receptor_dimensions(self) -> None:
        profile = build_s2jw_default_live_profile()
        stream = fixtures.S2LJSourceStream(profile, mode="QUALIFICATION")
        pair, source = stream.materialize_next_formation()
        self.assertEqual(48, len(pair.auditory.timed_frame.frame.values))
        self.assertEqual(288, len(pair.visual.timed_frame.frame.values))
        self.assertEqual(source.source_digest, runner._digest(source.payload_without_digest()))
        self.assertEqual(1, stream.next_ordinal)

    def test_04_slow_proofs_bind_created_matched_matched(self) -> None:
        for proof in self.record["transitions"]:
            self.assertEqual(["CREATED", "MATCHED", "MATCHED"], proof["event_chain"])
            self.assertEqual([1, 2, 3], proof["support_chain"])
            self.assertEqual("PPB_TRANSITION_INTEGRITY_VALID", proof["integrity_status"])
            verifier._verify_transition(proof, proof["modality"])

    def test_05_transition_rejects_original_value_substitution(self) -> None:
        proof = deepcopy(self.record["transitions"][0])
        proof["recorded_prototype_values"][2][0] += 1e-12
        payload = dict(proof)
        payload.pop("proof_digest")
        proof["proof_digest"] = runner._digest(payload)
        with self.assertRaises(verifier.S2LJVerificationError):
            verifier._verify_transition(proof, "AUDITORY")

    def test_06_neutral_atomic_memory_step_is_complete(self) -> None:
        formation = self.record["formations"][0]
        self.assertEqual("CONSUMED", formation["owner_status"])
        self.assertNotEqual(formation["prestate_digest"], formation["poststate_digest"])
        self.assertEqual(formation["poststate_digest"], self.record["final_memory_digest"])

    def test_07_neutral_observed_and_direct_field_arms_match(self) -> None:
        field = self.record["field"]
        self.assertEqual((1, 2), (field["group_count"], field["event_count"]))
        self.assertTrue(field["initial_fields_distinct"])
        self.assertTrue(field["initial_fields_zero"])
        self.assertTrue(field["final_components_equal"])
        self.assertEqual(field["observed_final_digest"], field["direct_final_digest"])
        self.assertTrue(field["nontrivial"])

    def test_08_neutral_record_contains_no_cues_scans_evaluation_or_raw_payload(self) -> None:
        self.assertEqual([], self.record["cue_sources"])
        self.assertEqual({}, self.record["scan_results"])
        self.assertEqual([], self.record["completions"])
        self.assertIsNone(self.record["evaluation"])
        serialized = json.dumps(self.record, sort_keys=True)
        for forbidden in ('"raw_bytes"', '"rgb_bytes"', '"pcm_values"', '"image"'):
            self.assertNotIn(forbidden, serialized)

    def test_09_independent_verifier_accepts_atomic_neutral_record(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = runner.write_atomic_result(
                Path(temporary).resolve() / "s2lj-neutral-record",
                deepcopy(self.record),
            )
            result = verifier.verify_result_file(path, ROOT, expected_mode="QUALIFICATION")
        self.assertEqual("RECORDING_COMPLETE", result["verification_status"])
        self.assertTrue(result["read_only"])

    def test_10_verifier_rejects_transition_and_source_mutations(self) -> None:
        for mutation in ("transition", "source"):
            record = deepcopy(self.record)
            if mutation == "transition":
                record["transitions"][1]["support_chain"] = [1, 2, 4]
            else:
                first = next(iter(record["source_hashes"]))
                record["source_hashes"][first] = "0" * 64
            record = _reseal(record)
            with tempfile.TemporaryDirectory() as temporary:
                path = runner.write_atomic_result(
                    Path(temporary).resolve() / f"s2lj-{mutation}", record
                )
                with self.assertRaises(verifier.S2LJVerificationError):
                    verifier.verify_result_file(path, ROOT, expected_mode="QUALIFICATION")

    def test_11_atomic_writer_rejects_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary).resolve() / "s2lj-once"
            runner.write_atomic_result(directory, deepcopy(self.record))
            with self.assertRaises(runner.S2LJRunnerError):
                runner.write_atomic_result(directory, deepcopy(self.record))

    def test_12_public_evidence_types_are_immutable_and_sources_stay_bound(self) -> None:
        profile = build_s2jw_default_live_profile()
        stream = fixtures.S2LJSourceStream(profile, mode="QUALIFICATION")
        _, source = stream.materialize_next_formation()
        with self.assertRaises(FrozenInstanceError):
            source.ordinal = 2
        self.assertEqual(set(runner.SOURCE_PATHS), set(self.record["source_hashes"]))
        self.assertEqual(runner.source_hashes(ROOT), self.record["source_hashes"])


if __name__ == "__main__":
    unittest.main()
