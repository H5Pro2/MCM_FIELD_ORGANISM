"""One bounded neutral composition qualification, never NP payloads or NQ history."""
from copy import deepcopy
from dataclasses import asdict, replace, FrozenInstanceError
import json
import math
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tests import test_s2kz_private_auditory_partial_cue_retrieval_336 as fx
from tools import _s2nq_private_run as run
from tools import _s2nq_private_verification as verify
from tools import _s2nq_private_evaluation as evaluation
from mcm_field_organism.broadband_hearing_path import AuditoryReceptorState, AuditoryReceptorContact
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig

s, src = run.s, run.sources
METRICS = dict(scan_calls=0,scan_comparisons=0,verification_comparisons=0,historical_scan_calls=0,
               maximum_arm_bytes=0,maximum_serialization_bytes=0,neutral_formations=0,nj_calls=0)
EVENTS = tuple(src.Event("neutral-h01",f"neutral-e{i+1:02d}",i,"neutral-a01",None if i in (1,5) else 0) for i in range(6))


class NeutralSources:
    def __init__(self,config):
        self.config=config
        self.audio_analyses=self.visual_analyses=self.nj_projections=0
        self.catalog=dict(audio={"neutral-a01":dict(pcm_digest="1"*64,source_digest="2"*64,
            values_digest=s.digest([0.2]*48))},visual={"0":dict(payload_digest="3"*64,values_digest=s.digest([0.25]*288))},source_root="4"*64)

    def materialize(self,spec):
        config=self.config
        half=s.profile.half
        raw=AuditoryReceptorState("auditory",half.RAW_GEOMETRY,spec.ordinal*20,spec.ordinal*9600,
            spec.ordinal*9600+4800,config.profile.profile.auditory_config.carrier_ids,(0.4,)*48,AuditoryReceptorContact.ACTIVE_ENERGY)
        projection=half.project_auditory_half_v1(raw,config=LogSpectralConfig(),source_profile_digest=half.RAW_PROFILE_DIGEST)
        self.nj_projections+=1
        METRICS["nj_calls"]+=1
        visual=None
        if spec.kind=="FORMATION":
            p=config.profile.profile.visual_config
            visual=src.ReceptorContactFrame("visual",p.geometry_id,spec.event_id,"video.frame",
                6*spec.ordinal+2,6*spec.ordinal+3,p.carrier_ids,(0.25,)*288)
        return src.bind(spec,config,self.catalog,projection,visual)


def cue(config,view=s.VIEWS[0],values=None,start=9600):
    return s.Cue(s.plan(view),(0.1,)*24 if values is None else values,config.config_digest,
        s.profile.half.PROFILE_DIGEST,"1"*64,"2"*64,"3"*64,"audio.sample",start,start+4800)


def reseal(p,key):
    p[key]=s.digest({k:v for k,v in p.items() if k!=key})
    return p


def tearDownModule():
    print("NQ_NEUTRAL_METRICS "+json.dumps(METRICS,sort_keys=True,allow_nan=False))


class TransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config=s.profile.build_config()
        cls.tmp=tempfile.TemporaryDirectory()
        cls.provider=NeutralSources(cls.config)
        original_primary,original_direct,original_verify=s.retrieve,run.baseline.direct,run.baseline.verify
        verification_depth=[0]
        def observed(function):
            def call(**kwargs):
                result=function(**kwargs)
                if verification_depth[0]:
                    METRICS["verification_comparisons"]+=result.comparisons+result.equality_comparisons
                else:
                    METRICS["scan_calls"]+=1
                    METRICS["scan_comparisons"]+=result.comparisons+result.equality_comparisons
                METRICS["maximum_arm_bytes"]=max(METRICS["maximum_arm_bytes"],len(s.canonical(asdict(result))))
                return result
            return call
        def observed_verify(*args,**kwargs):
            verification_depth[0]+=1
            try:
                return original_verify(*args,**kwargs)
            finally:
                verification_depth[0]-=1
        # Guard the entire qualification, including setup, against real NP access.
        cls.guards=[patch.object(src,"load_catalog",side_effect=AssertionError("NP_CATALOG_FORBIDDEN")),
                    patch.object(src.Sources,"materialize",side_effect=AssertionError("NP_PAYLOAD_FORBIDDEN")),
                    patch.object(s,"retrieve",side_effect=observed(original_primary)),
                    patch.object(run.baseline,"direct",side_effect=observed(original_direct)),
                    patch.object(run.baseline,"verify",side_effect=observed_verify)]
        for guard in cls.guards:
            guard.start()
            cls.addClassCleanup(guard.stop)
        path=run.execute_once(run_id="s2nq-neutral-composition",output_root=cls.tmp.name,
            events=EVENTS,provider_factory=NeutralSources)
        cls.path=path
        cls.record=json.loads(path.read_bytes())
        if cls.record["status"] != "RECORDING_COMPLETE":
            raise AssertionError(cls.record["failure"])
        METRICS["neutral_formations"]=cls.record["counts"]["formations"]
        cls.proof=verify.verify_record(cls.record,events=EVENTS,catalog=cls.provider.catalog,config=cls.config)
        out=Path(os.environ["S2NQ_QUAL_DIR"])
        run.io.atomic_write(out/"neutral-recording.json",cls.record,run.MAX_BYTES)
        run.io.atomic_write(out/"neutral-verification.json",cls.proof,run.MAX_BYTES)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def arms(self,state,c):
        results=[]
        for fn in (s.retrieve,run.baseline.direct):
            r=fn(config=self.config,state=state,cue=c)
            run.baseline.verify(r,config=self.config,state=state,cue=c)
            results.append(r)
        self.assertEqual(run.baseline.semantics(results[0]),run.baseline.semantics(results[1]))
        return results[0]

    def test_01_two_literal_masks_and_complements(self):
        for view in s.VIEWS:
            p=s.plan(view)
            self.assertEqual(24,len(p.observed))
            self.assertEqual(set(range(48)),set(p.observed)|set(p.complement))
            self.assertFalse(set(p.observed)&set(p.complement))
            with self.assertRaises(FrozenInstanceError):
                p.view="other"
            with self.assertRaises(s.S2NQError):
                replace(p,observed=tuple(reversed(p.observed)))

    def test_02_cue_only_has_24_values(self):
        for view in s.VIEWS:
            c=cue(self.config,view)
            self.assertEqual(24,len(c.values))
            with self.assertRaises(s.S2NQError):
                replace(c,values=(0.1,)*48)
            with self.assertRaises(s.S2NQError):
                replace(c,values=list(c.values))

    def test_03_complement_hypothesis(self):
        v=tuple(float(i)/480 for i in range(48))
        st=fx._state(self.config,b4=(v,))
        for view in s.VIEWS:
            p=s.plan(view)
            r=self.arms(st,cue(self.config,view,tuple(v[i] for i in p.observed)))
            self.assertEqual("ADMIT_SINGLE_CONTEXT",r.decision)
            self.assertEqual(p.complement,r.hypothesis.indices)
            self.assertEqual(tuple(v[i] for i in p.complement),r.hypothesis.values)

    def test_04_historical_contiguous_compatibility(self):
        for st in (fx._state(self.config),fx._state(self.config,b4=(fx.MATCH_A,),fast=(fx.MATCH_A,)),
                   fx._state(self.config,slow=(fx.MATCH_A,)),fx._state(self.config,b4=(fx.MATCH_A,fx.MATCH_B))):
            c=cue(self.config)
            r=self.arms(st,c)
            bp=s.ne.kz.build_auditory_band_plan_48()
            oldcue=s.ne.kz.build_masked_auditory_cue_48(pcm_payload_digest=c.pcm_digest,receptor_state_digest=c.parent_digest,
                receptor_values_digest=c.parent_values_digest,config_digest=c.config_digest,
                auditory_source_clock_id=c.clock_id,auditory_window_start_tick=c.start,auditory_window_end_tick=c.end,
                observed_values=c.values,band_plan=bp)
            old=s.ne.retrieve(rule=s.ne.ALTERNATIVE,config=self.config,state=st,cue=oldcue,band_plan=bp).evidence
            METRICS["historical_scan_calls"]+=1
            self.assertEqual((old.decision,old.a_recent.status,old.b_stable_auditory.status),(r.decision,r.a_status,r.b_status))
            for a,b in zip([x for bank in old.bank_scans for x in bank.records],r.rows,strict=True):
                self.assertEqual((a.slot_id,a.eligible,a.observed_match,a.observed_distance),
                                 (b.slot_id,b.eligible,b.matched,b.statistic))
            self.assertEqual(None if old.hypothesis is None else old.hypothesis.proposed_values,
                             None if r.hypothesis is None else r.hypothesis.values)

    def test_05_maximum_inclusive_boundary(self):
        for view in s.VIEWS:
            for v,matched in ((0.1,True),(math.nextafter(0.1,math.inf),False)):
                with self.subTest(view=view,value=v):
                    values=[0.0]*48
                    values[s.plan(view).observed[0]]=v
                    r=self.arms(fx._state(self.config,b4=(tuple(values),)),cue(self.config,view,(0.0,)*24))
                    self.assertEqual(matched,r.rows[0].matched)

    def test_06_slow_historical_sum_and_support(self):
        v=(0.01,)*48
        for view in s.VIEWS:
            for support in (2,3):
                with self.subTest(view=view,support=support):
                    r=self.arms(fx._state(self.config,slow=(v,),slow_supports=(support,)),cue(self.config,view,(0.0,)*24))
                    row=r.rows[12]
                    self.assertEqual(support==3,row.eligible)
                    self.assertEqual(None if support==2 else sum((0.01,)*24)/24,row.statistic)

    def test_07_internal_equality_and_conflict(self):
        for view in s.VIEWS:
            a=(0.1,)*48
            b=list(a)
            b[s.plan(view).complement[-1]]=0.2
            for right,expected in ((a,"ADMIT_SINGLE_CONTEXT"),(tuple(b),"ABSTAIN_INTERNAL_CONFLICT")):
                r=self.arms(fx._state(self.config,b4=(a,),fast=(right,)),cue(self.config,view))
                self.assertEqual(expected,r.decision)
                self.assertEqual(48,r.equality_comparisons)

    def test_08_each_bank_ambiguity_full_scan(self):
        for view in s.VIEWS:
            for kw in (dict(b4=((0.1,)*48,)*2),dict(fast=((0.1,)*48,)*2),dict(slow=((0.1,)*48,)*2)):
                r=self.arms(fx._state(self.config,**kw),cue(self.config,view))
                self.assertEqual("ABSTAIN_INTERNAL_AMBIGUITY",r.decision)
                self.assertEqual((9,3,8),tuple(sum(x.bank==b for x in r.rows) for b in s.ROLES))

    def test_09_public_ambiguity_no_b_preference(self):
        st=fx._state(self.config,b4=((0.1,)*48,),slow=((0.1,)*48,))
        for view in s.VIEWS:
            r=self.arms(st,cue(self.config,view))
            self.assertEqual("ABSTAIN_AMBIGUOUS_CONTEXT",r.decision)
            self.assertIsNone(r.hypothesis)

    def test_10_null_and_incompatible(self):
        for st,expected in ((fx._state(self.config),"ABSTAIN_NO_CONTEXT"),
                             (fx._state(self.config,b4=(fx.MISMATCH,)),"ABSTAIN_NO_APPLICABLE_CONTEXT")):
            for view in s.VIEWS:
                self.assertEqual(expected,self.arms(st,cue(self.config,view)).decision)

    def test_11_hidden_positions_not_used_for_applicability(self):
        for view in s.VIEWS:
            a=(0.1,)*48
            b=list(a)
            for i in s.plan(view).complement:
                b[i]=0.99
            ra=self.arms(fx._state(self.config,b4=(a,)),cue(self.config,view))
            rb=self.arms(fx._state(self.config,b4=(tuple(b),)),cue(self.config,view))
            self.assertEqual((ra.rows[0].terms,ra.decision),(rb.rows[0].terms,rb.decision))
            self.assertNotEqual(ra.hypothesis.values,rb.hypothesis.values)

    def test_12_native_time_and_profile_rejection(self):
        c=cue(self.config)
        st=fx._state(self.config)
        with self.assertRaises(s.S2NQError):
            s.retrieve(config=fx._config(),state=st,cue=c)
        with self.assertRaises(s.S2NQError):
            replace(c,clock_id="video.frame")
        with self.assertRaises(s.S2NQError):
            replace(c,end=c.end+1)
        with self.assertRaises(s.S2NQError):
            self.arms(fx._state(self.config,b4=(fx.MATCH_A,),auditory_end_tick=12000),c)

    def test_13_source_and_numeric_errors(self):
        c=cue(self.config)
        for bad in (math.inf,math.nan,-0.1,1.01):
            with self.subTest(bad=repr(bad)), self.assertRaises(s.S2NQError) as caught:
                replace(c,values=(bad,)+(0.1,)*23)
            self.assertEqual("VALUE_DOMAIN_INVALID",caught.exception.code)
        with self.assertRaises(s.S2NQError):
            replace(c,pcm_digest="missing")

    def test_14_state_and_scan_manipulation(self):
        st=fx._state(self.config,b4=(fx.MATCH_A,))
        c=cue(self.config)
        with self.assertRaises(s.S2NQError):
            s.retrieve(config=self.config,state=replace(st,state_digest="0"*64),cue=c)
        r=self.arms(st,c)
        bad=replace(r,rows=tuple(reversed(r.rows)))
        bad=replace(bad,result_digest=s.digest(bad.payload()))
        with self.assertRaises(s.S2NQError):
            run.baseline.verify(bad,config=self.config,state=st,cue=c)

    def test_15_read_only_continuation_and_ppb(self):
        self.assertEqual(4,self.record["counts"]["formations"])
        events=self.record["events"]
        self.assertEqual(events[0]["poststate"],events[1]["prestate"])
        self.assertEqual(events[1]["prestate"],events[1]["poststate"])
        self.assertEqual(events[1]["poststate"],events[2]["prestate"])
        self.assertEqual(["NO_UPDATE","CREATED","MATCHED","MATCHED"],
                         [t["ppb"][0]["event"] for t in self.proof["transitions"]])
        self.assertEqual(3,self.proof["transitions"][-1]["ppb"][0]["support"])
        self.assertTrue(self.proof["read_only"])

    def test_16_literal_main_plan_is_metadata_only(self):
        src.validate_plan(src.EVENTS)
        self.assertEqual((36,16,20),(len(src.EVENTS),sum(e.kind=="FORMATION" for e in src.EVENTS),sum(e.kind=="CUE" for e in src.EVENTS)))
        self.assertFalse(run.MAIN_GATE)
        with self.assertRaises(s.S2NQError):
            run.run_main_once(run_id="s2nq-blocked-main")
        self.assertFalse(run.MAIN_GATE)

    def test_17_source_binding_mutations_independent(self):
        for index in (0,1):
            for kind in ("event","clock","visual","values"):
                with self.subTest(index=index,kind=kind):
                    receipt=deepcopy(self.record["events"][index]["source"])
                    if kind=="event": receipt["event"]["ordinal"]+=1
                    if kind=="clock": receipt["projection"]["clock_id"]="wrong-clock"
                    if kind=="visual": receipt["visual"]=None if index==0 else self.record["events"][0]["source"]["visual"]
                    if kind=="values": receipt["projection"]["values"][0]=0.99
                    reseal(receipt,"binding_digest")
                    with self.assertRaises(s.S2NQError):
                        src.restore(EVENTS[index],receipt,self.config,self.provider.catalog)

    def test_18_missing_and_swapped_evidence(self):
        for kind in ("missing","swapped","arm"):
            r=deepcopy(self.record)
            if kind=="missing": r["events"].pop()
            if kind=="swapped": r["events"][0],r["events"][1]=r["events"][1],r["events"][0]
            if kind=="arm":
                r["events"][1]["arms"].pop()
                reseal(r["events"][1],"event_digest")
            reseal(r,"record_digest")
            with self.subTest(kind=kind),self.assertRaises(s.S2NQError):
                verify.verify_record(r,events=EVENTS,catalog=self.provider.catalog,config=self.config)

    def test_19_valid_abstention_and_evaluation_separation(self):
        # Final neutral cue is ambiguous: repeated B4 and stable B, still verified.
        self.assertIsNone(self.record["events"][-1]["arms"][0]["hypothesis"])
        result=evaluation.evaluate(self.record,self.proof,{"neutral-a01":("neutral-a01","EXACT")})
        self.assertEqual("EVALUATED",result["status"])
        self.assertFalse(result["observations"][-1]["correct"][0])

    def test_20_separate_denominators_and_loss(self):
        self.assertEqual(dict(N=3,D=2,R=1,L=1,status="ASSESSED",gains=1),evaluation.retention([(True,True),(True,False),(False,True)]))
        self.assertEqual("ERHALTUNG_NICHT_GEPRUEFT",evaluation.retention([(False,True)])["status"])
        result=evaluation.evaluate(self.record,self.proof,{"neutral-a01":("neutral-a01","VARIANT")})
        self.assertEqual(2,sum(g["public_retention"]["N"] for g in result["groups"]))
        self.assertGreater(sum(g["relationship_retention"][b]["N"] for g in result["groups"] for b in s.ROLES),2)

    def test_21_atomic_conflict_and_failure_record(self):
        with self.assertRaises(FileExistsError):
            run.io.atomic_write(self.path,self.record,run.MAX_BYTES)
        class Broken(NeutralSources):
            def materialize(self,spec):
                raise s.S2NQError("NEUTRAL_SOURCE_FAILURE")
        path=run.execute_once(run_id="s2nq-neutral-failure",output_root=self.tmp.name,events=EVENTS,provider_factory=Broken)
        r=json.loads(path.read_bytes())
        self.assertEqual(("NOT_EVALUABLE","SOURCE",0),(r["status"],r["failure"]["phase"],r["failure"]["completed_events"]))
        self.assertEqual("NOT_EVALUABLE",verify.verify_record(r,events=EVENTS,catalog=self.provider.catalog,config=self.config)["status"])

    def test_22_one_readonly_file_verification(self):
        path=verify.verify_file_once(self.path,events=EVENTS,catalog=self.provider.catalog,config=self.config)
        proof=json.loads(path.read_bytes())
        self.assertTrue(proof["file_unchanged"])
        self.assertEqual("RECORDING_COMPLETE",proof["status"])
        with self.assertRaises(s.S2NQError):
            verify.verify_file_once(self.path,events=EVENTS,catalog=self.provider.catalog,config=self.config)

    def test_23_full_serialization_and_separate_work_limits(self):
        value=0.00019999999999999998
        st=fx._state(self.config,b4=((value,)*48,)*9,fast=((value,)*48,)*3,slow=((value,)*48,)*8)
        r=self.arms(st,cue(self.config,values=(0.0,)*24))
        self.assertEqual(480,r.comparisons)
        # Serialization only: no main source generation, formation or 36-event execution.
        form=deepcopy(self.record["events"][0])
        ce=deepcopy(self.record["events"][1])
        ce["arms"]=[asdict(r)]*4
        largest={**self.record,"states":{f"{i:064x}":asdict(st) for i in range(20)},"events":[form]*16+[ce]*20}
        size=len(s.canonical(largest))
        METRICS["maximum_serialization_bytes"]=size
        self.assertLessEqual(size,run.MAX_BYTES)
        self.assertLessEqual(len(s.canonical(asdict(r))),32768)
        self.assertEqual(38400,run.VERIFY_LIMITS["band_differences"])
        self.assertEqual(38400,run.LIMITS["band_differences"])
        self.assertGreater(self.proof["verification_work"]["fast_rank_terms"],0)
        oversized={**self.record,"padding":"x"*run.MAX_BYTES}
        with self.assertRaises(s.S2NQError):
            verify.verify_record(oversized,events=EVENTS,catalog=self.provider.catalog,config=self.config)

    def test_24_baseline_has_no_productive_scan_helpers(self):
        st=fx._state(self.config,b4=(fx.MATCH_A,))
        with patch.object(s,"retrieve",side_effect=AssertionError("NO_SHARED_SCAN")):
            r=run.baseline.direct(config=self.config,state=st,cue=cue(self.config))
        self.assertEqual("ADMIT_SINGLE_CONTEXT",r.decision)
        self.assertEqual("DIRECT_BASELINE",r.implementation)
        self.assertFalse(run.MAIN_GATE)
