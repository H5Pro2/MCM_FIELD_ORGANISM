import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import _structure_comparison as c
from tools import _structure_comparison_verify as v
from tools import _structure_source_binding as s


def neutral_payload(index):
    index={12:0,13:6}.get(index,index)
    data=bytearray([16]) * 6220800
    # Neutral bands, unrelated to the sealed rectangles and backgrounds.
    start=(200+index*10)*1920*3
    data[start:start+1920*30*3]=bytes([100+index])*(1920*30*3)
    return data


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.root=Path(os.environ.get('STRUCTURE_NEUTRAL_OUT',cls.temp.name))
        cls.root.mkdir(exist_ok=True)
        _,cls.evaluation=s.plans()
        sources=[];proofs=[]
        for i in range(14):
            src=dict(id=f'neutral-{i:02}',frame_index=i,time=[i,30])
            sources.append(src)
            payload=neutral_payload(i)
            proofs.append(dict(id=src['id'],bytes=len(payload),sha256=hashlib.sha256(payload).hexdigest()))
            del payload
        cls.binding=dict(execution=dict(sources=sources),seal=dict(sources=proofs),pairs=cls.evaluation['pairs'],
                         evaluation_digest=s.digest(cls.evaluation),kind='NEUTRAL')
        original=Path.read_bytes
        def blocked(path):
            if 'structure-location-source-seal-' in str(path):raise AssertionError('SEALED_SOURCE_READ_FORBIDDEN')
            return original(path)
        cls.guard=patch.object(Path,'read_bytes',blocked);cls.guard.start()
        c.MAIN_GATE=True
        cls.record,cls.proof=c.execute(cls.binding,cls.root/'success',0,
            lambda src:neutral_payload(src['frame_index']),cls.evaluation)
        if cls.record['status']!='RECORDING_COMPLETE' or cls.proof['status']!='EVIDENCE_VALID':
            raise AssertionError('NEUTRAL_COMPLETION_NOT_REACHED')

    @classmethod
    def tearDownClass(cls):
        cls.guard.stop();cls.temp.cleanup()

    def test_full_native_and_budget(self):
        self.assertEqual(self.record['counts']['differences'],19008)
        self.assertEqual(len(self.record['primary']),44)
        self.assertEqual(self.proof['work']['sums'],88)
        self.assertFalse(c.MAIN_GATE)
        self.assertFalse(c.ledger(self.root/'success',0)['violations'])
        # Count the complete format, not just a placeholder byte string.
        worst=copy.deepcopy(self.record)
        longhex=float.fromhex('0x0.fffffffffffffp-1022').hex()
        for row in worst['rows']:
            row['raw']=[longhex]*288;row['form']=[longhex]*144
        for bank in ('primary','direct'):
            for row in worst[bank]:
                row['terms']=[longhex]*len(row['terms']);row['mean']=longhex
        size=len(s.raw(worst))+16384
        self.assertLessEqual(size,c.CAPS['record.json'])
        c.publish(self.root/'envelope.json',dict(neutral_record_bytes=len(s.raw(self.record)),
            expanded_numeric_envelope_bytes=size,limit=c.CAPS['record.json']))

    def test_arithmetic_independent(self):
        a=tuple([1.0]+[2.0**-53]*287);b=(0.0,)*288
        result=c.distance(a,b)
        self.assertEqual(result['mean'],(sum(abs(a[i]-b[i]) for i in range(288))/288).hex())
        with patch.object(c,'distance',side_effect=AssertionError('PRODUCT_HELPER')):
            self.assertEqual(c.direct_distance(a,b),result)

    def test_missing_form(self):
        result=c.perceive(bytearray(6220800),0)
        self.assertEqual(result['form_status'],'NO_FORM_ACTIVATION')
        self.assertIsNone(result['form'])
        rows=copy.deepcopy(self.record['rows'])
        for row in rows:row.update(result)
        primary,direct,count=c.compare(rows,self.binding['pairs'])
        self.assertEqual(len(primary),44)
        self.assertEqual(sum(x['status']=='UNAVAILABLE' for x in primary),22)
        record=copy.deepcopy(self.record);record.update(rows=rows,primary=primary,direct=direct)
        record['exact'],n=c.exact(rows,self.binding['pairs'])
        record['counts'].update(differences=count,exact_equalities=n)
        proof=v.verify(record,self.binding)
        evaluated=c.evaluate(record,proof,self.evaluation)
        self.assertEqual(evaluated['N'],24)
        self.assertEqual(sum(x['status']=='UNAVAILABLE' for x in evaluated['criteria']),12)

    def test_strict_negative_and_tie(self):
        for relation,status in ((0.0,'TIE'),(-0.5,'FAIL'),(0.5,'PASS')):
            with self.subTest(status=status):
                record=copy.deepcopy(self.record)
                for row in record['primary']:
                    within=row['pair']<20 and row['pair']%5<2
                    row['mean']=(0.5 if within else 0.5+relation).hex()
                proof=dict(status='EVIDENCE_VALID',evaluation_allowed=True,record_digest=s.digest(record))
                result=c.evaluate(record,proof,self.evaluation)
                self.assertTrue(all(x['status']==status for x in result['criteria']))

    def test_mutated_pair(self):
        record=copy.deepcopy(self.record);record['primary'][0]['indices'].reverse()
        with self.assertRaisesRegex(v.VerificationError,'PAIR_BINDING'):v.verify(record,self.binding)

    def test_mutated_source(self):
        record=copy.deepcopy(self.record);record['rows'][0]['source_digest']='0'*64
        with self.assertRaisesRegex(v.VerificationError,'SOURCE_BINDING'):v.verify(record,self.binding)

    def test_direct_mismatch(self):
        record=copy.deepcopy(self.record)
        entry=record['direct'][0];entry['terms'][0]=(0.25).hex()
        entry['mean']=(sum(float.fromhex(x) for x in entry['terms'])/288).hex()
        with self.assertRaisesRegex(v.VerificationError,'DIRECT_MISMATCH'):v.verify(record,self.binding)

    def test_missing_pair(self):
        record=copy.deepcopy(self.record);record['direct'].pop()
        with self.assertRaisesRegex(v.VerificationError,'PAIR_COUNT'):v.verify(record,self.binding)

    def test_evaluation_gate(self):
        with self.assertRaisesRegex(c.ComparisonError,'EVALUATION_FORBIDDEN'):
            c.evaluate(self.record,{},self.evaluation)

    def test_hash_failure_once(self):
        output=self.root/'failure';c.MAIN_GATE=True
        with patch.object(c,'perceive',side_effect=AssertionError('ANALYSIS_BEFORE_HASH')):
            with self.assertRaisesRegex(c.ComparisonError,'PAYLOAD_HASH'):
                c.execute(self.binding,output,0,lambda src:bytearray(10),self.evaluation)
        failure=json.loads((output/'failure.json').read_bytes())
        self.assertEqual(failure['phase'],'PAYLOAD');self.assertEqual(failure['completed'],0)
        self.assertFalse(c.MAIN_GATE)
        c.MAIN_GATE=True
        with self.assertRaisesRegex(c.ComparisonError,'OUTPUT_EXISTS'):
            c.execute(self.binding,output,0,lambda src:None,self.evaluation)

    def test_verifier_read_only(self):
        before=s.raw(self.record)
        with patch.object(c,'perceive',side_effect=AssertionError('RECEPTOR_REPLAY')), \
             patch.object(c,'distance',side_effect=AssertionError('DISTANCE_REPLAY')):
            v.verify(self.record,self.binding)
        self.assertEqual(s.raw(self.record),before)

    def test_budget_boundaries(self):
        self.assertFalse(c.ledger(Path(self.temp.name)/'absent',0,{'record.json':1048576})['violations'])
        self.assertIn('record.json',c.ledger(Path(self.temp.name)/'absent',0,{'record.json':1048577})['violations'])
        self.assertIn('TOTAL',c.ledger(Path(self.temp.name)/'absent',4194304,{})['violations'])
