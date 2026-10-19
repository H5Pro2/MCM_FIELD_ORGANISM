"""Timing plumbing tests; no evaluation source or policy replay."""
import sys
import time
import unittest
from tools import s2uc_runtime_audit as a

FACTS={}


class AuditTests(unittest.TestCase):
    def test_D01_fixed_neutral_matrix(self):
        s=a.spec();self.assertEqual(s['replays'],18)
        self.assertEqual(s['experimental_admissions'],1440)
        self.assertEqual(set(s['cases']),{'N1','N2'})
        self.assertEqual(s['cases']['N1'],['A']*20)
        self.assertEqual(s['cases']['N2'],['A']*5+['B']*5+['A']*5+['B']*5)
        self.assertEqual(s['recipes']['A'][0],'1/32')

    def test_D02_nested_exclusive_clocks(self):
        b=a.Book()
        with b.scope('outer'):
            time.sleep(.003)
            with b.scope('inner'):time.sleep(.003)
        v=b.finish()
        self.assertEqual(sum(v['wall_ns'].values()),v['partition_wall_ns'])
        self.assertEqual(sum(v['cpu_ns'].values()),v['partition_cpu_ns'])
        self.assertGreater(v['wall_ns']['inner'],0);self.assertGreater(v['wall_ns']['outer'],0)
        self.assertIsNone(sys.gettrace())

    def test_D03_semantic_projection_keeps_all_functional_fields(self):
        r=dict(rows=[1],forecasts=[2],error_updates=[3],admissions=[4],state_hashes=[5],
            slots_released=True,terminal_cleanup=True,censored_target=81,resources={'time':1})
        self.assertEqual(set(a.semantic(r)),set(r)-{'resources'})
        for name in a.semantic(r):
            changed=dict(r);changed[name]=None
            self.assertNotEqual(a.semantic(r),a.semantic(changed))
        changed=dict(r);changed['resources']={}
        self.assertEqual(a.semantic(r),a.semantic(changed))

    def test_D04_trace_off_is_local_diagnostic(self):
        proxy=a.SysProxy(False)
        try:
            proxy.settrace(lambda f,e,v:None);self.assertIsNone(sys.gettrace())
        finally:sys.settrace(None)
        b=a.Book();f=a.instrumented(b,False)
        self.assertTrue(callable(f));self.assertIsNot(f,a.baseline.replay)

    def test_D05_watchdog_separate_events(self):
        normal=a.supervise_diagnostic(a.sleeping_worker,(.02,),5)
        timeout=a.supervise_diagnostic(a.sleeping_worker,(20,),1.5)
        self.assertEqual(normal['status'],'NORMAL');self.assertEqual(timeout['status'],'TIME_LIMIT')
        for label,r in (('normal',normal),('timeout',timeout)):
            events={e['event']:e for e in r['events']}
            self.assertFalse(events['worker_end_confirmed']['alive'])
            self.assertLessEqual(events['worker_end_confirmed']['monotonic_ns'],events['closure_admin_started']['monotonic_ns'])
            self.assertLessEqual(events['closure_admin_started']['monotonic_ns'],events['closure_admin_finished']['monotonic_ns'])
            self.assertEqual(r['historical_worker_stop'],'UNKNOWN_NOT_RECONSTRUCTED')
            if label=='timeout':
                self.assertGreaterEqual(events['abort_requested']['monotonic_ns'],events['deadline_established']['deadline_monotonic_ns'])
                self.assertLessEqual(events['abort_requested']['monotonic_ns'],events['worker_end_confirmed']['monotonic_ns'])
            else:self.assertNotIn('abort_requested',events)
        FACTS.update(normal=normal,timeout=timeout)


if __name__=='__main__':unittest.main()
