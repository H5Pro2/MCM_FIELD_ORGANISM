"""Incremental length oracle and fused-check mutation controls; small cases only."""
import copy
import gzip
import io
import json
from pathlib import Path
import tempfile
import unittest
from tools import _s2uc_ura1_delta_encode as enc
from tools import _s2uc_ura1_delta_decode as old
from tools import _s2uc_ura1_delta_fast_decode as fast
from tools import _s2uc_ura1_delta_fused as fused
from tools._s2uc_ura1_capture_integrity import manifest,full_record_digest


def blob(doc):return gzip.compress(old.canonical(doc),mtime=0)


def fixture(records,parent):
    seq=enc.collection()
    for item in records:seq.append(item)
    record=dict(events=seq,neutral=True);proof=manifest(record);expected=full_record_digest(record)
    path=Path(parent)/'case.gz';enc.write_archive(record,path,expected)
    return path.read_bytes(),proof,expected


class FastTests(unittest.TestCase):
    def test_O01_incremental_oracle_unicode_numbers_and_container_edits(self):
        records=[{'é\n':{'a':[0,-0.0,True,None,'漢😀\n\\"']},'bank':'a'*160},
                 {'é\n':{'a':[0.0,0.0,False,1,'\t\b\f\r']},'bank':'é😀'+ 'a'*158,'new':{}},
                 {'é\n':{'a':[]},'bank':'"\\'+ 'a'*158,'new':{'x':[1,2,3]}},
                 {'bank':'a'*160}, {}, [], ['é',-0.0], 'x'*160, '😀'+ 'x'*159, 1, 1.0, False, None]
        with tempfile.TemporaryDirectory() as p,enc.store(p):
            data,proof,expected=fixture(records,p);reader=fast.Reader(data);seen=[]
            def oracle(state,size):
                self.assertEqual(size,len(json.dumps(state,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')))
                seen.append(size)
            self.assertEqual(list(reader.records(0,oracle)),[old.canonical(x) for x in records])
            self.assertGreater(len(seen),12)
            a=io.BytesIO();b=io.BytesIO()
            self.assertEqual(old.verify(data,proof,expected,a.write),fast.verify(data,proof,expected,b.write))
            self.assertEqual(a.getvalue(),b.getvalue())

    def test_O02_transient_limit_and_exact_boundary(self):
        # Each assigned value fits; their intermediate containing object does not.
        doc=dict(format='URA1_STATE_DELTA_V1',values=[['scalar','x'*130000],['object',[['a',0]]],
                 ['scalar','y'*140000],['scalar',0]],paths=[['b']],deltas=[[[0,0,2],[0,1]]],
                 sequences=[[1,[0]]],root=3,original_bytes=1,original_sha256='0'*64)
        for decoder in (old,fast):
            with self.assertRaisesRegex(ValueError,'RECORD_LIMIT'):list(decoder.Reader(blob(doc)).records(0))
        for length,valid in [(262141,True),(262142,False)]:
            boundary=copy.deepcopy(doc);boundary.update(values=[['scalar','x'*length]],paths=[],deltas=[],sequences=[[0,[]]],root=0)
            if valid:self.assertEqual(len(next(fast.Reader(blob(boundary)).records(0)))+1,262144)
            else:
                for decoder in (old,fast):
                    with self.assertRaisesRegex(ValueError,'INITIAL_SIZE'):decoder.Reader(blob(boundary))

    def test_O03_corruption_identical_terminal_reasons(self):
        records=[dict(bank='a'*160,x=1),dict(bank='b'+'a'*159,x=2),dict(bank='c'+'a'*159,x=3)]
        with tempfile.TemporaryDirectory() as p,enc.store(p):
            data,proof,expected=fixture(records,p);base=json.loads(gzip.decompress(data))
            for fault in ('missing','swapped','path','value','initial','span','range','tag','envelope','anchor','structure','duplicate'):
                d=copy.deepcopy(base);pr=copy.deepcopy(proof)
                if fault=='missing':d['sequences'][0][1].pop()
                elif fault=='swapped':d['sequences'][0][1].reverse()
                elif fault=='path':d['deltas'][0][0][0]=999999
                elif fault=='value':next(x for x in d['deltas'][0] if x[1]==0)[2]=999999
                elif fault=='initial':d['sequences'][0][0]=0
                elif fault=='span':next(x for x in d['deltas'][0] if x[1]==2)[2][0][0]=1
                elif fault=='range':next(x for x in d['deltas'][0] if x[1]==2)[2][0][0]=9999
                elif fault=='tag':d['deltas'][0][0][1]=99
                elif fault=='envelope':d['original_sha256']='0'*64
                elif fault=='anchor':pr['collections']['/events']['sha256']='0'*64
                elif fault=='structure':pr['folded_sha256']='0'*64
                else:d['values'].append(['object',[['a',0],['a',0]]])
                errors=[]
                for decoder in (old,fast):
                    try:decoder.verify(blob(d),pr,expected)
                    except ValueError as e:errors.append(str(e))
                self.assertEqual(len(errors),2,fault);self.assertEqual(*errors,fault)

    def test_O04_fused_hash_and_independent_pair_negative_controls(self):
        from tools import _s2uc_ura1_delta_neutral as neutral
        with tempfile.TemporaryDirectory() as p,enc.store(p):
            rec=neutral.pair(neutral.blocks([(.125,.25),(.875,.75)]),trace=True)
            expected=full_record_digest(rec)
            actual,details=fused.finish(rec,fused.live_sequences(rec))
            self.assertEqual(actual,expected)
            self.assertTrue(all(v==(1 if k.startswith('/U/') else 2) for k,v in details['passes'].items()))
            # Materialize only this eight-frame fixture for independent mutation controls.
            base={k:v for k,v in rec.items()}
            for arm in ('U','R'):
                base[arm]=dict(rec[arm])
                for field in ('events','internal','forecasts','rows'):base[arm][field]=list(rec[arm][field])
            for fault in ('stock','cell','ticket','original','target','forecast','missing','diagnosis','cleanup','censored'):
                d=copy.deepcopy(base)
                if fault=='stock':d['R']['events'][0]['state']['next_index']+=1
                elif fault=='cell':d['R']['internal'][0]['state']['bank']='changed'
                elif fault=='ticket':d['R']['forecasts'][0]['receipt']['hypotheses'].append({'ticket':99})
                elif fault=='original':d['R']['forecasts'][0]['originals'].append({'ordinal':99})
                elif fault=='target':d['R']['rows'][0]['target']+=2
                elif fault=='forecast':d['R']['forecasts'][0]['index']+=2
                elif fault=='missing':d['R']['events'].pop()
                elif fault=='diagnosis':d['differences'].append({'target':99})
                elif fault=='cleanup':d['R']['cleanup']=False
                else:d['R']['censored_target']=999
                with self.subTest(fault=fault),self.assertRaises(ValueError):fused.finish(d,fused.live_sequences(d))


if __name__=='__main__':unittest.main()
