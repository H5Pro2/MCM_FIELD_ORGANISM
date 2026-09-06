"""Exactly one neutral NH binding qualification; no sealed NH payloads."""

from copy import deepcopy
from dataclasses import FrozenInstanceError
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from tools import _s2nh_private_runtime_binding as run
from tools import _s2nh_private_runtime_verification as verify

s=run.source
METRICS=dict(nh_payloads=0,main_calls=0,neutral_pcm_generated=0,neutral_rgb_generated=0)


def neutral_plan(config):
    audio=s.audio_recipe("neutral-nh-runtime-20260906",0)
    audio["amplitude"]=s.f32(0.01)
    specs=(s.SourceSpec("neutral-a","PCM",s.canonical(audio).decode()),
        s.SourceSpec("neutral-v","RGB",s.canonical(s.rgb_recipe("neutral-nh-grid-01",False)).decode()),
        s.SourceSpec("neutral-cue","RGB_CUE",s.canonical(s.rgb_recipe("neutral-nh-grid-01",True)).decode()),
        s.SourceSpec("neutral-other","RGB_CUE",s.canonical(s.rgb_recipe("neutral-nh-grid-02",True)).decode()))
    sources=[]
    for spec in specs:
        p=s.pcm_payload(json.loads(spec.recipe_json)) if spec.kind=="PCM" else s.rgb_payload(json.loads(spec.recipe_json))
        METRICS["neutral_pcm_generated" if spec.kind=="PCM" else "neutral_rgb_generated"]+=1
        view=memoryview(p).cast("B")
        sources.append(s.bind_source(spec,hashlib.sha256(view).hexdigest(),view.nbytes))
        view.release()
        del view,p
    events=[]
    a=0
    for k,kind in enumerate((s.AV,s.A,s.V,s.AV,s.A,s.V),1):
        audio=visual=None
        end=k*100000000
        if kind!=s.V:
            audio=dict(source_id="neutral-a",clock_id="audio.sample",start_tick=a*4800,end_tick=(a+1)*4800,
                hop_start=a*10,hop_end=(a+1)*10,endpoint_snapshot_index=a*10,common_window=[end-10000000,end])
            a+=1
        if kind!=s.A:
            f=3*k-1
            visual=dict(source_id="neutral-v" if kind==s.AV else "neutral-cue" if k==3 else "neutral-other",
                clock_id="video.frame",start_tick=f,end_tick=f+1,common_window=[f*1000000000//30,end])
        events.append(dict(event_id=f"e{k:02d}",ordinal=k,event_type=kind,recipe_id="neutral-00",
            source_occurrence_id=f"neutral-source-e{k:02d}",field_clock_id=run.FIELD_CLOCK,
            common_end_tick=end,auditory=audio,visual=visual))
    x=s.sealed(dict(sources=sources,events=events,profile=dict(coordinator_config_digest=config.config_digest)),"execution_digest")
    return run.BoundExecution("NEUTRAL",s.canonical(x).decode())


def changed_bound(bound,mutate):
    x=bound.payload()
    mutate(x)
    x.pop("execution_digest")
    return run.BoundExecution("NEUTRAL",s.canonical(s.sealed(x,"execution_digest")).decode())


def reseal(record):
    record.pop("record_digest",None)
    return s.sealed(record,"record_digest")


def archive(name,value):
    root=os.environ.get("S2NH_QUALIFICATION_ARTIFACTS")
    if root:
        run.ng.ne.atomic_write(Path(root)/name,value)


class RuntimeBindingQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config=run.ng.ne.make_config()
        cls.bound=neutral_plan(cls.config)
        cls.materializer=run.Materializer(cls.bound,cls.config)
        try:
            cls.materialized=cls.materializer.run_once()
        except Exception as error:
            archive("neutral-materialization-error.json",dict(phase=cls.materializer.phase,ordinal=cls.materializer.ordinal,
                source_id=cls.materializer.source_id,metrics=cls.materializer.metrics,error_class=type(error).__name__))
            raise
        METRICS["neutral_pcm_generated"]+=4
        METRICS["neutral_rgb_generated"]+=4
        METRICS.update(json.loads(cls.materialized.metrics_json))
        cls.comparison=run.compose(cls.materialized,cls.config,"s2nh-neutral-runtime-pair-01","NEUTRAL")
        cls.record=run.envelope("s2nh-neutral-runtime-pair-01",cls.bound,cls.materialized,cls.comparison)
        archive("neutral-recording.json",cls.record)
        cls.proof=verify.verify_bindings(cls.record,cls.bound,cls.config)
        archive("neutral-verification.json",cls.proof)
        cases=[dict(ordinal=n,expected_context=True,target_recipe="neutral-00",variant="NEUTRAL",
                    phase="EARLY" if n<4 else "LATE") for n in (2,3,5,6)]
        cls.root=s.sealed(dict(execution_digest=cls.bound.payload()["execution_digest"],cases=cases,
            expected_support={"neutral-00":3}),"evaluation_digest")
        cls.before_evaluation=s.digest(cls.record)
        cls.evaluated=verify.evaluate(cls.record,cls.proof,cls.bound,cls.root,cls.config)
        archive("neutral-evaluation.json",cls.evaluated)
        METRICS.update(neutral_formations_total=4,neutral_runtime_events=12,
            field_contacts=cls.proof["comparison_verification"]["field_contacts"],
            record_bytes=len(s.canonical(cls.record)),evaluation_bytes=len(s.canonical(cls.evaluated)))

    @classmethod
    def tearDownClass(cls):
        archive("neutral-metrics.json",METRICS)
        print(json.dumps(METRICS,sort_keys=True))

    def test_01_plan_and_input_immutability(self):
        with self.assertRaises(FrozenInstanceError):
            self.bound.mode="MAIN"
        with self.assertRaises(FrozenInstanceError):
            self.materialized.events=()
        self.assertIs(type(self.materialized.events),tuple)
        self.assertEqual(len(self.materialized.events),6)

    def test_02_native_audio_continues_over_visual_only(self):
        m=json.loads(self.materialized.metrics_json)
        self.assertEqual(m,dict(audio_windows=4,visual_frames=4,audio_hops=40,audio_snapshots=31,completed_events=6))
        a=self.materialized.events[3].field_payload.timed_frames[0].frame
        self.assertEqual((a.window_start_tick,a.window_end_tick,a.snapshot_id),(9600,14400,"auditory.receptor.20"))
        self.assertEqual(self.materialized.events[4].operation_payload.cue.auditory_window_end_tick,19200)

    def test_03_cue_payload_and_state_bindings(self):
        receipts=json.loads(self.materialized.receipts_json)
        for i in (1,4):
            cue=self.materialized.events[i].operation_payload.cue
            self.assertEqual(cue.pcm_payload_digest,receipts[i]["base"]["auditory"]["payload_sha256"])
            self.assertEqual(cue.receptor_state_digest,receipts[i]["base"]["auditory"]["receptor_state_digest"])
        for i in (2,5):
            event=self.materialized.events[i]
            self.assertEqual(event.operation_payload.source_digest,receipts[i]["source_digest"])
            self.assertEqual(event.field_payload.timed_frames[0].frame.values[32:],(0.0,)*256)

    def test_04_explicit_field_clock_and_contacts(self):
        self.assertEqual(self.proof["comparison_verification"]["field_contacts"],2688)
        for event in self.materialized.events:
            self.assertTrue(all(t.field_time.clock_id==run.FIELD_CLOCK for t in event.field_payload.timed_frames))
        self.assertTrue(all(x["field"]["step_count"]==6 for x in self.comparison["pairs"][-1]["arms"]))

    def test_05_isolation_fixed_rules_and_shared_inputs(self):
        self.assertTrue(self.proof["comparison_verification"]["sibling_states_equal"])
        self.assertNotEqual(self.comparison["runtime_configs"][0]["runtime_id"],self.comparison["runtime_configs"][1]["runtime_id"])
        self.assertNotEqual(self.comparison["bindings"][0],self.comparison["bindings"][1])
        for pair in self.comparison["pairs"]:
            self.assertEqual(pair["arms"][0]["memory"],pair["arms"][1]["memory"])
            self.assertEqual(pair["arms"][0]["field"],pair["arms"][1]["field"])

    def test_06_early_read_only_no_restart(self):
        for i in (1,2,4,5):
            for arm in self.comparison["pairs"][i]["arms"]:
                self.assertEqual(arm["pre"]["memory_state_digest"],arm["memory"])
        post=self.comparison["pairs"][3]["arms"][0]["memory"]
        self.assertEqual(self.comparison["states"][post]["generation"],2)
        self.assertEqual(self.comparison["pairs"][3]["arms"][0]["pre"]["memory_state_digest"],self.comparison["pairs"][0]["arms"][0]["memory"])

    def test_07_valid_abstention_and_unmet_support_evaluable(self):
        self.assertEqual(self.proof["status"],"RECORDING_COMPLETE")
        last=self.evaluated["comparison"]["rows"][-1]
        self.assertTrue(last["reference_abstains"] and last["alternative_abstains"])
        self.assertFalse(last["reference_correct"] or last["alternative_correct"])
        self.assertTrue(all(not x["predicted_support_present"] for x in self.evaluated["support_report"]))

    def test_08_lifecycle_and_baselines(self):
        self.assertTrue(all(x["status"]=="CLOSED" and x["processed_event_count"]==6 for x in self.comparison["final"]))
        self.assertTrue(self.proof["comparison_verification"]["baseline_equal"])
        self.assertEqual(self.proof["comparison_verification"]["scan_receipts"],16)

    def test_09_receipt_removal_and_reordering(self):
        for mode in ("remove","swap"):
            with self.subTest(mode=mode):
                r=deepcopy(self.record)
                if mode=="remove": r["source_receipts"].pop()
                else: r["source_receipts"][1:3]=reversed(r["source_receipts"][1:3])
                with self.assertRaises(run.S2NHRuntimeError):
                    verify.verify_bindings(reseal(r),self.bound,self.config)

    def test_10_source_time_and_clock_fail_closed(self):
        mutations=(lambda x:x["events"][3]["auditory"].update(start_tick=4800),
            lambda x:x["events"][2]["visual"].update(clock_id="audio.sample"),
            lambda x:x["events"][0].update(field_clock_id="foreign-clock"))
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                with self.assertRaises(run.S2NHRuntimeError): changed_bound(self.bound,mutate)

    def test_11_digest_manipulation(self):
        r=deepcopy(self.record)
        receipt=r["source_receipts"][1]
        receipt["base"]["auditory"]["receptor_state_digest"]="a"*64
        receipt.pop("receipt_digest")
        r["source_receipts"][1]=s.sealed(receipt,"receipt_digest")
        with self.assertRaises(run.S2NHRuntimeError): verify.verify_bindings(reseal(r),self.bound,self.config)

    def test_12_counts_and_output_limits(self):
        self.assertLessEqual(len(s.canonical(self.record)),run.ng.MAX_BYTES)
        self.assertLessEqual(len(s.canonical({**self.record,"comparison":None})),run.MAX_ENVELOPE_BYTES)
        self.assertLessEqual(run.ng.SERIALIZATION_BOUND+run.MAX_ENVELOPE_BYTES,run.ng.MAX_BYTES)
        r=deepcopy(self.record)
        r["materialization"]["audio_snapshots"]+=1
        with self.assertRaises(run.S2NHRuntimeError): verify.verify_bindings(reseal(r),self.bound,self.config)
        huge=run.envelope("neutral-large",self.bound,self.materialized,{**self.comparison,"extra":"x"*run.ng.MAX_BYTES})
        self.assertEqual(huge["failure"]["code"],"RECORD_SIZE_EXCEEDED")
        self.assertEqual(huge["status"],"NOT_EVALUABLE")

    def test_13_no_second_materialization_main_closed(self):
        with self.assertRaises(run.S2NHRuntimeError): self.materializer.run_once()
        self.assertFalse(run.MAIN_GATE or run.ng.MAIN_GATE or s.MAIN_GATE)
        with self.assertRaises(run.S2NHRuntimeError): run.run_main_once("invalid",Path("invalid"))
        self.assertFalse(run._MAIN_USED)

    def test_14_failure_record_and_one_read_only_file_check(self):
        failure=dict(phase="PAYLOAD_HASH",ordinal=1,source_id="neutral-a",code="PAYLOAD_HASH_INVALID",error_class="S2NHRuntimeError")
        r=run.envelope("neutral-failure",self.bound,None,None,failure)
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"recording.json"
            run.ng.ne.atomic_write(p,r)
            before=s.filehash(p)
            proof=verify.verify_once(p,self.bound,self.config)
            self.assertTrue(proof["evidence_valid"] and proof["file_unchanged"])
            self.assertEqual(proof["status"],"NOT_EVALUABLE")
            self.assertEqual(before,s.filehash(p))
            with self.assertRaises(run.S2NHRuntimeError): verify.verify_once(p,self.bound,self.config)

    def test_15_atomic_write_conflict(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"recording.json"
            run.ng.ne.atomic_write(p,self.record)
            before=p.read_bytes()
            with self.assertRaises(FileExistsError): run.ng.ne.atomic_write(p,self.record)
            self.assertEqual(p.read_bytes(),before)

    def test_16_evaluation_root_and_record_unchanged(self):
        before=s.digest(self.record)
        self.assertEqual(before,self.before_evaluation)
        wrong=deepcopy(self.root)
        wrong["execution_digest"]="0"*64
        wrong.pop("evaluation_digest")
        with self.assertRaises(run.S2NHRuntimeError):
            verify.evaluate(self.record,self.proof,self.bound,s.sealed(wrong,"evaluation_digest"),self.config)
        self.assertEqual(before,s.digest(self.record))

    def test_17_loss_gain_and_modality_denominators(self):
        template=dict(modality="auditory",expected_context=True,variant="VARIED",competition="COMPETITION_PRESENT",
            reference_false_admission=False,alternative_false_admission=False,reference_abstains=False,alternative_abstains=False,
            discarded_target_candidates=[])
        rows=[dict(template,ordinal=1,reference_correct=True,alternative_correct=False),
              dict(template,ordinal=2,reference_correct=False,alternative_correct=True),
              dict(template,ordinal=3,modality="visual",reference_correct=True,alternative_correct=True)]
        groups=verify.evaluation.summarize(rows)
        self.assertEqual(tuple(groups["auditory"]["ALL"][k] for k in ("N","D","R","L")),(2,1,0,1))
        self.assertEqual(groups["auditory"]["ALL"]["gains"],[2])
        zero=verify.evaluation.summarize(rows[1:])
        self.assertEqual(zero["auditory"]["ALL"]["retention_status"],"ERHALTUNG_NICHT_GEPRUEFT")
        rows[0]["discarded_target_candidates"]=[dict(slot_id="neutral-slot")]
        self.assertEqual(verify.evaluation.summarize(rows)["auditory"]["ALL"]["discarded_target_candidates"],
            [dict(ordinal=1,candidates=[dict(slot_id="neutral-slot")])])

    def test_18_ppb_lineage_saturation_mixing_replacement(self):
        def state(slot):
            return dict(tspm_state={m+"_ppb1_state":dict(slots=[deepcopy(slot)]) for m in ("auditory","visual")})
        blank=dict(slot_id="neutral-slot",occupied=False,support_count=0,prototype_values=[])
        history={m:{} for m in ("auditory","visual")}
        pre=state(blank)
        labels=[]
        for n,(support,recipe) in enumerate(((1,"neutral-a"),(2,"neutral-a"),(3,"neutral-a"),(3,"neutral-b"),(1,"neutral-c")),1):
            post=state(dict(slot_id="neutral-slot",occupied=True,support_count=support,prototype_values=[n/10]))
            t=verify.advance_lineage(pre,post,dict(ordinal=n,recipe_id=recipe),history,self.config)
            labels.append(t[0]["event"])
            if n==4: self.assertTrue(t[0]["mixed"])
            pre=post
        self.assertEqual(labels,["CREATED","MATCHED","MATCHED","MATCHED","REPLACED"])
        self.assertEqual(history["auditory"]["neutral-slot"],[dict(ordinal=5,recipe_id="neutral-c")])
        self.assertTrue(all(t["event"]=="NO_UPDATE" for t in verify.advance_lineage(pre,pre,dict(ordinal=6,recipe_id="neutral-c"),history,self.config)))

    def test_19_source_and_evaluation_roles_separated(self):
        self.assertTrue(all(src["recipe"]["seed"].startswith("neutral-") for src in self.bound.payload()["sources"]))
        self.assertNotIn("expected_support",self.materialized.receipts_json)
        self.assertNotIn("expected_context",s.canonical(self.comparison).decode())
        self.assertEqual(METRICS["nh_payloads"],0)
        bound=run.load_execution()
        self.assertEqual(len(bound.payload()["events"]),28)
        with self.assertRaises(run.S2NHRuntimeError): run.Materializer(bound,self.config)

    def test_20_complete_scans_and_no_raw_payloads(self):
        limits=run.ng.budget(tuple(e.event_type for e in self.materialized.events))
        self.assertLessEqual(self.proof["comparison_verification"]["value_comparisons"],limits["value_comparisons"])
        for scan in self.comparison["scans"]:
            p=scan["value"].get("evidence",scan["value"])
            self.assertEqual([len(b["records"]) for b in p["bank_scans"]],[9,3,8] if "evidence" in scan["value"] else [9,3,4])
            self.assertLess(len(s.canonical(scan["value"])),32768)
        def visit(value):
            self.assertNotIsInstance(value,(bytes,bytearray,memoryview))
            if isinstance(value,dict):
                for x in value.values(): visit(x)
            elif isinstance(value,list):
                for x in value: visit(x)
        visit(self.record)


if __name__=="__main__":
    unittest.main()
