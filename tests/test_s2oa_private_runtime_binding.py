"""One neutral OA qualification. No OA sources, payloads, FFT or main story."""
from copy import deepcopy
from dataclasses import asdict
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
from tools import _s2oa_private_runtime_binding as r
from tools import _s2oa_private_runtime_verification as v

OUT=Path(os.environ["S2OA_RUNTIME_QUAL_DIR"])
CONFIG=r.nn.profile.build_config()
AV,A,V="COMPLETE_AV_PERCEPTION","PARTIAL_AUDITORY_CUE","PARTIAL_VISUAL_CUE"
METRICS=dict(nj=0,events=0,formation_attempts=0,main_calls=0,receptor_calls=0)


def archive(name,value):
    r.ng.ne.atomic_write(OUT/name,value)


def inputs(rows):
    result=[]
    for g,(kind,value) in enumerate(rows):
        raw=visual=None
        if kind!=V:
            raw=r.half.AuditoryReceptorState("auditory",r.half.RAW_GEOMETRY,20*g,9600*g,9600*g+4800,
                tuple(b.channel_id for b in r.half.spectral.logarithmic_bands(r.nn.LogSpectralConfig())),
                (0.5,)*48,r.half.AuditoryReceptorContact.ACTIVE_ENERGY)
        if kind!=A:
            p=CONFIG.profile.profile.visual_config
            vals=(value,)*288 if kind==AV else (value,)*32+(0.0,)*256
            f=r.nn.ReceptorContactFrame("visual",p.geometry_id,f"oa-neutral-frame-{g}","video.frame",6*g+2,6*g+3,p.carrier_ids,vals)
            visual=r.nn.OrganismTimedReceptorFrame(f,r.nn.CommonFieldTime(r.CLOCK,(6*g+2)*1000000000//30,200000000*g+100000000))
        bound=r.bind_input(config=CONFIG,ordinal=g+1,event_id=f"s2oa-neutral-event-{g+1:02d}",kind=kind,
            raw_audio=raw,visual=visual,pcm_digest=None if raw is None else r.digest(dict(neutral_audio=g)),
            rgb_digest=None if visual is None else r.digest(dict(neutral_visual=g)))
        METRICS["nj"]+=int(raw is not None)
        result.append(bound)
    return tuple(result)


def run_case(rows,name,fault=None):
    xs=inputs(rows);c=r.SingleRuntime(xs,name)
    try:
        for i in range(len(xs)):
            if fault=="scan" and i==1:
                def fail(*args):raise r.S2OAError("NEUTRAL_SCAN_FAULT")
                c.subject._processor._auditory_scan=fail
            if fault=="field":
                def fail(*args):raise r.S2OAError("NEUTRAL_FIELD_FAULT")
                c.subject._processor._field=fail
            if fault=="memory":
                with patch.object(r.memory,"_advance_tspm_candidate",side_effect=r.S2OAError("NEUTRAL_POST_B4_FAULT")):
                    c.process_next()
            else:c.process_next()
            METRICS["events"]+=1
            METRICS["formation_attempts"]+=int(xs[i].event.event_type==AV)
            if c.failed:break
        record=c.finish()
        archive(name+".json",record)
        proof=v.verify(record,CONFIG)
        archive(name+"-proof.json",proof)
        return c,record,proof,xs
    finally:
        if c.subject.snapshot().status=="OPEN":c.subject.close()


def tearDownModule():
    archive("metrics.json",METRICS)


class RuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        original=Path.read_bytes
        def guarded(path):
            if path.suffix==".json" and path.resolve().is_relative_to(r.admin.ROOT/"reports") and not path.resolve().is_relative_to(OUT.resolve()):
                raise AssertionError("REAL_SOURCE_DATA_FORBIDDEN")
            return original(path)
        cls.guard=patch.object(Path,"read_bytes",guarded);cls.guard.start();cls.addClassCleanup(cls.guard.stop)
        cls.fft=patch.object(r.half.spectral.LogSpectralReceptor,"analyze",side_effect=AssertionError("RECEPTOR_FORBIDDEN"))
        cls.fft.start();cls.addClassCleanup(cls.fft.stop)
        rows=[(V,0.0),(AV,0.0),(V,0.0)]+[(AV,0.0)]*3+[(A,0.0)]+[(AV,0.25)]*4+[(AV,0.5)]*4+[(AV,0.75),(V,0.0),(AV,0.75)]+[(AV,1.0)]*2+[(V,0.0)]
        cls.c,cls.record,cls.proof,cls.inputs=run_case(rows,"s2oa-neutral-continuous")
        cls.memory_failure=run_case([(AV,0.5)],"s2oa-neutral-atomic-fault","memory")
        cls.field_failure=run_case([(AV,0.5)],"s2oa-neutral-field-fault","field")
        cls.scan_failure=run_case([(AV,0.5),(A,0.0)],"s2oa-neutral-scan-fault","scan")

    def rejects(self,code,call):
        with self.assertRaises(r.S2OAError) as caught:call()
        self.assertEqual(caught.exception.code,code)

    def test_01_complete_single_history(self):
        self.assertEqual(self.record["status"],"RECORDING_COMPLETE")
        self.assertEqual(len(self.record["rows"]),21)
        self.assertEqual(self.c.mb.state.generation,16)

    def test_02_lifecycle_no_reset(self):
        self.assertEqual(self.c.subject.snapshot().status,"CLOSED")
        for a,b in zip(self.record["rows"],self.record["rows"][1:]):self.assertEqual(a["post"],b["pre"])
        for key in ("memory_state_digest","field_state_digest","stream_state_digest"):
            self.assertEqual(self.record["final"][key],self.record["rows"][-1]["post"][key])
        with self.assertRaises(r.ng.runtime.S2MRRuntimeError):self.c.subject.close()

    def test_03_native_and_field_time(self):
        for g,x in enumerate(self.inputs):
            e=x.event
            self.assertEqual(e.field_payload.start_tick,0 if g==0 else 200000000*g-100000000)
            for f in e.field_payload.timed_frames:
                self.assertEqual(f.field_time.clock_id,r.CLOCK)
                self.assertEqual(f.field_time.window_end_tick,200000000*g+100000000)
            if e.event_type==AV:
                a,z=e.field_payload.timed_frames
                self.assertLess(a.field_time.window_start_tick,z.field_time.window_start_tick)
                self.assertEqual(e.operation_payload.plan.overlap_start_tick,z.field_time.window_start_tick)

    def test_04_nj_and_common_projection(self):
        for x in self.inputs:
            if x.event.event_type==AV:
                op=x.event.operation_payload
                self.assertEqual(op.auditory.timed_frame,x.event.field_payload.timed_frames[0])
                self.assertEqual(op.auditory.timed_frame.frame.values,(0.25,)*48)
        self.assertEqual(METRICS["nj"],21)

    def test_05_read_only_and_abstention(self):
        for p,e in zip(self.record["rows"],self.inputs):
            if e.event.event_type!=AV:
                self.assertEqual(p["pre"]["memory_state_digest"],p["memory"])
                self.assertIsNone(p["formation"])
        self.assertEqual(self.record["rows"][0]["step"]["context_status"],"ABSTAIN_NO_CONTEXT")

    def test_06_complete_independent_scans(self):
        self.assertTrue(self.proof["baseline_equal"])
        self.assertEqual(self.proof["scan_receipts"],10)
        self.assertEqual(self.proof["field_contacts"],16*336+4*288+48)

    def test_07_matched_retains_generation(self):
        matches=0
        previous=[None]*24
        for row in self.record["rows"]:
            gen=row["generations"]
            if gen:
                for i,action in enumerate(gen["actions"]):
                    if action=="MATCHED":
                        matches+=1;self.assertEqual(previous[i],gen["births"][i])
                previous=gen["births"]
        self.assertGreater(matches,0)

    def test_08_visual_replaced_generation(self):
        changed=[(i,x) for i,x in enumerate(self.record["rows"]) if x["generations"] and "REPLACED" in x["generations"]["actions"][20:]]
        self.assertEqual(len(changed),1)
        i,row=changed[0]
        slot=next(j for j in range(20,24) if row["generations"]["actions"][j]=="REPLACED")
        self.assertNotEqual(r.generation_identity(self.record,i-1,slot),r.generation_identity(self.record,i,slot))

    def test_09_fast_cleared_has_no_generation(self):
        found=0
        for row in self.record["rows"]:
            if row["generations"]:
                for i in range(9,12):
                    if row["generations"]["actions"][i]=="CLEARED":
                        found+=1;self.assertIsNone(row["current_births"][i])
        self.assertGreater(found,0)

    def test_10_historical_vs_current_evidence(self):
        early=self.record["rows"][16]
        self.assertEqual(early["step"]["context_status"],"CONTEXT_CANDIDATE_AVAILABLE")
        self.assertFalse(r.current_evidence(self.record,16,20,20))
        self.assertTrue(r.current_evidence(self.record,16,16,20))
        self.assertIsNone(self.record["rows"][20]["step"]["hypothesis"])

    def test_11_generation_manipulation(self):
        bad=deepcopy(self.record)
        bad["rows"][1]["current_births"][0]=999
        bad=r.sealed({k:z for k,z in bad.items() if k!="record_digest"},"record_digest")
        self.rejects("CURRENT_GENERATION_INVALID",lambda:v.verify(bad,CONFIG))

    def test_12_state_manipulation(self):
        bad=deepcopy(self.record);key=next(iter(bad["states"]))
        bad["states"][key]["generation"]=1
        bad=r.sealed({k:z for k,z in bad.items() if k!="record_digest"},"record_digest")
        self.rejects("STATE_BINDING_INVALID",lambda:v.verify(bad,CONFIG))

    def test_13_source_and_clock_manipulation(self):
        bad=json.loads(self.inputs[1].nj_json);bad["nj"]["projection_digest"]="f"*64
        with self.assertRaises(r.half.S2NJProjectionError):v.source_receipt(bad,self.inputs[1].event,CONFIG)
        bad=json.loads(self.inputs[0].nj_json);bad["rgb_digest"]="f"*64
        self.rejects("RGB_BINDING_INVALID",lambda:v.source_receipt(bad,self.inputs[0].event,CONFIG))

    def test_14_actual_auxiliary_receipt_sizes(self):
        sizes=self.proof["sizes"]
        self.assertEqual(len(sizes["nj_sizes"]),17)
        self.assertEqual(len(sizes["formation_sizes"]),16)
        self.assertEqual(len(sizes["generation_sizes"]),16)
        self.assertLessEqual(max(sizes["nj_sizes"]),1024)
        self.assertLessEqual(max(sizes["formation_sizes"]),1536)
        self.assertLessEqual(max(sizes["generation_sizes"]),1536)

    def test_15_complete_envelope(self):
        self.assertLessEqual(self.proof["sizes"]["ledger"]["total_reserved_bytes"],4194304)
        self.assertLessEqual(self.proof["sizes"]["ledger"]["metadata_bytes"],65536)
        bad=deepcopy(self.record);bad["rows"][1]["formation"]["extra"]="x"*1536
        with self.assertRaises(r.admin.S2OAAdminError) as caught:r.size_check(bad)
        self.assertEqual(caught.exception.code,"RESERVE_ITEM_LIMIT")

    def test_16_atomic_failure_after_b4_candidate(self):
        c,z,p,_=self.memory_failure
        self.assertEqual(z["status"],"NOT_EVALUABLE")
        self.assertEqual(c.mb.state.generation,0)
        self.assertEqual(z["initial"]["memory"],z["final"]["memory_state_digest"])
        self.assertEqual(z["rows"][0]["step"]["perception_status"],"FIELD_CONTACT_RECORDED")
        self.assertFalse(p["evaluation_allowed"])

    def test_17_field_failure_keeps_memory_independent(self):
        c,z,p,_=self.field_failure
        self.assertEqual(c.mb.state.generation,1)
        self.assertEqual(z["rows"][0]["step"]["memory_status"],"FORMATION_COMMITTED")
        self.assertEqual(z["initial"]["field"]["state_digest"],z["final"]["field_state_digest"])
        self.assertFalse(p["evaluation_allowed"])

    def test_18_scan_failure_field_continues(self):
        c,z,p,_=self.scan_failure
        self.assertEqual(z["rows"][1]["step"]["context_status"],"SCAN_FAILED")
        self.assertEqual(z["rows"][1]["field"]["step_count"],2)
        self.assertEqual(z["rows"][0]["memory"],z["rows"][1]["memory"])
        self.assertFalse(p["evaluation_allowed"])

    def test_19_phased_failure(self):
        bad=r.execute((),"s2oa-neutral-binding-failure")
        self.assertEqual(bad["failure"]["phase"],"BINDINGS")
        self.assertEqual(bad["failure"]["completed_events"],0)
        self.assertFalse(v.verify(bad,CONFIG)["evaluation_allowed"])
        archive("neutral-binding-failure.json",bad)

    def test_20_main_closed_and_foreign_order(self):
        self.rejects("MAIN_GATE_CLOSED",lambda:r.SingleRuntime(self.inputs,"s2oa-forbidden",mode="MAIN"))
        self.rejects("EVENT_ORDER_INVALID",lambda:r.SingleRuntime(tuple(reversed(self.inputs)),"s2oa-reversed"))
        self.assertFalse(r.MAIN_GATE)
        self.assertFalse(r.ng.MAIN_GATE)
        self.assertEqual(METRICS["events"],25)
        self.assertEqual(METRICS["formation_attempts"],19)


if __name__=="__main__":unittest.main()
