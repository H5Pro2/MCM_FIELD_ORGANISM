"""Runner gates and an unrelated short neutral source, never the 48er source."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import s2uc_multi_qualification as q
from tools._s2uc_multi_observer import replay
from tests.test_s2uc_multi_error import adapter, fixture, freeze, seed, measure, cells
from tests.test_s2uc_paired_error_ema import vec, sample, PROFILE

FACTS = {}


def neutral_spec():
    return dict(frames=12, arms=['U','M','E','K','P'],
                masks=dict(G=[3,5,7,9,11], H=[7,11], N=[3,5,9], F=[7], A_W=[11], A_R=[11]))


class RunnerTests(unittest.TestCase):
    def test_Q01_neutral_five_arms(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)/'neutral'
            result = q.export(out, neutral_spec(), lambda: [vec(x) for x in (.11,.23,.67,.89)*3])
            c = json.loads((out/'closure.json').read_text())
            a = json.loads((out/'assessment.json').read_text())
            self.assertEqual(c['status'], 'COMPLETE')
            self.assertEqual(a['technical_errors'], [])
            self.assertEqual(result['U']['frames'], 12)
            FACTS['Q1'] = dict(closure=c, assessment=a, neutral_frames=12,
                              experimental_admissions=60, reference_advances=60,
                              resources=result['U']['resources'], U=result['U'])

    def test_Q02_auth_before_source(self):
        with patch.object(q, 'verify'), patch.object(q, 'read', return_value={'status':'PENDING'}), \
             patch.object(q, 'authorization', return_value={'status':'AUTHORIZED_ONCE'}), \
             patch.object(q, 'export') as run:
            with self.assertRaisesRegex(RuntimeError, 'AUTHORIZATION'): q.compare('unused')
            run.assert_not_called()

    def test_Q03_exclusive_before_factory(self):
        with tempfile.TemporaryDirectory() as tmp:
            called = []
            with self.assertRaises(FileExistsError): q.export(Path(tmp), neutral_spec(), lambda: called.append(True))
            self.assertEqual(called, [])

    def test_Q04_failure_closure(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)/'failed'
            def fail(*args, **kwargs):
                kwargs['evidence']['stage'] = 'technical_failure'
                raise KeyboardInterrupt('fixture')
            with patch.object(q, 'multi_replay', fail), self.assertRaises(KeyboardInterrupt):
                q.export(out, neutral_spec(), lambda: [vec(.1)]*12)
            self.assertEqual(json.loads((out/'closure.json').read_text())['status'], 'FAILED')
            self.assertTrue((out/'partial.json').exists())

    def test_Q05_promotion_interrupts_and_reentrancy(self):
        from tools._s2tu_retained_trace import Frame
        from tests.test_s2uc_multi_error import frames
        points = [('promotion_validated', -1), ('promotion_generation', 0), ('promotion_role', 0)]
        for point in points:
            a = fixture(); seed(a,0,1,3,0,0.,.5); freeze(a)
            c = a.arm._candidate
            a.arm._forming = list(frames([f.values[0] for f in c.frames[:3]],17,'p5'))
            a.arm._forming_segment = 'p5'
            def stop(stage, index):
                with self.assertRaises(Exception): _ = a.selected_values
                if (stage,index) == point: raise KeyboardInterrupt('promotion fixture')
            a._checkpoint = stop
            frame = Frame(c.frames[3].values, PROFILE, 'owner','p5',20)
            with self.assertRaises(KeyboardInterrupt): measure(a,lambda: a._admit(frame))
            self.assertTrue(a.closed); self.assertFalse(any(a.bank))
            self.assertEqual(a._frozen,[None]*6)
        FACTS['Q5'] = dict(promotion_interruptions=3, reentrancy_blocked=True)

    def test_Q06_missing_capacity_fault(self):
        a = fixture(six=True)
        for i in range(6): seed(a,i,0 if i<4 else 1,i//2+1,i%2,0.,.5)
        freeze(a)
        # An injected failed lookup must not overwrite a full valid table.
        with patch.object(a,'_find',return_value=None), self.assertRaisesRegex(Exception,'CELL_LIMIT'):
            a.consume_feedback(sample(a,vec(.4)))
        self.assertTrue(a.closed); self.assertFalse(any(a.bank))


if __name__ == '__main__': unittest.main()
