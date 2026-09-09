"""One bounded neutral source qualification, no OA payload generation."""
import copy
import importlib.abc
import struct
import sys
import unittest
from unittest.mock import patch


class BlockSystem(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        if fullname.startswith("mcm_field_organism") or any(x in fullname for x in
            ("_s2nj_","_s2nn_","_s2mr_","_s2jw_","_s2ng_")):
            raise AssertionError("forbidden system import: "+fullname)


sys.meta_path.insert(0,BlockSystem())
from tools import _s2oa_private_source_binding as b
from tools import _s2oa_private_preseal_verification as v


class SourceTests(unittest.TestCase):
    def bad(self,code,fn,*args):
        with self.assertRaises(b.S2OABindingError) as cm:
            fn(*args)
        self.assertEqual(cm.exception.code,code)

    @classmethod
    def setUpClass(cls):
        cls.specs = b.specs()
        cls.rows = [b.bind_source(s,s["historical_payload_sha256"] or "0"*64) for s in cls.specs]
        cls.ex = b.execution_plan(cls.rows,{}, {}, {})
        cls.ev = b.evaluation_plan(cls.ex)

    def test_01_history_recipe(self):
        pcm,rgb,_ = b.history()
        self.assertEqual(pcm["source_id"],"np-a02")
        self.assertEqual(set((0,2,3,4,5))-set(rgb),set())
        self.assertEqual(pcm["recipe"],b.common.source_specs()[1].recipe())

    def test_02_event_order(self):
        self.assertEqual(len(b.validate_events(b.events())),28)
        rows=b.events(); rows[1],rows[2]=rows[2],rows[1]
        self.bad("EVENT_BINDING_INVALID",b.validate_events,rows)

    def test_03_modalities(self):
        rows=b.events(); v.check_events(rows)
        self.assertEqual([sum(e[k] is not None for e in rows) for k in ("auditory","visual")],[22,26])
        rows[0]["auditory"]=rows[1]["auditory"]
        self.bad("MODALITY_INVALID",v.check_events,rows)

    def test_04_native_indices(self):
        for start,result in ((0,0),(9600,20),(249600,520)):
            with self.subTest(start=start): self.assertEqual(b.native_index(start),result)

    def test_05_invalid_native_indices(self):
        for start in (-480,1,480.0,True):
            with self.subTest(start=start): self.bad("NATIVE_INDEX_INVALID",b.native_index,start)

    def test_06_audio_time(self):
        rows=b.events(); rows[1]["auditory"]["nj_snapshot_index"]=1
        self.bad("AUDIO_TIME_INVALID",v.check_events,rows)

    def test_07_visual_time(self):
        rows=b.events(); rows[1]["visual"]["common_window"][0]+=1
        self.bad("VISUAL_TIME_INVALID",v.check_events,rows)

    def test_08_field_clock(self):
        rows=b.events(); rows[0]["field_clock_id"]="foreign"
        self.bad("FIELD_TIME_INVALID",v.check_events,rows)

    def test_09_field_continuation(self):
        rows=b.events()
        for a,c in zip(rows,rows[1:]): self.assertEqual(a["field_window"][1],c["field_window"][0])
        rows[18]["field_window"][0]=0
        self.bad("FIELD_TIME_INVALID",v.check_events,rows)

    def test_10_neutral_rgb_occlusion(self):
        _,rgb,_=b.generators()
        image=rgb(1)  # Not one of the five OA ordinals.
        before=tuple(int(image[(i//3//12)*135,(i//3%12)*160,i%3]) for i in range(288))
        self.assertIs(b.occlude(image,list(range(32))),image)
        for i in range(288):
            cell,ch=divmod(i,3); row,col=divmod(cell,12)
            self.assertTrue((image[row*135:(row+1)*135,col*160:(col+1)*160,ch] == (before[i] if i<32 else 0)).all())
        self.bad("MASK_BINDING_INVALID",b.occlude,image,list(range(31)))
        del image

    def test_11_neutral_pcm(self):
        pcm,_,_=b.generators()
        recipe=dict(sample_count=16,sample_rate=48000,groups=[dict(seed="neutral-oa-not-source",partials=[dict(frequency_millihz=100000,amplitude_ratio=[0,1])])])
        payload=pcm(recipe)
        self.assertEqual(len(payload),64)
        self.assertEqual(struct.unpack("<16f",payload),(0.0,)*16)

    def test_12_source_identity(self):
        audio=[s for s in self.rows if s["kind"]=="PCM"]
        self.assertEqual(len({s["source_id"] for s in audio}),22)
        self.assertEqual(len({s["source_digest"] for s in audio}),22)
        self.assertEqual(len({s["payload_sha256"] for s in audio}),1)

    def test_13_historical_payload(self):
        s=next(s for s in self.specs if s["kind"]=="PCM")
        self.bad("HISTORICAL_PAYLOAD_MISMATCH",b.bind_source,s,"0"*64)
        s=copy.deepcopy(s); s["time_binding"]["end_tick"]+=1
        self.bad("SOURCE_BINDING_INVALID",b.bind_source,s,"0"*64)

    def test_14_plan_and_evaluation(self):
        with patch.object(b,"generators",side_effect=AssertionError("no generator needed")):
            v.check_plans(self.ex,self.ev)
        self.assertEqual(len(self.ev["cases"]),8)
        self.assertFalse(self.ev["functional_predictions_are_start_gates"])

    def test_15_manipulation(self):
        x=copy.deepcopy(self.ex); x["sources"][0]["recipe"]["ordinal"]=2
        self.bad("ROOT_DIGEST_INVALID",v.check_plans,x,self.ev)
        y=dict(self.ev); y["execution_digest"]="0"*64
        y=b.sealed({k:z for k,z in y.items() if k!="evaluation_digest"},"evaluation_digest")
        self.bad("EVALUATION_LINK_INVALID",v.check_plans,self.ex,y)

    def test_16_budgets(self):
        self.assertLess(len(b.canonical(self.ex)),b.MAX_METADATA_BYTES)
        self.assertEqual(b.budgets()["source_occurrences"],48)
        self.assertEqual(b.budgets()["future_field_contacts"],8544)
        self.bad("SOURCE_COUNT_INVALID",b.execution_plan,self.rows[:-1],{},{},{})

    def test_17_math_origin(self):
        identity=b.common.common.math_identity(b.common.math,sys.builtin_module_names)
        self.assertIsInstance(identity,dict)
        if b.common.math.__spec__.origin=="built-in":
            self.assertIn("math",sys.builtin_module_names)
            self.assertFalse(hasattr(b.common.math,"__file__"))

    def test_18_gates_and_immutability(self):
        before=b.canonical(self.ex)
        b.evaluation_plan(self.ex)
        self.assertEqual(before,b.canonical(self.ex))
        self.assertFalse(b.MAIN_GATE)
        self.assertFalse(any(n.startswith("mcm_field_organism") for n in sys.modules))
        self.assertFalse(any(self.ex[k] for k in self.ex if k.endswith("_authorized")))


if __name__ == "__main__":
    unittest.main()
