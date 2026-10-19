"""Independent archive reconstruction: no production selector or evaluation import."""
import json,math
from .common import *
from experiments.as480.oracle import decide as base_decide
from experiments.temporal_alignment.oracle import decide as grid_decide
EPS=float.fromhex('0x1.1a414d9cf9967p-15')

def check_record(case,arm,record,lookup):
    i=record['target'];f=record['frozen'];stock=[];banks=[]
    need(i in (3,5,7,9,11) and f['hint_indices']==[i-2,i-1],'RECORD_TIME')
    hint=[vector(lookup(key(case,j))['projection']['values']) for j in f['hint_indices']]
    for s in f['stock']:
        need(max(s['ordinals'])<=i-3,'FROZEN_FUTURE')
        values=[vector(lookup(key(case,j))['projection']['values']) for j in s['ordinals']]
        bank_rows=[lookup(n) for n in bank_keys(case,s['ordinals'])]
        need(s['bank_start']==(s['ordinals'][0]-1)*4800 and s['bank_digests']==[x['pcm_sha256'] for x in bank_rows],'BANK_PROVENANCE')
        stock.append(dict(role=s['role'],generation=s['generation'],formation=s['formation'],ordinals=s['ordinals'],values=values))
        banks.append(dict(values=[vector(x['projection']['values']) for x in bank_rows]))
    base=base_decide(stock,hint,'signal_approx_v1',EPS,1/32)
    answer=grid_decide(hint,banks,base['status']) if arm=='T' and base['status']=='ABSTAIN_NO_APPROX_CONTEXT' else None
    forecast=record['forecast'];receipt=json.loads(forecast['provenance_json'])
    need(receipt['status']==base['status'] and receipt['matches']==canonical(base['matches']),'BASE_ORACLE')
    context=answer['value'] if answer else base['context'];status=answer['status'] if answer else base['prediction']
    need(forecast['status']==status and forecast['context_values']==canonical(context) and forecast['persistence_values']==list(hint[1]),'OUTPUT_ORACLE')
    need(forecast['target_index']==i and receipt['input_indices']==[i-2,i-1] and receipt['source_intervals']==[[(i-3)*4800,(i-2)*4800],[(i-2)*4800,(i-1)*4800]],'FORECAST_TIME')
    need(receipt['read_revision']==f['read_revision']==forecast['read_revision'],'READ_REVISION')
    need(receipt['owner']=='owner' and receipt['stream']=='stream' and receipt['profile']==lookup(key(case,i))['projection']['profile_digest'],'RECEIPT_SCOPE')
    lost=base['exact_count']==1 and base['status'] in ('ABSTAIN_LOW_SIGNAL','ABSTAIN_STORED_LOW_SIGNAL','ABSTAIN_SIGNAL_NUMERIC')
    need(receipt['retrieval']==dict(policy='signal_approx_v1',epsilon=EPS,tau=1/32,exact_match_count=base['exact_count'],signal_lost_exact_single=lost),'RETRIEVAL_GATE')
    if answer:
        need(receipt['alignment']==dict(status=answer['status'],matches=answer['matches'],sources=[[s['role'],s['generation'],s['ordinals']] for s in f['stock']]),'GRID_ORACLE')
    else:need('alignment' not in receipt,'UNEXPECTED_ALIGNMENT')
    need(record['actual']==lookup(key(case,i))['projection']['values'],'ACTUAL_BINDING')
    need(record['freeze_token']==digest(raw(dict(forecast=forecast,frozen=f))),'FREEZE_DIGEST')
    record=dict(record,hint=canonical(hint),stock_fingerprint=digest(raw(dict(stock=stock,banks=banks))))
    return record

