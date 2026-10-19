"""Bound PCM competition probe; original arms and perception remain unchanged."""
import json,sys,time,tracemalloc,hashlib
from pathlib import Path
from fractions import Fraction
from tools.s2uc_pcm_temporal_check import ROOT,CONFIG,sha,save
from tools.s2uc_pcm_half_check import half_payload,process,band_comparison,measured
from tools.s2uc_k2_check import state,tu
from tools.s2uc_factor_hint_check import HintMeter
from tools._s2uc_provisional_hint import ProvisionalHintArm
from tools._s2uc_factor_hint import FactorHintArm
OLD=ROOT/'reports/s2uc/pcm-temporal-20260930-01'
OUT=ROOT/'reports/s2uc/pcm-competition-20260930-01'

def match(g,o,factor=None):
    d=dict(role='retained',generation=g,formation='A-1' if g==1 else 'D-1',ordinals=list(range(1,5)) if g==1 else list(range(9,13)),offset=o)
    if factor is not None:d['factors']=factor
    return d

def predictions(f):
    return {'BC':[match(g,1,[1.] if f else None) for g in (1,2)],'half_BC':[match(g,1,[.5]) for g in (1,2)] if f else [],'XB':[match(1,0,[1.] if f else None)],'half_XB':[match(1,0,[.5])] if f else []}

def oracle(traces,hint,f):
    found=[]
    for g,trace in enumerate(traces,1):
        for o in range(3):
            fs=[s for s in ((.5,1.,2.) if f else (1.,)) if all(Fraction(x)*Fraction(s)==Fraction(y) for j in range(2) for x,y in zip(trace[o+j],hint[j]))]
            if fs:found.append(match(g,o,fs if f else None))
    return found

def assess(actual,expected):
    return 'CONFIRMED' if actual==expected else 'VIOLATED'

def register():
    p=json.loads((OLD/'preregistration.json').read_text());inv=json.loads((OLD/'inventory.json').read_text())
    assert all(sha((ROOT/f).read_bytes())==h for f,h in p['bindings'].items())
    assert all(sha((ROOT/f).read_bytes())==d['sha256'] for f,d in inv.items())
    assert p['runtime']['python']==sys.version and p['runtime']['executable_sha256']==sha(Path(sys.executable).read_bytes())
    OUT.mkdir(exist_ok=False)
    bindings=dict(p['bindings'])
    for f in list(inv)+['reports/s2uc/pcm-temporal-20260930-01/inventory.json','tools/s2uc_pcm_competition_check.py','tests/test_s2uc_pcm_competition.py','docs/S2UC_PCM_KONKURRENZ_ENTWURF_20260930.txt']:
        bindings[f]=sha((ROOT/f).read_bytes())
    save(OUT/'preregistration.json',dict(bindings=bindings,runtime=p['runtime'],config=CONFIG,montage=[[1,2,3,4],[4,2,3,1]],sequence=['A-1','A-2','D-1','D-2'],predictions={a:predictions(a=='F') for a in ('E','F')},repeats_per_case_per_arm=2,criteria=['16 total queries','Check all positions/factors regardless of half-W1 relation','Prediction violations reported separately; no fallback prediction','Only one new half-W1 processing','D is synthetic montage; second presentations are test replay'],created_ns=time.time_ns()))

