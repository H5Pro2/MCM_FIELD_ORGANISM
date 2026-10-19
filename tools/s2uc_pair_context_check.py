"""Bound causal adapter counterprobe; existing vectors only."""
import json,sys,time,tracemalloc,dataclasses
from pathlib import Path
from tools.s2uc_pcm_temporal_check import ROOT,sha,save
from tools._s2uc_pair_context_adapter import PairContextAdapter,PerceptionSample
from tools._s2uc_factor_recency import FactorRecencyArm
from tools._s2tu_retained_trace import Frame
from tools.s2uc_k2_check import state,provenance
from tools.s2uc_factor_recency_check import oracle
OUT=ROOT/'reports/s2uc/pair-context-20260930-01'
OLD=ROOT/'reports/s2uc/pcm-temporal-20260930-01'

def snap(a):return dict(state=state(a),provenance=provenance(a),marks=dict(a._observation_end))
def register():
    folder=ROOT/'reports/s2uc/factor-recency-20260930-01';p=json.loads((folder/'preregistration.json').read_text());bindings=dict(p['bindings'])
    for f,h in bindings.items():assert sha((ROOT/f).read_bytes())==h
    for f in ('tools/_s2uc_pair_context_adapter.py','tools/s2uc_pair_context_check.py','tests/test_s2uc_pair_context_adapter.py','docs/S2UC_WAHRNEHMUNG_HINWEIS_INNERKONTEXT_VERTRAG_20260930.txt'):
        bindings[f]=sha((ROOT/f).read_bytes())
    OUT.mkdir(exist_ok=False)
    save(OUT/'preregistration.json',dict(bindings=bindings,predictions={'candidate':'PROVISIONAL_CANDIDATE_MATCH','retained_half':'CONFIRMED_RETAINED_MATCH','ambiguous':'ABSTAIN_AMBIGUOUS','empty':'ABSTAIN_NO_MATCH'},rules=['pairs 1/2,3/4 without selection','hint before both original frame admissions','same state as admission-only reference at every completed pair','residual admitted once then incomplete formation discarded','receipts no payload references','16+2 including transient frames'],runtime=sys.version,created_ns=time.time_ns()))
class Observer:
    def __init__(self):self.frames=0;self.payloads=0;self.frame_refs=0;self.object_bytes=0;self.samples=0
    def trace(self,frame,event,arg):
        name=Path(frame.f_code.co_filename).name
        if name not in ('_s2uc_pair_context_adapter.py','_s2uc_factor_recency.py','_s2uc_perception_recency.py','_s2uc_factor_hint.py','_s2uc_four_arm.py','_s2uc_provisional_hint.py','_s2ub_candidate_confirmation.py'):return None
        seen=set();frames=set();payloads=set();refs=0;size=0
        def visit(x):
            nonlocal refs,size
            if isinstance(x,Frame):refs+=1
            if id(x) in seen:return
            seen.add(id(x));size+=sys.getsizeof(x)
            if isinstance(x,Frame):frames.add(id(x));payloads.add(id(x.values))
            if isinstance(x,dict):
                for k,v in x.items():visit(k);visit(v)
            elif isinstance(x,(tuple,list)):
                for v in x:visit(v)
            elif dataclasses.is_dataclass(x) and not isinstance(x,type):
                for f in dataclasses.fields(x):visit(getattr(x,f.name))
            elif isinstance(x,(FactorRecencyArm,PairContextAdapter)):visit(vars(x))
        cursor=frame
        while cursor:
            if Path(cursor.f_code.co_filename).name in ('_s2uc_pair_context_adapter.py','_s2uc_perception_recency.py','_s2uc_factor_hint.py','_s2uc_four_arm.py','_s2uc_provisional_hint.py','_s2ub_candidate_confirmation.py'):
                for x in cursor.f_locals.values():visit(x)
            cursor=cursor.f_back
        self.frames=max(self.frames,len(frames));self.payloads=max(self.payloads,len(payloads));self.frame_refs=max(self.frame_refs,refs);self.object_bytes=max(self.object_bytes,size);self.samples+=1
        assert len(frames)<=18
        return self.trace

