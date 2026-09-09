"""Single bounded neutral NW qualification; sealed corpus generators blocked."""
from copy import deepcopy
from dataclasses import FrozenInstanceError, fields, replace
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
from tools import _s2nw_private_learning_prediction as p
from tools import _s2nw_private_learning_run as run
from tools import _s2nw_private_learning_verification as direct
from tools import _s2nw_private_learning_evaluation as evaluation
from tests.test_s2nv_private_prediction import synthetic_window, CARRIERS

b = p.b
LEVELS = ((.125,.25,.3125,.34375,.359375,.3671875),(.25,.5,.625,.6875,.71875),
          (.25,.5,.625,.5,.4375),(.25,.5,.625,.625,.625),(.25,.5,.625,.125,.125))


def values(x):
    return (float(x),)*48


def reseal(obj,key):
    obj.pop(key,None)
    obj[key] = b.digest(obj)


def neutral_plan(prefix="neutral", levels=LEVELS):
    rows = []
    for s,levels_s in enumerate(levels):
        sid = "l01" if s == 0 else f"s{s:02d}"
        for k,level in enumerate(levels_s):
            n = len(rows)
            rows.append(b.sealed(dict(source_id=f"{prefix}-{sid}-w{k:02d}",ordinal=n+1,stream_id=sid,window_ordinal=k,
                window_start_sample=n*4800,window_end_sample=(n+1)*4800,nj_snapshot_index=n*10,clock_id="audio.sample",
                pcm_sha256="a"*64,recipe_digest="b"*64,neutral_half=level),"source_digest"))
    return b.sealed(dict(sources=rows,profiles=b.profile_binding(),environment={"neutral":True}),"execution_digest")


class NeutralReader:
    carriers = CARRIERS

    def __init__(self):
        self.calls = []

    def __call__(self, source, work):
        self.calls.append(source["source_id"])
        work.phase,work.source_id = "NEUTRAL_WINDOW",source["source_id"]
        for key in ("generation_attempts","payloads_checked","analyze_attempts","analyze_returns","nj_attempts","nj_returns"):
            work.add(key)
        return synthetic_window(source)


def prefix(label="neutral"):
    work,reader,pair = p.Work(),NeutralReader(),run.LearningPair()
    stream = run.PrefixStream(neutral_plan(label)["sources"][:6],work,reader,pair,True)
    stream.read_next(0)
    stream.read_next(1)
    return stream,reader,work,pair


def state_from(obj):
    return p.LearningState(**{k:v for k,v in obj.items() if k not in ("schema","state_digest")})


class LearningQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for module in (b,b.pure,run.nv.b):
            guard = patch.object(module,"pcm_window",side_effect=AssertionError("sealed payload generation forbidden"))
            guard.start()
            cls.addClassCleanup(guard.stop)
        guard = patch.object(run,"load_presealed",side_effect=AssertionError("no corpus binding in neutral execution"))
        guard.start()
        cls.addClassCleanup(guard.stop)
        cls.plan = neutral_plan()
        cls.record = run.execute(cls.plan,NeutralReader(),"neutral-complete")

    def code(self, expected, fn, *args, **kwargs):
        with self.assertRaises(p.S2NWLearningError) as caught:
            fn(*args, **kwargs)
        self.assertEqual(caught.exception.code,expected)

    def test_01_closed_inputs(self):
        self.assertEqual([f.name for f in fields(p.LearnedInput)],
            ["half_profile_digest","alpha","previous_values","last_values"])
        self.code("PROFILE_INVALID",p.LearnedInput,"0"*64,0.0,values(0),values(0))
        for bad in (float("inf"),float("nan"),-0.1,1.1):
            with self.subTest(bad=repr(bad)):
                self.code("VECTOR_INVALID",p.LearnedInput,p.PROFILE,0.0,values(bad),values(0))
        self.code("INPUT_TYPE_INVALID",p.learned,{"recipe":"forbidden"})

    def test_02_exact_initial_state(self):
        a,d = p.initial(),direct.direct_initial()
        self.assertIsNot(a,d)
        self.assertEqual(a.payload(),d.payload())
        self.assertEqual((a.n,a.phase,a.predecessor,a.observation_digest),(0,"TRAIN",None,None))
        self.assertEqual([x.hex() for x in (a.Sxx,a.Sxy,a.alpha)],["0x0.0p+0"]*3)
        self.code("INITIAL_STATE_INVALID",replace,a,alpha=.5)

    def test_03_ordered_update_arithmetic(self):
        state = p.initial()
        before = state.payload()
        previous = tuple(float(i)/128 for i in range(48))
        last = tuple(x+.125 for x in previous)
        target = tuple(x+.0625 for x in last)
        actual,markers = p.update(state,previous,last,target,"a"*64)
        xx,xy = 0.0,0.0
        for i in range(48):
            x,y = last[i]-previous[i],target[i]-last[i]
            xx = xx+(x*x)
            xy = xy+(x*y)
        self.assertEqual((actual.Sxx.hex(),actual.Sxy.hex(),actual.alpha.hex()),(xx.hex(),xy.hex(),(xy/xx).hex()))
        self.assertEqual(state.payload(),before)
        self.assertEqual(actual.predecessor,before["state_digest"])
        self.assertTrue(markers["division_performed"])

    def test_04_null_denominator_and_underflow(self):
        for previous,last,target,underflow in ((0.0,0.0,0.0,False),(0.0,float.fromhex("0x0.0000000000001p-1022"),0.0,True)):
            with self.subTest(underflow=underflow):
                state,mark = p.update(p.initial(),values(previous),values(last),values(target),"a"*64)
                self.assertEqual(state.alpha.hex(),"0x0.0p+0")
                self.assertTrue(mark["zero_denominator"])
                self.assertFalse(mark["division_performed"])
                self.assertEqual(mark["product_underflow_indices"],list(range(48)) if underflow else [])
                ds,dm = direct.direct_update(direct.direct_initial(),values(previous),values(last),values(target),"a"*64)
                self.assertEqual(state.payload(),ds.payload())
                self.assertEqual(mark,dm)

    def test_05_state_forms_phases_immutability(self):
        state = p.initial()
        with self.assertRaises(FrozenInstanceError):
            state.alpha = 1.0
        for kwargs,code in ((dict(profile_digest="x"),"PROFILE_INVALID"),(dict(phase="OTHER"),"STATE_PHASE_INVALID"),
                (dict(Sxx=-1.0),"STATE_VALUES_INVALID"),(dict(alpha=float("inf")),"STATE_VALUES_INVALID"),
                (dict(predecessor="x"),"STATE_CHAIN_INVALID")):
            with self.subTest(kwargs=repr(kwargs)):
                self.code(code,replace,state,**kwargs)

    def test_06_finite_unclipped_predictions(self):
        for previous,last,alpha,expected in ((0,1,3.0,4.0),(1,0,3.0,-3.0)):
            with self.subTest(expected=expected):
                result = p.learned(p.LearnedInput(p.PROFILE,alpha,values(previous),values(last)))
                self.assertEqual(result,values(expected))
                self.assertEqual(p.score(result,values(0))["mae"],abs(expected))
                self.assertEqual(direct.direct_score(result,values(0)),p.score(result,values(0)))
        self.code("COEFFICIENT_INVALID",p.LearnedInput,p.PROFILE,float("inf"),values(0),values(1))
        self.code("VECTOR_INVALID",p.score,values(float("inf")),values(0))

    def test_07_historical_baselines_unchanged(self):
        previous,last = values(1),values(float.fromhex("0x1.0000000000001p-54"))
        outputs = p.predictions(p.LearnedInput(p.PROFILE,.5,previous,last))
        expected = p.historical.linear(p.historical.LinearInput(p.PROFILE,previous,last))
        self.assertEqual(p.bits(tuple(outputs["LINEAR"])),p.bits(expected))
        last = (-0.0,float.fromhex("0x0.0000000000001p-1022"))+values(.5)[2:]
        outputs = p.predictions(p.LearnedInput(p.PROFILE,.5,values(0),last))
        self.assertEqual(p.bits(tuple(outputs["PERSIST"])),p.bits(last))

    def test_08_independent_direct_learner(self):
        inp = p.LearnedInput(p.PROFILE,.5,values(.125),values(.25))
        expected = p.predictions(inp)
        state,mark = p.update(p.initial(),values(.125),values(.25),values(.3125),"a"*64)
        with patch.object(p,"initial",side_effect=AssertionError("no primary initial")),\
             patch.object(p,"update",side_effect=AssertionError("no primary update")),\
             patch.object(p,"learned",side_effect=AssertionError("no primary prediction")),\
             patch.object(p.historical,"linear",side_effect=AssertionError("no primary baseline")):
            actual,dm = direct.direct_update(direct.direct_initial(),values(.125),values(.25),values(.3125),"a"*64)
            self.assertEqual(actual.payload(),state.payload())
            self.assertEqual(dm,mark)
            self.assertEqual(direct.direct_predictions(inp),expected)

    def test_09_early_target_access(self):
        stream,reader,work,pair = prefix()
        self.code("FUTURE_ACCESS_DENIED",stream.read_next,3)
        self.code("PREDICTION_BINDING_MISSING",stream.read_next,2)
        self.assertEqual(len(reader.calls),2)

    def test_10_early_updates(self):
        stream,reader,work,pair = prefix()
        self.code("TARGET_NOT_OBSERVED",stream.update_learning)
        stream.bind_predictions()
        self.code("TARGET_NOT_OBSERVED",stream.update_learning)
        self.assertEqual(pair.primary.n,0)
        self.assertEqual(len(reader.calls),2)

    def test_11_missing_and_modified_prediction_binding(self):
        stream,reader,work,pair = prefix()
        bound = stream.bind_predictions()
        self.code("BINDING_PHASE_INVALID",stream.bind_predictions)
        original = stream._pending
        stream._pending = None
        self.code("PREDICTION_BINDING_MISSING",stream.read_next,2)
        stream._pending = original
        obj = json.loads(bound.data)
        obj["primary"]["LEARNED_DELTA"][0] = .9
        reseal(obj,"binding_digest")
        data = b.canonical(obj)
        object.__setattr__(bound,"data",data)
        object.__setattr__(bound,"digest",hashlib.sha256(data).hexdigest())
        self.code("PREDICTION_BINDING_CHANGED",stream.read_next,2)
        self.assertEqual(len(reader.calls),2)

    def test_12_manipulated_learner_before_target(self):
        stream,reader,work,pair = prefix()
        stream.bind_predictions()
        pair.primary = p.LearningState(p.PROFILE,1,1.0,.5,.5,"TRAIN","a"*64,"b"*64)
        self.code("LEARNING_CHAIN_INVALID",stream.read_next,2)
        self.assertEqual(len(reader.calls),2)

    def test_13_update_only_after_reader_and_score(self):
        stream,reader,work,pair = prefix()
        expected = []
        def observe(source,budget):
            k = source["window_ordinal"]
            stream._check_pending()
            self.code("TARGET_NOT_OBSERVED",stream.update_learning)
            expected.append((k,pair.primary.n))
            return reader(source,budget)
        stream._reader = observe
        for k in range(2,6):
            stream.bind_predictions()
            stream.read_next(k)
            self.assertEqual(pair.primary.n,k-1)
        result = stream.close()
        self.assertEqual(expected,[(2,0),(3,1),(4,2),(5,3)])
        self.assertEqual(len(result["sites"]),4)
        self.code("CLOSE_INVALID",stream.close)

    def test_14_freeze_requires_four_updates(self):
        pair = run.LearningPair()
        self.code("FREEZE_PHASE_INVALID",pair.change_phase,"FROZEN")
        stream,reader,work,pair = prefix()
        stream.bind_predictions()
        stream.read_next(2)
        self.code("FREEZE_PHASE_INVALID",pair.change_phase,"FROZEN")

    def test_15_twelve_frozen_sites_and_prefix_resets(self):
        self.assertEqual(self.record["status"],"RECORDING_COMPLETE")
        p.complete_counts(self.record["work"],p.work_limits())
        frozen = self.record["learning"]["frozen"]
        self.assertEqual(frozen["primary"]["alpha"],.5)
        for s,stream in enumerate(self.record["streams"][1:]):
            first = stream["sites"][0]["prediction_binding"]
            self.assertEqual(first["available_windows"],2)
            self.assertEqual(first["completed_analyses_before"],6+s*5+2)
            self.assertEqual(first["functional_prefix"]["previous_values"],list(values(.25)))
            for site in stream["sites"]:
                self.assertEqual(site["prediction_binding"]["learning_before"],frozen)
                self.assertIsNone(site["learning_update"])

    def test_16_frozen_update_rejected(self):
        pair = run.LearningPair()
        pair.primary = state_from(self.record["learning"]["frozen"]["primary"])
        pair.direct = state_from(self.record["learning"]["frozen"]["direct"])
        pair._expected = pair.payload_bytes()
        stream = run.PrefixStream(self.plan["sources"][6:11],p.Work(),NeutralReader(),pair,False)
        self.code("TEST_UPDATE_FORBIDDEN",stream.update_learning)
        self.code("UPDATE_PHASE_INVALID",p.update,pair.primary,values(0),values(0),values(0),"a"*64)
        self.code("LEARNING_PHASE_INVALID",run.PrefixStream,self.plan["sources"][:6],p.Work(),NeutralReader(),pair,True)

    def test_17_admin_identifiers_not_functional(self):
        bindings = []
        for label in ("neutral-one","neutral-two"):
            stream,reader,work,pair = prefix(label)
            bindings.append(json.loads(stream.bind_predictions().data))
        self.assertNotEqual(bindings[0]["prefix_digests"],bindings[1]["prefix_digests"])
        self.assertEqual(bindings[0]["primary"],bindings[1]["primary"])
        self.assertEqual(bindings[0]["functional_prefix"],bindings[1]["functional_prefix"])

    def test_18_source_hash_and_time_before_analysis(self):
        source = deepcopy(self.plan["sources"][0])
        reader = run.AudioReader(b.profile_binding(),lambda source:bytearray(19200))
        work = p.Work()
        with patch.object(reader.receptor,"analyze",side_effect=AssertionError("no analysis")):
            self.code("PCM_HASH_INVALID",reader,source,work)
        self.assertEqual(work.values["analyze_attempts"],0)
        source["window_start_sample"] = 1
        work = p.Work()
        self.code("SOURCE_TIME_INVALID",reader,source,work)
        self.assertEqual(work.values["generation_attempts"],0)

    def test_19_real_neutral_adapter_causal_path(self):
        sources = deepcopy(self.plan["sources"][:6])
        for k,source in enumerate(sources):
            source["neutral_pcm"] = (0.0,.03125,.046875,.0546875,.05859375,.060546875)[k]
            payload = bytearray(struct.pack("<f",source["neutral_pcm"]))*4800
            source["pcm_sha256"] = hashlib.sha256(payload).hexdigest()
            del payload
            reseal(source,"source_digest")
        work,pair,events = p.Work(),run.LearningPair(),[]
        def generate(source):
            k = source["window_ordinal"]
            if k >= 2:
                stream._check_pending()
                self.assertEqual(pair.primary.n,k-2)
            events.append(k)
            return bytearray(struct.pack("<f",source["neutral_pcm"]))*4800
        reader = run.AudioReader(b.profile_binding(),generate)
        stream = run.PrefixStream(sources,work,reader,pair,True)
        for k in range(6):
            if k >= 2:
                stream.bind_predictions()
            stream.read_next(k)
        receipt = stream.close()
        pair.change_phase("FROZEN")
        for source,row in zip(sources,receipt["windows"],strict=True):
            direct.verify_window(row,source,b.profile_binding(),reader.carriers)
        self.assertEqual(events,list(range(6)))
        self.assertEqual(work.values["analyze_returns"],6)
        self.assertEqual(work.values["nj_returns"],6)
        self.assertEqual(pair.primary.n,4)

    def test_20_complete_offline_verification(self):
        before = b.canonical(self.record)
        proof = direct.verify_record(self.record,self.plan)
        self.assertEqual(proof["work"],p.verification_limits())
        self.assertTrue(proof["baseline_equal"])
        self.assertFalse(proof["chronology_independently_proven"])
        self.assertEqual(before,b.canonical(self.record))

    def test_21_tampered_chains_and_test_update(self):
        for mode,code in (("prior","LEARNING_CHAIN_INVALID"),("update","LEARNING_UPDATE_INVALID"),
                ("frozen","FREEZE_BINDING_INVALID"),("test","TEST_UPDATE_FORBIDDEN")):
            with self.subTest(mode=mode):
                r = deepcopy(self.record)
                stream = r["streams"][1 if mode == "test" else 0]
                site = stream["sites"][0]
                if mode == "prior":
                    prior = site["prediction_binding"]["learning_before"]["primary"]
                    prior["alpha"] = .2
                    reseal(prior,"state_digest")
                    reseal(site["prediction_binding"],"binding_digest")
                elif mode == "update":
                    site["learning_update"]["observation_digest"] = "0"*64
                elif mode == "frozen":
                    r["learning"]["frozen"]["primary"]["predecessor"] = "0"*64
                else:
                    site["learning_update"] = {}
                reseal(site,"site_digest")
                reseal(stream,"stream_digest")
                reseal(r,"record_digest")
                self.code(code,direct.verify_record,r,self.plan)

    def test_22_evaluation_gate_training_and_switch_losses(self):
        ev = b.evaluation_plan(self.plan)
        self.code("EVALUATION_NOT_AUTHORIZED",evaluation.evaluate,self.record,
            b.sealed(dict(status="NOT_EVALUABLE"),"verification_digest"),ev)
        result = evaluation.evaluate(self.record,direct.verify_record(self.record,self.plan),ev)
        self.assertEqual(result["primary"],"CONFIRMED")
        self.assertEqual(result["streams"][0]["N_per_baseline"],4)
        self.assertEqual(result["streams"][0]["phase"],"TRAIN")
        for stream in result["streams"][2:]:
            self.assertEqual(stream["sites"][1]["outcomes"]["PERSIST"],"LOSS")
        self.assertIsNone(result["pooled_mean"])
        self.assertFalse(result["training_replaces_transfer"])
        self.assertEqual(len(result["criteria"]),9)

    def test_23_zero_learning_is_valid_negative(self):
        plan = neutral_plan(levels=((0.0,)*6,)+((0.0,)*5,)*4)
        record = run.execute(plan,NeutralReader(),"neutral-null")
        proof = direct.verify_record(record,plan)
        result = evaluation.evaluate(record,proof,b.evaluation_plan(plan))
        self.assertEqual(record["status"],"RECORDING_COMPLETE")
        self.assertEqual(record["work"]["primary_update_divisions"],0)
        self.assertEqual(proof["work"]["update_divisions"],0)
        self.assertEqual(result["primary"],"FALSIFIED")
        self.assertFalse(result["informative_learning_state"])
        self.assertTrue(all(site["outcomes"] == dict(PERSIST="TIE",LINEAR="TIE") for st in result["streams"] for site in st["sites"]))

    def test_24_outcomes_and_invalid_phase(self):
        self.assertEqual([evaluation.outcome(x) for x in (1.0,0.0,-1.0)],["WIN","TIE","LOSS"])
        state = state_from(self.record["learning"]["closed"]["primary"])
        self.code("UPDATE_PHASE_INVALID",p.update,state,values(0),values(0),values(0),"a"*64)
        self.code("FREEZE_PHASE_INVALID",p.transition,state,"FROZEN")

    def test_25_full_envelope_and_limits(self):
        envelope = deepcopy(self.record)
        envelope["code_hashes_before"] = envelope["code_hashes_after"] = run.watched()
        envelope["seal_digest"] = run.SEAL_DIGEST
        reseal(envelope,"record_digest")
        self.assertLessEqual(len(b.canonical(envelope)),p.MAX_OUTPUT_BYTES)
        b.publish(run.QUAL_DIR/"neutral-envelope.json",envelope,p.MAX_OUTPUT_BYTES)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"large.json"
            self.code("OUTPUT_SIZE_EXCEEDED",run.atomic,path,dict(oversize="x"*p.MAX_OUTPUT_BYTES),p.MAX_OUTPUT_BYTES)
            self.assertFalse(path.exists())
        self.code("WORK_LIMIT_EXCEEDED",p.Work().add,"primary_updates",5)

    def test_26_missing_source_and_prediction_corruption(self):
        for mode,code in (("missing","COMPLETE_BINDING_INVALID"),("source","SOURCE_BINDING_INVALID"),("prediction","PREDICTION_INVALID")):
            with self.subTest(mode=mode):
                r = deepcopy(self.record)
                if mode == "missing":
                    r["streams"].pop()
                else:
                    st = r["streams"][0]
                    if mode == "source":
                        st["windows"][0]["source_id"] = "other"
                        reseal(st["windows"][0],"window_digest")
                    else:
                        site = st["sites"][0]
                        site["prediction_binding"]["primary"]["LEARNED_DELTA"][0] = .9
                        reseal(site["prediction_binding"],"binding_digest")
                        reseal(site,"site_digest")
                    reseal(st,"stream_digest")
                reseal(r,"record_digest")
                self.code(code,direct.verify_record,r,self.plan)

    def test_27_neutral_entry_and_once_claims(self):
        hashes = {"neutral":"0"*64}
        qualification = b.sealed(dict(run_id=run.QUAL_ID,status="S2NW_LEARNING_QUALIFIED",passed_tests=28,unittest_calls=1,exit_code=0,
            hashes_before=hashes,hashes_after=hashes),"result_digest")
        actual_read = run.read
        def read_neutral(path,key):
            return qualification if path == run.QUAL_DIR/"result.json" else actual_read(path,key)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            b.publish(root/"evaluation-plan.json",b.evaluation_plan(self.plan),65536)
            with patch.object(run,"OUT_ROOT",root),patch.object(run,"SEAL_DIR",root),patch.object(run,"watched",return_value=hashes),\
                 patch.object(run,"load_presealed",return_value=self.plan),patch.object(run,"make_reader",return_value=NeutralReader()),\
                 patch.object(run,"read",side_effect=read_neutral):
                try:
                    run.MAIN_GATE = True
                    out = run.run_main_once("s2nw-learned-prediction-20990101-01")
                finally:
                    run.MAIN_GATE = False
                proof = run.verify_file_once(out)
                self.assertEqual(proof["status"],"S2NW_LEARNING_VERIFIED")
                result = run.evaluate_file_once(out)
                self.assertEqual(result["primary"],"CONFIRMED")
                with self.assertRaises(FileExistsError):
                    run.verify_file_once(out)
                self.assertFalse(list(out.glob("*.pending")))

    def test_28_failure_closure_and_write_conflict(self):
        class FailingReader(NeutralReader):
            def __call__(self,source,work):
                if source["window_ordinal"] == 2:
                    work.phase,work.source_id = "PCM_GENERATION",source["source_id"]
                    raise p.S2NWLearningError("NEUTRAL_GENERATION_FAILURE")
                return super().__call__(source,work)
        r = run.execute(self.plan,FailingReader(),"neutral-failure")
        self.assertEqual(r["failure"]["code"],"NEUTRAL_GENERATION_FAILURE")
        self.assertEqual(r["work"]["primary_updates"],0)
        self.assertEqual(r["streams"],[])
        self.assertIsNone(r["learning"])
        self.assertIsNone(r["evaluation"])
        self.assertFalse(direct.verify_record(r,self.plan)["evaluation_allowed"])
        self.code("MAIN_GATE_CLOSED",run.run_main_once,"s2nw-learned-prediction-20990101-02")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"result.json"
            run.atomic(path,dict(bound=True),65536)
            self.code("WRITE_CONFLICT",run.atomic,path,dict(bound=False),65536)
        self.assertFalse(run.MAIN_GATE)
        self.assertFalse(b.MAIN_GATE)
        self.assertFalse(run.nv.MAIN_GATE)


if __name__ == "__main__":
    unittest.main()
