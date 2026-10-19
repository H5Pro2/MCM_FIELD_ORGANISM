"""New frozen-connection checks; the earlier 18 tests are not imported."""
import copy
import unittest
import tempfile
import json
import sys
from pathlib import Path
from unittest.mock import patch
from tools import _visual_b_comparison as c
from tools import _visual_b_ledger as ledger
from reports import run_visual_b_comparison as entry


def native_history():
    core=dict(initial=dict(memory='e'*64),config_digest='f'*64,rows=[],states={})
    chain=c.frozen.digest(dict(initial='e'*64,config='f'*64))
    births=[None]*24
    for ordinal in range(1,5):
        def slot(i,key):return dict(slot_id=f'slot.{i:03}',occupied=False,support_count=None,**{key:[]})
        fast=[dict(slot_id=f'fast.{i:03}',occupied=False,support_count=None,auditory_values=[],visual_values=[]) for i in range(3)]
        visual=[slot(i,'prototype_values') for i in range(4)]
        if ordinal>=2:
            visual[0].update(occupied=True,support_count=ordinal-1,prototype_values=[0.0]*288)
            births[20]=2
        state=dict(b4_state=dict(entries=[slot(i,'values') for i in range(9)]),
            tspm_state=dict(fast_state=dict(slots=fast),auditory_ppb1_state=dict(slots=[slot(i,'prototype_values') for i in range(8)]),
                            visual_ppb1_state=dict(slots=visual)),generation=ordinal)
        state['state_digest']=c.frozen.digest(state)
        core['states'][state['state_digest']]=c.frozen.codec.encode(state)
        actions=['FREE']*24
        if ordinal>=2:actions[20]='CREATED' if ordinal==2 else 'MATCHED'
        transaction=c.frozen.digest(dict(neutral_formation=ordinal))
        gen=dict(event=ordinal,previous=chain,transaction=transaction,births=list(births),actions=actions)
        gen['chain_digest']=c.frozen.digest(gen);chain=gen['chain_digest']
        core['rows'].append(dict(memory=state['state_digest'],chain_digest=chain,current_births=list(births),
                                generations=gen,formation=dict(result_digest=transaction)))
    expected=dict(row=3,memory_digest=state['state_digest'],chain_digest=chain,births=list(births))
    record=dict(status='RECORDING_COMPLETE',execution=core)
    record['record_digest']=c.frozen.digest(record)
    proof=dict(evaluation_allowed=True,core=dict(record_digest=record['record_digest']))
    return core,expected,record,proof


def native_resolver():
    core,expected,record,proof=native_history()
    return c.frozen.authenticate(record,proof,expected),core,expected


def neutral_materializer(source,seal,counters):
    def one(row):
        counters['analyses']+=1
        return (0.0,)*32
    return one


def binding():
    candidates=[]
    for bank,count,start in (('B4',9,0),('FAST',3,9),('B',4,20)):
        for i in range(count):
            occupied=bank=='B' and i==0
            candidates.append(dict(bank=bank,flat_index=start+i,slot_id=f'{bank}.{i:03}',
                slot_digest=str(i)*64,occupied=occupied,support=3 if occupied else None,
                values=[0.0]*288 if occupied else [],generation=2 if occupied else None,
                formation_ordinals=[2,3,4] if occupied else []))
    value=dict(version=c.frozen.VERSION,memory_digest='a'*64,chain_digest='b'*64,
               candidates=candidates,source_record_required=True,historical_transition_proof_required=True)
    value['binding_digest']=c.frozen.digest(value)
    return value


