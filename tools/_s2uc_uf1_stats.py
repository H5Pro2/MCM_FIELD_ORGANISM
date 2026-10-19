"""One UF1 primary contrast, rational paired estimates, independent checks."""
import hashlib
from fractions import Fraction as F
from math import lcm
from collections import Counter
from tools._s2uc_hx1_stats import interval

def matrix_bytes():
    return bytes(2*(int.from_bytes(hashlib.sha256(f'MCM-UF1/bootstrap/v1/z={z}/orientation={o}/k={k}'.encode()).digest()[:8],'big')%16)+o
        for z in range(10000) for o in range(2) for k in range(16))
def verify_matrix(data):
    if len(data)!=320000:raise ValueError('MATRIX_LENGTH')
    for at,actual in enumerate(data):
        z,pos=divmod(at,32);o,k=divmod(pos,16)
        text='MCM-UF1/bootstrap/v1/z='+str(z)+'/orientation='+str(o)+'/k='+str(k)
        expected=2*(int(hashlib.sha256(text.encode('ascii')).hexdigest()[:16],16)%16)+o
        if actual!=expected:raise ValueError('MATRIX_REFERENCE')
    return [list(data[i:i+32]) for i in range(0,len(data),32)]
def reference_ci(values,draws,orientation=None):
    den=lcm(*(v.denominator for v in values));xs=[]
    for row in draws:
        selected=row if orientation is None else row[16*orientation:16*(orientation+1)]
        total=0
        for i,n in Counter(selected).items():total+=n*values[i].numerator*(den//values[i].denominator)
        xs.append(total)
    xs.sort();ci=[]
    for num in (1,39):
        q,r=divmod(9999*num,40);ci.append(F(xs[q]*(40-r)+xs[q+1]*r,40*len(selected)*den))
    return ci
def checked_ci(values,draws,orientation=None):
    a=interval(values,draws,orientation=orientation);b=reference_ci(values,draws,orientation)
    if a!=b:raise ValueError('CI_REFERENCE')
    return list(map(str,a))
def verdict(ci):
    lo,hi=map(F,ci)
    return 'F_VORTEIL_BELEGT' if lo>0 else 'U_VORTEIL_GEGEN_F_BELEGT' if hi<0 else 'KEIN_EINDEUTIGER_UNTERSCHIED_NACHGEWIESEN'
def selected(rows,mask):
    return [r for r in rows if mask=='G_all' or mask=='S' and r['target']%4==1 or mask=='Q' and r['target']%4==3 or mask.startswith('Q_') and r.get('cue')==mask[-1]]
def sums(rows):
    delta=[F(r['U'])-F(r['F']) for r in rows]
    gain=sum((max(-d,0) for d in delta),F(0));harm=sum((max(d,0) for d in delta),F(0))
    if harm-gain!=sum(delta,F(0)):raise ValueError('NET_REFERENCE')
    return dict(count=len(rows),improved=sum(d<0 for d in delta),worse=sum(d>0 for d in delta),equal=sum(d==0 for d in delta),
        gain=str(gain),harm=str(harm),net=str(gain-harm),max_harm=str(max([F(0)]+delta)))
def aggregate(reports,data,check=lambda:None):
    draws=verify_matrix(data);by={(r['replicate'],r['condition']):r for r in reports}
    if len(reports)!=64 or set(by)!={(r,c) for r in range(1,33) for c in ('D','N')}:raise ValueError('COMPLETE_PAIRS')
    means={};diagnosis=[]
    for (r,c),report in by.items():
        check();rows=report['rows']
        if not report['complete'] or [x['target'] for x in rows]!=list(range(3,1024,2)):raise ValueError('COMPLETE_TARGETS')
        for mask in ('Q','G_all','S','Q_X','Q_Y'):
            ss=selected(rows,mask)
            if len(ss)!={'Q':256,'G_all':511,'S':255,'Q_X':128,'Q_Y':128}[mask]:raise ValueError('MASK_COUNT')
            for arm in ('U','F'):
                value=sum((F(x[arm]) for x in ss),F(0))/len(ss)
                n,d=0,1
                for row in reversed(ss):
                    rn,rd=row[arm].as_integer_ratio();f=F(n*rd+rn*d,d*rd);n,d=f.numerator,f.denominator
                if value!=F(n,d*len(ss)):raise ValueError('MEAN_REFERENCE')
                means[r,c,mask,arm]=value
        q=selected(rows,'Q')
        for field,labels in [('class',('V0','V1','V2','V3')),('F_class',('F0','F1','F2')),('F_known',(False,True)),('F_replaced',(False,True))]:
            partitions=[]
            for label in labels:
                ss=[x for x in q if x[field]==label];d=sums(ss);partitions.append(d)
                diagnosis.append(dict(replicate=r,condition=c,partition=field,label=label,**d))
            whole=sums(q)
            if sum(x['count'] for x in partitions)!=256:raise ValueError('PARTITION')
            for key in ('gain','harm'):
                if sum((F(x[key]) for x in partitions),F(0))!=F(whole[key]):raise ValueError('PARTITION_SUM')
    details=[]
    for c in ('D','N'):
        for mask in ('Q','G_all','S','Q_X','Q_Y'):
            vals=[means[r,c,mask,'U']-means[r,c,mask,'F'] for r in range(1,33)]
            for o in (None,0,1):
                check();rs=list(range(1,33)) if o is None else list(range(o+1,33,2))
                rows=[x for r in rs for x in selected(by[r,c]['rows'],mask)];d=sums(rows);mh=F(d['max_harm'])
                pos=[[r,x['target']] for r in rs for x in selected(by[r,c]['rows'],mask) if mh>0 and F(x['U'])-F(x['F'])==mh]
                details.append(dict(condition=c,mask=mask,orientation=o,means={a:str(sum((means[r,c,mask,a] for r in rs),F(0))/len(rs)) for a in ('U','F')},
                    pairs=[str(vals[r-1]) for r in rs],mean=str(sum((vals[r-1] for r in rs),F(0))/len(rs)),ci=checked_ci(vals,draws,o),
                    maximum_harm_targets=pos,worst_mean=str(max(vals[r-1] for r in rs)),**d))
    primary=details[0];ci=primary['ci']
    interaction=[means[r,'D','Q','U']-means[r,'D','Q','F']-means[r,'N','Q','U']+means[r,'N','Q','F'] for r in range(1,33)]
    return dict(primary=dict(name='D:U-F',mean=primary['mean'],pairs=primary['pairs'],ci=ci,verdict=verdict(ci)),verdict=verdict(ci),
        secondary=details,diagnosis=diagnosis,story_means=[dict(replicate=r,condition=c,mask=m,arm=a,mean=str(x)) for (r,c,m,a),x in sorted(means.items())],interaction=dict(mean=str(sum(interaction,F(0))/32),pairs=list(map(str,interaction)),ci=checked_ci(interaction,draws)),
        bootstrap_sha256=hashlib.sha256(data).hexdigest(),reference_equal=True,known_sources=False)
