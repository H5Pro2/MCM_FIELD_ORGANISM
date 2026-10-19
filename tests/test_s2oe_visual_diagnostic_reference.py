import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools import _s2oe_visual_diagnostic_reference as r


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.addCleanup(patch.stopall)
        patch.object(r.shared.b, 'ROOT', self.root).start()
        self.bindings={}
        self.files={}
        for name in r.shared.b.r.ng.SOURCE_PATHS:
            self.put(name,b'neutral code binding\n')
            self.files[name]=self.bindings[name]
        self.put('oc.json',dict(version='neutral',ob=dict(files=self.files),connector={}))
        self.put('media.json',{})
        full=r.shared.b.sealed(dict(component_sources=[[p,self.files[p][0]] for p in r.shared.b.r.ng.SOURCE_PATHS]),'binding_digest')
        common=dict(version='neutral',manifest=dict(code_digest=self.bindings['media.json'][0]),
            inventory_sha256=self.bindings['oc.json'][0], references=[['sources',p,self.bindings[p][1],self.bindings[p][0]] for p in ('oc.json','media.json')],
            rule_binding={**full,'component_sources':{'$code_inventory':'ng-source-paths-v1'}},
            runtime_config=dict(neutral=True),qualification=None)
        self.common=r.shared.b.sealed(common,'common_digest')
        self.record=r.shared.b.sealed(dict(manifest=common['manifest'],references=[x[:3] for x in common['references']],
            code_digest=common['manifest']['code_digest'],execution=dict(binding=full,runtime_config=common['runtime_config'],value=[1,2,3])), 'record_digest')
        session=r.shared.b.sealed(dict(active_qualification=None),'session_digest')
        packed,sess=r.shared.pack(self.record,session,self.common)
        self.put('record.json',packed);self.put('session.json',sess);self.put('common.json',self.common)
        self.put('verification.json',r.shared.b.sealed(dict(record_digest=self.record['record_digest'],evaluation_allowed=True),'verification_digest'))

    def put(self,name,value):
        data=value if isinstance(value,bytes) else r.raw(value)
        path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        self.bindings[name]=[r.sha(data),len(data)]

    def resolve(self):return r.resolve(self.root,'',self.bindings)

    def test_native_expansion_and_digest(self):
        self.assertEqual(self.resolve()[0]['record'],self.record)
    def test_missing_file(self):
        (self.root/'oc.json').unlink()
        with self.assertRaisesRegex(r.ReferenceError,'REFERENCE_MISSING'):self.resolve()
    def test_changed_file(self):
        (self.root/'oc.json').write_bytes(b'{}')
        with self.assertRaisesRegex(r.ReferenceError,'REFERENCE_CHANGED'):self.resolve()
    def test_missing_token(self):
        import json
        x=json.loads((self.root/'record.json').read_bytes());del x['record']['manifest'];self.put('record.json',x)
        with self.assertRaisesRegex(r.shared.budget.BudgetError,'ADMIN_REFERENCE_CONFLICT'):self.resolve()
    def test_contradictory_token(self):
        import json
        x=json.loads((self.root/'record.json').read_bytes());x['record']['manifest']={'$oc_common':'runtime_config'};self.put('record.json',x)
        with self.assertRaisesRegex(r.shared.budget.BudgetError,'ADMIN_REFERENCE_CONFLICT'):self.resolve()
    def test_native_digest_not_replaced(self):
        import json
        x=json.loads((self.root/'record.json').read_bytes());x['record']['execution']['value'][0]=99;self.put('record.json',x)
        with self.assertRaisesRegex(ValueError,'DIGEST_INVALID'):self.resolve()
    def test_nested_source_missing(self):
        del self.bindings[next(iter(self.files))]
        with self.assertRaisesRegex(r.ReferenceError,'SOURCE_BINDING_INVALID'):self.resolve()
    def test_nested_source_changed(self):
        (self.root/next(iter(self.files))).write_bytes(b'changed')
        with self.assertRaisesRegex(r.ReferenceError,'REFERENCE_CHANGED'):self.resolve()
        for name,expected in r.HISTORICAL_ONLY.items():
            with self.subTest(historical=name):
                r.historical_source(self.root,name,expected,{},r.HISTORICAL_ONLY,())
            with self.subTest(active=name):
                with self.assertRaisesRegex(r.ReferenceError,'HISTORICAL_ROLE_INVALID'):
                    r.historical_source(self.root,name,expected,{},r.HISTORICAL_ONLY,(name,))
            with self.subTest(manipulated=name):
                with self.assertRaisesRegex(r.ReferenceError,'HISTORICAL_ROLE_INVALID'):
                    r.historical_source(self.root,name,['0'*64,1],{},r.HISTORICAL_ONLY,())
    def test_source_conflict(self):
        with self.assertRaisesRegex(r.ReferenceError,'SOURCE_CONFLICT'):
            r.flatten(dict(ob=dict(files={'a':['1',1]}),connector={'a':['2',1]},version='n'))
    def test_immutable_resolution(self):
        before=copy.deepcopy(self.bindings);a=self.resolve()[0];a['record']['execution']['value'][0]=9
        self.assertEqual(self.resolve()[0]['record'],self.record);self.assertEqual(before,self.bindings)
        import importlib
        for module in ('tools._s2oe_media_decoder','tools._s2oe_decoder_worker'):
            with self.subTest(blocked_import=module):
                with self.assertRaisesRegex(ImportError,'DECODER_IMPORT_FORBIDDEN'):
                    importlib.import_module(module)
    def test_full_failure_report_budget(self):
        a=r.alternatives(100,200)
        self.assertEqual(a['verification_failure']['parts']['metadata']-a['success']['parts']['metadata'],r.CAPS['failure'])
        self.assertTrue(all(not v['violations'] for v in a.values()))
    def test_metadata_boundary_and_overflow(self):
        a=r.alternatives(0,0);m=a['verification_failure']['parts']['metadata']
        self.assertEqual(r.alternatives(0,0,65536-m)['verification_failure']['violations'],[])
        self.assertIn('metadata',r.alternatives(0,0,65537-m)['verification_failure']['violations'])
    def test_global_boundary_and_overflow(self):
        a=r.alternatives(0,0)['verification_failure']['total']
        self.assertEqual(r.alternatives(4194304-a,0)['verification_failure']['violations'],[])
        self.assertIn('total',r.alternatives(4194305-a,0)['verification_failure']['violations'])
