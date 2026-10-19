"""Focused tests of one state-delta format, no large-case execution."""
import copy
import gzip
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from tools import _s2uc_ura1_delta_encode as enc
from tools._s2uc_ura1_delta_decode import verify
from tools._s2uc_ura1_capture_integrity import manifest,full_record_digest

ROOT=Path(__file__).resolve().parents[1]


class DeltaTests(unittest.TestCase):
    def fixture(self,parent):
        seq=enc.collection()
        records=[dict(bank='0'*832,original=3,ticket=[1,1,0],cells=[None,.25],vector=[-0.0]*48),
                 dict(bank='0'*20+'a'+'0'*811,original=7,ticket=[0,2,0],cells=[.1,.2],vector=[0.0]*48),
                 dict(bank='0'*21+'b'+'0'*810,original=9,ticket=[0,3,0],cells=[.3,.4],vector=[1.0]*48)]
        for item in records:seq.append(item)
        record=dict(events=seq,neutral=True);proof=manifest(record);expected=full_record_digest(record)
        path=Path(parent)/'case.gz';enc.write_archive(record,path,expected)
        return path,proof,expected,records

    def test_T01_full_bytes_numbers_metadata_and_anchors(self):
        with tempfile.TemporaryDirectory() as p,enc.store(p):
            path,proof,expected,records=self.fixture(p);sink=io.BytesIO()
            verify(path.read_bytes(),proof,expected,sink.write)
            self.assertEqual(sink.getvalue(),enc.canonical(dict(events=records,neutral=True))+b'\n')
            self.assertIn(b'-0.0',sink.getvalue());self.assertIn(b'0.0',sink.getvalue())

    def test_T02_missing_and_swapped_deltas(self):
        for fault in ('missing','swapped'):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory() as p,enc.store(p):
                path,proof,expected,_=self.fixture(p);doc=json.loads(gzip.decompress(path.read_bytes()))
                if fault=='missing':doc['sequences'][0][1].pop()
                else:doc['sequences'][0][1].reverse()
                damaged=gzip.compress(enc.dag.canonical(doc)+b'\n',mtime=0)
                with self.assertRaises(ValueError):verify(damaged,proof,expected)

    def test_T03_changed_span_and_wrong_initial_state(self):
        for fault in ('span','initial'):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory() as p,enc.store(p):
                path,proof,expected,_=self.fixture(p);doc=json.loads(gzip.decompress(path.read_bytes()))
                if fault=='initial':doc['sequences'][0][0]=0
                else:
                    op=next(op for changes in doc['deltas'] for op in changes if op[1]==2)
                    op[2][0][0]+=1
                with self.assertRaises(ValueError):verify(gzip.compress(enc.dag.canonical(doc),mtime=0),proof,expected)

    def test_T04_invalid_delta_path_and_value_references(self):
        for fault in ('delta','path','value'):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory() as p,enc.store(p):
                path,proof,expected,_=self.fixture(p);doc=json.loads(gzip.decompress(path.read_bytes()))
                if fault=='delta':doc['sequences'][0][1][0]=999999
                elif fault=='path':doc['deltas'][0][0][0]=999999
                else:
                    op=next(op for changes in doc['deltas'] for op in changes if op[1]==0);op[2]=999999
                with self.assertRaises(ValueError):verify(gzip.compress(enc.dag.canonical(doc),mtime=0),proof,expected)

    def test_T05_management_record_and_write_failure_cleanup(self):
        for limit in ('dictionary','nodes','edges','indices','collections'):
            with tempfile.TemporaryDirectory() as p:
                with self.assertRaises(ValueError),enc.store(p) as owner:
                    owner.limits[limit]=0;enc.collection().append(dict(x=[1]))
                self.assertTrue(owner.closed);self.assertFalse(owner.pool.nodes)
        with tempfile.TemporaryDirectory() as p,enc.store(p) as owner:
            with self.assertRaisesRegex(ValueError,'RECORD_LIMIT'):enc.collection().append('x'*262145)
            seq=enc.collection();seq.append(dict(x=1));record=dict(events=seq)
            with self.assertRaisesRegex(OSError,'INJECTED_WRITE'):
                enc.write_archive(record,Path(p)/'case.gz',full_record_digest(record),fault=True)
            self.assertFalse(list(Path(p).iterdir()))

    def test_T06_live_small_scope_and_original_bindings(self):
        from tools import _s2uc_ura1_delta_neutral as neutral
        with tempfile.TemporaryDirectory() as p,enc.store(p):
            record=neutral.pair(neutral.blocks([(.125,.25)]*2),trace=True)
            proof=manifest(record);expected=full_record_digest(record);path=Path(p)/'case.gz'
            enc.write_archive(record,path,expected);verify(path.read_bytes(),proof,expected)
        original=(ROOT/'tools/_s2uc_ura1_direct_neutral.py').read_text()
        current=(ROOT/'tools/_s2uc_ura1_delta_neutral.py').read_text().replace(
            'Delta-capture fork: identical checks; bounded previous records.',
            'Direct-capture fork: identical checks; bounded reference collections.').replace(
            'from tools._s2uc_ura1_delta_encode import collection','from tools._s2uc_ura1_direct_archive import collection')
        self.assertEqual(current,original)
        pre=ROOT/'reports/s2uc/ura1-size-preparation-20261015-01/prestart.json'
        for path,digest in json.loads(pre.read_text())['files'].items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest,path)


if __name__=='__main__':unittest.main()
