import copy
import unittest
from dataclasses import asdict
from tools import _structure_av_sources as a


class Tests(unittest.TestCase):
    def fixture(self):
        e=dict(sources=[dict(id=x,recipe=dict(neutral=True)) for x in ('q04','q05','q06')])
        seal=dict(sources=[dict(id=x['id'],sha256=str(i+1)*64,bytes=6220800)
                          for i,x in enumerate(e['sources'])])
        p={x['id']:dict(sha256=y['sha256'],bytes=y['bytes'],source_digest=a.s.digest(x))
           for x,y in zip(e['sources'],seal['sources'])}
        p['q06-cue']=dict(sha256='4'*64,bytes=6220800,parent_sha256='3'*64,components=list(range(32)))
        return e,seal,dict(version=a.VERSION,execution_digest=a.s.digest(e),seal_digest=a.s.digest(seal),
                          files=p,manifest=asdict(a.manifest(p,'a'*64)))

    def test_manifest_order_repeated_source(self):
        e,s,r=self.fixture();a.verify(r,e,s)
        rows=r['manifest']['events']
        self.assertEqual(len(rows),5)
        self.assertEqual(rows[0]['rgb']['path'],rows[1]['rgb']['path'])
        self.assertNotEqual(rows[0]['rgb']['source_id'],rows[1]['rgb']['source_id'])

    def test_times(self):
        _,_,r=self.fixture();rows=r['manifest']['events']
        self.assertEqual([x['audio_index'] for x in rows],[0,20,40,60,None])
        self.assertEqual([x['visual_window'] for x in rows],[(2,3),(8,9),(14,15),(20,21),(26,27)])

    def test_cue_channels(self):
        x=bytearray([123]*12*8*3);a.cue_in_place(x,12,8)
        self.assertEqual(x[:32],bytearray([123]*32));self.assertEqual(x[32:],bytearray(256))

    def test_cue_geometry_error(self):
        with self.assertRaisesRegex(a.SourceError,'CUE_GEOMETRY'):a.cue_in_place(bytearray(3),1,1)

    def test_source_tamper(self):
        e,s,r=self.fixture();r['files']['q04']['sha256']='f'*64
        with self.assertRaisesRegex(a.SourceError,'SOURCE_BINDING'):a.verify(r,e,s)

    def test_time_tamper(self):
        e,s,r=self.fixture();r['manifest']['events'][1]['audio_index']=0
        with self.assertRaisesRegex(a.SourceError,'MANIFEST_BINDING'):a.verify(r,e,s)

    def test_cue_parent_tamper(self):
        e,s,r=self.fixture();r['files']['q06-cue']['parent_sha256']='0'*64
        with self.assertRaisesRegex(a.SourceError,'CUE_BINDING'):a.verify(r,e,s)

    def test_readonly_and_missing_source(self):
        e,s,r=self.fixture();before=copy.deepcopy(r);a.verify(r,e,s);self.assertEqual(r,before)
        del r['files']['q05']
        with self.assertRaisesRegex(a.SourceError,'SOURCE_SET'):a.verify(r,e,s)
