"""One bounded neutral qualification, never real NV source generation."""
from copy import deepcopy
from dataclasses import FrozenInstanceError, fields
import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools import _s2nv_private_prediction as p
from tools import _s2nv_private_prediction_run as run
from tools import _s2nv_private_prediction_verification as direct
from tools import _s2nv_private_prediction_evaluation as evaluation

b = p.b
LEVELS = ((.125,.25,.375,.5,.625),(.125,.25,.375,.25,.125),
          (.125,.25,.375,.375,.375),(.125,.25,.375,0.0,0.0))
CARRIERS = [f"auditory.log_hz.neutral.{i:03d}" for i in range(48)]


def values(x):
    return (float(x),)*48


def reseal(obj,key):
    obj.pop(key,None)
    obj[key] = b.digest(obj)


def neutral_plan(prefix="neutral",levels=LEVELS):
    rows = []
    for s in range(4):
        for k in range(5):
            n = 5*s+k
            rows.append(b.sealed(dict(source_id=f"{prefix}-s{s+1:02d}-w{k:02d}",ordinal=n+1,stream_id=f"s{s+1:02d}",
                window_ordinal=k,window_start_sample=n*4800,window_end_sample=(n+1)*4800,nj_snapshot_index=n*10,
                clock_id="audio.sample",pcm_sha256="a"*64,recipe_digest="b"*64,neutral_half=levels[s][k]),"source_digest"))
    return b.sealed(dict(sources=rows,profiles=b.profile_binding(),environment={"neutral":True}),"execution_digest")


def synthetic_window(source,carriers=CARRIERS):
    # These reduced fixtures are explicitly synthetic, not a receptor result.
    half = list(values(source["neutral_half"]))
    raw = [x*2.0 for x in half]
    state = dict(modality_id="auditory",geometry_id=b.profile_binding()["raw"]["geometry_id"],
        snapshot_index=source["nj_snapshot_index"],window_start_sample=source["window_start_sample"],
        window_end_sample=source["window_end_sample"],carrier_ids=carriers,energy=raw,
        contact="active_energy" if any(x!=0 for x in raw) else "active_zero")
    profiles = b.profile_binding()
    projection = b.sealed(dict(profile_id=profiles["half"]["profile_id"],profile_digest=p.PROFILE,
        geometry_id=profiles["half"]["geometry_id"],source_profile_digest=profiles["raw_profile_digest"],
        source_state_digest=b.digest(state),source_values_digest=b.digest(raw),snapshot_index=source["nj_snapshot_index"],
        clock_id="audio.sample",window_start_tick=source["window_start_sample"],window_end_tick=source["window_end_sample"],
        carrier_ids=carriers,values=half,subnormal_band_indices=[],underflow_band_indices=[]),"projection_digest")
    return b.sealed(dict(source_id=source["source_id"],source_digest=source["source_digest"],pcm_sha256=source["pcm_sha256"],
        payload_checked_before_analysis=True,raw_state=state,raw_state_digest=b.digest(state),projection=projection,
        raw_hex=[x.hex() for x in raw],half_hex=[x.hex() for x in half],
        raw_f64le_sha256=hashlib.sha256(p.bits(raw)).hexdigest(),half_f64le_sha256=hashlib.sha256(p.bits(half)).hexdigest(),
        raw_subnormal_indices=[]),"window_digest")


class NeutralReader:
    carriers = CARRIERS

    def __init__(self):
        self.calls = []

    def __call__(self,source,work):
        self.calls.append(source["source_id"])
        work.phase,work.source_id = "NEUTRAL_WINDOW",source["source_id"]
        for key in ("generation_attempts","payloads_checked","analyze_attempts","analyze_returns","nj_attempts","nj_returns"):
            work.add(key)
        return synthetic_window(source)


def prefix():
    plan,work,reader = neutral_plan(),p.Work(),NeutralReader()
    stream = run.PrefixStream(plan["sources"][:5],work,reader)
    stream.read_next(0)
    stream.read_next(1)
    return stream,reader,work


class PredictionQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = neutral_plan()
        with patch.object(b,"pcm_window",side_effect=AssertionError("NV PCM forbidden")),\
             patch.object(run,"load_presealed",side_effect=AssertionError("real NV plan forbidden")):
            cls.record = run.execute(cls.plan,NeutralReader(),"neutral-fixture")
        if cls.record["status"]!="RECORDING_COMPLETE":
            raise AssertionError(cls.record["failure"])

    def setUp(self):
        for module,name in ((b,"pcm_window"),(run,"load_presealed")):
            guard = patch.object(module,name,side_effect=AssertionError("real NV path forbidden"))
            guard.start()
            self.addCleanup(guard.stop)

    def code(self,code,fn,*args,**kwargs):
        with self.assertRaises(p.S2NVPredictionError) as caught:
            fn(*args,**kwargs)
        self.assertEqual(caught.exception.code,code)

    def test_01_closed_inputs_profile_domain(self):
        self.assertEqual([f.name for f in fields(p.LinearInput)],["half_profile_digest","previous_values","last_values"])
        self.assertEqual([f.name for f in fields(p.PersistInput)],["half_profile_digest","last_values"])
        self.code("PROFILE_INVALID",p.LinearInput,"0"*64,values(0),values(1))
        for bad in (float("inf"),float("nan"),-0.1,1.1):
            with self.subTest(bad=repr(bad)):
                self.code("VECTOR_INVALID",p.PersistInput,p.PROFILE,values(bad))
        self.code("INPUT_TYPE_INVALID",p.linear,{"half_profile_digest":p.PROFILE,"future_values":values(0)})

    def test_02_subtract_before_add(self):
        previous,last = values(1),values(float.fromhex("0x1.0000000000001p-54"))
        inp = p.LinearInput(p.PROFILE,previous,last)
        result = p.linear(inp)
        expected = last[0]+(last[0]-previous[0])
        self.assertEqual([x.hex() for x in result],[expected.hex()]*48)
        with self.assertRaises(FrozenInstanceError):
            inp.last_values = values(0)
        self.assertEqual(inp.last_values,last)

    def test_03_persist_bitcopy_subnormal_and_signed_zero(self):
        original = (-0.0,float.fromhex("0x0.0000000000001p-1022"))+values(.5)[2:]
        result = p.persist(p.PersistInput(p.PROFILE,original))
        self.assertEqual(p.bits(result),p.bits(original))
        self.assertEqual(result[0].hex(),"-0x0.0p+0")

    def test_04_unclipped_predictions_and_error(self):
        for previous,last,target,expected in ((0,1,0,2.0),(1,0,1,-1.0)):
            with self.subTest(expected=expected):
                prediction = p.linear(p.LinearInput(p.PROFILE,values(previous),values(last)))
                self.assertEqual(prediction,values(expected))
                score = p.score(prediction,values(target))
                self.assertEqual(score["mae"],2.0)
                self.assertEqual([r["original_index"] for r in score["terms"]],list(range(48)))

    def test_05_independent_direct_arithmetic(self):
        li,pi = p.LinearInput(p.PROFILE,values(.125),values(.25)),p.PersistInput(p.PROFILE,values(.25))
        expected = dict(LINEAR_TWO_STATE=list(p.linear(li)),PERSIST_LAST=list(p.persist(pi)))
        expected_score = p.score(tuple(expected["LINEAR_TWO_STATE"]),values(.5))
        with patch.object(p,"linear",side_effect=AssertionError("no productive helper")),\
             patch.object(p,"persist",side_effect=AssertionError("no productive helper")),\
             patch.object(p,"score",side_effect=AssertionError("no productive helper")):
            self.assertEqual(direct.direct_predictions(li,pi),expected)
            self.assertEqual(direct.direct_score(expected["LINEAR_TWO_STATE"],values(.5)),expected_score)

    def test_06_early_target_denied_before_reader(self):
        stream,reader,work = prefix()
        before = len(reader.calls)
        self.code("FUTURE_ACCESS_DENIED",stream.read_next,3)
        self.assertEqual(len(reader.calls),before)
        self.code("PREDICTION_BINDING_MISSING",stream.read_next,2)
        self.assertEqual(len(reader.calls),before)

    def test_07_missing_binding_and_duplicate_binding(self):
        stream,reader,work = prefix()
        stream.bind_predictions()
        self.code("BINDING_PHASE_INVALID",stream.bind_predictions)
        stream._pending = None
        self.code("PREDICTION_BINDING_MISSING",stream.read_next,2)
        self.assertEqual(len(reader.calls),2)

    def test_08_resealed_mutation_denied_before_target(self):
        stream,reader,work = prefix()
        binding = stream.bind_predictions()
        with self.assertRaises(FrozenInstanceError):
            binding.data = b"changed"
        changed = json.loads(binding.data)
        changed["primary"]["LINEAR_TWO_STATE"][0] = .9
        reseal(changed,"binding_digest")
        data = b.canonical(changed)
        object.__setattr__(binding,"data",data)
        object.__setattr__(binding,"digest",hashlib.sha256(data).hexdigest())
        self.code("PREDICTION_BINDING_CHANGED",stream.read_next,2)
        self.assertEqual(len(reader.calls),2)

    def test_09_mutation_during_read_is_not_published(self):
        stream,reader,work = prefix()
        binding = stream.bind_predictions()
        def bad(source,budget):
            row = reader(source,budget)
            object.__setattr__(binding,"data",b"changed")
            return row
        stream._reader = bad
        self.code("PREDICTION_BINDING_CHANGED",stream.read_next,2)
        self.assertEqual(work.values["analyze_returns"],3)
        self.assertEqual(work.values["completed_windows"],2)
        self.assertEqual(stream._sites,())

    def test_10_identical_prefix_ignores_admin_ids(self):
        bound = []
        for label in ("neutral-one","neutral-two"):
            work = p.Work()
            stream = run.PrefixStream(neutral_plan(label)["sources"][:5],work,NeutralReader())
            stream.read_next(0)
            stream.read_next(1)
            bound.append(json.loads(stream.bind_predictions().data))
        self.assertNotEqual(bound[0]["prefix_digests"],bound[1]["prefix_digests"])
        self.assertEqual(b.canonical(bound[0]["primary"]),b.canonical(bound[1]["primary"]))
        self.assertEqual(bound[0]["functional_prefix"],bound[1]["functional_prefix"])

    def test_11_actual_prefix_call_order_and_close(self):
        work,reader,events = p.Work(),NeutralReader(),[]
        def observed(source,budget):
            k = source["window_ordinal"]
            if k>=2:
                stream._check_pending()
                self.assertEqual(json.loads(stream._pending.data)["completed_analyses_before"],k)
            events.append((k,budget.values["analyze_returns"]))
            return reader(source,budget)
        stream = run.PrefixStream(self.plan["sources"][:5],work,observed)
        for k in range(5):
            if k>=2:
                stream.bind_predictions()
            stream.read_next(k)
        receipt = stream.close()
        self.assertEqual(events,[(k,k) for k in range(5)])
        self.assertEqual(len(receipt["sites"]),3)
        self.code("CLOSE_INVALID",stream.close)
        self.code("FUTURE_ACCESS_DENIED",stream.read_next,5)

    def test_12_stream_reset_and_complete_work(self):
        self.assertEqual(self.record["work"],p.work_limits())
        for s,stream in enumerate(self.record["streams"]):
            binding = stream["sites"][0]["prediction_binding"]
            self.assertEqual(binding["available_windows"],2)
            self.assertEqual(binding["completed_analyses_before"],s*5+2)
            self.assertEqual(len(binding["prefix_digests"]),2)
            self.assertEqual(binding["functional_prefix"]["previous_values"],list(values(.125)))
        self.code("WORK_LIMIT_EXCEEDED",p.Work().add,"primary_error_terms",1153)

    def test_13_real_neutral_receptor_nj_prefix_adapter(self):
        sources = deepcopy(self.plan["sources"][:5])
        # Constant neutral windows, not any NV oscillator or sealed payload.
        for k,source in enumerate(sources):
            source["neutral_pcm"] = (0.0,.03125,.0625,.0625,.03125)[k]
            payload = bytearray(struct.pack("<f",source["neutral_pcm"]))*4800
            source["pcm_sha256"] = hashlib.sha256(payload).hexdigest()
            del payload
            reseal(source,"source_digest")
        work,order = p.Work(),[]
        def generate(source):
            k = source["window_ordinal"]
            if k>=2:
                stream._check_pending()
            order.append(k)
            return bytearray(struct.pack("<f",source["neutral_pcm"]))*4800
        reader = run.AudioReader(b.profile_binding(),generate)
        stream = run.PrefixStream(sources,work,reader)
        for k in range(5):
            if k>=2:
                stream.bind_predictions()
            stream.read_next(k)
        receipt = stream.close()
        for source,row in zip(sources,receipt["windows"],strict=True):
            direct.verify_window(row,source,b.profile_binding(),reader.carriers)
        self.assertEqual(order,list(range(5)))
        self.assertEqual(work.values["analyze_returns"],5)
        self.assertEqual(work.values["nj_returns"],5)

    def test_14_payload_and_time_fail_before_analysis(self):
        source = deepcopy(self.plan["sources"][0])
        reader = run.AudioReader(b.profile_binding(),lambda src:bytearray(19200))
        work = p.Work()
        with patch.object(reader.receptor,"analyze",side_effect=AssertionError("no analysis")):
            self.code("PCM_HASH_INVALID",reader,source,work)
        self.assertEqual(work.values["analyze_attempts"],0)
        source["window_start_sample"] = 1
        work = p.Work()
        self.code("SOURCE_TIME_INVALID",reader,source,work)
        self.assertEqual(work.values["generation_attempts"],0)

    def test_15_full_offline_verification_and_manipulations(self):
        original = b.canonical(self.record)
        proof = direct.verify_record(self.record,self.plan)
        self.assertEqual(proof["work"],p.verification_limits())
        self.assertFalse(proof["chronology_independently_proven"])
        self.assertEqual(original,b.canonical(self.record))
        for mode,code in (("source","SOURCE_BINDING_INVALID"),("missing","COMPLETE_BINDING_INVALID"),
                          ("prediction","PREDICTION_INVALID")):
            with self.subTest(mode=mode):
                r = deepcopy(self.record)
                if mode=="missing":
                    r["streams"].pop()
                else:
                    st = r["streams"][0]
                    if mode=="source":
                        st["windows"][0]["source_id"] = "tampered"
                        reseal(st["windows"][0],"window_digest")
                    else:
                        site = st["sites"][0]
                        site["prediction_binding"]["primary"]["LINEAR_TWO_STATE"][0] = .9
                        reseal(site["prediction_binding"],"binding_digest")
                        reseal(site,"site_digest")
                    reseal(st,"stream_digest")
                reseal(r,"record_digest")
                self.code(code,direct.verify_record,r,self.plan)

    def test_16_evaluation_gate_and_separate_switch_losses(self):
        ev = b.evaluation_plan(self.plan)
        self.code("EVALUATION_NOT_AUTHORIZED",evaluation.evaluate,self.record,
            b.sealed(dict(status="NOT_EVALUABLE"),"verification_digest"),ev)
        proof = direct.verify_record(self.record,self.plan)
        result = evaluation.evaluate(self.record,proof,ev)
        self.assertEqual(result["primary"],"CONFIRMED")
        self.assertEqual(result["streams"][0]["counts"],dict(WIN=3,TIE=0,LOSS=0))
        for stream in result["streams"][1:]:
            self.assertEqual(stream["sites"][1]["outcome"],"LOSS")
            self.assertEqual(stream["N"],3)
        self.assertIsNone(result["pooled_mean"])

    def test_17_ties_falsify_primary_without_technical_failure(self):
        plan = neutral_plan(levels=((0.0,)*5,)*4)
        record = run.execute(plan,NeutralReader(),"neutral-ties")
        proof = direct.verify_record(record,plan)
        result = evaluation.evaluate(record,proof,b.evaluation_plan(plan))
        self.assertEqual(record["status"],"RECORDING_COMPLETE")
        self.assertEqual(result["primary"],"FALSIFIED")
        self.assertTrue(all(r["counts"]==dict(WIN=0,TIE=3,LOSS=0) for r in result["streams"]))

    def test_18_full_envelope_and_limits(self):
        envelope = deepcopy(self.record)
        envelope["code_hashes_before"] = envelope["code_hashes_after"] = run.watched()
        envelope["seal_digest"] = run.SEAL_DIGEST
        reseal(envelope,"record_digest")
        self.assertLessEqual(len(b.canonical(envelope)),p.MAX_OUTPUT_BYTES)
        b.publish(run.QUAL_DIR/"neutral-envelope.json",envelope,p.MAX_OUTPUT_BYTES)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"too-large.json"
            self.code("OUTPUT_SIZE_EXCEEDED",run.atomic,path,dict(oversize="x"*p.MAX_OUTPUT_BYTES),p.MAX_OUTPUT_BYTES)
            self.assertFalse(path.exists())

    def test_19_neutral_entry_atomic_verification_evaluation(self):
        hashes = {"neutral":"0"*64}
        qualification = b.sealed(dict(run_id=run.QUAL_ID,status="S2NV_PREDICTION_QUALIFIED",passed_tests=20,unittest_calls=1,exit_code=0,
            hashes_before=hashes,hashes_after=hashes),"result_digest")
        actual_read = run.read
        def read_neutral(path,key):
            return qualification if path==run.QUAL_DIR/"result.json" else actual_read(path,key)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            b.publish(root/"evaluation-plan.json",b.evaluation_plan(self.plan),65536)
            with patch.object(run,"OUT_ROOT",root),patch.object(run,"SEAL_DIR",root),\
                 patch.object(run,"watched",return_value=hashes),patch.object(run,"load_presealed",return_value=self.plan),\
                 patch.object(run,"make_reader",return_value=NeutralReader()),patch.object(run,"read",side_effect=read_neutral):
                run.MAIN_GATE = True
                out = run.run_main_once("s2nv-prospective-prediction-20990101-01")
                self.assertFalse(run.MAIN_GATE)
                proof = run.verify_file_once(out)
                self.assertEqual(proof["status"],"S2NV_PREDICTION_VERIFIED")
                result = run.evaluate_file_once(out)
                self.assertEqual(result["primary"],"CONFIRMED")
                with self.assertRaises(FileExistsError):
                    run.verify_file_once(out)
                self.assertEqual(len(list(out.glob("*.pending"))),0)

    def test_20_failure_closure_and_write_conflict(self):
        class FailingReader(NeutralReader):
            def __call__(self,source,work):
                if source["window_ordinal"]==2:
                    work.phase,work.source_id = "PCM_GENERATION",source["source_id"]
                    raise p.S2NVPredictionError("NEUTRAL_GENERATION_FAILURE")
                return super().__call__(source,work)
        record = run.execute(self.plan,FailingReader(),"neutral-failure")
        self.assertEqual(record["failure"]["code"],"NEUTRAL_GENERATION_FAILURE")
        self.assertEqual(record["work"]["completed_windows"],2)
        self.assertEqual(record["streams"],[])
        self.assertIsNone(record["evaluation"])
        proof = direct.verify_record(record,self.plan)
        self.assertEqual(proof["status"],"TECHNICAL_FAILURE_RECORDED")
        self.assertFalse(proof["evaluation_allowed"])
        self.code("MAIN_GATE_CLOSED",run.run_main_once,"s2nv-prospective-prediction-20990101-02")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"result.json"
            run.atomic(path,dict(bound=True),65536)
            self.code("WRITE_CONFLICT",run.atomic,path,dict(bound=False),65536)
            self.assertEqual(json.loads(path.read_bytes()),dict(bound=True))
        self.assertFalse(run.MAIN_GATE)
        self.assertFalse(b.MAIN_GATE)


if __name__=="__main__":
    unittest.main()
