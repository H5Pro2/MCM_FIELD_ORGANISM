"""Once-only neutral connections; no NS sources and no historical logic-suite replay."""
from copy import deepcopy
from dataclasses import asdict, replace, FrozenInstanceError
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import _s2ns_private_run as run
from tools import _s2ns_private_run_verification as verify
from tools import _s2ns_private_run_evaluation as evaluation

s,src,io = run.s,run.src,run.io
METRICS = dict(memory_calls=0,receptor_calls=0,nj_calls=0,visual_calls=0,ns_payloads=0,
    execution_scans=0,verification_scans=0,execution_terms=0,verification_terms=0,
    formation_checks=0,max_full_record_bytes=0,worst_schema_bytes=0)


def neutral_plan():
    # 16 real neutral formations, four intervening/read-only endpoints, one history.
    specs = [(0.0,0.0)]*4 + [(0.0,None)] + [(x,0.0) for x in (.025,.05,.075,.1,.125,.15,.175,.2)]
    specs += [(.2,None),(.9,0.0),(.9,1.0),(.9,.5),(.9,.5),(.9,None),(0.0,None)]
    sources,events = {},[]
    for n,(audio,visual) in enumerate(specs,1):
        # IDs are technical identities, not expected outcome roles.
        aid = "neutral-a-"+s.digest(audio)[:12]
        sid = None if visual is None else "neutral-v-"+s.digest(visual)[:12]
        for ident,value,kind in ((aid,audio,"PCM"),(sid,visual,"RGB")):
            if ident is not None:
                sources[ident] = io.sealed(dict(source_id=ident,kind=kind,neutral_value=value,
                    payload_sha256=s.digest([kind,value]),recipe=dict(neutral=True)),"source_digest")
        end = n*100000000
        events.append(dict(event_id=f"n{n:02d}",ordinal=n,history_id="neutral-h",starts_fresh_history=n==1,
            event_type=run.b.A if visual is None else run.b.AV,source_occurrence_id=f"neutral-source-{n}",
            pairing_clock_id="neutral-pairing-clock",auditory=dict(source_id=aid,clock_id="audio.sample",
                start_tick=(n-1)*4800,end_tick=n*4800,endpoint_snapshot_index=n-1,common_window=[end-10000000,end]),
            visual=None if visual is None else dict(source_id=sid,clock_id="video.frame",start_tick=3*n-1,
                end_tick=3*n,common_window=[(3*n-1)*1000000000//30,end])))
    return io.sealed(dict(schema="s2ns.neutral-plan.v2",sources=list(sources.values()),events=events),"execution_digest")


class NeutralSources:
    def __init__(self,config,plan):
        self.config,self.plan = config,plan
        self.audio_analyses = self.nj_projections = self.visual_analyses = 0
        self.phase = "NEUTRAL_REDUCED_SOURCE"

    def materialize(self,event):
        t = src.bind_time(event,self.plan["execution_digest"])
        scalar = src.row(self.plan,event["auditory"]["source_id"])["neutral_value"]
        raw = src.AuditoryReceptorState("auditory",s.profile.half.RAW_GEOMETRY,t.nj_snapshot_index,
            t.window_start_sample,t.window_end_sample,self.config.profile.profile.auditory_config.carrier_ids,
            (float(scalar*2.0),)*48,src.AuditoryReceptorContact.ACTIVE_ENERGY if scalar else src.AuditoryReceptorContact.ACTIVE_ZERO)
        self.nj_projections += 1
        p = s.profile.half.project_auditory_half_v1(raw,config=src.LogSpectralConfig(),source_profile_digest=s.profile.half.RAW_PROFILE_DIGEST)
        visual = None
        if event["visual"] is not None:
            v = event["visual"]
            value = src.row(self.plan,v["source_id"])["neutral_value"]
            vc = self.config.profile.profile.visual_config
            visual = src.ReceptorContactFrame("visual",vc.geometry_id,"neutral-visual-source",v["clock_id"],
                v["start_tick"],v["end_tick"],vc.carrier_ids,(float(value),)*288)
        return src.bind_reduced(event,self.plan,self.config,t,raw,p,visual)


def reseal(record,index=None):
    if index is not None:
        record["events"][index] = io.sealed({k:v for k,v in record["events"][index].items() if k != "event_digest"},"event_digest")
    return io.sealed({k:v for k,v in record.items() if k != "record_digest"},"record_digest")


def tearDownModule():
    print("NS_RUN_METRICS "+json.dumps(METRICS,sort_keys=True))


class RunBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config,cls.plan = s.profile.build_config(),neutral_plan()
        cls.temp = tempfile.TemporaryDirectory(prefix="s2ns-neutral-")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.depth = 0
        def count_call(key,fn):
            def call(*a,**kw):
                METRICS[key] += 1
                return fn(*a,**kw)
            return call
        def scan(fn):
            def call(*a,**kw):
                value = fn(*a,**kw)
                part = "verification" if cls.depth else "execution"
                METRICS[part+"_scans"] += 1
                METRICS[part+"_terms"] += value.comparisons
                return value
            return call
        cls.guards = [patch.object(s.memory,"advance_s2jv_atomic",side_effect=count_call("memory_calls",s.memory.advance_s2jv_atomic)),
            patch.object(s.profile.half,"project_auditory_half_v1",side_effect=count_call("nj_calls",s.profile.half.project_auditory_half_v1)),
            patch.object(s,"scan_view",side_effect=scan(s.scan_view)),patch.object(run.direct,"_scan",side_effect=scan(run.direct._scan)),
            patch.object(verify.formation_check,"_formation",side_effect=count_call("formation_checks",verify.formation_check._formation)),
            patch.object(src.b,"generators",side_effect=AssertionError("SEALED_GENERATORS_FORBIDDEN")),
            patch.object(src,"load_plan",side_effect=AssertionError("NS_PLAN_MATERIALIZATION_FORBIDDEN"))]
        for g in cls.guards:
            g.start()
            cls.addClassCleanup(g.stop)
        cls.path = run.execute_once(run_id="s2ns-neutral-chain",output_root=cls.temp.name,plan=cls.plan,provider_factory=NeutralSources)
        cls.record = json.loads(cls.path.read_bytes())
        root = Path(os.environ["S2NS_RUN_QUAL_DIR"])
        io.atomic_write(root/"neutral-recording.json",cls.record,run.LIMITS["record_bytes"])
        if cls.record["status"] != "RECORDING_COMPLETE":
            raise AssertionError("NEUTRAL_CHAIN_FAILED: "+json.dumps(cls.record["failure"]))
        cls.depth += 1
        try:
            vp = verify.verify_file_once(cls.path,plan=cls.plan,config=cls.config)
        finally:
            cls.depth -= 1
        wrapper = json.loads(vp.read_bytes())
        io.atomic_write(root/"neutral-verification.json",wrapper,run.LIMITS["record_bytes"])
        if wrapper["status"] != "RECORDING_COMPLETE":
            raise AssertionError("NEUTRAL_VERIFICATION_FAILED: "+json.dumps(wrapper))
        cls.proof = {k:v for k,v in wrapper.items() if k not in ("report_digest","file_sha256","file_unchanged")}
        METRICS["max_full_record_bytes"] = len(s.canonical(cls.record))

    def code(self,code,fn):
        with self.assertRaises(s.S2NSError) as caught:
            fn()
        self.assertEqual(code,caught.exception.code)

    def verify(self,record):
        type(self).depth += 1
        try:
            return verify.verify_record(record,plan=self.plan,config=self.config)
        finally:
            type(self).depth -= 1

    def test_01_historical_and_native_index(self):
        for n in (1,2,14,31):
            # Only literal sealed-plan metadata; no source values or generators.
            e = run.b.events()[n-1]
            t = src.bind_time(e,src.EXECUTION_DIGEST)
            self.assertEqual((n-1,10*(n-1)),(t.endpoint_snapshot_index,t.nj_snapshot_index))
            self.assertEqual((n-1)*4800,t.window_start_sample)
            with self.assertRaises(FrozenInstanceError):
                t.nj_snapshot_index = 0

    def test_02_exact_divisibility_and_types(self):
        for value in (-480,1,480.0,True):
            with self.subTest(start=value):
                e = deepcopy(self.plan["events"][0]); e["auditory"]["start_tick"] = value
                self.code("NATIVE_TIME_INVALID",lambda:src.bind_time(e,self.plan["execution_digest"]))

    def test_03_wrong_index_rejected_before_analysis(self):
        e = self.plan["events"][1]; t = src.bind_time(e,self.plan["execution_digest"])
        with patch.object(src.LogSpectralReceptor,"analyze",side_effect=AssertionError("ANALYSIS_FORBIDDEN")) as guard:
            self.code("TIME_BINDING_INVALID",lambda:src.analyze_endpoint(None,event=e,plan_digest=self.plan["execution_digest"],binding=replace(t,nj_snapshot_index=1)))
            guard.assert_not_called()

    def test_04_manipulated_event_and_plan_binding(self):
        e = self.plan["events"][1]; t = src.bind_time(e,self.plan["execution_digest"])
        for forged in (replace(t,plan_digest="f"*64),replace(t,event_id="foreign"),replace(t,window_end_sample=t.window_end_sample+480)):
            with self.subTest(binding=forged):
                self.code("TIME_BINDING_INVALID",lambda:src.validate_time(forged,e,self.plan["execution_digest"]))

    def test_05_real_neutral_materialization_order(self):
        import numpy as np
        from mcm_field_organism.finite_video_path import LocalChannelGridReceptor
        plan = deepcopy(self.plan)
        plan["events"] = deepcopy(plan["events"][:2])
        plan["events"][1]["event_type"] = run.b.A
        plan["events"][1]["visual"] = None
        pcm = bytes(19200)
        image = np.zeros((1080,1920,3),dtype=np.uint8)
        for i,row in enumerate(plan["sources"]):
            row["payload_sha256"] = hashlib.sha256(pcm if row["kind"] == "PCM" else memoryview(image).cast("B")).hexdigest()
            plan["sources"][i] = io.sealed({k:v for k,v in row.items() if k != "source_digest"},"source_digest")
        del image
        plan = io.sealed({k:v for k,v in plan.items() if k != "execution_digest"},"execution_digest")
        provider = object.__new__(src.Sources)
        provider.config,provider.plan = self.config,plan
        provider.audio_analyses = provider.nj_projections = provider.visual_analyses = 0
        provider.pcm = lambda recipe: bytearray(pcm)
        provider.rgb = lambda recipe: np.zeros((1080,1920,3),dtype=np.uint8)
        order = []
        original_analyze = src.LogSpectralReceptor.analyze
        original_bind = src.bind_reduced
        def analyze(obj,samples):
            METRICS["receptor_calls"] += 1; order.append("ANALYZE")
            return original_analyze(obj,samples)
        def bind(*a,**kw):
            order.append("CONTACT_OR_VIEWS")
            return original_bind(*a,**kw)
        with patch.object(src.LogSpectralReceptor,"analyze",new=analyze),patch.object(src,"bind_reduced",side_effect=bind):
            for e in plan["events"]:
                receipt,bound = provider.materialize(e)
                self.assertEqual(receipt["time_binding"]["nj_snapshot_index"],receipt["raw_state"]["snapshot_index"])
                self.assertEqual(receipt["projection"]["source_state_digest"],receipt["raw_state_digest"])
                src.restore(e,receipt,plan,self.config)
        METRICS["visual_calls"] += provider.visual_analyses
        self.assertEqual((2,2,1),(provider.audio_analyses,provider.nj_projections,provider.visual_analyses))
        self.assertEqual(2,order.count("ANALYZE"))

    def test_06_continuation_and_read_only(self):
        self.assertEqual((20,16,4),(self.record["counts"]["events"],self.record["counts"]["formations"],self.record["counts"]["cues"]))
        self.assertEqual(self.record["events"][3]["poststate"],self.record["events"][5]["prestate"])
        for e in self.record["events"]:
            if e["formation"] is None:
                self.assertEqual(e["prestate"],e["poststate"])
                self.assertEqual(2,len(e["results"]))
        self.assertTrue(self.proof["baseline_equal"])

    def test_07_actual_generations_created_matched_replaced(self):
        ppb = [t["ppb"][0]["event"] for t in self.proof["transitions"]]
        self.assertTrue({"CREATED","MATCHED","REPLACED"}.issubset(ppb))
        prior = {}
        for t in self.proof["transitions"]:
            for g in t["generations"]:
                i,action,d = g["index"],g["action"],g["generation_digest"]
                if action == "MATCHED":
                    self.assertEqual(prior[i],d)
                if action == "REPLACED":
                    self.assertNotEqual(prior[i],d)
                if action in ("FREE","CLEARED"):
                    self.assertIsNone(d)
                prior[i] = d

    def test_08_manipulated_generation_origin(self):
        r = deepcopy(self.record)
        g = next(x["generation"] for x in r["events"][4]["inventory"]["slots"] if x["generation"] is not None)
        g["input_digest"] = "f"*64
        self.code("GENERATION_CHAIN_INVALID",lambda:self.verify(reseal(r,4)))

    def test_09_manipulated_transaction(self):
        r = deepcopy(self.record)
        r["events"][0]["formation"]["result_digest"] = "f"*64
        self.code("RECORD_BINDING_INVALID",lambda:self.verify(reseal(r,0)))

    def test_10_missing_event(self):
        r = deepcopy(self.record); r["events"].pop()
        self.code("RECORD_COMPLETENESS_INVALID",lambda:self.verify(reseal(r)))

    def test_11_swapped_events(self):
        r = deepcopy(self.record); r["events"][0],r["events"][1] = r["events"][1],r["events"][0]
        self.code("EVENT_CHAIN_INVALID",lambda:self.verify(reseal(r)))

    def test_12_source_identity(self):
        r = deepcopy(self.record); e = r["events"][0]
        e["source"]["pcm_digest"] = "f"*64
        e["source"] = io.sealed({k:v for k,v in e["source"].items() if k != "source_binding_digest"},"source_binding_digest")
        self.code("SOURCE_BINDING_INVALID",lambda:self.verify(reseal(r,0)))

    def test_13_cue_source_shape(self):
        e = self.record["events"][4]
        receipt = deepcopy(e["source"]); receipt["visual"] = self.record["events"][0]["source"]["visual"]
        receipt = io.sealed({k:v for k,v in receipt.items() if k != "source_binding_digest"},"source_binding_digest")
        self.code("SOURCE_FORM_INVALID",lambda:src.restore(self.plan["events"][4],receipt,self.plan,self.config))

    def test_14_materialization_failure_terminal(self):
        class Failed(NeutralSources):
            def materialize(self,event):
                self.phase = "PCM_PAYLOAD"
                raise s.S2NSError("PCM_PAYLOAD_INVALID")
        path = run.execute_once(run_id="s2ns-neutral-failure",output_root=self.temp.name,plan=self.plan,provider_factory=Failed)
        r = json.loads(path.read_bytes())
        self.assertEqual("NOT_EVALUABLE",r["status"])
        self.assertEqual(("SOURCE","PCM_PAYLOAD",0),(r["failure"]["phase"],r["failure"]["source_phase"],r["failure"]["completed_events"]))
        self.assertFalse(self.verify(r)["evaluation_allowed"])
        root = Path(os.environ["S2NS_RUN_QUAL_DIR"])
        io.atomic_write(root/"neutral-failure.json",r,run.LIMITS["record_bytes"])

    def eval_plan(self):
        target = self.plan["events"][0]["auditory"]["source_id"]
        return io.sealed(dict(execution_digest=self.plan["execution_digest"],cases=[dict(event_id=e["event_id"],target=target,
            prediction="B_STABLE_AUDITORY",subtype="NEUTRAL") for e in self.record["events"] if e["formation"] is None]),"evaluation_digest")

    def test_15_evaluation_requires_verification(self):
        bad = io.sealed(dict(status="NOT_EVALUABLE",record_digest=self.record["record_digest"],evaluation_allowed=False),"verification_digest")
        self.code("EVALUATION_REQUIRES_VERIFICATION",lambda:evaluation.evaluate_record(self.record,bad,plan=self.plan,evaluation_plan=self.eval_plan()))

    def test_16_valid_abstention_evaluated_separately(self):
        r = evaluation.evaluate_record(self.record,self.proof,plan=self.plan,evaluation_plan=self.eval_plan())
        self.assertEqual("FUNCTION_EVALUATED",r["status"])
        self.assertTrue(all(a["area"] is None for a in self.record["events"][4]["results"][0]["admissions"]))
        self.assertTrue(r["no_netting"])
        io.atomic_write(Path(os.environ["S2NS_RUN_QUAL_DIR"])/"neutral-evaluation.json",r,run.LIMITS["record_bytes"])

    def test_17_original_variation_and_missing_reference(self):
        r = evaluation.evaluate_record(self.record,self.proof,plan=self.plan,evaluation_plan=self.eval_plan())
        self.assertTrue(all(c["receptor_variation"] is False for c in r["cases"][0]["comparisons"]))
        self.assertTrue(all(c["receptor_variation"] is True for c in r["cases"][1]["comparisons"]))
        p = self.eval_plan()
        for c in p["cases"]:
            c["target"] = "neutral-absent"
        p = io.sealed({k:v for k,v in p.items() if k != "evaluation_digest"},"evaluation_digest")
        absent = evaluation.evaluate_record(self.record,self.proof,plan=self.plan,evaluation_plan=p)
        self.assertTrue(all(c["receptor_variation"] is None for row in absent["cases"] for c in row["comparisons"]))
        self.assertTrue(all(g["public_retention"]["status"] == "ERHALTUNG_NICHT_GEPRUEFT" for g in absent["groups"]))

    def test_18_full_actual_schema_envelope(self):
        # Size-only specimen, not a claimed trajectory: every section comes from
        # actual neutral receipts, expanded to 31/16/15 and fully populated scans.
        r = deepcopy(self.record)
        form = next(e for e in reversed(r["events"]) if e["formation"] is not None)
        cue = next(e for e in reversed(r["events"]) if e["formation"] is None)
        r["events"] = [deepcopy(form) for _ in range(16)]+[deepcopy(cue) for _ in range(15)]
        for e in r["events"]:
            for result in e["results"]:
                for scan in result["scans"]:
                    for row in scan["rows"]:
                        row.update(eligible=True,terms=[2.2250738585072014e-308]*24,statistic=2.2250738585072014e-308,
                            generation_digest="f"*64,matched=True)
        self.assertEqual(17,len(r["states"]))
        measured = run.size_check(r)
        self.assertLessEqual(measured,run.MAX_ENVELOPE_BYTES)
        METRICS["worst_schema_bytes"] = measured
        root = Path(os.environ["S2NS_RUN_QUAL_DIR"])
        io.atomic_write(root/"size-witness.json",dict(kind="NON_EXECUTED_SIZE_ONLY_FULL_SCHEMA",bytes=measured,
            specimen_digest=s.digest(r),section_limits=run.SECTION_BYTES,max_envelope=run.MAX_ENVELOPE_BYTES,
            events=31,formations=16,cues=15,states=17,raw_and_nj_and_visual_sources=True),65536)
        r["events"][0]["source"]["unexpected_padding"] = "x"*16384
        self.code("SOURCE_SIZE_EXCEEDED",lambda:run.size_check(r))

    def test_19_exclusive_output_and_verification(self):
        with self.assertRaises(FileExistsError):
            run.execute_once(run_id="s2ns-neutral-chain",output_root=self.temp.name,plan=self.plan,provider_factory=NeutralSources)
        self.code("VERIFICATION_ALREADY_EXISTS",lambda:verify.verify_file_once(self.path,plan=self.plan,config=self.config))

    def test_20_gates_and_work_bounds(self):
        self.assertIs(run.MAIN_GATE,False)
        self.assertIs(s.MAIN_GATE,False)
        self.assertIs(run.b.MAIN_GATE,False)
        self.code("MAIN_GATE_CLOSED",lambda:run.run_main_once(run_id="s2ns-forbidden-main"))
        self.assertIs(run.MAIN_GATE,False)
        self.assertEqual(16,METRICS["memory_calls"])
        self.assertLessEqual(METRICS["formation_checks"],40)
        self.assertLessEqual(METRICS["execution_scans"],16)
        self.assertLessEqual(METRICS["verification_scans"],8)


if __name__ == "__main__":
    unittest.main()
