import dataclasses,json,unittest
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path
from tools.s2uc_nasa_comparison import BoundSource,ROOT,CORPUS,PROFILE,TARGETS,validate_window
from tools._s2uc_pair_context_adapter import AdapterError,PerceptionSample,PairContextAdapter
from tools._s2uc_continuation_adapter import ContinuationAdapter,consume_prediction
from tools._s2uc_factor_recency import FactorRecencyArm
from tools.s2uc_continuous_comparison import state

class Probe:
    def __init__(self,i):self.next_index=i;self.closed=False;self.pending_prediction=None
    def _terminate(self):self.closed=True;self.pending_prediction=None

class NasaComparisonTests(unittest.TestCase):
    def test_inventory_and_bound_file_fail_closed(self):
        original=Path.read_bytes
        for filename,code in [('inventory.json','INVENTORY_BINDING'),('window-100.json','FILE_BINDING')]:
            def read(p):
                raw=original(p)
                return raw+b' ' if p==ROOT/CORPUS/filename else raw
            with self.subTest(file=filename),patch.object(Path,'read_bytes',read):
                with self.assertRaisesRegex(AdapterError,code):BoundSource()
    def test_all_49_missing_forecasts_block_before_delivery(self):
        for target in TARGETS:
            with self.subTest(target=target):
                s=BoundSource();s.pulls=target-1;a=Probe(target)
                with self.assertRaisesRegex(AdapterError,'FUTURE_BEFORE_PREDICTION'):s.take(a)
                self.assertEqual(s.deliveries,0);self.assertTrue(s.closed and a.closed)
    def test_all_49_gate_targets_and_pair_bindings(self):
        s=BoundSource();a=Probe(1)
        try:
            for i in range(1,101):
                a.next_index=i
                if i in TARGETS:a.pending_prediction=SimpleNamespace(target_index=i,provenance_json=json.dumps({'input_indices':[i-2,i-1]}),read_revision=i,status='NEUTRAL_GATE_PROBE')
                self.assertEqual(s.take(a).index,i)
            self.assertEqual(s.deliveries,100);self.assertEqual([r['target'] for r in s.log],TARGETS)
            with self.assertRaises(StopIteration):s.take(a)
        finally:s.close()
    def test_wrong_target_or_pair_rejected(self):
        for target,pair,code in [(5,[1,2],'FUTURE_BEFORE_PREDICTION'),(3,[2,3],'PREDICTION_PAIR')]:
            s=BoundSource();s.pulls=2;a=Probe(3);a.pending_prediction=SimpleNamespace(target_index=target,provenance_json=json.dumps({'input_indices':pair}))
            with self.assertRaisesRegex(AdapterError,code):s.take(a)
            self.assertEqual(s.deliveries,0);self.assertIsNone(a.pending_prediction)
    def test_source_time_profile_digest_mutations(self):
        original=json.loads((ROOT/CORPUS/'window-001.json').read_text())
        for section,key,value,code in [('origin','start_sample',1,'SOURCE_TIME'),('projection','profile_digest','0'*64,'PROFILE_CHANGED'),('projection','snapshot_index',1,'PROJECTION_TIME'),('projection','projection_digest','0'*64,'PROJECTION_DIGEST')]:
            d=json.loads(json.dumps(original));d[section][key]=value
            with self.assertRaisesRegex(AdapterError,code):validate_window(d,1)
    def test_error_releases_forecast_and_cache(self):
        s=BoundSource();a=ContinuationAdapter(FactorRecencyArm(PROFILE,'owner'),'stream')
        for _ in range(2):a.accept_perception(s.take(a))
        d=json.loads(s.cache['window-003.json']);d['projection']['values'][0]=.987654321
        s.cache['window-003.json']=json.dumps(d).encode()
        with self.assertRaisesRegex(AdapterError,'PROJECTION_DIGEST'):s.take(a)
        self.assertTrue(a.closed and s.closed);self.assertIsNone(a.pending_prediction);self.assertFalse(s.cache)
    def test_neutral_admission_state_and_end_release(self):
        a=ContinuationAdapter(FactorRecencyArm(PROFILE,'owner'),'stream');b=PairContextAdapter(FactorRecencyArm(PROFILE,'owner'),'stream');ordinals=[]
        admit=a._admit
        def watched(f):
            self.assertIsNotNone(a.pending_prediction);ordinals.append(f.ordinal);admit(f)
        a._admit=watched
        for i in range(1,13):
            x=PerceptionSample((float(i)/20,)*48,PROFILE,'owner','stream',i,(i-1)*4800,i*4800)
            if a.pending_prediction is not None:consume_prediction(a,x);self.assertIsNone(a.pending_prediction)
            self.assertEqual(a.accept_perception(x),b.accept_perception(x));self.assertEqual(state(a.arm),state(b.arm))
        self.assertEqual(ordinals,list(range(1,13)));self.assertEqual(a.pending_prediction.target_index,13)
        a.finish_story();b.finish_story();self.assertIsNone(a.pending_prediction);self.assertEqual(state(a.arm),state(b.arm))
        self.assertEqual(a.admitted,12)

if __name__=='__main__':unittest.main()