class Connection(unittest.TestCase):
    def setUp(self):
        guard=patch.object(entry.sources.s,'render',side_effect=AssertionError('REAL_SOURCE_FORBIDDEN'))
        guard.start();self.addCleanup(guard.stop)
    def test_complete_negative_and_readonly(self):
        b=binding();before=copy.deepcopy(b);source,_=c.d.plans()
        record=c.record_steps(source,b,lambda row:(1.0,)*32)
        self.assertEqual(record['status'],'RECORDING_COMPLETE')
        proof=c.verify(record,source,b)
        self.assertTrue(proof['evaluation_allowed'])
        self.assertEqual(b,before)
        self.assertTrue(all(r['primary']['b'][0]['decision']=='ABSTAIN_NO_APPLICABLE_CONTEXT' for r in record['rows']))

    def test_source_manipulation(self):
        b=binding();source,_=c.d.plans()
        record=c.record_steps(source,b,lambda row:(0.0,)*32)
        self.assertEqual(record['status'],'RECORDING_COMPLETE')
        record['rows'][0]['source_digest']='x'
        with self.assertRaisesRegex(c.frozen.FrozenBindingError,'CUE_SOURCE'):
            c.verify(record,source,b)

    def test_generation_manipulation(self):
        b=binding();b['candidates'][-4]['generation']=3
        with self.assertRaisesRegex(c.frozen.FrozenBindingError,'BINDING_DIGEST'):
            c.compare((0.0,)*32,b)

    def test_failure_blocks_evaluation(self):
        b=binding();source,evaluation=c.d.plans()
        def failed(row):raise ValueError('NEUTRAL_FAILURE')
        record=c.record_steps(source,b,failed)
        self.assertEqual(record['status'],'NOT_EVALUABLE')
        proof=c.verify(record,source,b)
        self.assertFalse(proof['evaluation_allowed'])
        with self.assertRaisesRegex(c.frozen.FrozenBindingError,'EVALUATION_GATE'):
            c.evaluate(record,proof,evaluation,source)

    def test_independent_verification(self):
        b=binding();source,_=c.d.plans()
        record=c.record_steps(source,b,lambda row:(0.0,)*32)
        self.assertEqual(record['status'],'RECORDING_COMPLETE')
        with patch.object(c,'a_primary',side_effect=AssertionError('PRIMARY_FORBIDDEN')):
            self.assertTrue(c.verify(record,source,b)['evaluation_allowed'])

    def test_roles_and_nonindependence(self):
        b=binding();source,evaluation=c.d.plans()
        record=c.record_steps(source,b,lambda row:(0.0,)*32)
        self.assertEqual(record['status'],'RECORDING_COMPLETE')
        result=c.evaluate(record,c.verify(record,source,b),evaluation,source)
        self.assertEqual([g['N'] for g in result['groups']],[3,2,1,1])
        self.assertTrue(result['byte_identical_not_independent'])
        self.assertIsNone(result['independent_replication_count'])

    def test_native_codec_and_authenticated_origin(self):
        core,expected,record,proof=native_history();before=c.frozen.digest(core)
        result=c.frozen.authenticate(record,proof,expected)
        target=result['candidates'][12]
        self.assertEqual(target['generation'],2)
        self.assertEqual(target['formation_ordinals'],[2,3,4])
        self.assertEqual(target['support'],3)
        self.assertEqual(c.frozen.digest(core),before)
        self.assertEqual(c.frozen.verify_binding(result,core,expected)['status'],'FROZEN_BINDING_VALID')

    def test_native_tampering_independent(self):
        for code,change in (
            ('NATIVE_RECORD_DIGEST',lambda r,p:r.update(status='BROKEN')),
            ('HISTORICAL_PROOF',lambda r,p:p['core'].update(record_digest='0'*64))):
            with self.subTest(code=code):
                core,expected,record,proof=native_history();change(record,proof)
                with self.assertRaisesRegex(c.frozen.FrozenBindingError,code):c.frozen.authenticate(record,proof,expected)
        core,expected,record,proof=native_history()
        core['states'][expected['memory_digest']]['native_sha256']='0'*64
        with self.assertRaisesRegex(c.frozen.FrozenBindingError,'FROZEN_NATIVE_INVALID'):c.frozen.extract(core,expected)

    def test_replaced_generation_same_id(self):
        core,expected,_,_=native_history()
        old=c.frozen.extract(core,expected)
        last=core['rows'][3];gen=last['generations']
        gen['actions'][20]='REPLACED';gen['births'][20]=4
        gen['chain_digest']=c.frozen.digest({k:v for k,v in gen.items() if k!='chain_digest'})
        last['chain_digest']=gen['chain_digest'];last['current_births'][20]=4
        expected.update(chain_digest=gen['chain_digest'],births=list(gen['births']))
        new=c.frozen.extract(core,expected)
        self.assertEqual(new['candidates'][12]['slot_id'],old['candidates'][12]['slot_id'])
        self.assertEqual(new['candidates'][12]['generation'],4)
        with self.assertRaisesRegex(c.frozen.FrozenBindingError,'CANDIDATE_ORIGIN'):c.frozen.verify_binding(old,core,expected)

    def test_generation_chain_and_free_slots(self):
        for mutation,code in ((lambda x:x['rows'][1]['generations'].update(previous='x'),'GENERATION_ORDER'),
                              (lambda x:x['rows'][1]['formation'].update(result_digest='x'),'TRANSACTION_BINDING')):
            with self.subTest(code=code):
                core,expected,_,_=native_history();mutation(core)
                with self.assertRaisesRegex(c.frozen.FrozenBindingError,code):c.frozen.extract(core,expected)
        core,expected,_,_=native_history()
        self.assertTrue(all(x['generation'] is None for x in c.frozen.extract(core,expected)['candidates'] if not x['occupied']))

    def test_native_successful_entry_and_once(self):
        source,evaluation=c.d.plans()
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'once'
            result=entry.execute(out,{},source,evaluation,dict(collisions=[]),native_resolver,neutral_materializer)
            self.assertEqual(result['status'],'RECORDING_COMPLETE')
            self.assertEqual(result['analyses'],7)
            self.assertTrue(entry.read(out/'verification.json')['evaluation_allowed'])
            self.assertFalse(result['violations'])
            with self.assertRaises(FileExistsError):entry.execute(out,{},source,evaluation,{},native_resolver,neutral_materializer)

    def test_native_failure_after_progress(self):
        source,evaluation=c.d.plans()
        def failing(source,seal,counters):
            def one(row):
                counters['analyses']+=1
                if counters['analyses']==3:raise ValueError('NEUTRAL_ANALYSIS_FAILURE')
                return (0.0,)*32
            return one
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'failure'
            result=entry.execute(out,{},source,evaluation,{},native_resolver,failing)
            self.assertEqual(result['status'],'NOT_EVALUABLE')
            self.assertEqual(result['completed'],2)
            self.assertEqual(result['analyses'],3)
            self.assertFalse((out/'evaluation.json').exists())
            self.assertEqual(entry.read(out/'error.json')['error'],'NEUTRAL_ANALYSIS_FAILURE')

    def test_actual_global_budget_and_temp(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);(p/'record.json.tmp').write_bytes(b'{}')
            result=ledger.measure(p,{},phase='VERIFY',completed=1)
            self.assertIn('TEMPORARY_REMAINS:record.json.tmp',result['violations'])
            self.assertEqual(result['parts']['evidence'],2)
        entries=[dict(name='metadata',kind='metadata',bytes=131072)]
        self.assertFalse(ledger.totals(entries)['violations'])
        entries[0]['bytes']+=1
        self.assertEqual(ledger.totals(entries)['violations'],['metadata'])
        result=ledger.totals([dict(name='sources',kind='sources',bytes=4194305)])
        self.assertEqual(result['violations'],['total'])

    def test_public_denominator_and_loss(self):
        b=binding();source,evaluation=c.d.plans()
        # A second stable B candidate is outside exact equality but inside tau:
        # target applicability remains while the public unique admission is lost.
        other=b['candidates'][13]
        other.update(occupied=True,support=3,values=[c.d.TAU/2]*288,generation=3,formation_ordinals=[3])
        b['binding_digest']=c.frozen.digest({k:v for k,v in b.items() if k!='binding_digest'})
        record=c.record_steps(source,b,lambda row:(0.0,)*32)
        self.assertEqual(record['status'],'RECORDING_COMPLETE')
        result=c.evaluate(record,c.verify(record,source,b),evaluation,source)
        first=result['groups'][0]
        self.assertEqual((first['D'],first['R'],first['L']),(3,3,0))
        self.assertEqual((first['public']['D'],first['public']['R'],first['public']['L']),(3,0,3))

    def test_budget_alternatives(self):
        result=ledger.preflight({})
        success,failure=result['alternatives']
        self.assertNotIn('error.json',[x['name'] for x in success['contributions']])
        self.assertNotIn('evaluation.json',[x['name'] for x in failure['contributions']])
        self.assertTrue(all(any(x['name']=='temporary-publication' for x in a['contributions']) for a in result['alternatives']))

    def test_admission_pin_gate_and_profile(self):
        with self.assertRaisesRegex(c.frozen.FrozenBindingError,'PROFILE_BINDING'):
            entry.load_frozen(Path('never-read'),dict(profile='wrong'))
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            def put(name,value):
                (root/name).write_bytes(entry.sources.s.raw(value))
                return dict(kind='metadata',**entry.sources.pin(root/name))
            inv={};ip=put('inventory.json',inv)
            qp=put('qualification.json',dict(status='QUALIFIED',version=c.VERSION,inventory_digest=c.frozen.digest(inv)))
            permit=dict(authorized=True,version=c.VERSION,budget_version=ledger.VERSION,
                references={'inventory.json':ip,'qualification.json':qp},inventory='inventory.json',
                qualification='qualification.json',output='neutral-once',run_id='neutral-once')
            pin=put('admission.json',permit)
            self.assertEqual(entry.check_admission(root/'admission.json',pin['sha256'],root)[2],root/'neutral-once')
            with self.assertRaisesRegex(c.frozen.FrozenBindingError,'ADMISSION_PIN'):
                entry.check_admission(root/'admission.json','0'*64,root)
            permit['budget_version']='historical';pin=put('admission.json',permit)
            with self.assertRaisesRegex(c.frozen.FrozenBindingError,'ADMISSION'):
                entry.check_admission(root/'admission.json',pin['sha256'],root)
            c.MAIN_GATE=False
            with self.assertRaisesRegex(c.frozen.FrozenBindingError,'GATE_CLOSED'):entry.run(root/'admission.json',pin['sha256'])

    def test_a_does_not_fill_b_public_denominator(self):
        b=binding();source,evaluation=c.d.plans()
        b['candidates'][0].update(occupied=True,values=[1.0]*288,generation=1,formation_ordinals=[1])
        b['binding_digest']=c.frozen.digest({k:v for k,v in b.items() if k!='binding_digest'})
        record=c.record_steps(source,b,lambda row:(1.0,)*32)
        self.assertEqual(record['status'],'RECORDING_COMPLETE')
        result=c.evaluate(record,c.verify(record,source,b),evaluation,source)
        group=result['groups'][0]
        self.assertEqual(group['D'],0)
        self.assertEqual(group['public']['D'],0)
        self.assertEqual(group['public']['preservation'],'ERHALTUNG_NICHT_GEPRUEFT')
        self.assertTrue(result['rows'][0]['a_admission_unassigned_to_b_target'])

    def test_primary_error_survives_temporary_failure(self):
        source,evaluation=c.d.plans()
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'failure'
            def make(source,seal,counters):
                def one(row):
                    (out/'record.json.tmp').write_bytes(b'leftover')
                    raise ValueError('PRIMARY_NEUTRAL')
                return one
            with self.assertRaises(ledger.BudgetError):
                entry.execute(out,{},source,evaluation,{},native_resolver,make)
            error=entry.read(out/'error.json')
            self.assertEqual(error['error'],'PRIMARY_NEUTRAL')
            self.assertTrue((out/'record.json.tmp').exists())
            self.assertFalse((out/'evaluation.json').exists())

    def test_outer_entry_native_codec_boundary(self):
        core,expected,native,proof=native_history()
        b=c.frozen.authenticate(native,proof,expected)
        source,evaluation=c.d.plans()
        source.update(profile='visual.grid12x8.channels3.source1920x1080.v1',
            frozen=dict(expected,runtime_config_digest='neutral-runtime-profile'))
        seal=dict(execution_digest=c.frozen.digest(source),evaluation_digest=c.frozen.digest(evaluation),collisions=[])
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);files={}
            def put(name,value,kind='metadata'):
                path=root/name;path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(entry.sources.s.raw(value))
                item=dict(kind=kind,**entry.sources.pin(path));files[name]=item
                return item
            common=put('common.json',dict(runtime_config=dict(config_digest='neutral-runtime-profile')))
            put(entry.sources.MEM+'common-reference.json',dict(path='common.json',**{k:common[k] for k in ('bytes','sha256')}))
            put(entry.sources.MEM+'record.json',native,'evidence')
            put(entry.sources.MEM+'session.json',{})
            put(entry.sources.MEM+'verification.json',proof,'verification')
            put(entry.SEAL+'execution.json',source);put(entry.SEAL+'evaluation.json',evaluation)
            put(entry.SEAL+'seal.json',seal)
            put(entry.SEAL+'verification.json',dict(status='BINDING_VALID',record_digest=c.frozen.digest(seal)))
            put('frozen.json',b,'evidence')
            inventory=copy.deepcopy(files)
            ip=put('inventory.json',inventory,'sources')
            qp=put('qualification.json',dict(status='QUALIFIED',version=c.VERSION,inventory_digest=c.frozen.digest(inventory)))
            permit=dict(authorized=True,version=c.VERSION,budget_version=ledger.VERSION,
                references={'inventory.json':ip,'qualification.json':qp},inventory='inventory.json',qualification='qualification.json',
                output='neutral-main',run_id='neutral-main',frozen_binding='frozen.json',
                environment=dict(interpreter=entry.sources.pin(Path(sys.executable)),numpy_version=entry.np.__version__,
                                 numpy_init=entry.sources.pin(Path(entry.np.__file__))))
            pin=put('admission.json',permit)
            # Historical shared-wire expansion is reused, not requalified here.
            # New authentication, native codec, provenance, run and close are real.
            with patch.object(entry.sources,'ROOT',root),patch.object(entry.shared,'unpack',return_value=(native,{})),\
                 patch.object(entry,'materializer',side_effect=neutral_materializer),patch.object(c,'verify',wraps=c.verify) as verify:
                c.MAIN_GATE=True
                result=entry.run(root/'admission.json',pin['sha256'])
                self.assertEqual(result['status'],'RECORDING_COMPLETE')
                self.assertEqual(verify.call_count,1)
                self.assertFalse(c.MAIN_GATE)
                c.MAIN_GATE=True
                with self.assertRaisesRegex(c.frozen.FrozenBindingError,'OUTPUT_USED'):
                    entry.run(root/'admission.json',pin['sha256'])
                self.assertEqual(verify.call_count,1)


if __name__=='__main__':
    unittest.main()
