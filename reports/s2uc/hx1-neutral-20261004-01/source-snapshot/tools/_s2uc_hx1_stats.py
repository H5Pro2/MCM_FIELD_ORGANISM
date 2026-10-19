"""Exact rational HX1 estimates; stratified paired cluster bootstrap."""
import hashlib
from fractions import Fraction as F
from collections import Counter
from math import lcm

def matrix():
    result=[]
    for z in range(10000):
        row=[]
        for o in (0,1):
            for k in range(16):
                u=int.from_bytes(hashlib.sha256(f'MCM-HX1/bootstrap/v1/z={z}/orientation={o}/k={k}'.encode()).digest()[:8],'big')
                row.append(2*(u%16)+o)
        result.append(row)
    return result

def quantile(xs,q):
    pos=(len(xs)-1)*q;i=pos.numerator//pos.denominator;part=pos-i
    return xs[i] if not part else xs[i]+part*(xs[i+1]-xs[i])

def interval(values,draws,primary=False,orientation=None):
    # Integer common denominator, exact and materially cheaper than Fraction per draw.
    denominator=lcm(*(v.denominator for v in values));nums=[int(v*denominator) for v in values]
    selected=draws if orientation is None else [row[16*orientation:16*(orientation+1)] for row in draws]
    count=len(selected[0]);samples=sorted(sum(nums[i] for i in row) for row in selected)
    low=F(1,120) if primary else F(1,40)
    return [quantile(samples,low)/(count*denominator),quantile(samples,1-low)/(count*denominator)]

def judgement(ci):
    return 'BELEGT' if ci[1]<0 else 'WIDERLEGT' if ci[0]>0 else 'NICHT_NACHGEWIESEN'

def primary(values,draws):
    out=[]
    for name,v in zip(('D:U-G','D:U-P','interaction'),values,strict=True):
        ci=interval(v,draws,True)
        out.append(dict(name=name,mean=str(sum(v,F(0))/32),pairs=list(map(str,v)),ci=list(map(str,ci)),verdict=judgement(ci)))
    verdicts=[x['verdict'] for x in out]
    verdict='HINWEISNUTZEN_BELEGT' if all(v=='BELEGT' for v in verdicts) else 'GEMEINSAME_ERWARTUNG_WIDERLEGT' if 'WIDERLEGT' in verdicts else 'HINWEISNUTZEN_NICHT_NACHGEWIESEN'
    return dict(primary=out,verdict=verdict)

