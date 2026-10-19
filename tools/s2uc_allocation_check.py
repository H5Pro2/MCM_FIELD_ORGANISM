"""Preregistered equal-frame-budget allocation comparison, synthetic only."""
import hashlib
import json
from pathlib import Path

from tools._s2uc_allocation import TwoCandidateOneRetainedArm
from tools._s2uc_provisional_hint import ProvisionalHintArm
from tools.s2uc_k2_check import Meter, submit, candidates, provenance, state, tu, ROOT

OUT=ROOT/'reports/s2uc/allocation-20260930-01'
ARMS={'1K2R':ProvisionalHintArm,'2K1R':TwoCandidateOneRetainedArm}


def meter():
    result=Meter()
    result.files.add(str((ROOT/'tools/_s2uc_allocation.py').resolve()))
    return result


def query(arm,measure,values,identity):
    before=state(arm)
    measure.hint_positions+=3*(len(candidates(arm))+len(arm._retained_many))
    assert measure.call(arm,'hint',tu.Frame(tuple(values[0]),'a'*64,arm.owner,identity,10000)) is None
    result=measure.call(arm,'hint',tu.Frame(tuple(values[1]),'a'*64,arm.owner,identity,10001))
    assert state(arm)==before
    return result


def replay(p,name,case,hints):
    spec=p['cases'][case];arm=ARMS[name]('a'*64,f'{name}/{case}/{hints}');m=meter()
    rows=[];probes=[];snapshots=[]
    for step,label in enumerate(spec['sequence'],1):
        before=provenance(arm)
        receipt=submit(arm,m,p['vectors'][label],f'step{step}',step*10)
        after=provenance(arm)
        removed={role:[x for x in before[role] if x not in after[role]] for role in before}
        actual=[[int(x['formation'][4:]) for x in after[role]] for role in ('candidates','retained')]
        rows.append(dict(step=step,receipt=receipt,before=before,after=after,removed=removed,
                         expected_state=spec['states'][name][step-1],
                         prediction='CONFIRMED' if actual==spec['states'][name][step-1] else 'VIOLATED'))
        snapshots.append(state(arm))
        if hints:
            for probe_index,probe in enumerate(spec['probes']):
                if probe['after']!=step:
                    continue
                for repeat in range(probe['repeat']):
                    result=query(arm,m,p['vectors'][probe['target']],f'{case}/{probe_index}/{repeat}')
                    expected=probe['expected'][name]
                    origins=[{k:v for k,v in match.items() if k!='generation'} for match in result['matches']]
                    probes.append(dict(after=step,target=probe['target'],repeat=repeat,result=result,expected=expected,
                                       prediction='CONFIRMED' if result['decision']==expected['decision'] and origins==expected['matches'] else 'VIOLATED'))
    assert m.peak_trace<=16 and m.peak_hint<=2 and m.peak_total<=18
    arm.close_owner()
    assert all(v==0 for v in arm.resources().values())
    return dict(steps=rows,probes=probes,meter=m.summary()),snapshots


def boundary(p,name):
    arm=ARMS[name]('a'*64,name+'/boundary');m=meter()
    sequence=p['boundary'][name]
    for i,label in enumerate(sequence,1):
        submit(arm,m,p['vectors'][label],f'step{i}',i*10)
    for i,value in enumerate(p['vectors']['C']):
        m.call(arm,'form',tu.Frame(tuple(value),'a'*64,arm.owner,'C',100+i))
    before=provenance(arm)
    receipt=query(arm,m,p['vectors']['A'],'boundary')
    close=m.call(arm,'close_segment','C')
    after=provenance(arm)
    assert (m.peak_trace,m.peak_hint,m.peak_total)==(16,2,18)
    assert receipt['decision']=='PROVISIONAL_CANDIDATE_MATCH'
    assert [x['formation'] for x in after['candidates']]==(['C'] if name=='1K2R' else ['step4','C'])
    arm.close_owner()
    return dict(before=before,hint=receipt,close=close,after=after,meter=m.summary())


def run():
    raw=(OUT/'preregistration.json').read_bytes();p=json.loads(raw)
    assert all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==sha for f,sha in p['bindings'].items())
    result=dict(preregistration_sha256=hashlib.sha256(raw).hexdigest(),arms={})
    for name in ARMS:
        result['arms'][name]={}
        for case in p['cases']:
            observed,snapshots=replay(p,name,case,True)
            control,plain=replay(p,name,case,False)
            assert observed['steps']==control['steps'] and snapshots==plain
            observed['no_hint_control_equal']=True
            result['arms'][name][case]=observed
        result['arms'][name]['boundary']=boundary(p,name)
    result['bindings_unchanged']=all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==sha for f,sha in p['bindings'].items())
    result['notes']=['Equal frame capacity, not equal RAM. Numeric capacity is 6912 bytes per arm including hints.',
                     'Whole-trace comparisons are actual _same_values calls; hint positions count exhaustive search positions, not scalar comparisons.',
                     'Times include tracing, not an efficiency benchmark. Temporary census observes Python trace boundaries.',
                     'Removed candidates include promotion; receipt action distinguishes promotion from eviction.',
                     'No-hint controls compare all post-close states and receipts; hints do not renew or confirm.']
    with (OUT/'result.json').open('x') as f:
        json.dump(result,f,indent=2)
    return result


if __name__=='__main__':
    r=run()
    for name,cases in r['arms'].items():
        for case,data in cases.items():
            print(name,case,data['meter'])
