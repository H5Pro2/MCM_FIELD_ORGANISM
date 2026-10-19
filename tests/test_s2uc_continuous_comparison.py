import dataclasses
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools.s2uc_continuous_comparison import BoundSource, ROOT, BINDING, PROFILE, TARGETS
from tools._s2uc_continuation_adapter import ContinuationAdapter, consume_prediction
from tools._s2uc_factor_recency import FactorRecencyArm
from tools._s2uc_pair_context_adapter import AdapterError

def adapter():
    return ContinuationAdapter(FactorRecencyArm(PROFILE,'owner'),'stream',hop=67200)

class ContinuousTests(unittest.TestCase):
    def test_manifest_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/BINDING;p.parent.mkdir(parents=True);p.write_text('{}')
            with self.assertRaisesRegex(AdapterError,'MANIFEST_BINDING_INVALID'):BoundSource(tmp)

    def test_bound_file_tampering(self):
        original=Path.read_bytes
        selected=json.loads((ROOT/BINDING).read_bytes())['files'][0]['path']
        def read(p):
            raw=original(p)
            return raw+b' ' if p==ROOT/selected else raw
        with patch.object(Path,'read_bytes',read):
            with self.assertRaisesRegex(AdapterError,'FILE_BINDING_INVALID'):BoundSource()

    def test_all_nine_future_accesses_are_denied_without_forecast(self):
        for target in TARGETS:
            with self.subTest(target=target):
                source=BoundSource();a=adapter()
                for i in range(1,target):
                    sample=source.take(a)
                    if a.pending_prediction is not None:consume_prediction(a,sample)
                    a.accept_perception(sample)
                a.release_prediction()
                with self.assertRaisesRegex(AdapterError,'FUTURE_BEFORE_PREDICTION'):source.take(a)
                self.assertEqual(source.pulls,target-1)
                self.assertTrue(source.closed and a.closed)
                self.assertIsNone(a.pending_prediction)

    def test_source_time_failure_releases_pending(self):
        source=BoundSource();a=adapter()
        for _ in range(2):a.accept_perception(source.take(a))
        source.positions[2]['source_start_sample']+=1
        with self.assertRaisesRegex(AdapterError,'SOURCE_TIME_INVALID'):source.take(a)
        self.assertTrue(a.closed and source.closed);self.assertIsNone(a.pending_prediction)

    def test_runtime_time_failure(self):
        source=BoundSource();a=adapter();original=source.expand
        def expand(obj):
            item=original(obj)
            if isinstance(item,dict) and 'event' in item and 'field' in item:
                item['field']['timed_frames'][0]['frame']['window_start_tick']+=1
            return item
        source.expand=expand
        with self.assertRaisesRegex(AdapterError,'RUNTIME_TIME_INVALID'):source.take(a)
        self.assertTrue(a.closed and source.closed)

    def test_adapter_rejects_unexpected_source_time(self):
        source=BoundSource();a=adapter();sample=source.take(a)
        with self.assertRaisesRegex(AdapterError,'TIME_DISCONTINUITY'):
            a.accept_perception(dataclasses.replace(sample,start_sample=1))
        self.assertTrue(a.closed);source.close()

    def test_close_releases_pending_and_disallows_further_read(self):
        source=BoundSource();a=adapter()
        for _ in range(2):a.accept_perception(source.take(a))
        self.assertIsNotNone(a.pending_prediction);a.finish_story()
        self.assertIsNone(a.pending_prediction)
        with self.assertRaisesRegex(AdapterError,'SOURCE_CLOSED'):source.take(a)
        self.assertFalse(source.cache)

if __name__=='__main__':unittest.main()
