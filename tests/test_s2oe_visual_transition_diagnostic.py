import copy
import math
import unittest
from unittest.mock import patch
from tools import _s2oe_visual_transition_diagnostic as d


def fixture(values=(0.2, 0.4), q=0.0):
    slots=[]
    for i in range(4):
        occupied=i<len(values)
        slots.append(dict(slot_id=f'slot.{i:03}', occupied=occupied,
            prototype_values=[float(values[i])]*288 if occupied else [],
            support_count=1 if occupied else None, last_selected_step=i+1 if occupied else None))
    cfg=dict(match_threshold=0.01, expire_after_steps=64, stable_after=3, update_rate=0.05)
    data=dict(values=[float(q)]*288, config=cfg, births=[1,2,None,None],
        pre=dict(accepted_step_count=2,slots=slots), frame=dict(clock_id='v',window_end_tick=4))
    return data


def completed():
    x=fixture(); post=copy.deepcopy(x['pre'])
    post.update(accepted_step_count=3,source_clock_id='v',last_source_window_end_tick=4)
    post['slots'][2].update(occupied=True,prototype_values=[0.0]*288,support_count=1,last_selected_step=3)
    x.update(post=post,observed=dict(event='CREATED',slot_id='slot.002'))
    return x


class DiagnosticTests(unittest.TestCase):
    def test_all_slots_and_creation(self):
        x=completed(); r=d.table(x)
        self.assertEqual(d.verify(x,r)['comparisons'],576)
        self.assertEqual(len(r['rows']),4)
    def test_exact_threshold(self):
        self.assertEqual(d.table(fixture((0.01,)))['action'],'MATCHED')
    def test_above_threshold(self):
        self.assertEqual(d.table(fixture((math.nextafter(0.01,math.inf),)))['action'],'CREATED')
    def test_tie_slot_order(self):
        self.assertEqual(d.table(fixture((0.0,0.0)))['selected_slot_id'],'slot.000')
    def test_full_replacement(self):
        self.assertEqual(d.table(fixture((.2,.3,.4,.5)))['action'],'REPLACED')
    def test_expiry(self):
        x=fixture((0.0,));x['pre']['accepted_step_count']=64
        self.assertEqual(d.table(x)['action'],'CREATED')
    def test_missing_values(self):
        x=fixture();x['values'].pop()
        with self.assertRaisesRegex(d.DiagnosticError,'VALUES_INVALID'):d.table(x)
    def test_nonfinite(self):
        x=fixture();x['values'][0]=float('inf')
        with self.assertRaisesRegex(d.DiagnosticError,'VALUES_INVALID'):d.table(x)
    def test_manipulated_term(self):
        x=completed();r=d.table(x);r['rows'][0]['terms'][0]['difference']=0.0
        with self.assertRaisesRegex(d.DiagnosticError,'TERM_INVALID'):d.verify(x,r)
    def test_missing_candidate(self):
        x=completed();r=d.table(x);r['rows'].pop()
        with self.assertRaisesRegex(d.DiagnosticError,'TABLE_INCOMPLETE'):d.verify(x,r)
    def test_independent_and_immutable(self):
        x=completed();before=copy.deepcopy(x);r=d.table(x)
        with patch.object(d.ppb,'normalized_mean_l1_distance',side_effect=AssertionError('forbidden')):
            self.assertEqual(d.verify(x,r)['status'],'EVIDENCE_VALID')
        self.assertEqual(x,before)
    def test_wrong_recorded_transition(self):
        x=completed();r=d.table(x);x['observed']['slot_id']='slot.001'
        with self.assertRaisesRegex(d.DiagnosticError,'OBSERVED_TRANSITION_MISMATCH'):d.verify(x,r)


if __name__=='__main__':unittest.main(verbosity=2)
