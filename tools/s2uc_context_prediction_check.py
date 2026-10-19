"""Five preregistered causal next-frame contrasts, observer separated."""
import json,sys,time,tracemalloc,dataclasses
from pathlib import Path
from tools.s2uc_pcm_temporal_check import ROOT,sha,save
from tools._s2uc_continuation_adapter import ContinuationAdapter,consume_prediction
from tools._s2uc_pair_context_adapter import PairContextAdapter,PerceptionSample
from tools._s2uc_factor_recency import FactorRecencyArm
from tools._s2tu_retained_trace import Frame
from tools.s2uc_pair_context_check import snap
OUT=ROOT/'reports/s2uc/context-prediction-20260930-03'
OLD=ROOT/'reports/s2uc/pcm-temporal-20260930-01'
CASES={'K1':dict(seed=['A','A'],inputs=[0,1,2],expected=['HIT','MISS']), 'K2':dict(seed=['A','A'],inputs=[0,1,1],expected=['MISS','HIT']), 'K3':dict(seed=[],inputs=[0,1,1],expected=['ABSTAIN','HIT']), 'K4':dict(seed=['A','A','D','D'],inputs=[1,2,3],expected=['AMBIGUOUS','MISS']), 'K5':dict(seed=['A','A'],inputs=[2,3,0],expected=['ABSTAIN','MISS'])}

def register():
    p=json.loads((ROOT/'reports/s2uc/pair-context-20260930-01/preregistration.json').read_text());bindings=dict(p['bindings'])
    for f,h in bindings.items():assert sha((ROOT/f).read_bytes())==h
    for f in ('tools/_s2uc_continuation_adapter.py','tools/s2uc_context_prediction_check.py','tests/test_s2uc_continuation_adapter.py','docs/S2UC_KONTEXT_FORTSETZUNG_VERGLEICHSVERTRAG_20260930.txt'):
        bindings[f]=sha((ROOT/f).read_bytes())
    OUT.mkdir(exist_ok=False);save(OUT/'preregistration.json',dict(bindings=bindings,cases=CASES,criteria=['prediction before admission, third pull only after pending','K1/K2 identical predictions','no tolerance or correction','state equals old adapter after each input','2 output vectors outside16+2','negative findings remain reported'],scope='CONTROLLED_NEXT_FRAME_PREDICTION_NOT_PERCEPTION_IMPROVEMENT',runtime=sys.version,created_ns=time.time_ns()))

class GatedSource:
    """Owned solely by observer. Predictor receives one sample per call."""
    def __init__(self,values):self._iterator=iter(values);self.pulls=0;self.log=[]
    def take(self,predictor):
        if self.pulls==2:
            if predictor.pending_prediction is None:raise RuntimeError('FUTURE_BEFORE_PREDICTION')
            self.log.append(dict(event='THIRD_PULL',prediction_bound=True,target=predictor.pending_prediction.target_index))
        x=next(self._iterator);self.pulls+=1;return PerceptionSample(x,predictor.arm.profile,'owner','stream',self.pulls,(self.pulls-1)*4800,self.pulls*4800)

class BudgetObserver:
    def __init__(self):self.frame_peak=0;self.output_slots_peak=0;self.combined_peak=0;self.output_python_bytes_peak=0;self.samples=0
    def trace(self,frame,event,arg):
        names={'_s2uc_continuation_adapter.py','_s2uc_pair_context_adapter.py','_s2uc_factor_hint.py','_s2uc_perception_recency.py','_s2uc_four_arm.py','_s2uc_provisional_hint.py','_s2ub_candidate_confirmation.py'}
        if Path(frame.f_code.co_filename).name not in names:return None
        seen=set();frames=set();outputs=[]
        def visit(x):
            if id(x) in seen:return
            seen.add(id(x))
            if isinstance(x,Frame):frames.add(id(x))
            if isinstance(x,ContinuationAdapter):
                if x.pending_prediction is not None:outputs.append(x.pending_prediction)
                visit(vars(x))
            elif isinstance(x,FactorRecencyArm):visit(vars(x))
            elif isinstance(x,dict):
                for v in x.values():visit(v)
            elif isinstance(x,(list,tuple)):
                for v in x:visit(v)
            elif dataclasses.is_dataclass(x) and not isinstance(x,type):
                for f in dataclasses.fields(x):visit(getattr(x,f.name))
        cursor=frame
        while cursor:
            if Path(cursor.f_code.co_filename).name in names:
                for x in cursor.f_locals.values():visit(x)
            cursor=cursor.f_back
        slots=max((1+(p.context_values is not None) for p in outputs),default=0)
        bytecost=max((sys.getsizeof(p)+sys.getsizeof(p.provenance_json)+sum(sys.getsizeof(v)+sum(sys.getsizeof(x) for x in v) for v in (p.context_values,p.persistence_values) if v is not None) for p in outputs),default=0)
        self.frame_peak=max(self.frame_peak,len(frames));self.output_slots_peak=max(self.output_slots_peak,slots);self.combined_peak=max(self.combined_peak,len(frames)+slots);self.output_python_bytes_peak=max(self.output_python_bytes_peak,bytecost);self.samples+=1
        assert len(frames)<=18 and slots<=2 and len(frames)+slots<=20
        return self.trace

