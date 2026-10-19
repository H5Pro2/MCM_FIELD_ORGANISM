"""Two directional primary paired-cluster contrasts; full secondary accounting."""
import hashlib
import math
from tools._s2uc_lz1_stats import quantile

def weights():
    result=[]
    for z in range(10000):
        row=[0]*32
        for k in range(32):
            i=int.from_bytes(hashlib.sha256(f'MCM-ULZ1/bootstrap/v1/z={z}/k={k}'.encode()).digest()[:8],'big')%32
            row[i]+=1
        result.append(bytes(row))
    return result

def interval(ds,ws,primary,indices=None):
    indices=list(range(32)) if indices is None else indices
    draws=[]
    for w in ws:
        total=sum(w[i] for i in indices)
        if not total:raise ValueError('EMPTY_BOOTSTRAP_ORIENTATION')
        draws.append(sum(w[i]*ds[i] for i in indices)/total)
    draws.sort()
    lo,hi=(.0125,.9875) if primary else (.025,.975)
    return [quantile(draws,lo),quantile(draws,hi)]

def verdict(ci,direction):
    if direction=='negative':return 'BELEGT' if ci[1]<0 else 'WIDERLEGT' if ci[0]>0 else 'NICHT_NACHGEWIESEN'
    return 'BELEGT' if ci[0]>0 else 'WIDERLEGT' if ci[1]<0 else 'NICHT_NACHGEWIESEN'

def aggregate(reports,plan,check=lambda:None):
    if len(reports)!=64 or [r['id'] for r in reports]!=[s['id'] for s in plan['cases']]:raise ValueError('ALL_64_CASES')
    for r,s in zip(reports,plan['cases'],strict=True):
        if (r['replicate'],r['condition'])!=(s['replicate'],s['condition']):raise ValueError('CLUSTER_IDENTITY')
        if not r['complete'] or [x['target'] for x in r['rows']]!=plan['masks']['G']:raise ValueError('COMPLETE_TARGETS')
        if any(not math.isfinite(x[a]) or x[a]<0 for x in r['rows'] for a in ('U','L')):raise ValueError('INVALID_ERROR')
        for m,ts in plan['masks'].items():
            for a in ('U','L'):
                if r['metrics'][m][a]!=sum(x[a] for x in r['rows'] if x['target'] in ts)/len(ts):raise ValueError('MASK_METRICS')
    ws=weights();contrasts=[];harms=[]
    for c in ('S','W'):
        rs=[r for r in reports if r['condition']==c]
        if [r['replicate'] for r in rs]!=list(range(1,33)):raise ValueError('CLUSTER_ORDER')
        for m,ts in plan['masks'].items():
            ds=[r['metrics'][m]['U']-r['metrics'][m]['L'] for r in rs]
            for orientation in ('ALL','E_A','E_B'):
                check()
                ids=[i for i in range(32) if orientation=='ALL' or i%2==(0 if orientation=='E_A' else 1)]
                primary=orientation=='ALL' and ((c,m)==('S','Y_33_128') or (c,m)==('W','Y_129_160'))
                direction='positive' if (c,m)==('W','Y_129_160') else 'negative'
                ci=interval(ds,ws,primary,ids)
                contrasts.append(dict(condition=c,mask=m,orientation=orientation,primary=primary,
                    direction=direction if primary else None,mean=sum(ds[i] for i in ids)/len(ids),
                    ci=ci,level=.975 if primary else .95,per_replicate=[ds[i] for i in ids],
                    verdict=verdict(ci,direction) if primary else 'EXPLORATIV'))
            diffs=[x['U']-x['L'] for r in rs for x in r['rows'] if x['target'] in ts]
            harms.append(dict(condition=c,mask=m,improved=sum(d<0 for d in diffs),worse=sum(d>0 for d in diffs),
                equal=sum(d==0 for d in diffs),gain_sum=-sum(d for d in diffs if d<0),harm_sum=sum(d for d in diffs if d>0),
                max_harm=max(0.,max(diffs)),worst_replicate_mean=max(ds)))
    primary=[x for x in contrasts if x['primary']]
    if len(primary)!=2:raise ValueError('TWO_PRIMARY')
    return dict(Technik='AUSWERTBAR',Abwaegung='BELEGT' if all(x['verdict']=='BELEGT' for x in primary) else
        'WIDERLEGT' if any(x['verdict']=='WIDERLEGT' for x in primary) else 'NICHT_NACHGEWIESEN',
        contrasts=contrasts,harms=harms,bootstrap=dict(draws=10000,clusters=32,
            weights_sha256=hashlib.sha256(b''.join(ws)).hexdigest()),general_MCM_claim=False)
