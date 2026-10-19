"""Focused single qualification; synthetic receptor endpoints, no media files."""
from dataclasses import asdict, replace
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
from tools import _experience_comparison as c
from tools import _experience_verification as v
from tools import _experience_entry as entry

b,r,p = c.b,c.r,c.p
OUT = Path(os.environ["EXPERIENCE_QUAL_OUT"])


def manifest():
    return p.build("experience-neutral-20260919-01",p.Source("neutral-no-payload","0"*64,1),"1"*64)


class Supplier:
    def __init__(self, fail=None):
        self.fail, self.calls = fail, []

    def next(self,e):
        if e.ordinal==self.fail:
            raise c.ComparisonError("NEUTRAL_MATERIALIZATION_ERROR")
        self.calls.append(e.ordinal)
        config = r.nn.profile.build_config()
        nn = r.nn
        times = b.expected_times(e.ordinal,e.kind)
        raw = visual = None
        if e.kind!=b.V:
            from mcm_field_organism.broadband_hearing_path import AuditoryReceptorContact
            raw = r.half.AuditoryReceptorState("auditory",r.half.RAW_GEOMETRY,times["audio_index"],
                *times["audio_window"],tuple(z.channel_id for z in r.half.spectral.logarithmic_bands(nn.LogSpectralConfig())),
                (0.25,)*48,AuditoryReceptorContact.ACTIVE_ENERGY)
        if e.kind!=b.A:
            vp = config.profile.profile.visual_config
            values = tuple(0.125 if e.kind==b.AV or i<32 else 0.0 for i in range(288))
            visual = nn.OrganismTimedReceptorFrame(nn.ReceptorContactFrame("visual",vp.geometry_id,
                "neutral-frame-"+str(e.ordinal),"video.frame",*times["visual_window"],vp.carrier_ids,values),
                nn.CommonFieldTime(b.CLOCK,*times["visual_common"]))
        return b.bind_input(config=config,ordinal=e.ordinal,event_id=e.event_id,kind=e.kind,
            raw_audio=raw,visual=visual,pcm_digest="2"*64 if raw is not None else None,
            rgb_digest="3"*64 if visual is not None else None)


