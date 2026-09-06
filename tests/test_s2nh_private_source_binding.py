"""Neutral seeds only; no NH corpus payload or receptor execution."""

from copy import deepcopy
from dataclasses import FrozenInstanceError
import hashlib
import math
from pathlib import Path
import struct
import sys
import tempfile
from types import SimpleNamespace
import unittest

import numpy as np
from tools import _s2nh_private_source_binding as b
from tools import _s2nh_private_preseal_verification as v


class SourceTests(unittest.TestCase):
    def neutral_recipe(self, index=0):
        return b.audio_recipe("neutral-source-qualification-only",index)

    def synthetic_plans(self):
        sources = [b.bind_source(s,"a"*64,19200 if s.kind=="PCM" else 6220800) for s in b.source_specs()]
        x = b.execution_plan(sources,{}, {})
        return x,b.evaluation_plan(x)

    def test_01_source_identity(self):
        a = b.SourceSpec("neutral-a","PCM",b.canonical(self.neutral_recipe()).decode("ascii"))
        c = b.SourceSpec("neutral-b","PCM",a.recipe_json)
        self.assertNotEqual(b.bind_source(a,"a"*64,19200)["source_digest"], b.bind_source(c,"a"*64,19200)["source_digest"])
        with self.assertRaises(FrozenInstanceError):
            a.source_id = "other"

    def test_02_invalid_source(self):
        for sid,kind in (("TARGET","PCM"),("neutral","OTHER")):
            with self.subTest(sid=sid), self.assertRaises(b.S2NHError):
                b.SourceSpec(sid,kind,"{}")

    def test_03_float32_order(self):
        r = self.neutral_recipe(13)
        payload = b.pcm_payload(r)
        def round32(x):
            return struct.unpack("<f",struct.pack("<f",x))[0]
        for j in range(4800):
            theta = ((2.0*math.pi*r["frequency_hz"]*j)/48000)+r["phase"]
            value = round32(round32(round32(r["amplitude"]*math.sin(theta))*r["input_scale"])*r["post_gain"])
            self.assertEqual(payload[4*j:4*j+4],struct.pack("<f",value))

    def test_04_seed_recipe_relations(self):
        a,b1 = self.neutral_recipe(0),self.neutral_recipe(1)
        p,f = self.neutral_recipe(13),self.neutral_recipe(14)
        self.assertEqual(a["frequency_hz"],p["frequency_hz"])
        self.assertEqual(a["phase"],p["phase"])
        self.assertEqual(f["frequency_hz"],b1["frequency_hz"]+7)
        self.assertEqual(f["phase"],b1["phase"])

    def test_05_pcm_fail_closed(self):
        r = self.neutral_recipe()
        r["phase"] = float("nan")
        with self.assertRaises(b.S2NHError): b.pcm_payload(r)
        r = self.neutral_recipe()
        r["sample_count"] = 1
        with self.assertRaises(b.S2NHError): b.pcm_payload(r)

    def test_06_full_rgb_geometry(self):
        recipe = b.rgb_recipe("neutral-rgb-only",False)
        frame = b.rgb_payload(recipe)
        bits=[]
        for i in (0,1):
            for byte in hashlib.sha256(f"neutral-rgb-only:{i:03d}".encode("ascii")).digest():
                bits.extend(255 if byte & (1<<shift) else 0 for shift in range(8))
        grid = np.array(bits[:288],dtype=np.uint8).reshape(8,12,3)
        self.assertEqual(frame.shape,(1080,1920,3))
        self.assertEqual(frame.nbytes,6220800)
        self.assertFalse(frame.flags.writeable)
        for row in range(8):
            for col in range(12):
                self.assertTrue(np.all(frame[row*135:(row+1)*135,col*160:(col+1)*160] == grid[row,col]))

    def test_07_mask_geometry(self):
        frame=b.rgb_payload(b.rgb_recipe("neutral-mask-only",True))
        values=frame[::135,::160].reshape(-1)
        self.assertTrue(np.all(values[32:]==0))
        self.assertEqual(values.shape,(288,))
        self.assertTrue(np.any(values[:32] != 0))
        self.assertTrue(np.all(frame.reshape(8,135,12,160,3) == frame[::135,::160][:,None,:,None,:]))

    def test_08_rgb_fail_closed(self):
        r=b.rgb_recipe("neutral-bad",True)
        r["visible_positions"]=[0]
        with self.assertRaises(b.S2NHError): b.rgb_payload(r)

    def test_09_literal_events(self):
        x,y=self.synthetic_plans()
        v.check_plans(x,y)
        self.assertEqual(sum(e["event_type"]==b.AV for e in x["events"]),20)
        self.assertEqual([e["ordinal"] for e in x["events"] if e["event_type"]==b.A],[3,23,25,27])

    def test_10_native_times(self):
        es=b.events()
        self.assertIsNone(es[3]["auditory"])
        self.assertEqual(es[4]["auditory"]["start_tick"],14400)
        self.assertEqual(es[4]["auditory"]["endpoint_snapshot_index"],30)
        self.assertEqual(es[-2]["auditory"]["end_tick"],115200)
        self.assertEqual(es[-1]["visual"]["end_tick"],84)

    def test_11_time_manipulation(self):
        x,y=self.synthetic_plans()
        x["events"][4]["auditory"]["start_tick"] += 1
        x=b.sealed({k:z for k,z in x.items() if k!="execution_digest"},"execution_digest")
        y=b.evaluation_plan(x)
        with self.assertRaisesRegex(b.S2NHError,"AUDIO_TIME_INVALID"): v.check_plans(x,y)

    def test_12_separate_roots(self):
        x,y=self.synthetic_plans()
        self.assertNotIn("cases",x)
        self.assertNotIn("expected_support",x)
        y["execution_digest"]="b"*64
        y=b.sealed({k:z for k,z in y.items() if k!="evaluation_digest"},"evaluation_digest")
        with self.assertRaisesRegex(b.S2NHError,"ROOT_LINK_INVALID"): v.check_plans(x,y)

    def test_13_metadata_immutability(self):
        x,y=self.synthetic_plans()
        before=deepcopy((x,y))
        v.check_plans(x,y)
        self.assertEqual((x,y),before)
        x["target"]="forbidden"
        x=b.sealed({k:z for k,z in x.items() if k!="execution_digest"},"execution_digest")
        with self.assertRaisesRegex(b.S2NHError,"EXECUTION_KEYS_INVALID"): v.check_plans(x,b.evaluation_plan(x))

    def test_14_builtin_math(self):
        m=SimpleNamespace(__name__="math",__spec__=SimpleNamespace(origin="built-in"))
        self.assertEqual(b.utility.math_identity(m,("math",))["kind"],"BUILT_IN")
        with self.assertRaises(ValueError): b.utility.math_identity(m,())
        m.__spec__.origin="unknown"
        with self.assertRaises(ValueError): b.utility.math_identity(m,())

    def test_15_payload_limits_and_duplicates(self):
        spec=b.SourceSpec("neutral","PCM",b.canonical(self.neutral_recipe()).decode("ascii"))
        with self.assertRaises(b.S2NHError): b.bind_source(spec,"a"*64,19201)
        with self.assertRaises(b.S2NHError): b.bind_source(spec,"bad",19200)
        a=b.bind_source(spec,"a"*64,19200)
        self.assertEqual(b.collisions([a,{**a,"source_id":"neutral-2"}]),[["neutral","neutral-2"]])
        self.assertEqual(b.budgets()["generated_rgb_bytes"],17*6220800)

    def test_16_output_and_write_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"neutral.json"
            b.publish(path,{"v":1})
            with self.assertRaises(FileExistsError): b.publish(path,{"v":2})
            with self.assertRaises(b.S2NHError): b.publish(Path(d)/"oversize.json","x"*b.MAX_BYTES)
            self.assertFalse((Path(d)/"oversize.json").exists())

    def test_17_forbidden_imports_and_gate(self):
        self.assertFalse(b.MAIN_GATE)
        self.assertFalse(any(n.startswith("mcm_field_organism") for n in sys.modules))
        self.assertFalse(any(n.startswith("tools._s2ng") for n in sys.modules))

    def test_18_profile_and_source_forms(self):
        specs=b.source_specs()
        self.assertEqual(len(specs),32)
        self.assertEqual(sum(s.kind=="PCM" for s in specs),15)
        self.assertEqual(sum(s.kind=="RGB_CUE" for s in specs),4)
        profile=b.profile_binding()
        self.assertEqual(profile["auditory"]["band_count"],48)
        self.assertEqual(profile["visual"]["grid_rows"]*profile["visual"]["grid_columns"]*3,288)


if __name__ == "__main__":
    unittest.main()
