"""Bound local sampled-observation comparison. No source decoding or NJ calls."""
import dataclasses
import hashlib
import json
import math
from pathlib import Path
import sys
import time
import tracemalloc
from collections import Counter
from tools._s2uc_continuation_adapter import ContinuationAdapter, consume_prediction
from tools._s2uc_pair_context_adapter import PairContextAdapter, PerceptionSample, AdapterError
from tools._s2uc_factor_recency import FactorRecencyArm
from tools.s2uc_context_prediction_check import BudgetObserver

ROOT = Path(__file__).resolve().parents[1]
BINDING = 'docs/S2UC_FORTLAUFENDER_VERGLEICH_BESTAND_20260930.json'
BINDING_SHA = 'e86b581c53971a9ff38bee5d55b3d7894a9b6ae0b45fb49b2bfbc881c5b4d537'
PROFILE = '55f1de8602c945749728ce17c74cdff8320d1b5fc72c800f239bc86737db1a1e'
TARGETS = list(range(3, 20, 2))

def need(ok, message):
    if not ok:
        raise AdapterError(message)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def state(arm):
    # Include every state field, including formation/hint end markers and watermarks.
    def convert(x):
        if dataclasses.is_dataclass(x):
            return {f.name: convert(getattr(x, f.name)) for f in dataclasses.fields(x)}
        if isinstance(x, dict):
            return {str(k): convert(v) for k, v in x.items()}
        if isinstance(x, (tuple, list)):
            return [convert(v) for v in x]
        return x
    return convert(vars(arm))

