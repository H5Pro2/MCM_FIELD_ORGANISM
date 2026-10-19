import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools import _s2uc_comparison_preparation as p
from tools import _s2nu_private_source_binding as nu
from tools import s2uc_run_bound_once as starter
from tools import _s2uc_source_execution as execution

class PreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inv = p.current()

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(dir=p.ROOT / 'reports/s2uc', prefix='p1-')
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name); self.folder = self.root / 'prep'
        self.addCleanup(patch.stopall)
        patch.object(p, 'current', return_value=self.inv).start()
        self.source = patch.object(nu, 'pcm_window', side_effect=AssertionError('SOURCE_OPENED')).start()
        self.write('dependency-inventory.json', self.inv)
        ids = [n for n in p.test_ids() if n.startswith('tests.test_s2uc_comparison_preparation.')]
        self.result = dict(test_ids=ids, results=dict.fromkeys(ids, 'PASS'), tests_run=len(ids),
                           errors=0, failures=0, skips=0, exit_code=0, formal_qualification=False,
                           real_execution_authorized=False, code_unchanged=True,
                           expected_ids_complete=True, inventory=p.reference(self.root / 'dependency-inventory.json'))
        self.write('test-result.json', self.result)
        self.groups = []
        for folder in [p.ROOT/'reports/s2uc'/n for n in
                       ('provenance-appendix-repeat-20260929-01','regression-105-20260930-01')]+[self.root]:
            self.groups.append({k:p.reference(folder/name) for k,name in
                                [('result','test-result.json'),('inventory','dependency-inventory.json')]})

    def tearDown(self):
        self.source.assert_not_called()

    def write(self, name, value):
        (self.root/name).write_bytes(p.canonical(value))

    def build(self):
        return p.prepare(self.folder, self.groups, self.root / 'dependency-inventory.json')

    def test_complete_preparation_and_closed_starters(self):
        self.build(); result = p.read(self.folder)
        self.assertEqual(result['test_count'], len(p.test_ids()))
        self.assertFalse(result['real_execution_authorized'])
        self.assertLessEqual((self.folder / 'protocol.json').stat().st_size, 32768)
        paths = {r['path'] for r in result['budget']['files']}
        self.assertTrue(all(g[k]['path'] in paths for g in self.groups for k in g))
        for authorized in (False, True):
            with self.assertRaises(ValueError):
                starter.start(self.root / 'output', authorize=authorized, binding_file=self.folder / 'preparation.json')
        with self.assertRaisesRegex(ValueError, 'V9_REAL_EXECUTION_DISABLED'):
            execution.start_real(p.old.b.context.source_context())
        self.assertFalse(starter.entry.MAIN_GATE)

    def test_bound_file_mutations(self):
        self.build()
        saved = {x.name: x.read_bytes() for x in self.folder.iterdir()}
        cases = [('preparation', 'run_id', 'NEUTRAL'), ('preparation', 'output', 'reports/other'),
                 ('preparation', 'authority.real_execution_authorized', True),
                 ('preparation', 'evaluation', []), ('source-context', 'targets', {}),
                 ('resources', 'limits.code', 999999), ('protocol', 'padding', 'x'*32768),
                 ('protocol', 'rows', []), ('ledger', 'actual.categories.code', 0)]
        for stem, field, value in cases:
            with self.subTest(file=stem, field=field):
                name=stem+'.json'; changed=json.loads(saved[name]); node=changed
                parts=field.split('.')
                for part in parts[:-1]: node=node[part]
                node[parts[-1]]=value; self.write('prep/'+name,changed)
                if stem in ('source-context','resources','protocol'):
                    binding=json.loads(saved['preparation.json'])
                    binding['context' if stem=='source-context' else stem]=p.reference(self.folder/name)
                    self.write('prep/preparation.json',binding)
                with self.assertRaises(ValueError): p.read(self.folder)
                for key,data in saved.items(): (self.folder/key).write_bytes(data)
        (self.folder/'extra').write_bytes(b'x')
        with self.assertRaises(ValueError): p.read(self.folder)

    def test_missing_failed_duplicate_and_stale_original_evidence(self):
        for kind in ('missing', 'fail', 'inventory', 'duplicate'):
            with self.subTest(kind=kind):
                value=copy.deepcopy(self.result); groups=copy.deepcopy(self.groups)
                key=value['test_ids'][0]
                if kind=='missing': value['test_ids'].remove(key); del value['results'][key]; value['tests_run']-=1
                if kind=='fail': value['results'][key]='FAIL'
                if kind=='inventory': value['inventory']['sha256']='0'*64
                if kind=='duplicate': groups.append(groups[0])
                self.write('test-result.json',value); groups[2]['result']=p.reference(self.root/'test-result.json')
                with self.assertRaises(ValueError): p._coverage(groups,self.inv,{})
        self.write('test-result.json',self.result); self.build(); self.write('test-result.json',{})
        with self.assertRaisesRegex(ValueError,'P1_REFERENCE_CHANGED'): p.read(self.folder)

    def test_code_runtime_and_resource_boundaries(self):
        for runtime in (False,True):
            prior=copy.deepcopy(self.inv)
            row=prior['external']['interpreter'] if runtime else prior['files'][0]
            row['sha256']='0'*64
            with self.assertRaises(ValueError): p._compatible(prior,self.inv)
        for category,limit in [('code',868340),('metadata',65536),('static_shared',196608)]:
            amounts=dict.fromkeys(p.old.b.resources.CATEGORIES,0); amounts[category]=limit
            self.assertTrue(p.resources.account(amounts)['within_limits'])
            amounts[category]+=1
            self.assertFalse(p.resources.account(amounts)['within_limits'])
        self.assertEqual(p.resources.old.LIMITS['code'],851968)
