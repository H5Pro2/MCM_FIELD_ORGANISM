"""Stored-vector factor experiment, no receptor or source invocation."""
import hashlib
import json
import math
import sys
import tracemalloc
from pathlib import Path

from tools import _s2uc_gain_confirmation as gain
from tools._s2uc_provisional_hint import ProvisionalHintArm
from tools.s2uc_k2_check import Meter,submit,provenance,state,tu,ROOT
from tools.s2uc_allocation_check import query

OUT=ROOT/'reports/s2uc/gain-20260930-01'
ARMS={'E':ProvisionalHintArm,'G':gain.GainConfirmationArm}


class GainMeter(Meter):
    def __init__(self):
        super().__init__()
        self.files.add(str(Path(gain.__file__).resolve()))
        self.factor_tests=0
        self.scalar_tests=0
        self.python_peak=0

    def trace(self,frame,event,arg):
        if frame.f_code in (gain.scaled_equal.__code__,gain.component_equal.__code__) or frame.f_code.co_name=='<genexpr>' and frame.f_code.co_filename==gain.__file__:
            if event=='call':
                self.factor_tests+=frame.f_code is gain.scaled_equal.__code__
                self.scalar_tests+=frame.f_code is gain.component_equal.__code__
            return None
        return super().trace(frame,event,arg)

    def call(self,arm,method,arg):
        current=tracemalloc.get_traced_memory()[0]
        tracemalloc.reset_peak()
        result=super().call(arm,method,arg)
        self.python_peak=max(self.python_peak,tracemalloc.get_traced_memory()[1]-current)
        return result

    def summary(self):
        return dict(**super().summary(),factor_tests=self.factor_tests,scalar_factor_tests=self.scalar_tests,
                    traced_incremental_call_peak_bytes=self.python_peak)


def inputs(p):
    a=tuple(tuple(float.fromhex(v) for v in frame) for frame in p['A_values_hex'])
    h=tuple(tuple(math.ldexp(v,-1) for v in frame) for frame in a)
    q=tuple(tuple(math.ldexp(v,-2) for v in frame) for frame in a)
    return {'A':a,'H':h,'Q':q,'R':h[::-1],'L':(h[0],*a[1:])}


def preflight(p,v):
    checks={}
    checks['shape']=len(v['A'])==4 and all(len(f)==48 for f in v['A'])
    checks['finite_nonnegative']=all(math.isfinite(x) and x>=0 for f in v['A'] for x in f)
    checks['nonzero']=any(x>0 for f in v['A'] for x in f)
    checks['normal_reversible']=all(x==0 or (math.ldexp(x,-2)>=sys.float_info.min and math.ldexp(math.ldexp(x,-2),2)==x) for f in v['A'] for x in f)
    checks['ordered_distinct']=v['A']!=v['A'][::-1] and v['A']!=v['H']!=v['Q']
    # Static exact-hint suitability of preregistered states, no memory execution.
    checks['hint_suitability']=True
    for case in p['cases'].values():
        seq=case['sequence']
        for arm in ARMS:
            stored=[('retained',s) for s in case['retained'][arm]]
            if case['candidate'][arm] is not None:
                stored.append(('candidate',case['candidate'][arm]))
            for hint_index,label in enumerate((seq[0],seq[-1])):
                hits=[(role,s,offset) for role,s in stored for offset in range(3)
                      if v[seq[s-1]][offset:offset+2]==v[label][:2]]
                decision='ABSTAIN_NO_MATCH' if not hits else 'ABSTAIN_AMBIGUOUS' if len(hits)>1 else 'CONFIRMED_RETAINED_MATCH' if hits[0][0]=='retained' else 'PROVISIONAL_CANDIDATE_MATCH'
                expected=case['hints'][arm][hint_index]
                checks['hint_suitability'] &= decision==expected[0] and ([x[1:] for x in hits]==([] if expected[1] is None else [(expected[1],0)]))
    return checks


