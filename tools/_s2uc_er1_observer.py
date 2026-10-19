"""External ER1 provenance/cost accounting; no policy imports or inputs."""
import json

def origin(match):return tuple(match['ordinals'])
def derive(arm):
    events=list(arm['events']);forecasts=list(arm['forecasts']);rows=list(arm['rows'])
    feedback={};targets=[];blocks=[]
    bytarget={x['target']:x for x in rows}
    for forecast in forecasts:
        target=forecast['index']+1
        receipt=forecast['receipt'];eligible=[]
        for match,h in zip(receipt['matches'],receipt['hypotheses'],strict=True):
            if not h['eligible']:continue
            ident=(origin(match),match['offset']);key=({'retained':0,'candidate':1}[match['role']],match['generation'],match['offset'])
            prior=list(feedback.get(ident,[]))
            eligible.append(dict(origin=list(ident[0]),offset=ident[1],key=list(key),warm=h['ec'] is not None,prior_live_feedback=prior,chosen=forecast['selected'] is not None and list(forecast['selected'])==list(key),original_age=target-ident[0][0],feedback_gap=None if not prior else target-prior[-1]))
        if target in bytarget:
            row=bytarget[target]
            targets.append(dict(target=target,hypotheses=eligible,output=forecast['output'],error=row['error']))
            for update in row['updates']:
                if update['live']:
                    match=next(h for h in eligible if h['key']==list(update['key']))
                    ident=(tuple(match['origin']),match['offset']);feedback.setdefault(ident,[]).append(target)
    per=[e for e in events if e['stage']=='perception:after']
    previous=None
    for e in per:
        state=e['state'];index=state['accepted']
        if index%4:continue
        after=state['stock'];before=previous
        if before is None:
            before=dict(retained=[],candidate=None,observation_end={})
        a=[t['ordinals'] for t in after['retained']];b=[t['ordinals'] for t in before['retained']]
        new=[x for x in a if x not in b];victims=[x for x in b if x not in a]
        ca=after['candidate'];cb=before['candidate']
        if new:action='promotion'
        elif ca!=cb:action='admission' if cb is None else 'candidate_replacement'
        else:action='confirmation' if after['observation_end']!=before['observation_end'] else 'discard'
        victim_details=[dict(origin=t['ordinals'],original_age=index-t['ordinals'][0],last_observation_end=before['observation_end'].get(t['generation'],before['observation_end'].get(str(t['generation'])))) for t in before['retained'] if t['ordinals'] in victims]
        blocks.append(dict(end=index,action=action,before=before,after=after,new_originals=new,victims=victims,victim_details=victim_details,reordered=not new and a!=b))
        previous=after
    return dict(blocks=blocks,targets=targets)
def compare(e,f):
    left=derive(e);right=derive(f)
    differences=[]
    for a,b in zip(left['targets'],right['targets'],strict=True):
        if a['target']!=b['target']:raise ValueError('OBSERVER_TARGET')
        ids=lambda row:{(tuple(h['origin']),h['offset']) for h in row['hypotheses']}
        differences.append(dict(target=a['target'],E_only=sorted(ids(a)-ids(b)),F_only=sorted(ids(b)-ids(a)),delta=a['error']-b['error']))
    affected=[x for x in differences if x['E_only'] or x['F_only']]
    origins={tuple(o) for x in affected for key in ('E_only','F_only') for o,off in x[key]}
    return dict(E=left,F=right,differences=differences,counts=dict(block_events_per_arm=len(left['blocks']),affected_targets=len(affected),unique_differing_origins=len(origins)),cost_balance=dict(gain=sum(-x['delta'] for x in differences if x['delta']<0),harm=sum(x['delta'] for x in differences if x['delta']>0),max_harm=max([0.]+[x['delta'] for x in differences]),better_targets=[x['target'] for x in differences if x['delta']<0],worse_targets=[x['target'] for x in differences if x['delta']>0],equal_targets=[x['target'] for x in differences if x['delta']==0]))

def archive_form(observer,collection):
    # Five additional bounded sequences: 13 total including the two policy arms.
    def sequence(items):
        result=collection()
        for item in items:result.append(item)
        return result
    return dict(E={k:sequence(v) for k,v in observer['E'].items()},F={k:sequence(v) for k,v in observer['F'].items()},differences=sequence(observer['differences']),counts=observer['counts'],cost_balance=observer['cost_balance'])
