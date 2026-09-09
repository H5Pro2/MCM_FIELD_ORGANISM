"""Neutral metadata qualification; no NX corpus generation or receptor import."""
from dataclasses import FrozenInstanceError
import hashlib
import math
import struct
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from tools import _s2nx_private_source_binding as b
from tools import _s2nx_private_preseal_verification as v

NEUTRAL = ((113.0,0.09,0.13),(227.0,0.0,0.27),(349.0,0.03,0.41))


def reseal(obj, key):
    obj.pop(key,None)
    obj[key] = b.digest(obj)


def bundle():
    sources = [b.bind_source(s,b.digest(s.recipe())) for s in b.specs()]
    hashes = {"neutral":"0"*64}
    ex = b.execution_plan(sources,{"neutral":True},hashes,{"neutral":True})
    ev = b.evaluation_plan(ex)
    se = b.sealed(dict(schema="s2nx.source-seal.v1",run_id="neutral",status="S2NX_SOURCES_PRESEALED",
        execution_digest=ex["execution_digest"],evaluation_digest=ev["evaluation_digest"],
        hashes_before=hashes,hashes_after=hashes,attempted_sources=32,completed_sources=32,generated_pcm_bytes=614400,
        max_live_payloads=1,raw_payloads_persisted=0,main_gate_after=False,prefix_groups=b.prefix_groups(),
        collisions=b.common.collision_groups(sources),receptor_calls=0,nj_calls=0,prediction_calls=0,learning_calls=0,error_calls=0,
        memory_calls=0,field_calls=0,context_calls=0,runtime_calls=0),"seal_digest")
    return ex,ev,se,hashes


def refresh(ex,ev,se):
    reseal(ex,"execution_digest")
    ev["execution_digest"] = se["execution_digest"] = ex["execution_digest"]
    reseal(ev,"evaluation_digest")
    se["evaluation_digest"] = ev["evaluation_digest"]
    reseal(se,"seal_digest")


