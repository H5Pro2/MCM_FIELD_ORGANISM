"""Paired triplet cluster bootstrap; Y is the only primary mask."""
import hashlib
import math
import statistics
from tools import _s2uc_lz1_sources as source

def weights():
    result=[]
    for z in range(1,10001):
        counts=[0]*32
        for k in range(1,33):
            i=int.from_bytes(hashlib.sha256(f'MCM-LZ1/uncertainty/v1/z={z}/k={k}'.encode()).digest()[:8],'big')%32
            counts[i]+=1
        result.append(bytes(counts))
    return result

def quantile(ordered,p):
    h=(len(ordered)-1)*p;a=math.floor(h);b=math.ceil(h)
    return ordered[a]+(ordered[b]-ordered[a])*(h-a)

def interval(vectors,bootstrap,primary):
    means=sorted(sum(w*x for w,x in zip(row,vectors,strict=True))/32 for row in bootstrap)
    lo,hi=(.00625,.99375) if primary else (.025,.975)
    return [quantile(means,lo),quantile(means,hi)]

def aggregate(reports,plan,check=lambda:None):
    expected=[s['id'] for s in plan['cases']]
    if [r['id'] for r in reports]!=expected or len(reports)!=96:raise ValueError('ALL_96_CASES')
    for r,s in zip(reports,plan['cases'],strict=True):
        if (r['replicate'],r['condition'])!=(s['replicate'],s['condition']):raise ValueError('CLUSTER_IDENTITY')
        if not r['complete'] or [x['target'] for x in r['rows']]!=plan['masks']['G']:raise ValueError('COMPLETE_TARGETS')
        for mask,ts in plan['masks'].items():
            for arm in ('P','U','H64'):
                if r['metrics'][mask][arm]!=sum(x[arm] for x in r['rows'] if x['target'] in ts)/len(ts):raise ValueError('MASK_METRICS')
    bootstrap=weights();contrasts=[]
    for condition in ('S','W','N'):
        rs=[r for r in reports if r['condition']==condition]
        if [r['replicate'] for r in rs]!=list(range(1,33)):raise ValueError('CLUSTER_ORDER')
        for mask in plan['masks']:
            for left,right in (('H64','P'),('U','P'),('U','H64')):
                check()
                ds=[r['metrics'][mask][left]-r['metrics'][mask][right] for r in rs]
                primary=mask=='G_Y' and condition in ('S','W') and right=='P'
                ci=interval(ds,bootstrap,primary)
                contrasts.append(dict(condition=condition,mask=mask,contrast=left+'-'+right,
                    primary=primary,mean=sum(ds)/32,median=statistics.median(ds),sd=statistics.stdev(ds),
                    per_replicate=ds,ci=ci,level=.9875 if primary else .95,
                    verdict='BELEGT' if ci[1]<0 else 'NICHT_NACHGEWIESEN'))
    if sum(x['primary'] for x in contrasts)!=4:raise ValueError('FOUR_PRIMARY_Y')
    harms=[]
    for condition in ('S','W','N'):
        rs=[r for r in reports if r['condition']==condition]
        for right in ('P','H64'):
            for mask,ts in plan['masks'].items():
                ds=[x['U']-x[right] for r in rs for x in r['rows'] if x['target'] in ts]
                harms.append(dict(condition=condition,comparison='U-'+right,mask=mask,
                    improved=sum(x<0 for x in ds),worse=sum(x>0 for x in ds),equal=sum(x==0 for x in ds),
                    gain_sum=-sum(x for x in ds if x<0),harm_sum=sum(x for x in ds if x>0),max_harm=max(ds),
                    worst_replicate_mean=max(r['metrics'][mask]['U']-r['metrics'][mask][right] for r in rs)))
    return dict(Technik='AUSWERTBAR',primary_mask='G_Y',contrasts=contrasts,harms=harms,
        bootstrap=dict(draws=10000,clusters=32,paired_triplets=True,weights_sha256=hashlib.sha256(b''.join(bootstrap)).hexdigest()),
        interpretation='N null expectation applies to G_Y only. Skeleton gains alone are not information leakage.',
        known_synthetic_capacity_only=True,transfer_claim=False)
