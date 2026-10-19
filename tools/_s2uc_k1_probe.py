"""Neutral qualification driver with independent memory/feedback expectations."""
import json
import sys
from tools import _s2uc_k1 as implementation
from tools._s2uc_k1_reference import Reference
from tools._s2uc_multi_observer import Meter, cells, HEAD, ENTRY, POLICY, PerceptionSample, digest


def snapshot(arm):
    def trace(t, generation):
        return dict(generation=generation, ordinals=[f.ordinal for f in t.frames], values=[f.values for f in t.frames])
    return dict(candidate=None if arm._candidate is None else trace(arm._candidate,arm._candidate.candidate_generation),
        retained=[trace(t,t.generation) for t in arm._retained_many], forming=[f.ordinal for f in arm._forming],
        candidate_serial=arm._candidate_generation,retained_serial=arm._retained_generation,
        observation_end=dict(arm._observation_end))


def error(left,right):
    total=0.0
    for i in range(48):
        total=total+abs(left[i]-right[i])
    return total/48


def cellmap(adapter):
    return {(x['role'],x['generation'],x['offset']):(x['ec'],x['ep']) for x in cells(adapter)}


def keyset(model):
    return {(0,t['generation']) for t in model.retained} | (set() if model.candidate is None else {(1,model.candidate['generation'])})


def probe(values, *, enabled, trace=False):
    values=[tuple(v) for v in values]
    profile=digest(values)
    adapter=implementation.create(profile,'neutral-owner','neutral-stream',
        candidate_policy=implementation.POLICY if enabled else 'disabled',multi_policy=POLICY)
    reference=Reference(enabled)
    meter=Meter(adapter)
    records=[];forecasts=[];updates=[];expected={};outputs=[]
    oldtrace=sys.gettrace()
    def operation(name,fn):
        if not trace:return meter.measure(name,fn)
        sys.settrace(meter.trace)
        try:return fn()
        finally:sys.settrace(oldtrace)
    try:
        for i,vector in enumerate(values,1):
            sample=PerceptionSample(vector,profile,'neutral-owner','neutral-stream',i,(i-1)*4800,i*4800)
            if adapter.pending_prediction:
                prediction=adapter.pending_prediction
                frozen=[]
                for j in range(HEAD.unpack_from(adapter.bank,192)[2]):
                    g,role,off,_,_=ENTRY.unpack_from(adapter.bank,208+16*j)
                    alive=(role,g) in keyset(reference)
                    assert alive==adapter._generation_live(role,g)
                    ec=error(adapter._frozen[j].values,vector);ep=error(adapter._pframe.values,vector)
                    key=(role,g,off)
                    if alive:
                        prior=expected.get(key)
                        expected[key]=(ec,ep) if prior is None else (.5*prior[0]+.5*ec,.5*prior[1]+.5*ep)
                    frozen.append(dict(key=list(key),live=alive,original=adapter._frozen[j].ordinal,ec=ec,ep=ep))
                outputs.append(dict(target=i,decision=prediction.status,
                    error=error(adapter.selected_values,vector),persistence=error(prediction.persistence_values,vector)))
                operation('feedback',lambda:adapter.consume_feedback(sample))
                assert cellmap(adapter)==expected,'INDEPENDENT_FEEDBACK'
                updates.append(dict(target=i,hypotheses=frozen,cells=cells(adapter)))
            before=reference.snapshot()
            pre_cells=dict(expected)
            receipt=operation('perception',lambda:adapter.accept_perception(sample))
            if i%2==0:
                actual=json.loads(receipt.json_text)
                matches=reference.matches(values[i-2:i])
                assert matches==sorted((0 if x['role']=='retained' else 1,x['generation'],x['offset']) for x in actual['matches'])
                candidates={k:pre_cells.get(k) for k in matches if k[2]<2}
                scored=[(pair[0]-pair[1],k) for k,pair in candidates.items() if pair is not None and pair[0]<pair[1]]
                best=min((d for d,k in scored),default=None)
                winning=[k for d,k in scored if d==best]
                chosen=None if len(winning)!=1 else winning[0]
                tickets={h['ticket']:(0 if m['role']=='retained' else 1,m['generation'],m['offset'])
                    for m,h in zip(actual['matches'],actual['hypotheses']) if h['eligible']}
                actualkey=None if not actual['choice'] else tickets[actual['choice']-1]
                assert actualkey==chosen,'INDEPENDENT_SELECTION'
                for h in actual['hypotheses']:
                    if h['eligible']:
                        v=pre_cells.get(tickets[h['ticket']])
                        assert (None if h['ec'] is None else (h['ec'],h['ep']))==v
                frozen_prediction=adapter.pending_prediction
                forecasts.append(actual)
                for ordinal in (i-1,i):reference.feed(ordinal,values[ordinal-1])
                after=reference.snapshot()
                old_candidate=before['candidate']
                promoted=next((t for t in after['retained'] if old_candidate and t['ordinals']==old_candidate['ordinals'] and
                    not any(b['generation']==t['generation'] for b in before['retained'])),None)
                if promoted:
                    expected={(0,promoted['generation'],k[2]) if k[:2]==(1,old_candidate['generation']) else k:v for k,v in expected.items()}
                expected={k:v for k,v in expected.items() if k[:2] in keyset(reference)}
                assert cellmap(adapter)==expected,'INDEPENDENT_PRUNE_PROMOTION'
                assert adapter.pending_prediction is frozen_prediction
                meter.receipt=max(meter.receipt,len(receipt.json_text.encode()))
            assert snapshot(adapter.arm)==reference.snapshot(),'INDEPENDENT_MEMORY'
            assert len(adapter.bank)==416
            records.append(dict(index=i,before=before,after=reference.snapshot(),cells=cells(adapter)))
        operation('finish',adapter.finish_story)
        assert adapter.closed and not any(adapter.bank) and not any(adapter._frozen)
        assert not adapter.arm._candidate and not adapter.arm._retained_many and not adapter.arm._forming
        return dict(enabled=enabled,trace_pass=trace,frames=len(values),forecasts=forecasts,
            updates=updates,outputs=outputs,admissions=records,resources=meter.snapshot(),
            reference_equal=True,cleanup=True,neutral_only=True)
    finally:
        sys.settrace(oldtrace)
        if not adapter.closed:adapter._terminate()
