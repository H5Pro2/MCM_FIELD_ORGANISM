"""Read-only stock observer; unchanged EMA/retrieval/memory methods called once.

No planned material is created here. Instrumentation is serial, not thread safe.
"""
import hashlib
import json
import sys
import tracemalloc
from unittest.mock import patch
from tools import _s2uc_paired_error_ema as ema
from tools import _s2uc_paired_error_replay as replay
from tools._s2uc_signal_approx_compare import ApproxBudgetObserver
from tools.s2uc_continuous_comparison import state
from tests.test_s2uc_paired_error_ema import addon_owned


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def cells(a):
    if a._errors is None:return []
    return [dict(generation=g,ec=ec,ep=ep,role=r,offset=o,quality=k)
        for g,ec,ep,r,o,k,valid in (ema.CELL.unpack_from(a._errors.cells,i*32) for i in range(12)) if valid]


def inventory(a):
    def item(t,role):
        return dict(role=role,generation=t.generation if role==0 else t.candidate_generation,
            ordinals=[f.ordinal for f in t.frames],values_sha256=digest([f.values for f in t.frames]))
    return dict(retained=[item(t,0) for t in a.arm._retained_many],
        candidate=None if a.arm._candidate is None else item(a.arm._candidate,1))


def stock_keys(stock):
    return [[t['role'],t['generation']] for t in stock['retained']+([stock['candidate']] if stock['candidate'] else [])]


