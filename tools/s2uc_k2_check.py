"""Small, preregistered synthetic FIFO-capacity comparison."""
import hashlib
import json
from pathlib import Path
import sys
import time

from tools._s2uc_two_candidates import TwoCandidateArm, tu, ub
from tools._s2uc_provisional_hint import ProvisionalHintArm
from tools.s2uc_b2v_check import VariantObserver, state

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/s2uc/k2-20260930-01'
FACTORIES={'K1':ProvisionalHintArm,'K2':TwoCandidateArm}


def candidates(arm):
    if isinstance(arm,TwoCandidateArm):
        return arm._candidates
    return [] if arm._candidate is None else [arm._candidate]


def provenance(arm):
    return dict(candidates=[dict(generation=c.candidate_generation,formation=c.frames[0].segment,
                                 ordinals=[f.ordinal for f in c.frames]) for c in candidates(arm)],
                retained=[dict(generation=t.generation,formation=t.frames[0].segment,
                               ordinals=[f.ordinal for f in t.frames]) for t in arm._retained_many])


class Meter(VariantObserver):
    def __init__(self):
        super().__init__(set(range(10000,11000)))
        for name in ('_s2uc_two_candidates.py','_s2uc_provisional_hint.py'):
            self.files.add(str((ROOT/'tools'/name).resolve()))
        self.trace_comparisons=0
        self.hint_positions=0
        self.call_ns=0
        self.role_peaks={}

    def trace(self,frame,event,arg):
        if event=='call' and frame.f_code is ub._same_values.__code__:
            self.trace_comparisons+=1
        return super().trace(frame,event,arg)

    def call(self,arm,method,arg):
        start=time.perf_counter_ns()
        sys.settrace(self.trace)
        try:
            result=getattr(arm,method)(arg)
        finally:
            sys.settrace(None)
        self.call_ns+=time.perf_counter_ns()-start
        for k,v in arm.resources().items():
            self.role_peaks[k]=max(self.role_peaks.get(k,0),v)
        assert arm.resources()['trace_frames'] <= (20 if isinstance(arm,TwoCandidateArm) else 16)
        return result

    def summary(self):
        return dict(whole_trace_comparisons=self.trace_comparisons,hint_positions_checked=self.hint_positions,
                    traced_call_ns=self.call_ns,roles=self.role_peaks,
                    temporary_trace=self.peak_trace,temporary_hint=self.peak_hint,temporary_total=self.peak_total)


def submit(arm,meter,values,segment,start):
    for i,value in enumerate(values):
        meter.call(arm,'form',tu.Frame(tuple(value),'a'*64,arm.owner,segment,start+i))
    return meter.call(arm,'close_segment',segment)


def query(arm,meter,probe_id):
    before=state(arm)
    meter.hint_positions+=3*(len(candidates(arm))+len(arm._retained_many))
    assert meter.call(arm,'hint',tu.Frame((1.,)*48,'a'*64,arm.owner,probe_id,10000)) is None
    result=meter.call(arm,'hint',tu.Frame((2.,)*48,'a'*64,arm.owner,probe_id,10001))
    assert state(arm)==before
    return result


def replay(prereg,name,case,with_hints):
    arm=FACTORIES[name]('a'*64,f'{name}/{case}/{with_hints}')
    meter=Meter(); steps=[]; hints=[]; snapshots=[]
    for index,label in enumerate(prereg['cases'][case],1):
        receipt=submit(arm,meter,prereg['vectors'][label],f'step{index}',index*10)
        prov=provenance(arm)
        steps.append(dict(step=index,receipt=receipt,**prov))
        snapshots.append(state(arm))
        if with_hints:
            key=('conflict' if case=='conflict' and index==2 else
                 'after_A' if index==1 else 'after_AB' if index==2 else
                 'after_ABA' if case=='ABA' else 'after_ABC' if index==3 else 'after_ABCA')
            expected=prereg['predictions'][key][name]
            for repeat in range(4 if case=='repeat_control' and index==2 else 1):
                result=query(arm,meter,f'{case}/{index}/{repeat}')
                formations=[m['formation'] for m in result['matches']]
                offsets=[m['offset'] for m in result['matches']]
                expected_forms=expected[1] if isinstance(expected[1],list) else [] if expected[1] is None else [expected[1]]
                expected_offsets=expected[2] if isinstance(expected[2],list) else [] if expected[2] is None else [expected[2]]
                fulfilled=result['decision']==expected[0] and formations==expected_forms and offsets==expected_offsets
                hints.append(dict(after=index,repeat=repeat,expected=expected,result=result,
                                  prediction='CONFIRMED' if fulfilled else 'VIOLATED'))
    arm.close_owner()
    assert all(v==0 for v in arm.resources().values())
    return dict(steps=steps,hints=hints,meter=meter.summary()),snapshots


def boundary(prereg,name):
    arm=FACTORIES[name]('a'*64,'boundary/'+name); meter=Meter()
    for i,label in enumerate(('D','D','E','E','A','B'),1):
        submit(arm,meter,prereg['vectors'][label],f'step{i}',i*10)
    for i,values in enumerate(prereg['vectors']['C']):
        meter.call(arm,'form',tu.Frame(tuple(values),'a'*64,arm.owner,'step7',70+i))
    before=provenance(arm)
    receipt=query(arm,meter,'boundary-hint')
    close=meter.call(arm,'close_segment','step7')
    assert (meter.peak_trace,meter.peak_hint,meter.peak_total)==((20,2,22) if name=='K2' else (16,2,18))
    after=provenance(arm)
    arm.close_owner()
    return dict(before=before,hint=receipt,close=close,after=after,meter=meter.summary())


def run():
    raw=(OUT/'preregistration.json').read_bytes(); p=json.loads(raw)
    for path,sha in p['bindings'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha
    report=dict(preregistration_sha256=hashlib.sha256(raw).hexdigest(),arms={})
    for name in FACTORIES:
        report['arms'][name]={}
        for case in p['cases']:
            measured,states=replay(p,name,case,True)
            plain,plain_states=replay(p,name,case,False)
            assert states==plain_states and measured['steps']==plain['steps']
            measured['no_hint_control_equal']=True
            if case in p['expected_candidate_origins'][name]:
                actual=[[c['formation'] for c in step['candidates']] for step in measured['steps']]
                measured['candidate_fifo_prediction']='CONFIRMED' if actual==p['expected_candidate_origins'][name][case] else 'VIOLATED'
            if case=='ABA':
                expected='step1' if name=='K2' else None
                actual=measured['steps'][-1]['retained']
                measured['promotion_origin_prediction']='CONFIRMED' if ([x['formation'] for x in actual]==([] if expected is None else [expected])) else 'VIOLATED'
            report['arms'][name][case]=measured
        report['arms'][name]['boundary']=boundary(p,name)
    report['notes']=['K1 code unchanged; two candidates is the sole capacity intervention.',
                     'Whole-trace count observes actual _same_values calls; hint positions = 3 per searched trace, exhaustive in both implementations.',
                     'Counts are not scalar-comparison counts. Call times include line tracing; not a speed benchmark.',
                     'Numerical payload is not process RAM. Temporary census counts unique live Frame identities, not aliases.',
                     'Owner/segment labels carry provenance only; all matching uses values and disjoint ordinals.']
    report['bindings_unchanged']=all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==sha for f,sha in p['bindings'].items())
    with (OUT/'result.json').open('x') as f:
        json.dump(report,f,indent=2)
    return report


if __name__=='__main__':
    r=run()
    for name,cases in r['arms'].items():
        for case,data in cases.items():
            print(name,case,data['meter'])
