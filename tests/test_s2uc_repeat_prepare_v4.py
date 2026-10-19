"""Read-only assessment repair; no replay, mock worker or timing repetition."""
import ast
import copy
import inspect
import textwrap
import unittest
from tools import s2uc_repeat_prepare_v4 as q


class AssessmentRepairTests(unittest.TestCase):
    def test_J05_identical_measured_worker_and_gates(self):
        for name in ('worker','execute','integrated_baseline','supervise','run','validate_authorization','charged_bytes','timeplan'):
            def tree(module):
                return ast.dump(ast.parse(textwrap.dedent(inspect.getsource(getattr(module,name)))))
            self.assertEqual(tree(q),tree(q.v3))
        self.assertEqual(q.plan(),q.v3.plan())
        self.assertIs(q.SampleLeafBudgetObserver,q.v3.SampleLeafBudgetObserver)
        q.v3.verify();q.verify()

    def test_J06_heap_measurement_and_structural_failures(self):
        r=q.old.read(q.NEUTRAL/'N1-U.json')
        changed=copy.deepcopy(r)
        changed['resources']['calls'][0]['total']+=1
        changed['resources']['calls'][0]['transient']+=1
        self.assertTrue(q.resource_structure_equal(r,changed))
        changed['resources']['calls'][0]['operation']='WRONG'
        self.assertFalse(q.resource_structure_equal(r,changed))
        changed=copy.deepcopy(r);changed['resources']['original_frames_peak']+=1
        self.assertFalse(q.resource_structure_equal(r,changed))
        changed=copy.deepcopy(r);changed['resources']['calls'][0]['total']=16385
        with self.assertRaisesRegex(RuntimeError,'U_HEAP_RECORD_INVALID'):
            q.resource_structure_equal(r,changed)
        changed=copy.deepcopy(r);changed['resources']['additional_python_peak']=16385
        with self.assertRaisesRegex(RuntimeError,'PYTHON_LIMIT'):q.old.resource_check(changed)

    def test_J07_completed_matrix_reuse_and_closed_raster(self):
        self.assertEqual(q.old.read(q.NEUTRAL/'closure.json')['status'],'COMPLETE')
        self.assertEqual(len(q.old.read(q.NEUTRAL/'phase-times.json')['replays']),10)
        self.assertEqual(q.old.read(q.v3.QUAL/'closure.json')['status'],'FAILED')
        self.assertFalse(q.OUT.exists())
        with self.assertRaisesRegex(RuntimeError,'EXPLICIT_SEPARATE_AUTHORIZATION'):
            q.validate_authorization({'status':'PENDING_SEPARATE_AUTHORIZATION'},{'status':'AUTHORIZED_ONCE'})


if __name__=='__main__':unittest.main()
