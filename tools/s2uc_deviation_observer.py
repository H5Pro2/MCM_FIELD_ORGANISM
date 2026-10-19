"""Observer-only arithmetic on stored records; stdlib, no memory/decoder imports."""
import csv,hashlib,json,math,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MATERIAL='reports/s2uc/nasa-contiguous-materialization-20260930-01'
COMPARISON='reports/s2uc/nasa-context-comparison-20260930-01'
OUT=ROOT/'reports/s2uc/nasa-deviation-observer-20260930-01'
METRICS=('mae','max_abs','mean_abs_x','mean_abs_y')
def need(ok,code):
    if not ok:raise ValueError(code)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def measures(x,y):
    need(len(x)==len(y) and len(x)>0,'DIMENSION')
    need(all(type(v) in (float,int) and math.isfinite(v) for v in (*x,*y)),'NONFINITE')
    errors=[abs(a-b) for a,b in zip(x,y)]
    return dict(n=len(x),mae=math.fsum(errors)/len(x),max_abs=max(errors),mean_abs_x=math.fsum(abs(v) for v in x)/len(x),mean_abs_y=math.fsum(abs(v) for v in y)/len(y))
def summarize(rows):
    return {key:dict(count=len(rows),minimum=min(r[key] for r in rows),median=statistics.median(r[key] for r in rows),mean=math.fsum(r[key] for r in rows)/len(rows),maximum=max(r[key] for r in rows)) for key in METRICS}
def check_frames(frames,vectors,segment=None):
    need(len(frames)==4,'FORMATION_LENGTH')
    for f in frames:
        need(f['ordinal'] in vectors and f['values']==vectors[f['ordinal']],'FRAME_PROVENANCE')
        if segment is not None:need(f['segment']==segment,'SEGMENT_PROVENANCE')
    return [v for f in frames for v in f['values']]
def analyze(record,vectors):
    targets=list(range(3,100,2));need([r['target'] for r in record['target_evaluations']]==targets,'TARGET_SET')
    persistence=[]
    for row in record['target_evaluations']:
        t=row['target'];pair=row['provenance']['input_indices'];need(pair==[t-2,t-1],'TARGET_PROVENANCE')
        need(row['score']['persistence']=='MISS','HISTORICAL_SCORE_CHANGED')
        persistence.append(dict(target=t,pair=pair,x_ordinals=[pair[-1]],y_ordinals=[t],read_revision=row['provenance']['read_revision'],**measures(vectors[pair[-1]],vectors[t])))
    states={r['index']:r['state'] for r in record['states']};need(set(states)==set(range(1,101)),'STATE_SET')
    forms=record['formation_receipts'];need(len(forms)==25,'FORMATION_SET');candidates=[]
    for j,row in enumerate(forms):
        end=(j+1)*4;event=row['result'];after=states[end]['_candidate']
        if j==0:
            need(event['action']=='TRACE_CANDIDATE_CREATED','INITIAL_CANDIDATE');continue
        need(event['action']=='TRACE_CANDIDATE_REPLACED','REPLACEMENT_EXPECTED')
        before=states[end-1]['_candidate'];need(before is not None and after is not None,'CANDIDATE_MISSING')
        need(before['candidate_generation']==event['evicted'] and after['candidate_generation']==event['candidate_generation'],'GENERATION_PROVENANCE')
        need([f['ordinal'] for f in after['frames']]==list(range(end-3,end+1)),'FOLLOWING_FORMATION')
        need([f['ordinal'] for f in before['frames']]==list(range(end-7,end-3)),'IMMEDIATE_PREDECESSOR')
        x=check_frames(before['frames'],vectors,forms[j-1]['segment']);y=check_frames(after['frames'],vectors,row['segment'])
        candidates.append(dict(candidate_generation=before['candidate_generation'],following_generation=after['candidate_generation'],candidate_segment=forms[j-1]['segment'],following_segment=row['segment'],state_before_index=end-1,formation_end=end,x_ordinals=[f['ordinal'] for f in before['frames']],y_ordinals=[f['ordinal'] for f in after['frames']],**measures(x,y)))
    need(len(candidates)==24,'CANDIDATE_COUNT')
    return dict(persistence=persistence,candidates=candidates,summary=dict(persistence=summarize(persistence),candidates=summarize(candidates)))
def register():
    OUT.mkdir(exist_ok=False)
    paths=[ROOT/'docs/S2UC_NASA_ABWEICHUNGSVERTRAG_20260930.txt',Path(__file__).resolve(),ROOT/'tests/test_s2uc_deviation_observer.py']
    for folder in (MATERIAL,COMPARISON):
        inv=ROOT/folder/'inventory.json';paths.append(inv)
        for item in json.loads(inv.read_text())['files']:
            p=ROOT/folder/item['path'];need(sha(p)==item['sha256'],'HISTORICAL_BINDING')
            paths.append(p)
    rows=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(set(paths))]
    (OUT/'preregistration.json').write_text(json.dumps(dict(formulas='MAE=fsum(abs(x-y))/N; MAX=max(abs(x-y)); MEAN_ABS_X/Y=fsum(abs(x/y))/N',persistence_targets=list(range(3,100,2)),candidate_transitions=24,threshold=None,files=rows),indent=2)+'\n')
def run():
    pre=json.loads((OUT/'preregistration.json').read_text())
    need(all(sha(ROOT/r['path'])==r['sha256'] for r in pre['files']),'PREBINDING_CHANGED')
    vectors={}
    for i in range(1,101):
        d=json.loads((ROOT/MATERIAL/f'window-{i:03d}.json').read_text());vectors[i]=d['projection']['values']
        need(d['index']==i and len(vectors[i])==48,'WINDOW_BINDING')
    record=json.loads((ROOT/COMPARISON/'result.json').read_text());result=analyze(record,vectors)
    need(all(sha(ROOT/r['path'])==r['sha256'] for r in pre['files']),'POSTBINDING_CHANGED')
    result.update(status='OBSERVER_ANALYSIS_COMPLETE',existing_files_unchanged=True,memory_runs=0,decoder_calls=0,preregistration_sha256=sha(OUT/'preregistration.json'))
    with (OUT/'result.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,allow_nan=False)
    for group in ('persistence','candidates'):
        rows=result[group]
        with (OUT/(group+'.csv')).open('x',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader()
            for row in rows:w.writerow({k:json.dumps(v) if isinstance(v,list) else v for k,v in row.items()})
    print(json.dumps(result['summary'],indent=2))
if __name__=='__main__':
    import sys
    if sys.argv[1:]==['register']:register()
    elif sys.argv[1:]==['run']:run()
    else:raise SystemExit('register or run')
