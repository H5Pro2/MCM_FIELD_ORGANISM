"""Neutral source-binding checks; no NS payload generation or system imports."""
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
from unittest.mock import patch

from reports.s2nd.seal_inventory import math_identity
from tools import _s2ns_private_source_binding as b
from tools import _s2ns_private_preseal_verification as v


def plans():
    rows = [b.bind_source(s, hashlib.sha256(f"neutral-{0 if i==2 else i}".encode()).hexdigest())
        for i,s in enumerate(b.source_specs())]
    x = b.execution_plan(rows, dict(neutral=True), dict(neutral="1"*64), dict(neutral=True))
    return x, b.evaluation_plan(x)


def reseal(x, y=None):
    x = b.sealed({k:v for k,v in x.items() if k != "execution_digest"}, "execution_digest")
    return x, b.evaluation_plan(x) if y is None else y


class SourceTests(unittest.TestCase):
    def test_01_literals_and_exact_source_identity(self):
        specs = b.source_specs()
        self.assertEqual([f"ns-a{i:02d}" for i in range(1,8)]+[f"ns-v{i:02d}" for i in range(1,12)], [s.source_id for s in specs])
        self.assertEqual(specs[0].recipe(), specs[2].recipe())
        self.assertNotEqual(b.bind_source(specs[0],"1"*64)["source_digest"], b.bind_source(specs[2],"1"*64)["source_digest"])
        self.assertEqual([279130,1116520,6978250], [p["frequency_millihz"] for p in specs[4].recipe()["groups"][0]["partials"]])
        self.assertEqual([[9,40],[3,40],[3,80]], [p["amplitude_ratio"] for p in specs[3].recipe()["groups"][0]["partials"]])

    def test_02_two_groups_preserve_zero_positions(self):
        groups = b.source_specs()[5].recipe()["groups"]
        self.assertEqual(["s2ns-pcm-001","s2ns-pcm-002"], [g["seed"] for g in groups])
        self.assertEqual([[271000,1084000,6775000],[419000,1676000,10475000]],
            [[p["frequency_millihz"] for p in g["partials"]] for g in groups])
        self.assertEqual([[[6,20],[2,20],[0,1]],[[0,1],[0,1],[1,20]]],
            [[p["amplitude_ratio"] for p in g["partials"]] for g in groups])
        self.assertEqual([3,3], [len(g["partials"]) for g in groups])

    def test_03_neutral_two_group_pcm_and_phase_order(self):
        pcm, _, identity = b.generators()
        seeds = ("neutral-ns-group-a", "neutral-ns-group-b")
        freq = ((127000,254000,889000),(431000,862000,1293000))
        amps = (((1,8),(1,16),(0,1)),((0,1),(0,1),(1,32)))
        recipe = dict(sample_count=16, sample_rate=48000, groups=[dict(seed=seed, partials=[
            dict(frequency_millihz=f, amplitude_ratio=list(a)) for f,a in zip(fs,aa,strict=True)])
            for seed,fs,aa in zip(seeds,freq,amps,strict=True)])
        expected, angles = bytearray(), []
        for j in range(16):
            total = 0.0
            for g in range(2):
                for i in range(3):
                    u = int.from_bytes(hashlib.sha256(f"{seeds[g]}:{i}".encode()).digest()[:4],"little")
                    angle = ((math.tau*(float(freq[g][i])/1000.0))*(float(j)/48000.0))+(float(u)/4294967296.0)*math.tau
                    angles.append(angle)
                    a = amps[g][i]
                    total = total+(float(a[0])/float(a[1]))*math.sin(angle)
            expected.extend(struct.pack("<f", total))
        with patch.object(math, "sin", wraps=math.sin) as sin:
            actual = pcm(recipe)
        self.assertEqual(expected, actual)
        self.assertEqual(64, len(actual))
        self.assertEqual(angles, [c.args[0] for c in sin.call_args_list])
        self.assertEqual(96, sin.call_count)
        self.assertFalse(identity["pcm"]["historical_entry_executed"])

    def test_04_neutral_rgb_geometry(self):
        _, rgb, _ = b.generators()
        recipe = b.source_specs()[7].recipe()
        recipe["seed"] = "neutral-ns-rgb"
        frame = rgb(recipe)
        try:
            self.assertEqual((1080,1920,3), frame.shape)
            self.assertEqual(6220800, frame.nbytes)
            self.assertFalse(frame.flags.writeable)
            bits = []
            for block in (0,1):
                for byte in hashlib.sha256(f"neutral-ns-rgb:{block:03d}".encode()).digest():
                    bits.extend(255 if byte & (1<<bit) else 0 for bit in range(8))
            for i,value in enumerate(bits[:288]):
                cell,channel = divmod(i,3)
                row,col = divmod(cell,12)
                self.assertEqual(value, int(frame[row*135,col*160,channel]))
                self.assertEqual(value, int(frame[row*135+134,col*160+159,channel]))
        finally:
            del frame

    def test_05_frozen_sources_and_invalid_identity(self):
        spec = b.source_specs()[0]
        with self.assertRaises(FrozenInstanceError):
            spec.kind = "RGB"
        copy = spec.recipe()
        copy["groups"].clear()
        self.assertEqual(1, len(spec.recipe()["groups"]))
        with self.assertRaisesRegex(b.common.S2NRBindingError, "SOURCE_ID_INVALID"):
            b.SourceSpec("bad identity", "PCM", "{}")
        with self.assertRaisesRegex(b.S2NSBindingError, "SOURCE_SPEC_INVALID"):
            b.bind_source(b.SourceSpec("ns-a99", "PCM", spec.recipe_json), "1"*64)

    def test_06_native_times_and_no_rolling_indices(self):
        for n,e in enumerate(b.events(),1):
            with self.subTest(ordinal=n):
                a,z = e["auditory"],e["visual"]
                self.assertEqual(((n-1)*4800,n*4800,n-1),(a["start_tick"],a["end_tick"],a["endpoint_snapshot_index"]))
                self.assertEqual([n*100000000-10000000,n*100000000],a["common_window"])
                self.assertEqual("s2ns-pairing-clock", e["pairing_clock_id"])
                self.assertNotIn("hop_start", a)
                if z is not None:
                    self.assertEqual((3*n-1,3*n),(z["start_tick"],z["end_tick"]))
                    self.assertEqual([(3*n-1)*1000000000//30,n*100000000],z["common_window"])
                else:
                    self.assertEqual(b.A,e["event_type"])

    def test_07_complementary_views_and_profiles(self):
        x,_ = plans()
        self.assertEqual([list(range(24)),list(range(24,48))],[p["indices"] for p in x["views"]])
        self.assertEqual(x["views"][0]["indices"], x["views"][1]["complement"])
        self.assertEqual(x["views"][1]["indices"], x["views"][0]["complement"])
        self.assertEqual("s2nj.auditory.hann48.output-half.v1", x["profiles"]["auditory"]["half"]["profile_id"])
        self.assertEqual((0.1,0.01),(x["comparison"]["a_threshold"],x["comparison"]["slow_threshold"]))
        self.assertFalse(x["comparison"]["full_mean_replacement"])

    def test_08_literal_history_continuation(self):
        ev = b.events()
        expected = [1,2,3,4,5,6,7,2,3,4,5,6,7]+[1]*4+[2]*9+[3,4,5,6,7]
        self.assertEqual([f"ns-a{i:02d}" for i in expected], [e["auditory"]["source_id"] for e in ev])
        self.assertEqual([1,8,14],[e["ordinal"] for e in ev if e["starts_fresh_history"]])
        self.assertEqual([1,2,8,14,15,16,17,18,19,20,21,22,23,24,25,26], [e["ordinal"] for e in ev if e["event_type"]==b.AV])
        self.assertEqual(31,len({e["source_occurrence_id"] for e in ev}))
        self.assertEqual([1,14,15,16,17],[r["ordinal"] for r in b.bind_source(b.source_specs()[0],"1"*64)["occurrences"]])

    def test_09_separate_roots_and_unchanged_plans(self):
        x,y = plans()
        before = b.digest([x,y])
        v.check_plans(x,y)
        self.assertEqual(before,b.digest([x,y]))
        self.assertEqual(15,len(y["cases"]))
        self.assertEqual("ERHALTUNG_NICHT_GEPRUEFT",y["zero_denominator"])
        self.assertNotIn('"target"',json.dumps(x))
        self.assertFalse(y["offset_losses_with_gains"])

    def test_10_source_and_group_tampering(self):
        for field,value in (("source_id","ns-a99"),("byte_count",4),("recipe_digest","0"*64),("zero",None)):
            with self.subTest(field=field):
                x,y = plans()
                row = x["sources"][5]
                if field == "zero":
                    row["recipe"]["groups"][1]["partials"].pop(0)
                    row["recipe_digest"] = b.digest(row["recipe"])
                else:
                    row[field] = value
                row["source_digest"] = v.sha({k:v for k,v in row.items() if k != "source_digest"})
                x,y = reseal(x)
                with self.assertRaisesRegex(b.S2NSBindingError,"SOURCE_FORM_INVALID"):
                    v.check_plans(x,y)

    def test_11_time_view_and_root_tampering(self):
        for field,code in (("time","AUDIO_TIME_INVALID"),("view","VIEW_INVALID"),("evaluation","EVALUATION_FORM_INVALID"),("root","ROOT_LINK_INVALID")):
            with self.subTest(field=field):
                x,y = plans()
                if field=="time":
                    x["events"][1]["auditory"]["endpoint_snapshot_index"] = 10
                if field=="view":
                    x["views"][1]["indices"][0] = 0
                x,y = reseal(x)
                if field=="evaluation":
                    y["cases"][0]["target"] = None
                if field=="root":
                    y["execution_digest"] = "0"*64
                y = b.sealed({k:v for k,v in y.items() if k != "evaluation_digest"},"evaluation_digest")
                with self.assertRaisesRegex(b.S2NSBindingError,code):
                    v.check_plans(x,y)

    def test_12_builtin_math_identity(self):
        fake = SimpleNamespace(__name__="math",__spec__=SimpleNamespace(origin="built-in"))
        self.assertEqual("BUILT_IN",math_identity(fake,("math",))["kind"])
        with self.assertRaisesRegex(ValueError,"MATH_BUILTIN_BINDING_INVALID"):
            math_identity(fake,())
        fake.__spec__.origin = None
        with self.assertRaisesRegex(ValueError,"MATH_MODULE_ORIGIN_INVALID"):
            math_identity(fake,("math",))

    def test_13_exclusive_publication_and_limits(self):
        x,y = plans()
        self.assertLess(len(b.canonical(x)),65536)
        self.assertLess(len(b.canonical(y)),65536)
        self.assertEqual((1,1),(x["budgets"]["max_live_pcm_payloads"],x["budgets"]["max_live_rgb_payloads"]))
        self.assertEqual((7,11,31,16,15),tuple(x["budgets"][k] for k in ("pcm_sources","rgb_sources","events","formations","auditory_cues")))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"neutral.json"
            b.publish(path,dict(neutral=True),100)
            with self.assertRaises(FileExistsError):
                b.publish(path,dict(neutral=True),100)
            with self.assertRaisesRegex(b.common.common.S2NPBindingError,"OUTPUT_SIZE_EXCEEDED"):
                b.publish(Path(folder)/"large.json",dict(neutral="x"*100),10)

    def test_14_no_system_imports_and_closed_gates(self):
        self.assertFalse(any(n.startswith("mcm_field_organism") for n in sys.modules))
        self.assertFalse(any(n in sys.modules for n in ("tools._s2nj_private_auditory_output_projection",
            "tools._s2nq_private_mask_scan","tools._s2mr_private_minimal_mcm_runtime")))
        self.assertFalse(b.MAIN_GATE)
        self.assertFalse(b.common.MAIN_GATE)
        self.assertFalse(b.common.common.MAIN_GATE)
