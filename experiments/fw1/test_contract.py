"""New FW1 contract checks; no historical suites or research execution."""
import copy,json,unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch
from .adapter import ResetAdapter
from . import engine,sources,statistics
from .reference import Reference
from .archive_reference import Reference as ArchiveReference
from .integration import pair_receipt
from tools._s2uc_multi_error import CELL,ADMITTING,POLICY
from tools._s2uc_factor_recency import FactorRecencyArm
from tools._s2uc_pair_context_adapter import PerceptionSample
from tools._s2uc_k1_probe import cellmap,snapshot

LOG=Path('reports/s2uc/fw1-neutral-qualification-20261018-01/execution-ledger.jsonl')
def event(**data):
    with LOG.open('a') as f:f.write(json.dumps(data)+'\n')

def fixture(n=2,t=3):
    return [dict(pair=i,orientation=(i-1)%2,complete=True,conditions={label:dict(pair=i,condition=label,complete=True,cleanup=True,stock_equal=True,integrity='PASS_DELTA_INTEGRITY',targets=list(range(3,3+2*t,2)),KEEP=[.25]*t,RESET=[.5]*t,resets=[dict(end=4,deleted=1)]) for label in ('A','B')}) for i in range(1,n+1)]

class Contract(unittest.TestCase):
    def test_01_cells_offsets_zero_signs_and_role(self):
        # Artificial state-only calls, not policy histories.
        for offsets in ((),(0,),(1,),(0,1)):
            for ec,ep in ((0.,0.),(.5,.25),(.25,.5),(.5,.5)):
                a=object.__new__(ResetAdapter);a.bank=bytearray(416);a.bank[408]=ADMITTING
                a.admitted=12;a.first_ordinal=1;a.arm=NS(_retained_many=[NS(generation=7),NS(generation=8)],_candidate=NS(candidate_generation=7),_observation_end={7:12,8:8})
                for slot,off in enumerate(offsets):CELL.pack_into(a.bank,slot*32,7,ec,ep,0,off,0,1)
                CELL.pack_into(a.bank,128,8,.1,.2,0,0,0,1);CELL.pack_into(a.bank,160,7,.1,.2,1,0,0,1)
                before=bytes(a.bank);a._invalidate_confirmed(7)
                self.assertEqual(bytes(a.bank[128:]),before[128:]);self.assertFalse(any(a.bank[:128]))
                with self.assertRaisesRegex(ValueError,'RESET_GENERATION'):a._invalidate_confirmed(9)
                with self.assertRaisesRegex(ValueError,'RESET_ENDMARK'):a._invalidate_confirmed(8)

    def history(self,*,fault=None,duplicate=False,seed=False):
        test=self;captures=[];before={};reset_count=0
        class Observed(ResetAdapter):
            def _checkpoint(a,stage,index):
                nonlocal reset_count
                if stage=='reset_validated':
                    reset_count+=1
                    before.clear();before.update(bank=bytes(a.bank[192:]),frozen=tuple(a._frozen),pframe=a._pframe,pending=a.pending_prediction,output=repr(a.pending_prediction),stock=json.dumps(snapshot(a.arm),sort_keys=True))
                if stage=='reset_cell' and fault=='partial':raise MemoryError('INJECTED_PARTIAL')
                if stage=='reset_complete':
                    test.assertEqual(bytes(a.bank[192:]),before['bank']);test.assertEqual(tuple(a._frozen),before['frozen'])
                    test.assertTrue(all(x is y for x,y in zip(a._frozen,before['frozen'])));test.assertIs(a._pframe,before['pframe']);test.assertIs(a.pending_prediction,before['pending'])
                    test.assertEqual(repr(a.pending_prediction),before['output']);test.assertEqual(json.dumps(snapshot(a.arm),sort_keys=True),before['stock'])
                    captures.append((a.admitted,dict(cellmap(a))))
        a=Observed(FactorRecencyArm(engine.PROFILE,'comparison'),'stream',multi_policy=POLICY)
        refs=[Reference('RESET'),ArchiveReference('RESET')]
        event(event='unit_arm_start',test=self.id(),policy=1,live_reference=1,archive_state_reference=1,frames_limit=20)
        try:
            values=[engine.vector(x) for _ in range(5) for x in (.5,.5,.5,.5)]
            for i,v in enumerate(values,1):
                s=PerceptionSample(v,engine.PROFILE,'comparison','stream',i,(i-1)*4800,i*4800)
                if a.pending_prediction:
                    a.consume_feedback(s)
                    for ref in refs:ref.feedback(i,v)
                    self.assertEqual(cellmap(a),refs[0].cells)
                    if i==13:self.assertTrue(cellmap(a))
                    if i==13 and seed:self.assertTrue(all(v==(0.,0.) for v in cellmap(a).values()))
                if i==12 and seed:
                    for slot in range(6):
                        g,ec,ep,role,off,q,valid=CELL.unpack_from(a.bank,slot*32)
                        if valid:
                            CELL.pack_into(a.bank,slot*32,g,.75,.25,role,off,q,valid)
                            for ref in refs:ref.cells[(role,g,off)]=(.75,.25)
                a.accept_perception(s)
                for ref in refs:ref.perceive(i,v)
                self.assertEqual(cellmap(a),refs[0].cells);self.assertEqual(refs[0].cells,refs[1].cells)
                self.assertEqual(snapshot(a.arm),refs[0].stock.snapshot())
                if duplicate and i==12:
                    with self.assertRaises(ValueError):a.accept_perception(s)
                    self.assertTrue(a.closed);return
            self.assertEqual([i for i,_ in captures],[12,16,20]);self.assertEqual(reset_count,3)
            self.assertEqual(refs[0].resets,refs[1].resets)
        finally:
            if not a.closed:a._terminate()
            event(event='unit_arm_end',test=self.id(),accepted=a.accepted,cleanup=a.closed and not any(a.bank))
            for ref in refs:
                ref.cells.clear();ref.pending=None;ref.pair.clear();ref.closed=True

    def test_02_frozen_relearning_repeated_events(self):self.history()
    def test_03_partial_publication_fails_closed(self):
        with self.assertRaisesRegex(MemoryError,'INJECTED_PARTIAL'):self.history(fault='partial')
    def test_04_duplicate_input_rejected(self):self.history(duplicate=True)
    def test_05_source_recipe_and_scope(self):
        event(event='neutral_source_unit',pairs=2,blocks=24,reconstructions=2)
        for p in (1,2):
            a=sources.generate(p,24);b=sources.reconstruct(p,24);self.assertEqual(a,b)
            for c in ('A','B'):sources.verify_material(sources.materialize(a,c),b,c)
        for fn in (sources.generate,sources.reconstruct):
            with self.assertRaises(PermissionError):fn(1,neutral=False)
        d=sources.Draws(1,'cue',lambda _:b'\xff'*32)
        with self.assertRaisesRegex(ValueError,'DRAW_LIMIT'):d.below(24)
    def test_06_mixture_not_interaction(self):
        r=fixture();m=bytes([0,1]*4);a=statistics.primary(r,m);b=statistics.reference(r,m)
        self.assertEqual(a['mean'],'-1/4');self.assertEqual(a['verdict'],'NUTZEN_GESTUETZT')
        for k in ('mean','pairs','ci'):self.assertEqual(a[k],b[k])
        for row in r:
            row['conditions']['B']['KEEP']=[.75]*3
        self.assertEqual(statistics.primary(r,m)['mean'],'0')
    def test_07_equal_and_last_reset_information(self):
        r=fixture();m=bytes([0,1]*4)
        for row in r:
            for c in row['conditions'].values():c['RESET']=c['KEEP'][:]
        self.assertEqual(statistics.primary(r,m)['verdict'],'INCONCLUSIVE')
        for row in r:
            for c in row['conditions'].values():c['resets']=[dict(end=8,deleted=1)]
        self.assertEqual(statistics.primary(r,m)['verdict'],'NICHT_INFORMATIV')
    def test_08_incomplete_and_bad_matrix(self):
        r=fixture();m=bytes([0,1]*4)
        with self.assertRaisesRegex(ValueError,'PAIR_INCOMPLETE'):pair_receipt(1,{'A':r[0]['conditions']['A']})
        r[0]['conditions']['B']['KEEP'].pop()
        for f in (statistics.primary,statistics.reference):
            with self.assertRaises(ValueError):f(r,m)
            with self.assertRaises(ValueError):f(fixture(),bytes([1,0]*4))
    def test_09_full_denominator_synthetic_only(self):
        r=fixture(16,511);m=bytes(list(range(0,16,2))+list(range(1,16,2)))*4
        a=statistics.primary(r,m);b=statistics.reference(r,m)
        self.assertEqual(a['arm_errors'],32704)
        for k in ('mean','pairs','ci'):self.assertEqual(a[k],b[k])
    def test_10_no_extra_policy_state(self):
        keep=engine.create('KEEP');reset=engine.create('RESET')
        event(event='construction_only',policy_histories=0,instances=2)
        self.assertEqual(set(vars(keep)),set(vars(reset)));keep._terminate();reset._terminate()

    def test_11_internal_stock_identity_and_eviction(self):
        from contextlib import ExitStack
        traces=[];actions=[]
        for mode in ('KEEP','RESET'):
            a=engine.create(mode);trace=[];seen=[]
            event(event='unit_arm_start',test=self.id(),mode=mode,policy=1,frames_limit=40,live_reference=0,archive_state_reference=0)
            def capture(name):
                state=engine.common(a);state.pop('bank');trace.append((name,state))
            with ExitStack() as stack:
                for name in ('form','close_segment'):
                    original=getattr(FactorRecencyArm,name)
                    def wrapped(obj,*args,_name=name,_original=original,**kw):
                        capture(_name+':before');r=_original(obj,*args,**kw);capture(_name+':after')
                        if _name=='close_segment':seen.append(r)
                        return r
                    stack.enter_context(patch.object(FactorRecencyArm,name,wrapped))
                try:
                    values=[engine.vector(x) for x in (.5,.5,.5,.25,.25,.75,.75,.5,.5,.5) for _ in range(4)]
                    for i,v in enumerate(values,1):
                        s=PerceptionSample(v,engine.PROFILE,'comparison','stream',i,(i-1)*4800,i*4800)
                        if a.pending_prediction:
                            capture('feedback:before');a.consume_feedback(s);capture('feedback:after')
                        capture('admit:before');a.accept_perception(s);capture('admit:after')
                    self.assertTrue(any(x.get('evicted') is not None for x in seen));traces.append(trace);actions.append(seen)
                finally:
                    a._terminate();event(event='unit_arm_end',test=self.id(),accepted=a.accepted,cleanup=a.closed and not any(a.bank))
        self.assertEqual(traces[0],traces[1]);self.assertEqual(actions[0],actions[1])

    def test_12_wrong_event_generation_fail_closed(self):
        a=engine.create('RESET');original=FactorRecencyArm.close_segment
        event(event='unit_arm_start',test=self.id(),policy=1,frames_limit=12,live_reference=0,archive_state_reference=0)
        def wrong(obj,*args,**kwargs):
            r=original(obj,*args,**kwargs)
            return r|dict(generation=999) if r['action']=='TRACE_CONFIRMED_RECENT' else r
        try:
            with patch.object(FactorRecencyArm,'close_segment',wrong),self.assertRaisesRegex(ValueError,'RESET_TRANSITION'):
                for i in range(1,13):
                    s=PerceptionSample(engine.vector(.5),engine.PROFILE,'comparison','stream',i,(i-1)*4800,i*4800)
                    if a.pending_prediction:a.consume_feedback(s)
                    a.accept_perception(s)
            self.assertTrue(a.closed);self.assertFalse(any(a.bank))
        finally:
            if not a.closed:a._terminate()
            event(event='unit_arm_end',test=self.id(),accepted=a.accepted,cleanup=a.closed and not any(a.bank))

    def test_16_variable_resampling_and_decisions(self):
        r=fixture(16,511)
        for i,row in enumerate(r):
            for c in row['conditions'].values():c['KEEP']=[float(i)/32]*511
        m=bytes(list(range(0,16,2))+list(range(1,16,2))+[0]*8+[1]*8+[14]*8+[15]*8)
        a=statistics.primary(r,m);b=statistics.reference(r,m)
        for k in ('mean','pairs','ci','informative','verdict'):self.assertEqual(a[k],b[k])
        self.assertNotEqual(a['ci'][0],a['ci'][1])
        for ci,expected in [(['-1','0'],'INCONCLUSIVE'),(['0','1'],'INCONCLUSIVE'),(['1/10','1'],'SCHADEN_GESTUETZT')]:self.assertEqual(statistics.decision(ci,True),expected)
        for row in r:
            for c in row['conditions'].values():c['resets']=[]
        self.assertEqual(statistics.primary(r,m)['verdict'],'NICHT_INFORMATIV');self.assertEqual(statistics.reference(r,m)['verdict'],'NICHT_INFORMATIV')
        for fn in (statistics.primary,statistics.reference):
            with self.assertRaises(ValueError):fn(r,m,neutral=False)

    def test_17_nonqualifying_events_and_prewrite_validation(self):
        for action in ('TRACE_CONFIRMED','CANDIDATE_CREATED','NO_CHANGE'):
            a=object.__new__(ResetAdapter);a.closed=False;a.bank=bytearray(416);a.admitted=11;a.first_ordinal=1;a.revision=0
            a.arm=NS(_retained_many=[NS(generation=7)],_candidate=None,_observation_end={7:8},form=lambda f:None,close_segment=lambda s:dict(action=action,generation=7))
            CELL.pack_into(a.bank,0,7,.75,.25,0,0,0,1);before=bytes(a.bank)
            a._admit(NS(ordinal=12,segment='test'));self.assertEqual(bytes(a.bank),before)
            a.bank[408]=ADMITTING;a.arm._observation_end[7]=12
            CELL.pack_into(a.bank,32,7,.75,.25,0,0,0,1);before=bytes(a.bank)
            with self.assertRaisesRegex(ValueError,'DUPLICATE_CELL'):a._invalidate_confirmed(7)
            self.assertEqual(bytes(a.bank),before)

    def test_18_old_errors_not_restored(self):self.history(seed=True)

if __name__=='__main__':unittest.main()
