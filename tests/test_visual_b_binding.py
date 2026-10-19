"""Prospectively fixed neutral inputs only; no sealed cue materialization."""
import copy
import math
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from tools import _visual_b_diagnostic as d
from tools import _structure_source_binding as s
from reports import seal_visual_b_once as runner


def slots(support=3):
    return [dict(occupied=True,support=support,values=(0.0,)*288)
            for _ in range(4)]


def cue(first=0.0):
    return (first,)+(0.0,)*31


def source_fixture():
    e,v=d.plans()
    for row in e['rows']:
        row['original_sha256']='a'*64
    proofs=[dict(id=r['id'],source_digest=s.digest(r),original_sha256='a'*64,
                 bytes=6220800,sha256='b'*64) for r in e['rows']]
    record=dict(execution_digest=s.digest(e),evaluation_digest=s.digest(v),
                generated=7,sources=proofs,collisions=[[r['id'] for r in e['rows']]],
                environment_binding='c'*64)
    return record,e,v


class VisualB(unittest.TestCase):
    def setUp(self):
        # Any accidental use of the real source generator in qualification fails.
        p=patch.object(s,'render',side_effect=AssertionError('GENERATION_FORBIDDEN'))
        p.start();self.addCleanup(p.stop)

    def test_01_inclusive_boundary(self):
        for value,expected in ((math.nextafter(d.TAU,0.0),True),(d.TAU,True),
                               (math.nextafter(d.TAU,math.inf),False)):
            with self.subTest(value=value.hex()):
                for call in (d.scan,d.direct):
                    self.assertEqual(bool(call(cue(value),slots(),'MAX32_RGB8_STEP')['matches']),expected)

    def test_02_binary64_terms_and_order(self):
        q=tuple((i+1)/257.0 for i in range(32))
        bank=slots()
        bank[0]['values']=tuple(i/511.0 for i in range(288))
        result=d.scan(q,bank,'MAX32_RGB8_STEP')
        self.assertEqual(result,d.direct(q,bank,'MAX32_RGB8_STEP'))
        self.assertEqual([r['index'] for r in result['rows'][0]['terms']],list(range(32)))
        for i,term in enumerate(result['rows'][0]['terms']):
            self.assertEqual(term['difference'].hex(),abs(q[i]-bank[0]['values'][i]).hex())

    def test_03_complete_scans(self):
        for rule in ('EXACT','MAX32_RGB8_STEP'):
            result=d.scan(cue(),slots(),rule)
            self.assertEqual(len(result['rows']),4)
            self.assertEqual(result['matches'],[0,1,2,3])
            self.assertLessEqual(len(s.raw(result)),32767)

    def test_04_unstable_and_empty(self):
        bank=slots(2)
        bank[1]=dict(occupied=False,support=None,values=())
        for rule in ('EXACT','MAX32_RGB8_STEP'):
            self.assertEqual(d.scan(cue(),bank,rule)['matches'],[])
            self.assertEqual(d.scan(cue(),bank,rule),d.direct(cue(),bank,rule))

    def test_05_historical_exact(self):
        for q in (cue(),cue(-0.0),cue(math.ulp(0.0)),cue(0.25)):
            fixture=SimpleNamespace(values=q+(None,)*256,cue_digest='a'*64,mask_plan_digest='b'*64)
            record,_=d.historical._slot_record(bank_role='B_STABLE_VISUAL',slot_id='slot.000',
                slot_digest='c'*64,values=(0.0,)*288,support=3,cue=fixture)
            self.assertEqual(d.scan(q,slots(),'EXACT')['rows'][0]['matched'],record.observed_match)

    def test_06_a_and_public_resolution_unchanged(self):
        self.assertIs(d.resolve_a,d.historical._resolve_a)
        self.assertIs(d.decide,d.historical._decide)
        b4=SimpleNamespace(status='BANK_MULTIPLE_OBSERVED_MATCHES',scan_digest='a'*64)
        fast=SimpleNamespace(status='BANK_UNIQUE_OBSERVED_MATCH',scan_digest='b'*64)
        finding,count=d.resolve_a(b4,(),fast,())
        self.assertEqual(finding.status,'A_RECENT_INTERNAL_AMBIGUITY')
        self.assertEqual(count,0)
        b=SimpleNamespace(status='B_STABLE_APPLICABLE',public_candidate_count=1)
        self.assertEqual(d.decide(finding,b),('ABSTAIN_INTERNAL_AMBIGUITY',None))

    def test_07_independent_direct(self):
        with patch.object(d,'scan',side_effect=AssertionError('PRIMARY_FORBIDDEN')):
            for rule in ('EXACT','MAX32_RGB8_STEP'):
                self.assertEqual(d.direct(cue(),slots(),rule)['matches'],[0,1,2,3])

    def test_08_readonly_and_hidden_values(self):
        bank=slots();before=copy.deepcopy(bank);q=cue()
        first=d.scan(q,bank,'MAX32_RGB8_STEP')
        self.assertEqual(bank,before)
        bank[0]['values']=(0.0,)*32+(1.0,)*256
        self.assertEqual(first,d.scan(q,bank,'MAX32_RGB8_STEP'))

    def test_09_invalid_values_independent(self):
        for bad in (math.inf,math.nan,-0.1,1.1):
            with self.subTest(value=repr(bad)):
                with self.assertRaisesRegex(d.DiagnosticError,'^VALUES$'):
                    d.scan(cue(bad),slots(),'EXACT')

    def test_10_source_order_and_times(self):
        e,v=d.plans()
        self.assertEqual([r['base'] for r in e['rows']],['q04','q05','q06','q06','q06','q01','q06'])
        self.assertEqual([r['level'] for r in e['rows']],[0,0,0,1,-1,0,0])
        self.assertEqual(len({r['id'] for r in e['rows']}),7)
        for i,row in enumerate(e['rows']):
            self.assertEqual(row['window'],[26+6*i,27+6*i])
            self.assertEqual(row['time_base'],[1,30])
        self.assertNotIn('roles',e)
        self.assertEqual(v['groups'],[3,2,1,1])
        self.assertEqual(e['tau_hex'],(1.0/255.0).hex())

    def test_11_occlusion_and_level_order(self):
        for level in (-1,0,1):
            with self.subTest(level=level):
                data=bytearray([24])*288
                d.modify_and_occlude(data,12,8,level,False)
                self.assertEqual(data,bytearray([24+level])*32+bytearray(256))
        data=bytearray([24])*288
        d.modify_and_occlude(data,12,8,0,True)
        self.assertEqual(data[:3],bytearray([216])*3)
        self.assertEqual(data[3:32],bytearray([24])*29)

    def test_12_invalid_geometry_and_no_clipping(self):
        with self.assertRaisesRegex(d.DiagnosticError,'^GEOMETRY$'):
            d.modify_and_occlude(bytearray(),0,0,0,False)
        with self.assertRaisesRegex(d.DiagnosticError,'^NO_CLIPPING$'):
            d.modify_and_occlude(bytearray([255])*288,12,8,1,False)

    def test_13_losses_not_netting_gains(self):
        self.assertTrue(d.classify(True,False,True)['lost'])
        self.assertFalse(d.classify(True,False,True)['gained'])
        self.assertTrue(d.classify(False,True,False)['new_false'])
        self.assertTrue(d.classify(False,True,True)['gained'])
        self.assertEqual(d.plans()[1]['D_zero'],'ERHALTUNG_NICHT_GEPRUEFT')

    def test_14_binding_verifier_without_generator(self):
        record,e,v=source_fixture()
        before=s.raw((record,e,v))
        self.assertEqual(d.verify_sources(record,e,v,'c'*64)['status'],'BINDING_VALID')
        self.assertEqual(s.raw((record,e,v)),before)

    def test_15_binding_manipulations_independent(self):
        for mutation,code in ((lambda r:r.update(execution_digest='x'),'ROOT'),
                (lambda r:r['sources'][0].update(id='vb-02'),'SOURCE'),
                (lambda r:r['sources'][0].update(original_sha256='b'*64),'ORIGINAL_PAYLOAD'),
                (lambda r:r.update(generated=6),'COUNT'),
                (lambda r:r.update(collisions=[]),'COLLISIONS')):
            with self.subTest(code=code):
                record,e,v=source_fixture();mutation(record)
                with self.assertRaisesRegex(d.DiagnosticError,'^'+code+'$'):
                    d.verify_sources(record,e,v,'c'*64)

    def test_16_budgets_independent(self):
        self.assertFalse(s.budget(0,65536,1048576,262144)['violations'])
        for args,code in (((0,65537,0,0),'metadata'),((0,0,1048577,0),'evidence'),
                          ((0,0,0,262145),'verification'),((4194305,0,0,0),'TOTAL')):
            with self.subTest(code=code):
                self.assertEqual(s.budget(*args)['violations'],[code])
        self.assertFalse(runner.budget({})['violations'])
        local=sum(cap for name,cap in runner.CAPS.items()
                  if name not in ('inventory.json','seal.json','verification.json'))
        files={'neutral':dict(kind='metadata',bytes=98304-local)}
        self.assertFalse(runner.budget(files)['violations'])
        files['neutral']['bytes']+=1
        self.assertEqual(runner.budget(files)['violations'],['metadata'])
        failure=runner.failure_record(ValueError('\U0001f600'*10000),'GENERATION',3)
        self.assertTrue(failure['diagnostic_overflow'])
        self.assertEqual(failure['completed_sources'],3)
        self.assertLessEqual(len(s.raw(failure)),4096)

    def test_17_frozen_and_evaluation_binding(self):
        record,e,v=source_fixture()
        e['frozen_memory_digest']='0'*64
        with self.assertRaisesRegex(d.DiagnosticError,'^ROOT$'):
            d.verify_sources(record,e,v,'c'*64)
        record,e,v=source_fixture();v['target'][0]=False
        with self.assertRaisesRegex(d.DiagnosticError,'^ROOT$'):
            d.verify_sources(record,e,v,'c'*64)

    def test_18_missing_and_reordered_sources(self):
        record,e,v=source_fixture();record['sources'].pop()
        with self.assertRaisesRegex(d.DiagnosticError,'^COUNT$'):
            d.verify_sources(record,e,v,'c'*64)
        record,e,v=source_fixture();record['sources'][0],record['sources'][1]=record['sources'][1],record['sources'][0]
        with self.assertRaisesRegex(d.DiagnosticError,'^SOURCE$'):
            d.verify_sources(record,e,v,'c'*64)


if __name__=='__main__':
    unittest.main()