def run():
    raw=(OUT/'preregistration.json').read_bytes();p=json.loads(raw);assert all(sha((ROOT/f).read_bytes())==h for f,h in p['bindings'].items())
    old=json.loads((OLD/'result.json').read_text());v=[d['projection']['values'] for d in old['processed'][:4]];profile=old['processed'][0]['projection']['profile_digest'];A=v;D=[v[3],v[1],v[2],v[0]];Z=list(reversed(v));half=[[x*.5 for x in row] for row in v]
    scenarios={'candidate':([A],A[:2]),'retained_half':([A,A],half[:2]),'ambiguous':([A,A,D,D],v[1:3]+v[:2]),'empty':([],v[:2]),'full':([A,A,D,D,Z],A)}
    tracemalloc.start();start=time.perf_counter_ns();results={}
    for label,(seeds,inputs) in scenarios.items():
        arm=FactorRecencyArm(profile,label);ref=FactorRecencyArm(profile,label);ordinal=1
        for k,values in enumerate(seeds):
            for a in (arm,ref):
                for j,x in enumerate(values):a.form(Frame(tuple(x),profile,label,f'seed{k}',ordinal+j))
                a.close_segment(f'seed{k}')
            ordinal+=4
        adapter=PairContextAdapter(arm,'stream',first_ordinal=ordinal);obs=Observer();receipts=[];checks=[];originals=[];pending=[]
        for i,x in enumerate(inputs,1):
            sample=PerceptionSample(tuple(x),profile,label,'stream',i,(i-1)*4800,i*4800);originals.append(sample.values);pending.append(sample)
            before=snap(ref)
            expected=oracle(ref,[s.values for s in pending],True) if len(pending)==2 else None
            sys.settrace(obs.trace)
            try:receipt=adapter.accept_perception(sample)
            finally:sys.settrace(None)
            if i%2:
                assert receipt is None and snap(arm)==before
            else:
                data=json.loads(receipt.json_text);assert data['matches']==expected
                assert data['input_indices']==[i-1,i] and data['read_revision']==((i-2)+(i-2)//4)
                assert len(receipt.json_text.encode())<=16384
                if label in p['predictions'] and i==2:assert data['status']==p['predictions'][label]
                for s in pending:
                    f=Frame(s.values,profile,label,f'p{(s.index-1)//4+1}',ordinal+s.index-1);ref.form(f)
                    if s.index%4==0:ref.close_segment(f.segment)
                pending.clear();assert snap(arm)==snap(ref)
                assert adapter.accepted==adapter.admitted==i
                assert not adapter.pair and not adapter.intervals and not arm._hints
                receipts.append(data);checks.append(snap(arm))
        # No adapter-side receipt history or source archive.
        assert set(vars(adapter))=={'arm','stream','hop','window','start_sample','first_ordinal','next_index','pair','intervals','closed','revision','accepted','admitted','discarded_on_error'}
        before_close=snap(arm);adapter.finish_story();ref.close_owner();assert snap(arm)==snap(ref) and not arm._observation_end
        results[label]=dict(receipts=receipts,pair_states=checks,before_close=before_close,accepted=adapter.accepted,admitted=adapter.admitted,resources=vars(obs),reset=True,max_receipt_bytes=max(len(json.dumps(x,separators=(',',':')).encode()) for x in receipts))
    _,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
    assert all(sha((ROOT/f).read_bytes())==h for f,h in p['bindings'].items())
    save(OUT/'result.json',dict(scenarios=results,bindings_unchanged=True,preregistration_sha256=sha(raw),pcm_calls=0,resources=dict(elapsed_ns=time.perf_counter_ns()-start,python_peak_bytes=peak)))
    print({k:dict(status=v['receipts'][0]['status'],accepted=v['accepted'],resources=v['resources']) for k,v in results.items()})
if __name__=='__main__':
    if sys.argv[1:]==['register']:register()
    elif sys.argv[1:]==['run']:run()
