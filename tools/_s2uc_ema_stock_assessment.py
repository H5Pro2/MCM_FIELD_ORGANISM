"""Fixed-mask assessment. Expectations never write to system state."""
import math


def key(cell):
    return (cell['role'],cell['generation'],cell['offset'],cell['quality'])


def metrics(results,masks):
    rows={a:{r['target']:r for r in results[a]['rows']} for a in ('E','K','P')}
    output={}
    for name,targets in masks.items():
        arms={}
        for a in rows:
            missing=[t for t in targets if t not in rows[a]]
            values=[rows[a][t]['selected_mae'] for t in targets if t in rows[a]]
            valid=all(type(x) in (int,float) and math.isfinite(x) and x>=0 for x in values)
            arms[a]=dict(count=len(values),expected_count=len(targets),missing=missing,
                status='EVALUABLE' if not missing and valid else 'NOT_EVALUABLE',
                error_sum=sum(values) if not missing and valid else None,
                mae=sum(values)/len(targets) if not missing and valid else None)
        differences=[]
        for t in targets:
            if all(t in rows[a] for a in rows):
                differences.append(dict(target=t,choice=rows['E'][t]['choice'],
                    context_available=rows['E'][t]['context_mae'] is not None,
                    E_minus_K=rows['E'][t]['selected_mae']-rows['K'][t]['selected_mae'],
                    E_minus_P=rows['E'][t]['selected_mae']-rows['P'][t]['selected_mae']))
        output[name]=dict(targets=targets,arms=arms,individual_differences=differences)
    return output


