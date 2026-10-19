import copy
import json
import os
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
from unittest.mock import patch
from tools import _s2uc_p2_execution as e
from tools import _s2uc_p2_resources as r
from tools import _s2uc_p2_appendix as appendix
from tools import s2uc_p2_process as process
from tools import _s2nu_private_source_binding as nu

class P2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inv=e.current();cls.p1inv=e.p1.current()

    def setUp(self):
        parent=Path(os.environ.get('MCM_P2_QUALIFICATION_ROOT',str(e.ROOT/'reports/s2uc')))
        tmp=tempfile.TemporaryDirectory(dir=parent,prefix='p2-test-')
        self.addCleanup(tmp.cleanup);self.root=Path(tmp.name)
        self.q=parent if 'MCM_P2_QUALIFICATION_ROOT' in os.environ else self.root
        self.addCleanup(patch.stopall)
        patch.object(e,'current',return_value=self.inv).start()
        patch.object(e.p1,'current',return_value=self.p1inv).start()
        self.real=patch.object(nu,'pcm_window',side_effect=AssertionError('REAL_SOURCE_OPENED')).start()

    def tearDown(self): self.real.assert_not_called()

    def prepare(self): return e.prepare(self.root/'case',self.q)

    def test_budget_boundaries_and_reservations(self):
        for k,limit in r.LIMITS.items():
            if k in ('shared','total'): continue
            amounts=dict.fromkeys(r.CATEGORIES,0);amounts[k]=min(limit,r.RESERVES.get(k,limit))
            self.assertTrue(r.account(amounts)['within_limits'],k)
            amounts[k]+=1;self.assertFalse(r.account(amounts)['within_limits'],k)
        a=dict.fromkeys(r.CATEGORIES,0);a.update(static_shared=r.LIMITS['static_shared'],
            error=r.LIMITS['error'],terminal=r.LIMITS['terminal'],minimal=r.LIMITS['minimal'])
        self.assertEqual(r.account(a)['shared_bytes'],1687552)
        a['code']=True
        with self.assertRaises(ValueError):r.account(a)
        a=dict.fromkeys(r.CATEGORIES,0);a['record']=9
        self.assertEqual(r.account(a)['categories']['record'],9)
        self.assertEqual(r.closure_reservation(a)['categories']['record'],245760)

    def test_preparation_and_closed_productive_entry(self):
        path=self.prepare();value,ledger=e.load(path)
        self.assertEqual(value['authorization'],e.AUTH)
        self.assertTrue(ledger.admit()['accounting_complete'])
        for auth in (False,True,{'kind':'ONE_REAL_EXECUTION'}):
            with self.assertRaisesRegex(ValueError,'PRODUCTIVE_AUTHORIZATION_ABSENT'):
                e.start_real(path,authorization=auth)
        self.assertFalse((path.parent/'claim.json').exists())
        with self.assertRaisesRegex(ValueError,'JOB_REQUIRED'):
            e.prepare_bound_supplier(e.context.source_context(),{})

    def test_binding_and_input_mutations(self):
        path=self.prepare();raw=path.read_bytes();value=json.loads(raw)
        for key,altered in [('run_id','REAL'),('authorization',{'kind':'ONE_REAL_EXECUTION'}),
                            ('output',str(self.root/'wrong')),('inputs',[])]:
            bad=copy.deepcopy(value);bad[key]=altered;path.write_bytes(e.canonical(bad))
            with self.assertRaises(ValueError):e.load(path)
            path.write_bytes(raw)
        for name in ('resources.json','manifest.json','inventory.json'):
            target=path.parent/name;original=target.read_bytes();target.write_bytes(original+b' ')
            with self.assertRaises(ValueError):e.load(path)
            target.write_bytes(original)

    def test_exclusive_claim_and_no_restart_retry(self):
        path=self.prepare();value,ledger=e.load(path);e.claim(path,value,ledger)
        with self.assertRaises(FileExistsError):e.claim(path,value,ledger)
        with self.assertRaisesRegex(ValueError,'ALREADY_USED'):process.run_neutral(path)
        self.assertFalse((path.parent/'observer').exists())

    def test_unclassified_alias_and_inventory_overflow(self):
        path=self.prepare();_,ledger=e.load(path)
        f=path.parent/'unexpected.bin';f.write_bytes(b'x')
        with self.assertRaisesRegex(ValueError,'UNCLASSIFIED'):ledger.admit()
        f.unlink();f=path.parent/'stdout.txt';os.link(path,f)
        with self.assertRaisesRegex(ValueError,'FILE_ALIAS'):ledger.admit()
        f.unlink();f=path.parent/'protocol.json';f.write_bytes(b'x'*32769)
        with self.assertRaisesRegex(ValueError,'PER_FILE_LIMIT'):ledger.admit()

    def test_simultaneous_retained_files_count(self):
        path=self.prepare();_,ledger=e.load(path)
        before=ledger.snapshot()['actual']['total_bytes']
        a=self.root/'retained-a';b=self.root/'retained-b';a.mkdir();b.mkdir()
        (a/'result.json').write_bytes(b'x'*1000);(b/'result.json').write_bytes(b'x'*2000)
        self.assertEqual(ledger.snapshot()['actual']['total_bytes'],before+3000)
        (a/'record.json').write_bytes(b'x'*130000);(b/'record.json').write_bytes(b'x'*130000)
        with self.assertRaisesRegex(ValueError,'ACTUAL_BUDGET'):ledger.admit()

    def test_atomic_staging_failure_and_primary_preserved(self):
        path=self.prepare();_,ledger=e.load(path);folder=path.parent/'product';folder.mkdir()
        with patch.object(e.os,'rename',side_effect=OSError('RENAME_FAILED')):
            with self.assertRaisesRegex(OSError,'RENAME_FAILED'):
                e.atomic(folder/'record.json',b'{}',ledger)
        self.assertTrue((folder/'publication.tmp').exists())
        with patch.object(e,'atomic',side_effect=OSError('SECONDARY_DISK')):
            result=e.fail(folder,ledger,'PRIMARY_SOURCE')
        self.assertEqual(result['primary_failure'],'PRIMARY_SOURCE')
        self.assertFalse(result['evaluation_allowed']);self.assertTrue(result['secondary_failures'])
        self.assertFalse((folder/'publication.tmp').exists())

    def test_child_requires_job_before_supplier(self):
        path=self.prepare();value,ledger=e.load(path);e.claim(path,value,ledger)
        supplier=unittest.mock.Mock()
        with self.assertRaisesRegex(ValueError,'JOB_REQUIRED'):e.execute_child(path,supplier,{})
        supplier.assert_not_called();self.assertFalse((path.parent/'product').exists())

    def test_forged_job_receipt_cannot_admit_parent(self):
        path=self.prepare();value,ledger=e.load(path);e.claim(path,value,ledger)
        supplier=unittest.mock.Mock()
        forged=dict(member=True,limit=640*1048576,flags=0x2100,job_name='Local\\MCM-P2-NOT-A-JOB')
        with self.assertRaisesRegex(ValueError,'JOB_REQUIRED'):e.execute_child(path,supplier,forged)
        with self.assertRaisesRegex(ValueError,'JOB_REQUIRED'):
            e.prepare_bound_supplier(e.context.source_context(),forged)
        supplier.assert_not_called()

    def test_success_appendix_and_original_byte_mutations(self):
        path=self.prepare();result=process.run_neutral(path)
        self.assertEqual(result['status'],'CLOSED_NEUTRAL_P2_VERIFIED',result)
        original={p:p.read_bytes() for p in (path.parent/'product').iterdir()}
        done=appendix.publish(path);self.assertEqual(done['status'],'CLOSED_NEUTRAL_PROVENANCE',done)
        report=appendix.read(path)
        self.assertEqual(report['candidate_gains'],['g1/24'])
        self.assertEqual(report['candidate_losses'],['g1/26','g2/38','g3/67'])
        self.assertFalse(report['hints'][1]['legacy_expectation']['fulfilled'])
        for file,data in original.items():
            self.assertEqual(file.read_bytes(),data);file.write_bytes(data+b' ')
            with self.assertRaises(ValueError):appendix.read(path)
            file.write_bytes(data)
        with self.assertRaisesRegex(ValueError,'ALREADY_USED'):process.run_neutral(path)

    def test_late_supplier_failure_is_not_evaluable(self):
        path=self.prepare();result=process.run_neutral(path,case='memoryerror')
        self.assertEqual(result['status'],'NOT_EVALUABLE',result)
        proof=e.read_json(path.parent/'product/error.json')
        self.assertTrue(proof['primary_failure']);self.assertFalse(proof['evaluation_allowed'])
        self.assertEqual(e.read_json(path.parent/'observer/facts.json')['calls'],58)
        with self.assertRaises(ValueError):appendix.read(path)

    def test_wrong_source_hash_stops_before_analysis(self):
        path=self.prepare();result=process.run_neutral(path,case='bad_hash')
        self.assertEqual(result['status'],'NOT_EVALUABLE',result)
        record=e.codec.loads((path.parent/'product/record.json').read_bytes())
        self.assertEqual(record['source_completion']['counters']['audio_analyses'],0)
        self.assertEqual(e.read_json(path.parent/'observer/facts.json')['calls'],1)

    def test_external_abort_consumes_claim(self):
        path=self.prepare();result=process.run_neutral(path,case='abort')
        self.assertEqual(result['status'],'NOT_EVALUABLE',result)
        self.assertEqual(result['exit_code'],17)
        self.assertFalse((path.parent/'product').exists())
        with self.assertRaisesRegex(ValueError,'ALREADY_USED'):process.run_neutral(path)

    def test_appendix_write_failure_preserves_product(self):
        path=self.prepare();result=process.run_neutral(path)
        self.assertEqual(result['status'],'CLOSED_NEUTRAL_P2_VERIFIED',result)
        originals={p:p.read_bytes() for p in (path.parent/'product').iterdir()}
        atomic=e.atomic
        def fail_report(target,data,ledger):
            if Path(target).name=='provenance.json':raise OSError('APPENDIX_DISK_FAILURE')
            return atomic(target,data,ledger)
        with patch.object(e,'atomic',side_effect=fail_report):result=appendix.publish(path)
        self.assertEqual(result['primary_failure'],'APPENDIX_DISK_FAILURE')
        self.assertEqual(result['status'],'NOT_EVALUABLE')
        for p,data in originals.items():self.assertEqual(p.read_bytes(),data)

    def test_parent_job_setup_failure_consumes_claim(self):
        path=self.prepare();real_runpy=process.runpy.run_path
        def helper(*args,**kwargs):
            api=real_runpy(*args,**kwargs);api['create']=lambda *a:None;return api
        with patch.object(process.runpy,'run_path',side_effect=helper):result=process.run_neutral(path)
        self.assertEqual(result['primary_failure'],'P2_JOB_CREATE_FAILED')
        self.assertTrue((path.parent/'claim.json').exists())
        self.assertFalse((path.parent/'product').exists())

    def test_bound_identity_is_not_production_authority(self):
        path=e.prepare(self.root/'case',self.q,source_test=True)
        value,ledger=e.load(path);manifest=e.read_json(path.parent/'manifest.json')
        original=e.context.source_context()['manifest']
        self.assertEqual(value['authorization'],e.AUTH)
        self.assertEqual(value['source_identity'],e.BOUND_TEST)
        for actual,prior in zip(manifest['events'],original['events'],strict=True):
            rebuilt=copy.deepcopy(actual)
            if 'endpoint' in rebuilt:
                self.assertNotEqual(rebuilt['endpoint']['pcm_sha256'],prior['endpoint']['pcm_sha256'])
                rebuilt['endpoint']['pcm_sha256']=prior['endpoint']['pcm_sha256']
            self.assertEqual(rebuilt,prior)
        for grant in (None,e.AUTH,dict(kind='ONE_REAL_EXECUTION',real_sources=True)):
            with self.assertRaisesRegex(ValueError,'PRODUCTIVE_AUTHORIZATION_ABSENT'):
                e.start_real(path,authorization=grant)
        raw=path.read_bytes();bad=copy.deepcopy(value);bad['authorization']['real_sources']=True
        path.write_bytes(e.canonical(bad))
        with self.assertRaisesRegex(ValueError,'AUTHORIZATION'):e.load(path)
        path.write_bytes(raw)
        self.assertFalse((path.parent/'claim.json').exists())

    def test_bound_supplier_full_58_and_seven_hints(self):
        path=e.prepare(self.root/'case',self.q,source_test=True)
        result=process.run_neutral(path)
        self.assertEqual(result['status'],'CLOSED_NEUTRAL_P2_VERIFIED',result)
        facts=e.read_json(path.parent/'observer/facts.json')
        self.assertEqual((facts['calls'],facts['bound_supplier_calls'],facts['replacement_calls']),(58,58,58))
        self.assertEqual(facts['real_production_calls'],0)
        self.assertEqual(facts['rejected_endpoints_before_production'],8)
        self.assertLess(facts['source_admission_ns'],facts['first_supplier_ns'])
        self.assertLessEqual(facts['first_supplier_ns'],facts['first_production_ns'])
        original={p:p.read_bytes() for p in (path.parent/'product').iterdir()}
        closed=appendix.publish(path);self.assertEqual(closed['status'],'CLOSED_NEUTRAL_PROVENANCE',closed)
        report=appendix.read(path)
        self.assertEqual(report['scope'],'BOUND_SOURCE_TEST_P2');self.assertTrue(report['test_evidence'])
        self.assertEqual(report['coverage'],dict(determinate=7,total=7))
        self.assertFalse(report['real_execution_authorized'])
        self.assertEqual(report['candidate_gains'],['g1/24'])
        self.assertEqual(report['candidate_losses'],['g1/26','g2/38','g3/67'])
        for p,data in original.items():self.assertEqual(p.read_bytes(),data)
        # A constructed-but-unused binder must invalidate an otherwise closed case.
        fp=path.parent/'observer/facts.json';raw=fp.read_bytes();facts['bound_supplier_calls']=0
        fp.write_bytes(e.canonical(facts))
        with self.assertRaisesRegex(ValueError,'BOUND_SUPPLIER_NOT_EXECUTED'):appendix.observe(path)
        fp.write_bytes(raw)

    def test_bound_production_substitute_hash_is_still_verified(self):
        path=e.prepare(self.root/'case',self.q,source_test=True)
        result=process.run_neutral(path,case='bad_hash')
        self.assertEqual(result['status'],'NOT_EVALUABLE',result)
        facts=e.read_json(path.parent/'observer/facts.json')
        self.assertEqual((facts['bound_supplier_calls'],facts['replacement_calls']),(1,1))
        record=e.codec.loads((path.parent/'product/record.json').read_bytes())
        self.assertEqual(record['source_completion']['counters']['audio_analyses'],0)

    def test_bound_missing_admission_or_job_has_no_supplier(self):
        path=e.prepare(self.root/'case',self.q,source_test=True)
        for token in ('deny','admit'):
            with self.subTest(token=token):
                folder=path.parent/token;folder.mkdir()
                cfg=dict(binding=str(path),folder=str(folder),job='Local\\MCM-P2-ABSENT',case='success',
                    inventory_sha256=e.p1.reference(path.parent/'inventory.json')['sha256'],
                    binding_sha256=e.p1.reference(path)['sha256'])
                process.save(folder/'config.json',cfg)
                run=subprocess.run([sys.executable,'-S',str(Path(process.__file__)),str(folder/'config.json'),
                    e.sha((folder/'config.json').read_bytes())],input=token+'\n',capture_output=True,
                    text=True,timeout=30,cwd=e.ROOT,creationflags=subprocess.CREATE_NO_WINDOW)
                self.assertNotEqual(run.returncode,0)
                self.assertIn('P2_ADMISSION_MISSING' if token=='deny' else 'P2_JOB_MISSING',run.stderr)
                self.assertEqual({p.name for p in folder.iterdir()},{'config.json','bootstrap.json'})
        self.assertFalse((path.parent/'product').exists())
