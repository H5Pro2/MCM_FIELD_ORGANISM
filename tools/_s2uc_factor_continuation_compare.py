"""Observer only: fixed-target three-arm comparisons, no material generation."""
import math
from tools._s2uc_origin_judge import replay,judge,aggregate
from tools.s2uc_deviation_observer import measures
from tools.s2uc_context_prediction_check import BudgetObserver

class ScalingBudgetObserver(BudgetObserver):
    """Count the C tuple builder as one live vector from its first yield.

    No value archive is kept. Generator yield count bounds its pending storage.
    Existing frame/receipt accounting remains active in the parent tracer.
    """
    def __init__(self):
        super().__init__()
        self.scaling_calls=0;self.builder_components=0;self.builder_peak_components=0
        self.transient_output_slots_peak=0;self.temporary_vector_lists=0
    def trace(self,frame,event,arg):
        super().trace(frame,event,arg)
        name=frame.f_code.co_name
        if frame.f_code.co_filename.endswith('_s2uc_continuation_adapter.py'):
            if name=='_scaled_continuation' and event=='call':
                self.scaling_calls+=1;self.builder_components=0
            if name=='<genexpr>' and event=='return' and type(arg) is float:
                self.builder_components+=1
                assert self.builder_components<=48
                self.builder_peak_components=max(self.builder_peak_components,self.builder_components)
                # One builder plus the existing persistence tuple, never a third output.
                self.transient_output_slots_peak=max(self.transient_output_slots_peak,2)
            if name=='_scaled_continuation':
                for v in frame.f_locals.values():
                    if isinstance(v,list) and len(v)==48:
                        self.temporary_vector_lists+=1;raise AssertionError('TEMPORARY_VECTOR_LIST')
                if event=='return':self.builder_components=0
        return self.trace

def compare(values,profile,truth,*,measure_resources=False):
    """Same finite input and final target for each policy; labels after replay."""
    count=len(values)
    if count%2!=1:raise ValueError('FIXED_ODD_TARGET_REQUIRED')
    systems={}
    for key,policy in [('legacy','legacy_v1'),('scaled','factor_scaled_v1')]:
        systems[key]=replay(iter(values),profile,count,policy=policy,
            resource_meter=ScalingBudgetObserver() if measure_resources else None)
    a,b=systems['legacy'],systems['scaled']
    assert a['states']==b['states'] and a['final_state']==b['final_state']
    assert a['receipts']==b['receipts'] and a['admitted']==b['admitted']
    rows={k:judge(v['targets'][-1],truth) for k,v in systems.items()}
    assert rows['legacy']['origin_category']==rows['scaled']['origin_category']
    assert rows['legacy']['persistence_mae']==rows['scaled']['persistence_mae']
    learning_rows={}
    for key,system in systems.items():
        learning_rows[key]=[]
        for t in system['targets'][:-1]:
            f=t['forecast'];p=measures(f['persistence_values'],t['actual'])['mae']
            c=None if f['context_values'] is None else measures(f['context_values'],t['actual'])['mae']
            learning_rows[key].append(dict(target=t['target'],status=f['status'],persistence_mae=p,
                context_mae=c,observer_hybrid_mae=p if c is None else c,delta=0. if c is None else p-c))
    return dict(systems=systems,rows=rows,target=count,
                learning_rows=learning_rows,
                learning_targets=[t['target'] for t in a['targets'][:-1]])

def summarize(cases):
    def mean(xs):return math.fsum(xs)/len(xs) if xs else None
    tables={}
    for key in ('legacy','scaled'):
        rows=[dict(case_id=cid,**{k:v for k,v in c['rows'][key].items() if k!='case_id'}) for cid,c in cases.items()]
        tables[key]=dict(origin_and_prediction=aggregate(rows),total=len(rows),context_covered=sum(r['context_covered'] for r in rows),
            assignment_covered=sum(r['assignment_covered'] for r in rows),rows=rows)
    pairs={}
    for left,right in [('scaled','legacy'),('scaled','persistence'),('legacy','persistence')]:
        rows=[]
        for cid,c in cases.items():
            x=c['rows'][left]['context_mae'];y=c['rows']['legacy']['persistence_mae'] if right=='persistence' else c['rows'][right]['context_mae']
            if x is not None and y is not None:rows.append(dict(case_id=cid,target=c['target'],left=x,right=y,delta=y-x))
        pairs[left+'_vs_'+right]=dict(rows=rows,count=len(rows),left_mae=mean([x['left'] for x in rows]),right_mae=mean([x['right'] for x in rows]),delta=mean([x['delta'] for x in rows]),better=sum(x['delta']>0 for x in rows),equal=sum(x['delta']==0 for x in rows),worse=sum(x['delta']<0 for x in rows),harms=[x for x in rows if x['delta']<0])
    full=[]
    for cid,c in cases.items():
        l=c['rows']['legacy'];n=c['rows']['scaled'];p=l['persistence_mae']
        full.append(dict(case_id=cid,target=c['target'],persistence=p,legacy=l['observer_hybrid_mae'],scaled=n['observer_hybrid_mae'],
            scaled_vs_persistence=p-n['observer_hybrid_mae'],scaled_vs_legacy=l['observer_hybrid_mae']-n['observer_hybrid_mae']))
    return dict(policies=tables,paired=pairs,full_rows=full,full_means={k:mean([r[k] for r in full]) for k in ('persistence','legacy','scaled','scaled_vs_persistence','scaled_vs_legacy')},
        harms_against_persistence=[r for r in full if r['scaled_vs_persistence']<0],
        harms_against_legacy=[r for r in full if r['scaled_vs_legacy']<0],
        learning_targets={cid:c['learning_targets'] for cid,c in cases.items()})