def assess(results,plan):
    report=dict(metrics=metrics(results,plan['masks']),technical_errors=[],expectation_deviations=[])
    technical=report['technical_errors'];deviations=report['expectation_deviations']
    expected_targets=plan['masks']['Gesamt']
    for arm,r in results.items():
        if [x['target'] for x in r['rows']]!=expected_targets:technical.append(arm+':TARGET_SET')
        if not all(r.get(k) for k in ('states_identical','slots_released','ema_cleared')):
            technical.append(arm+':RELEASE_OR_REFERENCE')
        if r.get('censored_target')!=65:technical.append(arm+':CENSOR')
    if not results['E']['state_hashes']==results['K']['state_hashes']==results['P']['state_hashes']:
        technical.append('CROSS_ARM_STATES')
    receipts=[[f['receipt'] for f in results[a]['forecasts']] for a in ('E','K','P')]
    if not receipts[0]==receipts[1]==receipts[2]:technical.append('CROSS_ARM_RECEIPTS')
    forecasts={f['target']:f for f in results['E']['forecasts']}
    updates={u['target']:u for u in results['E']['error_updates']}
    admissions={e['frame']:e for e in results['E']['generation_events']}
    for expected in plan['expected_stock']:
        event=admissions.get(expected['frame'])
        if event is None:
            deviations.append(dict(frame=expected['frame'],kind='MISSING_STOCK_OBSERVATION'));continue
        def identity(item):
            block=(item['ordinals'][0]-1)//4
            return [plan['blocks'][block],item['generation']]
        stock=event['after']
        actual=dict(retained=[identity(x) for x in stock['retained']],
            candidate=identity(stock['candidate']) if stock['candidate'] else None)
        wanted={k:expected[k] for k in ('retained','candidate')}
        if actual!=wanted:deviations.append(dict(frame=expected['frame'],kind='STOCK_HYPOTHESIS',expected=wanted,actual=actual))
    for target,expected in plan['expected_targets'].items():
        target=int(target);f=forecasts.get(target)
        if f is None:
            deviations.append(dict(target=target,kind='MISSING_FORECAST'));continue
        matches=f['receipt']['matches']
        actual=sorted([[{'retained':0,'candidate':1}[m['role']],m['generation'],m['offset']] for m in matches])
        if actual!=sorted(expected['matches']) or f['context_available']!=expected['context_available']:
            deviations.append(dict(target=target,kind='RETRIEVAL_HYPOTHESIS',actual=actual,expected=expected))
    # Technical checks are independent of the hypothesized stock chronology.
    for target,u in updates.items():
        f=forecasts[target];ticket=u['ticket'];g,_,role,offset,quality,choice,valid=ticket
        if not valid and u['before']!=u['after']:technical.append(f'{target}:UPDATE_WITHOUT_TICKET')
        old=next((c for c in f['errors_before'] if key(c)==(role,g,offset,quality)),None)
        wanted='CONTEXT' if valid and old is not None and old['ec']<old['ep'] else 'PERSISTENCE'
        if f['choice']!=wanted:technical.append(f'{target}:CHOICE_NOT_FROM_OWN_PRIOR_CELL')
        if not u['atomic_pair_verified']:technical.append(f'{target}:PAIR_UPDATE')
        expected=[dict(c) for c in u['before']]
        if valid and u['key_live']:
            previous=next((c for c in expected if key(c)==(role,g,offset,quality)),None)
            if previous is None:
                expected.append(dict(role=role,generation=g,offset=offset,quality=quality,
                    ec=u['context_error'],ep=u['persistence_error']))
            else:
                previous.update(ec=.5*previous['ec']+.5*u['context_error'],
                    ep=.5*previous['ep']+.5*u['persistence_error'])
        if sorted(expected,key=key)!=sorted(u['after'],key=key):technical.append(f'{target}:WRONG_CELL_UPDATE')
    for frame,event in admissions.items():
        stock=event['after'];live={(x['role'],x['generation']) for x in stock['retained']}
        if stock['candidate']:live.add((1,stock['candidate']['generation']))
        expected=[c for c in event['cells_before'] if (c['role'],c['generation']) in live]
        if event['cells_after']!=expected:technical.append(f'{frame}:ILLEGAL_ADMISSION_CELL_CHANGE')
    report['availability_V']=dict(expected=len(plan['masks']['V']),
        observed=sum(bool(forecasts.get(t,{}).get('context_available')) for t in plan['masks']['V']))
    dependent_ok=not technical and not deviations
    report['stock_causality']='PASS' if dependent_ok else 'NOT_EVALUABLE'
    choices={int(t):e['choice'] for t,e in plan['expected_targets'].items()}
    choice_differences=[t for t,wanted in choices.items() if forecasts.get(t,{}).get('choice')!=wanted]
    report['expected_choice_differences']=choice_differences
    experience_checks={}
    if dependent_ok:
        def cell_at(target,role,generation,when):
            return next((c for c in updates[target][when] if key(c)==(role,generation,0,0)),None)
        b=cell_at(31,0,2,'before');a=cell_at(31,0,1,'before')
        experience_checks['opposite_live_errors']=bool(a and b and a['ec']<a['ep'] and b['ec']>b['ep'])
        experience_checks['A_unchanged_at31']=cell_at(31,0,1,'before')==cell_at(31,0,1,'after')
        experience_checks['B_unchanged_at35']=cell_at(35,0,2,'before')==cell_at(35,0,2,'after')
        experience_checks['ambiguous39_no_update']=updates[39]['before']==updates[39]['after'] and not updates[39]['ticket'][-1]
        experience_checks['old_r1_deleted48']=any(key(c)==(0,1,0,0) for c in admissions[48]['deleted'])
        experience_checks['no_old_r1_on_return']=all(cell_at(t,0,1,'before') is None for t in (51,55,59,63))
        experience_checks['fresh_candidate55']=cell_at(55,1,7,'before') is None
        experience_checks['candidate_deleted56']=any(key(c)==(1,7,0,0) for c in admissions[56]['deleted'])
        experience_checks['fresh_retained59']=cell_at(59,0,5,'before') is None
        experience_checks['own_new_experience63']=cell_at(63,0,5,'before')==cell_at(59,0,5,'after') and cell_at(59,0,5,'after') is not None
    report['experience_checks']=experience_checks
    report['experience_selection']=('PASS' if not choice_differences and all(experience_checks.values()) else 'FAIL') if dependent_ok else 'NOT_EVALUABLE'
    v=report['metrics']['V']['arms']
    available=report['availability_V']['observed']==report['availability_V']['expected']
    if not dependent_ok or not available or any(v[a]['status']!='EVALUABLE' for a in v):
        benefit='NOT_EVALUABLE'
    elif v['E']['mae']<v['K']['mae'] and v['E']['mae']<v['P']['mae']:
        benefit='NETTONUTZEN_BELEGT'
    elif v['E']['mae']>v['K']['mae'] or v['E']['mae']>v['P']['mae']:
        benefit='SCHADEN'
    else:benefit='NICHT_NACHGEWIESEN'
    report['net_benefit']=benefit
    report['diagnostic_D_cannot_replace_V']=True
    report['deviation_policy']='Hypothesis deviations are not implementation failures; dependent criteria NOT_EVALUABLE. Preserve observations; no intervention/retry.'
    report['lost_experience_evidence']={str(t):admissions.get(t) for t in (40,48,52,56)}
    report['cold_and_relearning_evidence']={str(t):dict(forecast=forecasts.get(t),update=updates.get(t)) for t in (51,55,59,63)}
    return report
