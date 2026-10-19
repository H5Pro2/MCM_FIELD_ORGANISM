import copy
from pathlib import Path
import unittest
from unittest.mock import patch
from tools import _structure_comparison as c
from tools import _structure_comparison_ledger as l


def ref(path,size):
    return dict(path=path,kind=l.classify(path),bytes=size,sha256='0'*64)


def binding(*refs):
    return dict(version=l.VERSION,files=list(refs),report_reserve=0)


class Tests(unittest.TestCase):
    def measure(self,b,files=None):
        return c.ledger(Path('not-created-neutral-ledger-directory'),b,files or {})

    def test_reference_counting(self):
        a=ref('a.json',10);b=binding(a,copy.deepcopy(a),ref('copy.json',10))
        result=self.measure(b)
        self.assertEqual(result['metadata'],20);self.assertEqual(result['reference_count'],2)

    def test_conflicting_reference(self):
        with self.assertRaisesRegex(l.LedgerError,'REFERENCE_CONFLICT'):
            self.measure(binding(ref('a.json',10),ref('a.json',11)))

    def test_reference_class(self):
        r=ref('a.json',1);r['kind']='sources'
        with self.assertRaisesRegex(l.LedgerError,'REFERENCE_CLASS'):self.measure(binding(r))

    def test_class_boundaries(self):
        for path,limit,key in (('a.json',98304,'METADATA'),('x/verification.json',262144,'VERIFICATION')):
            with self.subTest(key=key):
                self.assertFalse(self.measure(binding(ref(path,limit)))['violations'])
                self.assertIn(key,self.measure(binding(ref(path,limit+1)))['violations'])

    def test_global_boundary(self):
        self.assertFalse(self.measure(binding(ref('a.py',4194304)))['violations'])
        self.assertIn('TOTAL',self.measure(binding(ref('a.py',4194305)))['violations'])

    def test_work_separation(self):
        neutral=dict(basis='retrospective',differences=32256,verification_terms=51264)
        result=l.work(l.REAL_WORK,l.VERIFY_WORK,neutral)
        self.assertEqual(result['real']['differences'],19008)
        for domain,key in (('real','differences'),('verification','terms')):
            with self.subTest(domain=domain):
                r=dict(l.REAL_WORK);v=dict(l.VERIFY_WORK)
                (r if domain=='real' else v)[key]+=1
                with self.assertRaisesRegex(l.LedgerError,'WORK_LIMIT'):l.work(r,v,neutral)

    def test_alternatives_and_reserve(self):
        choices=l.alternatives(c.CAPS)
        self.assertNotIn('failure.json',choices['success'])
        self.assertNotIn('evaluation.json',choices['failure'])
        b=binding(ref('a.json',100));b['report_reserve']=8192
        for choice in choices.values():
            result=self.measure(b,choice)
            self.assertFalse(result['violations']);self.assertEqual(result['reserve'],8192)
        with patch.object(c,'perceive',side_effect=AssertionError('NO_FUNCTIONAL_RUN')):
            self.measure(b,choices['success'])

    def test_historical_limit_unchanged(self):
        self.assertIn('METADATA',c.ledger(Path('not-created-neutral-ledger-directory'),0,
            {'evaluation.json':65536-12288+1})['violations'])
