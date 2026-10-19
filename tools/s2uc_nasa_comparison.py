"""Causal local comparison of the bound NASA materialization; no decoder imports."""
import json,math,sys,time,tracemalloc
from fractions import Fraction
from pathlib import Path
from collections import Counter
from tools.s2uc_continuous_comparison import need,digest,state,summarize
from tools._s2uc_continuation_adapter import ContinuationAdapter,consume_prediction
from tools._s2uc_pair_context_adapter import PairContextAdapter,PerceptionSample
from tools._s2uc_factor_recency import FactorRecencyArm
from tools.s2uc_context_prediction_check import BudgetObserver
ROOT=Path(__file__).resolve().parents[1]
CORPUS='reports/s2uc/nasa-contiguous-materialization-20260930-01'
BINDING_SHA='f675ebaffa330ef64a6f1689e0fcd23cba3e76263bcfc6cb23c70e71507f0baa'
PROFILE='4a56de2f630055816533ecb45cdef5662157993bc1192023d01cf29e92247c9f'
RAW_PROFILE='5c6b2b19281a44023497b435a96b1051905af4bbac493cae7e699ea1320392c7'
TARGETS=list(range(3,100,2))

def validate_window(d,i):
    o=d['origin'];p=d['projection']
    need(d['index']==o['index']==i,'WINDOW_ORDER')
    start=(i-1)*4800;end=i*4800
    need((o['start_sample'],o['end_sample'])==(start,end),'SOURCE_TIME')
    need((p['window_start_tick'],p['window_end_tick'],p['snapshot_index'])==(start,end,10*(i-1)),'PROJECTION_TIME')
    need(p['profile_digest']==PROFILE and p['source_profile_digest']==RAW_PROFILE,'PROFILE_CHANGED')
    need(p['geometry_id']=='auditory.log48.50-18000.w4800.h480.half.v1','GEOMETRY_CHANGED')
    need(p['clock_id']=='audio.sample','CLOCK_CHANGED')
    v=p['values'];need(len(v)==48 and all(type(x) is float and math.isfinite(x) and 0<=x<=1 for x in v),'VALUES_INVALID')
    payload=dict(p);h=payload.pop('projection_digest')
    need(digest(json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode())==h,'PROJECTION_DIGEST')
    cursor=start
    for f in o['decoder_fragments']:
        need(f['source_start']==cursor and type(f['samples']) is int and f['samples']>0,'FRAGMENT_GAP')
        tick=f['pts']*Fraction(*f['time_base'])*48000
        need(tick.denominator==1 and tick<=cursor,'FRAGMENT_PTS')
        cursor+=f['samples']
    need(cursor==end,'FRAGMENT_END')
    for h in (d['pcm_sha256'],p['source_state_digest'],p['source_values_digest']):
        need(type(h) is str and len(h)==64 and all(c in '0123456789abcdef' for c in h),'SOURCE_DIGEST_FORMAT')

class BoundSource:
    """Observer-only prevalidation/cache; predictor gets a single gated sample."""
    def __init__(self,root=ROOT):
        self.root=Path(root)/CORPUS;self.cache={};self.pulls=0;self.log=[];self.closed=False;self.positions=[];self.deliveries=0
        raw=(self.root/'inventory.json').read_bytes();need(digest(raw)==BINDING_SHA,'INVENTORY_BINDING')
        inv=json.loads(raw);self.bytes_read=len(raw)
        try:
            for row in inv['files']:
                need(Path(row['path']).name==row['path'],'INVENTORY_PATH')
                data=(self.root/row['path']).read_bytes()
                need(len(data)==row['bytes'] and digest(data)==row['sha256'],'FILE_BINDING:'+row['path'])
                need(row['path'] not in self.cache,'DUPLICATE_FILE')
                self.cache[row['path']]=data;self.bytes_read+=len(data)
            names={f'window-{i:03d}.json' for i in range(1,101)}
            need({p.name for p in self.root.glob('window-*.json')}==names,'WINDOW_SET')
            need({p for p in self.cache if p.startswith('window-')}==names,'BOUND_WINDOW_SET')
            c=json.loads(self.cache['closure.json']);need(c['status']=='MATERIALIZATION_COMPLETE' and c['windows']==100 and c['error'] is None,'CORPUS_INCOMPLETE')
            need(c['facts']['facts']['accepted']==480000 and c['facts']['facts']['closed'] and c['facts']['projection_calls']=={'nj':100,'receptor':100},'CORPUS_COUNTS')
            b=json.loads(self.cache['binding.json']);need(b['nj_profile_digest']==PROFILE and b['raw_profile_digest']==RAW_PROFILE,'BINDING_PROFILE')
            for i in range(1,101):
                d=json.loads(self.cache[f'window-{i:03d}.json']);validate_window(d,i)
                self.positions.append(dict(index=i,start_sample=(i-1)*4800,end_sample=i*4800,pcm_sha256=d['pcm_sha256'],projection_digest=d['projection']['projection_digest']))
            self.cached_bytes=sum(map(len,self.cache.values()))
        except BaseException:self.close();raise
    def take(self,adapter):
        try:
            need(not self.closed and not adapter.closed,'SOURCE_CLOSED')
            i=self.pulls+1
            if i>100:raise StopIteration
            need(adapter.next_index==i,'PULL_ORDER')
            if i in TARGETS:
                p=adapter.pending_prediction
                need(p is not None and p.target_index==i,'FUTURE_BEFORE_PREDICTION')
                need(json.loads(p.provenance_json)['input_indices']==[i-2,i-1],'PREDICTION_PAIR')
                self.log.append(dict(target=i,prediction_bound=True,read_revision=p.read_revision,status=p.status,provenance_sha256=digest(p.provenance_json.encode())))
            d=json.loads(self.cache[f'window-{i:03d}.json']);validate_window(d,i)
            self.pulls=i;self.deliveries+=1
            return PerceptionSample(tuple(d['projection']['values']),PROFILE,'owner','stream',i,(i-1)*4800,i*4800)
        except StopIteration:raise
        except BaseException:self.close();adapter._terminate();raise
    def close(self):self.cache.clear();self.closed=True