def memory(v,h,p):
    traces=[v,[v[3],v[1],v[2],v[0]]];cases={'BC':v[1:3],'half_BC':h[1:3],'XB':v[:2],'half_XB':h[:2]};out={};common=None;baseline=None
    profile=p
    for name,cls in [('E',ProvisionalHintArm),('F',FactorHintArm)]:
        arm=cls(profile,name+'/competition');meter=HintMeter();receipts=[];states=[]
        for step,segment in enumerate(('A-1','A-2','D-1','D-2')):
            for j,x in enumerate(traces[step//2]):meter.call(arm,'form',tu.Frame(tuple(x),profile,arm.owner,segment,step*4+j+1))
            receipts.append(meter.call(arm,'close_segment',segment));states.append(state(arm))
        assert [r['action'] for r in receipts]==['TRACE_CANDIDATE_CREATED','TRACE_PROMOTED','TRACE_CANDIDATE_CREATED','TRACE_PROMOTED']
        if baseline is None:baseline=states
        else:assert states==baseline
        before=state(arm)
        if common is None:common=before
        else:assert before==common
        results={}
        for label,hint in cases.items():
            expected=predictions(name=='F')[label];actual_oracle=oracle(traces,hint,name=='F');repeats=[]
            for rep in range(2):
                meter.hint_positions+=6
                assert meter.call(arm,'hint',tu.Frame(tuple(hint[0]),profile,arm.owner,label+str(rep),10000)) is None
                result=meter.call(arm,'hint',tu.Frame(tuple(hint[1]),profile,arm.owner,label+str(rep),10001))
                assert state(arm)==before
                assert result['matches']==actual_oracle
                decision='ABSTAIN_NO_MATCH' if not actual_oracle else 'ABSTAIN_AMBIGUOUS' if len(actual_oracle)>1 else 'CONFIRMED_RETAINED_MATCH'
                assert result['decision']==decision
                repeats.append(result)
            assert repeats[0]==repeats[1]
            results[label]=dict(repeats=repeats,expected=expected,oracle=actual_oracle,prediction=assess(actual_oracle,expected),state_unchanged=True)
        assert meter.peak_trace<=16 and meter.peak_hint<=2 and meter.peak_total<=18
        out[name]=dict(cases=results,receipts=receipts,states=states,meter=meter.summary())
        arm.close_owner();assert all(x==0 for x in arm.resources().values())
    return out

def run():
    raw=(OUT/'preregistration.json').read_bytes();p=json.loads(raw)
    assert all(sha((ROOT/f).read_bytes())==h for f,h in p['bindings'].items())
    assert sys.version==p['runtime']['python'] and sha(Path(sys.executable).read_bytes())==p['runtime']['executable_sha256']
    tracemalloc.start();old,cost=measured(lambda:json.loads((OLD/'result.json').read_text()))
    payload=(ROOT/old['provenance']['source']).read_bytes()[:19200]
    assert sha(payload)==old['provenance']['windows'][0]['sha256']
    (half,checks),dercost=measured(lambda:half_payload(payload));assert half is not None
    with (OUT/'half-W1.pcm').open('xb') as f:f.write(half)
    save(OUT/'input-binding.json',dict(parent=old['provenance'],window=1,samples=[0,4800],parent_window_sha256=sha(payload),half_sha256=sha(half),bytes=len(half),rule='Stored float32 samples * 0.5 then pack <f',checks=checks,preregistration_sha256=sha(raw)))
    proc,pcost=measured(lambda:process(half,CONFIG))
    assert proc['numpy_version']==p['runtime']['numpy']
    original=old['processed'][0]
    bands,bcost=measured(lambda:[dict(index=i,carrier=original['projection']['carrier_ids'][i],receptor=band_comparison(original['raw'][i],proc['raw'][i]),nj=band_comparison(original['projection']['values'][i],proc['projection']['values'][i])) for i in range(48)])
    v=[x['projection']['values'] for x in old['processed'][:4]];h=[proc['projection']['values']]+[x['projection']['values'] for x in old['processed'][4:]]
    start=time.perf_counter_ns();mem=memory(v,h,proc['projection']['profile_digest']);mcost=time.perf_counter_ns()-start
    unchanged=all(sha((ROOT/f).read_bytes())==h for f,h in p['bindings'].items());assert unchanged
    r=dict(status='EVALUATED_PCM_MONTAGE_COMPETITION',preregistration_sha256=sha(raw),half_checks=checks,processed_half_W1=proc,bands=bands,memory=mem,resources=dict(reused_evidence_loading=cost,derivation=dercost,processing=pcost,band_observer=bcost,memory_with_observer_elapsed_ns=mcost),bindings_unchanged=unchanged,new_receptor_calls=1,new_nj_calls=1,total_queries=16,notes=['D is synthetic montage','Second presentations are test replay','Python peaks not full process/native RAM; memory call peaks include tracer; phase peaks nonadditive','Only half-W1 is new; other six processed outputs reused'])
    tracemalloc.stop();save(OUT/'result.json',r)
    print(json.dumps({a:{k:dict(result=d['repeats'][0],prediction=d['prediction']) for k,d in x['cases'].items()} for a,x in mem.items()},indent=2))
if __name__=='__main__':
    if sys.argv[1:]==['register']:register()
    elif sys.argv[1:]==['run']:run()
    else:raise SystemExit('register | run')
