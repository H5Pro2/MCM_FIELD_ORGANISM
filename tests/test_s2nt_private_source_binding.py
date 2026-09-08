"""Neutral metadata and two-sample generator tests; never generate NT PCM."""
from dataclasses import FrozenInstanceError
import hashlib
import math
from pathlib import Path
import struct
import sys
import tempfile
import unittest

from tools import _s2nt_private_source_binding as b
from tools import _s2nt_private_preseal_verification as v


def bundle():
    rows = [b.bind_source(s, hashlib.sha256(f"neutral-{ {3:1,8:2}.get(s.ordinal,s.ordinal)}".encode()).hexdigest())
            for s in b.source_specs()]
    e = b.execution_plan(rows,dict(neutral=True),dict(neutral="0"*64),dict(neutral=True))
    a = b.evaluation_plan(e)
    s = b.sealed(dict(schema="s2nt.source-seal.v1",status="S2NT_SOURCES_PRESEALED",
        execution_digest=e["execution_digest"],evaluation_digest=a["evaluation_digest"],
        hashes_before=e["source_hashes"],hashes_after=e["source_hashes"],
        attempted_sources=14,completed_sources=14,generated_pcm_bytes=268800,max_live_payloads=1,
        raw_payloads_persisted=0,receptor_calls=0,nj_calls=0,distance_calls=0,memory_calls=0,
        field_calls=0,context_calls=0,runtime_calls=0,main_gate_after=False,
        exact_pairs=[["nt-a01","nt-a03"],["nt-a02","nt-a08"]],
        collisions=b.common.collision_groups(rows)),"seal_digest")
    return e,a,s


def reseal(value,key):
    value.pop(key,None)
    value[key] = b.digest(value)


def rebind(e,a,s):
    reseal(e,"execution_digest")
    a["execution_digest"] = e["execution_digest"]
    reseal(a,"evaluation_digest")
    s.update(execution_digest=e["execution_digest"],evaluation_digest=a["evaluation_digest"])
    reseal(s,"seal_digest")


