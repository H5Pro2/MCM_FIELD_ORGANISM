"""Static integration checks only. The qualification starts exactly one worker."""
import ast
import inspect
import textwrap
import unittest
from tools import s2uc_repeat_prepare_v3 as q


class IntegrationTests(unittest.TestCase):
    def test_J01_frozen_contract_and_watchdog(self):
        for name in ('supervise','validate_authorization','run','charged_bytes','known_registry'):
            def tree(module):
                return ast.dump(ast.parse(textwrap.dedent(inspect.getsource(getattr(module,name)))))
            self.assertEqual(tree(q),tree(q.v2))
        before=q.v2.plan();after=q.plan()
        for key in before:
            self.assertEqual(before[key],after[key])
        self.assertIs(q.old.resource_check,q.v2.old.resource_check)

    def test_J02_reused_qualification_seals(self):
        q.v2.preparation_check();q.sample.verify()
        self.assertTrue(q.old.read(q.sample.REPORT/'tests.json')['success'])
        self.assertEqual(q.old.read(q.sample.REPORT/'tests.json')['count'],10)
        self.assertTrue(q.old.read(q.v2.QUAL/'tests.json')['success'])
        self.assertEqual(q.old.read(q.v2.QUAL/'tests.json')['count'],7)
        self.assertEqual(q.verify()['code']['tools/_s2uc_sample_leaf_observer_v1.py'],
                         q.old.sha(q.ROOT/'tools/_s2uc_sample_leaf_observer_v1.py'))

    def test_J03_real_worker_no_test_dispatch(self):
        source=inspect.getsource(q.worker)+inspect.getsource(q.execute)+inspect.getsource(q.integrated_baseline)
        self.assertNotIn('MagicMock',source)
        self.assertNotIn('wraps=',source)
        self.assertNotIn('side_effect=',source)
        self.assertNotIn('from tests',source)
        self.assertIn("execute(folder,specs,supplier,validator,registry,charged,check",source)
        self.assertIn("SampleLeafBudgetObserver.trace",source)
        self.assertIn('FunctionType(old.execute.__code__',source)
        self.assertIs(q.BudgetObserver.trace,q.leaf.OLD)
        self.assertEqual(q.old.sha(q.ROOT/'tools/_s2uc_eval_baseline_replay.py'),
                         q.old.read(q.old.BINDING)['code']['tools/_s2uc_eval_baseline_replay.py'])

    def test_J04_neutral_json_and_exact_gate(self):
        specs,supply,validate,registry,summary=q.neutral_inputs()
        self.assertEqual([s['id'] for s in specs],['N1','N2'])
        self.assertEqual(sum(s['frames'] for s in specs)*len(q.old.ARMS),800)
        for spec in specs:validate(supply(spec),spec)
        with self.assertRaisesRegex(RuntimeError,'EXPLICIT_SEPARATE_AUTHORIZATION'):
            q.validate_authorization({'status':'PENDING_SEPARATE_AUTHORIZATION'},{'status':'AUTHORIZED_ONCE'})
        self.assertFalse(q.OUT.exists())


if __name__=='__main__':unittest.main()
