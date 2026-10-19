"""Neutral observer for signal-gated approximate retrieval; no parameter search."""
import dataclasses,json,sys
from pathlib import Path
from tools._s2uc_signal_approx_adapter import SignalApproxAdapter
from tools._s2uc_continuation_adapter import consume_prediction
from tools._s2uc_factor_recency import FactorRecencyArm
from tools._s2uc_pair_context_adapter import PairContextAdapter,PerceptionSample
from tools._s2uc_origin_judge import GatedReplay,judge
from tools.s2uc_continuous_comparison import state
from tools.s2uc_context_prediction_check import BudgetObserver
from tools._s2uc_factor_continuation_compare import summarize

class ApproxBudgetObserver(BudgetObserver):
    def __init__(self):
        super().__init__();self.receipt_bytes_peak=0;self.scalar_pair_comparisons=0
        self.temporary_numeric_vectors_peak=0;self.match_metadata_peak=0
        self.receipt_transient_utf8_bytes_peak=0;self.receipt_python_bytes_peak=0
    def trace(self,frame,event,arg):
        super().trace(frame,event,arg)
        if Path(frame.f_code.co_filename).name=='_s2uc_signal_approx_adapter.py':
            if frame.f_code.co_name=='relative_l1' and event=='call':self.scalar_pair_comparisons+=1
            if frame.f_code.co_name in ('amplitude','relative_l1','_select','_receipt'):
                # All allowed 48-vectors here are borrowed from Frame objects.
                cursor=frame;adapter=None
                while cursor:
                    if isinstance(cursor.f_locals.get('self'),SignalApproxAdapter):adapter=cursor.f_locals['self'];break
                    cursor=cursor.f_back
                if adapter:
                    frames=list(adapter.pair)+list(adapter.arm._forming)+list(adapter.arm._hints)
                    for _,_,fs in adapter._sources():frames.extend(fs)
                    borrowed={id(f.values) for f in frames}
                    for name,v in frame.f_locals.items():
                        if isinstance(v,(list,tuple)) and len(v)==48 and all(type(x) is float for x in v) and id(v) not in borrowed:
                            self.temporary_numeric_vectors_peak=max(self.temporary_numeric_vectors_peak,1)
                            raise AssertionError('UNBUDGETED_DISTANCE_VECTOR:'+name)
                    count=len({id(f) for f in frames});self.frame_peak=max(self.frame_peak,count)
                    assert count<=18
                    if adapter.pending_prediction:
                        slots=1+(adapter.pending_prediction.context_values is not None)
                        self.combined_peak=max(self.combined_peak,count+slots);assert count+slots<=20
                if 'raw' in frame.f_locals:
                    size=len(frame.f_locals['raw'].encode());self.receipt_bytes_peak=max(self.receipt_bytes_peak,size);assert size<=16384
                strings={}
                for value in frame.f_locals.values():
                    if isinstance(value,str) and value.startswith('{') and 'input_indices' in value:strings[id(value)]=value
                    raw=getattr(value,'json_text',None)
                    if raw is not None:strings[id(raw)]=raw
                if adapter and adapter.pending_prediction:
                    raw=adapter.pending_prediction.provenance_json;strings[id(raw)]=raw
                total=sum(len(x.encode()) for x in strings.values())
                self.receipt_transient_utf8_bytes_peak=max(self.receipt_transient_utf8_bytes_peak,total)
                self.receipt_python_bytes_peak=max(self.receipt_python_bytes_peak,sum(sys.getsizeof(x) for x in strings.values()))
                assert total<=32768
                ms=frame.f_locals.get('matches',[])
                self.match_metadata_peak=max(self.match_metadata_peak,len(ms));assert len(ms)<=9
        return self.trace

