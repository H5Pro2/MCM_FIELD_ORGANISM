"""Serial fresh paired arms; observer-only evidence, gated reads and scalar audit."""
import dataclasses,math
from .common import *
from . import material,oracle
from tools._s2uc_signal_approx_adapter import SignalApproxAdapter
from tools._s2uc_factor_recency import FactorRecencyArm
from tools._s2uc_pair_context_adapter import PairContextAdapter
from tools._s2uc_origin_judge import GatedReplay
from tools._s2uc_continuation_adapter import consume_prediction
from tools._s2uc_signal_approx_compare import ApproxBudgetObserver
from tools.s2uc_continuous_comparison import state
from tools import _s2nj_private_auditory_output_projection as nj

def stock(arm):
    traces=[('retained',t.generation,t.frames) for t in arm._retained_many]
    if arm._candidate is not None:traces.append(('candidate',arm._candidate.candidate_generation,arm._candidate.frames))
    return [dict(role=role,generation=g,formation=fs[0].segment,ordinals=[f.ordinal for f in fs],values=[list(f.values) for f in fs]) for role,g,fs in traces]
def frozen(adapter,i):
    p=adapter.pending_prediction
    need(p is not None and p.target_index==i and read_receipt(p)['input_indices']==[i-2,i-1],'TARGET_GATE')
def read_receipt(p):return json.loads(p.provenance_json)
class FileStream:
    def __init__(self,folder,case,manifest):self.folder=Path(folder)/'material';self.case=case;self.manifest=manifest;self.i=0;self.log=[]
    def __iter__(self):return self
    def __next__(self):
        self.i+=1
        if self.i>11:raise StopIteration
        name=f'{self.case}-{self.i:02}.json';p=self.folder/name
        need(info(p)==self.manifest['files'][name],'FRAME_HASH')
        self.log.append(self.i);return tuple(read(p)['projection']['values'])
    def close(self):pass

def run_arm(folder,case,mode,manifest,ledger):
    kwargs={} if mode=='exact_v1' else dict(epsilon=EPS,tau=TAU)
    ledger.bump('arms_started');a=SignalApproxAdapter(FactorRecencyArm(nj.PROFILE_DIGEST,'owner'),'stream',retrieval_policy=mode,**kwargs)
    ledger.bump('reference_started');ref=PairContextAdapter(FactorRecencyArm(nj.PROFILE_DIGEST,'owner'),'stream')
    feed=FileStream(folder,case,manifest);source=GatedReplay(iter(feed),nj.PROFILE_DIGEST)
    meter=ApproxBudgetObserver();records=[];boundaries=[];pending=None;completed=False
    def observed(fn,*args):
        sys.settrace(meter.trace)
        try:return fn(*args)
        finally:sys.settrace(None)
    try:
        for i in range(1,12):
            if i>=3 and i%2:frozen(a,i)
            sample=source.take(a)
            if a.pending_prediction:
                forecast=dataclasses.asdict(a.pending_prediction)
                rec=dict(pending,forecast=forecast,receipt=read_receipt(a.pending_prediction),actual=list(sample.values),target=i,mode=mode)
                output=forecast['context_values'] if forecast['context_values'] is not None else forecast['persistence_values']
                rec['error']=math.fsum(abs(x-y) for x,y in zip(output,sample.values))/48
                rec['p_error']=math.fsum(abs(x-y) for x,y in zip(forecast['persistence_values'],sample.values))/48
                observed(consume_prediction,a,sample);records.append(json.loads(raw(rec)))
            if i%2==0:
                pending=dict(stock=stock(a.arm),hint=[list(a.pair[0].values),list(sample.values)])
                if i==10:need(len(pending['stock'])==1 and pending['stock'][0]['ordinals']==[1,2,3,4] and not a.arm._candidate,'QUERY_STOCK')
            ledger.bump('policy_admissions');observed(a.accept_perception,sample)
            ledger.bump('reference_admissions');ref.accept_perception(sample)
            need(state(a.arm)==state(ref.arm),'STATE_REFERENCE')
            boundaries.append(state(a.arm))
            if i==4:need(not a.arm._retained_many and a.arm._candidate is not None and [f.ordinal for f in a.arm._candidate.frames]==[1,2,3,4],'CANDIDATE_PREFIX')
            if i==8:need(a.arm.inventory==(1,) and a.arm._candidate is None and not a.arm._forming and [f.ordinal for f in a.arm._retained_many[0].frames]==[1,2,3,4],'PROMOTION_PREFIX')
        observed(a.finish_story);ref.finish_story()
        need(state(a.arm)==state(ref.arm) and a.pending_prediction is None,'FINAL_REFERENCE')
        need(feed.log==list(range(1,12)) and [r['target'] for r in records]==[3,5,7,9,11],'COUNTS')
        ledger.bump('arms_completed');ledger.bump('reference_completed');completed=True
        return dict(records=records,states=boundaries,pull_log=source.log,resources=vars(meter),complete=True,cleanup=True)
    finally:
        source.close()
        if not a.closed:a._terminate()
        if not ref.closed:ref._terminate()
        ledger.bump('arms_closed');ledger.bump('reference_closed')
        ledger.event('ARM_EXIT',case=case,mode=mode,complete=completed,slots_released=a.pending_prediction is None)

def compare(folder,mode,ledger):
    manifest=material.verify(folder,mode);budget=Budget(folder);results={};main={};peaks={}
    for case in CASES:
        results[case]={}
        for name,policy in (('E','exact_v1'),('N','signal_approx_v1')):
            value=run_arm(folder,case,policy,manifest,ledger)
            for record in value['records']:
                ledger.bump('decisions_started');oracle.check(record,EPS,TAU);ledger.bump('decisions_completed')
            for k,v in value['resources'].items():
                if isinstance(v,(int,float)):peaks[k]=max(peaks.get(k,0),v)
            budget.save(f'{case}-{name}.json',value);results[case][name]=value
        need(results[case]['E']['states']==results[case]['N']['states'],'PAIRED_STOCK')
        main[case]={}
        for name in ('E','N'):
            rec=results[case][name]['records'][-1];main[case][name]=dict(oracle.assignment(rec),error=rec['error'])
        main[case]['P']=dict(error=rec['p_error'])
        main[case]['N-E']=main[case]['N']['error']-main[case]['E']['error']
        main[case]['N-P']=main[case]['N']['error']-main[case]['P']['error']
    collisions=[]
    for ac in ('A0','A480'):
        for bc in ('B0','B480'):
            a=results[ac]['E']['records'][-1];b=results[bc]['E']['records'][-1]
            if a['hint']==b['hint'] and a['stock']==b['stock'] and a['actual']!=b['actual']:collisions.append([ac,bc])
    assessment=oracle.verdict(main,bool(collisions))
    if mode=='neutral':assessment=dict(neutral_only=True,diagnostic_criteria=assessment,scientific_verdict=None)
    budget.save('assessment.json',dict(cases=main,assessment=assessment,collisions=collisions,peaks=peaks,targets_per_arm=[3,5,7,9,11]))
    expected=dict(sources=2,receptor_started=44,receptor_completed=44,nj_started=44,nj_completed=44,
        arms_started=8,arms_completed=8,arms_closed=8,reference_started=8,reference_completed=8,reference_closed=8,
        policy_admissions=88,reference_admissions=88,decisions_started=40,decisions_completed=40)
    need(ledger.counts==expected,'EXECUTION_BALANCE')
    material.verify(folder,mode)
    return dict(counts=expected,peaks=peaks,cleanup=True,material_unchanged=True)
