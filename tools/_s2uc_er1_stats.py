"""ER1 complete-denominator exact statistics; synthetic qualification only."""
import hashlib,math
from fractions import Fraction as F
from tools._s2uc_ura1_cr1_stats import interval, MATRIX_SHA

def decision(ci):
    lo,hi=map(F,ci)
    if lo>hi:raise ValueError('INTERVAL_ORDER')
    return 'E_BETTER' if hi<0 else 'E_WORSE' if lo>0 else 'INCONCLUSIVE'
def balance(rows):
    d=[F(x['E'])-F(x['F']) for x in rows]
    return dict(count=len(d),mean=None if not d else str(sum(d,F())/len(d)),gain=str(sum((-x for x in d if x<0),F())),harm=str(sum((x for x in d if x>0),F())),better=sum(x<0 for x in d),worse=sum(x>0 for x in d),equal=sum(x==0 for x in d),max_harm=str(max([F()]+d)))
def aggregate(reports,matrix):
    if hashlib.sha256(matrix).hexdigest()!=MATRIX_SHA:raise ValueError('MATRIX_BINDING')
    if [r['replicate'] for r in reports]!=list(range(1,33)):raise ValueError('COMPLETE_STORIES')
    for r in reports:
        if r['complete'] is not True or r['orientation']!=(r['replicate']-1)%2:raise ValueError('COMPLETE_ORIENTATION')
        if [x['target'] for x in r['rows']]!=list(range(3,1024,2)):raise ValueError('COMPLETE_TARGETS')
        for x in r['rows']:
            if any(type(x[k]) is not float or not math.isfinite(x[k]) or x[k]<0 for k in ('E','F')):raise ValueError('ERROR_VALUE')
    pairs=[sum((F(x['E'])-F(x['F']) for x in r['rows']),F())/511 for r in reports]
    ci=interval(pairs,matrix)
    return dict(primary=dict(name='ER1:E-F:all511',count=16352,mean=str(sum(pairs,F())/32),pairs=list(map(str,pairs)),ci=ci,verdict=decision(ci)),balance=balance([x for r in reports for x in r['rows']]),orientation=[balance([x for r in reports if r['orientation']==o for x in r['rows']]) for o in (0,1)],worst_story_delta=str(max(pairs)),descriptive={name:balance([x for r in reports for x in r['rows'] if predicate(x)]) for name,predicate in {
        'pre':lambda x:x['target']<=512,'post':lambda x:x['target']>512,
        'Q':lambda x:x['target']%4==3,'S':lambda x:x['target']%4==1,
        'warm':lambda x:x.get('warm') is True,'cold':lambda x:x.get('warm') is False}.items()})
def reference(reports,matrix):
    # Independent sums, stratified integer-weight bootstrap and percentile interpolation.
    if len(reports)!=32 or len(matrix)!=320000:raise ValueError('REFERENCE_SHAPE')
    values=[]
    for number,r in enumerate(reports,1):
        if r['replicate']!=number or r['orientation']!=(number-1)%2 or not r['complete']:raise ValueError('REFERENCE_CASE')
        if any(type(x[k]) is not float or not math.isfinite(x[k]) or x[k]<0 for x in r['rows'] for k in ('E','F')):raise ValueError('REFERENCE_ERROR')
        indexed={x['target']:x for x in r['rows']}
        if len(r['rows'])!=511 or set(indexed)!=set(range(3,1024,2)):raise ValueError('REFERENCE_TARGETS')
        values.append((sum((F(indexed[t]['E']) for t in sorted(indexed)),F())-sum((F(indexed[t]['F']) for t in sorted(indexed)),F()))/511)
    denominator=math.lcm(*(x.denominator for x in values));scaled=[int(x*denominator) for x in values]
    samples=[]
    for k in range(10000):
        row=matrix[k*32:k*32+32]
        if any(v>=32 or v%2 != (j//16) for j,v in enumerate(row)):raise ValueError('REFERENCE_STRATA')
        weights=[row.count(j) for j in range(32)]
        samples.append(sum(a*b for a,b in zip(weights,scaled)))
    samples.sort();ci=[]
    for numerator in (1,39):
        pos=F(9999*numerator,40);left=pos.numerator//pos.denominator;part=pos-left
        ci.append(str(((1-part)*samples[left]+part*samples[left+1])/(32*denominator)))
    return dict(mean=str(sum(values,F())/32),ci=ci,pairs=list(map(str,values)))
