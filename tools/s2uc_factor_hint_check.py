"""Twelve preregistered exact/factor hint cases with exact confirmation."""
import hashlib
import json
from pathlib import Path
import tracemalloc
from tools import _s2uc_factor_hint as factor
from tools._s2uc_provisional_hint import ProvisionalHintArm
from tools.s2uc_k2_check import Meter,submit,state,provenance,ROOT
from tools.s2uc_allocation_check import query

OUT=ROOT/'reports/s2uc/factor-hint-20260930-01'
ARMS={'E':ProvisionalHintArm,'F':factor.FactorHintArm}


def decode_values(p):
    # JSON 0 and 0.0 have the same specified value; Frames require float objects.
    for key,frames in p['vectors'].items():
        p['vectors'][key]=[[float(x) for x in frame] for frame in frames]
    for case in p['cases'].values():
        case['hint_values']=[[float(x) for x in frame] for frame in case['hint_values']]
    return p


class HintMeter(Meter):
    def __init__(self):
        super().__init__()
        self.files.add(str(Path(factor.__file__).resolve()))
        self.factors=0
        self.scalars=0
        self.peak_bytes=0

    def trace(self,frame,event,arg):
        if frame.f_code in (factor.factor_matches.__code__,factor.component_equal.__code__) or frame.f_code.co_name=='<genexpr>' and frame.f_code.co_filename==factor.__file__:
            if event=='call':
                self.factors+=frame.f_code is factor.factor_matches.__code__
                self.scalars+=frame.f_code is factor.component_equal.__code__
            return None
        return super().trace(frame,event,arg)

    def call(self,arm,method,arg):
        before=tracemalloc.get_traced_memory()[0]
        tracemalloc.reset_peak()
        result=super().call(arm,method,arg)
        self.peak_bytes=max(self.peak_bytes,tracemalloc.get_traced_memory()[1]-before)
        return result

    def summary(self):
        return dict(**super().summary(),factor_checks=self.factors,scalar_factor_checks=self.scalars,
                    incremental_python_call_peak_bytes=self.peak_bytes)


def replay(p,name,key,hints):
    spec=p['cases'][key];arm=ARMS[name]('a'*64,f'{name}/{key}/{hints}');m=HintMeter()
    states=[];transitions=[];outputs=[]
    for step,label in enumerate(spec['sequence'],1):
        receipt=submit(arm,m,p['vectors'][label],f'step{step}',step*10)
        transitions.append(receipt);states.append(state(arm))
    initial=provenance(arm)
    if hints:
        for repeat in range(p['repeat_count']):
            result=query(arm,m,spec['hint_values'],f'{key}/hint/{repeat}')
            normalized=[dict(match,**({'factors':[1.]} if name=='E' else {})) for match in result['matches']]
            outputs.append(dict(repeat=repeat,decision=result['decision'],matches=normalized,
                                decision_prediction='CONFIRMED' if result['decision']==spec['expected_decisions'][name] else 'VIOLATED',
                                matches_prediction='CONFIRMED' if normalized==spec['expected'][name] else 'VIOLATED',
                                serialized_provenance_bytes=len(json.dumps(normalized).encode())))
    for step,label in enumerate(p['followup'],len(spec['sequence'])+1):
        receipt=submit(arm,m,p['vectors'][label],f'step{step}',step*10)
        transitions.append(receipt);states.append(state(arm))
    assert m.peak_trace<=16 and m.peak_hint<=2 and m.peak_total<=18
    arm.close_owner();assert all(x==0 for x in arm.resources().values())
    return dict(initial=initial,hints=outputs,transitions=transitions,meter=m.summary()),states


def boundary(p,name):
    arm=ARMS[name]('a'*64,name+'/boundary');m=HintMeter()
    for step,label in enumerate(('A','A','Q','Q','H'),1):
        submit(arm,m,p['vectors'][label],f'step{step}',step*10)
    from tools._s2uc_four_arm import tu
    for i,values in enumerate(p['vectors']['B']):
        m.call(arm,'form',tu.Frame(tuple(values),'a'*64,arm.owner,'forming',60+i))
    result=query(arm,m,p['cases']['02_half']['hint_values'],'full-hint')
    expected='PROVISIONAL_CANDIDATE_MATCH' if name=='E' else 'ABSTAIN_AMBIGUOUS'
    assert (m.peak_trace,m.peak_hint,m.peak_total)==(16,2,18)
    assert result['decision']==expected
    assert len(result['matches'])==(1 if name=='E' else 3)
    close=m.call(arm,'close_segment','forming')
    assert m.peak_trace<=16
    return dict(hint=result,close=close,meter=m.summary())


def run():
    raw=(OUT/'preregistration.json').read_bytes();p=decode_values(json.loads(raw))
    assert all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==sha for f,sha in p['bindings'].items())
    tracemalloc.start()
    report=dict(preregistration_sha256=hashlib.sha256(raw).hexdigest(),arms={})
    baseline_states={};baseline_transitions={}
    for name in ARMS:
        report['arms'][name]={}
        for key in p['cases']:
            result,states=replay(p,name,key,True)
            control,plain=replay(p,name,key,False)
            assert states==plain and result['transitions']==control['transitions']
            result['without_hints_equal']=True
            if name=='E':
                baseline_states[key]=states;baseline_transitions[key]=result['transitions']
            else:
                assert states==baseline_states[key] and result['transitions']==baseline_transitions[key]
                result['same_state_and_exact_transitions_as_E']=True
            report['arms'][name][key]=result
        report['arms'][name]['boundary']=boundary(p,name)
    tracemalloc.stop()
    report['bindings_unchanged']=all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==sha for f,sha in p['bindings'].items())
    report['notes']=['Only hint overridden; gain-confirmation module is not used.',
        'E factors [1] are observer metadata only; reference code untouched.',
        'Hint match key includes role, generation, original formation/frame ordinals and position; factors grouped within key.',
        'At most3 source references,9 match records,3 factors per record; no scaled vector banks.',
        'Python call peaks include tracing/observer allocations, not process RAM. Numeric frame budget6912 bytes per arm.',
        'Scalar factor counters observe helper calls; reference whole-trace counts concern unchanged confirmation.',
        'Trace-point census is not native allocation completeness; wall times include instrumentation.']
    assert not any(x.endswith('_s2uc_gain_confirmation') for x in __import__('sys').modules)
    with (OUT/'result.json').open('x') as f:json.dump(report,f,indent=2)
    for name,cases in report['arms'].items():
        print(name,'cases',len(cases)-1,'factor checks',sum(x['meter']['factor_checks'] for k,x in cases.items() if k!='boundary'))
    return report


if __name__=='__main__':run()
