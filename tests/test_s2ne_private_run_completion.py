"""Only the added execution/recording boundary; never run the 20/13 history."""

from copy import deepcopy
from dataclasses import asdict
import json
import os
from pathlib import Path
import tempfile
import unittest

from mcm_field_organism.receptor_contract import ReceptorContactFrame
from tools import _s2ne_private_run as run
from tools import _s2ne_private_run_verification as verification
from tools import _s2ne_private_run_evaluation as evaluation

QUALIFICATION_ID = "s2ne-run-completion-qualification-20260906-01"
PLAN = (
    run.Event("s2ne-neutral-h04", "s2ne-neutral-h04-e01", 0, "neutral01", 0),
    run.Event("s2ne-neutral-h04", "s2ne-neutral-h04-e02", 1, "neutral02", None),
    run.Event("s2ne-neutral-h04", "s2ne-neutral-h04-e03", 2, "neutral01", 0),
    run.Event("s2ne-neutral-h04", "s2ne-neutral-h04-e04", 3, "neutral02", None),
    run.Event("s2ne-neutral-h06", "s2ne-neutral-h06-e01", 0, "neutral02", None),
)
METRICS = {}


def archive(name, path):
    directory = os.environ.get("S2NE_QUALIFICATION_ARTIFACTS")
    if directory:
        target = Path(directory) / name
        with target.open("xb") as handle:
            handle.write(path.read_bytes())


class NeutralSources:
    """Synthetic reduced frames, not raw sources or the S2-NE corpus."""
    def __init__(self, config):
        self.config = config
        self.audio_analyses = self.visual_analyses = 0
        item = dict(values=[0.1] * 48, values_digest=run.digest([0.1] * 48),
                    payload_digest="1" * 64, parent_digest="2" * 64)
        self.catalog = dict(audio={"neutral01": dict(item), "neutral02": dict(item)},
                            visual={"0": dict(values_digest=run.digest([0.0] * 288), payload_digest="3" * 64)})

    def materialize(self, spec):
        p = self.config.profile.profile
        a = ReceptorContactFrame("auditory", p.auditory_config.geometry_id, spec.event_id,
            spec.history_id + "-audio-sample", spec.ordinal * 9600, spec.ordinal * 9600 + 4800,
            p.auditory_config.carrier_ids, tuple(self.catalog["audio"][spec.audio_source]["values"]))
        v = None
        if spec.kind == "FORMATION":
            v = ReceptorContactFrame("visual", p.visual_config.geometry_id, f"visual.receptor.{6 * spec.ordinal + 2}",
                                    "video.frame", 6 * spec.ordinal + 2, 6 * spec.ordinal + 3,
                                    p.visual_config.carrier_ids, (0.0,) * 288)
        return run.materialized_from_frames(spec, self.config, self.catalog, a, v)


class CompletionQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="s2ne-completion-")
        cls.root = Path(cls.temp.name)
        cls.config = run.make_config()
        cls.catalog = NeutralSources(cls.config).catalog
        cls.path = run.execute_once(run_id="s2ne-neutral-recording-01", output_root=cls.root,
                                    plan=PLAN, provider_factory=NeutralSources)
        cls.original_bytes = cls.path.read_bytes()
        cls.record = json.loads(cls.original_bytes)
        proof_path = verification.verify_file_once(cls.path, plan=PLAN, catalog_factory=lambda: cls.catalog,
                                                   config=cls.config, mode="NEUTRAL")
        cls.proof = json.loads(proof_path.read_bytes())
        archive("neutral-recording.json", cls.path)
        archive("neutral-verification.json", proof_path)
        METRICS.update(recording_bytes=len(cls.original_bytes), neutral_counts=cls.record["counts"],
                       technical_status=cls.record["status"], verification_status=cls.proof["status"],
                       main_gate=run.MAIN_GATE, receptor_calls=0, field_calls=0, main_calls=0)

    @classmethod
    def tearDownClass(cls):
        print("S2NE_COMPLETION_METRICS=" + json.dumps(METRICS, sort_keys=True))
        cls.temp.cleanup()

    def verify(self, record):
        return verification.verify_record(record, plan=PLAN, catalog=self.catalog, config=self.config)

    def rehash(self, record):
        record["record_digest"] = run.digest({k: v for k, v in record.items() if k != "record_digest"})
        return record

    def test_01_literal_main_plan_is_not_executed(self):
        self.assertEqual((33, 20, 13), (len(run.EVENTS), sum(e.kind == "FORMATION" for e in run.EVENTS),
                                      sum(e.kind == "CUE" for e in run.EVENTS)))
        h04 = tuple(e for e in run.EVENTS if e.history_id == "s2ne-h04")
        self.assertEqual(("CUE", "FORMATION", "CUE"), tuple(e.kind for e in h04[-3:]))
        self.assertEqual((13, 14, 15), tuple(e.ordinal for e in h04[-3:]))
        self.assertEqual(("s007", "s001", "s007"), tuple(e.audio_source for e in h04[-3:]))
        self.assertFalse(run.MAIN_GATE)
        with self.assertRaises(run.RunError):
            run.run_main_once(run_id="s2ne-forbidden-main", output_root=self.root)
        self.assertFalse((self.root / "s2ne-forbidden-main").exists())

    def test_02_whole_neutral_sequence_and_mid_cue_continuity(self):
        self.assertEqual("RECORDING_COMPLETE", self.record["status"])
        self.assertEqual("RECORDING_COMPLETE", self.proof["status"])
        self.assertEqual((5, 2, 3, 12, 240), tuple(self.record["counts"][k] for k in ("events", "formations", "cues", "arms", "slot_visits")))
        e = self.record["events"]
        self.assertEqual(e[0]["poststate"], e[1]["prestate"])
        self.assertEqual(e[1]["prestate"], e[1]["poststate"])
        self.assertEqual(e[1]["poststate"], e[2]["prestate"])
        self.assertEqual(2, self.record["states"][e[2]["poststate"]]["generation"])
        self.assertEqual(self.original_bytes, self.path.read_bytes())

    def test_03_missing_or_swapped_events_are_rejected(self):
        for modify in (lambda r: r["events"].pop(1),
                       lambda r: r["events"].__setitem__(slice(0, 2), list(reversed(r["events"][:2])))):
            bad = deepcopy(self.record)
            modify(bad)
            with self.assertRaises(run.RunError):
                self.verify(self.rehash(bad))

    def test_04_missing_or_swapped_arm_evidence_is_rejected(self):
        for remove in (True, False):
            bad = deepcopy(self.record)
            e = bad["events"][1]
            if remove:
                e["arms"].pop()
            else:
                e["arms"][0], e["arms"][1] = e["arms"][1], e["arms"][0]
            e["event_digest"] = run.digest({k: v for k, v in e.items() if k != "event_digest"})
            with self.assertRaises(run.RunError):
                self.verify(self.rehash(bad))

    def test_05_swapped_formation_and_state_links_are_rejected(self):
        for field in ("formation", "prestate", "source"):
            bad = deepcopy(self.record)
            e = bad["events"][2]
            e[field] = deepcopy(bad["events"][0][field])
            e["event_digest"] = run.digest({k: v for k, v in e.items() if k != "event_digest"})
            with self.assertRaises((run.RunError, run.arms.kz.S2KZError)):
                self.verify(self.rehash(bad))

    def test_06_valid_abstention_verifies_but_prediction_can_fail(self):
        self.assertEqual("ABSTAIN_NO_CONTEXT", self.record["events"][-1]["arms"][0]["evidence"]["decision"])
        self.assertEqual("RECORDING_COMPLETE", self.proof["status"])
        row = dict(retention_group="varied:alone", prediction_matches=False, reference_correct_a=True,
                   alternative_correct_a=False, reference_false_admission=False, alternative_false_admission=False,
                   reference_abstains=False, alternative_abstains=True)
        result = evaluation.summarize([row])
        self.assertEqual("FALSIFIED", result["status"])
        self.assertEqual((1, 0, 1), tuple(result["retention"]["varied:alone"][k] for k in ("D", "R", "L")))
        row["reference_correct_a"] = False
        self.assertEqual("ERHALTUNG_NICHT_GEPRUEFT", evaluation.summarize([row])["retention"]["varied:alone"]["status"])

    def test_07_existing_run_directory_rejects_before_source_call(self):
        def forbidden(config):
            self.fail("source factory reached after directory conflict")
        with self.assertRaises(FileExistsError):
            run.execute_once(run_id=self.record["run_id"], output_root=self.root,
                             plan=PLAN, provider_factory=forbidden)
        self.assertEqual(self.original_bytes, self.path.read_bytes())

    def test_08_atomic_publication_does_not_replace_existing_file(self):
        path = self.root / "existing.json"
        path.write_bytes(b"retained")
        with self.assertRaises(FileExistsError):
            run.atomic_write(path, {"neutral": True})
        self.assertEqual(b"retained", path.read_bytes())

    def test_09_size_failure_has_compact_technical_record(self):
        plan = (PLAN[-1],)
        path = run.execute_once(run_id="s2ne-neutral-size-error", output_root=self.root,
            plan=plan, provider_factory=NeutralSources, size_limit=1)
        result = json.loads(path.read_bytes())
        self.assertEqual("NOT_EVALUABLE", result["status"])
        self.assertEqual(("PUBLICATION", "RECORDING_SIZE_EXCEEDED", 1), tuple(result["failure"][k]
                         for k in ("phase", "code", "completed_events")))
        proof = verification.verify_record(result, plan=plan, catalog=self.catalog, config=self.config)
        self.assertEqual("NOT_EVALUABLE", proof["status"])
        self.assertLess(path.stat().st_size, run.MAX_BYTES)
        archive("size-failure-recording.json", path)
        METRICS["compact_failure_bytes"] = path.stat().st_size

    def test_10_source_failure_has_phase_and_attempt_counts(self):
        class Failing(NeutralSources):
            def materialize(self, spec):
                raise run.RunError("PCM_PAYLOAD_INVALID")
        path = run.execute_once(run_id="s2ne-neutral-source-error", output_root=self.root,
                                plan=PLAN, provider_factory=Failing)
        record = json.loads(path.read_bytes())
        archive("source-failure-recording.json", path)
        self.assertEqual(("SOURCE", 0, 0), tuple(record["failure"][k] for k in ("phase", "event_index", "completed_events")))
        self.assertEqual(0, record["attempts"]["formations"])
        self.assertEqual(0, record["attempts"]["arms"])
        self.assertEqual("NOT_EVALUABLE", self.verify(record)["status"])
        record["failure"]["completed_events"] = 2
        with self.assertRaises(run.RunError):
            self.verify(self.rehash(record))

    def test_11_verification_is_once_and_read_only(self):
        before = self.path.read_bytes()
        with self.assertRaises(run.RunError):
            verification.verify_file_once(self.path, plan=PLAN, catalog_factory=lambda: self.catalog,
                                          config=self.config, mode="NEUTRAL")
        self.assertEqual(before, self.path.read_bytes())
        self.assertTrue(self.proof["file_unchanged"])

    def test_12_source_catalog_and_counters_are_bound(self):
        for name in ("catalog_digest", "config_digest", "plan_digest"):
            record = deepcopy(self.record)
            record[name] = "0" * 64
            with self.assertRaises(run.RunError):
                self.verify(self.rehash(record))
        record = deepcopy(self.record)
        record["counts"]["slot_visits"] -= 1
        with self.assertRaises(run.RunError):
            self.verify(self.rehash(record))


if __name__ == "__main__":
    unittest.main()