def run_comparison(root=ROOT):
    tracemalloc.start(); started = time.perf_counter_ns()
    source = None
    a = ContinuationAdapter(FactorRecencyArm(PROFILE, 'owner'), 'stream', hop=4800)
    b = PairContextAdapter(FactorRecencyArm(PROFILE, 'owner'), 'stream', hop=4800)
    budget = BudgetObserver()
    receipts=[]; rows=[]; states=[]; admitted=[]; pre_admission=[]; formations=[]
    original_admit = a._admit
    def admit(frame):
        p = a.pending_prediction
        need(p is not None and p.target_index == ((frame.ordinal+1)//2)*2+1, 'PREDICTION_NOT_BOUND_BEFORE_ADMISSION')
        pre_admission.append(dict(ordinal=frame.ordinal,target=p.target_index,read_revision=p.read_revision))
        admitted.append(frame.ordinal); original_admit(frame)
    a._admit = admit
    def formation_profile(frame,event,result):
        if event=='return' and frame.f_code.co_name=='close_segment' and Path(frame.f_code.co_filename).name=='_s2uc_perception_recency.py' and frame.f_locals.get('self') is a.arm:
            formations.append(dict(segment=frame.f_locals['segment'],result=dict(result)))
    def observed(fn, *args):
        sys.settrace(budget.trace);sys.setprofile(formation_profile)
        try: return fn(*args)
        finally: sys.settrace(None);sys.setprofile(None)
    try:
        source=BoundSource(root)
        reader_peak=tracemalloc.get_traced_memory()[1]
        for _ in range(100):
            sample=source.take(a)
            if a.pending_prediction is not None:
                status=a.pending_prediction.status
                provenance=json.loads(a.pending_prediction.provenance_json)
                score=observed(consume_prediction,a,sample)
                need(a.pending_prediction is None,'OUTPUT_NOT_RELEASED')
                rows.append(dict(target=sample.index,prediction_status=status,provenance=provenance,score=score))
            receipt=observed(a.accept_perception,sample)
            reference=b.accept_perception(sample)
            need(receipt==reference and state(a.arm)==state(b.arm),'REFERENCE_STATE_MISMATCH')
            if receipt is not None: receipts.append(json.loads(receipt.json_text))
            states.append(dict(index=sample.index,state=state(a.arm),reference_equal=True))
        need(a.pending_prediction.target_index==101,'TERMINAL_TARGET_INVALID')
        terminal=dict(target=101,status='NOT_EVALUABLE_END',prediction_status=a.pending_prediction.status)
        observed(a.finish_story); b.finish_story()
        need(state(a.arm)==state(b.arm),'FINAL_STATE_MISMATCH')
        need(a.pending_prediction is None and a.closed and a.accepted==a.admitted==100,'FINAL_INVALID')
        need(admitted==list(range(1,101)) and [r['target'] for r in rows]==TARGETS,'COVERAGE_INVALID')
        need([x['target'] for x in source.log]==TARGETS and len(receipts)==50,'RECEIPTS_INVALID')
        resources=dict(predictor=vars(budget),reader_cached_bytes=source.cached_bytes,reader_bytes_read=source.bytes_read,
                       reader_initialization_python_peak_bytes=reader_peak, observer_state_snapshots=len(states),
                       whole_instrumented_python_peak_bytes=tracemalloc.get_traced_memory()[1],elapsed_ns=time.perf_counter_ns()-started,
                       scope='Python traced allocations, reader/observer/reference included; not process RSS',
                       logical_budget='16 memory + 2 pair/hint + 2 separate output slots')
        result=dict(status='LOCAL_COMPARISON_COMPLETE',materialization_status='MATERIALIZATION_COMPLETE',source_positions=source.positions,
                    formation_receipts=formations,formation_counts=dict(Counter(x['result']['action'] for x in formations)),pair_receipts=receipts,target_evaluations=rows,terminal=terminal,counts=summarize(rows),pull_log=source.log,
                    pre_admission_checks=pre_admission,admitted_ordinals=admitted,states=states,final_state=state(a.arm),
                    slots_released=True,resources=resources,binding_sha256=BINDING_SHA,source_processing_calls=0)
        resources['observer_result_json_bytes']=len(json.dumps(result).encode())
        return result
    finally:
        sys.settrace(None);sys.setprofile(None)
        if not a.closed: a._terminate()
        if not b.closed: b._terminate()
        if source is not None: source.close()
        tracemalloc.stop()

if __name__ == '__main__':
    out=ROOT/'reports/s2uc/nasa-context-comparison-20260930-01'
    out.mkdir(exist_ok=False)
    try:
        result=run_comparison()
        (out/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result['counts']))
    except Exception as exc:
        (out/'failure.json').write_text(json.dumps({'error':str(exc)}),encoding='utf-8')
        raise
