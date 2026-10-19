"""Single interaction; whole source pairs are the only resampling unit."""
from fractions import Fraction as F
import math
import hashlib
from .matrix import shape

TARGETS=list(range(3,1024,2))

def validate(records):
    if len(records)!=16 or [r['pair'] for r in records]!=list(range(1,17)):raise ValueError('COMPLETE_PAIRS')
    for r in records:
        if r.get('complete') is not True or r['orientation']!=(r['pair']-1)%2:raise ValueError('PAIR_RECEIPT')
        if set(r['conditions'])!={'A','B'}:raise ValueError('CONDITIONS')
        for label,c in r['conditions'].items():
            if c.get('condition')!=label:raise ValueError('CONDITION_BINDING')
            if c.get('complete') is not True or c.get('integrity')!='PASS_DELTA_INTEGRITY' or c.get('cleanup') is not True:raise ValueError('UNVERIFIED_CONDITION')
            if c['pair']!=r['pair'] or c['targets']!=TARGETS:raise ValueError('PAIR_OR_DENOMINATOR')
            if len(c['E'])!=511 or len(c['F'])!=511:raise ValueError('ARM_DENOMINATOR')
            if any(type(v) is not float or not math.isfinite(v) or v<0 for a in ('E','F') for v in c[a]):raise ValueError('ERROR_VALUE')

def decision(ci):
    lo,hi=map(F,ci)
    if lo>hi:raise ValueError('INTERVAL_ORDER')
    return 'NEGATIVE_INTERACTION' if hi<0 else 'POSITIVE_INTERACTION' if lo>0 else 'INCONCLUSIVE'

def primary(records,data,digest):
    validate(records);shape(data)
    if hashlib.sha256(data).hexdigest()!=digest:raise ValueError('MATRIX_BINDING')
    pairs=[]
    for r in records:
        d={label:sum((F(e)-F(f) for e,f in zip(c['E'],c['F'],strict=True)),F())/511 for label,c in r['conditions'].items()}
        pairs.append(d['A']-d['B'])
    denominator=math.lcm(*(x.denominator for x in pairs));scaled=[int(x*denominator) for x in pairs]
    samples=sorted(sum(scaled[k] for k in data[i:i+16]) for i in range(0,len(data),16))
    ci=[]
    for q in (F(1,40),F(39,40)):
        h=9999*q;j=h.numerator//h.denominator
        ci.append(str((samples[j]*(1-h+j)+samples[j+1]*(h-j))/(16*denominator)))
    return dict(name='ZW1:(E-F)A-(E-F)B:all511',pairs=list(map(str,pairs)),mean=str(sum(pairs,F())/16),ci=ci,verdict=decision(ci),source_pairs=16,condition_target_pairs=16352,arm_errors=32704)

def reference(records,data):
    # Independent shape and arithmetic, including recomputation from all four arms.
    from .matrix import verify
    verify(data)
    if len(records)!=16:raise ValueError('REFERENCE_PAIRS')
    arms=[]
    for number,r in enumerate(records,1):
        if r['pair']!=number or not r['complete'] or r['orientation']!=(number-1)%2 or set(r['conditions'])!={'A','B'}:raise ValueError('REFERENCE_PAIR')
        values=[]
        for label in ('A','B'):
            c=r['conditions'][label]
            if c['pair']!=number or c['condition']!=label or c['targets']!=list(range(3,1024,2)) or not c['complete'] or not c['cleanup'] or c['integrity']!='PASS_DELTA_INTEGRITY':raise ValueError('REFERENCE_CONDITION')
            for name in ('E','F'):
                if len(c[name])!=511 or any(type(x) is not float or x<0 or not math.isfinite(x) for x in c[name]):raise ValueError('REFERENCE_ARM')
                values.append(sum(map(F,c[name]),F())/511)
        arms.append(values)
    diffs=[a-b-c+d for a,b,c,d in arms]
    denominator=math.lcm(*(v.denominator for row in arms for v in row));scaled=[[int(v*denominator) for v in row] for row in arms]
    samples=[]
    for start in range(0,160000,16):
        row=data[start:start+16];weights=[row.count(i) for i in range(16)]
        totals=[sum(weights[i]*scaled[i][a] for i in range(16)) for a in range(4)]
        samples.append(totals[0]-totals[1]-totals[2]+totals[3])
    samples.sort();bounds=[]
    for numerator in (1,39):
        div,rem=divmod(9999*numerator,40)
        bounds.append(str(F((40-rem)*samples[div]+rem*samples[div+1],40*16*denominator)))
    return dict(mean=str(sum(diffs,F())/16),pairs=list(map(str,diffs)),ci=bounds)
