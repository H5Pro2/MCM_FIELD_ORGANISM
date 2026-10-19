"""FW1 mixture mean. Only supplied small neutral matrices; no draw generator."""
from fractions import Fraction as F
import math
import hashlib

def validate(records,data,neutral=True,digest=None):
    n=len(records)
    if n not in (2,16) or [r['pair'] for r in records]!=list(range(1,n+1)):raise ValueError('COMPLETE_PAIRS')
    if type(data) is not bytes or len(data)%n:raise ValueError('MATRIX_SHAPE')
    if neutral is True:
        if not 2<=len(data)//n<=64:raise ValueError('NEUTRAL_MATRIX')
    elif neutral is False:
        if n!=16 or len(data)!=160000 or digest is None or hashlib.sha256(data).hexdigest()!=digest:raise ValueError('FULL_MATRIX_BINDING')
    else:raise ValueError('STATISTICS_SCOPE')
    for start in range(0,len(data),n):
        if any(v>=n or v%2!=int(c>=n//2) for c,v in enumerate(data[start:start+n])):raise ValueError('MATRIX_STRATA')
    targets=records[0]['conditions']['A']['targets']
    if not targets or targets!=list(range(3,targets[-1]+1,2)) or targets[-1]>1023:raise ValueError('TARGETS')
    if not neutral and targets!=list(range(3,1024,2)):raise ValueError('FULL_TARGETS')
    for r in records:
        if r['complete'] is not True or r['orientation']!=(r['pair']-1)%2 or set(r['conditions'])!={'A','B'}:raise ValueError('PAIR_RECEIPT')
        for label,c in r['conditions'].items():
            if c['pair']!=r['pair'] or c['condition']!=label or c['targets']!=targets:raise ValueError('CONDITION_BINDING')
            if any(c[k] is not True for k in ('complete','cleanup','stock_equal')) or c['integrity']!='PASS_DELTA_INTEGRITY':raise ValueError('UNVERIFIED')
            for a in ('KEEP','RESET'):
                if len(c[a])!=len(targets) or any(type(v) is not float or not math.isfinite(v) or v<0 for v in c[a]):raise ValueError('ERROR_VALUE')
    return n,len(targets)

def decision(ci,informative):
    lo,hi=map(F,ci)
    if lo>hi:raise ValueError('INTERVAL_ORDER')
    if not informative:return 'NICHT_INFORMATIV'
    return 'NUTZEN_GESTUETZT' if hi<0 else 'SCHADEN_GESTUETZT' if lo>0 else 'INCONCLUSIVE'

def primary(records,data,*,neutral=True,digest=None):
    n,t=validate(records,data,neutral,digest);pairs=[];informative=False
    for r in records:
        total=F()
        for c in r['conditions'].values():
            total+=sum((F(a)-F(b) for a,b in zip(c['KEEP'],c['RESET'],strict=True)),F())
            informative|=any(e['deleted']>0 and e['end']+3<=c['targets'][-1] for e in c['resets'])
        pairs.append(total/(2*t))
    samples=sorted(sum((pairs[k] for k in data[i:i+n]),F())/n for i in range(0,len(data),n))
    ci=[]
    for q in (F(1,40),F(39,40)):
        h=(len(samples)-1)*q;j=h.numerator//h.denominator
        ci.append(str(samples[j]*(1-h+j)+samples[j+1]*(h-j)))
    return dict(name='FW1:mean((KEEP-RESET)A,(KEEP-RESET)B)',neutral_only=neutral,pairs=list(map(str,pairs)),mean=str(sum(pairs,F())/n),ci=ci,informative=informative,verdict=decision(ci,informative),source_pairs=n,condition_target_pairs=n*2*t,arm_errors=n*4*t)

def reference(records,data,*,neutral=True,digest=None):
    # Separate validation and weighted-arm arithmetic; does not call primary/validate.
    count=len(records)
    if count not in (2,16) or type(data) is not bytes or len(data)%count:raise ValueError('REFERENCE_SHAPE')
    if neutral is True:
        if not 2<=len(data)//count<=64:raise ValueError('REFERENCE_NEUTRAL_MATRIX')
    elif neutral is False:
        if count!=16 or len(data)//count!=10000 or digest is None or hashlib.sha256(data).hexdigest()!=digest:raise ValueError('REFERENCE_MATRIX_BINDING')
    else:raise ValueError('REFERENCE_SCOPE')
    means=[];target_set=None;opportunities=0
    for ordinal,r in enumerate(records,1):
        if r['pair']!=ordinal or r['orientation']!=(ordinal-1)%2 or r['complete'] is not True or set(r['conditions'])!={'A','B'}:raise ValueError('REFERENCE_PAIR')
        arms=[]
        for label in ('A','B'):
            c=r['conditions'][label];targets=c['targets']
            if not targets or targets!=list(range(3,targets[-1]+1,2)) or targets[-1]>1023:raise ValueError('REFERENCE_TARGETS')
            if not neutral and len(targets)!=511:raise ValueError('REFERENCE_FULL_TARGETS')
            if target_set is None:target_set=targets
            if targets!=target_set or c['pair']!=ordinal or c['condition']!=label or any(c[k] is not True for k in ('complete','cleanup','stock_equal')) or c['integrity']!='PASS_DELTA_INTEGRITY':raise ValueError('REFERENCE_CONDITION')
            for reset in c['resets']:
                if reset['deleted'] and any(target>reset['end']+1 for target in targets):opportunities+=1
            for name in ('KEEP','RESET'):
                values=c[name]
                if len(values)!=len(targets) or any(type(v) is not float or not math.isfinite(v) or v<0 for v in values):raise ValueError('REFERENCE_ERRORS')
                arms.append(sum(map(F,values),F())/len(values))
        means.append(arms)
    diffs=[(a-b+c-d)/2 for a,b,c,d in means];draws=[]
    for row in range(len(data)//count):
        indices=data[row*count:(row+1)*count]
        if any(i>=count or i%2!=(column//(count//2)) for column,i in enumerate(indices)):raise ValueError('REFERENCE_STRATA')
        weights=[indices.count(i) for i in range(count)]
        totals=[sum((weights[i]*means[i][a] for i in range(count)),F()) for a in range(4)]
        draws.append((totals[0]-totals[1]+totals[2]-totals[3])/(2*count))
    draws.sort();ci=[]
    for numerator in (1,39):
        j,rem=divmod((len(draws)-1)*numerator,40)
        ci.append(str((draws[j]*(40-rem)+draws[j+1]*rem)/40))
    verdict='NICHT_INFORMATIV' if opportunities==0 else 'NUTZEN_GESTUETZT' if F(ci[1])<0 else 'SCHADEN_GESTUETZT' if F(ci[0])>0 else 'INCONCLUSIVE'
    return dict(mean=str(sum(diffs,F())/count),pairs=list(map(str,diffs)),ci=ci,informative=opportunities>0,verdict=verdict)
