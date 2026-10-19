"""Fixed temporal controls, observer only; reuse unchanged absolute measures."""
import json,csv,math,statistics,sys
from pathlib import Path
from tools.s2uc_deviation_observer import ROOT,MATERIAL,COMPARISON,measures,check_frames,need,sha,summarize
OUT=ROOT/'reports/s2uc/nasa-temporal-controls-20260930-01'
PREVIOUS='reports/s2uc/nasa-deviation-observer-20260930-01'
FRAME_TARGETS=list(range(53,100,2))
FORMATION_TARGETS=list(range(14,26))
def selection():
    return dict(frames=[dict(target=t,near=t-1,far=t-51) for t in FRAME_TARGETS],formations=[dict(target=j,near=j-1,far=j-13) for j in FORMATION_TARGETS])
def compare(target,near,far,values):
    a=measures(values[near],values[target]);b=measures(values[far],values[target])
    delta=b['mae']-a['mae']
    return dict(target=target,near_index=near,far_index=far,near=a,far=b,delta_mae_far_minus_near=delta,neighbor='smaller' if delta>0 else 'larger' if delta<0 else 'equal')
def summary(rows):
    ds=[r['delta_mae_far_minus_near'] for r in rows]
    return dict(count=len(rows),neighbor_counts={k:sum(r['neighbor']==k for r in rows) for k in ('smaller','equal','larger')},near=summarize([r['near'] for r in rows]),far=summarize([r['far'] for r in rows]),delta_mae=dict(minimum=min(ds),median=statistics.median(ds),mean=math.fsum(ds)/len(ds),maximum=max(ds)))
def formations_from_record(record,vectors):
    states={r['index']:r['state'] for r in record['states']};forms={}
    need(len(record['formation_receipts'])==25,'FORMATION_COUNT')
    for j,r in enumerate(record['formation_receipts'],1):
        c=states[4*j]['_candidate'];need(c is not None and c['candidate_generation']==r['result']['candidate_generation'],'GENERATION')
        need([f['ordinal'] for f in c['frames']]==list(range(4*j-3,4*j+1)),'FORMATION_ORDINALS')
        forms[j]=check_frames(c['frames'],vectors,r['segment'])
    return forms

def register():
    OUT.mkdir(exist_ok=False)
    paths=[Path(__file__).resolve(),ROOT/'tools/s2uc_deviation_observer.py',ROOT/'tests/test_s2uc_temporal_controls.py']
    for folder in (MATERIAL,COMPARISON,PREVIOUS):
        inv=ROOT/folder/'inventory.json';paths.append(inv)
        for row in json.loads(inv.read_text())['files']:
            p=ROOT/folder/row['path'];need(sha(p)==row['sha256'],'HISTORICAL_BINDING');paths.append(p)
    pre=dict(selection=selection(),formulas=dict(mae='fsum(abs(x-y))/N',max_abs='max(abs(x-y))',mean_abs_x='fsum(abs(x))/N',mean_abs_y='fsum(abs(y))/N',delta='MAE_far - MAE_near'),summary='Each metric: count,min,median,mean,max on matched target subset only; exact sign counts for delta',threshold=None,files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(set(paths))])
    (OUT/'preregistration.json').write_text(json.dumps(pre,indent=2)+'\n')
def run():
    pre=json.loads((OUT/'preregistration.json').read_text());need(pre['selection']==selection(),'SELECTION_CHANGED')
    need(all(sha(ROOT/r['path'])==r['sha256'] for r in pre['files']),'PREBINDING_CHANGED')
    vectors={i:json.loads((ROOT/MATERIAL/f'window-{i:03d}.json').read_text())['projection']['values'] for i in range(1,101)}
    record=json.loads((ROOT/COMPARISON/'result.json').read_text());forms=formations_from_record(record,vectors)
    rows={group:[compare(p['target'],p['near'],p['far'],data) for p in pre['selection'][group]] for group,data in [('frames',vectors),('formations',forms)]}
    previous=json.loads((ROOT/PREVIOUS/'result.json').read_text())
    for r in rows['frames']:
        old=next(p for p in previous['persistence'] if p['target']==r['target'])
        need(all(r['near'][k]==old[k] for k in r['near']),'PREVIOUS_NEAR_MISMATCH')
        r['source_ordinals']=dict(target=[r['target']],near=[r['near_index']],far=[r['far_index']])
    for r in rows['formations']:
        old=next(p for p in previous['candidates'] if p['formation_end']==4*r['target'])
        need(all(r['near'][k]==old[k] for k in r['near']),'PREVIOUS_FORMATION_MISMATCH')
        r['source_ordinals']={k:list(range(4*j-3,4*j+1)) for k,j in [('target',r['target']),('near',r['near_index']),('far',r['far_index'])]}
    need(all(sha(ROOT/r['path'])==r['sha256'] for r in pre['files']),'POSTBINDING_CHANGED')
    result=dict(status='OBSERVER_CONTROL_COMPLETE',groups=rows,summary={g:summary(r) for g,r in rows.items()},historical_files_unchanged=True,matched_subset_verified=True,memory_runs=0,decoder_calls=0,preregistration_sha256=sha(OUT/'preregistration.json'))
    with (OUT/'result.json').open('x') as f:json.dump(result,f,indent=2,allow_nan=False)
    for g,rs in rows.items():
        flat=[]
        for r in rs:
            v={k:r[k] for k in ('target','near_index','far_index','delta_mae_far_minus_near','neighbor')}
            for arm in ('near','far'):
                v.update({arm+'_'+k:x for k,x in r[arm].items()})
            v.update({k+'_ordinals':json.dumps(x) for k,x in r['source_ordinals'].items()});flat.append(v)
        with (OUT/(g+'.csv')).open('x',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
    print(json.dumps(result['summary'],indent=2))
if __name__=='__main__':
    if sys.argv[1:]==['register']:register()
    elif sys.argv[1:]==['run']:run()
