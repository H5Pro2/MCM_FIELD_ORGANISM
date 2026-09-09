"""Neutral NZ integration tests, with all sealed PCM generators blocked."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import _s2nz_private_diagnostic_run as run
from tools import _s2nz_private_diagnostic_evaluation as ev
from tests.test_s2ny_private_prediction import neutral_plan as ny_plan,NeutralReader,values,reseal,CARRIERS

b,p=run.b,run.p


def plan(label="neutral-nz",levels=None):
    base=ny_plan(label) if levels is None else ny_plan(label,levels)
    base.pop("execution_digest")
    for source in base["sources"]:
        recipe=dict(schema="s2nz.pcm-window-recipe.v1",sample_rate=48000,sample_count=4800,
            group=dict(seed="nz-neutral-phase",partials=[dict(frequency_ratio=[f,1],amplitude_ratio=[a,20])
                for f,a in ((113,4),(227,2),(349,1))]),gain_ratio=[37,1024],
            noise=dict(seed="nz-neutral-noise",window=source["window_ordinal"],amplitude_ratio=[1,1024]),
            synthesis_time="float(j)/48000.0; j=0..4799",rounding="group-sum;gain;optional-noise-add;single-f32le")
        source.update(recipe=recipe,recipe_digest=b.digest(recipe),format="PCM_F32LE",channels=1,pcm_byte_count=19200)
        reseal(source,"source_digest")
    base.update(schema="s2nz.source-execution-plan.v1",contract_sha256=b.PINS[b.CONTRACT],
        source_order=[s["source_id"] for s in base["sources"]],budgets=b.budgets(),
        prediction_contract=b.prediction_contract(),noise_contract=b.noise_contract(),
        authorizations={key:False for key in b.FORBIDDEN_CALLS})
    return b.sealed(base,"execution_digest")


def prefix(observed=False,label="neutral-nz"):
    ex=plan(label)
    work,reader=p.Work(),NeutralReader()
    frozen=run.ny.FrozenInputs(ex["freeze_import"])
    stream=run.ny.PrefixStream(ex["sources"][:5],work,reader,frozen)
    stream.read_next(0)
    stream.read_next(1)
    if observed:
        stream.bind_predictions()
        stream.read_next(2)
    return stream,reader,work,frozen


class DiagnosticQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for module in (b,b.old,b.old.pure,b.old.pure.pure,run.ny.nw.b,run.ny.nw.nv.b):
            for name in ("pcm_window","preseal_once"):
                guard=patch.object(module,name,side_effect=AssertionError("sealed payload forbidden"))
                guard.start()
                cls.addClassCleanup(guard.stop)
        for module in (run,run.ny):
            guard=patch.object(module,"load_presealed",side_effect=AssertionError("no real input"))
            guard.start()
            cls.addClassCleanup(guard.stop)
        cls.plan=plan()
        cls.reader=NeutralReader()
        cls.record=run.execute(cls.plan,cls.reader,"neutral-nz-run")
        cls.proof=run.verify_record(cls.record,cls.plan)

    def code(self,code,fn,*args):
        with self.assertRaises(p.S2NYPredictionError) as caught:
            fn(*args)
        self.assertEqual(caught.exception.code,code)

    def test_01_complete_unchanged_ny_composition(self):
        self.assertEqual(self.record["status"],"RECORDING_COMPLETE",self.record["failure"])
        self.assertEqual(self.record["core"]["schema"],"s2ny.prefix-recommendation.v1")
        self.assertEqual(len(self.reader.calls),30)
        self.assertTrue(self.proof["baseline_equal"])
        self.assertEqual(self.proof["core_proof"]["work"]["sites"],18)
        self.assertEqual(self.record["work"]["primary_local_fits"],12)

    def test_02_all_arms_before_target_reader(self):
        stream,reader,_,_=prefix(True)
        original=stream.reader
        def inspect(source,work):
            committed=json.loads(stream._committed)
            self.assertEqual(set(committed["primary"]["predictions"]),{"H1","H2","LOCAL","PERSIST"})
            self.assertEqual(committed["primary"],committed["direct"])
            self.assertEqual(committed["target"],source["window_ordinal"])
            self.assertEqual(committed["error_evidence"]["primary"][0]["target"],2)
            return original(source,work)
        stream.reader=inspect
        stream.bind_predictions()
        stream.read_next(3)
        self.assertEqual(len(reader.calls),4)
        stream.abort()

    def test_03_future_access_missing_commit(self):
        stream,reader,_,_=prefix()
        self.code("PREDICTION_BINDING_MISSING",stream.read_next,2)
        self.code("FUTURE_ACCESS_DENIED",stream.read_next,3)
        self.assertEqual(len(reader.calls),2)
        stream.abort()

    def test_04_changed_commit(self):
        stream,reader,_,_=prefix()
        stream.bind_predictions()
        changed=json.loads(stream._pending)
        changed["primary"]["predictions"]["H1"][0]=.9
        reseal(changed,"binding_digest")
        stream._pending=b.canonical(changed)
        self.code("PREDICTION_BINDING_CHANGED",stream.read_next,2)
        self.assertEqual(len(reader.calls),2)
        stream.abort()

    def test_05_error_provenance_independent_controls(self):
        for key,value in (("stream_id","s02"),("target",0),("state_digest","0"*64),("mae",99.0)):
            with self.subTest(key=key):
                stream,reader,_,_=prefix(True)
                evidence=json.loads(stream.error_evidence)
                evidence["primary"][0][key]=value
                stream.error_evidence=b.canonical(evidence)
                self.code("ERROR_PROVENANCE_INVALID",stream.bind_predictions)
                self.assertEqual(len(reader.calls),3)
                stream.abort()

    def test_06_functional_prefix_has_no_source_metadata(self):
        a,_,_,_=prefix(True,"one")
        c,_,_,_=prefix(True,"another")
        first,second=json.loads(a.bind_predictions()),json.loads(c.bind_predictions())
        self.assertEqual(first["primary"],second["primary"])
        self.assertNotEqual(first["prefix_digests"],second["prefix_digests"])
        a.abort()
        c.abort()

    def test_07_clean_input_or_target_forbidden(self):
        for key in ("clean_counterpart_as_input","clean_counterpart_as_target"):
            with self.subTest(key=key):
                ex=deepcopy(self.plan)
                ex["prediction_contract"][key]=True
                reseal(ex,"execution_digest")
                self.code("CONTROL_BOUNDARY_INVALID",run.validate_plan,ex)

    def test_08_counterpart_cannot_replace_observed_target(self):
        stream,reader,work,frozen=prefix()
        clean=self.plan["sources"][5]
        stream.reader=lambda source,w:reader(clean,w)
        stream.bind_predictions()
        self.code("WINDOW_BINDING_INVALID",stream.read_next,2)
        stream.abort()
        frozen.release()

    def test_09_scores_use_own_observed_target(self):
        stream=self.record["core"]["streams"][1]
        clean=self.record["core"]["streams"][0]
        site=stream["sites"][0]
        self.assertNotEqual(stream["windows"][2]["projection"]["values"],clean["windows"][2]["projection"]["values"])
        prediction=site["prediction_binding"]["primary"]["predictions"]["H1"][0]
        actual=stream["windows"][2]["projection"]["values"][0]
        self.assertEqual(site["primary"]["scores"]["H1"]["terms"][0]["value"],abs(prediction-actual))
        self.assertEqual(site["target_window_digest"],stream["windows"][2]["window_digest"])

    def test_10_each_stream_resets_prefix_and_errors(self):
        for stream in self.record["core"]["streams"]:
            binding=stream["sites"][0]["prediction_binding"]
            self.assertEqual(len(binding["prefix_digests"]),2)
            self.assertEqual(binding["error_evidence"],dict(primary=None,direct=None))
            self.assertEqual(binding["primary"]["recommendation"]["status"],"ABSTAIN_INSUFFICIENT_PREFIX")
            self.assertTrue(stream["closed"])

    def test_11_freeze_read_only_mutation_and_release(self):
        stream,reader,_,frozen=prefix()
        before=frozen.data
        stream.bind_predictions()
        self.assertEqual(frozen.data,before)
        self.assertFalse(hasattr(frozen,"update"))
        frozen.data=b"changed"
        self.code("FREEZE_BINDING_CHANGED",stream.read_next,2)
        self.assertEqual(len(reader.calls),2)
        stream.abort()
        frozen.release()
        self.assertTrue(frozen.closed)
        self.assertIsNone(frozen.data)

    def test_12_focus_four_with_partial_abstention(self):
        result=ev.evaluate(self.record,self.proof,b.evaluation_plan(self.plan))
        focus=result["focus"]
        self.assertEqual(focus["N"],4)
        self.assertEqual(focus["D"],2)
        self.assertEqual(focus["site_ids"],["p05","p06","p11","p12"])
        for row in result["rows"]:
            if row["recommendation"]["history"] is None:
                self.assertIsNone(row["recommended_mae"])
                self.assertEqual(row["recommendation_gains"],{})
                self.assertIn("H1",row["mae"])
        self.assertEqual(result["status"],"DIAGNOSTICALLY_DESCRIBED")

    def test_13_all_abstentions_do_not_reduce_N(self):
        ex=plan("ties",((.25,)*5,)*6)
        record=run.execute(ex,NeutralReader(),"neutral-ties")
        proof=run.verify_record(record,ex)
        result=ev.evaluate(record,proof,b.evaluation_plan(ex))
        self.assertTrue(proof["evaluation_allowed"])
        self.assertEqual((result["focus"]["N"],result["focus"]["D"]),(4,0))
        self.assertEqual(result["focus"]["status"],"NUTZEN_NICHT_GEPRUEFT")
        self.assertTrue(all(r["recommended_mae"] is None for r in result["rows"]))

    def test_14_negative_local_differences_regular(self):
        ex=plan("negative",((.125,.25,.3125,.34375,.359375),)*6)
        frozen=ex["freeze_import"]
        frozen["histories"][1]["frozen_payload"]["alpha"]=1.0
        frozen["histories"][1]["frozen_payload"]["Sxy"]=1.0
        frozen["histories"][1]["alpha_binary64_hex"]=(1.0).hex()
        reseal(frozen["histories"][1]["frozen_payload"],"state_digest")
        reseal(frozen,"freeze_import_digest")
        reseal(ex,"execution_digest")
        record=run.execute(ex,NeutralReader(),"neutral-negative")
        proof=run.verify_record(record,ex)
        result=ev.evaluate(record,proof,b.evaluation_plan(ex))
        members=[r for r in result["rows"] if r["target"]>2]
        self.assertTrue(proof["evaluation_allowed"])
        self.assertEqual(len(members),12)
        self.assertTrue(all(all(g<0 for g in r["fixed_history_gains_vs_local"].values()) for r in members))
        self.assertTrue(all(r["recommendation_gains"]["LOCAL"]<0 for r in members))
        self.assertEqual(result["focus"]["N"],4)
        self.assertIsNone(result["practical_success_status"])
        self.assertIsNone(result["robustness_status"])

    def test_15_next_best_is_not_local_or_persist_gain(self):
        site=deepcopy(self.record["core"]["streams"][0]["sites"][1])
        site["prediction_binding"]["primary"]["recommendation"]=dict(status="RECOMMEND",history="H1")
        for arm,value in (("H1",.2),("H2",.3),("LOCAL",.1),("PERSIST",0.0)):
            site["primary"]["scores"][arm]["mae"]=value
        site["primary"].update(recommended_mae=.2,recommendation_gains=dict(LOCAL=-.1,PERSIST=-.2),
            gains_vs_persist=dict(H1=-.2,H2=-.3,LOCAL=-.1))
        row=ev.site_result(site,"p02","s01")
        self.assertEqual(row["recommendation_outcome"],"NEXT_BEST")
        self.assertEqual(row["recommendation_outcomes"],dict(LOCAL="LOSS",PERSIST="LOSS"))
        self.assertEqual(row["fixed_history_gains_vs_local"]["H1"],-.1)

    def test_16_direct_verification_no_primary_arithmetic(self):
        with patch.object(p,"predict",side_effect=AssertionError("no primary")),\
             patch.object(p,"local_fit",side_effect=AssertionError("no primary")),\
             patch.object(p,"score",side_effect=AssertionError("no primary")),\
             patch.object(p,"recommend",side_effect=AssertionError("no primary")):
            proof=run.verify_record(self.record,self.plan)
        self.assertTrue(proof["baseline_equal"])

    def test_17_offline_missing_and_foreign_target(self):
        for mode in ("missing","foreign"):
            with self.subTest(mode=mode):
                record=deepcopy(self.record)
                stream=record["core"]["streams"][0]
                if mode=="missing":
                    stream["sites"].pop()
                else:
                    stream["sites"][0]["target_window_digest"]=record["core"]["streams"][1]["windows"][2]["window_digest"]
                    reseal(stream["sites"][0],"site_digest")
                reseal(stream,"stream_digest")
                reseal(record["core"],"record_digest")
                reseal(record,"record_digest")
                self.code("STREAM_BINDING_INVALID" if mode=="missing" else "TARGET_BINDING_INVALID",run.verify_record,record,self.plan)

    def test_18_no_clipping_and_null_denominator(self):
        for seq in ((values(.25),)*3,(values(0),values(.25),values(1))):
            primary=p.predict((.25,.75),seq,(.1,.2))
            direct=run.ny.direct.direct_predict((.25,.75),seq,(.1,.2))
            self.assertEqual(b.canonical(primary),b.canonical(direct))
        self.assertGreater(primary["predictions"]["LOCAL"][0],1.0)
        self.assertEqual(p.local_fit(p.LocalInput(p.PROFILE,*(values(.25),)*3))["beta"],0.0)

    def test_19_unchanged_work_limits_and_atomic_conflict(self):
        self.code("WORK_LIMIT_EXCEEDED",p.Work().add,"generation_attempts",31)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"result.json"
            run.atomic(path,dict(test=1),65536)
            before=path.read_bytes()
            self.code("WRITE_CONFLICT",run.atomic,path,dict(test=2),65536)
            self.assertEqual(before,path.read_bytes())
            self.code("OUTPUT_SIZE_EXCEEDED",run.atomic,Path(folder)/"big.json",dict(big="x"*2097152),2097152)

    def test_20_materialization_failure_and_lifecycle(self):
        reader=NeutralReader()
        def fail(source,work):
            if source["window_ordinal"]==2:
                raise p.S2NYPredictionError("NEUTRAL_SOURCE_FAILURE")
            return reader(source,work)
        fail.carriers=CARRIERS
        record=run.execute(self.plan,fail,"neutral-failure")
        self.assertEqual(record["status"],"NOT_EVALUABLE")
        self.assertEqual(record["failure"]["phase"],"SOURCE_PROCESSING")
        self.assertEqual(record["failure"]["code"],"NEUTRAL_SOURCE_FAILURE")
        self.assertEqual(record["core"]["streams"],[])
        self.assertTrue(record["closed"])
        self.assertEqual(len(reader.calls),2)
        proof=run.verify_record(record,self.plan)
        self.assertFalse(proof["evaluation_allowed"])
        self.code("EVALUATION_BEFORE_VERIFICATION",ev.evaluate,record,proof,b.evaluation_plan(self.plan))

    def test_21_source_time_profile_and_gate(self):
        ex=deepcopy(self.plan)
        ex["sources"][0]["nj_snapshot_index"]=1
        reseal(ex["sources"][0],"source_digest")
        reseal(ex,"execution_digest")
        self.code("SOURCE_TIME_INVALID",run.validate_plan,ex)
        record=run.execute(ex,NeutralReader(),"neutral-plan-failure")
        self.assertEqual(record["status"],"NOT_EVALUABLE")
        self.assertIsNone(record["core"])
        ex=deepcopy(self.plan)
        ex["profiles"]["half_profile_digest"]="0"*64
        reseal(ex,"execution_digest")
        self.code("PLAN_BINDING_INVALID",run.validate_plan,ex)
        self.code("MAIN_GATE_CLOSED",run.run_main_once,"s2nz-diagnostic-disturbance-20260909-99")
        self.assertFalse(run.MAIN_GATE)

    def test_22_real_neutral_reader_commits_before_generation(self):
        ex=deepcopy(self.plan)
        ex["environment"]=b.environment()
        sources=ex["sources"][:5]
        for row in sources:
            row["pcm_sha256"]=hashlib.sha256(bytes(19200)).hexdigest()
            reseal(row,"source_digest")
        calls=[]
        holder={}
        def zero(source):
            k=source["window_ordinal"]
            if k>=2:
                committed=json.loads(holder["stream"]._committed)
                self.assertEqual(committed["target"],k)
                self.assertEqual(committed["primary"],committed["direct"])
            calls.append(k)
            return bytearray(19200)
        with patch.object(run,"generate",side_effect=zero):
            reader=run.make_reader(ex)
            work=p.Work()
            frozen=run.ny.FrozenInputs(ex["freeze_import"])
            stream=run.ny.PrefixStream(sources,work,reader,frozen)
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

    def test_23_atomic_readonly_file_verification_and_evaluation(self):
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder)/"neutral-nz-run"
            out.mkdir()
            record=deepcopy(self.record)
            hashes=run.watched()
            record.update(code_hashes_before=hashes,code_hashes_after=hashes,seal_digest=run.SEAL_DIGEST)
            reseal(record,"record_digest")
            run.atomic(out/"result.json",record,p.MAX_OUTPUT_BYTES)
            before=(out/"result.json").read_bytes()
            evdir=Path(folder)/"evaluation"
            evdir.mkdir()
            run.atomic(evdir/"evaluation-plan.json",b.evaluation_plan(self.plan),65536)
            with patch.object(run,"load_presealed",return_value=self.plan),patch.object(run,"SEAL_DIR",evdir),\
                 patch.object(run,"watched",return_value=hashes):
                proof=run.verify_file_once(out)
                result=run.evaluate_file_once(out)
            self.assertEqual(proof["verification_calls"],1)
            self.assertEqual(result["focus"]["N"],4)
            self.assertEqual(before,(out/"result.json").read_bytes())

    def test_24_full_hull_and_evaluation_lock(self):
        record=deepcopy(self.record)
        hashes=run.watched()
        record.update(code_hashes_before=hashes,code_hashes_after=hashes,seal_digest=run.SEAL_DIGEST)
        reseal(record,"record_digest")
        proof=run.verify_record(record,self.plan)
        result=ev.evaluate(record,proof,b.evaluation_plan(self.plan))
        self.assertLessEqual(len(b.canonical(record)),2097152)
        self.assertLessEqual(len(b.canonical(proof)),262144)
        self.assertLessEqual(len(b.canonical(result)),262144)
        run.atomic(run.QUAL_DIR/"neutral-envelope.json",record,2097152)
        run.atomic(run.QUAL_DIR/"neutral-evaluation.json",result,262144)
        proof["evaluation_allowed"]=False
        reseal(proof,"verification_digest")
        self.code("EVALUATION_BEFORE_VERIFICATION",ev.evaluate,record,proof,b.evaluation_plan(self.plan))
        record["excess"]="x"*2097152
        reseal(record,"record_digest")
        self.code("OUTPUT_SIZE_EXCEEDED",run.verify_record,record,self.plan)


if __name__=="__main__":
    unittest.main()
