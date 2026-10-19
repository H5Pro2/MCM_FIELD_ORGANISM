"""Neutral A1 observer: independent stock, errors, tickets and decision checks."""
import json
import sys
from tools import _s2uc_a1 as impl
from tools._s2uc_a1_reference import Reference
from tools._s2uc_k1_reference import Reference as UReference
from tools._s2uc_k1_probe import snapshot,error,cellmap,keyset
from tools._s2uc_multi_observer import Meter,POLICY,PerceptionSample,HEAD,ENTRY,digest
from tools._s2uc_t1_evidence_v2 import expected_matches,match_core,key,select


def probe(indices,*,enabled=True,trace=False):
    values=[tuple(.125+(n+1)/512+j/262144 for j in range(48)) for n in indices]
    profile=digest(values)
    a=impl.create(profile,'neutral-a1','stream',admission_policy=impl.POLICY if enabled else 'disabled',multi_policy=POLICY)
    ref=Reference() if enabled else UReference(False)
    meter=Meter(a);expected={};rows=[];forecasts=[];states=[];revision=0;slots=0
    oldtrace=sys.gettrace()
    def op(name,fn):
        if not trace:return meter.measure(name,fn)
        sys.settrace(meter.trace)
        try:return fn()
        finally:sys.settrace(oldtrace)
    def rekey(old,new):
        nonlocal expected
        expected={(tuple(new)+(k[2],)) if k[:2]==tuple(old) else k:v for k,v in expected.items()}
        expected={k:v for k,v in expected.items() if k[:2] in keyset(ref)}
    try:
        for i,v in enumerate(values,1):
            sample=PerceptionSample(v,profile,'neutral-a1','stream',i,(i-1)*4800,i*4800)
            if a.pending_prediction is not None:
                prediction=a.pending_prediction;updates=[]
                for j in range(HEAD.unpack_from(a.bank,192)[2]):
                    g,role,off,_,_=ENTRY.unpack_from(a.bank,208+16*j);k=(role,g,off)
                    live=k[:2] in keyset(ref);ec=error(a._frozen[j].values,v);ep=error(a._pframe.values,v)
                    if live:
                        prev=expected.get(k);expected[k]=(ec,ep) if prev is None else (.5*prev[0]+.5*ec,.5*prev[1]+.5*ep)
                    updates.append(dict(key=list(k),live=live,ec=ec,ep=ep,original=a._frozen[j].ordinal))
                rows.append(dict(target=i,error=error(a.selected_values,v),decision=prediction.status,updates=updates))
                op('feedback',lambda:a.consume_feedback(sample));assert cellmap(a)==expected,'FEEDBACK'
            event=None;before=ref.snapshot()
            original=None if a.arm._candidate is None else a.arm._candidate.frames
            if i%2==0 and enabled:
                event=ref.preforecast([(i-1,values[i-2]),(i,v)])
                if event:rekey(event['old_key'],event['new_key']);revision+=1
            forecast_stock=ref.snapshot();forecast_cells=dict(expected)
            receipt=op('perception',lambda:a.accept_perception(sample))
            if i%2==0:
                f=json.loads(receipt.json_text)
                assert f.get('a1_admission')==event
                assert f['read_revision']==revision
                assert sorted(map(match_core,f['matches']))==sorted(expected_matches(forecast_stock,values,i+1))
                pairs={};tickets={}
                for m,h in zip(f['matches'],f['hypotheses'],strict=True):
                    k=key(m);eligible=m['factors']==[1.0] and m['offset']<2
                    assert h['eligible']==eligible
                    if not eligible:continue
                    pair=forecast_cells.get(k);assert (None if h['ec'] is None else (h['ec'],h['ep']))==pair
                    pairs[k]=pair;tickets[h['ticket']]=k
                    assert ENTRY.unpack_from(a.bank,208+16*h['ticket'])[:3]==(k[1],k[0],k[2])
                    assert a._frozen[h['ticket']].ordinal==m['ordinals'][m['offset']+2]
                chosen=select(pairs);actual=None if not f['choice'] else tickets[f['choice']-1]
                assert actual==chosen
                selected=values[i-1] if chosen is None else next(values[m['ordinals'][m['offset']+2]-1] for m in f['matches'] if key(m)==chosen)
                assert a.selected_values==selected
                assert a.pending_prediction.provenance_json==receipt.json_text
                if event:
                    retained=next(t for t in a.arm._retained_many if t.generation==event['new_key'][1])
                    assert retained.frames is original,'ORIGINAL_TUPLE_IDENTITY'
                    assert f['retained_semantics']=='ADMITTED_NOT_FULL_REPEAT_PROOF'
                forecasts.append(f)
                old=ref.candidate
                for ordinal in (i-1,i):ref.feed(ordinal,values[ordinal-1])
                promoted=next((t for t in ref.retained if old and t['frames']==old['frames'] and not any(x['generation']==t['generation'] for x in forecast_stock['retained'])),None)
                if promoted:rekey((1,old['generation']),(0,promoted['generation']))
                expected={k:v for k,v in expected.items() if k[:2] in keyset(ref)}
                revision+=2+int(i%4==0)
                meter.receipt=max(meter.receipt,len(receipt.json_text.encode()))
                slots=max(slots,1+int(a.pending_prediction.context_values is not None))
                assert meter.receipt<=16384 and 2*meter.receipt<=32768 and slots<=2
            assert snapshot(a.arm)==ref.snapshot(),'INDEPENDENT_STOCK'
            assert cellmap(a)==expected and len(a.bank)==416
            states.append(dict(index=i,stock={k:v for k,v in ref.snapshot().items() if k!='forming'},cells=[dict(key=list(k),values=v) for k,v in expected.items()]))
        if len(values)%2:
            ref.feed(len(values),values[-1])
        op('finish',a.finish_story)
        assert a.closed and not any(a.bank) and not any(a._frozen) and not a.arm._retained_many and a.arm._candidate is None
        resources=meter.snapshot();resources['output_slots_peak']=max(resources['output_slots_peak'],slots)
        return dict(frames=len(values),enabled=enabled,trace=trace,rows=rows,forecasts=forecasts,states=states,
            resources=resources,reference_equal=True,cleanup=True,neutral_only=True)
    finally:
        sys.settrace(oldtrace)
        if not a.closed:a._terminate()
