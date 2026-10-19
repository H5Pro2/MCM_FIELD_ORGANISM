"""HX1 observer: unchanged U followed by independent bounded G/P at each frame."""
import struct
import tracemalloc
from fractions import Fraction as F
from tools._s2uc_hx1_baselines import GlobalMean,Persistence,MeanReference,bits
from tools._s2uc_hx1_replay import replay as u_replay
from tools._s2uc_ulz1_engine import compact
from tools._s2uc_ulz1_resources import deep
from tools._s2uc_k1_probe import error
from tools._s2uc_paired_error_ema import mae48
from tools import _s2uc_hx1_sources as source

def need(ok,why):
    if not ok: raise ValueError(why)

class BaselineMeter:
    def __init__(self,arm,limit): self.arm=arm;self.limit=limit;self.peak=0
    def operation(self,fn,borrowed=()):
        # Exclude only the externally owned input vector alias, never a copied output.
        retained=deep(self.arm)
        if self.arm.output is not None and any(self.arm.output is v for v in borrowed): retained-=deep(self.arm.output)
        tracemalloc.start();base=tracemalloc.get_traced_memory()[0]
        try: return fn()
        finally:
            peak=tracemalloc.get_traced_memory()[1];tracemalloc.stop()
            total=retained+peak-base;self.peak=max(self.peak,total)
            need(total<=self.limit,'BASELINE_HEAP_LIMIT')

def replay(record,check=lambda:None,*,short=False):
    values=source.values(record);need(short or len(values)==1024,'FRAME_COUNT')
    g,p,gr=GlobalMean(),Persistence(),MeanReference()
    gm,pm=BaselineMeter(g,8192),BaselineMeter(p,4096)
    rows=[];qstates=[];prior=None;previous=None
    def frame(i,v):
        nonlocal prior,previous
        check()
        if i%2 and i>1:
            need(g.output is not None and p.output is not None,'BASELINE_FREEZE')
            need(bits(g.output)==bits(gr.output),'G_OUTPUT_REFERENCE')
            need(bits(p.output)==bits(previous),'P_OUTPUT_REFERENCE')
            ge,pe=mae48(g.output,v),mae48(p.output,v)
            need(ge==error(gr.output,v) and pe==error(previous,v),'BASELINE_ERROR_REFERENCE')
            rows.append(dict(target=i,G=ge,P=pe))
            if i%4==3:
                need(pe==.25,'P_Q_IDENTITY')
                qstates.append(dict(target=i,pre=prior,output=bits(g.output),error=ge))
        gm.operation(lambda:g.accept(i,v),(v,previous));gr.accept(i,v)
        need(set(vars(g))=={'bank','index','output'} and len(g.bank)==400,'G_STATE_BUDGET')
        need(g.bank[:384]==gr.state() and struct.unpack_from('<Q',g.bank,384)[0]==gr.n,'G_STATE_REFERENCE')
        pm.operation(lambda:p.accept(i,v),(v,previous))
        need(set(vars(p))=={'index','output'},'P_STATE_BUDGET')
        if i%4==2: prior=g.bank.hex()
        if i%4==3: qstates[-1]['post']=g.bank.hex()
        previous=v
    u=u_replay(values,source.digest('HX1-schema-48-float64'),check,frame)
    cumulative={pair:F(0) for pair in ('U/G','U/P','G/P')}
    for ur,r in zip(u['rows'],rows,strict=True):
        need(ur['target']==r['target'],'ROW_ALIGNMENT');r['U']=ur['error']
        if r['target']%4==3:
            hs=ur['hypotheses'];warm=[h for h in hs if h['before'] is not None]
            r['class']='V0' if not hs else 'V1' if not warm else 'V3' if ur['selected'] else 'V2'
            r['cue']='X' if record['ids'][r['target']-3]==0 else 'Y'
            r['age']=[len(h['prior_feedback']) for h in hs]
            r['first_feedback']=[h['prior_feedback'][0] if h['prior_feedback'] else None for h in hs]
            r['last_feedback']=[h['prior_feedback'][-1] if h['prior_feedback'] else None for h in hs]
            r['available']=[record['ids'][h['original']-1] for h in hs]
            r['warm']=[record['ids'][h['original']-1] for h in warm]
        else: need(r['U']==r['G']==r['P'],'SKELETON_EQUALITY')
        for pair in cumulative:
            cumulative[pair]+=F(r[pair[0]])-F(r[pair[2]])
        r['cumulative']={k:str(v) for k,v in cumulative.items()}
    gm.operation(g.close);pm.operation(p.close)
    need(not any(g.bank) and g.output is None and p.output is None,'BASELINE_CLEANUP')
    res=dict(u['resources']);res.pop('allocation_boundaries')
    return dict(U=compact(u),rows=rows,G_Q=qstates,complete=True,neutral_only=record['neutral_only'],
        resources=dict(U=res,G=dict(own_heap_peak=gm.peak,bank=400,output_slots=1,receipt_bytes=0),
                       P=dict(own_heap_peak=pm.peak,bank=0,output_slots=1,receipt_bytes=0)),
        reference_advances={a:len(values) for a in ('U','G','P')},cleanup=True,censored_target=len(values)+1)

def equal_global(d,n):
    need(d['G_Q']==n['G_Q'],'G_DN_BITWISE_INVARIANT')
