"""Neutral NZ binding tests; no NZ windows or receptor modules allowed."""
from dataclasses import FrozenInstanceError
import hashlib
import math
import struct
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from tools import _s2nz_private_source_binding as b
from tools import _s2nz_private_preseal_verification as v
from tests.test_s2ny_private_source_binding import nx_fixture,extract,reseal

NEUTRAL=((113.0,0.09,0.13),(227.0,0.0,0.27),(349.0,0.03,0.41))


def bundle():
    frozen=extract(*nx_fixture())
    sources=[b.bind_source(s,b.digest(s.recipe())) for s in b.specs()]
    hashes={"neutral":"0"*64}
    ex=b.execution_plan(sources,{"neutral":True},hashes,{"neutral":True},frozen)
    ev=b.evaluation_plan(ex)
    se=b.sealed(dict(schema="s2nz.source-seal.v1",status="S2NZ_SOURCES_PRESEALED",run_id="neutral",
        execution_digest=ex["execution_digest"],evaluation_digest=ev["evaluation_digest"],
        hashes_before=hashes,hashes_after=hashes,freeze_import_digest=frozen["freeze_import_digest"],
        attempted_sources=30,completed_sources=30,generated_pcm_bytes=576000,max_live_payloads=1,
        raw_payloads_persisted=0,noise_hashes=72000,main_gate_after=False,collisions=b.common.collision_groups(sources),
        **{key:0 for key in b.FORBIDDEN_CALLS}),"seal_digest")
    return ex,ev,se,hashes,frozen


def refresh(ex,ev,se):
    reseal(ex,"execution_digest")
    ev["execution_digest"]=se["execution_digest"]=ex["execution_digest"]
    reseal(ev,"evaluation_digest")
    se["evaluation_digest"]=ev["evaluation_digest"]
    reseal(se,"seal_digest")


