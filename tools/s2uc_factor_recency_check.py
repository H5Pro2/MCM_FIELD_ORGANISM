"""Bound stored-vector integration; no PCM processing."""
import json,sys,time,tracemalloc
from fractions import Fraction
from pathlib import Path
from tools.s2uc_pcm_temporal_check import ROOT,sha,save
from tools._s2uc_factor_recency import FactorRecencyArm
from tools._s2uc_factor_hint import FactorHintArm
from tools._s2uc_perception_recency import PerceptionRecencyArm
from tools.s2uc_factor_hint_check import HintMeter
from tools.s2uc_k2_check import state,provenance,tu
OUT=ROOT/'reports/s2uc/factor-recency-20260930-01'
OLD=ROOT/'reports/s2uc/pcm-temporal-20260930-01'

def oracle(a,h,factor):
    sources=[('retained',t.generation,t.frames) for t in a._retained_many]
    if a._candidate:sources.append(('candidate',a._candidate.candidate_generation,a._candidate.frames))
    result=[]
    for role,g,frames in sources:
        for o in range(3):
            fs=[f for f in ((.5,1.,2.) if factor else (1.,)) if all(Fraction(x)*Fraction(f)==Fraction(y) for j in range(2) for x,y in zip(frames[o+j].values,h[j]))]
            if fs:
                d=dict(role=role,generation=g,formation=frames[0].segment,ordinals=[x.ordinal for x in frames],offset=o)
                if factor:d['factors']=fs
                result.append(d)
    return result

def register():
    bindings={}
    for folder in (OLD,ROOT/'reports/s2uc/perception-recency-20260930-02'):
        for f,d in json.loads((folder/'inventory.json').read_text()).items():
            assert sha((ROOT/f).read_bytes())==d['sha256'];bindings[f]=d['sha256']
        for f,h in json.loads((folder/'preregistration.json').read_text())['bindings'].items():
            assert sha((ROOT/f).read_bytes())==h;bindings[f]=h
    for f in ('tools/_s2uc_factor_recency.py','tools/s2uc_factor_recency_check.py','tests/test_s2uc_factor_recency.py'):
        bindings[f]=sha((ROOT/f).read_bytes())
    OUT.mkdir(exist_ok=False)
    save(OUT/'preregistration.json',dict(bindings=bindings,scope='LOCAL_INTEGRATION_STORED_VECTORS_ONLY',cases=['half_hint','exact_observation','half_observation','ambiguous_hint'],expected_final={'half_hint':{'F':[2,3],'P':[2,3],'C':[2,3]},'exact_observation':{'F':[2,3],'P':[1,3],'C':[1,3]},'half_observation':{'F':[2,3],'P':[2,3],'C':[2,3]},'ambiguous_hint':{'F':[2,3],'P':[2,3],'C':[2,3]}},predictions=['half HA: F/C A@0 factor .5, P no match; state unchanged','exact A: P/C refresh original A, F no refresh; candidate unchanged','full half A: candidate created, no refresh, marks unchanged; Z replaces this candidate','half BC: F/C A@1,D@1 ambiguous; P no match','original BC: all A@1,D@1 ambiguous','full occupancy: 16 trace + 2 hint simultaneously; pending forming not searchable'],runtime=sys.version,created_ns=time.time_ns()))

