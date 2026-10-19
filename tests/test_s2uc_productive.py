"""Isolated Q1-Q7 fixtures; never generate an operative authorization."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from tools import _s2uc_productive as p
from tools import s2uc_productive_once as process

def fixture(root,inv,*,payload='original_bad_hash'):
    root=Path(root)
    for name,data in [('inventory.json',inv),('resources.json',p.e.resources.contract())]:
        p.e.write_new(root/name,p.e.canonical(data))
    value=dict(version=p.VERSION,kind='ISOLATED_TEST',run_id='S2UC-P3-TEST-'+os.urandom(16).hex(),
        authorization_id=os.urandom(16).hex(),decision='isolated implementation test; no operative authority',
        max_uses=1,outputs={k:(root/k).relative_to(p.ROOT).as_posix() for k in p.OUTPUTS},
        test_root=root.relative_to(p.ROOT).as_posix(),test_payload=payload,
        inventory=p.ref(root/'inventory.json'),resources=p.ref(root/'resources.json'),
        source_context=p.source_pin(),source_plan=p.plan_pin(),
        manifest_digest=p.e.context.source_context()['manifest']['binding_digest'],qualification=None)
    path=root/'binding.json';p.e.write_new(path,p.e.canonical(value));return path

class ProductiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.inv=p.current()

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=p.ROOT/'reports/s2uc',prefix='p3-test-')
        self.root=Path(self.tmp.name);self.addCleanup(self.tmp.cleanup)
        self.addCleanup(patch.stopall);patch.object(p,'current',return_value=self.inv).start()

    def prepare(self,payload='original_bad_hash'):return fixture(self.root,self.inv,payload=payload)

    def test_q1_public_rejects_test_and_no_self_authority(self):
        path=self.prepare()
        with patch.object(process.subprocess,'Popen') as launch:
            with self.assertRaisesRegex(ValueError,'AUTHORITY_KIND'):process.start(path)
            launch.assert_not_called()
        value=p.e.read_json(path)
        with self.assertRaisesRegex(ValueError,'OPERATIVE_AUTHORITY_REQUIRED'):process.authority(path,value)
        self.assertFalse((self.root/'admission').exists())
        self.assertTrue(all(not (p.ROOT/rel).exists() for rel in p.OUTPUTS.values()))

    def test_q1_untrusted_registry_acl_rejected(self):
        process.acl_rules('S-1-5-18',[(0,0xF003F,'S-1-5-32-544'),(0,0x20019,'S-1-5-32-545')])
        for owner,aces in [('S-1-5-32-545',[]),('S-1-5-18',None),
                          ('S-1-5-18',[(0,2,'S-1-1-0')]),('S-1-5-18',[(2,0,'S-1-5-18')])]:
            with self.assertRaises(ValueError):process.acl_rules(owner,aces)

    def test_q1_independent_receipt_absence_mismatch_and_acl(self):
        path=self.prepare();v=p.e.read_json(path)
        # In-memory verifier input only: no operative document or registry write.
        v['kind']='OPERATIVE_ONE_SHOT'
        with patch.object(process.winreg,'OpenKey',side_effect=PermissionError('DENIED')):
            with self.assertRaisesRegex(ValueError,'ABSENT_OR_UNTRUSTED'):process.authority(path,v)
        class Key:
            def __enter__(self):return 42
            def __exit__(self,*args):pass
        receipt=dict(binding_sha256=p.ref(path)['sha256'],authorization_id=v['authorization_id'],
                     decision=v['decision'],max_uses=1)
        with patch.object(process.winreg,'OpenKey',return_value=Key()),\
             patch.object(process,'registry_acl') as acl,\
             patch.object(process.winreg,'QueryValueEx',return_value=(json.dumps(receipt),process.winreg.REG_SZ)):
            self.assertEqual(process.authority(path,v),receipt);self.assertEqual(acl.call_count,3)
            v['decision']='different decision'
            with self.assertRaisesRegex(ValueError,'RECEIPT_MISMATCH'):process.authority(path,v)

    def test_q1_qualification_coverage_and_complete_ledger(self):
        from tools import s2uc_productive_check as checker
        self.prepare();ids=p.test_ids();inv=p.ref(self.root/'inventory.json')
        # Explicit synthetic verifier fixtures, not executed qualification evidence.
        result=dict(fixture_only=True,test_ids=ids,tests_run=len(ids),results=dict.fromkeys(ids,'PASS'),
            code_unchanged=True,expected_ids_complete=True,exit_code=0,errors=0,failures=0,skips=0,
            formal_qualification=False,real_execution_authorized=False,inventory=inv)
        f=self.root/'test-result.json';f.write_bytes(p.e.canonical(result))
        prefixes=sorted({n.rsplit('.',1)[0] for n in ids})
        protocol=dict(inventory=inv,result=p.ref(f),prefixes=prefixes,
            rows=[[prefixes.index(n.rsplit('.',1)[0]),n.rsplit('.',1)[1],'PASS'] for n in ids])
        (self.root/'protocol.json').write_bytes(p.e.canonical(protocol))
        checker.close_ledger(self.root,self.inv)
        value=dict(qualification={k:p.ref(self.root/name) for k,name in
            [('inventory','inventory.json'),('result','test-result.json'),('protocol','protocol.json'),('ledger','ledger.json')]})
        self.assertTrue(p.qualified(value,self.inv))
        ledger_file=self.root/'ledger.json';original=ledger_file.read_bytes()
        bad=json.loads(original);bad['files'][0]['category']='code'
        ledger_file.write_bytes(p.e.canonical(bad));value['qualification']['ledger']=p.ref(ledger_file)
        with self.assertRaisesRegex(ValueError,'QUALIFICATION_CATEGORY'):p.qualified(value,self.inv)
        ledger_file.write_bytes(original);value['qualification']['ledger']=p.ref(ledger_file)
        result['results'].pop(ids[0]);f.write_bytes(p.e.canonical(result))
        value['qualification']['result']=p.ref(f)
        with self.assertRaisesRegex(ValueError,'COVERAGE'):p.qualified(value,self.inv)

    def test_q1_binding_mutations_before_claim(self):
        path=self.prepare();raw=path.read_bytes();v=p.e.read_json(path)
        variants={'run_id':p.RUN,'outputs':p.OUTPUTS,'max_uses':True,'decision':'',
            'source_context':{},'source_plan':{},'manifest_digest':'0'*64,
            'resources':{},'inventory':{},'qualification':{},'test_payload':'original',
            'authorization_id':'bad','version':'old','kind':'ONE_P2_TEST_EXECUTION'}
        for k,x in variants.items():
            with self.subTest(k=k):
                bad=copy.deepcopy(v);bad[k]=x;path.write_bytes(p.e.canonical(bad))
                with self.assertRaises((ValueError,KeyError)):p._test_load(path)
                path.write_bytes(raw)
        self.assertFalse((self.root/'admission').exists())

    def test_q1_inventory_runtime_and_bound_files(self):
        path=self.prepare();raw=path.read_bytes()
        for name in ('inventory.json','resources.json'):
            file=self.root/name;original=file.read_bytes();file.write_bytes(original+b' ')
            with self.assertRaisesRegex(ValueError,'REFERENCE_CHANGED'):p._test_load(path)
            file.write_bytes(original)
        inv=copy.deepcopy(self.inv);inv['external']['interpreter']['sha256']='0'*64
        (self.root/'inventory.json').write_bytes(p.e.canonical(inv))
        v=json.loads(raw);v['inventory']=p.ref(self.root/'inventory.json');path.write_bytes(p.e.canonical(v))
        with self.assertRaisesRegex(ValueError,'CODE_RUNTIME'):p._test_load(path)

    def test_q2_original_manifest_and_no_supplier_parameter(self):
        path=self.prepare();v,_=p._test_load(path)
        self.assertEqual(p.manifest(v),p.e.context.source_context()['manifest'])
        self.assertNotIn('payload_substitution',v)
        with self.assertRaises(TypeError):p.execute_child(path,{},supplier=lambda ep:b'')
        with patch.object(p.e.context,'prepare_nu_supplier') as supplier:
            with self.assertRaises(ValueError):p.execute_child(path,{})
            supplier.assert_not_called()

    def test_q2_original_hash_rejects_replacement_before_receptor(self):
        path=self.prepare();result=process._run(path,test=True,case='original_bad_hash')
        self.assertEqual(result['status'],'NOT_EVALUABLE',result)
        facts=p.e.read_json(self.root/'observer/facts.json')
        self.assertEqual(facts['calls'],1);self.assertTrue(facts['test_evidence'])
        self.assertFalse(facts['real_execution_authorized'])
        record=p.e.codec.loads((self.root/'product/record.json').read_bytes())
        self.assertNotEqual(record['status'],'COMPLETE')
        self.assertIn('HASH',json.dumps(record).upper())
        self.assertEqual(record['source_completion']['counters']['audio_analyses'],0)
        self.assertEqual(record['source_completion']['counters']['nj_projections'],0)
        with self.assertRaises(ValueError):p._appendix(path,test=True,read=True)
        with self.assertRaises(ValueError):process._run(path,test=True,case='original_bad_hash')

    def test_q3_child_domain_cannot_target_real_roots(self):
        path=self.prepare();v=p.e.read_json(path)
        process.child_identity(v,True)
        for key,new in [('outputs',p.OUTPUTS),('run_id',p.RUN),('test_root','reports')]:
            bad=copy.deepcopy(v);bad[key]=new
            with self.assertRaises(ValueError):process.child_identity(bad,True)
        with self.assertRaises(ValueError):process.child_identity(v,False)
        self.assertTrue(all(not (p.ROOT/rel).exists() for rel in p.OUTPUTS.values()))

    def test_q4_concurrent_claim_process_restart_and_corruption(self):
        path=self.prepare()
        script=('from tools import _s2uc_productive as p; import sys; '
                'v,l=p._test_load(sys.argv[1]); p.claim(sys.argv[1],v,l)')
        children=[subprocess.Popen([sys.executable,'-c',script,str(path)],cwd=p.ROOT,
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW) for _ in range(2)]
        codes=[]
        for child in children:child.communicate(timeout=120);codes.append(child.returncode)
        self.assertEqual(codes.count(0),1,codes)
        self.assertFalse((self.root/'observer').exists())
        receipt=self.root/'admission/claim.json';receipt.write_bytes(b'{')
        with self.assertRaises(ValueError):p._test_load(path)
        with self.assertRaises(ValueError):p._test_load(path,consumed=True)

    def test_q4_partial_persistence_consumes_namespace(self):
        path=self.prepare();v,l=p._test_load(path)
        with patch.object(p.e,'write_new',side_effect=OSError('DISK')):
            with self.assertRaises(OSError):p.claim(path,v,l)
        self.assertTrue((self.root/'admission').is_dir())
        with self.assertRaisesRegex(ValueError,'ALREADY_USED'):p._test_load(path)
        self.assertFalse((self.root/'observer').exists())

    def test_q4_abort_consumed_without_source(self):
        path=self.prepare();result=process._run(path,test=True,case='abort')
        self.assertEqual(result['status'],'NOT_EVALUABLE');self.assertEqual(result['exit_code'],17)
        self.assertFalse((self.root/'product').exists())
        with self.assertRaisesRegex(ValueError,'ALREADY_USED'):process._run(path,test=True,case='abort')

    def test_q4_timeout_and_job_error_are_consumed(self):
        path=self.prepare();result=process._run(path,test=True,case='timeout',timeout=2)
        self.assertEqual(result['status'],'NOT_EVALUABLE')
        self.assertFalse((self.root/'product').exists())
        with self.assertRaisesRegex(ValueError,'ALREADY_USED'):p._test_load(path)

    def test_q4_job_creation_failure_after_claim(self):
        path=self.prepare()
        with patch.object(process.runpy,'run_path',side_effect=OSError('JOB_SETUP_FAILURE')):
            result=process._run(path,test=True,case='original_bad_hash')
        self.assertEqual(result['primary_failure'],'JOB_SETUP_FAILURE')
        with self.assertRaisesRegex(ValueError,'ALREADY_USED'):p._test_load(path)

    def test_q5_native_job_and_preimport_code_pins(self):
        path=self.prepare();v,l=p._test_load(path);p.claim(path,v,l)
        with patch.object(p.e.context,'prepare_nu_supplier') as supplier:
            with self.assertRaises(ValueError):p._execute(path,{},test=True)
            supplier.assert_not_called()
        forged=dict(job_name='Local\\MCM-NONEXISTENT-P3',member=True,limit=640*1048576,flags=0x2100)
        with self.assertRaises(ValueError):p._execute(path,forged,test=True)
        config=dict(binding=str(path),binding_sha256=p.ref(path)['sha256'])
        process.boot_pins(config)
        config['binding_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'BOOT_BINDING'):process.boot_pins(config)

    def test_q6_synthetic_closure_provenance_and_mutations(self):
        path=self.prepare('synthetic');result=process._run(path,test=True,case='synthetic')
        self.assertEqual(result['status'],'CLOSED_TEST_P3_VERIFIED',result)
        original={f:f.read_bytes() for f in (self.root/'product').iterdir()}
        terminal_file=self.root/'product/terminal.json';terminal=p.e.read_json(terminal_file)
        terminal['test_evidence']=1;terminal_file.write_bytes(p.e.canonical(terminal))
        v,l=p._test_load(path,consumed=True)
        with self.assertRaisesRegex(ValueError,'PRODUCT_NOT_EVALUABLE'):p._read_product(path,v,l)
        terminal_file.write_bytes(original[terminal_file])
        with patch.object(p,'provenance',side_effect=ValueError('ANNEX_FAILURE')):
            failed=p._appendix(path,test=True)
        self.assertEqual(failed['status'],'NOT_EVALUABLE')
        self.assertEqual(failed['primary_failure'],'ANNEX_FAILURE')
        for file,raw in original.items():self.assertEqual(file.read_bytes(),raw)
        for file in (self.root/'appendix').iterdir():file.unlink()
        (self.root/'appendix').rmdir()
        report=p._appendix(path,test=True)
        self.assertEqual(report['status'],'EVALUATED_TEST',report)
        self.assertEqual(report['candidate_gains'],['g1/24'])
        self.assertEqual(report['candidate_losses'],['g1/26','g2/38','g3/67'])
        self.assertFalse(report['hints'][1]['legacy_expectation']['fulfilled'])
        self.assertEqual(p._appendix(path,test=True,read=True),report)
        with self.assertRaisesRegex(ValueError,'AUTHORITY_KIND'):p.read_product(path)
        with self.assertRaisesRegex(ValueError,'AUTHORITY_KIND'):p.read_appendix(path)
        for file,raw in original.items():
            self.assertEqual(file.read_bytes(),raw);file.write_bytes(raw+b' ')
            with self.assertRaises(ValueError):p._appendix(path,test=True,read=True)
            file.write_bytes(raw)
        f=self.root/'appendix/provenance.json';raw=f.read_bytes();f.write_bytes(raw+b' ')
        with self.assertRaises(ValueError):p._appendix(path,test=True,read=True)

    def test_q6_failure_keeps_primary_and_product_bytes(self):
        path=self.prepare();v,l=p._test_load(path);p.claim(path,v,l)
        folder=self.root/'appendix';folder.mkdir()
        with patch.object(p.e,'atomic',side_effect=OSError('SECONDARY')):
            result=p.failure(folder,l,v,'PRIMARY',appendix=True)
        self.assertEqual(result['primary_failure'],'PRIMARY')
        self.assertTrue(result['secondary_failures']);self.assertFalse(result['evaluation_allowed'])

    def test_q7_four_roots_staging_copies_and_boundaries(self):
        path=self.prepare();v,l=p._test_load(path);before=l.admit()['actual']['total_bytes']
        for name,folder in p.paths(v).items():folder.mkdir()
        for i,folder in enumerate(p.paths(v).values(),1):(folder/'result.json').write_bytes(b'x'*i*100)
        self.assertEqual(l.admit()['actual']['total_bytes'],before+1000)
        stage=self.root/'product/publication.tmp';stage.write_bytes(b'x'*245760)
        self.assertTrue(l.admit()['actual']['within_limits']);stage.write_bytes(b'x'*245761)
        with self.assertRaisesRegex(ValueError,'ACTUAL_BUDGET'):l.admit()
        stage.unlink();f=self.root/'product/result.json';f.unlink()
        os.link(self.root/'observer/result.json',f)
        with self.assertRaisesRegex(ValueError,'FILE_ALIAS'):l.admit()

    def test_q7_limits_and_reserves_unchanged(self):
        limits=p.e.resources.LIMITS
        self.assertEqual(limits['code'],1048576);self.assertEqual(limits['total'],4194304)
        amounts=dict.fromkeys(p.e.resources.CATEGORIES,0)
        amounts['verification']=131072
        self.assertTrue(p.e.resources.account(amounts)['within_limits'])
        amounts['verification']+=1
        self.assertFalse(p.e.resources.account(amounts)['within_limits'])
        self.assertFalse(p.e.resources.contract()['parent_process_limited'])

if __name__=='__main__':unittest.main()