def reference_primary(values,draws):
    """Independent integer-scaled resampling and rational endpoint interpolation."""
    result=[]
    for v in values:
        den=1
        for value in v: den=lcm(den,value.denominator)
        integers=[value.numerator*(den//value.denominator) for value in v]
        samples=[]
        for row in draws:
            freq=Counter(row);total=0
            for i,n in freq.items(): total+=integers[i]*n
            samples.append(total)
        samples.sort();ends=[]
        for numerator in (1,119):
            q,r=divmod((len(samples)-1)*numerator,120)
            val=samples[q]*120 if not r else (120-r)*samples[q]+r*samples[q+1]
            ends.append(F(val,120*32*den))
        result.append(ends)
    return result

def aggregate(reports,check=lambda:None):
    expected={(r,c) for r in range(1,33) for c in ('D','N')}
    by={(x['replicate'],x['condition']):x for x in reports}
    if len(reports)!=64 or set(by)!=expected: raise ValueError('COMPLETE_PAIRS_REQUIRED')
    means={};draws=matrix();all_details=[];diagnosis=[]
    for (r,c),report in by.items():
        if not report['complete'] or [x['target'] for x in report['rows']]!=list(range(3,1024,2)): raise ValueError('COMPLETE_TARGETS_REQUIRED')
        for mask in ('Q','G_all','S','Q_X','Q_Y'):
            rows=[x for x in report['rows'] if mask=='G_all' or mask=='S' and x['target']%4==1 or mask=='Q' and x['target']%4==3 or mask.startswith('Q_') and x.get('cue')==mask[-1]]
            size={'G_all':511,'Q':256,'S':255,'Q_X':128,'Q_Y':128}[mask]
            if len(rows)!=size: raise ValueError('MASK_COUNT')
            for arm in 'UGP':
                errors=[F(x[arm]) for x in rows]
                if any(e<0 for e in errors): raise ValueError('ERROR_RANGE')
                means[r,c,mask,arm]=sum(errors,F(0))/size
                # Independent reduction from each stored binary64 ratio, not the above errors.
                n,d=0,1
                for row in reversed(rows):
                    rn,rd=row[arm].as_integer_ratio();n=n*rd+rn*d;d*=rd
                    simplified=F(n,d);n,d=simplified.numerator,simplified.denominator
                if F(n,d*size)!=means[r,c,mask,arm]: raise ValueError('AGGREGATION_REFERENCE')
        for cls in ('V0','V1','V2','V3'):
            subset=[x for x in report['rows'] if x.get('class')==cls]
            for other in ('G','P'):
                ds=[F(x[other])-F(x['U']) for x in subset]
                diagnosis.append(dict(replicate=r,condition=c,classification=cls,comparison='U/'+other,count=len(subset),
                    gain=str(sum((max(x,0) for x in ds),F(0))),harm=str(sum((max(-x,0) for x in ds),F(0)))))
        if sum('class' in x for x in report['rows'])!=256: raise ValueError('DIAGNOSIS_PARTITION')
    pv=[[],[],[]]
    for r in range(1,33):
        d=means[r,'D','Q','U']-means[r,'D','Q','G'];n=means[r,'N','Q','U']-means[r,'N','Q','G']
        if means[r,'D','Q','G']!=means[r,'N','Q','G']: raise ValueError('GLOBAL_MEAN_EQUALITY')
        pv[0].append(d);pv[1].append(means[r,'D','Q','U']-means[r,'D','Q','P']);pv[2].append(d-n)
        if d-n!=means[r,'D','Q','U']-means[r,'N','Q','U']: raise ValueError('INTERACTION_IDENTITY')
    out=primary(pv,draws)
    if [[str(x) for x in ci] for ci in reference_primary(pv,draws)]!=[x['ci'] for x in out['primary']]: raise ValueError('STATS_REFERENCE')
    for c in ('D','N'):
        for mask in ('Q','G_all','S','Q_X','Q_Y'):
            for first,second in [('U','G'),('U','P'),('G','P')]:
                vals=[means[r,c,mask,first]-means[r,c,mask,second] for r in range(1,33)]
                for orient in (None,0,1):
                    check();rs=list(range(1,33)) if orient is None else list(range(orient+1,33,2))
                    selected=[x for r in rs for x in by[r,c]['rows'] if mask=='G_all' or mask=='S' and x['target']%4==1 or mask=='Q' and x['target']%4==3 or mask.startswith('Q_') and x.get('cue')==mask[-1]]
                    delta=[F(x[first])-F(x[second]) for x in selected];maxharm=max([F(0)]+delta)
                    maximum_targets=[]
                    if maxharm>0:
                        for rr in rs:
                            for row in by[rr,c]['rows']:
                                eligible=mask=='G_all' or mask=='S' and row['target']%4==1 or mask=='Q' and row['target']%4==3 or mask.startswith('Q_') and row.get('cue')==mask[-1]
                                if eligible and F(row[first])-F(row[second])==maxharm: maximum_targets.append([rr,row['target']])
                    all_details.append(dict(condition=c,mask=mask,comparison=first+'/'+second,orientation=orient,
                        count=len(delta),means={a:str(sum((means[r,c,mask,a] for r in rs),F(0))/len(rs)) for a in 'UGP'},
                        pairs=[str(vals[r-1]) for r in rs],ci=list(map(str,interval(vals,draws,False,orient))),
                        improved=sum(d<0 for d in delta),worse=sum(d>0 for d in delta),equal=sum(d==0 for d in delta),
                        gain=str(sum((max(-d,0) for d in delta),F(0))),harm=str(sum((max(d,0) for d in delta),F(0))),
                        max_harm=str(maxharm),maximum_harm_targets=maximum_targets,worst_mean=str(max(vals[r-1] for r in rs))))
    return out|dict(secondary=all_details,diagnosis=diagnosis,bootstrap_sha256=hashlib.sha256(bytes(i for row in draws for i in row)).hexdigest(),reference_equal=True)
