"""Small artificial fixtures only; no historical policy/reference execution."""
import json,time,unittest
import diagnose as d

K=(0,7,0);L=(0,7,1);M=(1,9,0)
class Fixtures(unittest.TestCase):
    def test_empty_included(self):self.assertEqual(d.category({},{}),3)
    def test_both_cold(self):self.assertEqual(d.category({K:None},{K:None}),3)
    def test_valid_zero_is_warm(self):self.assertEqual(d.category({K:(0,0)},{K:None}),1)
    def test_raw_pair_even_same_delta(self):self.assertEqual(d.category({K:(1,2)},{K:(2,3)}),2)
    def test_identical_warm(self):self.assertEqual(d.category({K:(1,2)},{K:(1,2)}),3)
    def test_category_one_precedence(self):self.assertEqual(d.category({K:None,L:(1,2)},{K:(0,0),L:(2,3)}),1)
    def test_stock_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError,'STOCK'):d.category({K:None},{L:None})
    def test_receipt_zero_and_ineligible(self):
        r=dict(matches=[dict(role='retained',generation=7,offset=0),dict(role='retained',generation=7,offset=2)],hypotheses=[dict(eligible=True,ec=0,ep=0),dict(eligible=False)])
        self.assertEqual(d.hypotheses(r),{K:(0,0)})
    def test_half_cold_rejected(self):
        r=dict(matches=[dict(role='retained',generation=7,offset=0)],hypotheses=[dict(eligible=True,ec=None,ep=0)])
        with self.assertRaisesRegex(ValueError,'HALF_COLD'):d.hypotheses(r)
    def test_same_selection_reset_excluded(self):
        self.assertEqual(d.provenance(K,12,[dict(end=12,generation=7,offsets=[0])],{})['state'],'NO_PRIOR_DELETION')
    def test_same_generation_and_offset_required(self):
        rs=[dict(end=12,generation=7,offsets=[0])]
        self.assertEqual(d.provenance(L,20,rs,{K:[dict(target=13)]})['state'],'NO_PRIOR_DELETION')
        self.assertEqual(d.provenance(K,20,rs,{L:[dict(target=13)],(0,8,0):[dict(target=15)]})['state'],'NOT_YET_UPDATED')
    def test_feedback_must_precede_selection(self):
        rs=[dict(end=12,generation=7,offsets=[0])]
        self.assertEqual(d.provenance(K,14,rs,{K:[dict(target=15)]})['state'],'NOT_YET_UPDATED')
        self.assertEqual(d.provenance(K,14,rs,{K:[dict(target=13)]})['state'],'UPDATED')
    def test_new_reset_discards_old_update(self):
        rs=[dict(end=12,generation=7,offsets=[0]),dict(end=20,generation=7,offsets=[0])]
        self.assertEqual(d.provenance(K,22,rs,{K:[dict(target=13)]}),dict(state='NOT_YET_UPDATED',reset=20,feedback=[]))
    def test_multiple_hypotheses_mixed_states(self):
        rs=[dict(end=12,generation=7,offsets=[0,1])];u={K:[dict(target=13)]}
        self.assertEqual([d.provenance(k,16,rs,u)['state'] for k in (K,L,M)],['UPDATED','NOT_YET_UPDATED','NO_PRIOR_DELETION'])
    def test_exact_gain_harm_tie_accounting(self):
        b=d.empty()
        for x in (d.F(-1,4),d.F(1,2),d.F(0)):d.add(b,x)
        self.assertEqual(b,dict(targets=3,gains=1,harms=1,ties=1,error_sum=d.F(1,4)))

if __name__=='__main__':
    t=time.monotonic();d.install_job()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Fixtures)
    ids=[x.id() for x in suite]
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    d.write(d.Path(__file__).parent/'fixture-results.json',dict(test_ids=ids,tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),passed=result.wasSuccessful(),seconds=time.monotonic()-t,job=d.snapshot(),policy=0,archives=0))
    raise SystemExit(0 if result.wasSuccessful() else 1)
