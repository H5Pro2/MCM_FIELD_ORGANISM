"""One neutral binding suite. NY and historical corpus generation is blocked."""
from copy import deepcopy
from dataclasses import FrozenInstanceError
import hashlib
import math
import struct
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from tools import _s2ny_private_source_binding as b
from tools import _s2ny_private_preseal_verification as v

NEUTRAL = ((113.0,0.09,0.13),(227.0,0.0,0.27),(349.0,0.03,0.41))


def reseal(obj,key):
    obj.pop(key,None)
    obj[key] = b.digest(obj)


def nx_fixture():
    frozen,closed = {},{}
    for name,alpha in (("H1",0.25),("H2",0.75)):
        binding = dict(history=name,history_digest=b.digest(name),source_digests=[b.digest([name,i]) for i in range(6)])
        state = b.sealed(dict(schema="s2nw.learning-state.v1",profile_digest=b.profile_binding()["half_profile_digest"],
            n=4,Sxx=1.0,Sxy=alpha,alpha=alpha,phase="FROZEN",predecessor="a"*64,observation_digest="b"*64),"state_digest")
        c = {**state,"phase":"CLOSED","predecessor":state["state_digest"]}
        reseal(c,"state_digest")
        frozen[name] = dict(binding=binding,states=dict(primary=deepcopy(state),direct=deepcopy(state)))
        closed[name] = dict(binding=deepcopy(binding),states=dict(primary=deepcopy(c),direct=deepcopy(c)))
    record = b.sealed(dict(status="RECORDING_COMPLETE",main_gate_after=False,execution_digest="e"*64,
        profiles=b.profile_binding(),learning=dict(frozen=frozen,closed=closed)),"record_digest")
    proof = dict(status="S2NX_LEARNING_VERIFIED",read_only=True,baseline_equal=True,verification_calls=1)
    repin(record,proof)
    return record,proof,tuple(frozen[h]["states"]["primary"]["state_digest"] for h in ("H1","H2"))


def repin(record,proof):
    reseal(record,"record_digest")
    proof.update(record_digest=record["record_digest"],execution_digest=record["execution_digest"],
        file_sha256_before=b.digest(record),file_sha256_after=b.digest(record))
    reseal(proof,"verification_digest")


def extract(record,proof,states):
    return b.validate_nx_freezes(record,proof,b.digest(record),record["record_digest"],proof["verification_digest"],states)


def bundle():
    frozen = extract(*nx_fixture())
    sources = [b.bind_source(s,b.digest(s.recipe())) for s in b.specs()]
    hashes = {"neutral":"0"*64}
    ex = b.execution_plan(sources,{"neutral":True},hashes,{"neutral":True},frozen)
    ev = b.evaluation_plan(ex)
    se = b.sealed(dict(schema="s2ny.source-seal.v1",status="S2NY_SOURCES_PRESEALED",run_id="neutral",
        execution_digest=ex["execution_digest"],evaluation_digest=ev["evaluation_digest"],
        hashes_before=hashes,hashes_after=hashes,freeze_import_digest=frozen["freeze_import_digest"],
        attempted_sources=30,completed_sources=30,generated_pcm_bytes=576000,max_live_payloads=1,
        raw_payloads_persisted=0,main_gate_after=False,collisions=b.common.collision_groups(sources),
        **{key:0 for key in b.FORBIDDEN_CALLS}),"seal_digest")
    return ex,ev,se,hashes,frozen


def refresh(ex,ev,se):
    reseal(ex,"execution_digest")
    ev["execution_digest"] = se["execution_digest"] = ex["execution_digest"]
    reseal(ev,"evaluation_digest")
    se["evaluation_digest"] = ev["evaluation_digest"]
    reseal(se,"seal_digest")