def replay(p,v,name,case_key,with_hints=True):
    case=p['cases'][case_key];arm=ARMS[name]('a'*64,f'{name}/{case_key}/{with_hints}');meter=GainMeter()
    transitions=[];snapshots=[]
    for step,label in enumerate(case['sequence'],1):
        before=state(arm)
        receipt=submit(arm,meter,v[label],f'step{step}',step*10)
        if receipt['action']=='ABSTAIN_AMBIGUOUS_CONFIRMATION':
            assert state(arm)==before
        transitions.append(dict(step=step,receipt=receipt,state=provenance(arm),
                                expected_action=case['actions'][name][step-1],
                                prediction='CONFIRMED' if receipt['action']==case['actions'][name][step-1] else 'VIOLATED'))
        snapshots.append(state(arm))
    final=provenance(arm)
    actual_r=[int(x['formation'][4:]) for x in final['retained']]
    actual_c=[int(x['formation'][4:]) for x in final['candidates']]
    expected_c=[] if case['candidate'][name] is None else [case['candidate'][name]]
    state_prediction=actual_r==case['retained'][name] and actual_c==expected_c
    # All stored frames retain their exact original values and ordinals.
    for trace in arm._retained_many:
        s=int(trace.frames[0].segment[4:])
        assert tuple(f.values for f in trace.frames)==v[case['sequence'][s-1]]
        assert [f.ordinal for f in trace.frames]==list(range(s*10,s*10+4))
    hints=[]
    if with_hints:
        for index,label in enumerate((case['sequence'][0],case['sequence'][-1])):
            for repeat in range(2):
                result=query(arm,meter,v[label],f'hint/{index}/{repeat}')
                expected=case['hints'][name][index]
                expected_origins=[] if expected[1] is None else [(f'step{expected[1]}',list(range(expected[1]*10,expected[1]*10+4)),0)]
                actual=[(m['formation'],m['ordinals'],m['offset']) for m in result['matches']]
                hints.append(dict(source=label,repeat=repeat,result=result,expected=expected,
                                  prediction='CONFIRMED' if result['decision']==expected[0] and actual==expected_origins else 'VIOLATED'))
    assert meter.peak_trace<=16 and meter.peak_hint<=2 and meter.peak_total<=18
    arm.close_owner();assert all(x==0 for x in arm.resources().values())
    return dict(transitions=transitions,hints=hints,final=final,state_prediction='CONFIRMED' if state_prediction else 'VIOLATED',meter=meter.summary()),snapshots


def boundary(v,name):
    arm=ARMS[name]('a'*64,name+'/boundary');m=GainMeter()
    for i,values in enumerate((v['A'],v['A'],v['A'][::-1],v['A'][::-1],v['Q']),1):
        submit(arm,m,values,f'step{i}',i*10)
    for i,values in enumerate(v['L']):
        m.call(arm,'form',tu.Frame(tuple(values),'a'*64,arm.owner,'forming',60+i))
    receipt=query(arm,m,v['A'],'boundary')
    assert (m.peak_trace,m.peak_hint,m.peak_total)==(16,2,18)
    close=m.call(arm,'close_segment','forming')
    assert m.peak_trace<=16
    arm.close_owner()
    return dict(hint=receipt,close=close,meter=m.summary())


def run():
    raw=(OUT/'preregistration.json').read_bytes();p=json.loads(raw)
    assert all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==sha for f,sha in p['bindings'].items())
    v=inputs(p);checks=preflight(p,v)
    report=dict(preregistration_sha256=hashlib.sha256(raw).hexdigest(),preconditions=checks,arms={})
    if not all(checks.values()):
        report['status']='UNSUITABLE_INPUT_NO_MEMORY_EVALUATION'
    else:
        tracemalloc.start()
        report['status']='EVALUATED_SYNTHETIC_VECTORS'
        for name in ARMS:
            report['arms'][name]={}
            for key in p['cases']:
                result,states=replay(p,v,name,key)
                control,plain=replay(p,v,name,key,False)
                assert states==plain and result['transitions']==control['transitions']
                result['no_hint_control_equal']=True
                report['arms'][name][key]=result
            report['arms'][name]['boundary']=boundary(v,name)
        tracemalloc.stop()
    report['bindings_unchanged']=all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==sha for f,sha in p['bindings'].items())
    report['notes']=['Matching factors are source-relative, not chained. Original payload is never overwritten.',
      'Ambiguous confirmation is an explicitly preregistered added abstention rule across candidate and retained roles.',
      'Temporary sources contain only references (max3); factors max3 per source; provenance metadata has no numeric vector copies.',
      'tracemalloc call peaks include Python observer/tracing objects, exclude earlier allocations; not process RAM or pure algorithm memory.',
      'Factor/scalar counts are observed helper calls. Reference whole-trace counts are not directly scalar-comparable.',
      'Existing exact hint method is inherited unchanged.']
    with (OUT/'result.json').open('x') as f:json.dump(report,f,indent=2)
    print(report['status'],checks)
    for name,cases in report['arms'].items():
        for key,data in cases.items():print(name,key,data['meter'])


if __name__=='__main__':run()
