"""Observer-only metrics. No material generation or policy selection."""
import math
from .common import CASES,need,vector,raw,digest

def identity(receipt):
    alignment=receipt.get('alignment')
    if alignment is not None:
        ms=alignment['matches']
        if len(ms)!=1:return None
        si,k,f=ms[0];role,g,ords=alignment['sources'][si]
        return dict(role=role,generation=g,ordinals=ords,k=k,factors=f)
    ms=receipt['matches']
    if len(ms)!=1:return None
    m=ms[0]
    return dict(role=m['role'],generation=m['generation'],ordinals=m['ordinals'],k=m['offset']*10,factors=m['factors'])

def metrics(case,record):
    f=record['forecast'];receipt=__import__('json').loads(f['provenance_json']);ident=identity(receipt)
    actual=vector(record['actual']);p=vector(f['persistence_values']);ctx=f['context_values']
    output=vector(ctx) if ctx is not None else p
    differences=[abs(a-b) for a,b in zip(output,actual)]
    error=math.fsum(differences)/48;p_error=math.fsum(abs(a-b) for a,b in zip(p,actual))/48
    target=record.get('target',11)
    expected_role='candidate' if target==7 else 'retained' if target==11 else None
    expected_k=0 if target==7 else int(case[1:])//480 if target==11 else None
    provenance=bool(ident and expected_role is not None and ident['role']==expected_role and ident['generation']==1 and ident['ordinals']==[1,2,3,4])
    position=bool(ident and expected_k is not None and ident['k']==expected_k)
    factor=bool(ident and ident['factors']==[1.])
    successor=bool(ident and ident['k']<=10 and ctx is not None)
    exact=bool(ctx is not None and list(ctx)==list(actual))
    correct=bool((target==7 or target==11 and case[0]=='A') and provenance and position and factor and successor and exact)
    return dict(identity=ident,assigned=ident is not None,correct=correct,provenance_correct=provenance,
                position_correct=position,factor_correct=factor,successor_available=successor,continuation_exact=exact,
                foreign=target==11 and case[0]=='B' and ident is not None,error=error,p_error=p_error,
                context_error=error if ctx is not None else None,error_hex=error.hex(),p_error_hex=p_error.hex(),
                absolute_errors=differences,absolute_errors_hex=[x.hex() for x in differences],status=f['status'],
                matches=receipt.get('alignment',receipt)['matches'])

def decide(main,collisions,technical=False):
    if technical:return dict(verdict='TECHNICAL_FAILURE',criteria=None)
    need(set(main)==set(CASES),'SIX_CASES')
    s1=all(main[c]['T']['correct'] and not main[c]['N']['correct'] for c in ('A480','A2400'))
    s2=not any(main[c]['T']['foreign'] and not main[c]['N']['foreign'] for c in CASES[3:])
    s3=main['A0']['N']['correct'] and main['A0']['T']['correct'] and not any(main[c]['N']['correct'] and not main[c]['T']['correct'] for c in CASES[:3])
    means={a:math.fsum(main[c][a]['error'] for c in CASES)/6 for a in ('N','T')}
    means['P']=math.fsum(main[c]['N']['p_error'] for c in CASES)/6
    criteria=dict(S1=s1,S2=s2,S3=s3,S4=means['T']<means['N'] and means['T']<means['P'])
    verdict='IDENTIFIABILITY_LIMIT' if any(c['collision'] for c in collisions) else 'ADDITIONAL_BENEFIT_ON_GRID' if all(criteria.values()) else 'NO_ADDITIONAL_BENEFIT'
    return dict(verdict=verdict,criteria=criteria,means=means,means_hex={k:v.hex() for k,v in means.items()})

def report(archives):
    need(set(archives)=={c+'-'+a for c in CASES for a in ('N','T')},'TWELVE_ARMS')
    main={};individual=[];collisions=[]
    for case in CASES:
        main[case]={}
        for target in (3,5,7,9,11):
            rs={a:next(r for r in archives[case+'-'+a]['records'] if r['target']==target) for a in ('N','T')}
            m={a:metrics(case,rs[a]) for a in ('N','T')}
            need(m['N']['p_error']==m['T']['p_error'],'P_PAIR_EQUAL')
            row=dict(case=case,target=target,phase='main' if target==11 else 'transition' if target==9 else 'learning',**m)
            row.update(delta_T_N=m['T']['error']-m['N']['error'],delta_T_P=m['T']['error']-m['T']['p_error'],
                       higher_error_than_N=m['T']['error']>m['N']['error'],higher_error_than_P=m['T']['error']>m['T']['p_error'],
                       lost_correct=m['N']['correct'] and not m['T']['correct'],additional_foreign=m['T']['foreign'] and not m['N']['foreign'],
                       changed_identity=m['N']['identity']!=m['T']['identity'],changed_status=m['N']['status']!=m['T']['status'])
            individual.append(row)
            if target==11:main[case]=m
    for a in CASES[:3]:
        for b in CASES[3:]:
            x=archives[a+'-T']['records'][-1];y=archives[b+'-T']['records'][-1]
            same_hint=x['hint']==y['hint'];same_stock=x['stock_fingerprint']==y['stock_fingerprint']
            scales=[factor for factor in (.5,1.,2.) if all(x['hint'][j][k]*factor==y['hint'][j][k] for j in (0,1) for k in range(48))]
            collisions.append(dict(a=a,b=b,same_hint=same_hint,same_stock=same_stock,collision=same_hint and same_stock,
                                   different_target=x['actual']!=y['actual'],hint_factors=scales))
    return dict(**decide(main,collisions),main=main,individual=individual,collisions=collisions,
                losses=[dict(case=r['case'],target=r['target'],delta_T_N=r['delta_T_N'],delta_T_P=r['delta_T_P']) for r in individual if r['higher_error_than_N'] or r['higher_error_than_P'] or r['lost_correct'] or r['additional_foreign']])
