import unittest,json
from tests.test_s2uc_pair_context_adapter import PairAdapterTests
from tools._s2uc_pair_context_adapter import ContextReceipt,AdapterError
class PairBoundaryTests(unittest.TestCase):
    def setUp(self):self.factory=PairAdapterTests()
    def test_identical_prefix_independent_of_future(self):
        a=self.factory.adapter();b=self.factory.adapter()
        for x in (a,b):x.accept_perception(self.factory.sample(1))
        ra=a.accept_perception(self.factory.sample(2));rb=b.accept_perception(self.factory.sample(2));self.assertEqual(ra,rb)
        a.accept_perception(self.factory.sample(3,values=(.2,)*48));b.accept_perception(self.factory.sample(3,values=(.9,)*48));self.assertEqual(ra,rb)
        a.finish_story();b.finish_story()
    def test_every_original_admitted_once_by_identity(self):
        a=self.factory.adapter();seen=[];base=a.arm.form
        def spy(f):seen.append((f.ordinal,f.values));return base(f)
        a.arm.form=spy
        values=[tuple(float(i+j)/100 for j in range(48)) for i in range(1,10)]
        for i,v in enumerate(values,1):a.accept_perception(self.factory.sample(i,values=v))
        a.finish_story();self.assertEqual([n for n,v in seen],list(range(1,10)));self.assertTrue(all(v is w for (_,v),w in zip(seen,values)));self.assertEqual((a.accepted,a.admitted),(9,9))
    def test_receipt_size_bound_all_nine_matches(self):
        a=self.factory.adapter();matches=[dict(role='retained',generation=2**63-1,formation='x'*96,ordinals=[2**63-1]*4,offset=i%3,factors=[.5,1.,2.]) for i in range(9)]
        r=a._receipt('ABSTAIN_AMBIGUOUS',[1,2],[[0,4800],[4800,9600]],matches);self.assertLessEqual(len(r.json_text.encode()),16384);self.assertEqual(len(json.loads(r.json_text)['matches']),9)
        matches[0]['factors'].append(4.);self.assertEqual(len(json.loads(r.json_text)['matches'][0]['factors']),3)
        with self.assertRaises(AdapterError):a._receipt('X',[],[],[{'formation':'x'*17000}])
    def test_duplicate_and_close_reuse_rejected(self):
        a=self.factory.adapter();a.accept_perception(self.factory.sample(1))
        with self.assertRaises(AdapterError):a.accept_perception(self.factory.sample(1))
        self.assertEqual(a.discarded_on_error,1)
        with self.assertRaises(AdapterError):a.accept_perception(self.factory.sample(2))
if __name__=='__main__':unittest.main()
