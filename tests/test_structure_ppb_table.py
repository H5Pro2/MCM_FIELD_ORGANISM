import copy
import math
import unittest
from unittest.mock import patch
from tools import _structure_ppb_table as p


class Tests(unittest.TestCase):
    def test_inclusive_and_adjacent(self):
        for x,want in ((0.01,True),(math.nextafter(0.01,0),True),(math.nextafter(0.01,1),False)):
            with self.subTest(x=x):self.assertEqual(p.decision(x,x)['matched'],want)

    def test_native_rule(self):
        a=(0.0,)*288;b=(0.01,)*288
        self.assertEqual(p.normalized_mean_l1_distance(a,b),math.fsum(abs(x-y) for x,y in zip(a,b))/288)
        self.assertEqual(p.normalized_mean_l1_distance(a,a),0.0)

    def test_table_and_independent_check(self):
        vectors=[(0.0,)*288,(0.02,)*288]+[(0.0,)*288]*12
        old=[dict(indices=[0,1],terms=[(0.02).hex()]*288,mean=(sum([0.02]*288)/288).hex()) for _ in range(22)]
        result=p.table(vectors,old);before=copy.deepcopy(result)
        with patch.object(p,'normalized_mean_l1_distance',side_effect=AssertionError('REPLAY')):
            self.assertEqual(p.verify(result,old)['status'],'EVIDENCE_VALID')
        self.assertEqual(result,before)
        result['rows'][0]['matched']=True
        with self.assertRaisesRegex(p.s.BindingError,'DECISION'):p.verify(result,old)

    def test_missing_vector_and_parent(self):
        with self.assertRaisesRegex(p.s.BindingError,'VECTOR_SIZE'):p.vector(['0x0.0p+0']*287)
        with self.assertRaisesRegex(p.s.BindingError,'PARENT_PROOF'):
            p.extract({},dict(status='INVALID'),{},{},{})

    def test_pair_completeness(self):
        with self.assertRaisesRegex(p.s.BindingError,'INPUT_COUNT'):p.table([(0.0,)*288]*14,[])

    def test_difference_reporting(self):
        d=p.decision(math.nextafter(0.02,1),0.02)
        self.assertTrue(d['numeric_changed']);self.assertFalse(d['decision_changed'])