class SourceTests(unittest.TestCase):
    def setUp(self):
        for module in (b,b.pure,b.pure.pure):
            guard = patch.object(module,"pcm_window",side_effect=AssertionError("corpus generation forbidden"))
            guard.start()
            self.addCleanup(guard.stop)

    def code(self,code,fn,*args):
        with self.assertRaises(b.S2NYError) as caught:
            fn(*args)
        self.assertEqual(caught.exception.code,code)

    def test_01_literal_sources(self):
        specs = b.specs()
        self.assertEqual(len(specs),30)
        self.assertEqual(len({s.payload()["source_id"] for s in specs}),30)
        self.assertEqual(b.ROWS,(((0,128),(0,320),(0,368),(0,380),(0,383)),
            ((0,128),(0,320),(0,464),(0,572),(0,653)),((0,128),(0,192),(0,320),(0,576),(0,960)),
            ((0,320),(0,320),(0,320),(0,320),(0,320)),((0,128),(0,320),(0,368),(0,320),(0,308)),
            ((0,128),(0,320),(0,464),(1,464),(1,464))))
        self.code("WINDOW_SPEC_INVALID",b.WindowSpec,True,0)
        self.code("WINDOW_SPEC_INVALID",b.WindowSpec,0,5)
        self.code("PAYLOAD_HASH_INVALID",b.bind_source,specs[0],"x"*64)

    def test_02_native_times(self):
        for n,s in enumerate(b.specs()):
            r = s.payload()
            self.assertEqual((r["window_start_sample"],r["window_end_sample"],r["nj_snapshot_index"]),(n*4800,(n+1)*4800,n*10))
        for start in (-480,1,480.0,True):
            with self.subTest(start=start):
                self.code("NATIVE_TIME_INVALID",b.native_index,start)

    def test_03_exact_recipes_distinct_identities(self):
        a,c = (b.bind_source(b.WindowSpec(s,0),"a"*64) for s in (0,1))
        self.assertEqual(a["recipe_digest"],c["recipe_digest"])
        self.assertNotEqual(a["source_digest"],c["source_digest"])
        self.assertNotEqual(a["window_start_sample"],c["window_start_sample"])
        self.assertEqual([b.WindowSpec(3,k).recipe() for k in range(5)],[b.WindowSpec(3,0).recipe()]*5)

    def test_04_phase_null_partial_positions(self):
        group = dict(seed="ny-neutral-phase",partials=[dict(frequency_ratio=[101,1],amplitude_ratio=[0,1]),
            dict(frequency_ratio=[203,1],amplitude_ratio=[1,10])])
        actual = b.prepare_groups([group])[0]
        for p,row in enumerate(actual):
            u = int.from_bytes(hashlib.sha256(f"ny-neutral-phase:{p}".encode("ascii")).digest()[:4],"little")
            self.assertEqual(row[2].hex(),((float(u)/4294967296.0)*math.tau).hex())
        self.assertEqual(actual[0][1],0.0)
        self.assertEqual(len(actual),2)

    def test_05_local_time_group_gain_order(self):
        indices = (0,173,4799)
        payload = b.render(NEUTRAL,(37,1024),indices)
        reference = []
        for j in indices:
            total = 0.0
            for f,a,phase in NEUTRAL:
                total = total+a*math.sin(((math.tau*f)*(float(j)/48000.0))+phase)
            reference.append(struct.pack("<f",(37.0/1024.0)*total))
        self.assertEqual(payload,b"".join(reference))

    def test_06_single_float32_rounding(self):
        values = (0.1+2.0**-28,-0.2+2.0**-29,0.3)
        pack = struct.pack_into
        with patch.object(b.pure,"group_value",side_effect=values),patch.object(b.pure.struct,"pack_into",wraps=pack) as calls:
            payload = b.render(NEUTRAL,(71,1024),(0,1,2))
        self.assertEqual(calls.call_count,3)
        expected = [(71.0/1024.0)*x for x in values]
        self.assertEqual([c.args[3] for c in calls.call_args_list],expected)
        self.assertEqual(payload,b"".join(struct.pack("<f",x) for x in expected))

    def test_07_renderer_boundaries(self):
        for gain in ((3,64),(True,1024),(1025,1024)):
            with self.subTest(gain=gain):
                with self.assertRaises(b.pure.S2NXError) as caught:
                    b.render(NEUTRAL,gain,(0,))
                self.assertEqual(caught.exception.code,"GAIN_FORM_INVALID")
        with self.assertRaises(b.pure.S2NXError) as caught:
            b.render(NEUTRAL,(3,1024),tuple(range(4801)))
        self.assertEqual(caught.exception.code,"PAYLOAD_SIZE_INVALID")

    def test_08_independent_complete_bundle(self):
        args = bundle()
        before = b.canonical(args)
        with patch.object(b,"specs",side_effect=AssertionError("independent sources")),\
             patch.object(b,"forecast_sites",side_effect=AssertionError("independent sites")),\
             patch.object(b,"execution_plan",side_effect=AssertionError("independent plan")),\
             patch.object(b,"render",side_effect=AssertionError("no PCM")):
            result = v.verify_bundle(*args)
        self.assertEqual((result["windows"],result["forecast_sites_bound"],result["local_sites_bound"]),(30,18,12))
        self.assertEqual(b.canonical(args),before)

    def test_09_source_time_tampering(self):
        for key,value in (("nj_snapshot_index",1),("source_id","other"),("window_start_sample",1)):
            with self.subTest(key=key):
                ex,ev,se,h,f = bundle()
                ex["sources"][0][key] = value
                reseal(ex["sources"][0],"source_digest")
                refresh(ex,ev,se)
                self.code("WINDOW_BINDING_INVALID",v.verify_bundle,ex,ev,se,h,f)

    def test_10_source_order_and_count(self):
        self.code("SOURCE_COUNT_INVALID",b.execution_plan,[],{}, {}, {}, {})
        for key in ("source_order","sources"):
            with self.subTest(key=key):
                ex,ev,se,h,f = bundle()
                ex[key].reverse()
                refresh(ex,ev,se)
                self.code("SOURCE_ORDER_INVALID" if key=="source_order" else "WINDOW_BINDING_INVALID",v.verify_bundle,ex,ev,se,h,f)

    def test_11_future_prefix_and_previous_error(self):
        for mutate in ("future","foreign_error"):
            with self.subTest(mutate=mutate):
                ex,ev,se,h,f = bundle()
                if mutate=="future":
                    ex["forecast_sites"][0]["available_source_ids"].append("ny-s01-w02")
                else:
                    ex["forecast_sites"][1]["previous_error_site"]="p04"
                refresh(ex,ev,se)
                self.code("FORECAST_SITE_INVALID",v.verify_bundle,ex,ev,se,h,f)

    def test_12_local_sites_and_reset(self):
        sites = b.forecast_sites()
        self.assertEqual(len(sites),18)
        self.assertEqual(sum(s["local_available"] for s in sites),12)
        for s in sites:
            self.assertFalse(s["updates_allowed"])
            self.assertEqual(len(s["local_source_ids"]),3 if s["target"]>2 else 0)
            if s["target"]==2:
                self.assertIsNone(s["previous_error_site"])
        ex,ev,se,h,f = bundle()
        ex["forecast_sites"][3]["local_available"]=True
        refresh(ex,ev,se)
        self.code("FORECAST_SITE_INVALID",v.verify_bundle,ex,ev,se,h,f)

    def test_13_formula_metadata_isolation(self):
        for key in ("future_values","source_id","expected_history"):
            with self.subTest(key=key):
                ex,ev,se,h,f = bundle()
                ex["prediction_contract"]["predictor_fields"].append(key)
                refresh(ex,ev,se)
                self.code("PREDICTOR_BOUNDARY_INVALID",v.verify_bundle,ex,ev,se,h,f)

    def test_14_twenty_criteria_and_absolute_reporting(self):
        ex,ev,se,h,f = bundle()
        self.assertEqual([c["check_id"] for c in ev["criteria"]],[f"{p}{k:02d}" for p,n in (("R",4),("L",4),("P",4),("W",8)) for k in range(1,n+1)])
        self.assertEqual([c["site_id"] for c in ev["criteria"][-8:]],[p for p in ("p14","p15","p17","p18") for _ in range(2)])
        self.assertTrue(ev["reporting"]["absolute_mae_and_gain_required"])
        self.assertFalse(ev["W_guaranteed"])
        self.assertFalse(ev["W_start_gate"])
        ev["W_start_gate"]=True
        refresh(ex,ev,se)
        self.code("EVALUATION_BINDING_INVALID",v.verify_bundle,ex,ev,se,h,f)

    def test_15_resource_and_counter_limits(self):
        for section in ("counter","budget"):
            with self.subTest(section=section):
                ex,ev,se,h,f = bundle()
                if section=="counter":
                    se["completed_sources"]=29
                else:
                    ex["budgets"]["max_live_payloads"]=2
                refresh(ex,ev,se)
                self.code("COUNTERS_INVALID" if section=="counter" else "PROFILE_BUDGET_INVALID",v.verify_bundle,ex,ev,se,h,f)

    def test_16_immutability_and_evaluation_root(self):
        s = b.WindowSpec(0,0)
        with self.assertRaises(FrozenInstanceError):
            s.stream=2
        recipe = s.recipe()
        recipe["group"]["seed"]="changed"
        self.assertEqual(s.recipe()["group"]["seed"],"s2ny-pcm-001")
        ex,ev,se,h,f = bundle()
        self.assertNotIn("expected_history",ex)
        ex["expected_history"]=ev["expected_history"]
        refresh(ex,ev,se)
        self.code("EXECUTION_FORM_INVALID",v.verify_bundle,ex,ev,se,h,f)

    def test_17_builtin_math_identity(self):
        module = SimpleNamespace(__name__="math",__spec__=SimpleNamespace(origin="built-in"))
        self.assertEqual(b.common.common.math_identity(module,("math",)),
            dict(kind="BUILT_IN",module_name="math",spec_origin="built-in",builtin_membership=True))
        with self.assertRaisesRegex(ValueError,"^MATH_BUILTIN_BINDING_INVALID$"):
            b.common.common.math_identity(module,())

    def test_18_valid_neutral_freeze_payloads(self):
        r,p,states = nx_fixture()
        before = b.canonical((r,p))
        f = extract(r,p,states)
        self.assertEqual([h["frozen_payload"]["state_digest"] for h in f["histories"]],list(states))
        self.assertEqual(f["histories"][0]["alpha_binary64_hex"],(0.25).hex())
        self.assertFalse(f["owners_reopened"])
        self.assertFalse(f["historical_arithmetic_replayed"])
        self.assertEqual(b.canonical((r,p)),before)

    def test_19_freeze_root_and_proof_manipulation(self):
        r,p,states = nx_fixture()
        self.code("NX_ROOT_BINDING_INVALID",b.validate_nx_freezes,r,p,b.digest(r),"0"*64,p["verification_digest"],states)
        p["file_sha256_after"]="0"*64
        reseal(p,"verification_digest")
        self.code("NX_FILE_BINDING_INVALID",extract,r,p,states)

    def test_20_freeze_phase_and_profile(self):
        for key,value in (("phase","TRAIN"),("profile_digest","0"*64)):
            with self.subTest(key=key):
                r,p,states = nx_fixture()
                for arm in ("primary","direct"):
                    state=r["learning"]["frozen"]["H1"]["states"][arm]
                    state[key]=value
                    reseal(state,"state_digest")
                repin(r,p)
                self.code("NX_STATE_FORM_INVALID",extract,r,p,states)

    def test_21_history_swapping_and_state_tampering(self):
        r,p,states=nx_fixture()
        r["learning"]["frozen"]["H1"]["binding"]["history"]="H2"
        repin(r,p)
        self.code("NX_HISTORY_BINDING_INVALID",extract,r,p,states)
        r,p,states=nx_fixture()
        self.code("NX_STATE_BINDING_INVALID",extract,r,p,tuple(reversed(states)))

    def test_22_closed_binding_and_import_mutation(self):
        r,p,states=nx_fixture()
        c=r["learning"]["closed"]["H1"]["states"]["primary"]
        c["predecessor"]="0"*64
        reseal(c,"state_digest")
        repin(r,p)
        self.code("NX_CLOSED_BINDING_INVALID",extract,r,p,states)
        ex,ev,se,h,f=bundle()
        ex["freeze_import"]["histories"][0]["alpha_binary64_hex"]="0x0.0p+0"
        reseal(ex["freeze_import"],"freeze_import_digest")
        refresh(ex,ev,se)
        self.code("FREEZE_IMPORT_INVALID",v.verify_bundle,ex,ev,se,h,f)

    def test_23_historical_read_only_import_and_full_hulls(self):
        before=b.watched()
        frozen=b.load_freezes()
        self.assertEqual([x["frozen_payload"]["state_digest"] for x in frozen["histories"]],list(b.FREEZE_DIGESTS))
        sources=[b.bind_source(s,b.digest(s.recipe())) for s in b.specs()]
        env,gen=b.environment(),b.generator_identity()
        ex=b.execution_plan(sources,env,before,gen,frozen)
        prereg=dict(run_id=b.RUN_ID,hashes=before,environment=env,generator=gen,windows=[s.payload() for s in b.specs()],
            freeze_import=frozen,forecast_sites=b.forecast_sites(),prediction_contract=b.prediction_contract(),
            evaluation=b.evaluation_plan(dict(execution_digest="0"*64)),budgets=b.budgets(),retry=False)
        for obj in (ex,b.evaluation_plan(ex),prereg):
            self.assertLessEqual(len(b.canonical(obj)),65536)
        self.assertEqual(before,b.watched())
        ex,ev,se,h,f=bundle()
        ex["oversize"]="x"*65536
        refresh(ex,ev,se)
        self.code("METADATA_SIZE_INVALID",v.verify_bundle,ex,ev,se,h,f)

    def test_24_excluded_calls_and_typed_authorization(self):
        self.assertFalse(any(n.startswith("mcm_field_organism") or "_learning_prediction" in n
            or "_learning_run" in n or "_s2nj_private" in n or n=="numpy" for n in sys.modules))
        self.assertIs(b.MAIN_GATE,False)
        self.assertIs(b.pure.MAIN_GATE,False)
        ex,ev,se,h,f=bundle()
        ex["authorizations"]["local_calls"]=True
        refresh(ex,ev,se)
        self.code("AUTHORIZATION_INVALID",v.verify_bundle,ex,ev,se,h,f)


if __name__=="__main__":
    unittest.main()
