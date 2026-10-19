import copy,hashlib,json,unittest
from pathlib import Path
from collections import Counter
from fractions import Fraction
from . import sources,matrix,statistics as stats
from .integration import pair_receipt

ROOT=Path(__file__).resolve().parents[2]
PREP=ROOT/'reports/s2uc/zw1-neutral-preparation-20261018-01'

def artificial():
    result=[]
    for pair in range(1,17):
        conditions={}
        for label in ('A','B'):
            conditions[label]=dict(pair=pair,condition=label,complete=True,cleanup=True,integrity='PASS_DELTA_INTEGRITY',targets=list(stats.TARGETS),E=[.25]*511,F=[.25]*511)
        result.append(pair_receipt(pair,conditions))
    return result

class Sources(unittest.TestCase):
    def test_all_24_transitions(self):
        for previous in range(4):
            values=[sources.transition(previous,u) for u in range(24)]
            a=Counter(x for x,y in values);b=Counter(y for x,y in values)
            self.assertEqual(a,{i:12 if i==previous else 4 for i in range(4)})
            self.assertEqual(b,{i:6 for i in range(4)})
            self.assertEqual(Counter(values),{(i,j):3 if i==previous else 1 for i in range(4) for j in range(4)})
    def test_initial_reference_and_flip(self):
        for pair in (1,2):
            d=sources.generate(pair);r=sources.reconstruct(pair)
            self.assertEqual(d,r);self.assertEqual(d['blocks']['A'][0],d['blocks']['B'][0])
            for block,(a,b) in enumerate(zip(d['blocks']['A'],d['blocks']['B']),1):
                flip_a=a[1]^a[0]%2^(pair-1)%2^int(block>=129)
                flip_b=b[1]^b[0]%2^(pair-1)%2^int(block>=129)
                self.assertEqual(flip_a,flip_b)
            for label in ('A','B'):sources.verify_material(sources.materialize(d,label),r,label)
    def test_phase_128_129(self):
        for cue in range(4):
            for o in (0,1):
                for flip in (0,1):
                    self.assertEqual(sources.outcome(cue,o,128,flip)^sources.outcome(cue,o,129,flip),1)
    def test_draw_exhaustion(self):
        d=sources.Draws(1,'cue',lambda _:b'\xff'*32)
        with self.assertRaisesRegex(ValueError,'DRAW_LIMIT'):d.below(24)
        self.assertEqual(d.cursor,4096)
    def test_research_blocked(self):
        for f in (sources.generate,sources.reconstruct):
            with self.assertRaises(PermissionError):f(1,neutral=False)
    def test_material_has_no_pair_labels(self):
        self.assertEqual(set(sources.materialize(sources.generate(1,2),'A')),{'catalog','ids'})

class Matrix(unittest.TestCase):
    def test_independent_bytes_and_binding(self):
        data=(PREP/'bootstrap.bin').read_bytes();bound=json.loads((PREP/'matrix-binding.json').read_bytes())
        self.assertEqual(matrix.verify(data),bound['sha256']);matrix.shape(data)
    def test_corrupt_matrix(self):
        data=bytearray((PREP/'bootstrap.bin').read_bytes());data[0]^=2
        with self.assertRaises(ValueError):matrix.verify(data)
    def test_wrong_stratum(self):
        data=bytearray((PREP/'bootstrap.bin').read_bytes());data[0]=1
        with self.assertRaises(ValueError):matrix.shape(data)

class Statistics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=(PREP/'bootstrap.bin').read_bytes();cls.digest=hashlib.sha256(cls.data).hexdigest()
    def test_negative_positive_and_reference(self):
        for sign in (-1,1):
            records=artificial()
            for r in records:
                r['conditions']['A']['E']=[.25+sign*.125]*511
            main=stats.primary(records,self.data,self.digest);ref=stats.reference(records,self.data)
            self.assertEqual(main['mean'],str(Fraction(sign,8)))
            self.assertEqual(main['verdict'],'NEGATIVE_INTERACTION' if sign<0 else 'POSITIVE_INTERACTION')
            for key in ('mean','ci','pairs'):self.assertEqual(main[key],ref[key])
    def test_heterogeneous_interaction(self):
        r=artificial()
        for row in r:
            n=row['pair'];row['conditions']['A']['E']=[n/32]*511;row['conditions']['B']['F']=[(n%3)/16]*511
        a=stats.primary(r,self.data,self.digest);b=stats.reference(r,self.data)
        for key in ('mean','pairs','ci'):self.assertEqual(a[key],b[key])
    def test_all_four_arms_resampled_together(self):
        records=artificial()
        for r in records:
            for label in ('A','B'):
                r['conditions'][label]['E']=[r['pair']/32]*511
        result=stats.primary(records,self.data,self.digest)
        self.assertEqual(result['ci'],['0','0']);self.assertEqual(result['verdict'],'INCONCLUSIVE')
        self.assertEqual(stats.reference(records,self.data)['ci'],['0','0'])
    def test_zero_touch(self):
        self.assertEqual(stats.decision(['-1','0']),'INCONCLUSIVE')
        self.assertEqual(stats.decision(['0','1']),'INCONCLUSIVE')
    def test_missing_pair(self):
        with self.assertRaisesRegex(ValueError,'COMPLETE_PAIRS'):stats.primary(artificial()[:-1],self.data,self.digest)
    def test_missing_target(self):
        r=artificial();r[0]['conditions']['A']['targets'].pop()
        with self.assertRaises(ValueError):stats.primary(r,self.data,self.digest)
        with self.assertRaises(ValueError):stats.reference(r,self.data)
    def test_missing_arm_error(self):
        r=artificial();r[0]['conditions']['B']['F'].pop()
        with self.assertRaises(ValueError):stats.primary(r,self.data,self.digest)
    def test_cross_pair_condition(self):
        r=artificial();r[0]['conditions']['B']=copy.deepcopy(r[1]['conditions']['B'])
        with self.assertRaises(ValueError):stats.primary(r,self.data,self.digest)
        with self.assertRaises(ValueError):stats.reference(r,self.data)
    def test_missing_pair_receipt(self):
        r=artificial();r[2]['complete']=False
        with self.assertRaises(ValueError):stats.primary(r,self.data,self.digest)
    def test_incomplete_condition_no_receipt(self):
        r=artificial()[0]
        with self.assertRaisesRegex(ValueError,'PAIR_INCOMPLETE'):pair_receipt(1,{'A':r['conditions']['A']})
    def test_condition_swap(self):
        r=artificial();r[0]['conditions']['A'],r[0]['conditions']['B']=r[0]['conditions']['B'],r[0]['conditions']['A']
        with self.assertRaises(ValueError):stats.primary(r,self.data,self.digest)