def run():
    raw=(OUT/'preregistration.json').read_bytes();p=json.loads(raw);assert all(sha((ROOT/f).read_bytes())==h for f,h in p['bindings'].items())
    old=json.loads((OLD/'result.json').read_text());v=[tuple(d['projection']['values']) for d in old['processed'][:4]];profile=old['processed'][0]['projection']['profile_digest'];seed_values={'A':v,'D':[v[3],v[1],v[2],v[0]]};out={};predictions={}
    tracemalloc.start();started=time.perf_counter_ns()
    for key,spec in p['cases'].items():
        arm=FactorRecencyArm(profile,'owner');ref=FactorRecencyArm(profile,'owner');n=1
        for j,label in enumerate(spec['seed']):
            for a in (arm,ref):
                for k,x in enumerate(seed_values[label]):a.form(Frame(x,profile,'owner',f'seed{j}',n+k))
                a.close_segment(f'seed{j}')
            n+=4
        adapter=ContinuationAdapter(arm,'stream',first_ordinal=n);reference=PairContextAdapter(ref,'stream',first_ordinal=n);source=GatedSource(v[i] for i in spec['inputs']);observer=BudgetObserver();states=[]
        for _ in range(2):
            sample=source.take(adapter);sys.settrace(observer.trace)
            try:receipt=adapter.accept_perception(sample)
            finally:sys.settrace(None)
            rr=reference.accept_perception(sample);assert receipt==rr and snap(arm)==snap(ref);states.append(snap(arm))
        forecast=adapter.pending_prediction;assert forecast is not None and source.pulls==2
        predictions[key]=dataclasses.asdict(forecast)
        sample=source.take(adapter)
        sys.settrace(observer.trace)
        try:score=consume_prediction(adapter,sample)
        finally:sys.settrace(None)
        assert adapter.pending_prediction is None
        before=snap(arm);assert before==snap(ref)
        sys.settrace(observer.trace)
        try:adapter.accept_perception(sample)
        finally:sys.settrace(None)
        reference.accept_perception(sample);assert snap(arm)==snap(ref)
        states.append(snap(arm))
        sys.settrace(observer.trace)
        try:ar=adapter.finish_story()
        finally:sys.settrace(None)
        br=reference.finish_story();assert ar==br and snap(arm)==snap(ref) and adapter.pending_prediction is None
        assert adapter.accepted==adapter.admitted==3
        observed=[score['context'],score['persistence']]
        out[key]=dict(score=score,prediction_status=forecast.status,forecast=predictions[key],expectation=spec['expected'],prediction_check='CONFIRMED' if observed==spec['expected'] else 'VIOLATED',pull_log=source.log,state_checks=states,final_reset=snap(arm),resources=vars(observer),frames_admitted=3)
        del forecast
    assert predictions['K1']==predictions['K2']
    counts={}
    for arm in ('context','persistence'):
        vals=[d['score'][arm] for d in out.values()];counts[arm]={x:vals.count(x) for x in ('HIT','MISS','AMBIGUOUS','ABSTAIN')};covered=vals.count('HIT')+vals.count('MISS');counts[arm].update(covered=covered,total=5,coverage=covered/5,accuracy_when_covered=vals.count('HIT')/covered if covered else None)
    _,peak=tracemalloc.get_traced_memory();tracemalloc.stop();assert all(sha((ROOT/f).read_bytes())==h for f,h in p['bindings'].items())
    save(OUT/'result.json',dict(cases=out,counts=counts,prefix_equal=True,bindings_unchanged=True,pcm_calls=0,preregistration_sha256=sha(raw),resources=dict(elapsed_ns=time.perf_counter_ns()-started,python_peak_bytes=peak)))
    print(json.dumps(counts));print({k:d['resources'] for k,d in out.items()})
if __name__=='__main__':
    if sys.argv[1:]==['register']:register()
    elif sys.argv[1:]==['run']:run()