def reconstruct(folder):
    folder=Path(folder);manifest=read(folder/'material/manifest.json');cache={}
    need(read(folder/'material/recipe.json')==canonical(RECIPE) and sha(folder/'material/recipe.json')==manifest['recipe_sha256'],'RECIPE')
    for s,item in manifest['sources'].items():need(item['bytes']==76800 and info(folder/'material'/(s+'.f32le'))==item,'SOURCE_HASH')
    need(set(manifest['sources'])=={'A','B'},'TWO_SOURCES')
    names={key(c,i) for c in CASES for i in range(1,12)}|{f'{c}-bank-{b}-{k}' for c in CASES for b in (0,1) for k in range(31) if k%10}
    need(set(manifest['projections'])==names,'390_PROJECTIONS')
    for n,item in manifest['projections'].items():
        p=folder/'material'/(n+'.json');need(info(p)==item,'MATERIAL_HASH');row=read(p);vector(row['projection']['values'])
        c,kind,*tail=n.split('-')
        if kind=='base':
            i=int(tail[0]);s,a,b=interval(c,i);start=(i-1)*4800
        else:
            block,k=map(int,tail);s='A';a=k*480;b=a+4800;start=block*19200+a
        need(row['source']==s and row['source_interval']==[a,b] and row['start']==start and row['end']==start+4800,'INTERVAL_MANIFEST')
        proj=row['projection'];payload=dict(proj);stored_digest=payload.pop('projection_digest')
        need(stored_digest==digest(json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')),'PROJECTION_DIGEST')
        need(proj['profile_digest']=='4a56de2f630055816533ecb45cdef5662157993bc1192023d01cf29e92247c9f' and proj['window_start_tick']==start and proj['window_end_tick']==start+4800,'PROJECTION_PROFILE_TIME')
        need(row['source_sha256']==manifest['sources'][s]['sha256'],'SOURCE_BINDING')
        with (folder/'material'/(s+'.f32le')).open('rb') as f:f.seek(a*4);payload=f.read((b-a)*4)
        need(digest(payload)==row['pcm_sha256'],'PCM_INTERVAL_HASH');cache[n]=row
    result={}
    for c in CASES:
        for arm in ('N','T'):
            data=read(folder/'observer'/(c+'-'+arm+'.json'))
            need(data['cleanup'] and [x['target'] for x in data['records']]==[3,5,7,9,11],'ARM_COMPLETE')
            need([x['index'] for x in data['states']]==list(range(1,12)) and all(x['core']==x['reference'] for x in data['states']),'CORE_REFERENCE')
            expected=[]
            rec={x['target']:x for x in data['records']}
            for i in range(1,12):
                if i in rec:expected.append(dict(event='FREEZE',target=i,token=rec[i]['freeze_token']))
                expected.append(dict(event='READ',target=i,freeze=rec[i]['freeze_token'] if i in rec else None,pcm_sha256=cache[key(c,i)]['pcm_sha256']))
            need(data['events']==expected,'FREEZE_READ_ORDER')
            data['records']=[check_record(c,arm,x,cache.__getitem__) for x in data['records']]
            result[c+'-'+arm]=data
        need(result[c+'-N']['states']==result[c+'-T']['states'],'NT_BANK_CORE_COMPARISON')
    return result

def independent_verdict(archives):
    """Second implementation derives truth directly from checked forecast provenance."""
    rows={};hints={};means={}
    for c in CASES:
        rows[c]={}
        for arm in ('N','T'):
            r=archives[c+'-'+arm]['records'][-1];f=r['forecast'];p=json.loads(f['provenance_json']);single=None
            if 'alignment' in p:
                matches=p['alignment']['matches']
                if len(matches)==1:
                    si,k,factors=matches[0];role,g,ordinals=p['alignment']['sources'][si]
                    single=(role,g,ordinals,k,factors)
            elif len(p['matches'])==1:
                m=p['matches'][0];single=(m['role'],m['generation'],m['ordinals'],10*m['offset'],m['factors'])
            ctx=f['context_values'];values=ctx if ctx is not None else f['persistence_values']
            e=math.fsum(abs(values[j]-r['actual'][j]) for j in range(48))/48
            pe=math.fsum(abs(f['persistence_values'][j]-r['actual'][j]) for j in range(48))/48
            correct=bool(c.startswith('A') and single==('retained',1,[1,2,3,4],int(c[1:])//480,[1.]) and ctx is not None and ctx==r['actual'])
            rows[c][arm]=(correct,c.startswith('B') and single is not None,e,pe)
        hints[c]=archives[c+'-T']['records'][-1]
    means={a:math.fsum(rows[c][a][2] for c in CASES)/6 for a in ('N','T')}
    means['P']=math.fsum(rows[c]['N'][3] for c in CASES)/6
    flags=dict(S1=all(rows[c]['T'][0] and not rows[c]['N'][0] for c in CASES[1:3]),
               S2=all(not rows[c]['T'][1] or rows[c]['N'][1] for c in CASES[3:]),
               S3=bool(rows['A0']['N'][0] and rows['A0']['T'][0] and all(not rows[c]['N'][0] or rows[c]['T'][0] for c in CASES[:3])),
               S4=means['T']<means['N'] and means['T']<means['P'])
    collision=any(hints[a]['hint']==hints[b]['hint'] and hints[a]['stock_fingerprint']==hints[b]['stock_fingerprint'] for a in CASES[:3] for b in CASES[3:])
    verdict='IDENTIFIABILITY_LIMIT' if collision else 'ADDITIONAL_BENEFIT_ON_GRID' if all(flags.values()) else 'NO_ADDITIONAL_BENEFIT'
    return dict(verdict=verdict,criteria=flags,means=means)

def check_metrics(archives,result):
    """Independently recompute every scalar/component loss, not only the means."""
    need(len(result['individual'])==30 and len(result['collisions'])==9,'EVALUATION_SHAPE')
    expected_losses=[]
    for pos,(case,target) in enumerate((c,i) for c in CASES for i in (3,5,7,9,11)):
        row=result['individual'][pos];need(row['case']==case and row['target']==target,'EVALUATION_ORDER')
        errors={};correct={};foreign={}
        for arm in ('N','T'):
            r=next(x for x in archives[case+'-'+arm]['records'] if x['target']==target);f=r['forecast'];ctx=f['context_values'];p=f['persistence_values'];actual=r['actual']
            values=ctx if ctx is not None else p
            diffs=[abs(values[j]-actual[j]) for j in range(48)]
            e=math.fsum(diffs)/48;pe=math.fsum(abs(p[j]-actual[j]) for j in range(48))/48
            m=row[arm];need(m['error']==e and m['p_error']==pe and m['context_error']==(None if ctx is None else e),'INDEPENDENT_METRIC')
            need(m['absolute_errors']==diffs and m['absolute_errors_hex']==[d.hex() for d in diffs] and m['error_hex']==e.hex() and m['p_error_hex']==pe.hex(),'INDEPENDENT_COMPONENT_ERROR')
            receipt=json.loads(f['provenance_json']);ident=None
            if 'alignment' in receipt:
                a=receipt['alignment']
                if len(a['matches'])==1:
                    si,k,factors=a['matches'][0];role,g,ords=a['sources'][si];ident=dict(role=role,generation=g,ordinals=ords,k=k,factors=factors)
            elif len(receipt['matches'])==1:
                a=receipt['matches'][0];ident=dict(role=a['role'],generation=a['generation'],ordinals=a['ordinals'],k=10*a['offset'],factors=a['factors'])
            expected_role={7:'candidate',11:'retained'}.get(target);expected_k=0 if target==7 else int(case[1:])//480 if target==11 else None
            prov=bool(ident and expected_role and ident['role']==expected_role and ident['generation']==1 and ident['ordinals']==[1,2,3,4])
            position=bool(ident and expected_k is not None and ident['k']==expected_k)
            factor=bool(ident and ident['factors']==[1.]);successor=bool(ident and ident['k']<=10 and ctx is not None);exact=bool(ctx is not None and ctx==actual)
            correct[arm]=bool((target==7 or target==11 and case.startswith('A')) and prov and position and factor and successor and exact)
            foreign[arm]=target==11 and case.startswith('B') and ident is not None
            for key,value in dict(identity=ident,assigned=ident is not None,correct=correct[arm],foreign=foreign[arm],provenance_correct=prov,position_correct=position,factor_correct=factor,successor_available=successor,continuation_exact=exact).items():need(m[key]==value,'INDEPENDENT_ASSIGNMENT:'+key)
            errors[arm]=(e,pe)
        dn=errors['T'][0]-errors['N'][0];dp=errors['T'][0]-errors['T'][1]
        lost=correct['N'] and not correct['T'];extra=foreign['T'] and not foreign['N']
        need(row['delta_T_N']==dn and row['delta_T_P']==dp and row['lost_correct']==lost and row['additional_foreign']==extra,'INDEPENDENT_LOSS')
        need(row['higher_error_than_N']==(dn>0) and row['higher_error_than_P']==(dp>0),'INDEPENDENT_LOSS_FLAGS')
        if dn>0 or dp>0 or lost or extra:expected_losses.append(dict(case=case,target=target,delta_T_N=dn,delta_T_P=dp))
    need(result['losses']==expected_losses,'COMPLETE_LOSS_LIST')
    for item,(a,b) in zip(result['collisions'],((a,b) for a in CASES[:3] for b in CASES[3:]),strict=True):
        x=archives[a+'-T']['records'][-1];y=archives[b+'-T']['records'][-1]
        same=x['hint']==y['hint'];stock=x['stock_fingerprint']==y['stock_fingerprint']
        scales=[f for f in (.5,1.,2.) if all(x['hint'][j][k]*f==y['hint'][j][k] for j in (0,1) for k in range(48))]
        need(item==dict(a=a,b=b,same_hint=same,same_stock=stock,collision=same and stock,different_target=x['actual']!=y['actual'],hint_factors=scales),'INDEPENDENT_COLLISION')
    need({k:result[k] for k in ('verdict','criteria','means')}==independent_verdict(archives),'INDEPENDENT_VERDICT')
    return dict(decisions=60,persistence_values=30,collision_pairs=9,all_component_errors=True,all_assignments=True,all_losses=True)
