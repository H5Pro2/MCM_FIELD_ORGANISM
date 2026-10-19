"""Technical replay and separate judge. No labels enter replay or memory."""
import dataclasses,json,math,sys
from collections import Counter
from tools._s2uc_continuation_adapter import ContinuationAdapter,consume_prediction
from tools._s2uc_pair_context_adapter import PairContextAdapter,PerceptionSample,AdapterError
from tools._s2uc_factor_recency import FactorRecencyArm
from tools.s2uc_continuous_comparison import state
from tools.s2uc_deviation_observer import measures

def need(ok,code):
    if not ok:raise ValueError(code)

class GatedReplay:
    def __init__(self,values,profile):
        self._iterator=iter(values);self.profile=profile;self.pulls=0;self.closed=False;self.log=[]
    def take(self,a):
        try:
            need(not self.closed and not a.closed,'SOURCE_CLOSED');i=self.pulls+1
            need(a.next_index==i,'PULL_ORDER')
            if i>=3 and i%2:
                p=a.pending_prediction
                need(p is not None and p.target_index==i,'FUTURE_BEFORE_FORECAST')
                need(json.loads(p.provenance_json)['input_indices']==[i-2,i-1],'FORECAST_PAIR')
            # Gate precedes iterator advance, including lazy suppliers.
            values=next(self._iterator)
            self.pulls=i;self.log.append(dict(index=i,forecast_bound=i>=3 and i%2==1))
            return PerceptionSample(tuple(values),self.profile,'owner','stream',i,(i-1)*4800,i*4800)
        except StopIteration:raise
        except BaseException:self.close();a._terminate();raise
    def close(self):
        self.closed=True
        close=getattr(self._iterator,'close',None)
        if close:close()
        self._iterator=iter(())

def replay(values,profile,count,*,measure_resources=False,policy='legacy_v1',resource_meter=None):
    """No case ID, label, target class or expected continuation argument."""
    need(type(count) is int and 3<=count<=64,'REPLAY_BOUND')
    a=ContinuationAdapter(FactorRecencyArm(profile,'owner'),'stream',policy=policy)
    b=PairContextAdapter(FactorRecencyArm(profile,'owner'),'stream')
    source=GatedReplay(values,profile);targets=[];receipts=[];states=[];admitted=[]
    from tools.s2uc_context_prediction_check import BudgetObserver
    meter=resource_meter if resource_meter is not None else BudgetObserver() if measure_resources else None
    def observed(fn,*args):
        if meter:sys.settrace(meter.trace)
        try:return fn(*args)
        finally:
            if meter:sys.settrace(None)
    original=a._admit
    def admit(f):
        if len(a.pair)==2:need(a.pending_prediction is not None,'FORECAST_BEFORE_ADMISSION')
        admitted.append(f.ordinal);original(f)
    a._admit=admit
    try:
        for _ in range(count):
            s=source.take(a)
            if a.pending_prediction is not None:
                frozen=dataclasses.asdict(a.pending_prediction)
                score=observed(consume_prediction,a,s)
                need(a.pending_prediction is None,'SLOTS_NOT_RELEASED')
                targets.append(dict(target=s.index,forecast=frozen,actual=s.values,exact_score=score))
            r=observed(a.accept_perception,s);rr=b.accept_perception(s)
            need(r==rr and state(a.arm)==state(b.arm),'STATE_MISMATCH')
            if r:receipts.append(json.loads(r.json_text))
            states.append(state(a.arm))
        terminal=None
        if a.pending_prediction is not None:terminal=dict(target=a.pending_prediction.target_index,status='NOT_EVALUABLE_END')
        observed(a.finish_story);b.finish_story()
        need(a.pending_prediction is None and state(a.arm)==state(b.arm),'FINAL_MISMATCH')
        need(admitted==list(range(1,count+1)) and a.admitted==count,'ADMISSION_ONCE')
        return dict(targets=targets,receipts=receipts,states=states,final_state=state(a.arm),admitted=admitted,pull_log=source.log,terminal=terminal,slots_released=True,resources=vars(meter) if meter else None)
    finally:
        source.close()
        if not a.closed:a._terminate()
        if not b.closed:b._terminate()

