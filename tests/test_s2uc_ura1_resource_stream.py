"""Focused bounds, disk cleanup and unchanged-check-path controls."""
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from tools._s2uc_ura1_stream_archive import store,collection,write_archive
from tools._s2uc_ura1_archive_decode import read

ROOT=Path(__file__).resolve().parents[1]


class StreamTests(unittest.TestCase):
    def test_R05_collection_lossless_order_and_cleanup(self):
        with tempfile.TemporaryDirectory() as parent:
            with store(parent) as owner:
                seq=collection()
                for i in range(100):seq.append(dict(index=i,values=[.25,True,None]))
                self.assertEqual([x['index'] for x in seq],list(range(100)))
                self.assertEqual(len(seq),100)
                self.assertFalse(any(isinstance(v,list) for v in seq.__dict__.values()))
                record=dict(events=seq)
                target=Path(parent)/'case.gz';meta=write_archive(record,target)
                sink=io.BytesIO();read(target.read_bytes(),meta['original_sha256'],meta['original_bytes'],sink.write)
                self.assertEqual(json.loads(sink.getvalue()),dict(events=list(seq)))
            self.assertFalse(owner.path.exists())

    def test_R06_record_and_total_bounds_cleanup(self):
        with tempfile.TemporaryDirectory() as parent:
            for total in (False,True):
                with self.assertRaisesRegex(ValueError,'SPOOL_LIMIT'):
                    with store(parent) as owner:
                        seq=collection()
                        if total:owner.bytes=67108864;seq.append(1)
                        else:seq.append('x'*262145)
                self.assertFalse(owner.path.exists())

    def test_R07_original_and_policy_bindings(self):
        for folder in ('ura1-neutral-development-20261014-01','ura1-codec-development-20261014-01'):
            path=ROOT/'reports/s2uc'/folder
            for name,entry in json.loads((path/'closure.json').read_text())['files'].items():
                self.assertEqual(hashlib.sha256((path/name).read_bytes()).hexdigest(),entry['sha256'])
        path=ROOT/'reports/s2uc/ura1-neutral-development-20261014-01/development-binding.json'
        for name,digest in json.loads(path.read_text())['files'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest)
        old=(ROOT/'tools/_s2uc_ura1_neutral.py').read_text()
        new=(ROOT/'tools/_s2uc_ura1_resource_neutral.py').read_text()
        new=new.replace('"""Resource-only fork: identical checks; event collections spool to disk."""\nfrom tools._s2uc_ura1_stream_archive import collection',
                        '"""Bounded hand-fixture development only. No source recipe, matrix or runner."""')
        new=new.replace('events=collection();internal=collection();forecasts=collection();rows=collection()',
                        'events=[];internal=[];forecasts=[];rows=[]')
        self.assertEqual(old,new)


if __name__=='__main__':unittest.main()
