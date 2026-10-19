"""Focused authorization and serialized-metadata controls; no histories."""
import copy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch
from tools import _checkpoint_transfer_entry as e
from tools import _checkpoint_transfer_metadata as m


class AuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.patcher=patch.object(e.c.b,'ROOT',self.root);self.patcher.start();self.addCleanup(self.patcher.stop)
        self.binding=self.root/'binding.json';self.binding.write_text('{}')
        self.value=dict(authorization_path='permit.json',output='output',inventory={'files':{}})
        self.manifest=NS(run_id='neutral-transfer',manifest_digest='a'*64,profile_digest='b'*64,code_digest='c'*64)
        self.directory=self.root/'output';self.directory.mkdir()
        self.permit=e.expected_authorization(self.binding,self.value,self.manifest)

    def write(self,permit=None):
        path=self.root/'permit.json'
        path.write_bytes(e.c.b.canonical(self.permit if permit is None else permit))
        Path(str(path)+'.used').write_text(e.sha(path))

    def accept(self,role='reference'):
        return e.authorize_worker(self.binding,self.value,self.manifest,self.directory,role)

    def test_01_sections(self):
        self.write()
        for role,ends in [('reference',(1,7)),('save',(1,4)),('restore',(5,7))]:
            with self.subTest(role=role):
                v=self.accept(role);self.assertEqual((v['first'],v['last']),ends)

    def test_02_missing(self):
        with self.assertRaises(e.c.CheckpointError) as caught:self.accept()
        self.assertEqual(caught.exception.code,'TRANSFER_AUTHORIZATION_INVALID')

    def test_03_changed_section(self):
        p=copy.deepcopy(self.permit);p['roles']['save']['last']=7;self.write(p)
        with self.assertRaises(e.c.CheckpointError):self.accept('save')

    def test_04_foreign_run(self):
        p=copy.deepcopy(self.permit);p['run_id']='foreign';self.write(p)
        with self.assertRaises(e.c.CheckpointError):self.accept()

    def test_05_code_binding(self):
        self.write();self.binding.write_text('{"changed":true}')
        with self.assertRaises(e.c.CheckpointError):self.accept()

    def test_06_consumed_role(self):
        self.write();self.accept()
        with self.assertRaises(e.c.CheckpointError) as caught:self.accept()
        self.assertEqual(caught.exception.code,'TRANSFER_ALREADY_USED')

    def test_07_parent_consumption(self):
        self.write();(self.root/'permit.json.used').unlink()
        with self.assertRaises(e.c.CheckpointError) as caught:self.accept()
        self.assertEqual(caught.exception.code,'TRANSFER_AUTHORIZATION_NOT_CONSUMED')

    def test_08_foreign_output(self):
        self.write()
        with self.assertRaises(e.c.CheckpointError):e.authorize_worker(self.binding,self.value,self.manifest,self.root,'reference')

    def test_09_gate_before_factory(self):
        with patch.object(e,'check_binding',return_value=(self.value,self.manifest)), \
             patch.object(e,'load',return_value=dict(binding_sha256=e.sha(self.binding),run_id=self.manifest.run_id)), \
             patch.object(e.c,'NeutralCheckpointSessionV1') as factory,patch.object(e,'publish'), \
             patch.object(e.traceback,'print_exc'):
            self.assertEqual(e.worker(self.binding,self.directory,'reference'),1)
        factory.assert_not_called();self.assertIs(e.c.MAIN_GATE,False)

    def test_10_metadata_not_limit(self):
        with self.assertRaises(ValueError):e.budget.envelope(0)

    def test_11_full_format_contributions(self):
        a=m.derive('neutral-transfer',{'binding':100},['source.py'],['evidence.json'])
        b=m.derive('neutral-transfer',{'binding':101},['source.py'],['evidence.json'])
        self.assertEqual(b['maximum'],a['maximum']+1)
        for row in a['rows']:
            self.assertEqual(row['metadata'],100+sum(row['parts'].values()))

    def test_12_boundary(self):
        self.assertFalse(e.budget.envelope(0,1)['violations'])
        self.assertTrue(e.budget.envelope(0,196609)['violations'])
        self.assertTrue(e.budget.envelope(196609,0)['violations'])
        combined=e.budget.envelope(196608,196608)
        self.assertTrue(any('shared' in row['violations'] for row in combined['rows']))
        self.assertEqual(e.budget.LIMITS['total'],5242880)
        self.assertEqual(e.c.budgets.LIMITS['metadata'],65536)

    def test_13_private_publication(self):
        (self.directory/'common.json').write_bytes(e.c.b.canonical(dict(values={},sha256=e.c.b.digest({}))))
        (self.directory/'preregistration.json').write_text('{}')
        e.publish(self.directory/'neutral.json',dict(value='x'*34000))
        self.assertTrue((self.directory/'neutral.json').exists())
        self.assertFalse((self.directory/'neutral.json.pending').exists())

    def test_14_publication_overflow(self):
        (self.directory/'common.json').write_bytes(e.c.b.canonical(dict(values={},sha256=e.c.b.digest({}))))
        (self.directory/'preregistration.json').write_text('{}')
        with self.assertRaises(e.c.CheckpointError) as caught:
            e.publish(self.directory/'neutral.json',dict(value='x'*100000))
        self.assertEqual(caught.exception.code,'TRANSFER_BUDGET')
        self.assertIn('metadata',caught.exception.details['violations'])
        self.assertFalse((self.directory/'neutral.json').exists())

    def test_15_invalid_role(self):
        self.write()
        with self.assertRaises(e.c.CheckpointError) as caught:self.accept('other')
        self.assertEqual(caught.exception.code,'TRANSFER_ROLE')

    def test_16_authorized_gate(self):
        self.write();seen=[]
        def factory(*args,**kwargs):
            seen.append(e.c.MAIN_GATE)
            raise e.c.CheckpointError('NEUTRAL_FACTORY_STOP')
        with patch.object(e,'check_binding',return_value=(self.value,self.manifest)), \
             patch.object(e,'load',return_value=dict(binding_sha256=e.sha(self.binding),run_id=self.manifest.run_id)), \
             patch.object(e.c,'NeutralCheckpointSessionV1',side_effect=factory),patch.object(e,'publish'), \
             patch.object(e.traceback,'print_exc'):
            self.assertEqual(e.worker(self.binding,self.directory,'reference'),1)
        self.assertEqual(seen,[True]);self.assertIs(e.c.MAIN_GATE,False)

    def test_17_private_checkpoint_route(self):
        from threading import Lock
        runtime=NS(close=lambda:None)
        session=NS(_lock=Lock(),_terminal=False,_runtime=runtime,_manifest=None,_code='code',
                   accounting=lambda:{},failure=None)
        with patch.object(e.c,'export',return_value={'checkpoint_digest':'digest'}), \
             patch.object(e.c,'validate'),patch.object(e,'publish') as writer, \
             patch.object(e.c,'publish_new') as historical:
            self.assertEqual(e.suspend_transfer(session,self.directory/'checkpoint.json'),'digest')
        writer.assert_called_once();historical.assert_not_called()
        self.assertTrue(session._terminal);self.assertFalse(session._lock.locked())


if __name__=='__main__':unittest.main()
