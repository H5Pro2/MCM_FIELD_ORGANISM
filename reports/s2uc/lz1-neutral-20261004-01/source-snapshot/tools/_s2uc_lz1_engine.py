"""Observer wrapper around unchanged U replay and past-only P/H64 baselines."""
import sys
import tracemalloc
from collections import Counter
from tools._s2uc_a1_compare_engine import replay as u_replay
from tools._s2uc_k1_probe import error
from tools._s2uc_lz1_h64 import H64
from tools._s2uc_lz1_reference import H64Reference
from tools import _s2uc_lz1_sources as source

def need(ok,reason):
    if not ok:raise ValueError(reason)

def owned(h):
    seen=set()
    def size(v):
        if id(v) in seen:return 0
        seen.add(id(v));n=sys.getsizeof(v)
        if isinstance(v,(tuple,list)):n+=sum(size(x) for x in v)
        return n
    return sys.getsizeof(h)+sys.getsizeof(vars(h))+sum(size(v) for v in vars(h).values())

class HMeter:
    def __init__(self,h):self.h=h;self.peak=0
    def call(self,fn):
        retained=owned(self.h)
        tracemalloc.start();base=tracemalloc.get_traced_memory()[0]
        try:return fn()
        finally:
            peak=tracemalloc.get_traced_memory()[1]-base;tracemalloc.stop()
            self.peak=max(self.peak,retained+peak)
            need(self.peak<=128*1024,'H64_HEAP')

def compact_u(u):
    def hyp(h):return None if h is None else {k:v for k,v in h.items() if k not in ('prior_feedback','promotion_lineage')}
    return dict(rows=[r|dict(hypotheses=[hyp(h) for h in r['hypotheses']],selected=hyp(r['selected'])) for r in u['rows']],
        forecasts=u['forecasts'],events=[{k:v for k,v in e.items() if k not in ('forecast_stock','before_cells','partial_admission')} for e in u['events'] if e['index']%2==0],
        full_confirmations=u['full_confirmations'],resources=u['resources'],cleanup=u['cleanup'],
        reference_equal=u['reference_equal'],reference_advances=u['reference_advances'],censored_target=u['censored_target'])

def replay(record,check):
    values=source.values(record)
    need(len(values)==1040,'FRAME_COUNT')
    # False is the exact legacy U factory path. No A1 or K1 policy is enabled.
    u=u_replay(values,source.digest('LZ1-schema-48-float64'),False,check)
    h=H64();ref=H64Reference();meter=HMeter(h);rows=[];pending=None
    catalog=[tuple(v) for v in record['catalog']]
    def value_id(v):
        need(tuple(v) in catalog,'OUTPUT_OUTSIDE_OBSERVED_VALUES')
        return catalog.index(tuple(v))
    try:
        for i,v in enumerate(values,1):
            check()
            if pending is not None:
                t,pred,votes=pending
                need(t==i and tuple(pred)==tuple(h.output),'H64_FROZEN')
                before=h.count
                hp=error(pred,v);pp=error(values[i-2],v)
                meter.call(lambda:h.feedback(v));ref.feedback(v)
                need(h.count==ref.count==before+1,'H64_FEEDBACK_COUNT')
                rows.append(dict(target=i,P=pp,H64=hp,H64_prediction=value_id(pred),
                    H64_votes=votes,H64_prior_count=before,
                    H64_overwritten_target=None if before<64 else 3+2*(before-64)))
                pending=None
            if i%2==0:
                pred=meter.call(lambda:h.predict(values[i-2],v))
                expected=ref.predict(values[i-2],v)
                need(pred==expected,'H64_REFERENCE')
                counts=Counter(target for first,second,target in ref.records if (first,second)==ref.pending)
                votes=sorted([[value_id(k),n] for k,n in counts.items()])
                pending=(i+1,pred,votes)
        need(pending[0]==1041 and h.count==519,'H64_CENSORING')
        need([x['target'] for x in rows]==source.masks()['G'],'TARGETS')
        for r,ur in zip(rows,u['rows'],strict=True):
            need(r['target']==ur['target'],'PAIRED_TARGETS');r['U']=ur['error']
        cumulative={'U-P':0.,'U-H64':0.}
        for row in rows:
            for other in ('P','H64'):cumulative['U-'+other]+=row['U']-row[other]
            row['cumulative_differences']=dict(cumulative)
        # Diagnose structural opportunities; these are not positive benefit verdicts.
        state16=next(e['after'] for e in u['events'] if e['index']==16)
        originals=sorted(t['ordinals'] for t in state16['retained'])
        need(originals==[[1,2,3,4],[9,10,11,12]],'PREFIX_TWO_ORIGINALS')
        ys=[r for r in u['rows'] if r['target'] in source.masks()['G_Y']]
        cycle=dict(prefix_originals=originals,targets=len(ys),
            two_live_hypotheses=sum(len(r['hypotheses'])==2 for r in ys),
            live_feedback=sum(x['live'] for r in ys for x in r['updates']),
            warm_hypotheses=sum(h['before'] is not None for r in ys for h in r['hypotheses']),
            selected=sum(r['selected'] is not None for r in ys))
        need(cycle['two_live_hypotheses']==256 and cycle['live_feedback']==512,'CYCLE_OPPORTUNITY')
        metrics={m:{arm:sum(r[arm] for r in rows if r['target'] in targets)/len(targets)
            for arm in ('P','U','H64')} for m,targets in source.masks().items()}
        meter.call(h.close)
        need(not any(h.ring) and h.pending is None,'H64_CLEANUP')
        return dict(rows=rows,U=compact_u(u),metrics=metrics,cycle=cycle,
            resources=dict(U=u['resources'],H64_heap_peak=meter.peak,H64_ring_bytes=len(h.ring),P_vector_bytes=384),
            complete=True,reference_equal=True,neutral_only=record['neutral_only'],
            frames_per_arm=1040,targets_per_arm=519,H64_censored_prediction=value_id(pending[1]))
    finally:
        if h.pending is not None or any(h.ring):h.close()
