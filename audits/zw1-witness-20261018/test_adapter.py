import copy
import unittest
from adapter import bind_case,descriptive

def fixture():
    material=dict(catalog=[[0.0]*48,[1.0]*48],ids=[0]*1024)
    condition=dict(pair=1,condition='A',complete=True,cleanup=True,integrity='PASS_DELTA_INTEGRITY',targets=list(range(3,1024,2)))
    return [1,dict(pair=1,condition='A',path='pair-01-A-source.json',sha256='bound'),material,
        dict(entry_revision='ZW1_V1',neutral_only=False,source=[[0.0]*48]*1024),
        dict(replicate=1,pair=1,condition='A',orientation=0),
        dict(pair=1,orientation=0,complete=True,conditions={'A':condition,'B':condition|dict(condition='B')}),'bound']

class Mapping(unittest.TestCase):
    def test_positive(self):
        self.assertEqual(bind_case(*fixture())[:2],(1,'A'))
    def test_swapped_condition(self):
        f=fixture();f[1]['condition']='B'
        with self.assertRaisesRegex(ValueError,'MANIFEST_PAIR_CONDITION'):bind_case(*f)
    def test_crossed_pair(self):
        f=fixture();f[1]['pair']=2
        with self.assertRaisesRegex(ValueError,'MANIFEST_PAIR_CONDITION'):bind_case(*f)
    def test_crossed_summary(self):
        f=fixture();f[4]['pair']=2
        with self.assertRaisesRegex(ValueError,'SUMMARY_PAIR_CONDITION'):bind_case(*f)
    def test_swapped_receipt(self):
        f=fixture();f[5]['conditions']['A']['condition']='B'
        with self.assertRaisesRegex(ValueError,'RECEIPT_CONDITION'):bind_case(*f)
    def test_crossed_receipt(self):
        f=fixture();f[5]['pair']=2
        with self.assertRaisesRegex(ValueError,'RECEIPT_PAIR'):bind_case(*f)
    def test_wrong_source_file(self):
        f=fixture();f[1]['path']='pair-01-B-source.json'
        with self.assertRaisesRegex(ValueError,'SOURCE_PATH'):bind_case(*f)
    def test_wrong_source_hash(self):
        f=fixture();f[-1]='wrong'
        with self.assertRaisesRegex(ValueError,'SOURCE_HASH'):bind_case(*f)
    def test_wrong_source_content(self):
        f=fixture();f[2]['ids'][8]=1
        with self.assertRaisesRegex(ValueError,'ARCHIVE_SOURCE'):bind_case(*f)
    def test_wrong_revision(self):
        f=fixture();f[3]['entry_revision']='ER1_V2'
        with self.assertRaisesRegex(ValueError,'ARCHIVE_REVISION'):bind_case(*f)
    def test_unique_gain_harm_and_multiplicity(self):
        a=dict(keeper='E',stage='warm_use',target=19,keeper_error=0.0,other_error=.25)
        b=a|dict(target=23,keeper_error=.5)
        c=a|dict(target=27,keeper_error=.25)
        r=descriptive([a,a|dict(promotion_end=20),b,c])['E']
        self.assertEqual((r['warm_records'],r['unique_warm_targets'],r['unique_gain_targets'],r['unique_harm_targets'],r['unique_equal_targets']),(4,3,1,1,1))
        self.assertEqual((r['event_gains'],r['gain_error_sum'],r['harm_error_sum']),(2,.25,.25))
        self.assertEqual(r['multi_assigned_targets'],{'19':2})
    def test_conflicting_duplicate_errors(self):
        a=dict(keeper='E',stage='warm_use',target=19,keeper_error=0.0,other_error=.25)
        with self.assertRaisesRegex(ValueError,'TARGET_ERROR_CONFLICT'):descriptive([a,a|dict(keeper_error=.5)])

if __name__=='__main__':unittest.main()