def observed_replay(values,profile,arm,*,count=64,evidence=None):
    assert type(count) is int and 4<=count<=64 and count%2==0
    if evidence is None:evidence={}
    generation_events=[];phase=["idle"]
    forecasts=[];updates=[];admissions=[];states=[];lifetimes=[]
    meter=ApproxBudgetObserver();memory_peaks=[]
    evidence.update(forecasts=forecasts,error_updates=updates,cell_lifetime_events=lifetimes,
        generation_events=generation_events,state_hashes=states,admissions=admissions)
    original_admit=ema.PairedErrorAdapter._admit
    original_accept=ema.PairedErrorAdapter.accept_perception
    original_receipt=ema.PairedErrorAdapter._receipt
    original_feedback=ema.PairedErrorAdapter.consume_feedback
    original_prune=ema.ErrorMemory.prune
    original_freeze=ema.PairedErrorAdapter._freeze_choice

    def measured(a,fn,*args):
        tracing=sys.gettrace();sys.settrace(None)
        retained=addon_owned(a)
        tracemalloc.start();before=tracemalloc.get_traced_memory()[0]
        try:return fn(*args)
        finally:
            _,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
            memory_peaks.append(retained+max(0,peak-before))
            sys.settrace(tracing)

    def freeze(a):return measured(a,original_freeze,a)

    def prune(memory,a):
        before=cells(a)
        measured(a,original_prune,memory,a)
        after=cells(a)
        assert all(a._generation_live(c['role'],c['generation']) for c in after)
        expected=[c for c in before if a._generation_live(c['role'],c['generation'])]
        assert after==expected
        if before!=after:lifetimes.append(dict(phase=phase[0],at_admitted=a.admitted,before=before,after=after))

    def receipt(a,*args):
        result=original_receipt(a,*args)
        # exact_v1 serializes in PairContextAdapter, outside ApproxBudgetObserver's
        # file-specific counter. One immutable JSON string is shared by both
        # receipts; allow another complete UTF-8 copy for encode() preflight.
        size=len(result.json_text.encode('utf-8'))
        meter.receipt_bytes_peak=max(meter.receipt_bytes_peak,size)
        meter.receipt_transient_utf8_bytes_peak=max(meter.receipt_transient_utf8_bytes_peak,2*size)
        assert size<=16384 and 2*size<=32768
        if a.pending_prediction is not None:
            p=a.pending_prediction
            chosen=p.persistence_values if arm=='P' else a.selected_values
            forecasts.append(dict(target=p.target_index,choice='CONTEXT' if chosen is p.context_values else 'PERSISTENCE',
                context_available=p.context_values is not None,errors_before=cells(a),
                ticket=None if a._errors is None else list(ema.TICKET.unpack(a._errors.ticket)),
                receipt=json.loads(p.provenance_json),frozen_before_target=True))
        return result

    def admit(a,frame):
        before=cells(a);stock_before=inventory(a);phase[0]="admission"
        try:result=original_admit(a,frame)
        finally:phase[0]="idle"
        after=cells(a);stock_after=inventory(a)
        assert after==[c for c in before if a._generation_live(c["role"],c["generation"])]
        generation_events.append(dict(frame=frame.ordinal,phase="admission",before=stock_before,
            after=stock_after,cells_before=before,cells_after=after,
            deleted=[c for c in before if c not in after],
            removed_keys=[k for k in stock_keys(stock_before) if k not in stock_keys(stock_after)],
            new_keys=[k for k in stock_keys(stock_after) if k not in stock_keys(stock_before)]))
        return result

    def feedback(a,sample):
        before=cells(a);ticket=ema.TICKET.unpack(a._errors.ticket);p=a.pending_prediction
        assert p is not None and p.target_index==sample.index
        g,target,role,offset,quality,choice,valid=ticket
        live=bool(valid and a._generation_live(role,g))
        ec=None if p.context_values is None else ema.mae48(p.context_values,sample.values)
        ep=ema.mae48(p.persistence_values,sample.values)
        expected=[dict(c) for c in before]
        if live:
            old=next((c for c in expected if (c['role'],c['generation'],c['offset'],c['quality'])==(role,g,offset,quality)),None)
            if old is None:expected.append(dict(generation=g,ec=ec,ep=ep,role=role,offset=offset,quality=quality))
            else:old.update(ec=.5*old['ec']+.5*ec,ep=.5*old['ep']+.5*ep)
        phase[0]="target_consumption"
        try:measured(a,original_feedback,a,sample)
        finally:phase[0]="idle"
        after=cells(a)
        key=lambda c:(c['role'],c['generation'],c['offset'],c['quality'])
        assert sorted(after,key=key)==sorted(expected,key=key)
        assert a.pending_prediction is None and not any(a._errors.ticket)
        updates.append(dict(phase="target_consumption",target=sample.index,actual_entered=True,ticket=list(ticket),key_live=live,
            context_error=ec,persistence_error=ep,before=before,after=after,atomic_pair_verified=True))

    def accept(a,sample):
        sys.settrace(meter.trace)
        try:result=original_accept(a,sample)
        finally:sys.settrace(None)
        states.append(digest(state(a.arm)))
        admissions.append(sample.index)
        assert all(a._generation_live(c['role'],c['generation']) for c in cells(a))
        return result

    with patch.object(ema.PairedErrorAdapter,'_admit',admit),\
         patch.object(ema.PairedErrorAdapter,'accept_perception',accept),\
         patch.object(ema.PairedErrorAdapter,'_receipt',receipt),\
         patch.object(ema.PairedErrorAdapter,'consume_feedback',feedback),\
         patch.object(ema.PairedErrorAdapter,'_freeze_choice',freeze),\
         patch.object(ema.ErrorMemory,'prune',prune):
        result=replay.replay(values,profile,count=count,arm=arm)
    assert admissions==list(range(1,count+1)) and len(states)==count
    assert [x['target'] for x in forecasts]==list(range(3,count+2,2))
    assert result['censored_target']==count+1
    assert all(a['choice']==b['choice'] for a,b in zip(forecasts,result['rows']))
    if arm=='E':assert [x['target'] for x in updates]==list(range(3,count,2))
    assert result['slots_released'] and result['ema_cleared']
    assert meter.frame_peak<=18 and meter.output_slots_peak<=2 and meter.combined_peak<=20
    assert max(memory_peaks,default=0)<=16384
    result.update(generation_events=generation_events,forecasts=forecasts,error_updates=updates,cell_lifetime_events=lifetimes,state_hashes=states,
        resources=dict(frame_meter=vars(meter),additional_python_peak=max(memory_peaks,default=0),
            additional_measurements=len(memory_peaks),
            receipt_measurement='actual exact receipt UTF8 bytes; transient upper bound includes one complete encoding copy',
            qualification_method='retained addon Python size plus isolated tracemalloc peak; observer instrumentation excluded'))
    return result