class SourceTests(unittest.TestCase):
    def reject(self,code,fn,*args):
        with self.assertRaises(b.S2NTBindingError) as caught:
            fn(*args)
        self.assertEqual(caught.exception.code,code)

    def test_01_literal_inventory(self):
        specs = b.source_specs()
        self.assertEqual(len(specs),14)
        self.assertEqual([s.ordinal for s in specs],list(range(1,15)))
        self.assertEqual(specs[4].recipe()["groups"][0]["partials"][2]["frequency_millihz"],5747400)
        self.assertEqual(specs[9].recipe()["groups"][0]["partials"][2]["frequency_millihz"],8713800)

    def test_02_immutable_spec(self):
        spec = b.source_specs()[0]
        with self.assertRaises(FrozenInstanceError):
            spec.ordinal = 2
        copy = spec.recipe()
        copy["groups"][0]["partials"].clear()
        self.assertEqual(len(spec.recipe()["groups"][0]["partials"]),3)

    def test_03_exact_sources_distinct(self):
        specs = b.source_specs()
        for a,c in ((0,2),(1,7)):
            with self.subTest(a=a,c=c):
                self.assertEqual(specs[a].recipe(),specs[c].recipe())
                x,y = (b.bind_source(specs[i],"1"*64) for i in (a,c))
                self.assertNotEqual(x["source_id"],y["source_id"])
                self.assertNotEqual(x["source_digest"],y["source_digest"])
                self.assertNotEqual(x["nj_snapshot_index"],y["nj_snapshot_index"])

    def test_04_group_zero_positions(self):
        for n,seeds in ((6,("s2nt-pcm-001","s2nt-pcm-002")),(7,("s2nt-pcm-001","s2nt-pcm-002")),
                        (11,("s2nt-pcm-002","s2nt-pcm-001")),(12,("s2nt-pcm-002","s2nt-pcm-001"))):
            with self.subTest(n=n):
                groups = b.source_specs()[n-1].recipe()["groups"]
                self.assertEqual(tuple(g["seed"] for g in groups),seeds)
                self.assertEqual([p["amplitude_ratio"] for p in groups[1]["partials"]],[[0,1],[0,1],[1,20]])
                self.assertEqual(groups[0]["partials"][2]["amplitude_ratio"],[0,1] if n in (7,12) else [1,20])

    def test_05_native_time(self):
        for n,start,end,index in ((1,0,4800,0),(2,4800,9600,10),(14,62400,67200,130)):
            with self.subTest(n=n):
                row = b.source_specs()[n-1].payload()
                self.assertEqual((row["window_start_sample"],row["window_end_sample"],row["nj_snapshot_index"]),(start,end,index))
                self.assertEqual(row["clock_id"],"audio.sample")

    def test_06_invalid_start(self):
        for start in (-480,1,481,False,480.0):
            with self.subTest(start=start):
                self.reject("NATIVE_WINDOW_INVALID",b.native_index,start)

    def test_07_forged_native_index(self):
        for field,value in (("nj_snapshot_index",1),("window_start_sample",4801),("clock_id","wrong-clock")):
            with self.subTest(field=field):
                e,a,s = bundle()
                e["sources"][1][field] = value
                reseal(e["sources"][1],"source_digest")
                rebind(e,a,s)
                self.reject("SOURCE_METADATA_INVALID",v.verify_bundle,e,a,s,e["source_hashes"])

    def test_08_pairs_complete(self):
        e,a,s = bundle()
        self.assertEqual(len(e["pairs"]),25)
        self.assertEqual(len({p["pair_id"] for p in e["pairs"]}),25)
        self.assertEqual(e["pairs"][-1]["pair_id"],"d01-02")
        e["pairs"].pop()
        rebind(e,a,s)
        self.reject("PAIR_BINDING_INVALID",v.verify_bundle,e,a,s,e["source_hashes"])

    def test_09_order_controls(self):
        e,a,s = bundle()
        self.assertEqual([sum(x["group"] == g for x in a["order_checks"]) for g in ("PRIMARY","ATTRIBUTION","CONTROL")],[8,4,12])
        self.assertEqual(a["order_checks"][-1]["right"],"d01-02")
        a["order_checks"][0]["operator"] = "LE"
        rebind(e,a,s)
        self.reject("ORDER_BINDING_INVALID",v.verify_bundle,e,a,s,e["source_hashes"])

    def test_10_separate_roots(self):
        e,a,s = bundle()
        for word in ("families","order_checks","independent_controls","operational_admission"):
            self.assertNotIn(word,e)
            self.assertIn(word,a)
        self.assertIsNone(e["diagnostic"]["threshold"])
        self.assertIsNone(a["operational_admission"])
        a["execution_digest"] = "f"*64
        reseal(a,"evaluation_digest")
        self.reject("ROOT_BINDING_INVALID",v.verify_bundle,e,a,s,e["source_hashes"])

    def test_11_neutral_generator_phases_rounding(self):
        pcm,identity = b.pure_generator()
        self.assertEqual(identity["path"],"reports/s2nc/seal_inventory.py")
        self.assertFalse(identity["historical_entry_executed"])
        recipe = dict(sample_count=2,sample_rate=48000,groups=[
            dict(seed="neutral-group-x",partials=[dict(frequency_millihz=f,amplitude_ratio=a)
                for f,a in ((123000,[1,100]),(246000,[0,1]),(492000,[1,200]))]),
            dict(seed="neutral-group-y",partials=[dict(frequency_millihz=f,amplitude_ratio=a)
                for f,a in ((731000,[0,1]),(1462000,[0,1]),(2193000,[1,100]))])])
        angles = []
        class ObservedMath:
            tau = math.tau
            isfinite = staticmethod(math.isfinite)
            @staticmethod
            def sin(angle):
                angles.append(angle)
                return math.sin(angle)
        # This namespace belongs only to the freshly extracted neutral function.
        pcm.__globals__["math"] = ObservedMath
        data = pcm(recipe)
        self.assertEqual(len(data),8)
        self.assertEqual(len(angles),12)
        expected_angles,expected_bytes = [],bytearray()
        for j in range(2):
            value = 0.0
            for group in recipe["groups"]:
                for i,p in enumerate(group["partials"]):
                    word = int.from_bytes(hashlib.sha256((group["seed"]+":"+str(i)).encode("ascii")).digest()[:4],"little")
                    phase = (float(word)/4294967296.0)*math.tau
                    angle = ((math.tau*(float(p["frequency_millihz"])/1000.0))*(float(j)/48000.0))+phase
                    expected_angles.append(angle)
                    n,d = p["amplitude_ratio"]
                    value = value + (float(n)/float(d))*math.sin(angle)
            expected_bytes.extend(struct.pack("<f",value))
        self.assertEqual([x.hex() for x in angles],[x.hex() for x in expected_angles])
        self.assertEqual(data,expected_bytes)

    def test_12_source_identity_mutations(self):
        for mode in ("order","seed","zero"):
            with self.subTest(mode=mode):
                e,a,s = bundle()
                if mode == "order":
                    e["sources"][0],e["sources"][1] = e["sources"][1],e["sources"][0]
                else:
                    row = e["sources"][5]
                    if mode == "seed":
                        row["recipe"]["groups"][1]["seed"] = "wrong-phase"
                    else:
                        row["recipe"]["groups"][1]["partials"][0]["amplitude_ratio"] = [1,20]
                    row["recipe_digest"] = b.digest(row["recipe"])
                    reseal(row,"source_digest")
                rebind(e,a,s)
                self.reject("SOURCE_METADATA_INVALID",v.verify_bundle,e,a,s,e["source_hashes"])

    def test_13_profile_and_budget(self):
        for field in ("profiles","budgets"):
            with self.subTest(field=field):
                e,a,s = bundle()
                e[field] = {}
                rebind(e,a,s)
                self.reject("PROFILE_BUDGET_INVALID",v.verify_bundle,e,a,s,e["source_hashes"])
        self.assertEqual(b.budgets()["both_differences"],2400)
        self.assertEqual(b.budgets()["max_live_payload_bytes"],19200)

    def test_14_publication_limits(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"neutral.json"
            b.publish(path,dict(neutral=True),64)
            with self.assertRaises(FileExistsError):
                b.publish(path,dict(neutral=True),64)
            with self.assertRaises(b.common.S2NPBindingError) as caught:
                b.publish(Path(tmp)/"oversize.json",dict(value="x"*100),64)
            self.assertEqual(str(caught.exception),"OUTPUT_SIZE_EXCEEDED")

    def test_15_valid_bundle_and_collisions(self):
        e,a,s = bundle()
        before = b.canonical((e,a,s))
        result = v.verify_bundle(e,a,s,e["source_hashes"])
        self.assertEqual((result["sources"],result["pairs"],result["order_checks"]),(14,25,24))
        self.assertEqual(len(result["collisions"]),2)
        self.assertEqual(b.canonical((e,a,s)),before)
        s["collisions"] = []
        reseal(s,"seal_digest")
        self.reject("COLLISION_BINDING_INVALID",v.verify_bundle,e,a,s,e["source_hashes"])

    def test_16_math_identity_and_import_boundary(self):
        identity = b.common.common.math_identity(math,sys.builtin_module_names)
        if math.__spec__.origin == "built-in":
            self.assertEqual(identity["kind"],"BUILT_IN")
            self.assertTrue(identity["builtin_membership"])
            with self.assertRaises(ValueError) as caught:
                b.common.common.math_identity(math,())
            self.assertEqual(str(caught.exception),"MATH_BUILTIN_BINDING_INVALID")
        else:
            self.assertEqual(identity["kind"],"FILE_BASED")
        self.assertFalse(any(n.startswith("mcm_field_organism") for n in sys.modules))
        self.assertNotIn("tools._s2nj_private_auditory_output_projection",sys.modules)
        self.assertFalse(b.MAIN_GATE)
