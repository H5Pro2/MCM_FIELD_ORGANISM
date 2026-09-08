"""Neutral composition only; no NR payload generation or receptor analyses."""
from copy import deepcopy
from dataclasses import asdict, FrozenInstanceError, replace
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from mcm_field_organism.broadband_hearing_path import AuditoryReceptorState, AuditoryReceptorContact
from tools import _s2nr_private_runtime_binding as run
from tools import _s2nr_private_runtime_verification as verify

nn,ng,s=run.nn,run.ng,run.s
canonical=s.canonical
CLOCK="s2nr-neutral-runtime-clock"
METRICS=dict(runtime_events=0,formations=0,field_contacts=0,scans=0,verification_calls=0,
    nr_payload_calls=0,receptor_calls=0,nj_projections=0)


def archive(name,value):
    from tools._s2np_private_source_binding import publish
    publish(Path(os.environ["S2NR_QUAL_DIR"])/name,value,ng.MAX_BYTES)


def fixture(config):
    result=[]
    carriers=tuple(b.channel_id for b in nn.half.spectral.logarithmic_bands(nn.LogSpectralConfig()))
    for n,kind in enumerate(("COMPLETE_AV_PERCEPTION","PARTIAL_AUDITORY_CUE","COMPLETE_AV_PERCEPTION","PARTIAL_VISUAL_CUE")):
        end=(n+1)*100000000
        common=nn.CommonFieldTime(CLOCK,end-10000000,end)
        audio=None if n==3 else AuditoryReceptorState("auditory",nn.half.RAW_GEOMETRY,n*10,n*4800,(n+1)*4800,
            carriers,tuple(0.4+float(i%4)/16 for i in range(48)),AuditoryReceptorContact.ACTIVE_ENERGY)
        visual=None
        if n!=1:
            vp=config.profile.profile.visual_config
            values=(0.25,)*32+(0.0,)*256 if n==3 else (0.25,)*288
            visual=nn.OrganismTimedReceptorFrame(nn.ReceptorContactFrame("visual",vp.geometry_id,
                f"s2nr-neutral-frame-{n}","video.frame",3*n+2,3*n+3,vp.carrier_ids,values),
                nn.CommonFieldTime(CLOCK,(3*n+2)*1000000000//30,end) if n!=3 else common)
        value=nn.bind_event(config=config,event_id=f"s2nr-neutral-event-{n+1:02d}",ordinal=n+1,
            event_type=kind,field_start_tick=n*100000000,common_time=common,
            raw_audio=audio,pcm_digest=None if audio is None else s.digest(dict(neutral_audio=n)),
            visual=visual,rgb_digest=None if visual is None else s.digest(dict(neutral_rgb=n)),
            visual_time_binding=visual.field_time if n in (0,2) else None)
        METRICS["nj_projections"]+=int(audio is not None)
        result.append(value)
    return tuple(result)


def execute(inputs,config,name,failure=None):
    c=run.MaskRuntimeComparison(inputs=inputs,config=config,comparison_id=name,field_clock_id=CLOCK)
    if failure:
        def fail(state,event):
            raise ValueError("neutral branch failure")
        for subject in c.subjects:
            if failure=="scan":
                subject._processor._auditory_scan=fail
                subject._processor._auditory_baseline=fail
            else:
                subject._processor._field=fail
    for _ in inputs:
        c.process_next()
        if c.failed:
            break
    r=c.finish()
    METRICS["runtime_events"]+=2*len(r["pairs"])
    METRICS["formations"]+=2*sum(e.event_type=="COMPLETE_AV_PERCEPTION" for e in c.events[:len(r["pairs"])])
    METRICS["field_contacts"]+=sum(sum(len(t.frame.values) for t in c.events[n].field_payload.timed_frames)
        for n,p in enumerate(r["pairs"]) for a in p["arms"] if a["step"]["perception_status"]=="FIELD_CONTACT_RECORDED")
    METRICS["scans"]+=len(r["scans"])
    return c,r


def proof(record,inputs,config):
    METRICS["verification_calls"]+=1
    return verify.verify_record(record,inputs=inputs,config=config)


def tearDownModule():
    archive("metrics.json",METRICS)


class MaskRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config=nn.profile.build_config()
        cls.inputs=fixture(cls.config)
        cls.c,cls.record=execute(cls.inputs,cls.config,"s2nr-neutral-main")
        archive("neutral-record.json",cls.record)
        cls.proof=proof(cls.record,cls.inputs,cls.config)
        archive("neutral-proof.json",cls.proof)

    def test_01_fixed_views_profile_and_defaults(self):
        self.assertEqual(s.VIEWS,tuple(b["view"] for b in self.c.bindings))
        for b in self.c.bindings:
            self.assertEqual(("ALL_BANDS_24",0.1,0.01),(b["a_rule"],b["a_threshold"],b["slow_threshold"]))
        self.assertFalse(run.MAIN_GATE)
        self.assertFalse(nn.MAIN_GATE)
        self.assertFalse(ng.MAIN_GATE)
        with self.assertRaisesRegex(s.S2NQError,"MAIN_GATE_CLOSED"):
            run.MaskRuntimeComparison(inputs=self.inputs,config=self.config,comparison_id="s2nr-main-closed",field_clock_id=CLOCK,mode="MAIN")

    def test_02_parent_shared_only_operation_differs(self):
        a,b=self.c.arm_events[1]
        self.assertEqual(a.event_digest,b.event_digest)
        self.assertIs(a.field_payload,b.field_payload)
        self.assertEqual(a.source_digest,b.source_digest)
        self.assertNotEqual(a.operation_payload.cue.cue_digest,b.operation_payload.cue.cue_digest)
        for event,view in zip((a,b),s.VIEWS,strict=True):
            cue=event.operation_payload.cue
            self.assertEqual(24,len(cue.values))
            self.assertEqual(tuple(self.inputs[1].auditory_projection.values[i] for i in s.plan(view).observed),cue.values)
            self.assertEqual(["band_plan","values","config_digest","profile_digest","pcm_digest","parent_digest",
                "parent_values_digest","clock_id","start","end","schema"],list(asdict(cue)))

    def test_03_independent_instances_and_identical_states(self):
        self.c._isolation()
        a,b=self.c.subjects
        self.assertIsNot(a,b)
        self.assertIsNot(a._processor,b._processor)
        self.assertIsNot(a._state,b._state)
        for pair in self.record["pairs"]:
            self.assertEqual(pair["arms"][0]["field"],pair["arms"][1]["field"])
            self.assertEqual(pair["arms"][0]["memory"],pair["arms"][1]["memory"])

    def test_04_hypothesis_exact_type_and_complement(self):
        for i,view in enumerate(s.VIEWS):
            step=self.record["pairs"][1]["arms"][i]["step"]
            h=step["hypothesis"]
            self.assertEqual("CONTEXT_CANDIDATE_AVAILABLE",step["context_status"])
            self.assertEqual(s.plan(view).complement,tuple(h["candidate"]["indices"]))
            self.assertEqual(24,len(h["candidate"]["values"]))
            self.assertEqual("A_RECENT",h["candidate"]["area"])

    def test_05_historical_schema_payload_and_type_acceptance(self):
        kwargs=dict(runtime_id="s2nr-historical-neutral",max_event_count=4,source_binding_digest="1"*64,component_binding_digest="2"*64)
        rc=ng.runtime.build_minimal_runtime_config(**kwargs)
        expected=dict(schema="s2mr.private.minimal-mcm-runtime-336.v1",**kwargs)
        self.assertEqual(expected,rc.payload_without_digest())
        self.assertEqual(s.digest(expected),rc.config_digest)
        pre=verify.old.old.decode_state(self.record["states"][self.record["pairs"][0]["arms"][0]["memory"]],self.config)
        op=self.inputs[1].event.operation_payload
        historical=ng.audio.retrieve(rule="ALL_BANDS_24",config=self.config,state=pre,cue=op.cue,band_plan=op.band_plan).evidence
        self.assertIs(historical.hypothesis,ng.runtime._validate_hypothesis(historical.hypothesis,event_type="PARTIAL_AUDITORY_CUE"))
        result=self.c.scans[0][(2,"PRIMARY")]
        self.assertEqual(historical.decision,result.decision)
        self.assertEqual(historical.hypothesis.proposed_values,result.hypothesis.values)
        with self.assertRaises(ng.runtime.S2MRRuntimeError):
            ng.runtime._validate_hypothesis(run.types.wrap(result,self.c.arm_events[1][0].operation_payload),event_type="PARTIAL_AUDITORY_CUE")
        rc2=ng.runtime.MaskedMCMRuntimeConfig336V2(**self.record["runtime_configs"][0])
        with self.assertRaises(ng.runtime.S2MRRuntimeError):
            ng.runtime._validate_hypothesis(historical.hypothesis,event_type="PARTIAL_AUDITORY_CUE",config=rc2,
                operation=self.c.arm_events[1][0].operation_payload,state_digest=pre.state_digest)

    def test_06_wrong_mask_complement_profile_and_origin(self):
        op=self.c.arm_events[1][0].operation_payload
        result=self.c.scans[0][(2,"PRIMARY")]
        good=run.types.wrap(result,op)
        rc=ng.runtime.MaskedMCMRuntimeConfig336V2(**self.record["runtime_configs"][0])
        for name,bad in (("mask",replace(good,band_plan=s.plan(s.VIEWS[1]))),
            ("complement",replace(good,candidate=replace(good.candidate,indices=tuple(range(24))))),
            ("profile",replace(good,profile_digest="0"*64)),
            ("source",replace(good,source_digest="0"*64)),
            ("provenance",replace(good,candidate=replace(good.candidate,provenance=("bad",))))):
            with self.subTest(name=name),self.assertRaises(ng.runtime.S2MRRuntimeError):
                ng.runtime._validate_hypothesis(bad,event_type="PARTIAL_AUDITORY_CUE",config=rc,
                    operation=op,state_digest=result.prestate_digest)

    def test_07_hidden_cue_values_not_scanned(self):
        op=self.c.arm_events[1][0].operation_payload
        state=verify.old.old.decode_state(self.record["states"][self.record["pairs"][0]["arms"][0]["memory"]],self.config)
        changed=replace(op.cue,parent_values_digest="0"*64)
        a=s.retrieve(config=self.config,state=state,cue=changed)
        with patch.object(s,"retrieve",side_effect=AssertionError("production scan forbidden")):
            b=run.direct.direct(config=self.config,state=state,cue=changed)
        self.assertEqual(a.rows,self.c.scans[0][(2,"PRIMARY")].rows)
        self.assertEqual(a.hypothesis,b.hypothesis)
        with self.assertRaisesRegex(s.S2NQError,"CUE_SOURCE_INVALID"):
            run.pack_event(replace(self.c.arm_events[1][0],operation_payload=replace(op,cue=changed)),self.config,s.VIEWS[0])

    def test_08_read_only_and_continued_atomic_history(self):
        for i in range(2):
            a,cue,b,last=[p["arms"][i] for p in self.record["pairs"]]
            self.assertEqual(a["memory"],cue["memory"])
            self.assertEqual(cue["memory"],b["pre"]["memory_state_digest"])
            self.assertEqual(b["memory"],last["memory"])
            state=self.c.branches[i][1].state
            self.assertEqual(2,state.generation)
            self.assertEqual(2,state.tspm_state.fast_state.slots[0].support_count)
            self.assertEqual(1,state.tspm_state.auditory_ppb1_state.slots[0].support_count)

    def test_09_full_scans_and_independent_baselines(self):
        self.assertEqual(8,len(self.record["scans"]))
        self.assertTrue(self.proof["baseline_equal"])
        for i in range(2):
            a,b=(self.c.scans[i][(2,k)] for k in ("PRIMARY","DIRECT_BASELINE"))
            self.assertEqual(20,len(a.rows))
            self.assertEqual(run.direct.semantics(a),run.direct.semantics(b))
            self.assertEqual((9,3,8),tuple(sum(r.bank==bank for r in a.rows) for bank in s.ROLES))
        self.assertEqual(self.c.scans[0][(4,"PRIMARY")],self.c.scans[1][(4,"PRIMARY")])

    def test_10_scan_error_keeps_field_and_closes(self):
        c,r=execute(self.inputs[:2],self.config,"s2nr-neutral-scan-failure","scan")
        archive("scan-failure.json",r)
        p=proof(r,self.inputs[:2],self.config)
        archive("scan-failure-proof.json",p)
        self.assertEqual("NOT_EVALUABLE",p["status"])
        for a in r["pairs"][-1]["arms"]:
            self.assertEqual("SCAN_FAILED",a["step"]["context_status"])
            self.assertEqual("FIELD_CONTACT_RECORDED",a["step"]["perception_status"])
            self.assertEqual(a["pre"]["memory_state_digest"],a["post"]["memory_state_digest"])
        self.assertTrue(c.closed)

    def test_11_field_error_does_not_cancel_memory(self):
        c,r=execute(self.inputs[:1],self.config,"s2nr-neutral-field-failure","field")
        archive("field-failure.json",r)
        p=proof(r,self.inputs[:1],self.config)
        archive("field-failure-proof.json",p)
        self.assertEqual("NOT_EVALUABLE",p["status"])
        for a in r["pairs"][0]["arms"]:
            self.assertEqual("FIELD_CONTACT_FAILED",a["step"]["perception_status"])
            self.assertEqual("FORMATION_COMMITTED",a["step"]["memory_status"])
        self.assertTrue(c.closed)

    def test_12_lifecycle_and_immutable_types(self):
        for subject in self.c.subjects:
            self.assertEqual("CLOSED",subject.snapshot().status)
            with self.assertRaises(ng.runtime.S2MRRuntimeError):
                subject.close()
            with self.assertRaises(ng.runtime.S2MRRuntimeError):
                subject.process_once(self.inputs[0].event)
        with self.assertRaises(FrozenInstanceError):
            self.c.arm_events[1][0].operation_payload.cue.values=(0.0,)*24

    def test_13_valid_abstention_not_technical_failure(self):
        self.assertEqual("RECORDING_COMPLETE",self.proof["status"])
        self.assertEqual("ABSTAIN_INTERNAL_AMBIGUITY",self.record["pairs"][3]["arms"][0]["step"]["context_status"])
        # A functional expectation is not an input to verification.
        expected="CONTEXT_CANDIDATE_AVAILABLE"
        self.assertNotEqual(expected,self.record["pairs"][3]["arms"][0]["step"]["context_status"])

    def test_14_missing_swapped_and_corrupted_evidence(self):
        for name in ("missing","swapped","source","state"):
            with self.subTest(name=name):
                bad=deepcopy(self.record)
                if name=="missing": bad["scans"].pop()
                elif name=="swapped": bad["pairs"][0],bad["pairs"][1]=bad["pairs"][1],bad["pairs"][0]
                elif name=="source": bad["inputs"][1]["pcm_digest"]="0"*64
                else: next(iter(bad["states"].values()))["generation"]=8
                bad=ng.sealed({k:v for k,v in bad.items() if k!="record_digest"},"record_digest")
                with self.assertRaises((s.S2NQError,ng.S2NGError)):
                    proof(bad,self.inputs,self.config)

    def test_15_profile_time_and_double_projection_rejected(self):
        with self.assertRaises(nn.S2NNError):
            run.pack_input(self.inputs[0],ng.ne.make_config())
        with self.assertRaises(nn.half.S2NJProjectionError):
            nn.bind_event(config=self.config,event_id="s2nr-double-projection",ordinal=1,event_type="PARTIAL_AUDITORY_CUE",
                field_start_tick=0,common_time=nn.CommonFieldTime(CLOCK,90000000,100000000),
                raw_audio=self.inputs[0].auditory_projection,pcm_digest="1"*64)
        op=self.c.arm_events[1][0].operation_payload
        bad=replace(op,cue=replace(op.cue,start=0,end=4800))
        with self.assertRaisesRegex(s.S2NQError,"CUE_SOURCE_INVALID"):
            run.pack_event(replace(self.c.arm_events[1][0],operation_payload=bad),self.config,s.VIEWS[0])
        self.assertEqual(3,METRICS["nj_projections"])

    def test_16_output_envelopes_and_separate_work(self):
        budget=run.limits(("COMPLETE_AV_PERCEPTION",)*14+("PARTIAL_AUDITORY_CUE",)*4)
        self.assertEqual((320,7680,768,16,8448),(budget["slot_visits"],budget["band_differences"],
            budget["equality_comparisons"],budget["verification_scan_calls"],budget["verification_value_comparisons"]))
        self.assertLess(budget["serialization_bound"],ng.MAX_BYTES)
        # Worst-case complete envelopes, not only payload subtotals.
        envelope=dict(metadata="m"*65536,states={str(i):"s"*98304 for i in range(15)},
            inputs=["i"*16384 for _ in range(18)],pairs=["p"*16384 for _ in range(18)],
            scans=[dict(arm=1,ordinal=18,role="DIRECT_BASELINE",value="r"*32768) for _ in range(16)])
        self.assertLess(len(canonical(envelope)),budget["serialization_bound"])
        self.assertLess(len(canonical(self.record)),ng.MAX_BYTES)
        for p in self.record["inputs"]: self.assertLessEqual(len(canonical(p)),ng.MAX_INPUT_BYTES)
        for p in self.record["pairs"]: self.assertLessEqual(len(canonical(p)),ng.MAX_PAIR_BYTES)
        bad={**self.record,"oversize":"x"*ng.MAX_BYTES}
        with self.assertRaises((s.S2NQError,ng.S2NGError)):
            proof(bad,self.inputs,self.config)
        archive("size-metrics.json",dict(neutral_record_bytes=len(canonical(self.record)),
            max_envelope_bytes=len(canonical(envelope)),bound=budget["serialization_bound"],limits=budget))
