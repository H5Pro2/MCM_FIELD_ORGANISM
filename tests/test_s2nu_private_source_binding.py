"""One neutral source qualification, no NU payloads or receptor values."""
from copy import deepcopy
from dataclasses import FrozenInstanceError
import hashlib
import math
import struct
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from tools import _s2nu_private_source_binding as b
from tools import _s2nu_private_preseal_verification as v

NEUTRAL = (((113.0,0.09,0.13),(227.0,0.03,0.27)),
           ((349.0,0.07,0.41),),((461.0,0.02,0.59),))


def seal_again(obj,key):
    obj.pop(key,None)
    obj[key] = b.digest(obj)
    return obj


def bundle():
    rows = [b.bind_source(s,b.digest(s.recipe())) for s in b.specs()]
    hashes = {"neutral":"0"*64}
    execution = b.execution_plan(rows,{"neutral":True},hashes,{"neutral":True})
    evaluation = b.evaluation_plan(execution)
    seal = b.sealed(dict(schema="s2nu.source-seal.v1",run_id="neutral",status="S2NU_SOURCES_PRESEALED",
        execution_digest=execution["execution_digest"],evaluation_digest=evaluation["evaluation_digest"],
        hashes_before=hashes,hashes_after=hashes,attempted_sources=30,completed_sources=30,generated_pcm_bytes=576000,
        max_live_payloads=1,raw_payloads_persisted=0,main_gate_after=False,payload_correspondences=b.correspondences(),
        collisions=b.common.collision_groups(rows),receptor_calls=0,nj_calls=0,difference_calls=0,order_evaluations=0,
        memory_calls=0,field_calls=0,context_calls=0,runtime_calls=0),"seal_digest")
    return execution,evaluation,seal,hashes


def refresh(execution,evaluation,seal):
    seal_again(execution,"execution_digest")
    evaluation["execution_digest"] = seal["execution_digest"] = execution["execution_digest"]
    seal_again(evaluation,"evaluation_digest")
    seal["evaluation_digest"] = evaluation["evaluation_digest"]
    seal_again(seal,"seal_digest")


def direct_group(group,time):
    result,index = 0.0,0
    while index < len(group):
        frequency,amplitude,phase = group[index]
        result = result + amplitude*math.sin(((math.tau*frequency)*time)+phase)
        index += 1
    return result


