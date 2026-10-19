"""Only new dispatch/authorization/consumption paths; no scientific calls."""
import unittest,io,json,os
from pathlib import Path
from unittest.mock import patch
from . import gateway as g
from . import full
from .projector import Projector
from experiments.as480.common import exclusive,read
FOLDER=None

class Tests(unittest.TestCase):
    def test_authorization_exact_order_binding_target(self):
        auth=g.authorized('abc');g.verify_authorization(auth,'abc')
        for key,value in [('workflow','old'),('chat','other'),('binding_sha256','changed'),('target','elsewhere'),('research',True)]:
            wrong=dict(auth);wrong[key]=value
            with self.assertRaisesRegex(ValueError,'AUTHORIZATION'):g.verify_authorization(wrong,'abc')
    def test_durable_once_without_completion(self):
        p=FOLDER/'synthetic-consumed.json';g.consume_once(p,dict(nonce='synthetic',workflow='fixture'))
        self.assertEqual(read(p)['nonce'],'synthetic')
        with self.assertRaises(FileExistsError):g.consume_once(p,dict(nonce='second'))
        self.assertFalse((FOLDER/'synthetic-terminal.json').exists())
    def test_direct_full_call_rejected_before_material(self):
        with patch.object(full.Material,'prepare',side_effect=AssertionError('must not materialize')) as prepare:
            with self.assertRaisesRegex(ValueError,'CAPABILITY'):full.run(FOLDER/'direct')
            prepare.assert_not_called()
        self.assertFalse((FOLDER/'direct').exists())
    def test_dispatch_full_not_fixtures(self):
        token=object()
        with patch.object(full,'run',return_value='sentinel') as run:
            self.assertEqual(g.dispatch('full',FOLDER,token),'sentinel');run.assert_called_once_with(FOLDER,permit=token)
        with self.assertRaisesRegex(ValueError,'WORKER_TASK'):g.dispatch('research',FOLDER)
    def test_wrong_worker_and_nonce(self):
        token=object();active=dict(permit=token,pid=os.getpid()+1,nonce='fixture')
        with patch.object(g,'_ACTIVE',active):
            with self.assertRaisesRegex(ValueError,'PID'):g.check_active(g.FULL,token)
        active['pid']=os.getpid()
        records=[dict(workflow=g.ORDER,nonce='a'),dict(nonce='b'),dict(nonce='a')]
        with patch.object(g,'_ACTIVE',active),patch.object(g,'read',side_effect=records):
            with self.assertRaisesRegex(ValueError,'NONCE'):g.check_active(g.FULL,token)
    def test_worker_single_entry_marker(self):
        token=object();active=dict(permit=token,pid=os.getpid(),nonce='test')
        records=[dict(workflow=g.ORDER,nonce='test'),dict(nonce='test',supervisor_pid=os.getppid()),dict(nonce='test',pid=os.getpid())]
        marker=FOLDER/'synthetic-worker-entered.json'
        def write(*args):exclusive(marker,dict(entered=True))
        with patch.object(g,'_ACTIVE',active),patch.object(g,'read',side_effect=records*2),patch.object(g.job.win,'worker_membership',return_value=True),patch.object(g,'save',side_effect=write):
            g.check_active(g.FULL,token)
            with self.assertRaises(FileExistsError):g.check_active(g.FULL,token)
    def test_code_and_recipe_tamper_admission(self):
        from .entry import ROOT
        with self.assertRaisesRegex(ValueError,'FINAL_CODE'):g.verify_code({'experiments/temporal_alignment/gateway.py':'0'*64})
        self.assertEqual(full.NEUTRAL,{'A':[310,680,1390,1750],'B':[330,700,2180,2490]})
    def test_counter_callback_no_receptor(self):
        seen=[];p=Projector(on_event=seen.append)
        for event in ('receptor','receptor_completed','nj','nj_completed'):p.event(event)
        self.assertEqual(seen,['receptor','receptor_completed','nj','nj_completed']);self.assertEqual(p.calls,0)

def run(folder):
    global FOLDER
    FOLDER=Path(folder);log=io.StringIO()
    result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    return dict(passed=result.wasSuccessful(),tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),log=log.getvalue(),
        receptor_calls=0,nj_calls=0,policy_calls=0,formal_starts=0,synthetic_markers_only=True)