class SourceTests(unittest.TestCase):
    def setUp(self):
        for module in (b,b.pure):
            guard = patch.object(module,"pcm_window",side_effect=AssertionError("corpus generation forbidden"))
            guard.start()
            self.addCleanup(guard.stop)

    def code(self,expected,fn,*args):
        with self.assertRaises(b.S2NXError) as caught:
            fn(*args)
        self.assertEqual(caught.exception.code,expected)

    def test_01_literal_sources(self):
        sources = b.specs()
        self.assertEqual(len(sources),32)
        self.assertEqual(len({s.payload()["source_id"] for s in sources}),32)
        self.assertEqual(b.ROWS,(((0,128),(0,384),(0,448),(0,464),(0,468),(0,469)),
            ((0,128),(0,384),(0,576),(0,720),(0,828),(0,909)),
            ((1,192),(1,320),(1,352),(1,360),(1,362)),((1,192),(1,320),(1,416),(1,488),(1,542)),
            ((1,192),(1,320),(1,352),(1,320),(1,312)),((1,192),(1,320),(1,416),(2,416),(2,416))))
        self.assertEqual(sources[-1].payload()["source_id"],"nx-s04-w04")
        self.code("WINDOW_SPEC_INVALID",b.WindowSpec,True,0)
        self.code("PAYLOAD_HASH_INVALID",b.bind_source,sources[0],"g"*64)

    def test_02_native_times(self):
        for n,s in enumerate(b.specs()):
            r = s.payload()
            self.assertEqual((r["window_start_sample"],r["window_end_sample"],r["nj_snapshot_index"]),(n*4800,(n+1)*4800,n*10))
        for start in (-480,1,480.0,True):
            with self.subTest(start=start):
                self.code("NATIVE_TIME_INVALID",b.native_index,start)

    def test_03_shared_recipes_separate_identities(self):
        lookup = {s.payload()["source_id"]:b.bind_source(s,"a"*64) for s in b.specs()}
        for ids in b.prefix_groups():
            rows = [lookup[x] for x in ids]
            self.assertEqual(len({x["recipe_digest"] for x in rows}),1)
            self.assertEqual(len({x["source_digest"] for x in rows}),len(ids))
            self.assertEqual(len({x["window_start_sample"] for x in rows}),len(ids))

    def test_04_phase_and_null_position(self):
        group = dict(seed="nx-neutral-phase",partials=[dict(frequency_ratio=[101,1],amplitude_ratio=[0,1]),
            dict(frequency_ratio=[203,1],amplitude_ratio=[1,10])])
        actual = b.prepare_groups([group])[0]
        for p,value in enumerate(actual):
            u = int.from_bytes(hashlib.sha256(f"nx-neutral-phase:{p}".encode("ascii")).digest()[:4],"little")
            self.assertEqual(value[2].hex(),((float(u)/4294967296.0)*math.tau).hex())
        self.assertEqual(actual[0][1],0.0)
        self.assertEqual(len(actual),2)

    def test_05_group_gain_local_time_order(self):
        indices = (0,173,4799)
        data = b.render(NEUTRAL,(37,1024),indices)
        expected = []
        for j in indices:
            total = 0.0
            for f,a,phase in NEUTRAL:
                total = total+a*math.sin(((math.tau*f)*(float(j)/48000.0))+phase)
            expected.append((37.0/1024.0)*total)
        self.assertEqual(data,b"".join(struct.pack("<f",x) for x in expected))

    def test_06_single_float32_rounding_after_gain(self):
        inputs = (0.1+2.0**-28,-0.2+2.0**-29,0.3)
        pack = struct.pack_into
        with patch.object(b,"group_value",side_effect=inputs),patch.object(b.struct,"pack_into",wraps=pack) as calls:
            data = b.render(NEUTRAL,(71,1024),(0,1,2))
        self.assertEqual(calls.call_count,3)
        expected = [(71.0/1024.0)*x for x in inputs]
        self.assertEqual([x.args[3] for x in calls.call_args_list],expected)
        self.assertEqual(data,b"".join(struct.pack("<f",x) for x in expected))

    def test_07_partial_order_including_zero(self):
        sin = math.sin
        with patch.object(b.pure.math,"sin",wraps=sin) as calls:
            b.group_value(NEUTRAL,0.003)
        self.assertEqual(calls.call_count,3)
        self.assertEqual([c.args[0] for c in calls.call_args_list],[((math.tau*f)*0.003)+p for f,a,p in NEUTRAL])

    def test_08_independent_complete_bundle(self):
        objects = bundle()
        before = b.canonical(objects)
        with patch.object(b,"render",side_effect=AssertionError("no PCM")),\
             patch.object(b,"prepare_groups",side_effect=AssertionError("no phases")),\
             patch.object(b,"forecast_sites",side_effect=AssertionError("independent sites")),\
             patch.object(b,"learning_schedule",side_effect=AssertionError("independent schedule")),\
             patch.object(b,"prediction_contract",side_effect=AssertionError("independent contract")),\
             patch.object(b,"evaluation_plan",side_effect=AssertionError("independent evaluation")),\
             patch.object(b,"budgets",side_effect=AssertionError("independent budgets")):
            result = v.verify_bundle(*objects)
        self.assertEqual((result["windows"],result["training_histories"],result["frozen_test_sites_bound_not_executed"]),(32,2,12))
        self.assertFalse(result["chronological_predictor_execution_qualified"])
        self.assertEqual(before,b.canonical(objects))

    def test_09_source_time_and_order_manipulations(self):
        for field,value in (("nj_snapshot_index",1),("source_id","other-source"),("ordinal",2)):
            with self.subTest(field=field):
                ex,ev,se,h = bundle()
                ex["sources"][0][field] = value
                reseal(ex["sources"][0],"source_digest")
                refresh(ex,ev,se)
                self.code("WINDOW_BINDING_INVALID",v.verify_bundle,ex,ev,se,h)
        ex,ev,se,h = bundle()
        ex["source_order"].reverse()
        refresh(ex,ev,se)
        self.code("SOURCE_ORDER_INVALID",v.verify_bundle,ex,ev,se,h)

    def test_10_future_and_prefix_metadata(self):
        ex,ev,se,h = bundle()
        self.assertEqual(len(ex["forecast_sites"]),20)
        ex["forecast_sites"][0]["available_source_ids"].append("nx-l01-w02")
        refresh(ex,ev,se)
        self.code("FORECAST_SITE_INVALID",v.verify_bundle,ex,ev,se,h)
        ex,ev,se,h = bundle()
        se["prefix_groups"][0][0] = "nx-l01-w03"
        reseal(se,"seal_digest")
        self.code("PREFIX_BINDING_INVALID",v.verify_bundle,ex,ev,se,h)

    def test_11_closed_functional_contract(self):
        for field in ("future_values","recipe","source_id","history_id","time"):
            with self.subTest(field=field):
                ex,ev,se,h = bundle()
                ex["prediction_contract"]["arms"][0]["functional_fields"].append(field)
                refresh(ex,ev,se)
                self.code("PREDICTOR_BOUNDARY_INVALID",v.verify_bundle,ex,ev,se,h)

    def test_12_twenty_eight_separate_criteria(self):
        ex,ev,se,h = bundle()
        self.assertEqual([c["check_id"] for c in ev["criteria"]],
            [f"{p}{k:02d}" for p,n in (("K",6),("F",6),("B",12),("W",4)) for k in range(1,n+1)])
        self.assertNotIn("criteria",ex)
        self.assertNotIn("expected_history",ex)
        self.assertEqual(ev["expected_history"],dict(s01="H1",s02="H2"))
        self.assertEqual([(c["site_id"],c["left"]) for c in ev["criteria"][-4:]],
            [(p,"MAE_"+h) for p in ("p08","p11") for h in ("H1","H2")])
        ev["criteria"][0]["operator"] = "LE"
        refresh(ex,ev,se)
        self.code("EVALUATION_BINDING_INVALID",v.verify_bundle,ex,ev,se,h)

    def test_13_complete_metadata_size_and_limits(self):
        ex,ev,se,h = bundle()
        hashes,env,gen = b.watched(),b.environment(),b.generator_identity()
        full = b.execution_plan(ex["sources"],env,hashes,gen)
        prereg = dict(run_id=b.RUN_ID,hashes=hashes,environment=env,generator=gen,
            windows=[s.payload() for s in b.specs()],forecast_sites=b.forecast_sites(),prediction_contract=b.prediction_contract(),
            learning_schedule=b.learning_schedule(),evaluation=b.evaluation_plan(dict(execution_digest="0"*64)),
            budgets=b.budgets(),prefix_groups=b.prefix_groups(),retry=False)
        for obj in (full,ev,se,prereg):
            self.assertLessEqual(len(b.canonical(obj)),65536)
        self.code("PAYLOAD_SIZE_INVALID",b.render,NEUTRAL,(3,1024),tuple(range(4801)))
        ex["oversize"] = "x"*65536
        refresh(ex,ev,se)
        self.code("METADATA_SIZE_INVALID",v.verify_bundle,ex,ev,se,h)

    def test_14_immutability_profile_and_digest(self):
        s = b.WindowSpec(0,0)
        with self.assertRaises(FrozenInstanceError):
            s.stream = 2
        recipe = s.recipe()
        recipe["group"]["seed"] = "changed"
        self.assertEqual(s.recipe()["group"]["seed"],"s2nx-pcm-001")
        ex,ev,se,h = bundle()
        ex["profiles"]["half_profile_digest"] = "0"*64
        refresh(ex,ev,se)
        self.code("PROFILE_BUDGET_INVALID",v.verify_bundle,ex,ev,se,h)
        ex,ev,se,h = bundle()
        se["seal_digest"] = "0"*64
        self.code("SEALED_DIGEST_INVALID",v.verify_bundle,ex,ev,se,h)

    def test_15_builtin_math_identity(self):
        module = SimpleNamespace(__name__="math",__spec__=SimpleNamespace(origin="built-in"))
        self.assertEqual(b.common.common.math_identity(module,("math",)),
            dict(kind="BUILT_IN",module_name="math",spec_origin="built-in",builtin_membership=True))
        with self.assertRaisesRegex(ValueError,"^MATH_BUILTIN_BINDING_INVALID$"):
            b.common.common.math_identity(module,())

    def test_16_fail_closed_and_exclusions(self):
        self.code("SOURCE_COUNT_INVALID",b.execution_plan,[],{}, {}, {})
        with patch.object(b,"group_value",return_value=float("inf")):
            self.code("PCM_DOMAIN_INVALID",b.render,NEUTRAL,(3,1024),(0,))
        ex,ev,se,h = bundle()
        ex["prediction_execution_authorized"] = True
        refresh(ex,ev,se)
        self.code("AUTHORIZATION_INVALID",v.verify_bundle,ex,ev,se,h)
        self.assertFalse(any(n.startswith("mcm_field_organism") or "_s2nj_private" in n or n=="numpy" for n in sys.modules))
        self.assertIs(b.MAIN_GATE,False)

    def test_17_separate_update_histories(self):
        ex,ev,se,h = bundle()
        sites = ex["forecast_sites"]
        self.assertEqual([r["site_id"] for r in sites[:8]],[f"t{i:02d}" for i in range(1,9)])
        self.assertEqual([r["active_histories"] for r in sites[:8]],[["H1"]]*4+[["H2"]]*4)
        self.assertEqual([r["target"] for r in sites[:8]],[2,3,4,5]*2)
        self.assertTrue(all(r["target_source_id"] not in r["available_source_ids"] for r in sites))
        ex["forecast_sites"][4]["active_histories"] = ["H1"]
        refresh(ex,ev,se)
        self.code("FORECAST_SITE_INVALID",v.verify_bundle,ex,ev,se,h)

    def test_18_both_freeze_boundaries(self):
        for field,value in (("both_frozen_before_source","nx-s01-w01"),
                ("test_updates_allowed",True),("reset_prefix_each_stream",False),("training_order",["H2","H1"])):
            with self.subTest(field=field):
                ex,ev,se,h = bundle()
                self.assertEqual([x["freeze_after_site"] for x in ex["learning_schedule"]["histories"]],["t04","t08"])
                ex["learning_schedule"][field] = value
                refresh(ex,ev,se)
                self.code("LEARNING_SCHEDULE_INVALID",v.verify_bundle,ex,ev,se,h)

    def test_19_no_recipe_coefficient_initialization(self):
        for history in (0,1):
            for field,value in (("initial_state",dict(n=0,Sxx=0.0,Sxy=0.0,alpha=0.75)),("expected_learned_coefficient",0.25)):
                with self.subTest(history=history,field=field):
                    ex,ev,se,h = bundle()
                    self.assertIsNone(ex["learning_schedule"]["histories"][history]["expected_learned_coefficient"])
                    ex["learning_schedule"]["histories"][history][field] = value
                    refresh(ex,ev,se)
                    self.code("LEARNING_SCHEDULE_INVALID",v.verify_bundle,ex,ev,se,h)

    def test_20_counter_budget_and_root_isolation(self):
        for section in ("counter","budget","root"):
            with self.subTest(section=section):
                ex,ev,se,h = bundle()
                if section == "counter":
                    se["completed_sources"] = 31
                    code = "COUNTERS_INVALID"
                elif section == "budget":
                    ex["budgets"]["windows"] = 26
                    code = "PROFILE_BUDGET_INVALID"
                else:
                    ex["expected_history"] = ev["expected_history"]
                    code = "EXECUTION_FORM_INVALID"
                refresh(ex,ev,se)
                self.code(code,v.verify_bundle,ex,ev,se,h)

    def test_21_exact_fixed_control_binding(self):
        for field,value in (("value",0.25),("binary64_hex","0x0.0p+0"),("mutable",True),("source_estimated",True)):
            with self.subTest(field=field):
                ex,ev,se,h = bundle()
                c = ex["prediction_contract"]["fixed_control"]
                self.assertEqual(c["value"].hex(),c["binary64_hex"])
                c[field] = value
                refresh(ex,ev,se)
                self.code("PREDICTOR_BOUNDARY_INVALID",v.verify_bundle,ex,ev,se,h)

    def test_22_all_twelve_crossed_test_sites(self):
        ex,ev,se,h = bundle()
        sites = ex["forecast_sites"][8:]
        self.assertEqual(len(sites),12)
        self.assertEqual([r["site_id"] for r in sites],[f"p{k:02d}" for k in range(1,13)])
        self.assertTrue(all(r["active_histories"] == ["H1","H2"] and not r["update_after_target"] for r in sites))
        sites[0]["active_histories"] = ["H1"]
        refresh(ex,ev,se)
        self.code("FORECAST_SITE_INVALID",v.verify_bundle,ex,ev,se,h)

    def test_23_fits_are_functional_not_start_gates(self):
        ex,ev,se,h = bundle()
        self.assertTrue(ex["learning_schedule"]["learned_values_are_not_start_gates"])
        self.assertTrue(ev["full_success_requires"]["actual_alphas_different"])
        self.assertFalse(ev["automatic_history_selection_proven"])
        ev["full_success_requires"]["all_F"] = False
        refresh(ex,ev,se)
        self.code("EVALUATION_BINDING_INVALID",v.verify_bundle,ex,ev,se,h)

    def test_24_explicit_1024_without_historical_relaxation(self):
        from tools import _s2nw_private_source_binding as historical
        for gain in ((3,64),(3,512),(True,1024),(1025,1024)):
            with self.subTest(gain=gain):
                self.code("GAIN_FORM_INVALID",b.render,NEUTRAL,gain,(0,))
        with self.assertRaises(historical.S2NWError) as caught:
            historical.render(NEUTRAL,(3,1024),(0,))
        self.assertEqual(caught.exception.code,"GAIN_FORM_INVALID")
        self.assertTrue(all(s.recipe()["gain_ratio"][1] == 1024 for s in b.specs()))
        self.assertFalse(historical.MAIN_GATE)


if __name__=="__main__":
    unittest.main()
