"""External retention chains, separated from whole-series effectiveness."""
def witnesses(observer,source):
    result=[]
    for keeper,other in (('E','F'),('F','E')):
        a=observer[keeper];b=observer[other]
        for kept,lost in zip(a['blocks'],b['blocks'],strict=True):
            if kept['end']!=lost['end']:raise ValueError('MECHANISM_BLOCK')
            before={tuple(t['ordinals']):t for t in kept['before']['retained']}
            after={tuple(t['ordinals']):t for t in kept['after']['retained']}
            for victim in lost['victims']:
                identity=tuple(victim)
                if identity not in before or identity not in after:continue
                old=before[identity];marks=kept['before']['observation_end']
                last=marks.get(old['generation'],marks.get(str(old['generation']),identity[-1]))
                origin_values=[list(source[i-1]) for i in identity]
                intervening=[end for end in range(last+4,kept['end'],4) if [list(v) for v in source[end-4:end]]!=origin_values]
                if not intervening:continue
                base=dict(keeper=keeper,origin=list(identity),promotion_end=kept['end'],last_observation=last,unequal_blocks=intervening,other_victim=victim,keeper_victims=kept['victims'],newer_keeper_victims=[v for v in kept['victims'] if v[0]>identity[0]])
                result.append(base|dict(stage='retention'))
                for target in a['targets']:
                    if target['target']<=kept['end']:continue
                    relevant=[x for x in a['blocks'] if kept['end']<x['end']<target['target']]
                    if any(not any(tuple(t['ordinals'])==identity for t in x['after']['retained']) for x in relevant):continue
                    for h in target['hypotheses']:
                        if tuple(h['origin'])!=identity:continue
                        previous=[t for t in h['prior_live_feedback'] if t<kept['end'] and t<target['target']-1]
                        if not previous or not h['warm'] or not h['chosen']:continue
                        opposite=next(x for x in b['targets'] if x['target']==target['target'])
                        result.append(base|dict(stage='warm_use',offset=h['offset'],prior_live_feedback=previous,target=target['target'],output=target['output'],keeper_error=target['error'],other_error=opposite['error'],local_gain=target['error']<opposite['error']))
    return result

def summarize(records):
    return {mode:dict(retention_events=sum(x['keeper']==mode and x['stage']=='retention' for x in records),warm_uses=sum(x['keeper']==mode and x['stage']=='warm_use' for x in records),local_gains=sum(x['keeper']==mode and x['stage']=='warm_use' and x['local_gain'] for x in records),first_witness=next((x for x in records if x['keeper']==mode and x['stage']=='warm_use' and x['local_gain']),None)) for mode in ('E','F')}
