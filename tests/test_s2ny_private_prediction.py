"""Bound neutral NY qualification; sealed sources and real entry are blocked."""
from copy import deepcopy
from dataclasses import fields
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import _s2ny_private_prediction as p
from tools import _s2ny_private_prediction_run as run
from tools import _s2ny_private_prediction_verification as direct
from tools import _s2ny_private_prediction_evaluation as evaluation
from tests.test_s2ny_private_source_binding import nx_fixture,extract
from tests.test_s2nv_private_prediction import synthetic_window,CARRIERS,reseal

b=p.b
LEVELS=((.125,.25,.28125,.2890625,.291015625),(.125,.25,.34375,.4140625,.466796875),
        (.125,.25,.5,.875,.9375),(.25,.25,.25,.25,.25),(.125,.25,.28125,.25,.2421875),
        (.125,.25,.34375,.0625,.0625))


def values(x):
    return (float(x),)*48


def neutral_plan(label="neutral",levels=LEVELS):
    rows=[]
    for s,seq in enumerate(levels):
        for k,level in enumerate(seq):
            n=len(rows)
            rows.append(b.sealed(dict(source_id=f"{label}-s{s+1:02d}-w{k:02d}",ordinal=n+1,
                stream_id=f"s{s+1:02d}",window_ordinal=k,window_start_sample=n*4800,window_end_sample=(n+1)*4800,
                nj_snapshot_index=n*10,clock_id="audio.sample",pcm_sha256="a"*64,recipe_digest="b"*64,
                neutral_half=level),"source_digest"))
    return b.sealed(dict(sources=rows,profiles=b.profile_binding(),freeze_import=extract(*nx_fixture()),
        environment={"neutral":True}),"execution_digest")


class NeutralReader:
    carriers=CARRIERS

    def __init__(self):
        self.calls=[]

    def __call__(self,source,work):
        self.calls.append(source["source_id"])
        work.phase,work.source_id="NEUTRAL_WINDOW",source["source_id"]
        for key in ("generation_attempts","payloads_checked","analyze_attempts","analyze_returns","nj_attempts","nj_returns"):
            work.add(key)
        return synthetic_window(source)


def prefix(label="neutral",observed=False):
    plan,work,reader=neutral_plan(label),p.Work(),NeutralReader()
    frozen=run.FrozenInputs(plan["freeze_import"])
    stream=run.PrefixStream(plan["sources"][:5],work,reader,frozen)
    stream.read_next(0)
    stream.read_next(1)
    if observed:
        stream.bind_predictions()
        stream.read_next(2)
    return stream,reader,work,frozen


class PredictionQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for module in (b,b.pure,b.pure.pure,run.nw.b,run.nw.nv.b):
            guard=patch.object(module,"pcm_window",side_effect=AssertionError("sealed payload forbidden"))
            guard.start()
            cls.addClassCleanup(guard.stop)
        for name in ("load_presealed","make_reader"):
            guard=patch.object(run,name,side_effect=AssertionError("no real NY entry"))
            guard.start()
            cls.addClassCleanup(guard.stop)
        cls.plan=neutral_plan()
        cls.reader=NeutralReader()
        cls.record=run.execute(cls.plan,cls.reader,"neutral-recommendation")

    def code(self,code,fn,*args,**kwargs):
        with self.assertRaises(p.S2NYPredictionError) as caught:
            fn(*args,**kwargs)
        self.assertEqual(caught.exception.code,code)

    def test_01_complete_neutral_composition(self):
        self.assertEqual(self.record["status"],"RECORDING_COMPLETE",self.record["failure"])
        self.assertEqual(len(self.reader.calls),30)
        self.assertEqual(self.record["work"]["bound_sites"],18)
        proof=direct.verify_record(self.record,self.plan)
        self.assertEqual(proof["status"],"S2NY_PREDICTION_VERIFIED")

    def test_02_frozen_inputs_unchanged(self):
        self.assertEqual(self.record["freeze_import"],self.plan["freeze_import"])
        frozen=run.FrozenInputs(self.plan["freeze_import"])
        before=frozen.data
        frozen.coefficients()
        self.assertEqual(before,frozen.data)
        self.assertFalse(hasattr(frozen,"update"))
        frozen.release()
        self.assertTrue(frozen.closed)
        self.assertIsNone(frozen.data)

    def test_03_insufficient_prefix_no_fake_error(self):
        for stream in self.record["streams"]:
            site=stream["sites"][0]
            arm=site["prediction_binding"]["primary"]
            self.assertEqual(arm["recommendation"],dict(status="ABSTAIN_INSUFFICIENT_PREFIX",history=None))
            self.assertIsNone(arm["local"])
            self.assertIsNone(site["primary"]["recommended_mae"])
            self.assertEqual(site["primary"]["recommendation_gains"],{})
            self.assertEqual(set(arm["predictions"]),{"H1","H2","PERSIST"})

    def test_04_tie_not_fallback(self):
        for site in self.record["streams"][3]["sites"][1:]:
            self.assertEqual(site["prediction_binding"]["primary"]["recommendation"],dict(status="ABSTAIN_TIE",history=None))
            self.assertIsNone(site["primary"]["recommended_mae"])
        self.assertEqual(p.recommend((.25,.25)),direct.direct_predict((.25,.75),(values(0),values(0),values(0)),(.25,.25))["recommendation"])

    def test_05_foreign_stream_errors(self):
        stream,reader,_,_=prefix(observed=True)
        evidence=json.loads(stream.error_evidence)
        evidence["primary"][0]["stream_id"]="s02"
        stream.error_evidence=b.canonical(evidence)
        self.code("ERROR_PROVENANCE_INVALID",stream.bind_predictions)
        self.assertEqual(len(reader.calls),3)

    def test_06_swapped_errors(self):
        stream,_,_,_=prefix(observed=True)
        evidence=json.loads(stream.error_evidence)
        evidence["primary"].reverse()
        stream.error_evidence=b.canonical(evidence)
        self.code("ERROR_PROVENANCE_INVALID",stream.bind_predictions)

    def test_07_manipulated_error_value(self):
        for arm in ("primary","direct"):
            with self.subTest(arm=arm):
                stream,_,_,_=prefix(observed=True)
                evidence=json.loads(stream.error_evidence)
                evidence[arm][0]["mae"]=999.0
                stream.error_evidence=b.canonical(evidence)
                self.code("ERROR_PROVENANCE_INVALID",stream.bind_predictions)

    def test_08_foreign_freeze_error(self):
        stream,_,_,_=prefix(observed=True)
        evidence=json.loads(stream.error_evidence)
        evidence["direct"][1]["state_digest"]="0"*64
        stream.error_evidence=b.canonical(evidence)
        self.code("ERROR_PROVENANCE_INVALID",stream.bind_predictions)

    def test_09_stale_site_and_missing_errors(self):
        for mode in ("stale","missing"):
            with self.subTest(mode=mode):
                stream,_,_,_=prefix(observed=True)
                if mode=="stale":
                    evidence=json.loads(stream.error_evidence)
                    evidence["primary"][0]["target"]=0
                    stream.error_evidence=b.canonical(evidence)
                else:
                    stream.error_evidence=None
                self.code("ERROR_PROVENANCE_INVALID",stream.bind_predictions)

    def test_10_target_access_before_binding(self):
        stream,reader,_,_=prefix()
        self.code("PREDICTION_BINDING_MISSING",stream.read_next,2)
        self.code("FUTURE_ACCESS_DENIED",stream.read_next,3)
        self.assertEqual(len(reader.calls),2)

    def test_11_prediction_change_before_target(self):
        stream,reader,_,_=prefix()
        stream.bind_predictions()
        binding=json.loads(stream._pending)
        binding["primary"]["recommendation"]=dict(status="RECOMMEND",history="H1")
        reseal(binding,"binding_digest")
        stream._pending=b.canonical(binding)
        self.code("PREDICTION_BINDING_CHANGED",stream.read_next,2)
        self.assertEqual(len(reader.calls),2)

    def test_12_reader_sees_all_committed_arms(self):
        stream,reader,_,_=prefix(observed=True)
        original=stream.reader
        def inspect(source,work):
            bound=json.loads(stream._committed)
            self.assertEqual(set(bound["primary"]["predictions"]),{"H1","H2","PERSIST","LOCAL"})
            self.assertEqual(bound["primary"],bound["direct"])
            self.assertEqual(bound["target"],source["window_ordinal"])
            return original(source,work)
        stream.reader=inspect
        stream.bind_predictions()
        stream.read_next(3)
        self.assertEqual(len(reader.calls),4)

    def test_13_local_fresh_and_order(self):
        a=p.LocalInput(p.PROFILE,values(0),values(.25),values(.375))
        c=p.LocalInput(p.PROFILE,values(.5),values(.25),values(.375))
        self.assertEqual(p.local_fit(a)["beta"],.5)
        self.assertEqual(p.local_fit(c)["beta"],-.5)
        self.assertEqual(p.local_fit(a)["beta"],.5)
        for inp in (a,c):
            first=p.predict((.25,.75),(inp.first,inp.previous,inp.last),(.1,.2))
            second=direct.direct_predict((.25,.75),(inp.first,inp.previous,inp.last),(.1,.2))
            self.assertEqual(b.canonical(first),b.canonical(second))

    def test_14_null_subnormal_and_underflow(self):
        for tiny in (0.0,float.fromhex("0x0.0000000000001p-1022")):
            with self.subTest(tiny=tiny):
                prefix_values=(values(0),values(tiny),values(tiny))
                a=p.predict((.25,.75),prefix_values,(0.0,0.0))
                d=direct.direct_predict((.25,.75),prefix_values,(0.0,0.0))
                self.assertEqual(b.canonical(a),b.canonical(d))
                self.assertTrue(a["local"]["zero_denominator"])
                self.assertEqual(a["local"]["beta"],0.0)
                self.assertEqual(len(a["local"]["product_underflow_indices"]),48 if tiny else 0)

    def test_15_numeric_and_profile_errors(self):
        self.code("PROFILE_INVALID",p.LocalInput,"0"*64,values(0),values(0),values(0))
        for value in (float("inf"),float("nan"),-1.0):
            with self.subTest(value=value):
                self.code("VECTOR_INVALID",p.LocalInput,p.PROFILE,values(value),values(0),values(0))
        self.code("ERROR_VALUES_INVALID",p.recommend,(float("inf"),0.0))

    def test_16_independent_direct_no_primary_helpers(self):
        with patch.object(p,"predict",side_effect=AssertionError("primary prediction forbidden")),\
             patch.object(p,"local_fit",side_effect=AssertionError("primary beta forbidden")),\
             patch.object(p,"recommend",side_effect=AssertionError("primary decision forbidden")),\
             patch.object(p.nw,"score",side_effect=AssertionError("primary score forbidden")):
            output=direct.direct_predict((.25,.75),(values(0),values(.25),values(.375)),(.1,.2))
            scored=direct.direct_score(output,values(.5))
        self.assertEqual(output["local"]["beta"],.5)
        self.assertEqual(scored["scores"]["LOCAL"]["mae"],.0625)

    def test_17_no_source_fields_and_no_clipping(self):
        self.assertEqual([f.name for f in fields(p.LocalInput)],["profile_digest","first","previous","last"])
        out=p.predict((.25,.75),(values(0),values(.25),values(1)),(.1,.2))
        self.assertGreater(out["predictions"]["LOCAL"][0],1.0)
        self.assertEqual(b.canonical(out),b.canonical(direct.direct_predict((.25,.75),(values(0),values(.25),values(1)),(.1,.2))))

    def test_18_identical_prefix_unrelated_labels(self):
        a,_,_,_=prefix("alpha",True)
        c,_,_,_=prefix("beta",True)
        av,cv=json.loads(a.bind_predictions()),json.loads(c.bind_predictions())
        self.assertEqual(av["primary"],cv["primary"])
        self.assertNotEqual(av["prefix_digests"],cv["prefix_digests"])

    def test_19_freeze_mutation_before_reader(self):
        stream,reader,_,frozen=prefix()
        stream.bind_predictions()
        payload=json.loads(frozen.data)
        payload["histories"][0]["frozen_payload"]["alpha"]=.5
        frozen.data=b.canonical(payload)
        self.code("FREEZE_BINDING_CHANGED",stream.read_next,2)
        self.assertEqual(len(reader.calls),2)

    def test_20_reset_lifecycle(self):
        stream,_,work,frozen=prefix(observed=True)
        for k in (3,4):
            stream.bind_predictions()
            stream.read_next(k)
        stream.close()
        self.assertIsNone(stream.error_evidence)
        self.assertEqual(stream._windows,())
        self.code("FUTURE_ACCESS_DENIED",stream.read_next,0)
        plan=neutral_plan()
        fresh=run.PrefixStream(plan["sources"][5:10],work,NeutralReader(),frozen)
        fresh.read_next(0)
        fresh.read_next(1)
        bound=json.loads(fresh.bind_predictions())
        self.assertIsNone(bound["error_evidence"]["primary"])
        self.assertEqual(bound["primary"]["recommendation"]["status"],"ABSTAIN_INSUFFICIENT_PREFIX")
        fresh.abort()

    def test_21_failure_close_and_no_functional_partial(self):
        reader=NeutralReader()
        def fail(source,work):
            if source["window_ordinal"]==2:
                raise p.S2NYPredictionError("NEUTRAL_MATERIALIZATION_FAILURE")
            return reader(source,work)
        fail.carriers=CARRIERS
        record=run.execute(self.plan,fail,"neutral-failure")
        self.assertEqual(record["status"],"NOT_EVALUABLE")
        self.assertEqual(record["failure"]["code"],"NEUTRAL_MATERIALIZATION_FAILURE")
        self.assertEqual(record["failure"]["phase"],"SOURCE_PROCESSING")
        self.assertEqual(len(reader.calls),2)
        self.assertEqual(record["streams"],[])
        self.assertFalse(direct.verify_record(record,self.plan)["evaluation_allowed"])

    def test_22_offline_error_provenance_manipulation(self):
        record=deepcopy(self.record)
        stream=record["streams"][0]
        site=stream["sites"][1]
        site["prediction_binding"]["error_evidence"]["primary"][0]["mae"]=99.0
        reseal(site["prediction_binding"],"binding_digest")
        reseal(site,"site_digest")
        reseal(stream,"stream_digest")
        reseal(record,"record_digest")
        self.code("ERROR_PROVENANCE_INVALID",direct.verify_record,record,self.plan)

    def test_23_missing_or_reordered_evidence(self):
        for mode in ("missing","reordered"):
            with self.subTest(mode=mode):
                record=deepcopy(self.record)
                stream=record["streams"][0]
                if mode=="missing":
                    stream["sites"].pop()
                else:
                    stream["sites"].reverse()
                reseal(stream,"stream_digest")
                reseal(record,"record_digest")
                self.code("STREAM_BINDING_INVALID" if mode=="missing" else "PREFIX_BINDING_INVALID",direct.verify_record,record,self.plan)

    def test_24_next_best_can_lose_controls(self):
        site=deepcopy(self.record["streams"][0]["sites"][1])
        site["prediction_binding"]["primary"]["recommendation"]=dict(status="RECOMMEND",history="H1")
        for a,value in (("H1",.2),("H2",.3),("LOCAL",.1),("PERSIST",0.0)):
            site["primary"]["scores"][a]["mae"]=value
        site["primary"].update(recommended_mae=.2,recommendation_gains=dict(H1=0.0,H2=.1,LOCAL=-.1,PERSIST=-.2))
        row=evaluation.site_result(site,"p02","s01")
        self.assertEqual(row["recommendation_outcome"],"NEXT_BEST")
        self.assertEqual(row["recommendation_outcomes"]["LOCAL"],"LOSS")
        self.assertEqual(row["recommendation_outcomes"]["PERSIST"],"LOSS")

    def test_25_separate_twenty_criteria(self):
        proof=direct.verify_record(self.record,self.plan)
        result=evaluation.evaluate(self.record,proof,b.evaluation_plan(self.plan))
        self.assertEqual(len(result["criteria"]),20)
        self.assertEqual([r["N"] for r in result["blocks"].values()],[4,4,4,8])
        self.assertEqual(result["groups"][3]["D"],0)
        self.assertEqual(result["groups"][3]["status"],"NUTZEN_NICHT_GEPRUEFT")
        self.assertFalse(result["losses_compensated"])

    def test_26_unfulfilled_W_technically_valid(self):
        plan=neutral_plan("still",((.25,)*5,)*6)
        record=run.execute(plan,NeutralReader(),"neutral-all-ties")
        proof=direct.verify_record(record,plan)
        result=evaluation.evaluate(record,proof,b.evaluation_plan(plan))
        self.assertTrue(proof["evaluation_allowed"])
        self.assertTrue(all(g["D"]==0 for g in result["groups"]))
        self.assertEqual(result["blocks"]["W"],dict(N=8,confirmed=0))

    def test_27_work_and_output_limits(self):
        work=p.Work()
        self.code("WORK_LIMIT_EXCEEDED",work.add,"generation_attempts",31)
        with tempfile.TemporaryDirectory() as directory:
            self.code("OUTPUT_SIZE_EXCEEDED",run.atomic,Path(directory)/"big.json",dict(big="x"*2097152),2097152)
        record=deepcopy(self.record)
        record["big"]="x"*2097152
        reseal(record,"record_digest")
        self.code("OUTPUT_SIZE_EXCEEDED",direct.verify_record,record,self.plan)

    def test_28_atomic_no_overwrite_and_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"a.json"
            run.atomic(path,dict(a=1),65536)
            before=path.read_bytes()
            self.code("WRITE_CONFLICT",run.atomic,path,dict(a=2),65536)
            self.assertEqual(path.read_bytes(),before)
        self.code("MAIN_GATE_CLOSED",run.run_main_once,"s2ny-prefix-recommendation-20260909-99")
        self.assertFalse(run.MAIN_GATE)

    def test_29_neutral_actual_adapter_causal_boundary(self):
        plan=neutral_plan("adapter")
        sources=deepcopy(plan["sources"][:5])
        payload_hash=hashlib.sha256(bytes(19200)).hexdigest()
        for source in sources:
            source["pcm_sha256"]=payload_hash
            reseal(source,"source_digest")
        calls=[]
        holder={}
        def generate(source):
            k=source["window_ordinal"]
            if k>=2:
                pending=json.loads(holder["stream"]._committed)
                self.assertEqual(pending["target"],k)
                self.assertEqual(pending["primary"],pending["direct"])
            calls.append(k)
            return bytearray(19200)
        reader=run.nw.AudioReader(plan["profiles"],generate)
        frozen=run.FrozenInputs(plan["freeze_import"])
        work=p.Work()
        stream=run.PrefixStream(sources,work,reader,frozen)
        holder["stream"]=stream
        for k in range(5):
            if k>=2:
                self.code("PREDICTION_BINDING_MISSING",stream.read_next,k)
                self.assertEqual(calls,list(range(k)))
                stream.bind_predictions()
            stream.read_next(k)
        closed=stream.close()
        frozen.release()
        self.assertEqual(calls,list(range(5)))
        self.assertEqual(work.values["analyze_returns"],5)
        self.assertEqual(work.values["nj_returns"],5)
        self.assertTrue(closed["closed"])

    def test_30_full_final_hull_and_evaluation_lock(self):
        record=deepcopy(self.record)
        hashes=run.watched()
        record.update(code_hashes_before=hashes,code_hashes_after=hashes,seal_digest=run.SEAL_DIGEST)
        reseal(record,"record_digest")
        proof=direct.verify_record(record,self.plan)
        result=evaluation.evaluate(record,proof,b.evaluation_plan(self.plan))
        self.assertLessEqual(len(b.canonical(record)),2097152)
        self.assertLessEqual(len(b.canonical(proof)),262144)
        self.assertLessEqual(len(b.canonical(result)),262144)
        run.atomic(run.QUAL_DIR/"neutral-envelope.json",record,2097152)
        proof["evaluation_allowed"]=False
        reseal(proof,"verification_digest")
        self.code("EVALUATION_BEFORE_VERIFICATION",evaluation.evaluate,record,proof,b.evaluation_plan(self.plan))


if __name__=="__main__":
    unittest.main()
