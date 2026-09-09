"""Neutral source-only NW tests; corpus generation is blocked in every body."""
from dataclasses import FrozenInstanceError
import hashlib
import math
import struct
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from tools import _s2nw_private_source_binding as b
from tools import _s2nw_private_preseal_verification as v

NEUTRAL = ((113.0,0.09,0.13),(227.0,0.0,0.27),(349.0,0.03,0.41))


def reseal(obj, key):
    obj.pop(key,None)
    obj[key] = b.digest(obj)


def bundle():
    # Synthetic hash tokens from metadata, never hashes of generated NW PCM.
    sources = [b.bind_source(s,b.digest(s.recipe())) for s in b.specs()]
    hashes = {"neutral":"0"*64}
    ex = b.execution_plan(sources,{"neutral":True},hashes,{"neutral":True})
    ev = b.evaluation_plan(ex)
    se = b.sealed(dict(schema="s2nw.source-seal.v1",run_id="neutral",status="S2NW_SOURCES_PRESEALED",
        execution_digest=ex["execution_digest"],evaluation_digest=ev["evaluation_digest"],
        hashes_before=hashes,hashes_after=hashes,attempted_sources=26,completed_sources=26,generated_pcm_bytes=499200,
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
        with self.assertRaises(b.S2NWError) as caught:
            fn(*args)
        self.assertEqual(caught.exception.code,expected)

    def test_01_literal_sources(self):
        sources = b.specs()
        self.assertEqual(len(sources),26)
        self.assertEqual(len({s.payload()["source_id"] for s in sources}),26)
        self.assertEqual(b.ROWS,(((0,16),(0,32),(0,40),(0,44),(0,46),(0,47)),
            ((1,20),(1,28),(1,32),(1,34),(1,35)),((1,20),(1,28),(1,32),(1,28),(1,26)),
            ((1,20),(1,28),(1,32),(1,32),(1,32)),((1,20),(1,28),(1,32),(2,32),(2,32))))
        self.assertEqual(sources[-1].payload()["source_id"],"nw-s04-w04")
        self.code("WINDOW_SPEC_INVALID",b.WindowSpec,True,0)
        self.code("PAYLOAD_HASH_INVALID",b.bind_source,sources[0],"g"*64)

    def test_02_native_times(self):
        for n,s in enumerate(b.specs()):
            r = s.payload()
            self.assertEqual((r["window_start_sample"],r["window_end_sample"],r["nj_snapshot_index"]),(n*4800,(n+1)*4800,n*10))
        for start in (-480,1,480.0,True):
            with self.subTest(start=start):
                self.code("NATIVE_TIME_INVALID",b.native_index,start)

    def test_03_prefix_identity_not_deduplicated(self):
        for k in range(3):
            rows = [b.bind_source(b.WindowSpec(s,k),"a"*64) for s in range(1,5)]
            self.assertEqual(len({x["recipe_digest"] for x in rows}),1)
            self.assertEqual(len({x["source_digest"] for x in rows}),4)
            self.assertEqual(len({x["window_start_sample"] for x in rows}),4)
            self.assertEqual(b.prefix_groups()[k],[x["source_id"] for x in rows])

    def test_04_phase_and_null_position(self):
        group = dict(seed="nw-neutral-phase",partials=[dict(frequency_ratio=[101,1],amplitude_ratio=[0,1]),
            dict(frequency_ratio=[203,1],amplitude_ratio=[1,10])])
        actual = b.prepare_groups([group])[0]
        for p,value in enumerate(actual):
            u = int.from_bytes(hashlib.sha256(f"nw-neutral-phase:{p}".encode("ascii")).digest()[:4],"little")
            self.assertEqual(value[2].hex(),((float(u)/4294967296.0)*math.tau).hex())
        self.assertEqual(actual[0][1],0.0)
        self.assertEqual(len(actual),2)

    def test_05_group_gain_local_time_order(self):
        indices = (0,173,4799)
        data = b.render(NEUTRAL,(3,64),indices)
        expected = []
        for j in indices:
            total = 0.0
            for f,a,phase in NEUTRAL:
                total = total + a*math.sin(((math.tau*f)*(float(j)/48000.0))+phase)
            expected.append((3.0/64.0)*total)
        self.assertEqual(data,b"".join(struct.pack("<f",x) for x in expected))

    def test_06_single_float32_rounding_after_gain(self):
        inputs = (0.1+2.0**-28,-0.2+2.0**-29,0.3)
        pack = struct.pack_into
        with patch.object(b,"group_value",side_effect=inputs),patch.object(b.struct,"pack_into",wraps=pack) as calls:
            data = b.render(NEUTRAL,(7,64),(0,1,2))
        self.assertEqual(calls.call_count,3)
        expected = [(7.0/64.0)*x for x in inputs]
        self.assertEqual([x.args[3] for x in calls.call_args_list],expected)
        self.assertEqual(data,b"".join(struct.pack("<f",x) for x in expected))

    def test_07_partial_order_including_zero(self):
        sin = math.sin
        with patch.object(b.pure.math,"sin",wraps=sin) as calls:
            b.group_value(NEUTRAL,0.003)
        self.assertEqual(calls.call_count,3)
        self.assertEqual([c.args[0] for c in calls.call_args_list],[((math.tau*f)*0.003)+p for f,a,p in NEUTRAL])

    def test_08_complete_neutral_bundle(self):
        objects = bundle()
        before = b.canonical(objects)
        with patch.object(b,"render",side_effect=AssertionError("no PCM in verifier")),\
             patch.object(b,"prepare_groups",side_effect=AssertionError("no phases in verifier")):
            result = v.verify_bundle(*objects)
        self.assertEqual(result["windows"],26)
        self.assertEqual(result["frozen_test_sites_bound_not_executed"],12)
        self.assertFalse(result["chronological_predictor_execution_qualified"])
        self.assertEqual(before,b.canonical(objects))

    def test_09_source_and_time_manipulations(self):
        for field,value in (("nj_snapshot_index",1),("source_id","other-source")):
            with self.subTest(field=field):
                ex,ev,se,h = bundle()
                ex["sources"][0][field] = value
                reseal(ex["sources"][0],"source_digest")
                refresh(ex,ev,se)
                self.code("WINDOW_BINDING_INVALID",v.verify_bundle,ex,ev,se,h)

    def test_10_sites_and_prefix_manipulations(self):
        ex,ev,se,h = bundle()
        self.assertEqual(len(ex["forecast_sites"]),16)
        ex["forecast_sites"][0]["available_source_ids"].append("nw-l01-w02")
        refresh(ex,ev,se)
        self.code("FORECAST_SITE_INVALID",v.verify_bundle,ex,ev,se,h)
        ex,ev,se,h = bundle()
        se["prefix_groups"][0][0] = "nw-s01-w03"
        reseal(se,"seal_digest")
        self.code("PREFIX_BINDING_INVALID",v.verify_bundle,ex,ev,se,h)

    def test_11_closed_future_free_input_contract(self):
        for field in ("future_values","recipe","payload_sha256","source_id","time"):
            with self.subTest(field=field):
                ex,ev,se,h = bundle()
                ex["prediction_contract"]["arms"][0]["functional_fields"].append(field)
                refresh(ex,ev,se)
                self.code("PREDICTOR_BOUNDARY_INVALID",v.verify_bundle,ex,ev,se,h)
        ex,ev,se,h = bundle()
        ex["prediction_contract"]["standalone_materialization_authorized"] = True
        refresh(ex,ev,se)
        self.code("PREDICTOR_BOUNDARY_INVALID",v.verify_bundle,ex,ev,se,h)

    def test_12_evaluation_roots_and_nine_conditions(self):
        ex,ev,se,h = bundle()
        self.assertNotIn("categories",ex)
        self.assertNotIn("criteria",ex)
        self.assertEqual([(c["site_id"],c["right"],c["operator"]) for c in ev["criteria"]],
            [(f"p{k:02d}","MAE_"+arm,"LT") for k in (1,2,3) for arm in ("PERSIST","LINEAR")] +
            [(site,"MAE_PERSIST","GT") for site in ("p05","p08","p11")])
        ev["criteria"][0]["operator"] = "LE"
        refresh(ex,ev,se)
        self.code("EVALUATION_BINDING_INVALID",v.verify_bundle,ex,ev,se,h)

    def test_13_resource_limits(self):
        ex,ev,se,h = bundle()
        self.assertTrue(all(len(b.canonical(x))<=65536 for x in (ex,ev,se)))
        self.assertEqual(ex["budgets"]["max_live_pcm_bytes"],19200)
        self.code("PAYLOAD_SIZE_INVALID",b.render,NEUTRAL,(3,64),tuple(range(4801)))
        ex["oversize"] = "x"*65536
        refresh(ex,ev,se)
        self.code("METADATA_SIZE_INVALID",v.verify_bundle,ex,ev,se,h)

    def test_14_immutability_profile_and_digest(self):
        s = b.WindowSpec(0,0)
        with self.assertRaises(FrozenInstanceError):
            s.stream = 2
        recipe = s.recipe()
        recipe["group"]["seed"] = "changed"
        self.assertEqual(s.recipe()["group"]["seed"],"s2nw-pcm-001")
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
        self.code("GAIN_FORM_INVALID",b.render,NEUTRAL,(3,9),(0,))
        with patch.object(b,"group_value",return_value=float("inf")):
            self.code("PCM_DOMAIN_INVALID",b.render,NEUTRAL,(3,64),(0,))
        ex,ev,se,h = bundle()
        ex["prediction_execution_authorized"] = True
        refresh(ex,ev,se)
        self.code("AUTHORIZATION_INVALID",v.verify_bundle,ex,ev,se,h)
        self.assertIs(b.MAIN_GATE,False)
        self.assertFalse(any(n.startswith("mcm_field_organism") or "_s2nj_private" in n or n=="numpy" for n in sys.modules))


    def test_17_update_positions_after_observation(self):
        ex,ev,se,h = bundle()
        train = ex["forecast_sites"][:4]
        self.assertEqual([x["site_id"] for x in train],["t01","t02","t03","t04"])
        self.assertEqual([x["target"] for x in train],[2,3,4,5])
        self.assertTrue(all(x["update_after_target"] for x in train))
        for site in ex["forecast_sites"]:
            self.assertNotIn(site["target_source_id"],site["available_source_ids"])
        ex["forecast_sites"][0]["update_after_target"] = False
        refresh(ex,ev,se)
        self.code("FORECAST_SITE_INVALID",v.verify_bundle,ex,ev,se,h)

    def test_18_freeze_and_no_test_updates(self):
        for field,value in (("freeze_before_source","nw-s01-w01"),
                ("test_updates_allowed",True),("reset_prefix_each_stream",False)):
            with self.subTest(field=field):
                ex,ev,se,h = bundle()
                self.assertEqual(ex["learning_schedule"]["freeze_after_site"],"t04")
                self.assertFalse(any(x["update_after_target"] for x in ex["forecast_sites"][4:]))
                ex["learning_schedule"][field] = value
                refresh(ex,ev,se)
                self.code("LEARNING_SCHEDULE_INVALID",v.verify_bundle,ex,ev,se,h)

    def test_19_no_expected_coefficient_or_recipe_input(self):
        for field,value in (("initial_state",dict(n=0,Sxx=0.0,Sxy=0.0,alpha=0.75)),
                ("expected_learned_coefficient",0.75)):
            with self.subTest(field=field):
                ex,ev,se,h = bundle()
                self.assertIsNone(ex["learning_schedule"]["expected_learned_coefficient"])
                ex["learning_schedule"][field] = value
                refresh(ex,ev,se)
                self.code("LEARNING_SCHEDULE_INVALID",v.verify_bundle,ex,ev,se,h)

    def test_20_counters_budget_and_phase_isolation(self):
        for section in ("counter","budget","authorization"):
            with self.subTest(section=section):
                ex,ev,se,h = bundle()
                if section == "counter":
                    se["completed_sources"] = 25
                    code = "COUNTERS_INVALID"
                elif section == "budget":
                    ex["budgets"]["windows"] = 20
                    code = "PROFILE_BUDGET_INVALID"
                else:
                    ex["learning_execution_authorized"] = True
                    code = "AUTHORIZATION_INVALID"
                refresh(ex,ev,se)
                self.code(code,v.verify_bundle,ex,ev,se,h)


if __name__=="__main__":
    unittest.main()
