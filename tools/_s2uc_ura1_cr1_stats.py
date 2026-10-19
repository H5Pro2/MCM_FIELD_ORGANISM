"""CR1 exact statistics; one early-post-switch primary contrast."""
import hashlib
import math
from fractions import Fraction as F

WINDOWS={'Q_early_post':(129,160),'Q_pre':(97,128),'Q_late_post':(161,256),'Q_all_post':(129,256)}
MASKS=tuple(WINDOWS)+('Q','G_all','S','Q_X','Q_Y')
MATRIX_SHA='0b9fbf483e870adac01ded7d2d0d0a651a11474a4ac2e4fbae1c14e793d7d965'
GROUPS={'eligible':(0,1,2),'warm':('none','cold','mixed','warm'),
        'same_output':(False,True),'choice':('both_persistence','mixed','same_context','different_context')}


def quantile(values,q):
    values=sorted(values);h=(len(values)-1)*q;i=h.numerator//h.denominator
    return values[i] if i==len(values)-1 else values[i]+(h-i)*(values[i+1]-values[i])


def interval(values,data):
    if len(values)!=32 or len(data)!=320000:raise ValueError('BOOTSTRAP_SHAPE')
    den=math.lcm(*(x.denominator for x in values));ints=[x.numerator*(den//x.denominator) for x in values]
    totals=[]
    for start in range(0,len(data),32):
        row=data[start:start+32]
        if any(v>=32 or v%2!=int(i>=16) for i,v in enumerate(row)):raise ValueError('BOOTSTRAP_ORIENTATION')
        totals.append(sum(ints[v] for v in row))
    return [str(quantile(totals,F(q,40))/(32*den)) for q in (1,39)]


def select(rows,mask):
    if mask in WINDOWS:
        lo,hi=WINDOWS[mask]
        return [x for x in rows if x['target']%4==3 and lo<=(x['target']+1)//4<=hi]
    if mask=='G_all':return rows
    return [x for x in rows if (x['target']%4==1 if mask=='S' else x['target']%4==3 and (mask=='Q' or x['cue']==mask[-1]))]


def balance(rows):
    ds=[F(x['C'])-F(x['U']) for x in rows]
    return dict(count=len(ds),better=sum(d<0 for d in ds),worse=sum(d>0 for d in ds),equal=sum(d==0 for d in ds),
        gain=str(sum((-d for d in ds if d<0),F())),harm=str(sum((d for d in ds if d>0),F())),
        net=str(-sum(ds,F())),max_harm=str(max([F()]+ds)),
        mean_delta=str(sum(ds,F())/len(ds)) if ds else None)


def validate(reports):
    if len(reports)!=32 or [x['replicate'] for x in reports]!=list(range(1,33)):raise ValueError('COMPLETE_CASES')
    for report in reports:
        if report['orientation']!=(report['replicate']-1)%2 or report['complete'] is not True:raise ValueError('CASE_ORIENTATION')
        rows=report['rows']
        if [x['target'] for x in rows]!=list(range(3,1024,2)):raise ValueError('COMPLETE_TARGETS')
        for x in rows:
            if any(type(x[a]) is not float or not math.isfinite(x[a]) or x[a]<0 for a in ('C','U')):raise ValueError('MAE_VALUE')
            if x['cue'] not in (('X','Y') if x['target']%4==3 else (None,)):raise ValueError('CUE_TARGET')
            if any(x[k] not in labels for k,labels in GROUPS.items()):raise ValueError('DIAGNOSIS_LABEL')
        if [len(select(rows,m)) for m in MASKS]!=[32,32,96,128,256,511,255,128,128]:raise ValueError('MASK_COUNT')


def aggregate(reports,data,check=lambda:None):
    if hashlib.sha256(data).hexdigest()!=MATRIX_SHA:raise ValueError('MATRIX_BINDING')
    validate(reports);means={};cumulative=[]
    for rep in reports:
        check();r=rep['replicate'];value=F();curve=[]
        for row in rep['rows']:value+=F(row['C'])-F(row['U']);curve.append(str(value))
        cumulative.append(dict(replicate=r,targets=list(range(3,1024,2)),delta=curve))
        for mask in MASKS:
            xs=select(rep['rows'],mask)
            means[r,mask]={a:sum((F(x[a]) for x in xs),F())/len(xs) for a in ('C','U')}
    secondary=[]
    for mask in MASKS:
        for o in (None,0,1):
            check();rs=[x for x in reports if o is None or x['orientation']==o]
            rows=[(r['replicate'],x) for r in rs for x in select(r['rows'],mask)]
            pairs=[means[r['replicate'],mask]['C']-means[r['replicate'],mask]['U'] for r in rs]
            summary=balance([x for _,x in rows]);worst=max(pairs);mh=F(summary['max_harm'])
            secondary.append(dict(mask=mask,orientation=o,means={a:str(sum((means[r['replicate'],mask][a] for r in rs),F())/len(rs)) for a in ('C','U')},
                pairs=list(map(str,pairs)),mean=str(sum(pairs,F())/len(rs)),worst_mean=str(worst),
                worst_stories=[r['replicate'] for r,v in zip(rs,pairs) if v==worst],
                maximum_harm_targets=[[r,x['target']] for r,x in rows if mh>0 and F(x['C'])-F(x['U'])==mh],**summary))
    vals=list(map(F,secondary[0]['pairs']));ci=interval(vals,data)
    verdict=decision(ci)
    diagnosis=[]
    for field,labels in GROUPS.items():
        for label in labels:
            rows=[x for r in reports for x in select(r['rows'],'Q_early_post') if x[field]==label]
            diagnosis.append(dict(partition=field,label=label,**balance(rows)))
    return dict(primary=dict(name='CR1:Q129-160:C-U',mean=secondary[0]['mean'],pairs=secondary[0]['pairs'],ci=ci,verdict=verdict),
                secondary=secondary,diagnosis=diagnosis,cumulative=cumulative,bootstrap_sha256=hashlib.sha256(data).hexdigest())


def decision(ci):
    low,high=map(F,ci)
    if low>high:raise ValueError('INTERVAL_ORDER')
    return 'C_EARLY_POST_BETTER' if high<0 else 'U_EARLY_POST_BETTER' if low>0 else 'INCONCLUSIVE'
