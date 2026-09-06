"""Bound neutral NF qualification. No NF source or main history is executed."""

from copy import deepcopy
from dataclasses import asdict, replace
import json
import math
import os
from pathlib import Path
import tempfile
import unittest

from tools import _s2nf_private_run as run
from tools import _s2nf_private_run_verification as verify
from tools import _s2nf_private_run_evaluation as evaluate
from tests import test_s2kz_private_auditory_partial_cue_retrieval_336 as synthetic

ne = run.ne
PLAN = (
    ne.Event("s2nf-neutral-h01", "s2nf-neutral-h01-e01", 0, "neutral-t", 0),
    ne.Event("s2nf-neutral-h01", "s2nf-neutral-h01-e02", 1, "neutral-c", 2),
    ne.Event("s2nf-neutral-h01", "s2nf-neutral-h01-e03", 2, "neutral-variant", None),
    ne.Event("s2nf-neutral-h01", "s2nf-neutral-h01-e04", 3, "neutral-local", None),
    ne.Event("s2nf-neutral-h01", "s2nf-neutral-h01-e05", 4, "neutral-unknown", None),
    ne.Event("s2nf-neutral-h02", "s2nf-neutral-h02-e01", 0, "neutral-unknown", None),
)
METRICS = dict(receptor_calls=0, nf_pcm_calls=0, main_calls=0, field_calls=0, runtime_calls=0)


class NeutralSources:
    def __init__(self, config):
        self.config = config
        self.audio_analyses = self.visual_analyses = 0
        self.catalog = dict(audio={}, visual={str(o): dict(values_digest=ne.digest([v] * 288),
            payload_digest=str(i) * 64) for i, (o, v) in enumerate(((0, 0.0), (2, 1.0)), 3)}, plan_binding="9" * 64)
        values = {"neutral-t": [0.1] * 48, "neutral-c": [0.7] * 48,
            "neutral-variant": [0.15] * 48, "neutral-local": [0.35] + [0.1] * 47, "neutral-unknown": [1.0] * 48}
        for i, (sid, array) in enumerate(values.items(), 1):
            run.sources.bind_values(self.catalog, sid, str(i) * 64, "8" * 64, tuple(array))

    def materialize(self, event):
        profile = self.config.profile.profile
        audio = ne.ReceptorContactFrame("auditory", profile.auditory_config.geometry_id, event.event_id,
            event.history_id + "-audio-sample", 9600 * event.ordinal, 9600 * event.ordinal + 4800,
            profile.auditory_config.carrier_ids, tuple(self.catalog["audio"][event.audio_source]["values"]))
        visual = None
        if event.kind == "FORMATION":
            visual = ne.ReceptorContactFrame("visual", profile.visual_config.geometry_id,
                f"visual.receptor.{6 * event.ordinal + 2}", "video.frame", 6 * event.ordinal + 2,
                6 * event.ordinal + 3, profile.visual_config.carrier_ids,
                (0.0 if event.visual_ordinal == 0 else 1.0,) * 288)
        return ne.materialized_from_frames(event, self.config, self.catalog, audio, visual)


def archive(name, path):
    root = os.environ.get("S2NF_QUALIFICATION_ARTIFACTS")
    if root:
        with (Path(root) / name).open("xb") as handle:
            handle.write(path.read_bytes())


class RunQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="s2nf-neutral-")
        cls.root = Path(cls.temp.name)
        cls.config = ne.make_config()
        cls.path = run.execute_once(run_id="s2nf-neutral-composition-01", output_root=cls.root,
                                   plan=PLAN, provider_factory=NeutralSources)
        cls.record = json.loads(cls.path.read_bytes())
        cls.proof_path = verify.verify_file_once(cls.path, plan=PLAN, config=cls.config)
        cls.proof = json.loads(cls.proof_path.read_bytes())
        archive("neutral-recording.json", cls.path)
        archive("neutral-verification.json", cls.proof_path)
        METRICS.update(main_gate=run.MAIN_GATE, technical_status=cls.record["status"],
            verification_status=cls.proof["status"], recording_bytes=cls.path.stat().st_size,
            counts=cls.record["counts"])

    @classmethod
    def tearDownClass(cls):
        print("S2NF_NEUTRAL_METRICS=" + json.dumps(METRICS, sort_keys=True))
        cls.temp.cleanup()

    def rehash(self, record):
        record["record_digest"] = ne.digest({k: v for k, v in record.items() if k != "record_digest"})
        return record

    def check(self, record):
        return verify.verify_record(record, plan=PLAN, config=self.config)

    def test_01_main_closed_and_literal_plan(self):
        plan = run.sources.events_from_plan(run.sources.load_plan())
        self.assertEqual((13, 3, 10), (len(plan), sum(e.kind == "FORMATION" for e in plan), sum(e.kind == "CUE" for e in plan)))
        self.assertEqual(2, len({e.history_id for e in plan}))
        with self.assertRaises(ne.RunError):
            run.run_main_once(run_id="s2nf-forbidden-main", output_root=self.root)
        self.assertFalse(run.MAIN_GATE)

    def test_02_complete_competition_and_continuity(self):
        self.assertEqual("RECORDING_COMPLETE", self.record["status"])
        self.assertEqual("RECORDING_COMPLETE", self.proof["status"])
        self.assertEqual((6, 2, 4, 16, 320), tuple(self.record["counts"][k] for k in ("events", "formations", "cues", "arms", "slot_visits")))
        events = self.record["events"]
        state = verify.old.decode_state(self.record["states"][events[2]["prestate"]], self.config)
        self.assertEqual(2, sum(s.occupied for s in state.b4_state.entries))
        self.assertEqual(2, sum(s.occupied for s in state.tspm_state.fast_state.slots))
        self.assertEqual(events[2]["prestate"], events[2]["poststate"])
        self.assertEqual(events[2]["poststate"], events[3]["prestate"])
        self.assertTrue(all(b["reference"] and b["alternative"] for b in self.proof["baseline_equality"]))

    def test_03_ppb_no_update_is_bound(self):
        transitions = self.proof["ppb_transitions"]
        self.assertEqual(2, len(transitions))
        for row in transitions:
            self.assertEqual(["NO_UPDATE", "NO_UPDATE"], [t["event"] for t in row["transitions"]])
            self.assertTrue(all(t["pre_digest"] == t["post_digest"] for t in row["transitions"]))

    def test_04_catalog_digest_values_and_sources(self):
        for key in ("values_digest", "payload_digest", "parent_digest"):
            record = deepcopy(self.record)
            record["catalog"]["audio"]["neutral-t"][key] = "0" * 64
            record["catalog_digest"] = ne.digest(record["catalog"])
            with self.assertRaises((ne.RunError, ne.arms.kz.S2KZError)):
                self.check(self.rehash(record))
        catalog = deepcopy(self.record["catalog"])
        with self.assertRaises(ne.RunError):
            run.sources.bind_values(catalog, "neutral-t", "1" * 64, "8" * 64, (0.11,) * 48)

    def test_05_native_time_and_wrong_visual_clock(self):
        event = self.record["events"][2]
        state = verify.old.decode_state(self.record["states"][event["prestate"]], self.config)
        cue = verify.old._source(PLAN[2], event["source"], self.config, self.record["catalog"])
        for bad in (replace(cue, auditory_source_clock_id="video.frame"),
                    replace(cue, auditory_window_start_tick=9600, auditory_window_end_tick=14400)):
            bad = replace(bad, cue_digest=ne.digest(bad.payload_without_digest()))
            for rule in ne.arms.RULES:
                with self.assertRaises(ne.arms.kz.S2KZError):
                    ne.arms.retrieve(rule=rule, config=self.config, state=state, cue=bad,
                                     band_plan=ne.arms.kz.build_auditory_band_plan_48())

    def test_06_missing_swapped_and_foreign_events(self):
        for field in ("missing", "order", "source", "prestate"):
            record = deepcopy(self.record)
            if field == "missing":
                record["events"].pop()
            elif field == "order":
                record["events"][2:4] = list(reversed(record["events"][2:4]))
            else:
                e = record["events"][3]
                e[field] = deepcopy(record["events"][0][field])
                e["event_digest"] = ne.digest({k: v for k, v in e.items() if k != "event_digest"})
            with self.assertRaises((ne.RunError, ne.arms.kz.S2KZError)):
                self.check(self.rehash(record))

    def test_07_missing_and_swapped_arms(self):
        for remove in (False, True):
            record = deepcopy(self.record)
            e = record["events"][2]
            if remove:
                e["arms"].pop()
            else:
                e["arms"][0], e["arms"][2] = e["arms"][2], e["arms"][0]
            e["event_digest"] = ne.digest({k: v for k, v in e.items() if k != "event_digest"})
            with self.assertRaises(ne.RunError):
                self.check(self.rehash(record))

    def test_08_real_neutral_retention_and_loss_are_separate(self):
        relations = [dict(case_id=f"q{i + 1:02d}", event_id=e.event_id, related_source_id="neutral-t",
            competitor_source_id="neutral-c", target_present=i < 2,
            subtype="UNIFORM_GAIN" if i == 0 else "LOCAL_PARTIAL_ADDITION") for i, e in enumerate(PLAN[2:])]
        proof = {k: v for k, v in self.proof.items() if k not in ("record_file_sha256", "file_unchanged", "report_digest")}
        result = evaluate.evaluate_record(self.record, proof, relations=relations, config=self.config)
        group = result["retention"]["all_competition_cases"]
        self.assertEqual((2, 2, 1, 1), tuple(group[k] for k in ("N", "D", "R", "L")))
        self.assertEqual(["q02"], result["losses"])
        self.assertEqual("FALSIFIED", result["status"])
        self.assertEqual(0, result["outcomes"]["all"]["alternative"]["false_admissions"])
        METRICS["neutral_retention"] = group
        path = self.root / "neutral-evaluation.json"
        ne.atomic_write(path, result)
        archive("neutral-evaluation.json", path)

    def test_09_empty_denominators_not_success(self):
        result = evaluate.summarize([])
        self.assertEqual("ERHALTUNG_NICHT_GEPRUEFT", result["status"])
        self.assertTrue(all(g["D"] == g["R"] + g["L"] == 0 for g in result["retention"].values()))
        self.assertEqual("ABSTAIN_NO_CONTEXT", self.record["events"][-1]["arms"][0]["evidence"]["decision"])
        self.assertEqual("RECORDING_COMPLETE", self.proof["status"])

    def test_10_historical_arithmetic_and_inclusive_max(self):
        candidate = (0.2,) * 24 + (0.0,) * 24
        state = synthetic._state(self.config, b4=(candidate,))
        cue, band_plan = synthetic._cue(self.config, (0.0,) * 24)
        results = [ne.arms.retrieve(rule=rule, config=self.config, state=state, cue=cue, band_plan=band_plan) for rule in ne.arms.RULES]
        row = results[0].evidence.bank_scans[0].records[0]
        self.assertEqual(sum(candidate[:24]) / 24, row.observed_distance)
        self.assertFalse(row.observed_match)
        self.assertTrue(results[1].evidence.bank_scans[0].records[0].observed_match)
        state = synthetic._state(self.config, b4=((math.nextafter(0.2, math.inf),) + (0.0,) * 47,))
        result = ne.arms.retrieve(rule=ne.arms.ALTERNATIVE, config=self.config, state=state, cue=cue, band_plan=band_plan)
        self.assertFalse(result.evidence.bank_scans[0].records[0].observed_match)

    def test_11_slow_rule_and_complete_scans_unchanged(self):
        state = synthetic._state(self.config, slow=((0.02,) * 24 + (0.0,) * 24,), slow_supports=(3,))
        cue, plan = synthetic._cue(self.config, (0.0,) * 24)
        results = [ne.arms.retrieve(rule=rule, config=self.config, state=state, cue=cue, band_plan=plan) for rule in ne.arms.RULES]
        self.assertEqual(results[0].evidence.bank_scans[2], results[1].evidence.bank_scans[2])
        self.assertEqual(sum((0.02,) * 24) / 24, results[0].evidence.bank_scans[2].records[0].observed_distance)
        for e in self.record["events"][2:]:
            for a in e["arms"]:
                self.assertEqual([9, 3, 8], [len(s["records"]) for s in a["evidence"]["bank_scans"]])
                self.assertLess(len(ne.canonical(a)), 32768)

    def test_12_read_only_file_and_once_verification(self):
        before = self.path.read_bytes()
        with self.assertRaises(ne.RunError):
            verify.verify_file_once(self.path, plan=PLAN, config=self.config)
        self.assertEqual(before, self.path.read_bytes())
        self.assertTrue(self.proof["file_unchanged"])

    def test_13_directory_and_atomic_write_conflicts(self):
        with self.assertRaises(FileExistsError):
            run.execute_once(run_id=self.record["run_id"], output_root=self.root, plan=PLAN, provider_factory=NeutralSources)
        path = self.root / "existing.json"
        path.write_bytes(b"unchanged")
        with self.assertRaises(FileExistsError):
            ne.atomic_write(path, {"neutral": True})
        self.assertEqual(b"unchanged", path.read_bytes())

    def test_14_resource_limit_and_atomic_error_record(self):
        counts = deepcopy(self.record["counts"])
        counts["retrieval_comparisons"] = 21121
        with self.assertRaises(ne.RunError):
            run.check_limits(counts)
        path = run.execute_once(run_id="s2nf-neutral-size-error", output_root=self.root,
            plan=(PLAN[-1],), provider_factory=NeutralSources, size_limit=1)
        record = json.loads(path.read_bytes())
        self.assertEqual("NOT_EVALUABLE", record["status"])
        self.assertEqual(("PUBLICATION", "RECORDING_SIZE_EXCEEDED"), tuple(record["failure"][k] for k in ("phase", "code")))
        self.assertEqual("NOT_EVALUABLE", verify.verify_record(record, plan=(PLAN[-1],), config=self.config)["status"])
        archive("size-failure-recording.json", path)

    def test_15_source_failure_progress_without_partial_evaluation(self):
        class Broken(NeutralSources):
            def materialize(self, event):
                raise ne.RunError("PCM_PAYLOAD_INVALID")
        path = run.execute_once(run_id="s2nf-neutral-source-error", output_root=self.root, plan=PLAN, provider_factory=Broken)
        record = json.loads(path.read_bytes())
        self.assertEqual(("SOURCE", 0, 0), tuple(record["failure"][k] for k in ("phase", "event_index", "completed_events")))
        self.assertIsNone(record["catalog"])
        self.assertEqual([], record["events"])
        self.assertEqual("NOT_EVALUABLE", self.check(record)["status"])
        archive("source-failure-recording.json", path)
        record["failure"]["completed_events"] = 2
        with self.assertRaises(ne.RunError):
            self.check(self.rehash(record))

    def test_16_no_public_b_preference(self):
        candidate = (0.1,) * 48
        state = synthetic._state(self.config, b4=(candidate,), slow=(candidate,), slow_supports=(3,))
        cue, plan = synthetic._cue(self.config, (0.1,) * 24)
        for rule in ne.arms.RULES:
            result = ne.arms.retrieve(rule=rule, config=self.config, state=state, cue=cue, band_plan=plan)
            self.assertEqual("ABSTAIN_AMBIGUOUS_CONTEXT", result.evidence.decision)
            self.assertEqual(20, result.evidence.resource_ledger.total_slot_scan_count)


if __name__ == "__main__":
    unittest.main()