class BoundSource:
    """Observer-owned file cache. Predictor never receives this object or its root."""
    def __init__(self, root=ROOT):
        self.root = Path(root).resolve()
        raw = (self.root / BINDING).read_bytes()
        need(digest(raw) == BINDING_SHA, 'MANIFEST_BINDING_INVALID')
        self.manifest = json.loads(raw)
        self.cache = {}
        self.bytes_read = len(raw)
        self.pulls = 0
        self.log = []
        self.closed = False
        for item in self.manifest['files']:
            p = (self.root / item['path']).resolve()
            need(p.is_relative_to(self.root), 'PATH_OUTSIDE_PROJECT')
            data = p.read_bytes()
            need(len(data) == item['bytes'] and digest(data) == item['sha256'], 'FILE_BINDING_INVALID:' + item['path'])
            self.cache[item['path']] = data
            self.bytes_read += len(data)
        self.cached_bytes = sum(map(len, self.cache.values()))
        record = json.loads(self.cache[self.manifest['selected_record']])['value']
        core = self.resolve(record['core'])
        # resolve core shallowly: payload objects remain opaque until a permitted take.
        self.entries = self.resolve(core['inputs'])
        need(len(self.entries) == 20, 'INPUT_COUNT_INVALID')
        self.positions = self.manifest['positions']

    def resolve(self, obj):
        if isinstance(obj, dict) and '$media_object' in obj:
            name = 'reports/media-restart-real-20260913-03/objects/' + obj['$media_object'] + '.json'
            need(name in self.cache, 'UNBOUND_OBJECT')
            return json.loads(self.cache[name])['value']
        return obj

    def expand(self, obj):
        value = self.resolve(obj)
        if value is not obj:
            return self.expand(value)
        if isinstance(value, dict):
            return {k: self.expand(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self.expand(v) for v in value]
        return value

    def take(self, adapter):
        try:
            need(not self.closed and not adapter.closed, 'SOURCE_CLOSED')
            i = self.pulls + 1
            if i > 20:
                raise StopIteration
            need(adapter.next_index == i, 'PULL_ORDER_INVALID')
            if i in TARGETS:
                p = adapter.pending_prediction
                need(p is not None and p.target_index == i, 'FUTURE_BEFORE_PREDICTION')
                provenance = json.loads(p.provenance_json)
                need(provenance['input_indices'] == [i-2, i-1], 'PREDICTION_PAIR_INVALID')
                self.log.append(dict(target=i, prediction_bound=True, read_revision=p.read_revision,
                                     status=p.status, provenance_sha256=digest(p.provenance_json.encode())))
            # Only now parse this event's payload. No future values passed to adapter.
            item = self.expand(self.entries[i-1])
            need(item['event']['ordinal'] == i, 'EVENT_ORDER_INVALID')
            frames = [t['frame'] for t in item['field']['timed_frames'] if t['frame']['modality_id'] == 'auditory']
            need(len(frames) == 1, 'AUDITORY_COUNT_INVALID')
            f = frames[0]; pos = self.positions[i-1]
            need(f['geometry_id'] == self.manifest['geometry'], 'GEOMETRY_INVALID')
            need((f['window_start_tick'], f['window_end_tick']) == (9600*(i-1), 9600*(i-1)+4800), 'RUNTIME_TIME_INVALID')
            need((pos['source_start_sample'], pos['source_end_sample']) == (67200*(i-1), 67200*(i-1)+4800), 'SOURCE_TIME_INVALID')
            need(f['snapshot_id'] == pos['snapshot_id'], 'SNAPSHOT_INVALID')
            values = tuple(f['values'])
            need(len(values) == 48 and all(type(v) is float and math.isfinite(v) for v in values), 'VALUES_INVALID')
            self.pulls = i
            return PerceptionSample(values, PROFILE, 'owner', 'stream', i, pos['source_start_sample'], pos['source_end_sample'])
        except StopIteration:
            raise
        except Exception:
            self.close(); adapter._terminate(); raise

    def close(self):
        self.cache.clear(); self.entries = []; self.closed = True

def summarize(rows):
    result = {}
    for method in ('context', 'persistence'):
        counts = Counter(r['score'][method] for r in rows)
        covered = counts['HIT'] + counts['MISS']
        result[method] = dict(counts= dict(counts), covered=covered, total=len(rows),
                              coverage=covered/len(rows), accuracy_when_covered=counts['HIT']/covered if covered else None,
                              hit_fraction=counts['HIT']/len(rows))
    result['abstention_reasons'] = dict(Counter(r['prediction_status'] for r in rows if not r['score']['context_covered']))
    result['joint'] = {k: [] for k in ('both_hit','context_only_hit','persistence_only_hit','both_miss')}
    result['covered_by_role'] = dict(Counter(r['prediction_status'] for r in rows if r['score']['context_covered']))
    for r in rows:
        if r['score']['context_covered']:
            a,b = r['score']['context']=='HIT',r['score']['persistence']=='HIT'
            k = 'both_hit' if a and b else 'context_only_hit' if a else 'persistence_only_hit' if b else 'both_miss'
            result['joint'][k].append(r['target'])
    return result

def run_comparison(root=ROOT):
    tracemalloc.start(); started = time.perf_counter_ns()
    source = None
    a = ContinuationAdapter(FactorRecencyArm(PROFILE, 'owner'), 'stream', hop=67200)
    b = PairContextAdapter(FactorRecencyArm(PROFILE, 'owner'), 'stream', hop=67200)
    budget = BudgetObserver()
    receipts=[]; rows=[]; states=[]; admitted=[]; pre_admission=[]
    original_admit = a._admit
    def admit(frame):
        p = a.pending_prediction
        need(p is not None and p.target_index == ((frame.ordinal+1)//2)*2+1, 'PREDICTION_NOT_BOUND_BEFORE_ADMISSION')
        pre_admission.append(dict(ordinal=frame.ordinal,target=p.target_index,read_revision=p.read_revision))
        admitted.append(frame.ordinal); original_admit(frame)
    a._admit = admit
    def observed(fn, *args):
        sys.settrace(budget.trace)
        try: return fn(*args)
        finally: sys.settrace(None)
    try:
        source=BoundSource(root)
        reader_peak=tracemalloc.get_traced_memory()[1]
        for _ in range(20):
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
        need(a.pending_prediction.target_index==21,'TERMINAL_TARGET_INVALID')
        terminal=dict(target=21,status='NOT_EVALUABLE_END',prediction_status=a.pending_prediction.status)
        observed(a.finish_story); b.finish_story()
        need(state(a.arm)==state(b.arm),'FINAL_STATE_MISMATCH')
        need(a.pending_prediction is None and a.closed and a.accepted==a.admitted==20,'FINAL_INVALID')
        need(admitted==list(range(1,21)) and [r['target'] for r in rows]==TARGETS,'COVERAGE_INVALID')
        need([x['target'] for x in source.log]==TARGETS and len(receipts)==10,'RECEIPTS_INVALID')
        resources=dict(predictor=vars(budget),reader_cached_bytes=source.cached_bytes,reader_bytes_read=source.bytes_read,
                       reader_initialization_python_peak_bytes=reader_peak, observer_state_snapshots=len(states),
                       whole_instrumented_python_peak_bytes=tracemalloc.get_traced_memory()[1],elapsed_ns=time.perf_counter_ns()-started,
                       scope='Python traced allocations, reader/observer/reference included; not process RSS',
                       logical_budget='16 memory + 2 pair/hint + 2 separate output slots')
        result=dict(status='LOCAL_COMPARISON_COMPLETE',historical_status='NOT_EVALUABLE',source_positions=source.positions,
                    pair_receipts=receipts,target_evaluations=rows,terminal=terminal,counts=summarize(rows),pull_log=source.log,
                    pre_admission_checks=pre_admission,admitted_ordinals=admitted,states=states,final_state=state(a.arm),
                    slots_released=True,resources=resources,binding_sha256=BINDING_SHA,source_processing_calls=0)
        resources['observer_result_json_bytes']=len(json.dumps(result).encode())
        return result
    finally:
        sys.settrace(None)
        if not a.closed: a._terminate()
        if not b.closed: b._terminate()
        if source is not None: source.close()
        tracemalloc.stop()

if __name__ == '__main__':
    out=ROOT/'reports/s2uc/continuous-comparison-20260930-01'
    out.mkdir(exist_ok=False)
    try:
        result=run_comparison()
        (out/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result['counts']))
    except Exception as exc:
        (out/'failure.json').write_text(json.dumps({'error':str(exc)}),encoding='utf-8')
        raise
