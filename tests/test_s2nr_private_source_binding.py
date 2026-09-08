"""One neutral qualification: never generate any NR payload."""
from copy import deepcopy
from dataclasses import FrozenInstanceError
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import tempfile
from types import SimpleNamespace
import unittest

from tools import _s2nr_private_source_binding as b
from tools import _s2nr_private_preseal_verification as v


def plans():
    specs=b.source_specs()
    rows=[b.bind_source(s,hashlib.sha256(f"synthetic-{0 if i==2 else i}".encode()).hexdigest())
          for i,s in enumerate(specs)]
    x=b.execution_plan(rows,dict(neutral=True),dict(neutral="1"*64),dict(neutral=True))
    return x,b.evaluation_plan(x)


class SourceTests(unittest.TestCase):
    def test_01_literal_recipes_and_distinct_exact_sources(self):
        s=b.source_specs()
        self.assertEqual(17,len(s))
        self.assertEqual([f"nr-a{i:02d}" for i in range(1,7)]+[f"nr-v{i:02d}" for i in range(1,12)],[x.source_id for x in s])
        self.assertEqual(s[0].recipe(),s[2].recipe())
        self.assertNotEqual(s[0],s[2])
        self.assertEqual([1892110,3784220,5676330],[p["frequency_millihz"] for p in s[4].recipe()["groups"][0]["partials"]])
        self.assertEqual([[6,20],[3,40],[3,80]],[p["amplitude_ratio"] for p in s[3].recipe()["groups"][0]["partials"]])

    def test_02_immutable_specs_and_canonical_form(self):
        s=b.source_specs()[0]
        with self.assertRaises(FrozenInstanceError):
            s.kind="RGB"
        copy=s.recipe()
        copy["groups"].clear()
        self.assertEqual(1,len(s.recipe()["groups"]))
        with self.assertRaisesRegex(b.S2NRBindingError,"RECIPE_CANONICAL_INVALID"):
            b.SourceSpec("neutral-a01","PCM",'{ "a": 1 }')
        with self.assertRaisesRegex(b.S2NRBindingError,"SOURCE_ID_INVALID"):
            b.SourceSpec("bad identity","PCM","{}")

    def test_03_neutral_pcm_float32_order(self):
        pcm,_,identity=b.generators()
        recipe=dict(sample_count=16,sample_rate=48000,groups=[dict(seed="neutral-nr-qualification",partials=[
            dict(frequency_millihz=121000,amplitude_ratio=[1,8]),dict(frequency_millihz=363000,amplitude_ratio=[1,16])])])
        actual=pcm(recipe)
        expected=bytearray()
        for j in range(16):
            total=0.0
            for i,(f,a) in enumerate(((121000,(1,8)),(363000,(1,16)))):
                u=int.from_bytes(hashlib.sha256(f"neutral-nr-qualification:{i}".encode()).digest()[:4],"little")
                phase=(float(u)/4294967296.0)*math.tau
                total=total+(float(a[0])/float(a[1]))*math.sin(((math.tau*(float(f)/1000.0))*(float(j)/48000.0))+phase)
            expected.extend(struct.pack("<f",total))
        self.assertEqual(actual,expected)
        self.assertEqual(64,len(actual))
        self.assertFalse(identity["pcm"]["historical_entry_executed"])

    def test_04_neutral_rgb_geometry_and_bit_order(self):
        _,rgb,_=b.generators()
        recipe=b.source_specs()[6].recipe()
        recipe["seed"]="neutral-nr-rgb-qualification"
        image=rgb(recipe)
        try:
            self.assertEqual((1080,1920,3),image.shape)
            self.assertEqual(6220800,image.nbytes)
            self.assertFalse(image.flags.writeable)
            bits=[]
            for block in (0,1):
                for byte in hashlib.sha256(f"neutral-nr-rgb-qualification:{block:03d}".encode()).digest():
                    bits.extend(255 if byte & (1<<bit) else 0 for bit in range(8))
            for i,value in enumerate(bits[:288]):
                cell,channel=divmod(i,3)
                row,col=divmod(cell,12)
                self.assertEqual(value,int(image[row*135,col*160,channel]))
                self.assertEqual(value,int(image[row*135+134,col*160+159,channel]))
        finally:
            del image

    def test_05_literal_events_and_occurrence_identity(self):
        events=b.events()
        self.assertEqual(18,len(events))
        self.assertEqual([2,4,17,18],[e["ordinal"] for e in events if e["event_type"]==b.A])
        self.assertEqual(["nr-a02","nr-a03","nr-a01","nr-a04"]+["nr-a01"]*3+["nr-a02"]*9+["nr-a05","nr-a06"],
                         [e["auditory"]["source_id"] for e in events])
        row=b.bind_source(b.source_specs()[0],"1"*64)
        self.assertEqual([3,5,6,7],[r["ordinal"] for r in row["occurrences"]])
        self.assertEqual(18,len({e["source_occurrence_id"] for e in events}))

    def test_06_native_and_common_times(self):
        for i,e in enumerate(b.events()):
            with self.subTest(ordinal=i+1):
                a=e["auditory"]
                self.assertEqual((4800*i,4800*(i+1),10*i),(a["start_tick"],a["end_tick"],a["endpoint_snapshot_index"]))
                self.assertEqual([100000000*i,100000000*(i+1)],e["field_window"])
                self.assertEqual([100000000*(i+1)-10000000,100000000*(i+1)],a["common_window"])
                if e["visual"] is not None:
                    t=e["visual"]
                    self.assertLess(t["common_window"][0],a["common_window"][0])
                    self.assertEqual((3*i+2,3*i+3),(t["start_tick"],t["end_tick"]))
                else:
                    self.assertEqual(b.A,e["event_type"])

    def test_07_views_and_profile_metadata_only(self):
        x,_=plans()
        self.assertEqual(list(range(24)),x["views"][0]["indices"])
        self.assertEqual([0,3,4,7,8,11,12,15,16,19,20,23,24,27,28,31,32,35,36,39,40,43,44,47],x["views"][1]["indices"])
        for view in x["views"]:
            self.assertEqual(list(range(48)),sorted(view["indices"]+view["complement"]))
        self.assertEqual("s2nj.auditory.hann48.output-half.v1",x["profiles"]["auditory"]["half"]["profile_id"])
        self.assertEqual(0.1,x["retrieval"]["a_threshold"])
        self.assertEqual(0.01,x["retrieval"]["slow_threshold"])

    def test_08_separate_roots_and_valid_shapes(self):
        x,y=plans()
        before=b.digest([x,y])
        v.check_plans(x,y)
        self.assertEqual(before,b.digest([x,y]))
        self.assertNotIn('"target"',json.dumps(x))
        self.assertEqual(["EXACT","LEVEL","FREQUENCY","INDEPENDENT_CONTROL"],[r["subtype"] for r in y["cases"]])
        self.assertEqual("ERHALTUNG_NICHT_GEPRUEFT",y["zero_denominator"])

    def test_09_source_binding_manipulations(self):
        for field,value in (("source_id","nr-a99"),("byte_count",4),("recipe_digest","0"*64)):
            with self.subTest(field=field):
                x,y=plans()
                row=x["sources"][0]
                row[field]=value
                row["source_digest"]=v.sha({k:v for k,v in row.items() if k!="source_digest"})
                x=b.sealed({k:v for k,v in x.items() if k!="execution_digest"},"execution_digest")
                y=b.evaluation_plan(x)
                with self.assertRaisesRegex(b.S2NRBindingError,"SOURCE_FORM_INVALID"):
                    v.check_plans(x,y)

    def test_10_time_mask_and_evaluation_tampering(self):
        for which,code in (("time","AUDIO_TIME_INVALID"),("mask","EXECUTION_FORM_INVALID"),("evaluation","EVALUATION_FORM_INVALID")):
            with self.subTest(which=which):
                x,y=plans()
                if which=="time":
                    x["events"][1]["auditory"]["start_tick"]=0
                elif which=="mask":
                    x["views"][1]["indices"][0]=1
                x=b.sealed({k:v for k,v in x.items() if k!="execution_digest"},"execution_digest")
                y=b.evaluation_plan(x)
                if which=="evaluation":
                    y["cases"][0]["target"]=None
                    y=b.sealed({k:v for k,v in y.items() if k!="evaluation_digest"},"evaluation_digest")
                with self.assertRaisesRegex(b.S2NRBindingError,code):
                    v.check_plans(x,y)

    def test_11_builtin_math_identity(self):
        fake=SimpleNamespace(__name__="math",__spec__=SimpleNamespace(origin="built-in"))
        result=b.common.common.math_identity(fake,("math",))
        self.assertEqual("BUILT_IN",result["kind"])
        with self.assertRaisesRegex(ValueError,"MATH_BUILTIN_BINDING_INVALID"):
            b.common.common.math_identity(fake,())
        fake.__spec__.origin=None
        with self.assertRaisesRegex(ValueError,"MATH_MODULE_ORIGIN_INVALID"):
            b.common.common.math_identity(fake,("math",))

    def test_12_limits_exclusive_writes_and_no_system_imports(self):
        x,y=plans()
        self.assertLess(len(b.canonical(x)),65536)
        self.assertEqual(1,x["budgets"]["max_live_pcm_payloads"])
        self.assertEqual(1,x["budgets"]["max_live_rgb_payloads"])
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"neutral.json"
            b.publish(p,{"neutral":True},100)
            with self.assertRaises(FileExistsError):
                b.publish(p,{"neutral":True},100)
            with self.assertRaisesRegex(b.common.S2NPBindingError,"OUTPUT_SIZE_EXCEEDED"):
                b.publish(Path(folder)/"oversize.json",{"neutral":"x"*100},10)
        self.assertFalse(any(n.startswith("mcm_field_organism") for n in sys.modules))
        self.assertFalse(b.MAIN_GATE)