@dataclasses.dataclass(frozen=True)
class Truth:
    root:str
    positive:bool
    # Tuple of source ordinals -> genealogical base episode. Judge only.
    roots_by_ordinals:dict
    case_id:str='' 

def judge(target_record,truth):
    need(type(truth) is Truth,'TRUTH_REQUIRED')
    f=target_record['forecast'];p=json.loads(f['provenance_json']);matches=p['matches']
    role=None;assigned=None
    if not matches:category='ABSTAIN'
    elif len(matches)>1:category='AMBIGUOUS'
    else:
        m=matches[0];key=tuple(m['ordinals']);need(key in truth.roots_by_ordinals,'UNBOUND_ORIGIN')
        assigned=truth.roots_by_ordinals[key];role=m['role'];category='CORRECT' if assigned==truth.root else 'WRONG'
    y=target_record['actual'];base=measures(f['persistence_values'],y)['mae'];ctx=f['context_values']
    context=None if ctx is None else measures(ctx,y)['mae']
    hybrid=base if context is None else context
    return dict(case_id=truth.case_id,target=target_record['target'],positive=truth.positive,origin_category=category,assigned_root=assigned,true_root=truth.root,role=role,
        assignment_covered=category in ('CORRECT','WRONG'),correct_rejection=not truth.positive and category=='ABSTAIN',prediction_status=f['status'],
        context_covered=context is not None,persistence_mae=base,context_mae=context,
        paired_delta=None if context is None else base-context,observer_hybrid_mae=hybrid,full_delta=base-hybrid)

def aggregate(rows):
    need(len(rows)>0,'EMPTY_REPORT')
    mean=lambda xs:math.fsum(xs)/len(xs) if xs else None
    covered=[r for r in rows if r['context_covered']]
    counts=lambda rs:dict(Counter(r['origin_category'] for r in rs))
    positives=[r for r in rows if r['positive']];negatives=[r for r in rows if not r['positive']]
    return dict(total=len(rows),origin_counts=counts(rows),positive_origin_counts=counts(positives),negative_origin_counts=counts(negatives),
        assignment_coverage=sum(r['assignment_covered'] for r in rows)/len(rows),context_coverage=len(covered)/len(rows),
        positive_correct_fraction=mean([float(r['origin_category']=='CORRECT') for r in positives]),negative_wrong_fraction=mean([float(r['origin_category']=='WRONG') for r in negatives]),
        correct_rejections=sum(r['correct_rejection'] for r in rows),roles=dict(Counter(r['role'] for r in rows if r['role'])),
        prediction_abstentions=dict(Counter(r['prediction_status'] for r in rows if not r['context_covered'])),
        paired=dict(count=len(covered),persistence_mae=mean([r['persistence_mae'] for r in covered]),context_mae=mean([r['context_mae'] for r in covered]),delta=mean([r['paired_delta'] for r in covered]),better=sum(r['paired_delta']>0 for r in covered),equal=sum(r['paired_delta']==0 for r in covered),worse=sum(r['paired_delta']<0 for r in covered)),
        full_coverage=dict(count=len(rows),persistence_mae=mean([r['persistence_mae'] for r in rows]),observer_hybrid_mae=mean([r['observer_hybrid_mae'] for r in rows]),delta=mean([r['full_delta'] for r in rows])),
        harm_rows=[r for r in rows if r['full_delta']<0])


def evaluate_case(values,profile,count,target,truth,*,measure_resources=False):
    """Judge wrapper; labels are used only after the completed technical replay."""
    need(target==count and target%2==1,'FIXED_TEST_TARGET_REQUIRED')
    technical=replay(values,profile,count,measure_resources=measure_resources)
    selected=[r for r in technical['targets'] if r['target']==target]
    need(len(selected)==1,'TEST_TARGET_MISSING')
    return dict(system=technical,evaluation=judge(selected[0],truth),learning_targets=[r['target'] for r in technical['targets'] if r['target']!=target])