class SourceTests(unittest.TestCase):
    def setUp(self):
        for module in (b,b.old,b.old.pure,b.old.pure.pure):
            for name in ("pcm_window","preseal_once"):
                guard=patch.object(module,name,side_effect=AssertionError("corpus entry forbidden"))
                guard.start()
                self.addCleanup(guard.stop)

    def code(self,code,fn,*args):
        with self.assertRaises(b.S2NZError) as caught:
            fn(*args)
        self.assertEqual(caught.exception.code,code)

    def test_01_literal_sources(self):
        rows=[s.payload() for s in b.specs()]
        self.assertEqual(len(rows),30)
        self.assertEqual(len({r["source_id"] for r in rows}),30)
        self.assertEqual([r["recipe"]["gain_ratio"][0] for r in rows],
            [128,320,368,380,383]*2+[128,320,464,572,653]*2+[128,320,464,464,464]*2)
        self.assertEqual(b.NOISE_SEEDS,(None,"s2nz-noise-001",None,"s2nz-noise-002",None,"s2nz-noise-003"))
        self.code("WINDOW_SPEC_INVALID",b.WindowSpec,True,0)
        self.code("WINDOW_SPEC_INVALID",b.WindowSpec,0,5)
        self.code("PAYLOAD_HASH_INVALID",b.bind_source,b.WindowSpec(0,0),"x"*64)

    def test_02_native_times(self):
        for n,s in enumerate(b.specs()):
            r=s.payload()
            self.assertEqual((r["window_start_sample"],r["window_end_sample"],r["nj_snapshot_index"]),(n*4800,(n+1)*4800,n*10))
        for start in (-480,1,480.0,True):
            with self.subTest(start=start):
                self.code("NATIVE_TIME_INVALID",b.native_index,start)

    def test_03_exact_copy_distinct_identity(self):
        a,c=[b.bind_source(b.WindowSpec(s,0),"a"*64) for s in (0,2)]
        self.assertEqual(a["recipe_digest"],c["recipe_digest"])
        self.assertNotEqual(a["source_digest"],c["source_digest"])
        self.assertNotEqual(a["window_start_sample"],c["window_start_sample"])
        self.assertNotEqual(b.WindowSpec(0,0).recipe(),b.WindowSpec(1,0).recipe())

    def test_04_noise_hash_index_and_scale(self):
        for k,j in ((0,0),(1,173),(4,4799)):
            u=int.from_bytes(hashlib.sha256(f"nz-neutral:{k}:{j}".encode("ascii")).digest()[:4],"little")
            expected=(1.0/1024.0)*((float(u)/4294967296.0)*2.0-1.0)
            self.assertEqual(b.noise_value("nz-neutral",k,j).hex(),expected.hex())
        self.code("NOISE_INDEX_INVALID",b.noise_value,"nz-neutral",5,0)
        self.code("NOISE_SEED_INVALID",b.noise_value,"not a seed",0,0)

    def test_05_synthesis_gain_noise_rounding_reference(self):
        indices=(0,173,4799)
        actual=b.render(NEUTRAL,(37,1024),indices,"nz-neutral",2)
        expected=[]
        for j in indices:
            total=0.0
            for f,a,phase in NEUTRAL:
                total=total+a*math.sin(((math.tau*f)*(float(j)/48000.0))+phase)
            u=int.from_bytes(hashlib.sha256(f"nz-neutral:2:{j}".encode("ascii")).digest()[:4],"little")
            noise=(1.0/1024.0)*((float(u)/4294967296.0)*2.0-1.0)
            expected.append(struct.pack("<f",total*(37.0/1024.0)+noise))
        self.assertEqual(actual,b"".join(expected))

    def test_06_order_and_single_rounding(self):
        events=[]
        raw=(0.1+2.0**-28,-0.2+2.0**-29,0.3)
        pack=struct.pack_into
        def group(_,time):
            index=len([x for x in events if x=="group"])
            events.append("group")
            return raw[index]
        def noise(seed,k,j):
            events.append("noise")
            return 2.0**-15
        def write(*args):
            events.append("pack")
            return pack(*args)
        with patch.object(b,"group_value",side_effect=group),patch.object(b,"noise_value",side_effect=noise),\
             patch.object(b.struct,"pack_into",side_effect=write) as calls:
            result=b.render(NEUTRAL,(71,1024),(0,1,2),"nz-neutral",0)
        self.assertEqual(events,["group","noise","pack"]*3)
        expected=[x*(71.0/1024.0)+2.0**-15 for x in raw]
        self.assertEqual([c.args[3] for c in calls.call_args_list],expected)
        self.assertEqual(result,b"".join(struct.pack("<f",x) for x in expected))

    def test_07_clean_path_no_noise(self):
        with patch.object(b,"noise_value",side_effect=AssertionError("no noise on clean")):
            actual=b.render(NEUTRAL,(37,1024),(0,173,4799))
        self.assertEqual(actual,b.old.render(NEUTRAL,(37,1024),(0,173,4799)))

    def test_08_domain_and_resource_fail_closed(self):
        for gain in ((1,64),(True,1024),(1025,1024)):
            with self.subTest(gain=gain):
                self.code("GAIN_FORM_INVALID",b.render,NEUTRAL,gain,(0,))
        self.code("PAYLOAD_SIZE_INVALID",b.render,NEUTRAL,(1,1024),tuple(range(4801)))
        self.code("NOISE_BINDING_INVALID",b.render,NEUTRAL,(1,1024),(0,),None,0)
        for value in (2.0,float("inf")):
            with self.subTest(value=value),patch.object(b,"group_value",return_value=value):
                self.code("PCM_DOMAIN_INVALID",b.render,NEUTRAL,(1024,1024),(0,))

    def test_09_phase_and_zero_partial_positions(self):
        recipe=dict(seed="nz-neutral-phase",partials=[dict(frequency_ratio=[113,1],amplitude_ratio=[0,1]),
            dict(frequency_ratio=[227,1],amplitude_ratio=[1,10])])
        actual=b.prepare_groups([recipe])[0]
        for p,row in enumerate(actual):
            u=int.from_bytes(hashlib.sha256(f"nz-neutral-phase:{p}".encode("ascii")).digest()[:4],"little")
            self.assertEqual(row[2].hex(),((float(u)/4294967296.0)*math.tau).hex())
        self.assertEqual(actual[0][1],0.0)
        self.assertEqual(len(actual),2)

    def test_10_independent_complete_bundle(self):
        args=bundle()
        before=b.canonical(args)
        with patch.object(b,"specs",side_effect=AssertionError("no primary sources")),\
             patch.object(b,"forecast_sites",side_effect=AssertionError("no primary sites")),\
             patch.object(b,"execution_plan",side_effect=AssertionError("no primary plan")),\
             patch.object(b,"render",side_effect=AssertionError("no generation")):
            result=v.verify_bundle(*args)
        self.assertEqual(result["windows"],30)
        self.assertEqual(result["diagnostic_focus_N"],4)
        self.assertEqual(b.canonical(args),before)

    def test_11_source_time_tampering(self):
        for key,value in (("nj_snapshot_index",1),("source_id","other"),("window_start_sample",1)):
            with self.subTest(key=key):
                ex,ev,se,h,f=bundle()
                ex["sources"][0][key]=value
                reseal(ex["sources"][0],"source_digest")
                refresh(ex,ev,se)
                self.code("WINDOW_BINDING_INVALID",v.verify_bundle,ex,ev,se,h,f)

    def test_12_noise_recipe_tampering(self):
        for key,value in (("seed","substitute"),("amplitude_ratio",[2,1024]),("window",4)):
            with self.subTest(key=key):
                ex,ev,se,h,f=bundle()
                row=ex["sources"][5]
                row["recipe"]["noise"][key]=value
                row["recipe_digest"]=b.digest(row["recipe"])
                reseal(row,"source_digest")
                refresh(ex,ev,se)
                self.code("WINDOW_BINDING_INVALID",v.verify_bundle,ex,ev,se,h,f)

    def test_13_source_order_and_count(self):
        self.code("SOURCE_COUNT_INVALID",b.execution_plan,[],{},{},{},{})
        for key in ("source_order","sources"):
            with self.subTest(key=key):
                ex,ev,se,h,f=bundle()
                ex[key].reverse()
                refresh(ex,ev,se)
                self.code("SOURCE_ORDER_INVALID" if key=="source_order" else "WINDOW_BINDING_INVALID",v.verify_bundle,ex,ev,se,h,f)

    def test_14_forecast_sites_and_history_reset(self):
        sites=b.forecast_sites()
        self.assertEqual(len(sites),18)
        self.assertEqual(sum(s["local_available"] for s in sites),12)
        for s in sites:
            if s["target"]==2:
                self.assertIsNone(s["previous_error_site"])
        ex,ev,se,h,f=bundle()
        ex["forecast_sites"][0]["available_source_ids"].append("nz-s01-w02")
        refresh(ex,ev,se)
        self.code("FORECAST_SITE_INVALID",v.verify_bundle,ex,ev,se,h,f)

    def test_15_observed_target_boundary(self):
        for key in ("clean_counterpart_as_input","clean_counterpart_as_target"):
            with self.subTest(key=key):
                ex,ev,se,h,f=bundle()
                self.assertFalse(ex["prediction_contract"][key])
                ex["prediction_contract"][key]=True
                refresh(ex,ev,se)
                self.code("PREDICTOR_BOUNDARY_INVALID",v.verify_bundle,ex,ev,se,h,f)

    def test_16_focus_four_and_no_success_status(self):
        ex,ev,se,h,f=bundle()
        self.assertEqual(ev["focus"],dict(site_ids=["p05","p06","p11","p12"],N=4,
            emitted_denominator="D_SEPARATE",abstention_removes_case=False))
        self.assertEqual(ev["criteria"],[])
        self.assertIsNone(ev["practical_threshold"])
        self.assertFalse(ev["practical_success_status"])
        ev["focus"]["N"]=3
        refresh(ex,ev,se)
        self.code("EVALUATION_BINDING_INVALID",v.verify_bundle,ex,ev,se,h,f)

    def test_17_counters_and_budget(self):
        for mode in ("counter","budget","noise"):
            with self.subTest(mode=mode):
                ex,ev,se,h,f=bundle()
                if mode=="budget":
                    ex["budgets"]["max_live_payloads"]=2
                elif mode=="noise":
                    se["noise_hashes"]=1
                else:
                    se["completed_sources"]=29
                refresh(ex,ev,se)
                self.code("PROFILE_BUDGET_INVALID" if mode=="budget" else "COUNTERS_INVALID",v.verify_bundle,ex,ev,se,h,f)

    def test_18_plan_immutability_and_roles(self):
        spec=b.WindowSpec(0,0)
        with self.assertRaises(FrozenInstanceError):
            spec.stream=2
        recipe=spec.recipe()
        recipe["group"]["seed"]="changed"
        self.assertEqual(spec.recipe()["group"]["seed"],"s2nz-pcm-001")
        ex,ev,se,h,f=bundle()
        self.assertNotIn("categories",ex)
        ex["categories"]=ev["categories"]
        refresh(ex,ev,se)
        self.code("EXECUTION_FORM_INVALID",v.verify_bundle,ex,ev,se,h,f)

    def test_19_builtin_math(self):
        module=SimpleNamespace(__name__="math",__spec__=SimpleNamespace(origin="built-in"))
        self.assertEqual(b.common.common.math_identity(module,("math",)),
            dict(kind="BUILT_IN",module_name="math",spec_origin="built-in",builtin_membership=True))
        with self.assertRaisesRegex(ValueError,"^MATH_BUILTIN_BINDING_INVALID$"):
            b.common.common.math_identity(module,())

    def test_20_frozen_import_unchanged(self):
        args=nx_fixture()
        before=b.canonical(args)
        frozen=extract(*args)
        self.assertFalse(frozen["owners_reopened"])
        self.assertFalse(frozen["historical_arithmetic_replayed"])
        self.assertEqual(before,b.canonical(args))
        ex,ev,se,h,f=bundle()
        ex["freeze_import"]["histories"][0]["alpha_binary64_hex"]="0x0.0p+0"
        reseal(ex["freeze_import"],"freeze_import_digest")
        refresh(ex,ev,se)
        self.code("FREEZE_IMPORT_INVALID",v.verify_bundle,ex,ev,se,h,f)

    def test_21_collisions_not_deduplicated(self):
        ex,ev,se,h,f=bundle()
        self.assertTrue(se["collisions"])
        self.assertEqual(len(ex["sources"]),30)
        se["collisions"]=[]
        refresh(ex,ev,se)
        self.code("COLLISION_BINDING_INVALID",v.verify_bundle,ex,ev,se,h,f)

    def test_22_profile_and_formula_tampering(self):
        for mode in ("profile","noise"):
            with self.subTest(mode=mode):
                ex,ev,se,h,f=bundle()
                if mode=="profile":
                    ex["profiles"]["half_profile_digest"]="0"*64
                else:
                    ex["noise_contract"]["denominator"]=2048
                refresh(ex,ev,se)
                self.code("PROFILE_BUDGET_INVALID" if mode=="profile" else "NOISE_CONTRACT_INVALID",v.verify_bundle,ex,ev,se,h,f)

    def test_23_historical_import_and_complete_hulls(self):
        before=b.watched()
        f=b.load_freezes()
        self.assertEqual([h["frozen_payload"]["state_digest"] for h in f["histories"]],list(b.old.FREEZE_DIGESTS))
        sources=[b.bind_source(s,b.digest(s.recipe())) for s in b.specs()]
        env,gen=b.environment(),b.generator_identity()
        ex=b.execution_plan(sources,env,before,gen,f)
        prereg=dict(run_id=b.RUN_ID,hashes=before,environment=env,generator=gen,windows=[s.payload() for s in b.specs()],
            freeze_import=f,forecast_sites=b.forecast_sites(),noise_contract=b.noise_contract(),
            prediction_contract=b.prediction_contract(),evaluation=b.evaluation_plan(dict(execution_digest="0"*64)),
            budgets=b.budgets(),retry=False)
        for obj in (ex,b.evaluation_plan(ex),prereg):
            self.assertLessEqual(len(b.canonical(obj)),65536)
        self.assertEqual(before,b.watched())
        ex,ev,se,h,f=bundle()
        ex["oversize"]="x"*65536
        refresh(ex,ev,se)
        self.code("METADATA_SIZE_INVALID",v.verify_bundle,ex,ev,se,h,f)

    def test_24_excluded_modules_and_authorization(self):
        self.assertFalse(any(n.startswith("mcm_field_organism") or "_learning_prediction" in n or
            "_learning_run" in n or "_s2nj_private" in n or n=="numpy" for n in sys.modules))
        self.assertFalse(b.MAIN_GATE)
        self.assertFalse(b.old.MAIN_GATE)
        ex,ev,se,h,f=bundle()
        ex["authorizations"]["local_calls"]=True
        refresh(ex,ev,se)
        self.code("AUTHORIZATION_INVALID",v.verify_bundle,ex,ev,se,h,f)


if __name__=="__main__":
    unittest.main()
