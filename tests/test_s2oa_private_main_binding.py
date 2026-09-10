"""Focused new OA connections only. All generated payloads are neutral zeros."""
from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
import numpy as np
from tools import _s2oa_private_main_binding as b
from tools import _s2oa_private_main_verification as v

r=b.r
OUT=Path(os.environ["S2OA_MAIN_QUAL_DIR"])
CONFIG=r.nn.profile.build_config()
METRICS=dict(real_oa_payloads=0,neutral_audio=0,neutral_visual=0,neutral_nj=0,runtime_instances=0,
             full_events=0,verification_calls=0,evaluation_calls=0)


def archive(name,x):r.ng.ne.atomic_write(OUT/name,x,4194304)


def neutral_bound(provenance):
    kinds=[b.source.V,b.source.AV,b.source.A,b.source.V]+[b.source.AV]*5+[b.source.V]+[b.source.AV]*5+[b.source.A,b.source.V]+[b.source.AV]*5+[b.source.V]+[b.source.AV]*4+[b.source.V]
    events=[];sources=[]
    ph=hashlib.sha256(bytearray(19200)).hexdigest()
    image=np.zeros((1080,1920,3),dtype=np.uint8)
    with memoryview(image).cast("B") as view:vh=hashlib.sha256(view).hexdigest()
    del image
    for g,kind in enumerate(kinds):
        e=dict(event_id=f"neutral-oa-{g+1:02d}",ordinal=g+1,event_type=kind,field_clock_id=r.CLOCK,
            field_window=[0 if g==0 else 200000000*g-100000000,200000000*g+100000000],auditory=None,visual=None)
        for m,absent in (("auditory",b.source.V),("visual",b.source.A)):
            if kind==absent:continue
            audio=m=="auditory";sid=f"neutral-{g+1:02d}-{m}"
            t=dict(source_id=sid,clock_id="audio.sample" if audio else "video.frame",start_tick=9600*g if audio else 6*g+2,
                end_tick=9600*g+4800 if audio else 6*g+3,
                common_window=[200000000*g if audio else (6*g+2)*1000000000//30,200000000*g+100000000])
            if audio:t["nj_snapshot_index"]=20*g
            e[m]=t
            recipe=dict(neutral=True,ordinal=99,visible_positions=list(range(32)) if kind==b.source.V else None)
            sources.append(b.sealed(dict(source_id=sid,event_id=e["event_id"],event_ordinal=g+1,kind="PCM" if audio else "RGB",
                recipe=recipe,recipe_digest=b.digest(recipe),time_binding=t,byte_count=19200 if audio else 6220800,
                payload_sha256=ph if audio else vh),"source_digest"))
        events.append(e)
    ex=b.sealed(dict(events=events,sources=sources,source_order=[s["source_id"] for s in sources],
        profiles=dict(coordinator_config_digest=CONFIG.config_digest),generators=dict(neutral=True)),"execution_digest")
    cueevents=[e for e in events if e["event_type"]!=b.source.AV]
    ev=b.sealed(dict(execution_digest=ex["execution_digest"],cases=[dict(event_id=e["event_id"],cue_id=f"q{i+1:02d}",
        modality="auditory" if e["event_type"]==b.source.A else "visual",target_visual_ordinal=99,
        prediction="B_STABLE") for i,e in enumerate(cueevents)],state_predictions=dict(fast_expiry_formations=[12,16,20],
        visual_slow_replacement_formation=18,visual_slow_replaced_slot_order=0,ppb_calls_per_modality=15,
        final_visual_supports=[3,3,3,3])),"evaluation_digest")
    p={**provenance,"execution_digest":ex["execution_digest"],"evaluation_digest":ev["evaluation_digest"]}
    return b.BoundOA(b.canonical(ex).decode(),b.canonical(p).decode()),ev


def neutral_generators():
    return lambda recipe:bytearray(19200),lambda ordinal:np.zeros((1080,1920,3),dtype=np.uint8),dict(neutral=True)


class MainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Read-only historical/administrative binding; the ongoing qualification has no result yet.
        original=b.qualification
        def qual(directory,status,count,hashes):
            if directory.name==b.QUAL_ID:
                p=OUT/"preregistration.json"
                return {"preregistration.json":dict(path=p.relative_to(b.ROOT).as_posix(),sha256=r.admin.filehash(p),bytes=p.stat().st_size)}
            return original(directory,status,count,hashes)
        with patch.object(b,"qualification",side_effect=qual):cls.historical=b.load_bound()
        cls.bound,cls.ev=neutral_bound(cls.historical.provenance())
        manifest=dict(execution_digest=cls.bound.execution()["execution_digest"],
            literal_fixture="tests/test_s2oa_private_main_binding.py:neutral_bound",
            event_types=[e["event_type"] for e in cls.bound.execution()["events"]],
            source_digests=[s["source_digest"] for s in cls.bound.execution()["sources"]])
        archive("neutral-source-manifest.json",manifest);archive("neutral-evaluation.json",cls.ev)
        extra=sum((OUT/n).stat().st_size for n in ("neutral-source-manifest.json","neutral-evaluation.json"))
        p={**cls.bound.provenance(),"source_bytes":cls.bound.provenance()["source_bytes"]+extra,
           "neutral_extra_source_bytes":extra,"neutral_manifest_digest":b.digest(manifest)}
        cls.bound=b.BoundOA(cls.bound.execution_json,b.canonical(p).decode())
        (OUT/"reports/s2oa").mkdir(parents=True,exist_ok=False)
        cls.original_read=Path.read_bytes
        def read_guard(path):
            if path.suffix==".json" and path.is_relative_to(b.ROOT/"reports") and not path.is_relative_to(OUT):
                raise AssertionError("CORPUS_READ_FORBIDDEN_DURING_FUNCTIONAL_TEST")
            return cls.original_read(path)
        cls.guard=patch.object(Path,"read_bytes",read_guard);cls.guard.start();cls.addClassCleanup(cls.guard.stop)
        original_mat=b.Materializer.run_once;original_runtime=b.OARuntime
        def mat(self):
            xs=original_mat(self);cls.inputs=xs;cls.materializer=self;return xs
        def runtime(*args,**kw):
            c=original_runtime(*args,**kw);cls.instance=c;METRICS["runtime_instances"]+=1;return c
        cls.path=cls.entry(1,mat=mat,runtime=runtime)
        cls.record=json.loads((cls.path/"record.json").read_bytes())
        if cls.record["status"]!="RECORDING_COMPLETE":
            raise AssertionError(cls.record["failure"])
        METRICS.update(neutral_audio=cls.record["counts"]["audio"],neutral_visual=cls.record["counts"]["visual"],
            neutral_nj=cls.record["counts"]["nj"],full_events=len(cls.record["execution"]["rows"]))
        with patch.object(b,"load_bound",return_value=cls.bound):cls.proof=v.verify_once(cls.path)
        METRICS["verification_calls"]+=1
        if not cls.proof["evaluation_allowed"]:raise AssertionError(cls.proof)
        cls.eval=v.evaluate(cls.record,cls.proof,cls.bound,cls.ev);METRICS["evaluation_calls"]+=1
        archive("neutral-functional-evaluation.json",cls.eval)

    @classmethod
    def entry(cls,number,*,mat=None,runtime=None,load=None):
        # Test-only filesystem root and fresh one-use gate per isolated fault fixture.
        with patch.object(b,"ROOT",OUT),patch.object(b,"_USED",False),patch.object(b,"load_bound",side_effect=load) if load else patch.object(b,"load_bound",return_value=cls.bound),patch.object(b.source,"generators",side_effect=neutral_generators):
            with patch.object(b.Materializer,"run_once",mat) if mat else patch.object(b.Materializer,"run_once",lambda self: cls.stub(self)):
                with patch.object(b,"OARuntime",side_effect=runtime) if runtime else patch.object(b,"OARuntime",wraps=b.OARuntime):
                    b.MAIN_GATE=True
                    path=b.run_main_once(f"s2oa-continuous-runtime-20260910-{number:02d}")
                    if b.MAIN_GATE:raise AssertionError("GATE_LEFT_OPEN")
                    return path

    @classmethod
    def stub(cls,self):
        self.counts=dict(b.COUNTS);return cls.inputs

    def rejects(self,code,fn):
        with self.assertRaises(r.S2OAError) as c:fn()
        self.assertEqual(c.exception.code,code)

    def test_01_full_bound_28_one_instance(self):
        core=self.record["execution"]
        self.assertEqual(self.record["counts"],b.COUNTS)
        self.assertEqual(len(core["rows"]),28);self.assertEqual(self.instance.mb.state.generation,20)
        self.assertEqual(METRICS["runtime_instances"],1)
        self.assertEqual(core["runtime_config"]["max_event_count"],28)
        self.assertEqual(self.proof["runtime_verification"]["field_contacts"],8544)
        self.assertEqual(self.proof["runtime_verification"]["scan_receipts"],16)

    def test_02_complete_real_receipt_sizes(self):
        s=self.proof["sizes"];z=s["components"]
        self.assertEqual(tuple(len(z[k]) for k in ("nj_sizes","formation_sizes","generation_sizes")),(22,20,20))
        for key,cap in (("nj_sizes",1024),("formation_sizes",1536),("generation_sizes",1536)):
            self.assertLessEqual(max(z[key]),cap)
        self.assertEqual(s["balance"]["source_bytes"],162321+self.bound.provenance()["neutral_extra_source_bytes"])
        self.assertLessEqual(s["balance"]["metadata_bytes"],65536)
        self.assertLessEqual(s["balance"]["shared_reserved_bytes"],262144)
        self.assertLessEqual(s["balance"]["total_reserved_bytes"],4194304)

    def test_03_native_receptor_nj_contact_path(self):
        self.assertEqual(self.materializer.counts,b.COUNTS)
        self.assertTrue(self.materializer.used)
        self.rejects("MATERIALIZER_ALREADY_USED",self.materializer.run_once)
        for x,e in zip(self.inputs,self.bound.execution()["events"]):
            self.assertEqual(x.event.field_payload.end_tick,e["field_window"][1])
            if e["auditory"]:
                self.assertIsNotNone(json.loads(x.nj_json)["nj"])
                af=next(f for f in x.event.field_payload.timed_frames if f.frame.modality_id=="auditory")
                self.assertTrue(af.frame.snapshot_id.startswith("half."))
                self.assertEqual(af.frame.values,(0.0,)*48)

    def test_04_exact_time_and_source_rejections(self):
        for kind,code in (("time","OA_AUDIO_TIME_INVALID"),("source","OA_SOURCE_INVALID"),("mask","OA_OCCLUSION_INVALID")):
            with self.subTest(kind=kind):
                ex=self.bound.execution();s=next(s for s in ex["sources"] if s["kind"]==("RGB" if kind=="mask" else "PCM"))
                if kind=="time":
                    s["time_binding"]["nj_snapshot_index"]+=1
                    ex["events"][s["event_ordinal"]-1]["auditory"]=deepcopy(s["time_binding"])
                elif kind=="source":s["event_id"]="foreign"
                else:s["recipe"]["visible_positions"]=None;s["recipe_digest"]=b.digest(s["recipe"])
                s.update(b.sealed({k:v for k,v in s.items() if k!="source_digest"},"source_digest"))
                ex=b.sealed({k:v for k,v in ex.items() if k!="execution_digest"},"execution_digest")
                p={**self.bound.provenance(),"execution_digest":ex["execution_digest"]}
                bad=b.BoundOA(b.canonical(ex).decode(),b.canonical(p).decode())
                self.rejects(code,lambda:b.validate_bound(bad))

    def test_05_neutral_limit_unchanged_and_oa_gate(self):
        self.rejects("INPUTS_INVALID",lambda:r.SingleRuntime(self.inputs,"neutral-too-long"))
        self.rejects("OA_GATE_CLOSED",lambda:b.OARuntime(self.inputs,"closed",bound=self.bound))
        self.assertFalse(r.MAIN_GATE);self.assertFalse(b.MAIN_GATE)

    def test_06_bad_payload_before_analysis(self):
        ex=self.bound.execution();ex["sources"][0]["payload_sha256"]="f"*64
        s=ex["sources"][0];s.update(b.sealed({k:v for k,v in s.items() if k!="source_digest"},"source_digest"))
        ex=b.sealed({k:v for k,v in ex.items() if k!="execution_digest"},"execution_digest")
        bad=b.BoundOA(b.canonical(ex).decode(),b.canonical({**self.bound.provenance(),"execution_digest":ex["execution_digest"]}).decode())
        m=b.Materializer(bad)
        with patch.object(b.source,"generators",side_effect=neutral_generators),patch.object(b.LocalChannelGridReceptor,"analyze",side_effect=AssertionError("ANALYSIS_BEFORE_HASH")):
            self.rejects("PAYLOAD_HASH_INVALID",m.run_once)
        self.assertEqual(m.phase,"PAYLOAD_HASH");self.assertEqual(m.counts["visual"],0)

    def test_07_failure_before_materialization(self):
        def fail():raise r.S2OAError("NEUTRAL_BINDING_FAULT")
        out=self.entry(2,load=fail);z=json.loads((out/"record.json").read_bytes())
        p=v.verify(z,None);archive("binding-fault-proof.json",p)
        self.assertEqual(z["failure"]["phase"],"BINDINGS");self.assertEqual(z["failure"]["completed_events"],0)
        self.assertFalse(p["evaluation_allowed"])

    def test_08_formation_error_progress_and_close(self):
        with patch.object(r.memory,"_advance_tspm_candidate",side_effect=r.S2OAError("NEUTRAL_FORMATION_FAULT")):
            out=self.entry(3)
        z=json.loads((out/"record.json").read_bytes());p=v.verify(z,self.bound);archive("formation-fault-proof.json",p)
        self.assertEqual(z["failure"]["phase"],"FORMATION");self.assertEqual(z["failure"]["ordinal"],2)
        self.assertEqual(z["execution"]["final"]["processed_event_count"],2)
        self.assertFalse(p["evaluation_allowed"])

    def test_09_cue_error_field_isolation(self):
        original=b.OARuntime
        def runtime(*a,**kw):
            c=original(*a,**kw)
            def fail(*args):raise r.S2OAError("NEUTRAL_CUE_FAULT")
            c.subject._processor._visual_scan=fail
            return c
        out=self.entry(4,runtime=runtime);z=json.loads((out/"record.json").read_bytes());p=v.verify(z,self.bound)
        archive("cue-fault-proof.json",p)
        self.assertEqual(z["failure"]["phase"],"CUE");self.assertEqual(z["failure"]["ordinal"],1)
        self.assertEqual(z["execution"]["rows"][0]["step"]["perception_status"],"FIELD_CONTACT_RECORDED")
        self.assertFalse(p["evaluation_allowed"])

    def test_10_once_publication_and_verification(self):
        with self.assertRaises(FileExistsError):v.verify_once(self.path)
        with self.assertRaises(FileExistsError):r.ng.ne.atomic_write(self.path/"record.json",{})
        self.assertEqual(r.admin.filehash(self.path/"record.json"),hashlib.sha256(b.canonical(self.record)).hexdigest())
        for key in ("memory_state_digest","field_state_digest"):
            self.assertEqual(self.record["execution"]["final"][key],self.record["execution"]["rows"][-1]["post"][key])

    def test_11_outer_source_manipulation_rejected(self):
        bad=deepcopy(self.record);bad["bindings"]["execution_digest"]="f"*64
        bad=b.sealed({k:x for k,x in bad.items() if k!="record_digest"},"record_digest")
        self.rejects("MAIN_PROVENANCE_INVALID",lambda:v.verify(bad,self.bound))

    def test_12_valid_abstention_and_wrong_inventory_evaluable(self):
        self.assertTrue(self.proof["evaluation_allowed"])
        self.assertEqual(self.eval["status"],"FALSIFIED")
        self.assertEqual(len(self.eval["cues"]),8)
        self.assertFalse(self.eval["cues"][0]["confirmed"])
        bad=deepcopy(self.proof);bad["evaluation_allowed"]=False
        bad=b.sealed({k:x for k,x in bad.items() if k!="verification_digest"},"verification_digest")
        self.rejects("EVALUATION_BLOCKED",lambda:v.evaluate(self.record,bad,self.bound,self.ev))

    def test_13_complete_budget_rejections(self):
        for which in ("metadata","item","total"):
            with self.subTest(which=which):
                bad=deepcopy(self.record)
                if which=="metadata":bad["bindings"]["metadata_bytes"]=65536
                elif which=="item":bad["execution"]["rows"][1]["formation"]["extra"]="x"*1536
                else:bad["extra"]="x"*4194304
                with self.assertRaises((r.S2OAError,r.admin.S2OAAdminError)):b.envelope_size(bad)
        parts=[162321,22528,30720,30720]
        with self.assertRaises(r.admin.S2OAAdminError) as caught:
            r.admin.shared_total_check(parts+[262145-sum(parts)])
        self.assertEqual(caught.exception.code,"SHARED_LIMIT")

    def test_14_wrong_qualification_and_closed_entry(self):
        with patch.object(Path,"read_bytes",type(self).original_read):
            hashes=b.watched();hashes["tools/_s2oa_private_runtime_binding.py"]="f"*64
            self.rejects("QUALIFIED_CODE_CHANGED",lambda:b.qualification(b.OLD_QUAL,"S2OA_RUNTIME_QUALIFIED",20,hashes))
        self.rejects("MAIN_GATE_CLOSED",lambda:b.run_main_once("s2oa-continuous-runtime-20260910-99"))
        self.assertFalse(b.MAIN_GATE)


def tearDownModule():archive("metrics.json",METRICS)


if __name__=="__main__":unittest.main()
