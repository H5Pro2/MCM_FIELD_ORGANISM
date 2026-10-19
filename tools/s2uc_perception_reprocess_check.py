"""Controlled reprocessing of existing PCM for A-3 only."""
import json,sys,time,tracemalloc,struct
from tools.s2uc_pcm_half_check import process,measured
from tools.s2uc_pcm_temporal_check import CONFIG
from pathlib import Path
from tools.s2uc_pcm_temporal_check import ROOT,sha,save
from tools._s2uc_perception_recency import PerceptionRecencyArm
from tools._s2uc_provisional_hint import ProvisionalHintArm
from tools.s2uc_k2_check import Meter,state,tu,provenance
OUT=ROOT/'reports/s2uc/perception-reprocess-20260930-01'
OLD=ROOT/'reports/s2uc/pcm-temporal-20260930-01'

def register():
    previous=ROOT/'reports/s2uc/perception-recency-20260930-02'
    oldplan=json.loads((previous/'preregistration.json').read_text())
    temporal=json.loads((OLD/'preregistration.json').read_text())
    bindings={**oldplan['bindings'],**temporal['bindings']}
    for directory in (previous,OLD):
        inventory=json.loads((directory/'inventory.json').read_text())
        for f,d in inventory.items():
            assert sha((ROOT/f).read_bytes())==d['sha256']
            bindings[f]=d['sha256']
    for f in ('tools/s2uc_perception_reprocess_check.py','tests/test_s2uc_perception_reprocess.py'):
        bindings[f]=sha((ROOT/f).read_bytes())
    assert all(sha((ROOT/f).read_bytes())==h for f,h in bindings.items())
    assert sys.version==temporal['runtime']['python']
    assert sha(Path(sys.executable).read_bytes())==temporal['runtime']['executable_sha256']
    OUT.mkdir(exist_ok=False)
    save(OUT/'preregistration.json',dict(bindings=bindings,predicted=oldplan['predicted'],config=CONFIG,runtime=temporal['runtime'],windows=json.loads((ROOT/'sources/s2uc/temporal-chirp-v1/provenance.json').read_text()),scope='CONTROLLED_REPROCESSING_SAME_PCM_NOT_NEW_RECORDING',criteria=['192 exact NJ values expected; no tolerance or correction','four new receptor and four NJ calls for A-3 only','same materialized objects to both arms','prediction violation separately reported','watermarks counted, readonly under hints, empty on owner close/new story'],created_ns=time.time_ns()))

def equality_rows(old,new):
    return [dict(window=i+1,band=j,original_hex=old[i][j].hex(),actual_hex=new[i][j].hex(),numeric_equal=old[i][j]==new[i][j],bit_equal=struct.pack('>d',old[i][j])==struct.pack('>d',new[i][j]),absolute_difference=abs(old[i][j]-new[i][j])) for i in range(4) for j in range(48)]


