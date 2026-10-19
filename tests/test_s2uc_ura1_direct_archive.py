"""Focused direct-capture failure, bound, identity and immutability tests."""
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import _s2uc_ura1_direct_archive as codec
from tools._s2uc_ura1_archive_decode import read

ROOT=Path(__file__).resolve().parents[1]


class DirectTests(unittest.TestCase):
    def test_D02_roundtrip_order_metadata_cells(self):
        with tempfile.TemporaryDirectory() as parent,codec.store(parent) as owner:
            seq=codec.collection()
            values=[dict(ordinal=i,ticket=[1,i,0],cells=[None,.25,.5],original=[.25,-0.0],flag=True)
                    for i in (3,7,3)]
            for value in values:seq.append(value)
            raw=codec.canonical(dict(events=values))+b'\n'
            expected=dict(original_bytes=len(raw),original_sha256=hashlib.sha256(raw).hexdigest())
            target=Path(parent)/'case.gz'
            codec.write_archive(dict(events=seq),target,expected)
            sink=io.BytesIO();read(target.read_bytes(),expected['original_sha256'],len(raw),sink.write)
            self.assertEqual(raw,sink.getvalue())
            self.assertEqual(list(seq),values)
            self.assertEqual(owner.temp_peak,target.stat().st_size)
        self.assertTrue(owner.closed);self.assertFalse(owner.nodes);self.assertFalse(seq.ids)

    def test_D03_table_edge_dictionary_index_collection_limits(self):
        for key,message in [('nodes','NODE_LIMIT'),('edges','EDGE_LIMIT'),
                            ('dictionary','DICTIONARY_LIMIT'),('indices','INDEX_LIMIT'),
                            ('collections','COLLECTION_LIMIT')]:
            with self.subTest(bound=key),tempfile.TemporaryDirectory() as parent:
                with self.assertRaisesRegex(ValueError,message):
                    with codec.store(parent) as owner:
                        owner.limits[key]=0
                        seq=codec.collection();seq.append(dict(x=1))
                self.assertTrue(owner.closed);self.assertFalse(owner.nodes)
                self.assertFalse(list(Path(parent).iterdir()))

    def test_D04_record_and_temporary_limit(self):
        with tempfile.TemporaryDirectory() as parent:
            with self.assertRaisesRegex(ValueError,'RECORD_LIMIT'),codec.store(parent):
                codec.collection().append('x'*262145)
            with codec.store(parent),patch.object(codec,'MAX_TEMP',1):
                with self.assertRaisesRegex(ValueError,'TEMP_LIMIT'):
                    codec.write_archive(dict(x=1),Path(parent)/'case.gz',dict(original_bytes=8,original_sha256='0'*64))
            self.assertFalse(list(Path(parent).iterdir()))

    def test_D05_write_and_encoder_failure_cleanup(self):
        for fault in ('write','encoder'):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory() as parent:
                with codec.store(parent) as owner:
                    seq=codec.collection();seq.append(dict(x=1))
                    with self.assertRaisesRegex((OSError,ValueError),'INJECTED_'+fault.upper()):
                        codec.write_archive(dict(events=seq),Path(parent)/'case.gz',
                                            dict(original_bytes=21,original_sha256='0'*64),fault=fault)
                    self.assertGreater(owner.temp_peak,0)
                self.assertFalse(list(Path(parent).iterdir()));self.assertTrue(owner.closed)

    def test_D06_capture_failure_terminates_arm(self):
        from tools import _s2uc_ura1_direct_neutral as neutral
        captured=[];original=neutral.create
        def create(mode):
            arm=original(mode);captured.append(arm);return arm
        with tempfile.TemporaryDirectory() as parent,codec.store(parent) as owner:
            owner.limits['indices']=2
            with patch.object(neutral,'create',create):
                with self.assertRaisesRegex(ValueError,'INDEX_LIMIT'):
                    neutral.run_arm(neutral.blocks([(.125,.25)]*2),'R',trace=True)
            self.assertTrue(captured[0].closed)
            self.assertFalse(any(captured[0].bank))
            self.assertIsNone(captured[0].arm._candidate)
            self.assertFalse(captured[0].arm._retained_many)

    def test_D07_immutable_rules_references_and_check_scope(self):
        for name in ('ura1-neutral-development-20261014-01','ura1-codec-development-20261014-01','ura1-resource-development-20261014-01'):
            folder=ROOT/'reports/s2uc'/name
            for path,entry in json.loads((folder/'closure.json').read_text())['files'].items():
                self.assertEqual(hashlib.sha256((folder/path).read_bytes()).hexdigest(),entry['sha256'])
        for name in ('docs/S2UC_UF1_V1_20261005_CODEBINDUNG.json',
                     'reports/s2uc/ura1-neutral-development-20261014-01/development-binding.json',
                     'reports/s2uc/ura1-codec-development-20261014-01/binding.json',
                     'reports/s2uc/ura1-resource-development-20261014-01/binding.json'):
            for path,digest in json.loads((ROOT/name).read_text())['files'].items():
                self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest,path)
        old=(ROOT/'tools/_s2uc_ura1_resource_neutral.py').read_text()
        new=(ROOT/'tools/_s2uc_ura1_direct_neutral.py').read_text()
        new=new.replace('Direct-capture fork: identical checks; bounded reference collections.',
                        'Resource-only fork: identical checks; event collections spool to disk.')
        new=new.replace('from tools._s2uc_ura1_direct_archive import collection',
                        'from tools._s2uc_ura1_stream_archive import collection')
        self.assertEqual(old,new)

    def test_D08_integer_metadata_key_normalization(self):
        value=dict(observation_end={2:7,10:11,1:3})
        normalized=json.loads(codec.canonical(value))
        raw=codec.canonical(dict(events=[normalized]))+b'\n'
        with tempfile.TemporaryDirectory() as parent,codec.store(parent):
            seq=codec.collection();seq.append(value)
            target=Path(parent)/'case.gz'
            expected=dict(original_bytes=len(raw),original_sha256=hashlib.sha256(raw).hexdigest())
            codec.write_archive(dict(events=seq),target,expected)
            sink=io.BytesIO();read(target.read_bytes(),expected['original_sha256'],len(raw),sink.write)
            self.assertEqual(raw,sink.getvalue())


if __name__=='__main__':unittest.main()
