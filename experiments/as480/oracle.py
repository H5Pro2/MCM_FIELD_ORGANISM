"""Independent scalar decision oracle: no production distance/selection/judge."""
import math,sys

def need(ok,why):
    if not ok:raise ValueError(why)
def mean_abs(v):
    a=math.fsum(abs(x) for x in v)/48
    if not math.isfinite(a):raise ArithmeticError('AMPLITUDE')
    return a
def mae(a,b):return math.fsum(abs(x-y) for x,y in zip(a,b,strict=True))/48
def matches_equal(a,b):return a==b
def decide(stock,hint,mode,epsilon,tau):
    need(mode in ('exact_v1','signal_approx_v1'),'ORACLE_MODE')
    exact=[]
    for s in stock:
        for offset in range(3):
            factors=[]
            for factor in (.5,1.,2.):
                equal=True
                for j in range(2):
                    for x,y in zip(s['values'][offset+j],hint[j],strict=True):
                        try:z=x*factor
                        except OverflowError:equal=False;break
                        if z!=y:equal=False;break
                    if not equal:break
                if equal:factors.append(factor)
            if factors:exact.append(dict(role=s['role'],generation=s['generation'],formation=s['formation'],ordinals=s['ordinals'],offset=offset,factors=factors))
    base=('ABSTAIN_NO_MATCH' if not exact else 'ABSTAIN_AMBIGUOUS' if len(exact)>1 else
          'PROVISIONAL_CANDIDATE_MATCH' if exact[0]['role']=='candidate' else 'CONFIRMED_RETAINED_MATCH')
    selected=exact;status=base
    if mode=='signal_approx_v1':
        try:
            ah=[mean_abs(v) for v in hint]
            if min(ah)<=epsilon:status,selected='ABSTAIN_LOW_SIGNAL',[]
            elif len(exact)>1:selected=[dict(x,match_quality='EXACT') for x in exact]
            elif len(exact)==1:
                match=exact[0];s=next(s for s in stock if s['role']==match['role'] and s['generation']==match['generation'] and s['ordinals']==match['ordinals'])
                o=match['offset']
                if min(mean_abs(v) for v in s['values'][o:o+2])<=epsilon:status,selected='ABSTAIN_STORED_LOW_SIGNAL',[]
                else:selected=[dict(match,match_quality='EXACT')]
            else:
                selected=[]
                try:
                    for s in stock:
                        for o in range(3):
                            sv=s['values'][o:o+2];sa=[mean_abs(v) for v in sv]
                            if min(sa)<=epsilon:continue
                            scale=max((ah[0]+ah[1])/2,(sa[0]+sa[1])/2)
                            if not math.isfinite(scale) or scale<sys.float_info.min:raise ArithmeticError('DENOMINATOR')
                            distance=math.fsum(abs(hint[j][k]-sv[j][k]) for j in range(2) for k in range(48))/96/scale
                            if not math.isfinite(distance):raise ArithmeticError('DISTANCE')
                            if distance<=tau:selected.append(dict(role=s['role'],generation=s['generation'],formation=s['formation'],ordinals=s['ordinals'],offset=o,factors=[1.],match_quality='APPROXIMATE',distance=distance))
                    status='ABSTAIN_NO_APPROX_CONTEXT' if not selected else 'ABSTAIN_APPROX_AMBIGUOUS' if len(selected)>1 else 'APPROXIMATE_SINGLE_MATCH'
                except ArithmeticError:status,selected='ABSTAIN_APPROX_NUMERIC',[]
        except ArithmeticError:status,selected='ABSTAIN_SIGNAL_NUMERIC',[]
    context=None;prediction='ABSTAIN_NO_CONTEXT'
    if len(selected)>1:prediction='AMBIGUOUS_CONTEXT'
    elif selected:
        m=selected[0]
        if m['factors']!=[1.]:prediction='FACTOR_CONTINUATION_NOT_SPECIFIED'
        elif m['offset']>1:prediction='ABSTAIN_NO_SUCCESSOR'
        else:
            s=next(s for s in stock if s['role']==m['role'] and s['generation']==m['generation'] and s['ordinals']==m['ordinals'])
            context=s['values'][m['offset']+2];prediction='PREDICTED_'+m['role'].upper()
    return dict(status=status,matches=selected,context=context,persistence=hint[1],prediction=prediction,exact_count=len(exact))

def check(record,epsilon,tau):
    answer=decide(record['stock'],record['hint'],record['mode'],epsilon,tau)
    forecast=record['forecast'];receipt=record['receipt']
    need(receipt['status']==answer['status'] and receipt['matches']==answer['matches'],'ORACLE_MATCH')
    need(forecast['status']==answer['prediction'] and forecast['context_values']==answer['context'] and forecast['persistence_values']==answer['persistence'],'ORACLE_OUTPUT')
    if record['mode']=='signal_approx_v1':
        lost=answer['exact_count']==1 and answer['status'] in ('ABSTAIN_LOW_SIGNAL','ABSTAIN_STORED_LOW_SIGNAL','ABSTAIN_SIGNAL_NUMERIC')
        need(receipt['retrieval']==dict(policy=record['mode'],epsilon=epsilon,tau=tau,exact_match_count=answer['exact_count'],signal_lost_exact_single=lost),'ORACLE_RETRIEVAL')
    output=answer['context'] if answer['context'] is not None else answer['persistence']
    need(record['error']==mae(output,record['actual']) and record['p_error']==mae(answer['persistence'],record['actual']),'ORACLE_ERROR')
    return answer

def assignment(record):
    ms=record['receipt']['matches']
    if len(ms)!=1:return dict(assigned=False,correct=False)
    m=ms[0]
    correct=(m['role']=='retained' and m['generation']==1 and m['ordinals']==[1,2,3,4]
             and m['offset']==0 and m['factors']==[1.] and record['forecast']['context_values'] is not None)
    return dict(assigned=True,correct=correct)

def verdict(rows,collision=False,technical=False):
    if technical:return dict(verdict='TECHNICAL_ERROR',criteria=None)
    need(set(rows)=={'A0','A480','B0','B480'},'FOUR_CASES_REQUIRED')
    criteria=dict(S1=rows['A480']['N']['correct'] and not rows['A480']['E']['correct'],
        S2=not any(rows[c]['N']['assigned'] and not rows[c]['E']['assigned'] for c in ('B0','B480')),
        S3=not any(rows[c]['E']['correct'] and not rows[c]['N']['correct'] for c in ('A0','A480')))
    means={m:math.fsum(rows[c][m]['error'] for c in rows)/4 for m in ('E','N','P')}
    criteria['S4']=means['N']<means['E'] and means['N']<means['P']
    result='IDENTIFIABILITY_LIMIT' if collision else 'CRITERIA_MET' if all(criteria.values()) else 'NO_ADDITIONAL_BENEFIT'
    return dict(verdict=result,criteria=criteria,means=means,FLAG_ADDITIONAL_FALSE_RETRIEVAL=not criteria['S2'],
                FLAG_HIGHER_TOTAL_ERROR=means['N']>means['E'] or means['N']>means['P'])
