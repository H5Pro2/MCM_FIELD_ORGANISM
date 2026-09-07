"""One bounded neutral NO qualification; no sealed NH payload generation."""

from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import _s2no_private_half_materialization as run
from tools import _s2no_private_half_verification as verify

s, nn, ng = run.source, run.nn, run.ng
METRICS = dict(nh_payloads=0, main_calls=0, runtime_events=0, formation_attempts=0,
               field_contacts=0, nj_projections=0, audio_windows=0, audio_hops=0,
               audio_snapshots=0, visual_frames=0)


def archive(name, value):
    ng.ne.atomic_write(Path(os.environ["S2NO_QUAL_DIR"])/name, value)


def neutral_plan():
    audio = s.audio_recipe("neutral-no-20260907",0)
    audio["amplitude"] = s.f32(0.01)
    specs = (s.SourceSpec("neutral-a","PCM",s.canonical(audio).decode()),
        s.SourceSpec("neutral-v","RGB",s.canonical(s.rgb_recipe("neutral-no-image-a",False)).decode()),
        s.SourceSpec("neutral-cue","RGB_CUE",s.canonical(s.rgb_recipe("neutral-no-image-a",True)).decode()),
        s.SourceSpec("neutral-other","RGB_CUE",s.canonical(s.rgb_recipe("neutral-no-image-b",True)).decode()))
    sources = []
    for spec in specs:
        p = s.pcm_payload(json.loads(spec.recipe_json)) if spec.kind == "PCM" else s.rgb_payload(json.loads(spec.recipe_json))
        view = memoryview(p).cast("B")
        sources.append(s.bind_source(spec,hashlib.sha256(view).hexdigest(),view.nbytes))
        view.release()
        del view,p
    events, a = [], 0
    for k,kind in enumerate((s.AV,s.A,s.V,s.AV,s.A,s.V),1):
        audio = visual = None
        end = k*100000000
        if kind != s.V:
            audio = dict(source_id="neutral-a",clock_id="audio.sample",start_tick=a*4800,end_tick=(a+1)*4800,
                hop_start=a*10,hop_end=(a+1)*10,endpoint_snapshot_index=a*10,common_window=[end-10000000,end])
            a += 1
        if kind != s.A:
            f = 3*k-1
            visual = dict(source_id="neutral-v" if kind==s.AV else "neutral-cue" if k==3 else "neutral-other",
                clock_id="video.frame",start_tick=f,end_tick=f+1,common_window=[f*1000000000//30,end])
        events.append(dict(event_id=f"e{k:02d}",ordinal=k,event_type=kind,recipe_id="neutral-00",
            source_occurrence_id=f"neutral-no-e{k:02d}",field_clock_id=run.FIELD_CLOCK,
            common_end_tick=end,auditory=audio,visual=visual))
    x = s.sealed(dict(sources=sources,events=events,
        profile=dict(coordinator_config_digest=ng.ne.make_config().config_digest)),"execution_digest")
    return run.nh.BoundExecution("NEUTRAL",s.canonical(x).decode())


def changed_bound(bound, mutate):
    x = bound.payload()
    mutate(x)
    x.pop("execution_digest")
    return run.nh.BoundExecution("NEUTRAL",s.canonical(s.sealed(x,"execution_digest")).decode())


def reseal(value, key="record_digest"):
    value.pop(key,None)
    return s.sealed(value,key)


class ConnectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = nn.profile.build_config()
        cls.bound = neutral_plan()
        cls.trace, cls.raw = [], []
        project, pair, cue = run.half.project_auditory_half_v1, nn.profile.bind_pair, nn.profile.bind_cue
        def measured(raw, **kw):
            cls.raw.append(raw)
            value = project(raw, **kw)
            cls.trace.append(("NJ",value.projection_digest))
            return value
        def pairing(**kw):
            if cls.trace[-1] != ("NJ",kw["projection"].projection_digest):
                raise AssertionError("CONTACT_BEFORE_NJ")
            cls.trace.append(("CONTACT",kw["projection"].projection_digest))
            return pair(**kw)
        def cueing(**kw):
            if cls.trace[-1] != ("NJ",kw["projection"].projection_digest):
                raise AssertionError("CONTACT_BEFORE_NJ")
            cls.trace.append(("CONTACT",kw["projection"].projection_digest))
            return cue(**kw)
        cls.materializer = run.Materializer(cls.bound,cls.config)
        with patch.object(run.half,"project_auditory_half_v1",side_effect=measured), \
             patch.object(nn.profile,"bind_pair",side_effect=pairing), \
             patch.object(nn.profile,"bind_cue",side_effect=cueing), \
             patch.object(run.nh,"from_auditory_receptor_state",side_effect=AssertionError("OLD_CONTACT_FORBIDDEN")):
            cls.materialized = cls.materializer.run_once()
        METRICS.update({k:v for k,v in json.loads(cls.materialized.metrics_json).items() if k in METRICS})
        cls.comparison = run.compose(cls.materialized,cls.config,"s2no-neutral-connection","NEUTRAL")
        METRICS.update(runtime_events=12,formation_attempts=4,field_contacts=2688)
        cls.record = run.envelope("s2no-neutral-connection",cls.bound,cls.config,cls.materialized,cls.comparison)
        archive("neutral-recording.json",cls.record)
        cls.proof = verify.verify_bindings(cls.record,cls.bound,cls.config)
        archive("neutral-verification.json",cls.proof)
        cases = [dict(ordinal=n,expected_context=True,target_recipe="neutral-00",variant="NEUTRAL",
                      phase="EARLY" if n<4 else "LATE") for n in (2,3,5,6)]
        cls.root = s.sealed(dict(execution_digest=cls.bound.payload()["execution_digest"],cases=cases,
            expected_support={"neutral-00":3}),"evaluation_digest")
        cls.evaluation = verify.evaluate(cls.record,cls.proof,cls.bound,cls.root,cls.config)
        archive("neutral-evaluation.json",cls.evaluation)

    def test_01_single_half_before_contact(self):
        self.assertEqual([k for k,_ in self.trace],["NJ","CONTACT"]*4)
        self.assertEqual(self.materializer.metrics["nj_projections"],4)
        endpoints = [e for e in self.materialized.events if e.event_type != s.V]
        for raw,e in zip(self.raw,endpoints,strict=True):
            frame = e.field_payload.timed_frames[0].frame
            self.assertEqual(frame.values,tuple(v*0.5 for v in raw.energy))
            self.assertEqual(frame.geometry_id,run.half.GEOMETRY)

    def test_02_double_half_rejected(self):
        e = self.materialized.events[0]
        p = verify.decode_projection(self.record["source_receipts"][0]["nj"],
            e.field_payload.timed_frames[0].frame,self.bound.payload()["events"][0]["auditory"])
        with self.assertRaisesRegex(run.half.S2NJProjectionError,"RAW_STATE_REQUIRED"):
            nn.bind_event(config=self.config,event_id="neutral-double",ordinal=1,event_type=s.A,
                field_start_tick=0,common_time=nn.CommonFieldTime(run.FIELD_CLOCK,90000000,100000000),
                raw_audio=p,pcm_digest="1"*64)

    def test_03_distinct_windows_preserved(self):
        for i in (0,3):
            e = self.materialized.events[i]
            a,v = e.field_payload.timed_frames
            spec = self.bound.payload()["events"][i]
            self.assertNotEqual(a.field_time,v.field_time)
            self.assertEqual((v.field_time.window_start_tick,v.field_time.window_end_tick),tuple(spec["visual"]["common_window"]))
            self.assertEqual(e.operation_payload.auditory.timed_frame,a)
            self.assertEqual(e.operation_payload.visual.timed_frame,v)
            self.assertEqual((e.operation_payload.plan.overlap_start_tick,e.operation_payload.plan.overlap_end_tick),
                (max(a.field_time.window_start_tick,v.field_time.window_start_tick),
                 min(a.field_time.window_end_tick,v.field_time.window_end_tick)))

    def test_04_invalid_time_bindings_independent(self):
        mutations = (lambda x:x["events"][0]["visual"]["common_window"].__setitem__(0,90000000),
            lambda x:x["events"][3]["auditory"].update(start_tick=4800),
            lambda x:x["events"][0].update(field_clock_id="foreign"),
            lambda x:x["events"][2]["visual"].update(clock_id="audio.sample"))
        for i,m in enumerate(mutations):
            with self.subTest(i=i), self.assertRaises(run.nh.S2NHRuntimeError):
                changed_bound(self.bound,m)

    def test_05_nn_default_not_relaxed(self):
        e = self.materialized.events[0]
        a,v = e.field_payload.timed_frames
        kw = dict(config=self.config,event_id="neutral-time",ordinal=1,event_type=s.AV,field_start_tick=0,
            common_time=a.field_time,raw_audio=self.raw[0],pcm_digest="1"*64,visual=v,rgb_digest="2"*64)
        with self.assertRaisesRegex(nn.S2NNError,"VISUAL_TIME_INVALID"):
            nn.bind_event(**kw)
        for time in (nn.CommonFieldTime("foreign",66666666,100000000),
                     nn.CommonFieldTime(run.FIELD_CLOCK,90000000,100000000)):
            with self.subTest(time=time), self.assertRaisesRegex(nn.S2NNError,"VISUAL_TIME_BINDING_INVALID"):
                nn.bind_event(**kw,visual_time_binding=time)

    def test_06_continuing_hearing_and_memory(self):
        self.assertEqual(self.materializer.metrics,dict(audio_windows=4,visual_frames=4,audio_hops=40,
            audio_snapshots=31,nj_projections=4,completed_events=6))
        self.assertEqual(self.raw[2].snapshot_index,20)
        self.assertEqual((self.raw[2].window_start_sample,self.raw[2].window_end_sample),(9600,14400))
        arm = self.comparison["pairs"][3]["arms"][0]
        self.assertEqual(arm["pre"]["memory_state_digest"],self.comparison["pairs"][0]["arms"][0]["memory"])
        self.assertEqual(self.comparison["states"][arm["memory"]]["generation"],2)

    def test_07_shared_inputs_separate_states(self):
        self.assertTrue(self.proof["comparison_verification"]["sibling_states_equal"])
        for pair in self.comparison["pairs"]:
            a,b = pair["arms"]
            self.assertEqual(a["memory"],b["memory"])
            self.assertEqual(a["field"],b["field"])
        self.assertNotEqual(self.comparison["runtime_configs"][0]["runtime_id"],self.comparison["runtime_configs"][1]["runtime_id"])

    def test_08_readonly_hints_and_lifecycle(self):
        for i in (1,2,4,5):
            for arm in self.comparison["pairs"][i]["arms"]:
                self.assertEqual(arm["pre"]["memory_state_digest"],arm["post"]["memory_state_digest"])
                self.assertEqual(arm["step"]["perception_status"],"FIELD_CONTACT_RECORDED")
        self.assertTrue(all(s["status"]=="CLOSED" and s["processed_event_count"]==6 for s in self.comparison["final"]))

    def test_09_profiles_separate(self):
        with self.assertRaisesRegex(nn.S2NNError,"HALF_PROFILE_REQUIRED"):
            run.Materializer(self.bound,ng.ne.make_config())
        b = changed_bound(self.bound,lambda x:x["profile"].update(coordinator_config_digest=self.config.config_digest))
        with self.assertRaisesRegex(run.S2NOError,"SOURCE_PROFILE_INVALID"):
            run.Materializer(b,self.config)
        r = deepcopy(self.record)
        r["profile"]["config_digest"] = "0"*64
        with self.assertRaisesRegex(run.S2NOError,"RECORD_PROFILE_INVALID"):
            verify.verify_bindings(reseal(r),self.bound,self.config)

    def test_10_raw_and_projection_receipts(self):
        endpoints = [r for r in self.record["source_receipts"] if r["nj"] is not None]
        for raw,r in zip(self.raw,endpoints,strict=True):
            self.assertEqual(r["nj"]["source_state_digest"],raw.digest())
            self.assertEqual(r["nj"]["source_values_digest"],s.digest(list(raw.energy)))
        self.assertFalse(self.proof["offline_scope"]["half_multiplication_recomputed"])
        self.assertFalse(self.proof["offline_scope"]["raw_underflow_claim_recomputed"])
        self.assertTrue(self.proof["offline_scope"]["nj_digest_and_rounded_values_checked"])

    def test_11_source_and_nj_manipulations(self):
        for field in ("source_state_digest","source_values_digest","projection_digest"):
            with self.subTest(field=field):
                r = deepcopy(self.record)
                r["source_receipts"][0]["nj"][field] = "0"*64
                r["source_receipts"][0] = reseal(r["source_receipts"][0],"receipt_digest")
                with self.assertRaises(run.S2NOError): verify.verify_bindings(reseal(r),self.bound,self.config)
        r = deepcopy(self.record)
        r["source_receipts"][1]["base"]["auditory"]["payload_sha256"] = "0"*64
        r["source_receipts"][1] = reseal(r["source_receipts"][1],"receipt_digest")
        with self.assertRaisesRegex(run.S2NOError,"SOURCE_RECEIPT_INVALID"):
            verify.verify_bindings(reseal(r),self.bound,self.config)

    def test_12_complete_receipts_and_counters(self):
        for mode in ("remove","swap","count"):
            with self.subTest(mode=mode):
                r = deepcopy(self.record)
                if mode == "remove": r["source_receipts"].pop()
                elif mode == "swap": r["source_receipts"][1:3] = reversed(r["source_receipts"][1:3])
                else: r["materialization"]["nj_projections"] += 1
                with self.assertRaises(run.S2NOError): verify.verify_bindings(reseal(r),self.bound,self.config)

    def test_13_full_scans_and_size(self):
        self.assertTrue(self.proof["comparison_verification"]["baseline_equal"])
        self.assertEqual(len(self.comparison["scans"]),16)
        for r in self.comparison["scans"]:
            q = r["value"].get("evidence",r["value"])
            self.assertEqual([len(b["records"]) for b in q["bank_scans"]],[9,3,8] if r["ordinal"] in (2,5) else [9,3,4])
            self.assertLess(len(s.canonical(r["value"])),32768)
        self.assertLessEqual(len(s.canonical(self.record)),ng.MAX_BYTES)
        outer = {**self.record,"comparison":None}
        self.assertLessEqual(len(s.canonical(outer)),run.MAX_ENVELOPE_BYTES)
        # Capacity-only byte fixture, not a 28-event source or runtime story.
        largest = deepcopy(self.record["source_receipts"][0])
        largest["nj"]["subnormal_band_indices"] = list(range(48))
        largest["nj"]["underflow_band_indices"] = list(range(48))
        outer["source_receipts"] = [largest]*24+[self.record["source_receipts"][2]]*4
        METRICS["max_capacity_envelope_bytes"] = len(s.canonical(outer))
        self.assertLessEqual(len(s.canonical(outer)),run.MAX_ENVELOPE_BYTES)
        self.assertLessEqual(ng.SERIALIZATION_BOUND+run.MAX_ENVELOPE_BYTES,ng.MAX_BYTES)
        r = deepcopy(self.record)
        r["oversized"] = "x"*run.MAX_ENVELOPE_BYTES
        with self.assertRaisesRegex(run.S2NOError,"RECORD_SIZE_EXCEEDED"):
            verify.verify_bindings(reseal(r),self.bound,self.config)

    def test_14_payload_failure_before_receptor(self):
        def wrong(x):
            x["sources"][0]["payload_sha256"] = "0"*64
            x["sources"][0] = reseal(x["sources"][0],"source_digest")
        bound = changed_bound(self.bound,wrong)
        m = run.Materializer(bound,self.config)
        with patch.object(run.BroadbandHearingPath,"push",side_effect=AssertionError("RECEPTOR_AFTER_HASH_FAILURE")):
            with self.assertRaisesRegex(run.S2NOError,"PAYLOAD_HASH_INVALID") as caught:
                m.run_once()
        failure = run.failure_evidence(m.phase,caught.exception,m)
        r = run.envelope("s2no-neutral-hash-failure",bound,self.config,failure=failure)
        proof = verify.verify_bindings(r,bound,self.config)
        self.assertTrue(proof["evidence_valid"])
        self.assertEqual(proof["status"],"NOT_EVALUABLE")
        self.assertEqual(failure["metrics"]["audio_hops"],0)
        archive("payload-failure.json",r)
        archive("payload-failure-proof.json",proof)
        r["failure"]["metrics"]["completed_events"] = 1
        with self.assertRaises(run.S2NOError): verify.verify_bindings(reseal(r),bound,self.config)

    def test_15_scan_error_field_survives(self):
        c = ng.RuntimeComparison(config=self.config,events=self.materialized.events[:2],field_clock_id=run.FIELD_CLOCK,
                                 comparison_id="s2no-neutral-scan-failure",mode="NEUTRAL")
        def fail(state,event):
            raise ValueError("neutral scan fault")
        for subject in c.subjects:
            subject._processor._auditory_scan = fail
            subject._processor._auditory_baseline = fail
        try:
            for _ in c.events: c.process_next()
            r = c.finish()
        finally:
            for subject in c.subjects:
                if subject.snapshot().status=="OPEN": subject.close()
        METRICS["runtime_events"] += 4
        METRICS["formation_attempts"] += 2
        METRICS["field_contacts"] += 768
        proof = verify.direct.verify_record(r,config=self.config)
        self.assertEqual(proof["status"],"NOT_EVALUABLE")
        for a in r["pairs"][-1]["arms"]:
            self.assertEqual(a["step"]["perception_status"],"FIELD_CONTACT_RECORDED")
            self.assertEqual(a["pre"]["memory_state_digest"],a["post"]["memory_state_digest"])
        archive("scan-failure.json",r)
        archive("scan-failure-proof.json",proof)

    def test_16_technical_vs_functional(self):
        self.assertEqual(self.proof["status"],"RECORDING_COMPLETE")
        row = self.evaluation["comparison"]["rows"][-1]
        self.assertTrue(row["reference_abstains"] and row["alternative_abstains"])
        self.assertFalse(row["reference_correct"] or row["alternative_correct"])
        self.assertFalse(any(p["predicted_support_present"] for p in self.evaluation["support_report"]))
        self.assertTrue(self.evaluation["origin_is_not_implied_by_numeric_equality"])
        bad = deepcopy(self.proof)
        bad["status"] = "NOT_EVALUABLE"
        with self.assertRaises(run.nh.S2NHRuntimeError):
            verify.evaluate(self.record,reseal(bad,"verification_digest"),self.bound,self.root,self.config)

    def test_17_single_file_verification_and_write_conflict(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"recording.json"
            ng.ne.atomic_write(path,self.record)
            before = s.filehash(path)
            with patch.object(run.Materializer,"run_once",side_effect=AssertionError("OFFLINE_NO_MATERIALIZER")), \
                 patch.object(run.half,"project_auditory_half_v1",side_effect=AssertionError("OFFLINE_NO_NJ")):
                proof = verify.verify_once(path,self.bound,self.config)
            self.assertTrue(proof["evidence_valid"] and proof["file_unchanged"])
            self.assertEqual(before,s.filehash(path))
            with self.assertRaises(run.S2NOError): verify.verify_once(path,self.bound,self.config)
            with self.assertRaises(FileExistsError): ng.ne.atomic_write(path,self.record)

    def test_18_gates_one_shot_and_immutability(self):
        with self.assertRaises(FrozenInstanceError): self.materialized.events=()
        with self.assertRaisesRegex(run.S2NOError,"MATERIALIZATION_ALREADY_USED"): self.materializer.run_once()
        with self.assertRaisesRegex(run.S2NOError,"MAIN_GATE_CLOSED_OR_USED"):
            run.run_main_once("invalid",Path("invalid"))
        self.assertFalse(run._MAIN_USED)
        self.assertFalse(run.MAIN_GATE or ng.MAIN_GATE or nn.MAIN_GATE or run.nh.MAIN_GATE)
        self.assertEqual(s.digest(self.record),s.digest(json.loads((Path(os.environ["S2NO_QUAL_DIR"])/"neutral-recording.json").read_bytes())))

    def test_19_exact_historical_bindings_no_payloads(self):
        with patch.object(s,"pcm_payload",side_effect=AssertionError("NO_NH_PCM")), \
             patch.object(s,"rgb_payload",side_effect=AssertionError("NO_NH_RGB")):
            bound = run.load_execution()
        self.assertEqual(bound.payload()["execution_digest"],run.nh.EXECUTION_DIGEST)
        q = json.loads((run.ROOT/run.NN_QUAL).read_bytes())
        x = bound.payload()
        x["source_hashes"]["tools/_s2nh_private_source_binding.py"] = "0"*64
        with self.assertRaisesRegex(run.S2NOError,"HISTORICAL_SOURCE_CHANGED"): run.historical_bindings(x,q)
        self.assertEqual(METRICS["nh_payloads"],0)

    def test_20_denominators_no_offset(self):
        base = dict(modality="auditory",expected_context=True,variant="VARIED",competition="COMPETITION_PRESENT",
            reference_false_admission=False,alternative_false_admission=False,reference_abstains=False,
            alternative_abstains=False,discarded_target_candidates=[])
        rows = [dict(base,ordinal=1,reference_correct=True,alternative_correct=False),
            dict(base,ordinal=2,reference_correct=False,alternative_correct=True),
            dict(base,ordinal=3,modality="visual",reference_correct=True,alternative_correct=True)]
        summarize = verify.nhv.evaluation.summarize
        g = summarize(rows)["auditory"]["ALL"]
        self.assertEqual((g["D"],g["R"],g["L"]),(1,0,1))
        self.assertEqual(g["gains"],[2])
        self.assertEqual(summarize(rows[1:])["auditory"]["ALL"]["retention_status"],"ERHALTUNG_NICHT_GEPRUEFT")


def tearDownModule():
    archive("metrics.json",METRICS)


if __name__ == "__main__":
    unittest.main()
