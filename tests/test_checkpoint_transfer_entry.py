"""New process/closure connectors only; no historical history or real payloads."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace as NS
from tools import _checkpoint_transfer_entry as e


class EntryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)

    def test_01_stage_order(self):
        seen=[]
        def spawn(role):
            seen.append(role)
            if role=='save':(self.path/'checkpoint.json').write_text('{}')
            return 0
        result=e.launch_stages({},self.path,spawn)
        self.assertEqual(seen,list(e.ROLES));self.assertEqual(len(result),3)

    def test_02_child_failure_progress(self):
        with self.assertRaises(e.c.CheckpointError) as caught:
            e.launch_stages({},self.path,lambda _:7)
        self.assertEqual(caught.exception.code,'TRANSFER_CHILD_FAILED')
        self.assertEqual(caught.exception.details['completed_stages'][0]['exit_code'],7)

    def test_03_missing_checkpoint(self):
        seen=[]
        with self.assertRaises(e.c.CheckpointError) as caught:
            e.launch_stages({},self.path,lambda role:seen.append(role) or 0)
        self.assertEqual(caught.exception.code,'TRANSFER_CHECKPOINT_MISSING')
        self.assertEqual(seen,['reference','save'])

    def test_04_single_claim(self):
        path=self.path/'claim';e.claim(path,b'once')
        with self.assertRaises(e.c.CheckpointError):e.claim(path,b'twice')
        self.assertEqual(path.read_bytes(),b'once')

    def test_05_logs(self):
        code=e.bounded_process([sys.executable,'-c','print("neutral")'],self.path,'neutral')
        self.assertEqual(code,0)
        self.assertIn(b'neutral',(self.path/'neutral.stdout').read_bytes())

    def test_06_log_overflow(self):
        with self.assertRaises(e.c.CheckpointError) as caught:
            e.bounded_process([sys.executable,'-c','import sys;sys.stdout.write("x"*20000)'],self.path,'overflow')
        self.assertEqual(caught.exception.code,'TRANSFER_LOG_LIMIT')
        self.assertEqual(caught.exception.details['stored_bytes'],e.LOG_CAP)
        self.assertTrue(caught.exception.details['wait_completed'])

    def test_07_timeout(self):
        with self.assertRaises(e.c.CheckpointError) as caught:
            e.bounded_process([sys.executable,'-c','import time;time.sleep(10)'],self.path,'timeout',timeout=.1)
        self.assertEqual(caught.exception.code,'TRANSFER_TIMEOUT')

    def test_08_all_positions(self):
        bound=e.budget.envelope(100000)
        self.assertEqual(len(bound['rows']),19)
        self.assertEqual(bound['violations'],[])
        self.assertEqual(bound['work']['field_advances_in_verification'],0)

    def test_09_global_budget(self):
        self.assertTrue(e.budget.envelope(174080)['violations'])
        self.assertLess(174080,e.budget.LIMITS['shared'])

    def test_10_exact_budget(self):
        bound=e.budget.envelope(0)
        maximum=max(row['totals']['total'] for row in bound['rows'])
        room=e.budget.LIMITS['total']-maximum
        self.assertFalse(e.budget.envelope(room)['violations'])
        self.assertTrue(e.budget.envelope(room+1)['violations'])

    def test_11_components(self):
        row=dict(memory='m',field={'digest':'f'},generations=['g'],post={'time':1},step={'context_status':'ABSTAIN'})
        a=dict(rows=[row],inputs=[{}],source_receipts=[{}]);before=copy.deepcopy(a)
        b=copy.deepcopy(a);b['rows'][0]['field']['digest']='different'
        result=e.comparison_rows(a,b)[0]
        self.assertFalse(result['field_equal']);self.assertTrue(result['memory_equal'])
        self.assertEqual(a,before)

    def test_12_evaluation_block(self):
        with self.assertRaises(e.c.CheckpointError) as caught:
            e.evaluate(self.path,dict(status='NOT_EVALUABLE',evaluation_allowed=False),None)
        self.assertEqual(caught.exception.code,'TRANSFER_EVALUATION_BLOCKED')

    def test_13_manifest_values(self):
        spec=NS(event_id='neutral-event',ordinal=1,kind=e.c.b.AV,pcm=NS(sha256='audio'),rgb=NS(sha256='visual'))
        record=dict(inputs=[{}],source_receipts=[dict(nj=dict(pcm_digest='audio'),rgb_digest='visual')])
        with patch('tools._s2ng_private_comparison_verification.decode_input',return_value=NS(event_id=spec.event_id,ordinal=1,event_type=spec.kind)):
            e.validate_manifest_record(record,NS(events=[spec]))
            record['source_receipts'][0]['rgb_digest']='wrong'
            with self.assertRaises(e.c.CheckpointError) as caught:e.validate_manifest_record(record,NS(events=[spec]))
        self.assertEqual(caught.exception.code,'TRANSFER_MANIFEST_VISUAL')

    def test_14_primary_error(self):
        primary=e.c.CheckpointError('PRIMARY',dict(bytes=10,limit=9))
        out=e.error_details(primary,'FORMATION',completed_events=4)
        self.assertEqual(out['code'],'PRIMARY');self.assertEqual(out['details']['bytes'],10)
        self.assertEqual(out['progress']['completed_events'],4)

    def test_15_no_ready_admission(self):
        path=self.path/'binding.json';path.write_text(json.dumps(dict(version=e.VERSION,ready=False)))
        with self.assertRaises(e.c.CheckpointError) as caught:e.check_binding(path)
        self.assertEqual(caught.exception.code,'TRANSFER_NOT_READY')

    def test_16_gate_unchanged(self):
        self.assertIs(e.c.MAIN_GATE,False)

    def worker_fixture(self,role,fail_at=None):
        events=[NS(ordinal=n) for n in range(1,8)]
        manifest=NS(events=events,code_digest='code',run_id='neutral-transfer')
        instances=[];saved=[]
        class Session:
            def __init__(self,*args,**kwargs):
                self.n=4 if kwargs['checkpoint'] is not None else 0
                self._runtime=NS(closed=False,rows=[]);self._terminal=False;self.failure=None
                self.restored=kwargs['checkpoint'] is not None;instances.append(self)
            def next(self,event):
                if event.ordinal==fail_at:raise e.c.CheckpointError('NEUTRAL_FORMATION_FAILURE')
                self.n=event.ordinal
            def accounting(self):return dict(completed_events=self.n)
            def close(self):
                self._runtime.closed=True;self._terminal=True
                return dict(status='RECORDING_COMPLETE')
            def suspend(self,path):
                self.close();self.suspended=self.n;return 'checkpoint'
            def fail(self,exc,phase):
                self.failure=dict(code=exc.code,completed_events=self.n,field_effect_preserved=True)
                self.close()
        with patch.object(e,'check_binding',return_value=(dict(cut=4),manifest)), \
             patch.object(e,'load',return_value=dict(binding_sha256='hash',run_id=manifest.run_id)), \
             patch.object(e,'sha',return_value='hash'), \
             patch.object(e.c,'NeutralCheckpointSessionV1',Session), \
             patch.object(e,'point',side_effect=lambda s:dict(n=s.n)), \
             patch.object(e.c,'prefix_record',return_value={}), \
             patch.object(e.c,'load_common',return_value={}), \
             patch.object(e.c,'export',return_value={}), \
             patch.object(e,'full_ledger',return_value=dict(violations=[])), \
             patch.object(e,'publish',side_effect=lambda p,v:saved.append(copy.deepcopy(v))):
            code=e.worker('neutral',self.path,role)
        return code,instances[0],saved[-1]

    def test_17_reference_uninterrupted(self):
        code,session,out=self.worker_fixture('reference')
        self.assertEqual(code,0);self.assertFalse(session.restored)
        self.assertFalse(hasattr(session,'suspended'));self.assertEqual(session.n,7)
        self.assertEqual(out['cut'],dict(n=4));self.assertTrue(out['closed'])

    def test_18_save_boundary(self):
        code,session,out=self.worker_fixture('save')
        self.assertEqual(code,0);self.assertEqual(session.suspended,4)
        self.assertEqual(out['status'],'SUSPENDED_PREFIX')

    def test_19_restore_consumption(self):
        code,session,out=self.worker_fixture('restore')
        self.assertEqual(code,0);self.assertTrue(session.restored)
        self.assertEqual(out['cut'],dict(n=4))
        self.assertEqual([x['completed_events'] for x in out['accounts']],[5,6,7])

    def test_20_worker_primary_failure(self):
        code,session,out=self.worker_fixture('reference',fail_at=5)
        self.assertEqual(code,1);self.assertEqual(out['status'],'NOT_EVALUABLE')
        self.assertEqual(out['failure']['completed_events'],4)
        self.assertTrue(out['failure']['field_effect_preserved']);self.assertTrue(out['closed'])
        self.assertIs(e.c.MAIN_GATE,False)

    def total_fixture(self,same_pid=False):
        manifest=NS(events=[NS(event_id='neutral-'+str(n),kind=e.c.b.AV if n<5 or n==7 else e.c.b.V) for n in range(1,8)],code_digest='code')
        row=dict(memory='memory',field={},generations=[],post={},step=dict(context_status='ABSTAIN_NO_APPLICABLE_CONTEXT'))
        record=dict(status='RECORDING_COMPLETE',rows=[copy.deepcopy(row) for _ in range(7)],inputs=[{}]*7,source_receipts=[{}]*7)
        accounts=[dict(n=n) for n in range(1,8)]
        values={'reference.json':dict(status='RECORDING_COMPLETE',pid=1,closed=True,gate=False,cut={},record=record,accounts=accounts),
            'save.json':dict(status='SUSPENDED_PREFIX',checkpoint_digest='cp',pid=2,closed=True,gate=False,cut={},accounts=accounts[:4]),
            'restore.json':dict(status='RECORDING_COMPLETE',pid=2 if same_pid else 3,closed=True,gate=False,cut={},record=copy.deepcopy(record),accounts=accounts[4:]),
            'checkpoint.json':dict(process_id=2,checkpoint_digest='cp',stream=dict(processed_event_count=4))}
        def save(path,value):values[path.name]=copy.deepcopy(value)
        return manifest,values,save

    def test_21_total_verifier_and_abstention(self):
        manifest,values,save=self.total_fixture()
        with patch.object(e.c,'read_checkpoint',side_effect=lambda p:values[p.name]), \
             patch.object(e,'load',return_value=[dict(role=r,exit_code=0,wait_completed=True) for r in e.ROLES]), \
             patch.object(e.c.verify,'verify_core',return_value=dict(status='VALID')), \
             patch.object(e.c,'validate'),patch.object(e,'validate_manifest_record'), \
             patch.object(e.c,'validate_accounting'),patch.object(e,'publish',side_effect=save):
            proof=e.verify_total(self.path,manifest,4)
            self.assertEqual(proof['status'],'RECORDING_COMPLETE')
            result=e.evaluate(self.path,proof,manifest)
            self.assertEqual(result['status'],'CONFIRMED');self.assertEqual(len(result['decisions']),2)
            self.assertEqual(len(result['components']),7)

    def test_22_total_process_identity(self):
        manifest,values,save=self.total_fixture(True)
        with patch.object(e.c,'read_checkpoint',side_effect=lambda p:values[p.name]), \
             patch.object(e,'load',return_value=[dict(role=r,exit_code=0,wait_completed=True) for r in e.ROLES]):
            with self.assertRaises(e.c.CheckpointError) as caught:e.verify_total(self.path,manifest,4)
        self.assertEqual(caught.exception.code,'TRANSFER_PROCESS_IDENTITY')

    def test_23_valid_negative_evaluation(self):
        manifest,values,save=self.total_fixture()
        proof=dict(status='RECORDING_COMPLETE',evaluation_allowed=True,cut_equal=False,records_equal=False,
            rows=[dict(accounting_equal=True)],verification_digest='proof')
        values['verification.json']=proof
        with patch.object(e.c,'read_checkpoint',side_effect=lambda p:values[p.name]),patch.object(e,'publish',side_effect=save):
            out=e.evaluate(self.path,proof,manifest)
        self.assertEqual(out['status'],'FALSIFIED')
        self.assertEqual(len(out['decisions']),2)

    def test_24_incomplete_comparison(self):
        with self.assertRaises(e.c.CheckpointError) as caught:e.comparison_rows(dict(rows=[]),dict(rows=[{}]))
        self.assertEqual(caught.exception.code,'TRANSFER_COMPARISON_LENGTH')


if __name__=='__main__':unittest.main()