def run():
    raw=(OUT/'preregistration.json').read_bytes();p=json.loads(raw);assert all(sha((ROOT/f).read_bytes())==h for f,h in p['bindings'].items())
    old=json.loads((OLD/'result.json').read_text());v=[d['projection']['values'] for d in old['processed'][:4]];profile=old['processed'][0]['projection']['profile_digest'];A=v;D=[v[3],v[1],v[2],v[0]];Z=list(reversed(v));half=[[x*.5 for x in row] for row in A]
    tracemalloc.start();start=time.perf_counter_ns();out={};baseline={}
    for case in p['cases']+['full_occupancy']:
        out[case]={}
        for name,cls in [('F',FactorHintArm),('P',PerceptionRecencyArm),('C',FactorRecencyArm)]:
            a=cls(profile,f'{case}/{name}');meter=HintMeter();meter.files.add(str((ROOT/'tools/_s2uc_perception_recency.py').resolve()));receipts=[];snapshots=[];queries=[];n=1
            def snapshot():return dict(state=state(a),provenance=provenance(a),marks=dict(getattr(a,'_observation_end',{})))
            def submit(values,segment,close=True):
                nonlocal n
                for x in values:meter.call(a,'form',tu.Frame(tuple(x),profile,a.owner,segment,n));n+=1
                if close:receipts.append(meter.call(a,'close_segment',segment));snapshots.append(snapshot())
            def query(label,h):
                before=snapshot();candidate=a._candidate;retained=tuple(a._retained_many);meter.hint_positions+=3*(len(retained)+(candidate is not None))
                expected=oracle(a,h,name!='P');qn=10000+2*len(queries)
                assert meter.call(a,'hint',tu.Frame(tuple(h[0]),profile,a.owner,label,qn)) is None
                assert getattr(a,'_observation_end',{})==before['marks']
                result=meter.call(a,'hint',tu.Frame(tuple(h[1]),profile,a.owner,label,qn+1))
                assert snapshot()==before and a._candidate is candidate and all(x is y for x,y in zip(retained,a._retained_many))
                assert result['matches']==expected
                decision='ABSTAIN_NO_MATCH' if not expected else 'ABSTAIN_AMBIGUOUS' if len(expected)>1 else 'PROVISIONAL_CANDIDATE_MATCH' if expected[0]['role']=='candidate' else 'CONFIRMED_RETAINED_MATCH'
                assert result['decision']==decision;queries.append(dict(label=label,result=result,before=before,after=snapshot()));return result
            for values,seg in [(A,'A-1'),(A,'A-2'),(D,'D-1'),(D,'D-2')]:submit(values,seg)
            ta,td=a._retained_many;marks=dict(getattr(a,'_observation_end',{}));candidate=a._candidate
            if case=='half_hint':
                for rep in range(2):
                    q=query('halfHA'+str(rep),half[:2]);assert [(x['generation'],x['offset']) for x in q['matches']]==([] if name=='P' else [(1,0)])
            elif case=='exact_observation':
                submit(A,'A-3');assert a._candidate is candidate;assert a.inventory==((1,2) if name=='F' else (2,1));assert any(x is ta for x in a._retained_many)
            elif case=='half_observation':
                submit(half,'half-A');assert receipts[-1]['action']=='TRACE_CANDIDATE_CREATED' and a.inventory==(1,2) and getattr(a,'_observation_end',{})==marks
                assert [f.values for f in a._candidate.frames]==[tuple(x) for x in half]
            elif case=='ambiguous_hint':
                for rep in range(2):
                    assert query('BC'+str(rep),v[1:3])['decision']=='ABSTAIN_AMBIGUOUS'
                    q=query('halfBC'+str(rep),half[1:3]);assert q['decision']==('ABSTAIN_NO_MATCH' if name=='P' else 'ABSTAIN_AMBIGUOUS')
            if case=='full_occupancy':
                submit(Z,'Z-1');c=a._candidate;submit(A,'pending-A',False)
                assert a.resources()['trace_frames']==16
                query('fullBC',v[1:3]);query('fullHalfBC',half[1:3]);assert a._candidate is c
                assert (meter.peak_trace,meter.peak_hint,meter.peak_total)==(16,2,18)
                receipts.append(meter.call(a,'close_segment','pending-A'));assert a._candidate is c
            else:
                submit(Z,'Z-1');submit(Z,'Z-2');assert list(a.inventory)==p['expected_final'][case][name]
                if case=='half_observation':assert receipts[-2]['action']=='TRACE_CANDIDATE_REPLACED'
                keepA=case=='exact_observation' and name!='F'
                assert any(t is (ta if keepA else td) for t in a._retained_many)
                for label,h,want in [('HA',A[:2],[1] if keepA else []),('HD',[v[3],v[1]],[] if keepA else [2])]:assert [m['generation'] for m in query(label,h)['matches']]==want
            assert meter.peak_trace<=16 and meter.peak_hint<=2 and meter.peak_total<=18
            out[case][name]=dict(receipts=receipts,snapshots=snapshots,queries=queries,final=snapshot(),meter=meter.summary(),marks_python_bytes=sys.getsizeof(getattr(a,'_observation_end',{}))+sum(sys.getsizeof(k)+sys.getsizeof(v) for k,v in getattr(a,'_observation_end',{}).items()) if name!='F' else 0)
            a.close_owner();assert all(x==0 for x in a.resources().values()) and not getattr(a,'_observation_end',{})
        # Combined transition behavior must exactly equal recency-only reference.
        assert out[case]['C']['receipts']==out[case]['P']['receipts']
        assert out[case]['C']['snapshots']==out[case]['P']['snapshots']
    current,peak=tracemalloc.get_traced_memory();tracemalloc.stop();assert all(sha((ROOT/f).read_bytes())==h for f,h in p['bindings'].items())
    r=dict(cases=out,scope=p['scope'],preregistration_sha256=sha(raw),bindings_unchanged=True,pcm_calls=0,resources=dict(elapsed_ns=time.perf_counter_ns()-start,python_peak_bytes=peak,python_current_bytes=current),query_count=sum(len(x['queries']) for c in out.values() for x in c.values()))
    save(OUT/'result.json',r);print('PASS',r['query_count'],'queries',r['resources'])
if __name__=='__main__':
    if sys.argv[1:]==['register']:register()
    elif sys.argv[1:]==['run']:run()