class SourceTests(unittest.TestCase):
    def code(self,code,fn,*args):
        with self.assertRaises(b.S2NUError) as caught:
            fn(*args)
        self.assertEqual(caught.exception.code,code)

    def test_01_sources_and_recipes(self):
        windows = b.specs()
        self.assertEqual(len(windows),30)
        self.assertEqual(len({s.payload()["source_id"] for s in windows}),30)
        self.assertEqual(windows[0].payload()["source_id"],"nu-s01-w00")
        self.assertEqual(windows[-1].payload()["source_id"],"nu-s06-w04")
        self.assertEqual([s.recipe()["expression_id"] for s in windows[::5]],[1,2,2,4,5,6])

    def test_02_native_time(self):
        for n,spec in enumerate(b.specs()):
            row = spec.payload()
            self.assertEqual((row["window_start_sample"],row["window_end_sample"],row["nj_snapshot_index"]),(n*4800,(n+1)*4800,n*10))
        for start in (-480,1,480.0,True):
            with self.subTest(start=start):
                self.code("NATIVE_TIME_INVALID",b.native_index,start)

    def test_03_permutation_keeps_distinct_binding(self):
        for k,j in enumerate((0,3,1,2,4)):
            l,r = b.WindowSpec(2,j),b.WindowSpec(3,k)
            self.assertEqual(l.recipe(),r.recipe())
            self.assertNotEqual(l.payload()["window_start_sample"],r.payload()["window_start_sample"])
            self.assertNotEqual(b.bind_source(l,"a"*64)["source_digest"],b.bind_source(r,"a"*64)["source_digest"])
        self.assertEqual(b.correspondences()[0],["nu-s02-w00","nu-s03-w00"])
        self.assertEqual(b.correspondences()[-1],["nu-s02-w04","nu-s03-w04"])

    def test_04_phases_and_zero_positions(self):
        group = dict(seed="neutral-phase",partials=[dict(frequency_ratio=[101,1],amplitude_ratio=[0,1]),
            dict(frequency_ratio=[203,1],amplitude_ratio=[1,10])])
        values = b.prepare_groups([group])[0]
        self.assertEqual(len(values),2)
        for p,value in enumerate(values):
            u = int.from_bytes(hashlib.sha256(f"neutral-phase:{p}".encode()).digest()[:4],"little")
            self.assertEqual(value[2].hex(),((float(u)/4294967296.0)*math.tau).hex())
        self.assertEqual(values[0][1],0.0)
        self.assertNotEqual(values[0][2],values[1][2])

    def test_05_local_and_continuing_time(self):
        j,k = 173,3
        self.assertEqual(b.sample_value(1,k,j,NEUTRAL).hex(),direct_group(NEUTRAL[0],float(j)/48000.0).hex())
        time = float(4800*k+j)/48000.0
        phase_time = time+((4.0/100.0)*(time*time))
        self.assertEqual(b.sample_value(4,k,j,NEUTRAL).hex(),direct_group(NEUTRAL[0],phase_time).hex())
        self.assertEqual(b.sample_value(1,0,j,NEUTRAL),b.sample_value(1,4,j,NEUTRAL))

    def test_06_gain_uses_synthesis_window(self):
        for k in (0,3,1,2,4):
            j = 101
            expected = (0.5+(0.5*(float(4800*k+j)/24000.0)))*direct_group(NEUTRAL[0],float(j)/48000.0)
            self.assertEqual(b.sample_value(2,k,j,NEUTRAL).hex(),expected.hex())

    def test_07_zero_multipliers_do_not_skip_groups(self):
        for expression,group in ((5,NEUTRAL[2]),(6,NEUTRAL[1])):
            with self.subTest(expression=expression),patch.object(b,"group_value",return_value=0.125) as call:
                self.assertEqual(b.sample_value(expression,0,11,NEUTRAL),0.125)
                self.assertEqual(call.call_count,2)
                self.assertEqual(call.call_args.args[0],group)

    def test_08_single_f32_boundary(self):
        values = (0.1+2.0**-28,-0.2+2.0**-29,0.3)
        pack = struct.pack_into
        with patch.object(b,"sample_value",side_effect=values),patch.object(b.struct,"pack_into",wraps=pack) as calls:
            data = b.render(1,0,NEUTRAL,(0,1,2))
            self.assertEqual(calls.call_count,3)
            self.assertEqual([x.args[3] for x in calls.call_args_list],list(values))
        self.assertEqual(data,b"".join(struct.pack("<f",x) for x in values))

    def test_09_all_expressions_neutral(self):
        for expression in (1,2,4,5,6):
            with self.subTest(expression=expression):
                data = b.render(expression,2,NEUTRAL,(0,701,4799))
                expected = []
                for j in (0,701,4799):
                    time = float(j)/48000.0
                    x = direct_group(NEUTRAL[0],time)
                    if expression==1:
                        value = x
                    elif expression==2:
                        value = (0.5+(0.5*(float(9600+j)/24000.0)))*x
                    elif expression==4:
                        t = float(9600+j)/48000.0
                        value = direct_group(NEUTRAL[0],t+((4.0/100.0)*(t*t)))
                    elif expression==5:
                        value = x+(1.0*direct_group(NEUTRAL[2],time))
                    else:
                        w = float(j)/4800.0
                        value = ((1.0-w)*x)+(w*direct_group(NEUTRAL[1],time))
                    expected.append(value)
                self.assertEqual(data,b"".join(struct.pack("<f",x) for x in expected))
                del data

    def test_10_full_neutral_bundle_without_generation(self):
        with patch.object(b,"pcm_window",side_effect=AssertionError("NU forbidden")),patch.object(b,"render",side_effect=AssertionError("render forbidden")):
            result = v.verify_bundle(*bundle())
        self.assertEqual(result["windows"],30)
        self.assertEqual(result["payload_correspondences"],5)
        self.assertFalse(result["payload_bytes_independently_recomputed"])

    def test_11_source_time_tamper(self):
        ex,ev,se,h = bundle()
        ex["sources"][12]["nj_snapshot_index"] = 80
        seal_again(ex["sources"][12],"source_digest")
        refresh(ex,ev,se)
        self.code("WINDOW_BINDING_INVALID",v.verify_bundle,ex,ev,se,h)

    def test_12_permutation_tamper(self):
        ex,ev,se,h = bundle()
        se["payload_correspondences"][1] = ["nu-s02-w01","nu-s03-w01"]
        seal_again(se,"seal_digest")
        self.code("PERMUTATION_BINDING_INVALID",v.verify_bundle,ex,ev,se,h)

    def test_13_unordered_contract_no_sidechannel(self):
        for field in ("source_id","ordinal","native_windows","state_digest"):
            with self.subTest(field=field):
                ex,ev,se,h = bundle()
                ex["controls"][2]["functional_fields"].append(field)
                refresh(ex,ev,se)
                self.code("CONTROL_LEAKAGE_OR_FORM_INVALID",v.verify_bundle,ex,ev,se,h)

    def test_14_evaluation_and_criteria_separate(self):
        ex,ev,se,h = bundle()
        self.assertEqual(len(ev["criteria"]),5)
        self.assertEqual([x["role"] for x in ev["criteria"]],["PRIMARY"]+["DESCRIPTIVE"]*4)
        self.assertNotIn("categories",ex)
        ev["criteria"][0]["operator"] = "LE"
        refresh(ex,ev,se)
        self.code("CRITERIA_BINDING_INVALID",v.verify_bundle,ex,ev,se,h)

    def test_15_resource_limits(self):
        ex,ev,se,h = bundle()
        self.assertTrue(all(len(b.canonical(x))<=65536 for x in (ex,ev,se)))
        self.code("PAYLOAD_SIZE_INVALID",b.render,1,0,NEUTRAL,tuple(range(4801)))
        ex["oversize"] = "x"*65536
        refresh(ex,ev,se)
        self.code("METADATA_SIZE_INVALID",v.verify_bundle,ex,ev,se,h)

    def test_16_immutability_identity_and_exclusions(self):
        spec = b.WindowSpec(1,0)
        with self.assertRaises(FrozenInstanceError):
            spec.stream = 2
        recipe = spec.recipe()
        recipe["groups"][0]["seed"] = "changed"
        self.assertEqual(spec.recipe()["groups"][0]["seed"],"s2nu-pcm-001")
        module = SimpleNamespace(__name__="math",__spec__=SimpleNamespace(origin="built-in"))
        identity = b.common.common.math_identity(module,("math",))
        self.assertEqual(identity,dict(kind="BUILT_IN",module_name="math",spec_origin="built-in",builtin_membership=True))
        with self.assertRaisesRegex(ValueError,"^MATH_BUILTIN_BINDING_INVALID$"):
            b.common.common.math_identity(module,())
        ex,ev,se,h = bundle()
        original = b.canonical([ex,ev,se,h])
        v.verify_bundle(ex,ev,se,h)
        self.assertEqual(original,b.canonical([ex,ev,se,h]))
        ex["profiles"]["half_profile_digest"] = "0"*64
        refresh(ex,ev,se)
        self.code("PROFILE_BUDGET_INVALID",v.verify_bundle,ex,ev,se,h)
        self.assertIs(b.MAIN_GATE,False)
        self.assertFalse(any(n.startswith("mcm_field_organism") or "_s2nj_private" in n for n in sys.modules))


if __name__=="__main__":
    unittest.main()
