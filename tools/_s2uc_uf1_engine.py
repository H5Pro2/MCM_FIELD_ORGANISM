"""External U/F observer and independent F state comparison."""
import hashlib
import struct
import zlib
import tracemalloc
from fractions import Fraction as F
from tools._s2uc_uf1_f import HintFrequency,CONTROL,OUTPUT,SIZE
from tools._s2uc_uf1_reference import Reference
from tools._s2uc_hx1_replay import replay as u_replay
from tools._s2uc_ulz1_engine import compact
from tools._s2uc_ulz1_resources import deep
from tools import _s2uc_uf1_sources as source

class Meter:
    def __init__(self,h):self.h=h;self.peak=0;self.phases={}
    def call(self,name,fn):
        retained=deep(self.h);tracemalloc.start();base=tracemalloc.get_traced_memory()[0]
        try:return fn()
        finally:
            peak=tracemalloc.get_traced_memory()[1];tracemalloc.stop()
            total=retained+peak-base;self.peak=max(self.peak,total);self.phases[name]=max(self.phases.get(name,0),total)
            if total>32768:raise ValueError('F_HEAP_LIMIT')
            if len(self.h.bank)!=SIZE:raise ValueError('F_BANK_LIMIT')

def replay(record,check=lambda:None,*,short=False):
    values=source.hx.values(record)
    if len(values)!=1024 and not short:raise ValueError('FRAME_COUNT')
    h=HintFrequency();ref=Reference();meter=Meter(h);trace=[];rows=[];previous=bytes(h.bank)
    replacements=0;feedback_history={}
    def frame(i,v):
        nonlocal previous,replacements
        check()
        if bytes(h.bank)!=ref.state():raise ValueError('F_PRE_REFERENCE')
        kind=h.kind;slot=h.slot;value=h.value
        counts=None if slot==255 else [h.word(slot*1560+1536),h.word(slot*1560+1544)]
        stamp=None if slot==255 else h.word(slot*1560+1552)
        history=list(feedback_history.get(slot,[])) if slot!=255 else []
        replaced=i%4==3 and kind==1 and h.word(1536)>0 and h.word(3096)>0
        observed=meter.call(f'phase{i%4}',lambda:h.accept(i,v))
        expected=ref.accept(i,v)
        if observed!=expected:raise ValueError('F_ERROR_REFERENCE')
        current=bytes(h.bank)
        if current!=ref.state():raise ValueError('F_STATE_REFERENCE')
        delta=bytes(a^b for a,b in zip(previous,current,strict=True));packed=zlib.compress(delta,9)
        # Independently reconstruct each exported delta before publication.
        restored=zlib.decompress(packed)
        if bytes(x^previous[j] for j,x in enumerate(restored))!=ref.state():raise ValueError('F_DELTA_REFERENCE')
        trace.append([i,packed.hex()]);previous=current
        if i%2 and i>1:
            r=dict(target=i,F=observed)
            if i%4==3:r.update(F_known=kind in (2,3),F_slot=None if slot==255 else slot,F_replaced=bool(replaced),F_class={1:'F0',2:'F1',3:'F2'}[kind],F_counts=counts,F_value=None if value==255 else value,F_stamp=stamp,F_values_occupied=0 if counts is None else sum(n>0 for n in counts),F_first_feedback=history[0] if history else None,F_last_feedback=history[-1] if history else None)
            rows.append(r)
        if i%4==3:
            learned=0 if h.word(1552)==h.word(CONTROL+8) else 1
            if kind==1:feedback_history[learned]=[]
            feedback_history.setdefault(learned,[]).append(i)
        replacements+=int(replaced)
    try:
        u=u_replay(values,source.PROFILE,check,frame)
        meter.call('finish' if not short else 'short_abort',h.finish if not short else h.abort)
        ref.close() if short else ref.finish()
        if bytes(h.bank)!=ref.state():raise ValueError('F_CLEANUP_REFERENCE')
    finally:
        if not h.closed:meter.call('abort',h.abort)
    cumulative=F(0);qsum=F(0)
    for ur,r in zip(u['rows'],rows,strict=True):
        if ur['target']!=r['target']:raise ValueError('ALIGNMENT')
        r['U']=ur['error'];cumulative+=F(r['U'])-F(r['F']);r['cumulative']=str(cumulative)
        if r['target']%4==3:
            hs=ur['hypotheses'];warm=[x for x in hs if x['before'] is not None]
            r['class']='V0' if not hs else 'V1' if not warm else 'V3' if ur['selected'] else 'V2'
            r['cue']='X' if record['ids'][r['target']-3]==0 else 'Y'
            r['age']=[len(x['prior_feedback']) for x in hs]
            r['first_feedback']=[x['prior_feedback'][0] if x['prior_feedback'] else None for x in hs]
            r['last_feedback']=[x['prior_feedback'][-1] if x['prior_feedback'] else None for x in hs]
            qsum+=F(r['U'])-F(r['F']);r['cumulative_Q']=str(qsum)
        elif r['U']!=r['F']:raise ValueError('SKELETON_EQUALITY')
    res=dict(u['resources']);res.pop('allocation_boundaries')
    return dict(U=compact(u),F_delta_codec='zlib9 XOR of consecutive 4304-byte banks, initial zero except slot/value sentinels 255 at offsets 3145/3146',F_trace=trace,
        rows=rows,resources=dict(U=res,F=dict(own_heap_peak=meter.peak,phase_peaks=meter.phases,packed=SIZE,
            numeric_limit=5120,numeric_conservative_upper=4712,output_slots=1,borrowed_input_payload=384,
            borrowed_input_object_bytes=max(map(deep,values)),receipt_bytes=0)),
        observer=dict(input_object_bytes=deep(values),U_evidence_bytes=deep(u),F_trace_bytes=deep(trace),
            reference_F_boundary_bytes=deep(ref),note='External observer/reference copies, excluded from arm heap but inside joint process cap'),
        replacements=replacements,reference_advances=dict(U=len(values),F=len(values)),complete=True,
        cleanup=True,censored_target=len(values)+1,neutral_only=record['neutral_only'])
