"""Stored-vector recency integration, no perception processing."""
import json,sys,time,tracemalloc
from pathlib import Path
from tools.s2uc_pcm_temporal_check import ROOT,sha,save
from tools._s2uc_perception_recency import PerceptionRecencyArm
from tools._s2uc_provisional_hint import ProvisionalHintArm
from tools.s2uc_k2_check import Meter,state,tu,provenance
OUT=ROOT/'reports/s2uc/perception-recency-20260930-02'
OLD=ROOT/'reports/s2uc/pcm-temporal-20260930-01'

def register():
    OUT.mkdir(exist_ok=False)
    files=['tools/_s2uc_perception_recency.py','tools/s2uc_perception_recency_check.py','tests/test_s2uc_perception_recency.py','tools/_s2uc_provisional_hint.py','tools/_s2uc_four_arm.py','tools/_s2ub_candidate_confirmation.py','tools/_s2tu_retained_trace.py','tools/_s2tx_recency_confirmation.py','reports/s2uc/pcm-temporal-20260930-01/result.json']
    inv=json.loads((OLD/'inventory.json').read_text());f=files[-1];assert sha((ROOT/f).read_bytes())==inv[f]['sha256']
    save(OUT/'preregistration.json',dict(bindings={f:sha((ROOT/f).read_bytes()) for f in files},predicted={'main':{'R':[2,3],'P':[1,3]},'none':{'R':[2,3],'P':[2,3]},'hints':{'R':[2,3],'P':[2,3]}},scope='STORED_VECTOR_MEMORY_RULE_ONLY',overlap_rule='New full interval starts after latest accepted observation ends; max two ordinal watermarks; ordinal clock supplied by caller',runtime=sys.version,created_ns=time.time_ns()))

def run():
    raw=(OUT/'preregistration.json').read_bytes();p=json.loads(raw);assert all(sha((ROOT/f).read_bytes())==h for f,h in p['bindings'].items())
    old=json.loads((OLD/'result.json').read_text());v=[d['projection']['values'] for d in old['processed'][:4]];profile=old['processed'][0]['projection']['profile_digest'];data={'A':v,'D':[v[3],v[1],v[2],v[0]],'Z':list(reversed(v))};allout={}
    tracemalloc.start();start=time.perf_counter_ns()
    for case in ('main','none','hints'):
        allout[case]={}
        for name,cls in [('R',ProvisionalHintArm),('P',PerceptionRecencyArm)]:
            a=cls(profile,f'{case}/{name}');m=Meter();m.files.add(str((ROOT/'tools/_s2uc_perception_recency.py').resolve()));receipts=[];states=[];queries=[];ordinal=1
            def submit(label,seg):
                nonlocal ordinal
                for x in data[label]:m.call(a,'form',tu.Frame(tuple(x),profile,a.owner,seg,ordinal));ordinal+=1
                receipts.append(m.call(a,'close_segment',seg));states.append(dict(state=state(a),provenance=provenance(a)))
            def query(label,pair):
                before=state(a);watermark=dict(getattr(a,'_observation_end',{}));qord=10000+len(queries)*2;m.hint_positions+=6
                assert m.call(a,'hint',tu.Frame(tuple(pair[0]),profile,a.owner,label,qord)) is None
                res=m.call(a,'hint',tu.Frame(tuple(pair[1]),profile,a.owner,label,qord+1));assert state(a)==before and dict(getattr(a,'_observation_end',{}))==watermark
                sources=a._retained_many;expected=[]
                for t in sources:
                    for o in range(3):
                        if t.frames[o].values==tuple(pair[0]) and t.frames[o+1].values==tuple(pair[1]):expected.append(dict(role='retained',generation=t.generation,formation=t.frames[0].segment,ordinals=[f.ordinal for f in t.frames],offset=o))
                assert res['matches']==expected;queries.append(dict(label=label,result=res,state_unchanged=True));return res
            for label,seg in [('A','A-1'),('A','A-2'),('D','D-1'),('D','D-2')]:submit(label,seg)
            for label,pair in [('HA',v[:2]),('HD',[v[3],v[1]]),('HBC',v[1:3])]:query('before-'+label,pair)
            originalA=a._retained_many[0];originalD=a._retained_many[1]
            if case=='main':
                submit('A','A-3');assert any(t is originalA for t in a._retained_many)
                assert a.inventory==((2,1) if name=='P' else (1,2))
            elif case=='hints':
                query('intervening-1',v[:2]);query('intervening-2',v[:2]);assert a.inventory==(1,2)
            submit('Z','Z-1');submit('Z','Z-2')
            assert list(a.inventory)==p['predicted'][case][name]
            keepA=case=='main' and name=='P'
            survivor=originalA if keepA else originalD;assert any(t is survivor for t in a._retained_many)
            for label,pair,want in [('HA',v[:2],[1] if keepA else []),('HD',[v[3],v[1]],[] if keepA else [2]),('HBC',v[1:3],[1] if keepA else [2])]:
                res=query('after-'+label,pair);assert [d['generation'] for d in res['matches']]==want
            assert m.peak_trace<=16 and m.peak_hint<=2 and m.peak_total<=18
            allout[case][name]=dict(receipts=receipts,states=states,queries=queries,meter=m.summary(),original_survivor_object_preserved=True)
            a.close_owner();assert all(x==0 for x in a.resources().values())
    current,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
    assert all(sha((ROOT/f).read_bytes())==h for f,h in p['bindings'].items())
    r=dict(scope=p['scope'],preregistration_sha256=sha(raw),cases=allout,bindings_unchanged=True,pcm_calls=0,resources=dict(elapsed_ns=time.perf_counter_ns()-start,python_peak_bytes=peak,python_current_bytes=current),query_count=sum(len(a['queries']) for c in allout.values() for a in c.values()))
    save(OUT/'result.json',r);print('Completed',r['query_count'],'queries',r['resources'])
if __name__=='__main__':
    if sys.argv[1:]==['register']:register()
    elif sys.argv[1:]==['run']:run()
