import copy
import ast
import math
import json
import os
from pathlib import Path
import unittest
import io
import sys
import tempfile
from unittest.mock import patch
from tools import _structure_ppb_chain as c


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources=[dict(id=f'neutral-{i}',frame_index=i,time=[i,30]) for i in range(6)]
        cls.values=[(x,)*288 for x in (0.1,0.14,0.105,0.5,0.505,0.51)]
        cls.binding=dict(mode='NEUTRAL',sources=cls.sources)
        cls.record=c.generate(cls.values,cls.sources,cls.binding)
        if cls.record['status']!='RECORDING_COMPLETE':raise AssertionError('NATIVE_NOT_REACHED')
        cls.proof=c.verify(cls.record,cls.values,cls.sources,cls.binding)
        if cls.proof['status']!='EVIDENCE_VALID':raise AssertionError('VERIFICATION_NOT_REACHED')
        out=Path(os.environ['PPB_CHAIN_NEUTRAL'])
        with (out/'neutral-record.json').open('xb') as f:f.write(c.s.raw(cls.record))
        with (out/'neutral-verification.json').open('xb') as f:f.write(c.s.raw(cls.proof))

    def test_native_and_sizes(self):
        self.assertEqual(self.record['counts']['transitions'],9)
        self.assertLessEqual(len(c.s.raw(self.record)),1048576)
        for chain in self.record['chains']:
            for state in chain['states']:self.assertLessEqual(len(c.s.raw(state)),40960)
        supports=[chain['steps'][-1]['readout']['support_count'] for chain in self.record['chains']]
        self.assertIn(3,supports);self.assertIn(1,supports)

    def test_clock_binding(self):
        f=c.contact(c.config(),self.sources[2],self.values[2],1)
        self.assertEqual((f.window_start_tick,f.window_end_tick,f.clock_id),(2,3,'structure.ppb.k2'))
        bad=copy.deepcopy(self.sources[2]);bad['time']=[3,30]
        with self.assertRaisesRegex(c.ChainError,'SOURCE_TIME'):c.contact(c.config(),bad,self.values[2],1)

    def test_order(self):
        r=copy.deepcopy(self.record);r['chains'][0]['steps'].reverse()
        with self.assertRaisesRegex(c.ChainError,'ORDER'):c.verify(r,self.values,self.sources,self.binding)

    def test_bank_isolation(self):
        r=copy.deepcopy(self.record);r['chains'][1]['states']=r['chains'][0]['states']
        with self.assertRaises(c.ChainError):c.verify(r,self.values,self.sources,self.binding)

    def test_generation(self):
        r=copy.deepcopy(self.record);r['chains'][0]['steps'][1]['births_after'][0]['step']=2
        with self.assertRaisesRegex(c.ChainError,'POST_GENERATION'):c.verify(r,self.values,self.sources,self.binding)

    def test_values_mutation(self):
        r=copy.deepcopy(self.record);r['chains'][0]['states'][1]['slots'][0]['prototype_values'][0]=0.0
        with self.assertRaisesRegex(c.ChainError,'STATE_DIGEST'):c.verify(r,self.values,self.sources,self.binding)

    def test_error_progress(self):
        progress={}
        with patch.object(c.diagnostic,'table',side_effect=ValueError('NEUTRAL_TABLE_FAILURE')):
            with self.assertRaisesRegex(ValueError,'NEUTRAL_TABLE_FAILURE'):
                c.generate(self.values,self.sources,self.binding,progress)
        self.assertEqual(progress['completed'],1)
        self.assertEqual(progress['chains'][0]['states'][1]['accepted_step_count'],1)
        out=Path(os.environ['PPB_CHAIN_NEUTRAL'])
        with (out/'neutral-failure-progress.json').open('xb') as f:f.write(c.s.raw(progress))

    def test_negative_evaluation_and_no_replay(self):
        before=c.s.raw(self.record)
        with patch.object(c.ppb,'advance_ppb1_bank',side_effect=AssertionError('REPLAY')):
            c.verify(self.record,self.values,self.sources,self.binding)
        self.assertEqual(c.s.raw(self.record),before)
        pairs=[dict(indices=[seq[0],seq[2]],matched=False,distance=(0.5).hex()) for seq in c.SEQUENCES]
        result=c.evaluate(self.record,self.proof,pairs)
        self.assertEqual(len(result['third_inputs']),3)
        self.assertFalse(result['full_memory_test'])
        with self.assertRaisesRegex(c.ChainError,'EVALUATION_GATE'):c.evaluate(self.record,{},pairs)

    def reference_functions(self):
        tree=ast.parse(Path(os.environ['PPB_CHAIN_ARCHIVE']).read_text())
        nodes=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef))
               and n.name in ('DiagnosticError','need','table','verify')]
        scope=dict(math=math,wire=c.diagnostic.wire,ppb=c.ppb)
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'archived-pure-functions','exec'),scope)
        return scope,nodes

    def sample_data(self):
        chain=self.record['chains'][0];step=chain['steps'][1]
        return dict(config=self.record['config'],values=step['frame']['values'],frame=step['frame'],
            pre=chain['states'][1],post=chain['states'][2],observed=step['readout'],births=step['births_before'])

    def test_extraction_ast_and_shared_import(self):
        _,old=self.reference_functions()
        tree=ast.parse(Path(c.diagnostic.__file__).read_text())
        new=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef))]
        self.assertEqual([ast.dump(x,include_attributes=False) for x in old],
                         [ast.dump(x,include_attributes=False) for x in new])
        historical=ast.parse((Path(c.__file__).parent/'_s2oe_visual_transition_diagnostic.py').read_text())
        shared=next(n for n in historical.body if isinstance(n,ast.ImportFrom) and n.module=='tools._ppb_visual_transition_table')
        self.assertEqual({a.name for a in shared.names},{'DiagnosticError','need','table','verify'})

    def test_extraction_equivalence_boundary(self):
        old,_=self.reference_functions();data=self.sample_data()
        # Bind an exact observed distance as the inclusive neutral boundary.
        data=copy.deepcopy(data)
        actual=c.diagnostic.table(data)['rows'][0]['distance']
        data['config']['match_threshold']=actual
        newtable=c.diagnostic.table(data);oldtable=old['table'](data)
        self.assertEqual(newtable,oldtable);self.assertTrue(newtable['rows'][0]['matched'])
        self.assertEqual(c.diagnostic.verify(data,newtable),old['verify'](data,oldtable))

    def test_extraction_error_equivalence(self):
        old,_=self.reference_functions();data=self.sample_data()
        table=copy.deepcopy(self.record['chains'][0]['steps'][1]['table'])
        table['rows'][0]['terms']=[]
        for verify in (old['verify'],c.diagnostic.verify):
            with self.subTest(module=verify.__module__):
                with self.assertRaisesRegex(ValueError,'TERMS_INCOMPLETE'):verify(data,table)

    def test_extracted_verifier_independent(self):
        data=self.sample_data();table=self.record['chains'][0]['steps'][1]['table']
        with patch.object(c.ppb,'normalized_mean_l1_distance',side_effect=AssertionError('PRODUCT_DISTANCE_REPLAY')):
            self.assertEqual(c.diagnostic.verify(data,table)['status'],'EVIDENCE_VALID')

    def test_bounded_error_primary_and_progress(self):
        from reports import qualify_structure_chain_once as runner
        progress=dict(chains=self.record['chains'],completed=9)
        before=c.s.raw(progress)
        error=c.ChainError('STATE_LIMIT')
        error.__cause__=ValueError('x'*100000)
        result=runner.failure_evidence(error,'ADVANCE',progress,self.binding)
        self.assertEqual(result['primary_code'],'STATE_LIMIT')
        self.assertEqual(result['completed'],9)
        self.assertEqual(result['last_state']['state_index'],3)
        self.assertEqual(c.s.raw(progress),before)
        self.assertLessEqual(len(c.s.raw(result)),8192)

    def test_overlong_unknown_error(self):
        from reports import qualify_structure_chain_once as runner
        result=runner.failure_evidence(ValueError('\U0001f600'*10000),'VERIFY',{},self.binding)
        self.assertEqual(result['primary_code'],'UNKNOWN_ERROR')
        self.assertEqual(result['diagnostic_status'],'DIAGNOSTIC_LIMIT_REACHED')
        self.assertFalse(result['diagnostic_complete'])
        self.assertLessEqual(len(c.s.raw(result)),8192)

    def test_output_limit_and_equality(self):
        from reports import qualify_structure_chain_once as runner
        for size,expected in ((4096,False),(4097,True)):
            with self.subTest(size=size):
                log=io.BytesIO()
                code,overflow=runner.capture([sys.executable,'-c',f'import sys;sys.stdout.write("x"*{size})'],log,dict(os.environ))
                self.assertEqual(overflow,expected)
                self.assertEqual(len(log.getvalue()),4096)
                if not expected:self.assertEqual(code,0)

    def test_format_bound(self):
        from reports import qualify_structure_chain_once as runner
        self.assertLessEqual(len(c.s.raw(self.record)),runner.CAPS['record.json'])
        remainder=copy.deepcopy(self.record)
        for chain in remainder['chains']:
            for state in chain['states']:
                for slot in state['slots']:slot['prototype_values']=[]
            for step in chain['steps']:
                for carrier in step['frame']['carrier_ids']:
                    self.assertLessEqual(len(c.s.raw(carrier))+1,32)
                step['frame']['carrier_ids']=[];step['frame']['values']=[]
                step['readout']['prototype_values']=[]
                for row in step['table']['rows']:
                    for term in row['terms']:self.assertLessEqual(len(c.s.raw(term))+1,100)
                    row['terms']=[]
        self.assertLessEqual(len(c.s.raw(remainder)),65536)

    def test_write_failure_preserves_primary(self):
        from reports import qualify_structure_chain_once as runner
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(runner,'save',side_effect=OSError('disk unavailable')):
                result=runner.close_failure(Path(tmp),c.ChainError('STATE_LIMIT'),'ADVANCE',
                    dict(chains=self.record['chains'],completed=9),self.binding)
            self.assertFalse(result['secured'])
            self.assertEqual(result['primary']['primary_code'],'STATE_LIMIT')
            self.assertEqual(result['primary']['completed'],9)

    def test_finally_failure_preserves_primary(self):
        from reports import qualify_structure_chain_once as runner
        primary=dict(primary_code='STATE_LIMIT')
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(runner,'save',side_effect=OSError('disk unavailable')):
                result=runner.finish_balance(Path(tmp),{},dict(primary=primary,secured=True))
        self.assertEqual(result['status'],'CLOSURE_NOT_SECURED')
        self.assertEqual(result['primary'],primary)

    def test_temporary_class_and_no_duplicate_destination(self):
        from reports import qualify_structure_chain_once as runner
        self.assertEqual(runner.kind('record.json.tmp'),'evidence')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with patch.object(Path,'rename',side_effect=OSError('rename failed')):
                with self.assertRaises(OSError):runner.save(root,'verification.json',dict(status='NEUTRAL'))
            self.assertTrue((root/'verification.json.tmp').exists())
            self.assertFalse((root/'verification.json').exists())
            self.assertLessEqual((root/'verification.json.tmp').stat().st_size,32768)
