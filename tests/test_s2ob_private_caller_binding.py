"""One neutral qualification; caller files only, no historical corpus or replay."""
from copy import deepcopy
from dataclasses import asdict, replace, FrozenInstanceError
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import weakref
import numpy as np
from tools import _s2ob_private_caller_binding as b
from tools import _s2ob_private_caller_verification as v

OUT=Path(os.environ["S2OB_QUAL_DIR"])
CODE=os.environ["S2OB_CODE_DIGEST"]
METRICS=dict(audio=0,visual=0,nj=0,run_calls=0,verification_calls=0)
RECORDS=[]


def reseal(x):
    return b.sealed({k:z for k,z in x.items() if k!="record_digest"},"record_digest")


def make_manifest(root,kinds,name="caller-neutral-stream",offset=0):
    events=[]
    for g,kind in enumerate(kinds):
        refs={}
        for modality,needed in (("pcm",kind!=b.V),("rgb",kind!=b.A)):
            if not needed: refs[modality]=None; continue
            path=root/f"{name}-{g}-{modality}.bin"
            if modality=="pcm":
                raw=np.full(4800,0.03125+offset/1024,dtype="<f4").tobytes()
            else:
                color=20 if g<5 else 60+20*(g%8)
                frame=np.full((1080,1920,3),color+offset,dtype=np.uint8)
                if kind==b.V:
                    cells=frame.reshape(8,135,12,160,3)
                    for i in range(32,288):
                        cell,c=divmod(i,3); row,col=divmod(cell,12); cells[row,:,col,:,c]=0
                    del cells
                raw=frame.tobytes(); del frame
            path.write_bytes(raw)
            refs[modality]=b.Payload(f"caller-{g:02d}-{modality}-source",path.relative_to(b.ROOT).as_posix(),
                hashlib.sha256(raw).hexdigest(),len(raw)); del raw
        events.append(b.Event(f"caller-perception-{g+1:02d}",g+1,kind,**b.expected_times(g+1,kind),**refs))
    return b.build_manifest(name,tuple(events),CODE)


def execute(m,path,fault=None):
    METRICS["run_calls"]+=1
    original=b.CallerRuntime.process
    def process(c,item):
        def fail(*args,**kwargs): raise b.S2OBError("NEUTRAL_INJECTED_FAULT")
        if fault=="scan" and item.event.event_type==b.A:
            c.subject._processor._auditory_scan=fail
        if fault=="field": c.subject._processor._field=fail
        if fault=="memory":
            with patch.object(b.r.memory,"_advance_tspm_candidate",side_effect=fail):
                return original(c,item)
        return original(c,item)
    with patch.object(b.CallerRuntime,"process",process):
        b.MAIN_GATE=True
        b.run_once(m,path,mode="NEUTRAL")
    value=json.loads((path/"record.json").read_bytes())
    RECORDS.append(value)
    return value


def check(value,m):
    METRICS["verification_calls"]+=1
    return v.verify(value,m,tuple(tuple(z) for z in value["references"]))


class CallerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix="s2ob-neutral-",dir=b.ROOT/"reports/s2ob")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.payloads=Path(cls.temp.name)
        original=Path.read_bytes
        def guarded(path):
            if path.suffix==".json" and path.resolve().is_relative_to(b.ROOT/"reports") and not path.resolve().is_relative_to(OUT):
                raise AssertionError("HISTORICAL_CORPUS_READ_FORBIDDEN")
            return original(path)
        guard=patch.object(Path,"read_bytes",guarded);guard.start();cls.addClassCleanup(guard.stop)
        cls.audio_views=[]; cls.visual_views=[]
        audio=b.r.half.spectral.LogSpectralReceptor.analyze
        visual=b.LocalChannelGridReceptor.analyze
        nj=b.r.half.project_auditory_half_v1
        def audio_observer(self,samples):
            assert all(x() is None for x in cls.audio_views),"PREVIOUS_PCM_STILL_RETAINED"
            cls.audio_views.append(weakref.ref(samples)); METRICS["audio"]+=1
            return audio(self,samples)
        def visual_observer(self,frame,**kw):
            assert all(x() is None for x in cls.visual_views),"PREVIOUS_RGB_STILL_RETAINED"
            cls.visual_views.append(weakref.ref(frame)); METRICS["visual"]+=1
            return visual(self,frame,**kw)
        def nj_observer(*args,**kw):
            METRICS["nj"]+=1; return nj(*args,**kw)
        for target,name,fn in ((b.r.half.spectral.LogSpectralReceptor,"analyze",audio_observer),
                              (b.LocalChannelGridReceptor,"analyze",visual_observer),
                              (b.r.half,"project_auditory_half_v1",nj_observer)):
            p=patch.object(target,name,fn);p.start();cls.addClassCleanup(p.stop)
        cls.manifest=make_manifest(cls.payloads,[b.V,b.AV,b.AV,b.A]+[b.AV]*8+[b.V])
        cls.record=execute(cls.manifest,OUT/"neutral-complete")
        cls.proof=check(cls.record,cls.manifest)
        b.r.ng.ne.atomic_write(OUT/"neutral-complete"/"verification.json",cls.proof,262144)

    def reject(self,code,fn):
        with self.assertRaises(b.S2OBError) as caught: fn()
        self.assertEqual(caught.exception.code,code)

    def test_01_short_stream_and_real_counters(self):
        self.assertEqual(self.record["status"],"RECORDING_COMPLETE")
        self.assertEqual(self.record["counts"],dict(audio=11,nj=11,visual=12,payloads=23,materialized_events=13))
        self.assertEqual(self.proof["core"]["field_contacts"],3984)

    def test_02_manifest_immutable_and_caller_ids(self):
        with self.assertRaises(FrozenInstanceError): self.manifest.events=()
        self.assertTrue(all(e.event_id.startswith("caller-perception-") for e in self.manifest.events))
        self.assertEqual(b.decode_manifest(json.loads(b.canonical(asdict(self.manifest)))),self.manifest)

    def test_03_wrong_times_and_native_indices(self):
        e=self.manifest.events[1]
        for changes in (dict(audio_index=1),dict(audio_window=(9601,14401)),dict(visual_window=(8,10)),dict(field_window=(0,300000000))):
            with self.subTest(changes=changes):
                rows=list(self.manifest.events);rows[1]=replace(e,**changes)
                self.reject("TIME_INVALID",lambda:b.build_manifest("caller-invalid-time",tuple(rows),CODE))

    def test_04_profiles_and_execution_roles_rejected(self):
        bad=asdict(self.manifest);bad["profile_digest"]="f"*64
        bad=b.sealed({k:z for k,z in bad.items() if k!="manifest_digest"},"manifest_digest")
        self.reject("PROFILE_INVALID",lambda:b.decode_manifest(bad))
        bad=asdict(self.manifest);bad["expected_target"]="target"
        self.reject("MANIFEST_INVALID",lambda:b.decode_manifest(bad))

    def test_05_duplicate_and_short_ids(self):
        for value,code in (("e01","ID_INVALID"),(self.manifest.events[0].event_id,"ID_DUPLICATE")):
            with self.subTest(value=value):
                xs=list(self.manifest.events);xs[1]=replace(xs[1],event_id=value)
                self.reject(code,lambda:b.build_manifest("caller-invalid-id",tuple(xs),CODE))

    def test_06_source_hash_before_analysis(self):
        p=self.manifest.events[1].pcm
        with patch.object(b.r.half.spectral.LogSpectralReceptor,"analyze",side_effect=AssertionError("ANALYSIS_FORBIDDEN")):
            self.reject("PAYLOAD_HASH_INVALID",lambda:b.read_payload(replace(p,sha256="f"*64)))

    def test_07_changed_payload_and_phased_close(self):
        m=make_manifest(self.payloads,[b.AV],"caller-corrupted-payload",offset=1)
        p=m.events[0].pcm;path=b.payload_path(p)
        raw=bytearray(path.read_bytes());raw[0]^=1;path.write_bytes(raw);del raw
        z=execute(m,OUT/"neutral-payload-error")
        self.assertEqual(z["status"],"NOT_EVALUABLE")
        self.assertEqual(z["failure"]["code"],"PAYLOAD_HASH_INVALID")
        self.assertEqual(z["failure"]["phase"],"PAYLOAD_HASH")
        self.assertEqual(z["failure"]["completed_events"],0)
        self.assertEqual(z["failure"]["final"]["status"],"CLOSED")
        self.assertFalse(check(z,m)["evaluation_allowed"])

    def test_08_raw_payloads_released_and_never_recorded(self):
        self.assertTrue(all(x() is None for x in self.audio_views+self.visual_views))
        self.assertFalse(any(p.suffix==".bin" for p in OUT.rglob("*")))
        self.assertNotIn("payload_bytes",b.canonical(self.record).decode())

    def test_09_nj_once_common_field_memory_projection(self):
        x=self.record["execution"]
        for p,s in zip(x["inputs"],x["source_receipts"]):
            for f in p["field"]["timed_frames"]:
                if f["frame"]["modality_id"]=="auditory":
                    self.assertEqual(f["frame"]["snapshot_id"],"half."+s["nj"]["projection_digest"])
                    self.assertTrue(all(0<=z<=1 for z in f["frame"]["values"]))
        self.assertEqual(self.record["counts"]["nj"],self.record["counts"]["audio"])

    def test_10_read_only_hints_and_valid_abstention(self):
        x=self.record["execution"]
        for row,event in zip(x["rows"],self.manifest.events):
            if event.kind!=b.AV:
                self.assertEqual(row["pre"]["memory_state_digest"],row["memory"])
                self.assertIsNone(row["formation"])
        self.assertEqual(x["rows"][0]["step"]["context_status"],"ABSTAIN_NO_CONTEXT")
        self.assertTrue(self.proof["evaluation_allowed"])

    def test_11_same_runtime_no_reset_close(self):
        x=self.record["execution"]
        self.assertEqual(x["final"]["status"],"CLOSED")
        self.assertEqual(x["final"]["processed_event_count"],13)
        for a,z in zip(x["rows"],x["rows"][1:]): self.assertEqual(a["post"],z["pre"])
        for key in ("memory_state_digest","field_state_digest","stream_state_digest"):
            self.assertEqual(x["final"][key],x["rows"][-1]["post"][key])

    def test_12_actual_generations_match_and_replacement(self):
        x=self.record["execution"];prior=[None]*24;matched=replaced=0
        for row in x["rows"]:
            g=row["generations"]
            if g is None:continue
            for i,action in enumerate(g["actions"]):
                if action=="MATCHED":matched+=1;self.assertEqual(prior[i],g["births"][i])
                if action=="REPLACED":replaced+=1;self.assertNotEqual(prior[i],g["births"][i])
                if action in ("FREE","CLEARED"):self.assertIsNone(g["births"][i])
            prior=g["births"]
        self.assertGreater(matched,0);self.assertGreater(replaced,0)

    def test_13_generations_manipulation(self):
        z=deepcopy(self.record);x=z["execution"];x["rows"][1]["current_births"][0]=999
        z["execution"]=reseal(x);z=reseal(z)
        self.reject("CURRENT_GENERATION_INVALID",lambda:check(z,self.manifest))

    def test_14_complete_scans_and_independent_baseline(self):
        self.assertEqual(self.proof["core"]["scan_receipts"],6)
        self.assertTrue(self.proof["core"]["baseline_equal"])
        z=deepcopy(self.record);z["execution"]["scans"].pop()
        z["execution"]=reseal(z["execution"]);z=reseal(z)
        self.reject("SCAN_MISSING",lambda:check(z,self.manifest))

    def test_15_memory_failure_keeps_field(self):
        m=make_manifest(self.payloads,[b.AV],"caller-memory-error",offset=2)
        z=execute(m,OUT/"neutral-memory-error","memory")
        self.assertEqual(z["status"],"NOT_EVALUABLE")
        x=z["execution"]
        self.assertEqual(x["initial"]["memory"],x["final"]["memory_state_digest"])
        self.assertEqual(x["rows"][0]["step"]["perception_status"],"FIELD_CONTACT_RECORDED")
        self.assertFalse(check(z,m)["evaluation_allowed"])

    def test_16_field_failure_keeps_memory(self):
        m=make_manifest(self.payloads,[b.AV],"caller-field-error",offset=3)
        z=execute(m,OUT/"neutral-field-error","field")
        self.assertEqual(z["status"],"NOT_EVALUABLE")
        self.assertEqual(z["execution"]["rows"][0]["step"]["memory_status"],"FORMATION_COMMITTED")
        self.assertFalse(check(z,m)["evaluation_allowed"])

    def test_17_scan_failure_keeps_field_and_memory(self):
        m=make_manifest(self.payloads,[b.AV,b.A],"caller-scan-error",offset=4)
        z=execute(m,OUT/"neutral-scan-error","scan")
        x=z["execution"];self.assertEqual(x["rows"][1]["field"]["step_count"],2)
        self.assertEqual(x["rows"][0]["memory"],x["rows"][1]["memory"])
        self.assertFalse(check(z,m)["evaluation_allowed"])

    def test_18_item_budget_and_full_balance(self):
        z=deepcopy(self.record);z["execution"]["rows"][1]["formation"]["extra"]="x"*1536
        self.reject("ITEM_LIMIT",lambda:b.core_sizes(z["execution"]))
        measured=self.proof["sizes"]
        self.assertFalse(measured["violations"])
        self.assertGreater(measured["totals"]["shared"],0)

    def test_19_isolated_metadata_source_global_budgets(self):
        shell=dict(execution=None)
        for refs,code in ((("metadata","neutral-extra",65536),"METADATA_LIMIT"),
                          (("sources","neutral-extra",174081),"SOURCES_LIMIT")):
            with self.subTest(code=code):
                q=b.balance(shell,(refs,));self.assertIn(code,q["violations"])
                self.reject("ENVELOPE_LIMIT",lambda:b.enforce(q))
        # Separate sum-entry control, not a claim that all local maxima co-occur.
        q=b.balance(shell,(),proof_bytes=4335858)
        self.assertIn("TOTAL_LIMIT",q["violations"])
        self.assertIn("VERIFICATION_LIMIT",q["violations"])

    def test_20_reference_and_state_tampering(self):
        self.reject("REFERENCES_INVALID",lambda:v.verify(self.record,self.manifest,()))
        z=deepcopy(self.record);x=z["execution"];h=next(iter(x["states"]))
        x["states"][h]["generation"]=1;z["execution"]=reseal(x);z=reseal(z)
        self.reject("STATE_BINDING_INVALID",lambda:check(z,self.manifest))

    def test_21_gate_output_conflict_and_no_overwrite(self):
        self.reject("MAIN_GATE_CLOSED",lambda:b.run_once(self.manifest,OUT/"forbidden"))
        raw=(OUT/"neutral-complete"/"record.json").read_bytes()
        b.MAIN_GATE=True
        self.reject("OUTPUT_EXISTS_OR_PARENT_MISSING",lambda:b.run_once(self.manifest,OUT/"neutral-complete",mode="NEUTRAL"))
        self.assertFalse(b.MAIN_GATE)
        self.assertEqual(raw,(OUT/"neutral-complete"/"record.json").read_bytes())

    def test_22_source_form_and_preanalysis_occlusion(self):
        p=self.manifest.events[0].rgb
        self.reject("PAYLOAD_BINDING_INVALID",lambda:b.payload_path(replace(p,sha256="invalid")))
        z=asdict(self.manifest);z["events"][0]["pcm"]=asdict(self.manifest.events[1].pcm)
        z=b.sealed({k:x for k,x in z.items() if k!="manifest_digest"},"manifest_digest")
        self.reject("MODALITY_INVALID",lambda:b.decode_manifest(z))

    def test_23_limits_no_padding_and_duplicate_source(self):
        self.reject("MANIFEST_INVALID",lambda:b.build_manifest("caller-empty-stream",(),CODE))
        e=self.manifest.events[1];xs=list(self.manifest.events);xs[2]=replace(xs[2],pcm=e.pcm)
        self.reject("SOURCE_BINDING_INVALID",lambda:b.build_manifest("caller-duplicate-source",tuple(xs),CODE))
        kinds=[b.A]*3
        rows=tuple(b.Event(f"caller-extra-{i:02d}",i+1,b.A,**b.expected_times(i+1,b.A),
            pcm=replace(e.pcm,source_id=f"caller-extra-source-{i:02d}"),rgb=None) for i in range(3))
        self.reject("EVENT_LIMIT",lambda:b.build_manifest("caller-too-many-audio",rows,CODE))

    def test_24_wrong_sources_and_no_receptor_in_verification(self):
        z=deepcopy(self.record);z["execution"]["source_receipts"][1]["nj"]["pcm_digest"]="f"*64
        z["execution"]=reseal(z["execution"]);z=reseal(z)
        self.reject("SOURCE_BINDING_INVALID",lambda:check(z,self.manifest))
        with patch.object(b,"read_payload",side_effect=AssertionError("PAYLOAD_REPLAY_FORBIDDEN")), \
             patch.object(b.r.half.spectral.LogSpectralReceptor,"analyze",side_effect=AssertionError("FFT_REPLAY_FORBIDDEN")), \
             patch.object(b.r.memory,"advance_s2jv_atomic",side_effect=AssertionError("MEMORY_REPLAY_FORBIDDEN")):
            p=check(self.record,self.manifest)
        self.assertEqual(p,self.proof)


def tearDownModule():
    b.r.ng.ne.atomic_write(OUT/"metrics.json",dict(**METRICS,main_gate=b.MAIN_GATE,records=len(RECORDS)),65536)


if __name__=="__main__":unittest.main()