def replay(values,profile,*,retrieval_policy='exact_v1',epsilon=None,tau=None,measure=False):
    count=len(values)
    if not 3<=count<=64 or count%2!=1:raise ValueError('REPLAY_BOUND')
    a=SignalApproxAdapter(FactorRecencyArm(profile,'owner'),'stream',retrieval_policy=retrieval_policy,epsilon=epsilon,tau=tau)
    reference=PairContextAdapter(FactorRecencyArm(profile,'owner'),'stream')
    source=GatedReplay(iter(values),profile);meter=ApproxBudgetObserver() if measure else None
    targets=[];receipts=[];states=[];admitted=[]
    def observed(fn,*args):
        if meter:sys.settrace(meter.trace)
        try:return fn(*args)
        finally:
            if meter:sys.settrace(None)
    original=a._admit
    def admit(f):
        if len(a.pair)==2:assert a.pending_prediction is not None
        admitted.append(f.ordinal);original(f)
    a._admit=admit
    try:
        for _ in range(count):
            sample=source.take(a)
            if a.pending_prediction:
                frozen=dataclasses.asdict(a.pending_prediction)
                score=observed(consume_prediction,a,sample)
                targets.append(dict(target=sample.index,forecast=frozen,actual=sample.values,exact_score=score))
                assert a.pending_prediction is None
            rec=observed(a.accept_perception,sample);reference.accept_perception(sample)
            assert state(a.arm)==state(reference.arm)
            if rec:receipts.append(json.loads(rec.json_text))
            states.append(state(a.arm))
        observed(a.finish_story);reference.finish_story()
        assert a.pending_prediction is None and state(a.arm)==state(reference.arm)
        assert admitted==list(range(1,count+1))
        return dict(targets=targets,receipts=receipts,states=states,final_state=state(a.arm),
            admitted=admitted,pull_log=source.log,slots_released=True,resources=vars(meter) if meter else None)
    finally:
        source.close()
        if not a.closed:a._terminate()
        if not reference.closed:reference._terminate()

def compare(values,profile,truth,*,epsilon,tau,measure=False):
    systems=dict(exact=replay(values,profile,measure=measure),approx=replay(values,profile,
        retrieval_policy='signal_approx_v1',epsilon=epsilon,tau=tau,measure=measure))
    a,b=systems['exact'],systems['approx']
    assert a['states']==b['states'] and a['final_state']==b['final_state'] and a['admitted']==b['admitted']
    rows={k:judge(s['targets'][-1],truth) for k,s in systems.items()}
    prov=json.loads(b['targets'][-1]['forecast']['provenance_json'])
    return dict(systems=systems,rows=rows,target=len(values),learning_targets=[x['target'] for x in a['targets'][:-1]],
        additional_wrong=rows['approx']['origin_category']=='WRONG' and rows['exact']['origin_category']!='WRONG',
        lost_exact_assignment=rows['exact']['assignment_covered'] and not rows['approx']['assignment_covered'],
        signal_lost_exact_assignment=prov['retrieval']['signal_lost_exact_single'],
        lost_correct_exact=rows['exact']['origin_category']=='CORRECT' and rows['approx']['origin_category']!='CORRECT',
        match_quality=[m['match_quality'] for m in prov['matches']])

def report(cases):
    # Reuse the existing fixed-mask/MAE observer without relabeling product policies.
    mapped={cid:dict(rows=dict(legacy=c['rows']['exact'],scaled=c['rows']['approx']),target=c['target'],learning_targets=c['learning_targets']) for cid,c in cases.items()}
    return dict(comparison=summarize(mapped),schema_mapping={'legacy':'exact retrieval with legacy_v1 continuation','scaled':'signal_approx retrieval with legacy_v1 continuation; NO factor_scaled_v1'},
        additional_wrong=[cid for cid,c in cases.items() if c['additional_wrong']],
        lost_exact_assignments=[cid for cid,c in cases.items() if c['lost_exact_assignment']],
        signal_lost_exact_assignments=[cid for cid,c in cases.items() if c['signal_lost_exact_assignment']],
        lost_correct_exact=[cid for cid,c in cases.items() if c['lost_correct_exact']],
        admissible_no_new_wrong=not any(c['additional_wrong'] for c in cases.values()))