def run():
    raw=(OUT/'preregistration.json').read_bytes();p=json.loads(raw);assert all(sha((ROOT/f).read_bytes())==h for f,h in p['bindings'].items())
    old=json.loads((OLD/'result.json').read_text());v=[d['projection']['values'] for d in old['processed'][:4]];profile=old['processed'][0]['projection']['profile_digest'];data={'A':v,'D':[v[3],v[1],v[2],v[0]],'Z':list(reversed(v))};allout={}
    assert sys.version==p['runtime']['python'] and sha(Path(sys.executable).read_bytes())==p['runtime']['executable_sha256']
    tracemalloc.start();start=time.perf_counter_ns()
    payload=(ROOT/p['windows']['source']).read_bytes();assert sha(payload)==p['windows']['sha256']
    materialized=[];processing_costs=[]
    for i,w in enumerate(p['windows']['windows']):
        part=payload[w['samples'][0]*4:w['samples'][1]*4];assert sha(part)==w['sha256']
        result,cost=measured(lambda:process(part,p['config']))
        assert result['numpy_version']==p['runtime']['numpy']
        materialized.append(result);processing_costs.append(cost)
    anew=[x['projection']['values'] for x in materialized]
    comparisons=equality_rows(v,anew)
    raw_comparisons=equality_rows([x['raw'] for x in old['processed'][:4]],[x['raw'] for x in materialized])
    exact=all(x['numeric_equal'] for x in comparisons)
    save(OUT/'materialization.json',dict(processed=materialized,comparison=comparisons,raw_comparison=raw_comparisons,resources=processing_costs,exact=exact,preregistration_sha256=sha(raw),receptor_calls=4,nj_calls=4))
    tracemalloc.stop();tracemalloc.start();memory_start=time.perf_counter_ns()
    for case in ('main','none','hints'):
        allout[case]={}
        for name,cls in [('R',ProvisionalHintArm),('P',PerceptionRecencyArm)]:
            a=cls(profile,f'{case}/{name}');m=Meter();m.files.add(str((ROOT/'tools/_s2uc_perception_recency.py').resolve()));receipts=[];states=[];queries=[];ordinal=1;assert not getattr(a,'_observation_end',{})
            mark_peak=0;mark_bytes_peak=0
            def submit(label,seg):
                nonlocal ordinal,mark_peak,mark_bytes_peak
                for x in (anew if seg=='A-3' else data[label]):m.call(a,'form',tu.Frame(tuple(x),profile,a.owner,seg,ordinal));ordinal+=1
                receipts.append(m.call(a,'close_segment',seg));states.append(dict(state=state(a),provenance=provenance(a),watermarks=dict(getattr(a,'_observation_end',{}))))
                marks=getattr(a,'_observation_end',{});mark_peak=max(mark_peak,len(marks));mark_bytes_peak=max(mark_bytes_peak,sys.getsizeof(marks)+sum(sys.getsizeof(k)+sys.getsizeof(v) for k,v in marks.items()));assert len(marks)<=2
            def query(label,pair):
                before=state(a);watermark=dict(getattr(a,'_observation_end',{}));qord=10000+len(queries)*2;m.hint_positions+=6
                assert m.call(a,'hint',tu.Frame(tuple(pair[0]),profile,a.owner,label,qord)) is None
                res=m.call(a,'hint',tu.Frame(tuple(pair[1]),profile,a.owner,label,qord+1));assert state(a)==before and dict(getattr(a,'_observation_end',{}))==watermark
                sources=a._retained_many;expected=[]
                for t in sources:
                    for o in range(3):
                        if t.frames[o].values==tuple(pair[0]) and t.frames[o+1].values==tuple(pair[1]):expected.append(dict(role='retained',generation=t.generation,formation=t.frames[0].segment,ordinals=[f.ordinal for f in t.frames],offset=o))
                assert res['matches']==expected;queries.append(dict(label=label,result=res,state_unchanged=True,watermarks_before=watermark,watermarks_after=dict(getattr(a,'_observation_end',{}))));return res
            for label,seg in [('A','A-1'),('A','A-2'),('D','D-1'),('D','D-2')]:submit(label,seg)
            for label,pair in [('HA',v[:2]),('HD',[v[3],v[1]]),('HBC',v[1:3])]:query('before-'+label,pair)
            originalA=a._retained_many[0];originalD=a._retained_many[1]
            if case=='main':
                candidate_before=a._candidate
                submit('A','A-3');assert any(t is originalA for t in a._retained_many)
                if exact:
                    assert a._candidate is candidate_before
                    assert a.inventory==((2,1) if name=='P' else (1,2))
                else:assert receipts[-1]['action']!='TRACE_CONFIRMED_RECENT'
            elif case=='hints':
                query('intervening-1',v[:2]);query('intervening-2',v[:2]);assert a.inventory==(1,2)
            submit('Z','Z-1');submit('Z','Z-2')
            prediction='CONFIRMED' if list(a.inventory)==p['predicted'][case][name] else 'VIOLATED'
            keepA=case=='main' and name=='P' and exact
            survivor=originalA if keepA else originalD;assert any(t is survivor for t in a._retained_many)
            for label,pair,want in [('HA',v[:2],[1] if keepA else []),('HD',[v[3],v[1]],[] if keepA else [2]),('HBC',v[1:3],[1] if keepA else [2])]:
                res=query('after-'+label,pair);assert [d['generation'] for d in res['matches']]==want
            assert m.peak_trace<=16 and m.peak_hint<=2 and m.peak_total<=18
            allout[case][name]=dict(receipts=receipts,states=states,queries=queries,meter=m.summary(),original_survivor_object_preserved=True,prediction=prediction,watermark_peak_count=mark_peak,watermark_python_bytes_peak=mark_bytes_peak if name=='P' else 0)
            a.close_owner();assert all(x==0 for x in a.resources().values()) and not getattr(a,'_observation_end',{})
            allout[case][name]['watermarks_reset_on_close']=True
    current,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
    assert all(sha((ROOT/f).read_bytes())==h for f,h in p['bindings'].items())
    r=dict(scope=p['scope'],preregistration_sha256=sha(raw),cases=allout,bindings_unchanged=True,receptor_calls=4,nj_calls=4,exact_A3=exact,processing_resources=processing_costs,memory_elapsed_ns=time.perf_counter_ns()-memory_start,resources=dict(elapsed_ns=time.perf_counter_ns()-start,python_peak_bytes=peak,python_current_bytes=current),query_count=sum(len(a['queries']) for c in allout.values() for a in c.values()))
    save(OUT/'result.json',r);print('Completed',r['query_count'],'queries',r['resources'])
if __name__=='__main__':
    if sys.argv[1:]==['register']:register()
    elif sys.argv[1:]==['run']:run()
