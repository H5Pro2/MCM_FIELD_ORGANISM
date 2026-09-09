"""One neutral NX qualification; no sealed NX payloads or real history."""
from copy import deepcopy
from dataclasses import fields, replace
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
from tools import _s2nx_private_learning_prediction as p
from tools import _s2nx_private_learning_run as run
from tools import _s2nx_private_learning_verification as direct
from tools import _s2nx_private_learning_evaluation as evaluation
from tests.test_s2nv_private_prediction import synthetic_window, CARRIERS, reseal

b = p.b
LEVELS = ((.125,.25,.28125,.2890625,.291015625,.29150390625),
    (.125,.25,.34375,.4140625,.466796875,.50634765625),
    (.25,.5,.5625,.578125,.58203125), (.25,.5,.6875,.828125,.93359375),
    (.25,.5,.5625,.5,.484375), (.25,.5,.6875,.125,.125))


def values(x):
    return (float(x),)*48


def neutral_plan(prefix="neutral", levels=LEVELS):
    rows = []
    for s, seq in enumerate(levels):
        sid = f"l{s+1:02d}" if s < 2 else f"s{s-1:02d}"
        for k, level in enumerate(seq):
            n = len(rows)
            rows.append(b.sealed(dict(source_id=f"{prefix}-{sid}-w{k:02d}", ordinal=n+1, stream_id=sid, window_ordinal=k,
                window_start_sample=n*4800, window_end_sample=(n+1)*4800, nj_snapshot_index=n*10, clock_id="audio.sample",
                pcm_sha256="a"*64, recipe_digest="b"*64, neutral_half=level), "source_digest"))
    return b.sealed(dict(sources=rows, profiles=b.profile_binding(), environment={"neutral":True}), "execution_digest")


class NeutralReader:
    carriers = CARRIERS

    def __init__(self):
        self.calls = []

    def __call__(self, source, work):
        self.calls.append(source["source_id"])
        work.phase, work.source_id = "NEUTRAL_WINDOW", source["source_id"]
        for key in ("generation_attempts", "payloads_checked", "analyze_attempts", "analyze_returns", "nj_attempts", "nj_returns"):
            work.add(key)
        return synthetic_window(source)


def prefix(label="neutral"):
    plan, work, reader = neutral_plan(label), p.Work(), NeutralReader()
    histories = run.Histories(plan["sources"])
    stream = run.PrefixStream(plan["sources"][:6], work, reader, histories, "H1")
    stream.read_next(0)
    stream.read_next(1)
    return stream, reader, work, histories


def restore_histories(plan, record):
    histories = run.Histories(plan["sources"])
    for h in p.HISTORIES:
        pair = histories.pairs[h]
        for a in ("primary", "direct"):
            obj = record["learning"]["frozen"][h]["states"][a]
            setattr(pair, a, p.nw.LearningState(**{k:v for k,v in obj.items() if k not in ("schema", "state_digest")}))
        pair._expected = pair.payload_bytes()
        histories.freezes[h] = pair.bound_payload()
    histories._frozen_bytes = b.canonical(histories.freezes)
    return histories


class LearningQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for module in (b, b.pure, run.nw.b, run.nw.nv.b):
            guard = patch.object(module, "pcm_window", side_effect=AssertionError("sealed payload forbidden"))
            guard.start()
            cls.addClassCleanup(guard.stop)
        guard = patch.object(run, "load_presealed", side_effect=AssertionError("no real NX execution"))
        guard.start()
        cls.addClassCleanup(guard.stop)
        cls.plan = neutral_plan()
        cls.reader = NeutralReader()
        cls.record = run.execute(cls.plan, cls.reader, "neutral-crossed")

    def code(self, code, fn, *args, error=p.S2NXLearningError, **kwargs):
        with self.assertRaises(error) as caught:
            fn(*args, **kwargs)
        self.assertEqual(caught.exception.code, code)

    def test_01_two_own_null_states(self):
        histories = run.Histories(self.plan["sources"])
        states = [getattr(histories.pairs[h], a) for h in p.HISTORIES for a in ("primary", "direct")]
        self.assertEqual(len({id(x) for x in states}), 4)
        self.assertTrue(all(s.payload() == states[0].payload() for s in states))
        self.assertEqual([states[0].Sxx.hex(), states[0].Sxy.hex(), states[0].alpha.hex()], ["0x0.0p+0"]*3)
        self.assertNotEqual(histories.pairs["H1"].binding, histories.pairs["H2"].binding)

    def test_02_foreign_history_transitions(self):
        histories = run.Histories(self.plan["sources"])
        self.code("HISTORY_BINDING_INVALID", run.PrefixStream, self.plan["sources"][6:12], p.Work(), NeutralReader(), histories, "H1")
        self.assertEqual(histories.pairs["H1"].primary.n, 0)

    def test_03_swapped_owners_and_states(self):
        for mode in ("owner", "binding", "state"):
            with self.subTest(mode=mode):
                stream, reader, work, histories = prefix()
                stream.bind_predictions()
                if mode == "owner":
                    histories.pairs["H1"], histories.pairs["H2"] = histories.pairs["H2"], histories.pairs["H1"]
                    code = "HISTORY_BINDING_INVALID"
                elif mode == "binding":
                    histories.pairs["H1"].binding = histories.pairs["H2"].binding
                    code = "HISTORY_BINDING_INVALID"
                else:
                    histories.pairs["H1"].primary = p.nw.LearningState(p.PROFILE,1,1.0,.5,.5,"TRAIN","a"*64,"b"*64)
                    code = "LEARNING_CHAIN_INVALID"
                self.code(code, stream.read_next, 2)
                self.assertEqual(len(reader.calls), 2)

    def test_04_exact_nw_update_order(self):
        previous = tuple(float(i)/128 for i in range(48))
        last = tuple(x+.125 for x in previous)
        target = tuple(x+.03125 for x in last)
        state, marker = p.nw.update(p.nw.initial(), previous, last, target, "a"*64)
        xx, xy = 0.0, 0.0
        for i in range(48):
            x, y = last[i]-previous[i], target[i]-last[i]
            xx = xx+(x*x)
            xy = xy+(x*y)
        self.assertEqual((state.Sxx.hex(),state.Sxy.hex(),state.alpha.hex()), (xx.hex(),xy.hex(),(xy/xx).hex()))
        expected, mark = direct.nw.direct_update(direct.nw.direct_initial(), previous,last,target,"a"*64)
        self.assertEqual(state.payload(), expected.payload())
        self.assertEqual(marker, mark)

    def test_05_future_and_missing_binding(self):
        stream, reader, work, histories = prefix()
        self.code("FUTURE_ACCESS_DENIED", stream.read_next, 3)
        self.code("PREDICTION_BINDING_MISSING", stream.read_next, 2)
        self.assertEqual(len(reader.calls), 2)

    def test_06_updates_before_observation(self):
        stream, reader, work, histories = prefix()
        self.code("TARGET_NOT_OBSERVED", stream.update_learning)
        stream.bind_predictions()
        self.code("TARGET_NOT_OBSERVED", stream.update_learning)
        self.assertEqual(histories.pairs["H1"].primary.n, 0)

    def test_07_prediction_change_and_missing_direct_arm(self):
        for mode in ("change", "remove_direct"):
            with self.subTest(mode=mode):
                stream, reader, work, histories = prefix()
                bound = stream.bind_predictions()
                obj = json.loads(bound.data)
                if mode == "change":
                    obj["primary"]["H1"][0] = .9
                else:
                    obj.pop("direct")
                reseal(obj, "binding_digest")
                data = b.canonical(obj)
                object.__setattr__(bound, "data", data)
                object.__setattr__(bound, "digest", hashlib.sha256(data).hexdigest())
                self.code("PREDICTION_BINDING_CHANGED", stream.read_next, 2)
                self.assertEqual(len(reader.calls), 2)

    def test_08_scores_before_each_update(self):
        stream, reader, work, histories = prefix()
        seen = []
        actual = p.nw.update
        def update(state, previous, last, target, observation):
            self.assertEqual(work.values["analyze_returns"], state.n+3)
            self.assertEqual(work.values["primary_mae_sums"], (state.n+1)*4)
            self.assertEqual(work.values["direct_mae_sums"], (state.n+1)*4)
            self.assertEqual(work.phase, "LEARNING_UPDATE")
            seen.append(state.n)
            return actual(state, previous, last, target, observation)
        def observe(source, budget):
            stream._check_pending()
            self.code("TARGET_NOT_OBSERVED", stream.update_learning)
            return reader(source, budget)
        stream._reader = observe
        with patch.object(p.nw, "update", side_effect=update):
            for k in range(2, 6):
                stream.bind_predictions()
                stream.read_next(k)
        self.assertEqual(seen, [0,1,2,3])
        self.assertEqual(histories.pairs["H2"].primary.n, 0)
        self.assertEqual(len(stream.close()["sites"]), 4)

    def test_09_score_failure_prevents_update(self):
        stream, reader, work, histories = prefix()
        stream.bind_predictions()
        with patch.object(p.nw, "score", side_effect=p.S2NXLearningError("NEUTRAL_SCORE_FAILURE")):
            self.code("NEUTRAL_SCORE_FAILURE", stream.read_next, 2)
        self.assertEqual(histories.pairs["H1"].primary.n, 0)
        self.code("TARGET_NOT_OBSERVED", stream.update_learning)
        stream.abort()

    def test_10_both_freezes_before_first_test(self):
        histories = run.Histories(self.plan["sources"])
        self.code("FREEZE_BINDING_MISSING", run.PrefixStream, self.plan["sources"][12:17], p.Work(), NeutralReader(), histories)
        self.code("FREEZE_PHASE_INVALID", histories.freeze, "H1", error=p.nw.S2NWLearningError)
        self.code("FREEZE_BINDING_MISSING", run.PrefixStream, self.plan["sources"][6:12], p.Work(), NeutralReader(), histories, "H2")
        frozen = restore_histories(self.plan, self.record)
        del frozen.freezes["H2"]
        self.code("FREEZE_BINDING_MISSING", run.PrefixStream, self.plan["sources"][12:17], p.Work(), NeutralReader(), frozen)

    def test_11_twelve_sites_identical_frozen_inputs(self):
        self.assertEqual(self.record["status"], "RECORDING_COMPLETE", self.record.get("failure"))
        self.assertEqual(len(self.reader.calls), 32)
        self.assertEqual(len(set(self.reader.calls)), 32)
        frozen = self.record["learning"]["frozen"]
        self.assertEqual([frozen[h]["states"]["primary"]["alpha"] for h in p.HISTORIES], [.25,.75])
        n = 0
        for s, stream in enumerate(self.record["streams"][2:]):
            for k, site in enumerate(stream["sites"]):
                binding = site["prediction_binding"]
                self.assertEqual(binding["learning_before"], frozen)
                self.assertEqual(binding["active_histories"], ["H1","H2"])
                self.assertEqual(binding["completed_analyses_before"], 12+s*5+k+2)
                self.assertIsNone(site["learning_update"])
                self.assertEqual(set(binding["primary"]), {"H1","H2","PERSIST","LINEAR","FIXED_HALF"})
                n += 1
            self.assertEqual(stream["sites"][0]["prediction_binding"]["functional_prefix"]["previous_values"], list(values(.25)))
        self.assertEqual(n, 12)

    def test_12_no_test_updates_or_freeze_mutation(self):
        histories = restore_histories(self.plan, self.record)
        stream = run.PrefixStream(self.plan["sources"][12:17], p.Work(), NeutralReader(), histories)
        self.code("TEST_UPDATE_FORBIDDEN", stream.update_learning)
        self.code("UPDATE_PHASE_INVALID", p.nw.update, histories.pairs["H1"].primary, values(0),values(0),values(0),"a"*64, error=p.nw.S2NWLearningError)
        histories.freezes["H1"]["states"]["primary"]["alpha"] = .5
        self.code("FREEZE_BINDING_MISSING", stream.read_next, 0)

    def test_13_admin_ids_not_functional(self):
        bindings = []
        for name in ("neutral-one", "neutral-two"):
            stream, reader, work, histories = prefix(name)
            bindings.append(json.loads(stream.bind_predictions().data))
        self.assertEqual(bindings[0]["primary"], bindings[1]["primary"])
        self.assertEqual(bindings[0]["functional_prefix"], bindings[1]["functional_prefix"])
        self.assertNotEqual(bindings[0]["learning_before"], bindings[1]["learning_before"])
        self.assertEqual([f.name for f in fields(p.nw.LearnedInput)], ["half_profile_digest","alpha","previous_values","last_values"])
        self.code("INPUT_TYPE_INVALID", p.nw.learned, {"recipe":"forbidden"}, error=p.nw.S2NWLearningError)

    def test_14_fixed_half_historical_controls(self):
        previous = values(1)
        last = (-0.0,float.fromhex("0x0.0000000000001p-1022"))+values(.5)[2:]
        learned, controls = p.predict((.25,.75), previous, last)
        self.assertEqual(p.bits(tuple(controls["PERSIST"])), p.bits(last))
        expected = p.nw.historical.linear(p.nw.historical.LinearInput(p.PROFILE,previous,last))
        self.assertEqual(p.bits(tuple(controls["LINEAR"])), p.bits(expected))
        expected = tuple(last[i]+(.5*(last[i]-previous[i])) for i in range(48))
        self.assertEqual(p.bits(tuple(controls["FIXED_HALF"])), p.bits(expected))
        self.assertEqual(p.predict((.25,),previous,last)[1], controls)

    def test_15_independent_direct_arithmetic(self):
        inp = (values(.125),values(.25))
        expected = p.predict((.25,.75), *inp)
        state, marker = p.nw.update(p.nw.initial(), *inp, values(.34375), "b"*64)
        with patch.object(p.nw, "initial", side_effect=AssertionError("primary initial")),\
             patch.object(p.nw, "update", side_effect=AssertionError("primary update")),\
             patch.object(p.nw, "learned", side_effect=AssertionError("primary predict")),\
             patch.object(p.nw.historical, "linear", side_effect=AssertionError("primary linear")),\
             patch.object(p, "predict", side_effect=AssertionError("primary NX")):
            actual, mark = direct.nw.direct_update(direct.nw.direct_initial(), *inp, values(.34375), "b"*64)
            self.assertEqual(actual.payload(), state.payload())
            self.assertEqual(mark, marker)
            self.assertEqual(direct.direct_predict((.25,.75), *inp), expected)

    def test_16_null_subnormal_and_nonfinite(self):
        for x, y, underflow in ((0.0,0.0,False),(float.fromhex("0x0.0000000000001p-1022"),float.fromhex("0x0.0000000000002p-1022"),True)):
            with self.subTest(underflow=underflow):
                state, marker = p.nw.update(p.nw.initial(), values(0),values(x),values(y),"a"*64)
                self.assertTrue(marker["zero_denominator"])
                self.assertEqual(state.alpha,0.0)
                self.assertEqual(marker["product_underflow_indices"],list(range(48)) if underflow else [])
        for bad in (float("inf"),float("nan")):
            with self.subTest(bad=repr(bad)):
                self.code("COEFFICIENT_INVALID",p.predict,(bad,),values(0),values(1),error=p.nw.S2NWLearningError)
                self.code("VECTOR_INVALID",p.predict,(.5,),values(bad),values(1),error=p.nw.S2NWLearningError)

    def test_17_unclipped_predictions(self):
        predicted, _ = p.predict((3.0,),values(0),values(1))
        self.assertEqual(predicted,[list(values(4))])
        self.assertEqual(p.nw.score(tuple(predicted[0]),values(0))["mae"],4.0)
        predicted, _ = p.predict((3.0,),values(1),values(0))
        self.assertEqual(predicted,[list(values(-3))])

    def test_18_complete_independent_verification(self):
        before = b.canonical(self.record)
        proof = direct.verify_record(self.record,self.plan)
        self.assertEqual(proof["work"],p.verification_limits())
        self.assertTrue(proof["baseline_equal"])
        self.assertFalse(proof["chronology_independently_proven"])
        self.assertEqual(before,b.canonical(self.record))
        self.__class__.proof = proof

    def test_19_tampered_history_and_freeze(self):
        for mode, code in (("history","LEARNING_CHAIN_INVALID"),("update","LEARNING_UPDATE_INVALID"),("freeze","FREEZE_BINDING_INVALID"),("test","TEST_UPDATE_FORBIDDEN")):
            with self.subTest(mode=mode):
                r = deepcopy(self.record)
                st = r["streams"][2 if mode == "test" else 1]
                site = st["sites"][0]
                if mode == "history":
                    site["prediction_binding"]["learning_before"]["H2"]["binding"]["history"] = "H1"
                    reseal(site["prediction_binding"],"binding_digest")
                elif mode == "update":
                    site["learning_update"]["history"] = "H1"
                elif mode == "freeze":
                    r["learning"]["frozen"]["H2"] = r["learning"]["frozen"]["H1"]
                else:
                    site["learning_update"] = {}
                reseal(site,"site_digest")
                reseal(st,"stream_digest")
                reseal(r,"record_digest")
                self.code(code,direct.verify_record,r,self.plan)

    def test_20_full_twenty_eight_evaluation(self):
        result = evaluation.evaluate(self.record,self.proof,b.evaluation_plan(self.plan))
        self.assertEqual(result["primary"],"CONFIRMED")
        self.assertEqual(len(result["criteria"]),28)
        self.assertEqual([sum(x["check_id"].startswith(k) for x in result["criteria"]) for k in ("K","F","B","W")],[6,6,12,4])
        self.assertEqual(result["work"],dict(outcome_classifications=108,training_outcome_classifications=24,strict_conditions=28))
        self.assertTrue(all(st["phase"]=="TRAIN" for st in result["streams"][:2]))
        self.assertIsNone(result["pooled_mean"])
        self.assertFalse(result["losses_compensated"])
        self.__class__.evaluated = result

    def test_21_equal_uninformative_fits_are_valid(self):
        plan = neutral_plan(levels=((0.0,)*6,)*2+((0.0,)*5,)*4)
        record = run.execute(plan,NeutralReader(),"neutral-null")
        proof = direct.verify_record(record,plan)
        result = evaluation.evaluate(record,proof,b.evaluation_plan(plan))
        self.assertEqual(record["status"],"RECORDING_COMPLETE")
        self.assertEqual(record["work"]["primary_update_divisions"],0)
        self.assertEqual(proof["work"]["update_divisions"],0)
        self.assertEqual(result["primary"],"FALSIFIED")
        self.assertFalse(result["actual_alphas_different"])
        self.assertFalse(any(result["informative_learning_states"].values()))
        self.assertTrue(all(not x["passed"] for x in result["criteria"]))

    def test_22_equal_informative_fits_and_switch_losses(self):
        plan = neutral_plan(levels=(LEVELS[0],LEVELS[0])+LEVELS[2:])
        record = run.execute(plan,NeutralReader(),"neutral-equal")
        result = evaluation.evaluate(record,direct.verify_record(record,plan),b.evaluation_plan(plan))
        self.assertTrue(all(result["informative_learning_states"].values()))
        self.assertEqual(result["blocks"]["K"],"FALSIFIED")
        self.assertFalse(result["actual_alphas_different"])
        self.assertEqual(result["streams"][4]["sites"][1]["outcomes"]["H1"]["PERSIST"],"LOSS")
        self.assertEqual(result["streams"][5]["sites"][1]["outcomes"]["H2"]["PERSIST"],"LOSS")

    def test_23_eval_gate_and_criteria_binding(self):
        ev = b.evaluation_plan(self.plan)
        self.code("EVALUATION_NOT_AUTHORIZED",evaluation.evaluate,self.record,b.sealed(dict(status="NOT_EVALUABLE"),"verification_digest"),ev)
        ev["criteria"].pop()
        reseal(ev,"evaluation_digest")
        self.code("EVALUATION_BINDING_INVALID",evaluation.evaluate,self.record,self.proof,ev)
        self.assertEqual([evaluation.outcome(x) for x in (1.,0.,-1.)],["WIN","TIE","LOSS"])

    def test_24_missing_sources_and_corrupted_prediction(self):
        for mode, code in (("missing","COMPLETE_BINDING_INVALID"),("source","SOURCE_BINDING_INVALID"),("prediction","PREDICTION_INVALID")):
            with self.subTest(mode=mode):
                r = deepcopy(self.record)
                if mode == "missing":
                    r["streams"].pop()
                else:
                    st = r["streams"][0]
                    if mode == "source":
                        st["windows"][0]["source_id"] = "foreign"
                        reseal(st["windows"][0],"window_digest")
                    else:
                        site = st["sites"][0]
                        site["prediction_binding"]["primary"]["FIXED_HALF"][0] = .9
                        reseal(site["prediction_binding"],"binding_digest")
                        reseal(site,"site_digest")
                    reseal(st,"stream_digest")
                reseal(r,"record_digest")
                self.code(code,direct.verify_record,r,self.plan,error=p.nw.S2NWLearningError if mode=="source" else p.S2NXLearningError)

    def test_25_full_envelope_and_work_caps(self):
        envelope = deepcopy(self.record)
        envelope["code_hashes_before"] = envelope["code_hashes_after"] = run.watched()
        envelope["seal_digest"] = run.SEAL_DIGEST
        reseal(envelope,"record_digest")
        self.assertLessEqual(len(b.canonical(envelope)),p.MAX_OUTPUT_BYTES)
        b.publish(run.QUAL_DIR/"neutral-envelope.json",envelope,p.MAX_OUTPUT_BYTES)
        self.assertLessEqual(len(b.canonical(self.evaluated)),262144)
        self.assertLessEqual(len(b.canonical(self.proof)),262144)
        self.code("WORK_LIMIT_EXCEEDED",p.Work().add,"primary_updates",9)
        self.code("WORK_LIMIT_EXCEEDED",p.Work().add,"analyze_returns",33)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"oversize.json"
            self.code("OUTPUT_SIZE_EXCEEDED",run.atomic,path,dict(large="x"*p.MAX_OUTPUT_BYTES),p.MAX_OUTPUT_BYTES)
            self.assertFalse(path.exists())

    def test_26_actual_neutral_reader_hash_and_time(self):
        source = deepcopy(self.plan["sources"][0])
        reader = run.AudioReader(b.profile_binding(),lambda source:bytearray(19200))
        work = p.Work()
        with patch.object(reader.receptor,"analyze",side_effect=AssertionError("no analysis")):
            self.code("PCM_HASH_INVALID",reader,source,work,error=p.nw.S2NWLearningError)
        self.assertEqual(work.values["analyze_attempts"],0)
        source["window_start_sample"] = 1
        work = p.Work()
        self.code("SOURCE_TIME_INVALID",reader,source,work,error=p.nw.S2NWLearningError)
        self.assertEqual(work.values["generation_attempts"],0)

    def test_27_real_neutral_adapter_prefix_binding(self):
        sources = deepcopy(self.plan["sources"])
        for k, source in enumerate(sources[:6]):
            source["neutral_pcm"] = (0.0,.03125,.046875,.0546875,.05859375,.060546875)[k]
            payload = bytearray(struct.pack("<f",source["neutral_pcm"]))*4800
            source["pcm_sha256"] = hashlib.sha256(payload).hexdigest()
            del payload
            reseal(source,"source_digest")
        work, histories, events = p.Work(),run.Histories(sources),[]
        def generate(source):
            k = source["window_ordinal"]
            if k >= 2:
                stream._check_pending()
                self.assertEqual(histories.pairs["H1"].primary.n,k-2)
            events.append(k)
            return bytearray(struct.pack("<f",source["neutral_pcm"]))*4800
        reader = run.AudioReader(b.profile_binding(),generate)
        stream = run.PrefixStream(sources[:6],work,reader,histories,"H1")
        for k in range(6):
            if k >= 2:
                stream.bind_predictions()
            stream.read_next(k)
        record = stream.close()
        histories.freeze("H1")
        for source, row in zip(sources[:6],record["windows"],strict=True):
            direct.nw.verify_window(row,source,b.profile_binding(),reader.carriers)
        self.assertEqual(events,list(range(6)))
        self.assertEqual(work.values["analyze_returns"],6)
        self.assertEqual(work.values["nj_returns"],6)
        histories.release()

    def test_28_failure_closure_releases_both(self):
        owners = []
        actual = run.Histories
        def histories(sources):
            value = actual(sources)
            owners.extend(value.pairs.values())
            return value
        class FailingReader(NeutralReader):
            def __call__(self,source,work):
                if source["ordinal"] == 9:
                    work.phase, work.source_id = "PCM_GENERATION",source["source_id"]
                    raise p.S2NXLearningError("NEUTRAL_GENERATION_FAILURE")
                return super().__call__(source,work)
        with patch.object(run,"Histories",side_effect=histories):
            r = run.execute(self.plan,FailingReader(),"neutral-failure")
        self.assertEqual(r["failure"]["code"],"NEUTRAL_GENERATION_FAILURE")
        self.assertEqual(r["work"]["primary_updates"],4)
        self.assertEqual(r["streams"],[])
        self.assertIsNone(r["learning"])
        self.assertIsNone(r["evaluation"])
        self.assertTrue(all(pair.primary is None and pair.direct is None for pair in owners))
        self.assertFalse(direct.verify_record(r,self.plan)["evaluation_allowed"])

    def test_29_lifecycle_and_gates(self):
        histories = restore_histories(self.plan,self.record)
        closed = histories.close()
        self.assertTrue(all(closed[h]["states"]["primary"]["phase"]=="CLOSED" for h in p.HISTORIES))
        self.code("LEARNING_PHASE_INVALID",histories.close)
        histories.release()
        self.assertEqual(histories.pairs,{})
        self.code("MAIN_GATE_CLOSED",run.run_main_once,"s2nx-crossed-learning-20990101-02")
        self.assertFalse(run.MAIN_GATE)
        self.assertFalse(b.MAIN_GATE)
        self.assertFalse(run.nw.MAIN_GATE)

    def test_30_closed_entry_and_once_claims(self):
        hashes = {"neutral":"0"*64}
        q = b.sealed(dict(run_id=run.QUAL_ID,status="S2NX_LEARNING_QUALIFIED",passed_tests=32,unittest_calls=1,
            exit_code=0,hashes_before=hashes,hashes_after=hashes),"result_digest")
        actual_read = run.read
        def read_neutral(path,key):
            return q if path==run.QUAL_DIR/"result.json" else actual_read(path,key)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            b.publish(root/"evaluation-plan.json",b.evaluation_plan(self.plan),65536)
            with patch.object(run,"OUT_ROOT",root),patch.object(run,"SEAL_DIR",root),patch.object(run,"watched",return_value=hashes),\
                 patch.object(run,"load_presealed",return_value=self.plan),patch.object(run,"make_reader",return_value=NeutralReader()),\
                 patch.object(run,"read",side_effect=read_neutral):
                try:
                    run.MAIN_GATE = True
                    out = run.run_main_once("s2nx-crossed-learning-20990101-01")
                finally:
                    run.MAIN_GATE = False
                proof = run.verify_file_once(out)
                self.assertEqual(proof["status"],"S2NX_LEARNING_VERIFIED")
                result = run.evaluate_file_once(out)
                self.assertEqual(result["primary"],"CONFIRMED")
                with self.assertRaises(FileExistsError):
                    run.verify_file_once(out)
                with self.assertRaises(FileExistsError):
                    run.evaluate_file_once(out)
                self.assertFalse(list(out.glob("*.pending")))

    def test_31_write_conflict_and_progress(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"result.json"
            run.atomic(path,dict(value=True),65536)
            self.code("WRITE_CONFLICT",run.atomic,path,dict(value=False),65536)
        r = deepcopy(self.record)
        r["work"]["analyze_returns"] = 31
        reseal(r,"record_digest")
        self.code("PROGRESS_INVALID",direct.verify_record,r,self.plan)

    def test_32_actual_call_boundary_shared_target(self):
        stream, reader, work, histories = prefix()
        bound = stream.bind_predictions()
        self.assertEqual(set(json.loads(bound.data)["primary"]),{"H1","FIXED_HALF","LINEAR","PERSIST"})
        seen = []
        actual_score = p.nw.score
        def scorer(prediction,target):
            seen.append(id(target))
            self.assertIsNotNone(stream._pending)
            self.assertEqual(histories.pairs["H1"].primary.n,0)
            return actual_score(prediction,target)
        with patch.object(p.nw,"score",side_effect=scorer):
            stream.read_next(2)
        self.assertEqual(len(seen),4)
        self.assertEqual(len(set(seen)),1)
        self.assertEqual(len(reader.calls),3)
        self.assertEqual(histories.pairs["H1"].primary.n,1)


if __name__ == "__main__":
    unittest.main()