class Qualification(unittest.TestCase):
    def reject(self,code,fn):
        with self.assertRaises(c.ComparisonError) as caught:
            fn()
        self.assertEqual(code,caught.exception.code)

    def test_01_profile_and_old_limits(self):
        self.assertEqual(c.PROFILE,"EXPERIENCE_COMPARISON_24M_V1")
        self.assertEqual(b.LIMITS["total"],4194304)
        self.assertEqual(c.LIMITS["total"],25165824)

    def test_02_joint_budget_equality_and_overflow(self):
        self.assertEqual(c.budget([dict(path="native",kind="native",bytes=c.LIMITS["total"])])["violations"],[])
        self.reject("JOINT_BUDGET_LIMIT",lambda:c.budget([dict(path="native",kind="native",bytes=c.LIMITS["total"]+1)]))

    def test_03_each_class_limit(self):
        for kind in ("metadata","sources","verification"):
            with self.subTest(kind=kind):
                self.reject("JOINT_BUDGET_LIMIT",lambda:c.budget([dict(path=kind,kind=kind,bytes=c.LIMITS[kind]+1)]))

    def test_04_shared_and_duplicate_paths(self):
        self.reject("JOINT_BUDGET_LIMIT",lambda:c.budget([dict(path="a",kind="formations",bytes=c.LIMITS["shared"]+1)]))
        self.reject("LEDGER_FORM",lambda:c.budget([dict(path="same",kind="native",bytes=0)]*2))

    def test_05_exact_sequences_and_counts(self):
        m=manifest()
        a,z=c.arm_manifest(m,"experienced"),c.arm_manifest(m,"fresh")
        self.assertEqual((len(a.events),len(z.events)),(24,14))
        self.assertEqual(sum(p.counts(x.events)["contacts"] for x in (a,z)),11424)
        self.assertEqual(z.positions,tuple(range(11,25)))
        self.assertEqual([e.kind for e in z.events if e.window_number==2],[b.A,b.V,b.AV])

    def test_06_manifest_immutability(self):
        a=c.arm_manifest(manifest(),"fresh")
        with self.assertRaises(AttributeError):
            a.positions=(1,)
        self.reject("ARM_INVALID",lambda:c.arm_manifest(manifest(),"other"))

    def test_07_same_input_distinct_local_ordinal(self):
        m=manifest(); item=Supplier().next(m.events[10])
        fresh=c.arm_manifest(m,"fresh")
        adapted=c.local_input(item,fresh.events[0],11)
        self.assertEqual(adapted.event.ordinal,1)
        self.assertEqual(adapted.event.field_payload.start_tick,0)
        self.assertEqual(adapted.event.field_payload.timed_frames,item.event.field_payload.timed_frames)
        self.assertEqual(adapted.event.operation_payload,item.event.operation_payload)
        self.assertEqual(item.event.ordinal,11)

    def test_08_position_error(self):
        m=manifest(); item=Supplier().next(m.events[10])
        self.reject("INPUT_POSITION_INVALID",lambda:c.local_input(item,c.arm_manifest(m,"fresh").events[0],12))

    def test_09_time_sequence(self):
        a=c.arm_manifest(manifest(),"fresh")
        times=[b.expected_times(g,e.kind) for g,e in zip(a.positions,a.events)]
        self.assertEqual(times[0]["audio_index"],200)
        self.assertEqual(times[-1]["field_window"][1],4700000000)
        self.assertTrue(all(x["field_window"][1]==y["field_window"][0] for x,y in zip(times,times[1:])))

    def test_10_origin_classes(self):
        self.assertEqual(c.origin_class(None,2),"UNDETERMINED")
        self.assertEqual(c.origin_class([dict(window=2)],2),"TARGET_ONLY")
        self.assertEqual(c.origin_class([dict(window=2),dict(window=3)],2),"MIXED")
        self.assertEqual(c.origin_class([dict(window=3)],2),"OTHER")

    def test_11_update_and_replacement_provenance(self):
        m=c.arm_manifest(manifest(),"experienced")
        events=m.events[:3]
        rows=[]
        for action in ("CREATED","MATCHED","REPLACED"):
            rows.append(dict(generations=dict(actions=[action]+["FREE"]*23,transaction="4"*64)))
        core=dict(rows=rows)
        result=c.provenance(core,replace(m,events=events))
        self.assertEqual([len(x[0]) for x in result],[1,2,1])
        self.assertEqual(result[2][0][0]["event"],3)
        self.assertEqual(len(result[0][0]),1)

    def test_12_evaluation_gate(self):
        self.reject("EVALUATION_NOT_ALLOWED",lambda:c.evaluate(dict(record_digest="a"),dict(evaluation_allowed=False)))

    def test_13_native_isolation_close(self):
        m=manifest(); a=c.Arm(c.arm_manifest(m,"experienced")); z=c.Arm(c.arm_manifest(m,"fresh"))
        try:
            self.assertIsNot(a.subject,z.subject);self.assertIsNot(a.fb,z.fb);self.assertIsNot(a.mb,z.mb)
            self.assertEqual(a.mb.state.state_digest,z.mb.state.state_digest)
            before=(a.mb.state.state_digest,a.fb.state.state_digest)
            a.close();a.close()
            self.assertEqual(before,(a.mb.state.state_digest,a.fb.state.state_digest))
        finally:
            a.close();z.close()

    def test_14_materialization_failure_preserves_progress(self):
        supplier=Supplier(fail=2)
        record=c.run_materialized(manifest(),supplier)
        self.assertEqual(record["status"],"NOT_EVALUABLE")
        self.assertEqual(record["failure"]["code"],"NEUTRAL_MATERIALIZATION_ERROR")
        self.assertEqual(record["failure"]["progress"],{"experienced":1})
        self.assertEqual(record["arms"]["experienced"]["final"]["status"],"CLOSED")

    def test_15_complete_native_comparison(self):
        supplier=Supplier()
        record=c.run_materialized(manifest(),supplier)
        (OUT/"native-record.json").write_bytes(b.canonical(record))
        self.assertEqual(record["status"],"RECORDING_COMPLETE",record.get("failure"))
        self.assertEqual(supplier.calls,list(range(1,25)))
        record=json.loads((OUT/"native-record.json").read_bytes())
        proof=v.verify(record)
        (OUT/"native-verification.json").write_bytes(b.canonical(proof))
        self.assertTrue(proof["evaluation_allowed"])
        evaluation=c.evaluate(record,proof)
        (OUT/"native-evaluation.json").write_bytes(b.canonical(evaluation))
        self.assertEqual(len(evaluation["rows"]),4)
        for core in record["arms"].values():
            for row in core["rows"]:
                if row["formation"] is None:
                    self.assertEqual(row["pre"]["memory_state_digest"],row["post"]["memory_state_digest"])
        self.assertEqual(sum(x["formations"] for x in proof["arms"].values()),30)
        self.assertEqual(sum(x["scans"] for x in proof["arms"].values()),16)

    def test_16_gate_remains_closed(self):
        self.assertFalse(c.MAIN_GATE)
        self.assertFalse(p.MAIN_GATE)
        self.assertFalse(b.MAIN_GATE)

    def test_17_profile_manipulation(self):
        record=b.sealed(dict(version=c.VERSION,profile="wrong",main_gate=False),"record_digest")
        self.reject("PROFILE_INVALID",lambda:v.verify(record))

    def test_18_readonly_missing_evidence(self):
        record=b.sealed(dict(version=c.VERSION,profile=c.PROFILE,main_gate=False,status="NOT_EVALUABLE",failure={}),"record_digest")
        before=b.canonical(record)
        self.reject("INCOMPLETE",lambda:v.verify(record))
        self.assertEqual(b.canonical(record),before)

    def test_19_closed_main_entry(self):
        self.reject("MAIN_GATE_CLOSED",lambda:entry.run_once({},OUT/"forbidden",qualification={},current_inventory={}))
        self.assertFalse((OUT/"forbidden").exists())
        self.assertFalse(entry.MAIN_GATE)

    def test_20_real_mode_rejects_neutral_supplier(self):
        self.reject("SUPPLIER_MODE_INVALID",lambda:c.run_materialized(manifest(),Supplier(),mode="MEDIA"))

    def test_21_gains_losses_and_negative_results(self):
        right=dict(target_admission=True,non_target_admission=False)
        abstain=dict(target_admission=False,non_target_admission=False)
        wrong=dict(target_admission=False,non_target_admission=True)
        self.assertTrue(c.comparison_flags(right,abstain)["gain"])
        self.assertTrue(c.comparison_flags(abstain,right)["loss"])
        self.assertTrue(c.comparison_flags(wrong,right)["experienced_non_target"])
        self.assertFalse(c.comparison_flags(abstain,abstain)["gain"])
        self.assertFalse(c.comparison_flags(wrong,abstain)["gain"])

    def test_22_neutral_full_resource_reservation(self):
        parts=[]
        for prefix in ("qualification","real","temporary"):
            parts += [dict(path=prefix+"-native",kind="native",bytes=6291456),
                      dict(path=prefix+"-formation",kind="formations",bytes=46080),
                      dict(path=prefix+"-generation",kind="generations",bytes=46080),
                      dict(path=prefix+"-nj",kind="nj",bytes=32768)]
        parts += [dict(path="meta",kind="metadata",bytes=1048576),
                  dict(path="proof",kind="verification",bytes=262144),
                  dict(path="sources",kind="sources",bytes=300000)]
        self.assertEqual(c.budget(parts)["violations"],[])
