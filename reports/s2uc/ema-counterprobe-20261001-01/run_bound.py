"""Authorized two-story counterprobe, read-only instrumentation of bound replay."""
import hashlib
import json
import math
import sys
import tracemalloc
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

from tools import s2uc_ema_qualification as q
from tools import _s2uc_paired_error_ema as ema
from tools import _s2uc_paired_error_replay as replay
from tools._s2uc_signal_approx_compare import ApproxBudgetObserver
from tools.s2uc_continuous_comparison import state
from tests.test_s2uc_paired_error_ema import addon_owned

OUT=Path(__file__).resolve().parent
AUTH=q.ROOT/'docs/S2UC_EMA_GEGENPROBEN_AUTORISIERUNG_20261001.json'


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def cells(a):
    if a._errors is None:return []
    return [dict(generation=g,ec=ec,ep=ep,role=r,offset=o,quality=k)
        for g,ec,ep,r,o,k,valid in (ema.CELL.unpack_from(a._errors.cells,i*32) for i in range(12)) if valid]


def material(plan,story):
    assert story in ('constant','switch_return') and plan['cycles']==24 and plan['frames_per_story']==200
    proto={k:float(Fraction(v)) for k,v in plan['prototype'].items() if k!='components'}
    scalars=[proto[k] for k in ('U','V','W','Z')]*2
    for j in range(1,25):
        scalars.extend(15/16+(4*j+k)/8192 for k in range(4))
        y=proto['V'] if story=='switch_return' and 9<=j<=16 else proto['W']
        scalars.extend((proto['U'],proto['V'],y,13/16+j/4096))
    assert len(scalars)==200
    return [tuple([x]*48) for x in scalars]


def observed_replay(values,profile,arm):
    forecasts=[];updates=[];admissions=[];states=[];lifetimes=[]
    meter=ApproxBudgetObserver();memory_peaks=[]
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
        if before!=after:lifetimes.append(dict(at_admitted=a.admitted,before=before,after=after))

    def receipt(a,*args):
        result=original_receipt(a,*args)
        if a.pending_prediction is not None:
            p=a.pending_prediction
            chosen=p.persistence_values if arm=='P' else a.selected_values
            forecasts.append(dict(target=p.target_index,choice='CONTEXT' if chosen is p.context_values else 'PERSISTENCE',
                context_available=p.context_values is not None,errors_before=cells(a),
                ticket=None if a._errors is None else list(ema.TICKET.unpack(a._errors.ticket)),
                receipt=json.loads(p.provenance_json),frozen_before_target=True))
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
        measured(a,original_feedback,a,sample)
        after=cells(a)
        key=lambda c:(c['role'],c['generation'],c['offset'],c['quality'])
        assert sorted(after,key=key)==sorted(expected,key=key)
        assert a.pending_prediction is None and not any(a._errors.ticket)
        updates.append(dict(target=sample.index,actual_entered=True,ticket=list(ticket),key_live=live,
            context_error=ec,persistence_error=ep,before=before,after=after,atomic_pair_verified=True))

    def accept(a,sample):
        sys.settrace(meter.trace)
        try:result=original_accept(a,sample)
        finally:sys.settrace(None)
        states.append(digest(state(a.arm)))
        admissions.append(sample.index)
        assert all(a._generation_live(c['role'],c['generation']) for c in cells(a))
        if sample.index%50==0:print(arm,'frame',sample.index,flush=True)
        return result

    with patch.object(ema.PairedErrorAdapter,'accept_perception',accept),\
         patch.object(ema.PairedErrorAdapter,'_receipt',receipt),\
         patch.object(ema.PairedErrorAdapter,'consume_feedback',feedback),\
         patch.object(ema.PairedErrorAdapter,'_freeze_choice',freeze),\
         patch.object(ema.ErrorMemory,'prune',prune):
        result=replay.replay(values,profile,count=200,arm=arm,bounded_contract=replay.EXTENSION)
    assert admissions==list(range(1,201)) and len(states)==200
    assert [x['target'] for x in forecasts]==list(range(3,202,2))
    assert result['censored_target']==201
    assert all(a['choice']==b['choice'] for a,b in zip(forecasts,result['rows']))
    if arm=='E':assert [x['target'] for x in updates]==list(range(3,200,2))
    assert result['slots_released'] and result['ema_cleared']
    assert meter.frame_peak<=18 and meter.output_slots_peak<=2 and meter.combined_peak<=20
    assert max(memory_peaks,default=0)<=16384
    result.update(forecasts=forecasts,error_updates=updates,cell_lifetime_events=lifetimes,state_hashes=states,
        resources=dict(frame_meter=vars(meter),additional_python_peak=max(memory_peaks,default=0),
            additional_measurements=len(memory_peaks),qualification_method='retained addon Python size plus isolated tracemalloc peak; observer instrumentation excluded'))
    return result


def main():
    b=q.read(q.BINDING);plan=q.read(q.PLAN);auth=q.read(AUTH)
    assert b['code']==q.hashes() and q.sha(q.PLAN)==b['plan_sha256']
    assert b['python']==sys.version and b['python_executable_sha256']==q.sha(sys.executable)
    assert auth==dict(status='AUTHORIZED_ONCE',action='RUN_EMA_COUNTERPROBES',plan_sha256=q.sha(q.PLAN),
        binding_sha256=q.sha(q.BINDING),runner_sha256=q.sha(__file__),stories=['constant','switch_return'],arms=['E','K','P'])
    q.save(OUT/'execution-claim.json',auth)
    q.save(OUT/'preexecution.json',dict(code=b['code'],runner_sha256=q.sha(__file__),
        plan_sha256=q.sha(q.PLAN),binding_sha256=q.sha(q.BINDING),python=sys.version,
        scope='two bound stories,200 frames,three arms; no parameter or recipe changes',
        instrumentation='transparent observer wrappers call bound methods exactly once; no policy changes'))
    profile=digest(dict(geometry='direct48.counterprobe.v1',plan_sha256=q.sha(q.PLAN)))
    results={};status='NOT_EVALUABLE';error=None
    try:
        for story in plan['stories']:
            values=material(plan,story)
            q.save(OUT/(story+'-material.json'),dict(story=story,profile=profile,values=values,values_digest=digest(values)))
            results[story]={}
            for arm in plan['arms']:
                print(story,arm,'START',flush=True)
                result=observed_replay(values,profile,arm);results[story][arm]=result
                q.save(OUT/(story+'-'+arm+'.json'),result)
                print(story,arm,'COMPLETE',flush=True)
            assert results[story]['E']['state_hashes']==results[story]['K']['state_hashes']==results[story]['P']['state_hashes']
            assert digest(values)==q.read(OUT/(story+'-material.json'))['values_digest']
        assert sum(r['frames'] for systems in results.values() for r in systems.values())==1200
        assert b['code']==q.hashes() and q.sha(q.PLAN)==b['plan_sha256']
        status='COMPLETE'
    except BaseException as exc:
        error=type(exc).__name__+':'+str(exc)
        raise
    finally:
        q.save(OUT/'execution-closure.json',dict(status=status,error=error,
            completed_arms={k:list(v) for k,v in results.items()},planned_frames=1200,
            policy_changed=False,parameters_changed=False))


if __name__=='__main__':main()
